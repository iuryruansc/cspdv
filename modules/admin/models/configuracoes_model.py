from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, cast

from database.connection import get_connection


class ConfiguracoesModel:
    @staticmethod
    def _registro_id(row: object) -> int | None:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes, bytearray)) or not row:
            return None

        valor = row[0]
        if valor is None:
            return None

        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def listar_pdvs() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, identificacao, descricao, status, ativo
                FROM pdvs
                WHERE COALESCE(ativo, 'S') = 'S'
                ORDER BY identificacao
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def carregar_empresa_pdv() -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
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
            registro = cast(Optional[Dict[str, Any]], cursor.fetchone()) or {}
            return {
                "id": registro.get("id"),
                "razao_social": str(registro.get("razao_social") or ""),
                "pdv_padrao_id": registro.get("pdv_padrao_id"),
                "moeda_padrao": str(registro.get("moeda_padrao") or "BRL"),
                "regime_tributario_padrao": str(
                    registro.get("regime_tributario_padrao") or "SIMPLES_NACIONAL"
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
                "exigir_ncm_cest_produto": str(
                    registro.get("exigir_ncm_cest_produto") or "S"
                ).strip().upper()
                == "S",
                "exigir_unidade_tributavel_produto": str(
                    registro.get("exigir_unidade_tributavel_produto") or "S"
                ).strip().upper()
                == "S",
                "cliente_padrao_venda": str(registro.get("cliente_padrao_venda") or "CONSUMIDOR_FINAL"),
                "regra_desconto_venda": str(registro.get("regra_desconto_venda") or "PERMITIR_DESCONTO"),
                "habilitar_venda_rapida_admin": str(
                    registro.get("habilitar_venda_rapida_admin") or "S"
                ).strip().upper()
                == "S",
                "permitir_venda_sem_estoque": str(
                    registro.get("permitir_venda_sem_estoque") or "N"
                ).strip().upper()
                == "S",
                "fundo_inicial_sugerido": float(registro.get("fundo_inicial_sugerido") or 0.0),
                "exigir_admin_sangria": str(registro.get("exigir_admin_sangria") or "S").strip().upper() == "S",
                "exigir_admin_reembolso": str(registro.get("exigir_admin_reembolso") or "S").strip().upper() == "S",
                "exigir_admin_diferenca_fechamento": str(
                    registro.get("exigir_admin_diferenca_fechamento") or "S"
                ).strip().upper()
                == "S",
                "prioridade_promocional": str(
                    registro.get("prioridade_promocional") or "PROMOCAO_ANTES_DESCONTO"
                ),
                "bloquear_promocoes_simultaneas": str(
                    registro.get("bloquear_promocoes_simultaneas") or "S"
                ).strip().upper()
                == "S",
                "ativar_promocoes_por_vigencia": str(
                    registro.get("ativar_promocoes_por_vigencia") or "S"
                ).strip().upper()
                == "S",
                "horas_sessao_persistida": int(registro.get("horas_sessao_persistida") or 12),
                "restaurar_login_automaticamente": str(
                    registro.get("restaurar_login_automaticamente") or "S"
                ).strip().upper()
                == "S",
                "bloquear_fechamento_programa_caixa_aberto": str(
                    registro.get("bloquear_fechamento_programa_caixa_aberto") or "S"
                ).strip().upper()
                == "S",
                "intervalo_backup_horas": int(registro.get("intervalo_backup_horas") or 24),
                "perfil_log": str(registro.get("perfil_log") or "OPERACIONAL"),
                "versao_referencia": str(registro.get("versao_referencia") or "CSPdv v1.0.0"),
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def salvar_empresa_pdv(*, razao_social: str, pdv_padrao_id: Optional[int], moeda_padrao: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM config_empresa ORDER BY id LIMIT 1")
            row = cast(object, cursor.fetchone())
            registro_id = ConfiguracoesModel._registro_id(row)

            if registro_id is not None:
                cursor.execute(
                    """
                    UPDATE config_empresa
                    SET razao_social = %s,
                        pdv_padrao_id = %s,
                        moeda_padrao = %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (razao_social, pdv_padrao_id, moeda_padrao, registro_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO config_empresa
                        (razao_social, nome_fantasia, pdv_padrao_id, moeda_padrao, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, %s, NOW(), NOW())
                    """,
                    (razao_social, razao_social, pdv_padrao_id, moeda_padrao),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def salvar_parametros_venda(
        *,
        cliente_padrao_venda: str,
        regra_desconto_venda: str,
        habilitar_venda_rapida_admin: bool,
        permitir_venda_sem_estoque: bool,
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, razao_social, nome_fantasia FROM config_empresa ORDER BY id LIMIT 1")
            row = cast(object, cursor.fetchone())
            registro_id = ConfiguracoesModel._registro_id(row)

            if registro_id is not None:
                cursor.execute(
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
                        "S" if habilitar_venda_rapida_admin else "N",
                        "S" if permitir_venda_sem_estoque else "N",
                        registro_id,
                    ),
                )
            else:
                cursor.execute(
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
                        "Empresa em configuração",
                        "Empresa em configuração",
                        cliente_padrao_venda,
                        regra_desconto_venda,
                        "S" if habilitar_venda_rapida_admin else "N",
                        "S" if permitir_venda_sem_estoque else "N",
                    ),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def salvar_parametros_caixa(
        *,
        fundo_inicial_sugerido: float,
        exigir_admin_sangria: bool,
        exigir_admin_reembolso: bool,
        exigir_admin_diferenca_fechamento: bool,
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, razao_social, nome_fantasia FROM config_empresa ORDER BY id LIMIT 1")
            row = cast(object, cursor.fetchone())
            registro_id = ConfiguracoesModel._registro_id(row)

            if registro_id is not None:
                cursor.execute(
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
                        "S" if exigir_admin_sangria else "N",
                        "S" if exigir_admin_reembolso else "N",
                        "S" if exigir_admin_diferenca_fechamento else "N",
                        registro_id,
                    ),
                )
            else:
                cursor.execute(
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
                        "Empresa em configuração",
                        "Empresa em configuração",
                        fundo_inicial_sugerido,
                        "S" if exigir_admin_sangria else "N",
                        "S" if exigir_admin_reembolso else "N",
                        "S" if exigir_admin_diferenca_fechamento else "N",
                    ),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def salvar_parametros_promocoes(
        *,
        prioridade_promocional: str,
        bloquear_promocoes_simultaneas: bool,
        ativar_promocoes_por_vigencia: bool,
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, razao_social, nome_fantasia FROM config_empresa ORDER BY id LIMIT 1")
            row = cast(object, cursor.fetchone())
            registro_id = ConfiguracoesModel._registro_id(row)

            if registro_id is not None:
                cursor.execute(
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
                        "S" if bloquear_promocoes_simultaneas else "N",
                        "S" if ativar_promocoes_por_vigencia else "N",
                        registro_id,
                    ),
                )
            else:
                cursor.execute(
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
                        "Empresa em configuração",
                        "Empresa em configuração",
                        prioridade_promocional,
                        "S" if bloquear_promocoes_simultaneas else "N",
                        "S" if ativar_promocoes_por_vigencia else "N",
                    ),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def salvar_parametros_seguranca(
        *,
        horas_sessao_persistida: int,
        restaurar_login_automaticamente: bool,
        bloquear_fechamento_programa_caixa_aberto: bool,
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, razao_social, nome_fantasia FROM config_empresa ORDER BY id LIMIT 1")
            row = cast(object, cursor.fetchone())
            registro_id = ConfiguracoesModel._registro_id(row)

            if registro_id is not None:
                cursor.execute(
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
                        "S" if restaurar_login_automaticamente else "N",
                        "S" if bloquear_fechamento_programa_caixa_aberto else "N",
                        registro_id,
                    ),
                )
            else:
                cursor.execute(
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
                        "Empresa em configuração",
                        "Empresa em configuração",
                        int(horas_sessao_persistida),
                        "S" if restaurar_login_automaticamente else "N",
                        "S" if bloquear_fechamento_programa_caixa_aberto else "N",
                    ),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def salvar_parametros_sistema(
        *,
        intervalo_backup_horas: int,
        perfil_log: str,
        versao_referencia: str,
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, razao_social, nome_fantasia FROM config_empresa ORDER BY id LIMIT 1")
            row = cast(object, cursor.fetchone())
            registro_id = ConfiguracoesModel._registro_id(row)

            if registro_id is not None:
                cursor.execute(
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
                        registro_id,
                    ),
                )
            else:
                cursor.execute(
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
                        "Empresa em configuração",
                        "Empresa em configuração",
                        int(intervalo_backup_horas),
                        perfil_log,
                        versao_referencia,
                    ),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

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
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, razao_social, nome_fantasia FROM config_empresa ORDER BY id LIMIT 1")
            row = cast(object, cursor.fetchone())
            registro_id = ConfiguracoesModel._registro_id(row)

            payload = (
                regime_tributario_padrao,
                origem_mercadoria_padrao,
                cfop_venda_padrao,
                cfop_devolucao_padrao,
                csosn_cst_padrao,
                natureza_operacao_padrao,
                "S" if exigir_ncm_cest_produto else "N",
                "S" if exigir_unidade_tributavel_produto else "N",
            )

            if registro_id is not None:
                cursor.execute(
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
                    (*payload, registro_id),
                )
            else:
                cursor.execute(
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
                        "Empresa em configuração",
                        "Empresa em configuração",
                        *payload,
                    ),
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

