from __future__ import annotations

from typing import Any, Dict, List

from modules.admin.models.configuracoes_model import ConfiguracoesModel
from utils.format_utils import numero_decimal

class ConfiguracoesService:
    _MAPA_MOEDA = {
        "Real (BRL)": "BRL",
        "Dólar (USD)": "USD",
    }
    _MAPA_CLIENTE_PADRAO = {
        "Consumidor Final": "CONSUMIDOR_FINAL",
        "Selecionar no momento da venda": "SELECIONAR_NO_MOMENTO",
    }
    _MAPA_REGRA_DESCONTO = {
        "Permitir desconto manual": "PERMITIR_DESCONTO",
        "Exigir autorização para desconto": "EXIGIR_AUTORIZACAO",
    }
    _MAPA_PRIORIDADE_PROMOCIONAL = {
        "Promoção antes do desconto manual": "PROMOCAO_ANTES_DESCONTO",
        "Desconto manual antes da promoção": "DESCONTO_ANTES_PROMOCAO",
    }
    _MAPA_PERFIL_LOG = {
        "Operacional": "OPERACIONAL",
        "Detalhado": "DETALHADO",
        "Silencioso": "SILENCIOSO",
    }

    @staticmethod
    def carregar_empresa_pdv() -> Dict[str, Any]:
        empresa = ConfiguracoesModel.carregar_empresa_pdv()
        pdvs = ConfiguracoesModel.listar_pdvs()
        return {
            "empresa": empresa,
            "pdvs": pdvs,
        }

    @staticmethod
    def carregar_parametros_venda() -> Dict[str, Any]:
        empresa = ConfiguracoesModel.carregar_empresa_pdv()
        return {
            "cliente_padrao_venda": str(empresa.get("cliente_padrao_venda") or "CONSUMIDOR_FINAL"),
            "regra_desconto_venda": str(empresa.get("regra_desconto_venda") or "PERMITIR_DESCONTO"),
            "habilitar_venda_rapida_admin": bool(empresa.get("habilitar_venda_rapida_admin", True)),
            "permitir_venda_sem_estoque": bool(empresa.get("permitir_venda_sem_estoque", False)),
        }

    @staticmethod
    def carregar_parametros_caixa() -> Dict[str, Any]:
        empresa = ConfiguracoesModel.carregar_empresa_pdv()
        return {
            "fundo_inicial_sugerido": float(empresa.get("fundo_inicial_sugerido") or 0.0),
            "exigir_admin_sangria": bool(empresa.get("exigir_admin_sangria", True)),
            "exigir_admin_reembolso": bool(empresa.get("exigir_admin_reembolso", True)),
            "exigir_admin_diferenca_fechamento": bool(
                empresa.get("exigir_admin_diferenca_fechamento", True)
            ),
        }

    @staticmethod
    def carregar_parametros_promocoes() -> Dict[str, Any]:
        empresa = ConfiguracoesModel.carregar_empresa_pdv()
        return {
            "prioridade_promocional": str(
                empresa.get("prioridade_promocional") or "PROMOCAO_ANTES_DESCONTO"
            ),
            "bloquear_promocoes_simultaneas": bool(
                empresa.get("bloquear_promocoes_simultaneas", True)
            ),
            "ativar_promocoes_por_vigencia": bool(
                empresa.get("ativar_promocoes_por_vigencia", True)
            ),
        }

    @staticmethod
    def carregar_parametros_seguranca() -> Dict[str, Any]:
        empresa = ConfiguracoesModel.carregar_empresa_pdv()
        return {
            "horas_sessao_persistida": int(empresa.get("horas_sessao_persistida") or 12),
            "restaurar_login_automaticamente": bool(
                empresa.get("restaurar_login_automaticamente", True)
            ),
            "bloquear_fechamento_programa_caixa_aberto": bool(
                empresa.get("bloquear_fechamento_programa_caixa_aberto", True)
            ),
        }

    @staticmethod
    def carregar_parametros_sistema() -> Dict[str, Any]:
        empresa = ConfiguracoesModel.carregar_empresa_pdv()
        return {
            "intervalo_backup_horas": int(empresa.get("intervalo_backup_horas") or 24),
            "perfil_log": str(empresa.get("perfil_log") or "OPERACIONAL"),
            "versao_referencia": str(empresa.get("versao_referencia") or "CSPdv v1.0.0"),
        }

    @staticmethod
    def salvar_empresa_pdv(*, razao_social: str, pdv_padrao_id: int | None, moeda_label: str) -> tuple[bool, str]:
        razao = str(razao_social or "").strip()
        if not razao:
            return False, "Informe a razão social da empresa."

        moeda = ConfiguracoesService._MAPA_MOEDA.get(str(moeda_label or "").strip(), "BRL")
        ConfiguracoesModel.salvar_empresa_pdv(
            razao_social=razao,
            pdv_padrao_id=int(pdv_padrao_id) if pdv_padrao_id is not None else None,
            moeda_padrao=moeda,
        )
        return True, "Dados de Empresa e PDV salvos com sucesso."

    @staticmethod
    def salvar_parametros_venda(
        *,
        cliente_padrao_label: str,
        regra_desconto_label: str,
        habilitar_venda_rapida_admin: bool,
        permitir_venda_sem_estoque: bool,
    ) -> tuple[bool, str]:
        cliente_padrao = ConfiguracoesService._MAPA_CLIENTE_PADRAO.get(
            str(cliente_padrao_label or "").strip(),
            "CONSUMIDOR_FINAL",
        )
        regra_desconto = ConfiguracoesService._MAPA_REGRA_DESCONTO.get(
            str(regra_desconto_label or "").strip(),
            "PERMITIR_DESCONTO",
        )

        ConfiguracoesModel.salvar_parametros_venda(
            cliente_padrao_venda=cliente_padrao,
            regra_desconto_venda=regra_desconto,
            habilitar_venda_rapida_admin=habilitar_venda_rapida_admin,
            permitir_venda_sem_estoque=permitir_venda_sem_estoque,
        )
        return True, "Parâmetros de Venda salvos com sucesso."

    @staticmethod
    def salvar_parametros_caixa(
        *,
        fundo_inicial_sugerido_texto: str,
        exigir_admin_sangria: bool,
        exigir_admin_reembolso: bool,
        exigir_admin_diferenca_fechamento: bool,
    ) -> tuple[bool, str]:
        fundo_inicial_sugerido = numero_decimal(fundo_inicial_sugerido_texto)
        if fundo_inicial_sugerido < 0:
            return False, "O fundo inicial sugerido não pode ser negativo."

        ConfiguracoesModel.salvar_parametros_caixa(
            fundo_inicial_sugerido=fundo_inicial_sugerido,
            exigir_admin_sangria=exigir_admin_sangria,
            exigir_admin_reembolso=exigir_admin_reembolso,
            exigir_admin_diferenca_fechamento=exigir_admin_diferenca_fechamento,
        )
        return True, "Parâmetros de Caixa salvos com sucesso."

    @staticmethod
    def salvar_parametros_promocoes(
        *,
        prioridade_promocional_label: str,
        bloquear_promocoes_simultaneas: bool,
        ativar_promocoes_por_vigencia: bool,
    ) -> tuple[bool, str]:
        prioridade_promocional = ConfiguracoesService._MAPA_PRIORIDADE_PROMOCIONAL.get(
            str(prioridade_promocional_label or "").strip(),
            "PROMOCAO_ANTES_DESCONTO",
        )
        ConfiguracoesModel.salvar_parametros_promocoes(
            prioridade_promocional=prioridade_promocional,
            bloquear_promocoes_simultaneas=bloquear_promocoes_simultaneas,
            ativar_promocoes_por_vigencia=ativar_promocoes_por_vigencia,
        )
        return True, "Parâmetros de Promoções salvos com sucesso."

    @staticmethod
    def salvar_parametros_seguranca(
        *,
        horas_sessao_persistida_texto: str,
        restaurar_login_automaticamente: bool,
        bloquear_fechamento_programa_caixa_aberto: bool,
    ) -> tuple[bool, str]:
        try:
            horas = int(str(horas_sessao_persistida_texto or "").strip() or "0")
        except ValueError:
            return False, "Informe um valor inteiro válido para as horas de sessão persistida."

        if horas <= 0:
            return False, "As horas de sessão persistida devem ser maiores que zero."

        ConfiguracoesModel.salvar_parametros_seguranca(
            horas_sessao_persistida=horas,
            restaurar_login_automaticamente=restaurar_login_automaticamente,
            bloquear_fechamento_programa_caixa_aberto=bloquear_fechamento_programa_caixa_aberto,
        )
        return True, "Parâmetros de Segurança e Sessão salvos com sucesso."

    @staticmethod
    def salvar_parametros_sistema(
        *,
        intervalo_backup_horas_texto: str,
        perfil_log_label: str,
        versao_referencia: str,
    ) -> tuple[bool, str]:
        try:
            intervalo = int(str(intervalo_backup_horas_texto or "").strip() or "0")
        except ValueError:
            return False, "Informe um valor inteiro válido para o intervalo de backup."

        if intervalo <= 0:
            return False, "O intervalo de backup deve ser maior que zero."

        perfil_log = ConfiguracoesService._MAPA_PERFIL_LOG.get(
            str(perfil_log_label or "").strip(),
            "OPERACIONAL",
        )
        versao = str(versao_referencia or "").strip() or "CSPdv v1.0.0"

        ConfiguracoesModel.salvar_parametros_sistema(
            intervalo_backup_horas=intervalo,
            perfil_log=perfil_log,
            versao_referencia=versao,
        )
        return True, "Parâmetros de Sistema salvos com sucesso."

    @staticmethod
    def opcoes_moeda() -> List[str]:
        return list(ConfiguracoesService._MAPA_MOEDA.keys())

    @staticmethod
    def opcoes_cliente_padrao() -> List[str]:
        return list(ConfiguracoesService._MAPA_CLIENTE_PADRAO.keys())

    @staticmethod
    def opcoes_regra_desconto() -> List[str]:
        return list(ConfiguracoesService._MAPA_REGRA_DESCONTO.keys())

    @staticmethod
    def opcoes_prioridade_promocional() -> List[str]:
        return list(ConfiguracoesService._MAPA_PRIORIDADE_PROMOCIONAL.keys())

    @staticmethod
    def opcoes_perfil_log() -> List[str]:
        return list(ConfiguracoesService._MAPA_PERFIL_LOG.keys())

    @staticmethod
    def label_moeda(codigo: str | None) -> str:
        codigo_normalizado = str(codigo or "BRL").strip().upper()
        for label, valor in ConfiguracoesService._MAPA_MOEDA.items():
            if valor == codigo_normalizado:
                return label
        return "Real (BRL)"

    @staticmethod
    def label_cliente_padrao(codigo: str | None) -> str:
        codigo_normalizado = str(codigo or "CONSUMIDOR_FINAL").strip().upper()
        for label, valor in ConfiguracoesService._MAPA_CLIENTE_PADRAO.items():
            if valor == codigo_normalizado:
                return label
        return "Consumidor Final"

    @staticmethod
    def label_regra_desconto(codigo: str | None) -> str:
        codigo_normalizado = str(codigo or "PERMITIR_DESCONTO").strip().upper()
        for label, valor in ConfiguracoesService._MAPA_REGRA_DESCONTO.items():
            if valor == codigo_normalizado:
                return label
        return "Permitir desconto manual"

    @staticmethod
    def label_prioridade_promocional(codigo: str | None) -> str:
        codigo_normalizado = str(codigo or "PROMOCAO_ANTES_DESCONTO").strip().upper()
        for label, valor in ConfiguracoesService._MAPA_PRIORIDADE_PROMOCIONAL.items():
            if valor == codigo_normalizado:
                return label
        return "Promoção antes do desconto manual"

    @staticmethod
    def label_perfil_log(codigo: str | None) -> str:
        codigo_normalizado = str(codigo or "OPERACIONAL").strip().upper()
        for label, valor in ConfiguracoesService._MAPA_PERFIL_LOG.items():
            if valor == codigo_normalizado:
                return label
        return "Operacional"
