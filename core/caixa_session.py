from copy import deepcopy
from typing import Any, Dict, Optional

class CaixaSession:
    _current_caixa: Optional[Dict[str, Any]] = None

    @classmethod
    def open(cls, caixa_data: Dict[str, Any]) -> None:
        cls._current_caixa = deepcopy(caixa_data)

    @classmethod
    def close(cls) -> None:
        cls._current_caixa = None

    @classmethod
    def current(cls) -> Optional[Dict[str, Any]]:
        if cls._current_caixa is None:
            return None
        return deepcopy(cls._current_caixa)

    @classmethod
    def has_open_caixa(cls) -> bool:
        return cls._current_caixa is not None
