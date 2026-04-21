from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional

class SessionManager:
    _current_user: Optional[Dict[str, Any]] = None
    _started_at: Optional[datetime] = None

    @classmethod
    def login(cls, user: Dict[str, Any]) -> None:
        cls._current_user = deepcopy(user)
        cls._started_at = datetime.now()

    @classmethod
    def logout(cls) -> None:
        cls._current_user = None
        cls._started_at = None

    @classmethod
    def current_user(cls) -> Optional[Dict[str, Any]]:
        if cls._current_user is None:
            return None
        return deepcopy(cls._current_user)

    @classmethod
    def is_authenticated(cls) -> bool:
        return cls._current_user is not None

    @classmethod
    def has_permission(cls, permission_key: str) -> bool:
        if cls._current_user is None:
            return False

        permissions = cls._current_user.get("permissoes", [])
        if "sistema.master" in permissions:
            return True

        return permission_key in permissions

    @classmethod
    def diagnostics(cls) -> Dict[str, Any]:
        return {
            "authenticated": cls.is_authenticated(),
            "started_at": cls._started_at.isoformat() if cls._started_at else None,
            "user_id": cls._current_user.get("id") if cls._current_user else None,
            "user_name": cls._current_user.get("nome") if cls._current_user else None,
            "permissions_count": len(cls._current_user.get("permissoes", [])) if cls._current_user else 0,
        }
