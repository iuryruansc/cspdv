from __future__ import annotations

import hashlib
import hmac
import json
import os
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Optional

class SessionManager:
    _current_user: Optional[Dict[str, Any]] = None
    _started_at: Optional[datetime] = None
    _expires_at: Optional[datetime] = None

    @classmethod
    def login(cls, user: Dict[str, Any], *, persist: bool = True) -> None:
        sanitized_user = deepcopy(user)
        sanitized_user.pop("senha", None)
        cls._current_user = sanitized_user
        cls._started_at = datetime.now()
        cls._expires_at = cls._started_at + timedelta(hours=cls._ttl_hours())

        if persist and cls.session_persistence_enabled():
            cls._save_persisted_session()
            return

        cls._clear_persisted_session()

    @classmethod
    def logout(cls, *, clear_persisted: bool = True) -> None:
        cls._current_user = None
        cls._started_at = None
        cls._expires_at = None

        if clear_persisted:
            cls._clear_persisted_session()

    @classmethod
    def current_user(cls) -> Optional[Dict[str, Any]]:
        if cls._current_user is None:
            return None
        return deepcopy(cls._current_user)

    @classmethod
    def is_authenticated(cls) -> bool:
        if cls._current_user is None:
            return False

        if cls._expires_at and datetime.now() > cls._expires_at:
            cls.logout()
            return False

        return True

    @classmethod
    def has_permission(cls, permission_key: str) -> bool:
        if not cls.is_authenticated() or cls._current_user is None:
            return False

        permissions = cls._current_user.get("permissoes", [])
        if "sistema.master" in permissions:
            return True

        return permission_key in permissions

    @classmethod
    def restore_persisted_session(
        cls,
        user_loader: Callable[[int], Optional[Dict[str, Any]]],
    ) -> bool:
        if not cls.session_persistence_enabled():
            cls._clear_persisted_session()
            return False

        payload = cls._read_persisted_session()
        if payload is None:
            return False

        user_id = payload.get("user_id")
        if not isinstance(user_id, int):
            cls._clear_persisted_session()
            return False

        issued_at = cls._parse_iso_datetime(payload.get("issued_at"))
        expires_at_payload = cls._parse_iso_datetime(payload.get("expires_at"))
        expires_at_config = (
            issued_at + timedelta(hours=cls._ttl_hours())
            if issued_at is not None
            else None
        )
        expires_at = cls._effective_expiration(expires_at_payload, expires_at_config)
        if expires_at is None or datetime.now() > expires_at:
            cls._clear_persisted_session()
            return False

        user = user_loader(user_id)
        if not user:
            cls._clear_persisted_session()
            return False

        cls.login(user, persist=True)
        return True

    @classmethod
    def diagnostics(cls) -> Dict[str, Any]:
        return {
            "authenticated": cls.is_authenticated(),
            "started_at": cls._started_at.isoformat() if cls._started_at else None,
            "expires_at": cls._expires_at.isoformat() if cls._expires_at else None,
            "user_id": cls._current_user.get("id") if cls._current_user else None,
            "user_name": cls._current_user.get("nome") if cls._current_user else None,
            "permissions_count": len(cls._current_user.get("permissoes", [])) if cls._current_user else 0,
            "session_file": str(cls._session_file_path()),
        }

    @classmethod
    def session_persistence_enabled(cls) -> bool:
        return bool(cls._carregar_parametros_seguranca().get("restaurar_login_automaticamente", True))

    @classmethod
    def should_block_close_with_open_caixa(cls) -> bool:
        return bool(
            cls._carregar_parametros_seguranca().get(
                "bloquear_fechamento_programa_caixa_aberto",
                True,
            )
        )

    @classmethod
    def _save_persisted_session(cls) -> None:
        if cls._current_user is None or cls._expires_at is None:
            return

        user_id = cls._current_user.get("id")
        if user_id is None:
            return

        payload = {
            "user_id": int(user_id),
            "issued_at": (cls._started_at or datetime.now()).isoformat(),
            "expires_at": cls._expires_at.isoformat(),
        }
        payload_json = cls._payload_json(payload)
        persisted = {"payload": payload, "signature": cls._sign_payload(payload_json)}

        session_file = cls._session_file_path()
        try:
            session_file.parent.mkdir(parents=True, exist_ok=True)
            session_file.write_text(json.dumps(persisted, ensure_ascii=True, indent=2), encoding="utf-8")
        except OSError:
            return

    @classmethod
    def _read_persisted_session(cls) -> Optional[Dict[str, Any]]:
        session_file = cls._session_file_path()
        if not session_file.exists():
            return None

        try:
            raw = json.loads(session_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cls._clear_persisted_session()
            return None

        payload = raw.get("payload")
        signature = raw.get("signature")
        if not isinstance(payload, dict) or not isinstance(signature, str):
            cls._clear_persisted_session()
            return None

        expected = cls._sign_payload(cls._payload_json(payload))
        if not hmac.compare_digest(signature, expected):
            cls._clear_persisted_session()
            return None

        return payload

    @classmethod
    def _clear_persisted_session(cls) -> None:
        session_file = cls._session_file_path()
        try:
            if session_file.exists():
                session_file.unlink()
        except OSError:
            # A remoção do cache de sessão é melhor esforço.
            return

    @classmethod
    def _payload_json(cls, payload: Dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

    @classmethod
    def _sign_payload(cls, payload_json: str) -> str:
        secret = cls._session_secret().encode("utf-8")
        return hmac.new(secret, payload_json.encode("utf-8"), hashlib.sha256).hexdigest()

    @classmethod
    def _session_secret(cls) -> str:
        return (
            os.getenv("SESSION_SECRET")
            or os.getenv("APP_SECRET")
            or f"cspdv:{os.getenv('DB_NAME', 'local')}:{os.getenv('DB_USER', 'user')}:{os.getenv('DB_HOST', '127.0.0.1')}"
        )

    @classmethod
    def _session_file_path(cls) -> Path:
        custom_path = str(os.getenv("CSPDV_SESSION_FILE") or "").strip()
        if custom_path:
            return Path(custom_path)

        custom_data_dir = str(os.getenv("CSPDV_DATA_DIR") or "").strip()
        if custom_data_dir:
            return Path(custom_data_dir) / "session.json"

        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            return Path(local_appdata) / "CSPdv" / "session.json"
        return Path.home() / ".cspdv" / "session.json"

    @classmethod
    def _ttl_hours(cls) -> int:
        parametros = cls._carregar_parametros_seguranca()
        raw = str(
            parametros.get("horas_sessao_persistida")
            or os.getenv("SESSION_TTL_HOURS", "12")
        ).strip()
        try:
            hours = int(raw)
        except ValueError:
            hours = 12
        return max(1, hours)

    @classmethod
    def _parse_iso_datetime(cls, value: Any) -> Optional[datetime]:
        if not isinstance(value, str) or not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @classmethod
    def _effective_expiration(
        cls,
        expires_at_payload: Optional[datetime],
        expires_at_config: Optional[datetime],
    ) -> Optional[datetime]:
        if expires_at_payload is None:
            return expires_at_config
        if expires_at_config is None:
            return expires_at_payload
        return min(expires_at_payload, expires_at_config)

    @classmethod
    def _carregar_parametros_seguranca(cls) -> Dict[str, Any]:
        try:
            from modules.admin.services.configuracoes_service import ConfiguracoesService

            return ConfiguracoesService.carregar_parametros_seguranca()
        except Exception:
            return {
                "horas_sessao_persistida": 12,
                "restaurar_login_automaticamente": True,
                "bloquear_fechamento_programa_caixa_aberto": True,
            }
