from __future__ import annotations

from typing import Any, Dict

_DEFAULTS: Dict[str, Any] = {
    "intervalo_backup_horas": 24,
    "perfil_log": "OPERACIONAL",
    "versao_referencia": "CSPdv v1.0.0",
}

_MAPA_LABEL_PERFIL = {
    "OPERACIONAL": "Operacional",
    "DETALHADO": "Detalhado",
    "SILENCIOSO": "Silencioso",
}

def carregar_parametros_sistema() -> Dict[str, Any]:
    try:
        from modules.admin.services.configuracoes_service import ConfiguracoesService

        dados = ConfiguracoesService.carregar_parametros_sistema()
    except Exception:
        dados = {}

    perfil = str(dados.get("perfil_log") or _DEFAULTS["perfil_log"]).strip().upper()
    if perfil not in _MAPA_LABEL_PERFIL:
        perfil = str(_DEFAULTS["perfil_log"])

    try:
        intervalo = int(dados.get("intervalo_backup_horas") or _DEFAULTS["intervalo_backup_horas"])
    except (TypeError, ValueError):
        intervalo = int(_DEFAULTS["intervalo_backup_horas"])

    versao = str(dados.get("versao_referencia") or _DEFAULTS["versao_referencia"]).strip()
    if not versao:
        versao = str(_DEFAULTS["versao_referencia"])

    return {
        "intervalo_backup_horas": max(1, intervalo),
        "perfil_log": perfil,
        "versao_referencia": versao,
    }

def versao_referencia() -> str:
    return str(carregar_parametros_sistema()["versao_referencia"])

def perfil_log() -> str:
    return str(carregar_parametros_sistema()["perfil_log"])

def perfil_log_label() -> str:
    return _MAPA_LABEL_PERFIL.get(perfil_log(), "Operacional")

def intervalo_backup_horas() -> int:
    return int(carregar_parametros_sistema()["intervalo_backup_horas"])

def descricao_ambiente() -> str:
    return (
        f"{versao_referencia()} | "
        f"Backup a cada {intervalo_backup_horas()}h | "
        f"Log {perfil_log_label()}"
    )
