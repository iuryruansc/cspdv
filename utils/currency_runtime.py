from __future__ import annotations

from typing import Any

_DEFAULT_CURRENCY = "BRL"
_CURRENCY_SYMBOLS = {
    "BRL": "R$",
    "USD": "US$",
}


def codigo_moeda_padrao() -> str:
    try:
        from modules.admin.services.configuracoes_service import ConfiguracoesService

        dados: dict[str, Any] = ConfiguracoesService.carregar_empresa_pdv().get("empresa") or {}
    except Exception:
        dados = {}

    codigo = str(dados.get("moeda_padrao") or _DEFAULT_CURRENCY).strip().upper()
    if codigo not in _CURRENCY_SYMBOLS:
        return _DEFAULT_CURRENCY
    return codigo


def simbolo_moeda_padrao() -> str:
    return _CURRENCY_SYMBOLS.get(codigo_moeda_padrao(), _CURRENCY_SYMBOLS[_DEFAULT_CURRENCY])
