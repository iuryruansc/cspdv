from __future__ import annotations

from typing import Any, cast

from database.connection import db_cursor, db_transaction
from modules.shared.constants import (
    CLIENTE_PADRAO_CONSUMIDOR_FINAL,
    FLAG_NAO,
    FLAG_SIM,
    PERFIL_LOG_OPERACIONAL,
    PRIORIDADE_PROMOCAO_ANTES_DESCONTO,
    REGIME_TRIBUTARIO_SIMPLES_NACIONAL,
    REGRA_DESCONTO_PERMITIR,
    bool_para_flag,
    flag_ativa,
)

class ConfiguracoesModel:
    @staticmethod
    def _obter_empresa_id(cur) -> int | None:
        cur.execute("SELECT id FROM config_empresa ORDER BY id LIMIT 1")
        row = cur.fetchone()
        return int(row[0]) if row else None

    @staticmethod
    def _empresa_placeholder() -> tuple:
        return ("Empresa em configuração", "Empresa em configuração")

    @staticmethod
    def listar_pdvs() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, identificacao, descricao, status, ativo
                FROM pdvs
                WHERE COALESCE(ativo, %s) = %s
                ORDER BY identificacao
                """,
                (FLAG_SIM, FLAG_SIM),
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def carregar_empresa_pdv() -> dict[str, Any]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    razao_social,
                    pdv_padrao_id,
                    moeda_padrao,
                    regime_tributario_padrao,
                    origem_mercadoria_padrao,
                    cfop_venda_padrao,
                    cfop_devolucao_padrao,
                    csosn_cst_padrao,
                    natureza_operacao_padrao,
                    exigir_ncm_cest_produto,
                    exigir_unidade_tributavel_produto,
                    cliente_padrao_venda,
                    regra_desconto_venda,
                    habilitar_venda_rapida_admin,
                    permitir_venda_sem_estoque,
                    fundo_inicial_sugerido,
                    exigir_admin_sangria,
                    exigir_admin_reembolso,
                    exigir_admin_diferenca_fechamento,
                    prioridade_promocional,
                    bloquear_promocoes_simultaneas,
                    ativar_promocoes_por_vigencia,
                    horas_sessao_persistida,
                    restaurar_login_automaticamente,
                    bloquear_fechamento_programa_caixa_aberto,
                    intervalo_backup_horas,
                    perfil_log,
                    versao_referencia
                FROM config_empresa
                ORDER BY id
                LIMIT 1
                """
            )
            registro = cast(dict[str, Any] | None, cur.fetchone()) or {}
            return {
                "id": registro.get("id"),
                "razao_social": str(registro.get("razao_social") or ""),
                "pdv_padrao_id": registro.get("pdv_padrao_id"),
                "moeda_padrao": str(registro.get("moeda_padrao") or "BRL"),
                "regime_tributario_padrao": str(
                    registro.get("regime_tributario_padrao") or REGIME_TRIBUTARIO_SIMPLES_NACIONAL
                ),
                "origem_mercadoria_padrao": str(
                    registro.get("origem_mercadoria_padrao") or "0"
                ),
                "cfop_venda_padrao": str(registro.get("cfop_venda_padrao") or "5102"),
                "cfop_devolucao_padrao": str(registro.get("cfop_devolucao_padrao") or "1202"),
                "csosn_cst_padrao": str(registro.get("csosn_cst_padrao") or "102"),
                "natureza_operacao_padrao": str(
                    registro.get("natureza_operacao_padrao") or "VENDA DE MERCADORIA"
                ),
                "exigir_ncm_cest_produto": flag_ativa(
                    registro.get("exigir_ncm_cest_produto"),
                    default=FLAG_SIM,
                ),
                "exigir_unidade_tributavel_produto": flag_ativa(
                    registro.get("exigir_unidade_tributavel_produto"),
                    default=FLAG_SIM,
                ),
                "cliente_padrao_venda": str(
                    registro.get("cliente_padrao_venda") or CLIENTE_PADRAO_CONSUMIDOR_FINAL
                ),
                "regra_desconto_venda": str(registro.get("regra_desconto_venda") or REGRA_DESCONTO_PERMITIR),
                "habilitar_venda_rapida_admin": flag_ativa(
                    registro.get("habilitar_venda_rapida_admin"),
                    default=FLAG_SIM,
                ),
                "permitir_venda_sem_estoque": flag_ativa(
                    registro.get("permitir_venda_sem_estoque"),
                    default=FLAG_NAO,
                ),
                "fundo_inicial_sugerido": float(registro.get("fundo_inicial_sugerido") or 0.0),
                "exigir_admin_sangria": flag_ativa(registro.get("exigir_admin_sangria"), default=FLAG_SIM),
                "exigir_admin_reembolso": flag_ativa(registro.get("exigir_admin_reembolso"), default=FLAG_SIM),
                "exigir_admin_diferenca_fechamento": flag_ativa(
                    registro.get("exigir_admin_diferenca_fechamento"),
                    default=FLAG_SIM,
                ),
                "prioridade_promocional": str(
                    registro.get("prioridade_promocional") or PRIORIDADE_PROMOCAO_ANTES_DESCONTO
                ),
                "bloquear_promocoes_simultaneas": flag_ativa(
                    registro.get("bloquear_promocoes_simultaneas"),
                    default=FLAG_SIM,
                ),
                "ativar_promocoes_por_vigencia": flag_ativa(
                    registro.get("ativar_promocoes_por_vigencia"),
                    default=FLAG_SIM,
                ),
                "horas_sessao_persistida": int(registro.get("horas_sessao_persistida") or 12),
                "restaurar_login_automaticamente": flag_ativa(
                    registro.get("restaurar_login_automaticamente"),
                    default=FLAG_SIM,
                ),
                "bloquear_fechamento_programa_caixa_aberto": flag_ativa(
                    registro.get("bloquear_fechamento_programa_caixa_aberto"),
                    default=FLAG_SIM,
                ),
                "intervalo_backup_horas": int(registro.get("intervalo_backup_horas") or 24),
                "perfil_log": str(registro.get("perfil_log") or PERFIL_LOG_OPERACIONAL),
                "versao_referencia": str(registro.get("versao_referencia") or "CSPdv v1.0.0"),
            }
    @staticmethod
    def salvar_empresa_pdv(*, razao_social: str, pdv_padrao_id: int | None, moeda_padrao: str) -> None:
        with db_transaction(dictionary=False) as cur:
            empresa_id = ConfiguracoesModel._obter_empresa_id(cur)

            if empresa_id is not None:
                cur.execute(
                    """
                    UPDATE config_empresa
                    SET razao_social = %s,
                        pdv_padrao_id = %s,
                        moeda_padrao = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (razao_social, pdv_padrao_id, moeda_padrao, empresa_id),
                )
            else:
                ph = ConfiguracoesModel._empresa_placeholder()
                cur.execute(
                    """
                    INSERT INTO config_empresa
                        (razao_social, nome_fantasia, pdv_padrao_id, moeda_padrao, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, %s, NOW(), NOW())
                    """,
                    (*ph, pdv_padrao_id, moeda_padrao),
                )
    @staticmethod
    def salvar_parametros_venda(
        *,
        cliente_padrao_venda: str,
        regra_desconto_venda: str,
        habilitar_venda_rapida_admin: bool,
        permitir_venda_sem_estoque: bool,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            empresa_id = ConfiguracoesModel._obter_empresa_id(cur)

            if empresa_id is not None:
                cur.execute(
                    """
                    UPDATE config_empresa
                    SET cliente_padrao_venda = %s,
                        regra_desconto_venda = %s,
                        habilitar_venda_rapida_admin = %s,
                        permitir_venda_sem_estoque = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (
                        cliente_padrao_venda,
                        regra_desconto_venda,
                        bool_para_flag(habilitar_venda_rapida_admin),
                        bool_para_flag(permitir_venda_sem_estoque),
                        empresa_id,
                    ),
                )
            else:
                ph = ConfiguracoesModel._empresa_placeholder()
                cur.execute(
                    """
                    INSERT INTO config_empresa
                        (
                            razao_social,
                            nome_fantasia,
                            cliente_padrao_venda,
                            regra_desconto_venda,
                            habilitar_venda_rapida_admin,
                            permitir_venda_sem_estoque,
                            createdAt,
                            updatedAt
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        *ph,
                        cliente_padrao_venda,
                        regra_desconto_venda,
                        bool_para_flag(habilitar_venda_rapida_admin),
                        bool_para_flag(permitir_venda_sem_estoque),
                    ),
                )
    @staticmethod
    def salvar_parametros_caixa(
        *,
        fundo_inicial_sugerido: float,
        exigir_admin_sangria: bool,
        exigir_admin_reembolso: bool,
        exigir_admin_diferenca_fechamento: bool,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            empresa_id = ConfiguracoesModel._obter_empresa_id(cur)

            if empresa_id is not None:
                cur.execute(
                    """
                    UPDATE config_empresa
                    SET fundo_inicial_sugerido = %s,
                        exigir_admin_sangria = %s,
                        exigir_admin_reembolso = %s,
                        exigir_admin_diferenca_fechamento = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (
                        fundo_inicial_sugerido,
                        bool_para_flag(exigir_admin_sangria),
                        bool_para_flag(exigir_admin_reembolso),
                        bool_para_flag(exigir_admin_diferenca_fechamento),
                        empresa_id,
                    ),
                )
            else:
                ph = ConfiguracoesModel._empresa_placeholder()
                cur.execute(
                    """
                    INSERT INTO config_empresa
                        (
                            razao_social,
                            nome_fantasia,
                            fundo_inicial_sugerido,
                            exigir_admin_sangria,
                            exigir_admin_reembolso,
                            exigir_admin_diferenca_fechamento,
                            createdAt,
                            updatedAt
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        *ph,
                        fundo_inicial_sugerido,
                        bool_para_flag(exigir_admin_sangria),
                        bool_para_flag(exigir_admin_reembolso),
                        bool_para_flag(exigir_admin_diferenca_fechamento),
                    ),
                )
    @staticmethod
    def salvar_parametros_promocoes(
        *,
        prioridade_promocional: str,
        bloquear_promocoes_simultaneas: bool,
        ativar_promocoes_por_vigencia: bool,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            empresa_id = ConfiguracoesModel._obter_empresa_id(cur)

            if empresa_id is not None:
                cur.execute(
                    """
                    UPDATE config_empresa
                    SET prioridade_promocional = %s,
                        bloquear_promocoes_simultaneas = %s,
                        ativar_promocoes_por_vigencia = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (
                        prioridade_promocional,
                        bool_para_flag(bloquear_promocoes_simultaneas),
                        bool_para_flag(ativar_promocoes_por_vigencia),
                        empresa_id,
                    ),
                )
            else:
                ph = ConfiguracoesModel._empresa_placeholder()
                cur.execute(
                    """
                    INSERT INTO config_empresa
                        (
                            razao_social,
                            nome_fantasia,
                            prioridade_promocional,
                            bloquear_promocoes_simultaneas,
                            ativar_promocoes_por_vigencia,
                            createdAt,
                            updatedAt
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        *ph,
                        prioridade_promocional,
                        bool_para_flag(bloquear_promocoes_simultaneas),
                        bool_para_flag(ativar_promocoes_por_vigencia),
                    ),
                )
    @staticmethod
    def salvar_parametros_seguranca(
        *,
        horas_sessao_persistida: int,
        restaurar_login_automaticamente: bool,
        bloquear_fechamento_programa_caixa_aberto: bool,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            empresa_id = ConfiguracoesModel._obter_empresa_id(cur)

            if empresa_id is not None:
                cur.execute(
                    """
                    UPDATE config_empresa
                    SET horas_sessao_persistida = %s,
                        restaurar_login_automaticamente = %s,
                        bloquear_fechamento_programa_caixa_aberto = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (
                        int(horas_sessao_persistida),
                        bool_para_flag(restaurar_login_automaticamente),
                        bool_para_flag(bloquear_fechamento_programa_caixa_aberto),
                        empresa_id,
                    ),
                )
            else:
                ph = ConfiguracoesModel._empresa_placeholder()
                cur.execute(
                    """
                    INSERT INTO config_empresa
                        (
                            razao_social,
                            nome_fantasia,
                            horas_sessao_persistida,
                            restaurar_login_automaticamente,
                            bloquear_fechamento_programa_caixa_aberto,
                            createdAt,
                            updatedAt
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        *ph,
                        int(horas_sessao_persistida),
                        bool_para_flag(restaurar_login_automaticamente),
                        bool_para_flag(bloquear_fechamento_programa_caixa_aberto),
                    ),
                )
    @staticmethod
    def salvar_parametros_sistema(
        *,
        intervalo_backup_horas: int,
        perfil_log: str,
        versao_referencia: str,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            empresa_id = ConfiguracoesModel._obter_empresa_id(cur)

            if empresa_id is not None:
                cur.execute(
                    """
                    UPDATE config_empresa
                    SET intervalo_backup_horas = %s,
                        perfil_log = %s,
                        versao_referencia = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (
                        int(intervalo_backup_horas),
                        perfil_log,
                        versao_referencia,
                        empresa_id,
                    ),
                )
            else:
                ph = ConfiguracoesModel._empresa_placeholder()
                cur.execute(
                    """
                    INSERT INTO config_empresa
                        (
                            razao_social,
                            nome_fantasia,
                            intervalo_backup_horas,
                            perfil_log,
                            versao_referencia,
                            createdAt,
                            updatedAt
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        *ph,
                        int(intervalo_backup_horas),
                        perfil_log,
                        versao_referencia,
                    ),
                )
    @staticmethod
    def salvar_parametros_fiscais(
        *,
        regime_tributario_padrao: str,
        origem_mercadoria_padrao: str,
        cfop_venda_padrao: str,
        cfop_devolucao_padrao: str,
        csosn_cst_padrao: str,
        natureza_operacao_padrao: str,
        exigir_ncm_cest_produto: bool,
        exigir_unidade_tributavel_produto: bool,
    ) -> None:
        with db_transaction(dictionary=False) as cur:
            empresa_id = ConfiguracoesModel._obter_empresa_id(cur)

            payload = (
                regime_tributario_padrao,
                origem_mercadoria_padrao,
                cfop_venda_padrao,
                cfop_devolucao_padrao,
                csosn_cst_padrao,
                natureza_operacao_padrao,
                FLAG_SIM if exigir_ncm_cest_produto else FLAG_NAO,
                FLAG_SIM if exigir_unidade_tributavel_produto else FLAG_NAO,
            )

            if empresa_id is not None:
                cur.execute(
                    """
                    UPDATE config_empresa
                    SET regime_tributario_padrao = %s,
                        origem_mercadoria_padrao = %s,
                        cfop_venda_padrao = %s,
                        cfop_devolucao_padrao = %s,
                        csosn_cst_padrao = %s,
                        natureza_operacao_padrao = %s,
                        exigir_ncm_cest_produto = %s,
                        exigir_unidade_tributavel_produto = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (*payload, empresa_id),
                )
            else:
                ph = ConfiguracoesModel._empresa_placeholder()
                cur.execute(
                    """
                    INSERT INTO config_empresa
                        (
                            razao_social,
                            nome_fantasia,
                            regime_tributario_padrao,
                            origem_mercadoria_padrao,
                            cfop_venda_padrao,
                            cfop_devolucao_padrao,
                            csosn_cst_padrao,
                            natureza_operacao_padrao,
                            exigir_ncm_cest_produto,
                            exigir_unidade_tributavel_produto,
                            createdAt,
                            updatedAt
                        )
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        *ph,
                        *payload,
                    ),
                )
