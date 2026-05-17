from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_001"
DESCRIPTION = "Padroniza colunas operacionais, fiscais e de configuracao em config_empresa"

def _add_column_if_missing(cursor: CursorLike, column_name: str, ddl: str) -> None:
    cursor.execute("SHOW COLUMNS FROM config_empresa")
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    colunas = {
        str(coluna["Field"] if isinstance(coluna, Mapping) else coluna[0])
        for coluna in rows
        if coluna
    }
    if column_name not in colunas:
        cursor.execute(ddl)

def apply(cursor: CursorLike) -> None:
    _add_column_if_missing(cursor, "pdv_padrao_id", "ALTER TABLE config_empresa ADD COLUMN pdv_padrao_id INT NULL")
    _add_column_if_missing(
        cursor,
        "moeda_padrao",
        "ALTER TABLE config_empresa ADD COLUMN moeda_padrao VARCHAR(10) NULL DEFAULT 'BRL'",
    )
    _add_column_if_missing(
        cursor,
        "regime_tributario_padrao",
        "ALTER TABLE config_empresa ADD COLUMN regime_tributario_padrao VARCHAR(40) NULL DEFAULT 'SIMPLES_NACIONAL'",
    )
    _add_column_if_missing(
        cursor,
        "origem_mercadoria_padrao",
        "ALTER TABLE config_empresa ADD COLUMN origem_mercadoria_padrao VARCHAR(5) NULL DEFAULT '0'",
    )
    _add_column_if_missing(
        cursor,
        "cfop_venda_padrao",
        "ALTER TABLE config_empresa ADD COLUMN cfop_venda_padrao VARCHAR(10) NULL DEFAULT '5102'",
    )
    _add_column_if_missing(
        cursor,
        "cfop_devolucao_padrao",
        "ALTER TABLE config_empresa ADD COLUMN cfop_devolucao_padrao VARCHAR(10) NULL DEFAULT '1202'",
    )
    _add_column_if_missing(
        cursor,
        "csosn_cst_padrao",
        "ALTER TABLE config_empresa ADD COLUMN csosn_cst_padrao VARCHAR(10) NULL DEFAULT '102'",
    )
    _add_column_if_missing(
        cursor,
        "natureza_operacao_padrao",
        "ALTER TABLE config_empresa ADD COLUMN natureza_operacao_padrao VARCHAR(120) NULL DEFAULT 'VENDA DE MERCADORIA'",
    )
    _add_column_if_missing(
        cursor,
        "exigir_ncm_cest_produto",
        "ALTER TABLE config_empresa ADD COLUMN exigir_ncm_cest_produto CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "exigir_unidade_tributavel_produto",
        "ALTER TABLE config_empresa ADD COLUMN exigir_unidade_tributavel_produto CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "cliente_padrao_venda",
        "ALTER TABLE config_empresa ADD COLUMN cliente_padrao_venda VARCHAR(40) NULL DEFAULT 'CONSUMIDOR_FINAL'",
    )
    _add_column_if_missing(
        cursor,
        "regra_desconto_venda",
        "ALTER TABLE config_empresa ADD COLUMN regra_desconto_venda VARCHAR(40) NULL DEFAULT 'PERMITIR_DESCONTO'",
    )
    _add_column_if_missing(
        cursor,
        "habilitar_venda_rapida_admin",
        "ALTER TABLE config_empresa ADD COLUMN habilitar_venda_rapida_admin CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "permitir_venda_sem_estoque",
        "ALTER TABLE config_empresa ADD COLUMN permitir_venda_sem_estoque CHAR(1) NULL DEFAULT 'N'",
    )
    _add_column_if_missing(
        cursor,
        "fundo_inicial_sugerido",
        "ALTER TABLE config_empresa ADD COLUMN fundo_inicial_sugerido DECIMAL(10,2) NULL DEFAULT 0.00",
    )
    _add_column_if_missing(
        cursor,
        "exigir_admin_sangria",
        "ALTER TABLE config_empresa ADD COLUMN exigir_admin_sangria CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "exigir_admin_reembolso",
        "ALTER TABLE config_empresa ADD COLUMN exigir_admin_reembolso CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "exigir_admin_diferenca_fechamento",
        "ALTER TABLE config_empresa ADD COLUMN exigir_admin_diferenca_fechamento CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "prioridade_promocional",
        "ALTER TABLE config_empresa ADD COLUMN prioridade_promocional VARCHAR(50) NULL DEFAULT 'PROMOCAO_ANTES_DESCONTO'",
    )
    _add_column_if_missing(
        cursor,
        "bloquear_promocoes_simultaneas",
        "ALTER TABLE config_empresa ADD COLUMN bloquear_promocoes_simultaneas CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "ativar_promocoes_por_vigencia",
        "ALTER TABLE config_empresa ADD COLUMN ativar_promocoes_por_vigencia CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "horas_sessao_persistida",
        "ALTER TABLE config_empresa ADD COLUMN horas_sessao_persistida INT NULL DEFAULT 12",
    )
    _add_column_if_missing(
        cursor,
        "restaurar_login_automaticamente",
        "ALTER TABLE config_empresa ADD COLUMN restaurar_login_automaticamente CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "bloquear_fechamento_programa_caixa_aberto",
        "ALTER TABLE config_empresa ADD COLUMN bloquear_fechamento_programa_caixa_aberto CHAR(1) NULL DEFAULT 'S'",
    )
    _add_column_if_missing(
        cursor,
        "intervalo_backup_horas",
        "ALTER TABLE config_empresa ADD COLUMN intervalo_backup_horas INT NULL DEFAULT 24",
    )
    _add_column_if_missing(
        cursor,
        "perfil_log",
        "ALTER TABLE config_empresa ADD COLUMN perfil_log VARCHAR(30) NULL DEFAULT 'OPERACIONAL'",
    )
    _add_column_if_missing(
        cursor,
        "versao_referencia",
        "ALTER TABLE config_empresa ADD COLUMN versao_referencia VARCHAR(60) NULL DEFAULT 'CSPdv v1.0.0'",
    )
