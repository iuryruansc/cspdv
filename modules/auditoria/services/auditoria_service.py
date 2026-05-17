from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.auditoria.models.auditoria_model import AuditoriaModel
from utils.app_logger import log_warning


class AuditoriaService:
    @staticmethod
    def listar_eventos(limit: int = 300) -> List[Dict[str, Any]]:
        rows = AuditoriaModel.listar(limit=limit)
        for row in rows:
            row["usuario"] = str(row.get("usuario_nome") or "-")
            row["data_hora"] = str(row.get("data_hora") or "-")
            row["categoria"] = str(row.get("categoria") or "-").replace("_", " ").title()
            row["evento"] = str(row.get("evento") or "-").replace("_", " ").title()
            row["entidade"] = str(row.get("entidade") or "-").replace("_", " ").title()
            row["caixa"] = f"Caixa #{int(row['caixa_id'])}" if row.get("caixa_id") else "-"
        return rows

    @staticmethod
    def obter_evento_detalhado(evento_id: int) -> Optional[Dict[str, Any]]:
        evento = AuditoriaModel.buscar_por_id(int(evento_id))
        if not evento:
            return None
        detalhes_brutos = str(evento.get("detalhes_json") or "").strip()
        detalhes_formatados = ""
        if detalhes_brutos:
            try:
                detalhes_formatados = json.dumps(json.loads(detalhes_brutos), ensure_ascii=False, indent=2, sort_keys=True)
            except Exception:
                detalhes_formatados = detalhes_brutos
        evento["detalhes_formatados"] = detalhes_formatados
        evento["categoria_label"] = str(evento.get("categoria") or "-").replace("_", " ").title()
        evento["evento_label"] = str(evento.get("evento") or "-").replace("_", " ").title()
        evento["entidade_label"] = str(evento.get("entidade") or "-").replace("_", " ").title()
        evento["usuario_label"] = str(evento.get("usuario_nome") or "-")
        evento["caixa_label"] = f"Caixa #{int(evento['caixa_id'])}" if evento.get("caixa_id") else "-"
        return evento

    @staticmethod
    def registrar_evento(
        *,
        evento: str,
        categoria: str,
        entidade: Optional[str] = None,
        entidade_id: Optional[int] = None,
        usuario_id: Optional[int] = None,
        caixa_id: Optional[int] = None,
        detalhes: Optional[Dict[str, Any]] = None,
    ) -> bool:
        usuario_final = int(usuario_id) if usuario_id is not None else AuditoriaService._usuario_sessao()
        caixa_final = int(caixa_id) if caixa_id is not None else AuditoriaService._caixa_sessao()

        try:
            AuditoriaModel.registrar_evento(
                evento=str(evento or "").strip().lower(),
                categoria=str(categoria or "").strip().lower(),
                entidade=str(entidade).strip().lower() if entidade else None,
                entidade_id=int(entidade_id) if entidade_id is not None else None,
                usuario_id=usuario_final,
                caixa_id=caixa_final,
                detalhes_json=AuditoriaService._serializar_detalhes(detalhes),
            )
            return True
        except Exception as exc:
            log_warning(f"Falha ao registrar evento de auditoria '{evento}': {exc}")
            return False

    @staticmethod
    def _serializar_detalhes(detalhes: Optional[Dict[str, Any]]) -> Optional[str]:
        if not detalhes:
            return None
        return json.dumps(detalhes, ensure_ascii=False, sort_keys=True, default=str)

    @staticmethod
    def _usuario_sessao() -> Optional[int]:
        usuario = SessionManager.current_user() or {}
        usuario_id = int(usuario.get("id") or 0)
        return usuario_id if usuario_id > 0 else None

    @staticmethod
    def _caixa_sessao() -> Optional[int]:
        caixa = CaixaSession.current() or {}
        caixa_id = int(caixa.get("id") or 0)
        return caixa_id if caixa_id > 0 else None
