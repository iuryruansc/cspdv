from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.migrations.runner import CursorLike

VERSION = "20260517_007"
DESCRIPTION = "Padroniza regras referenciais para vinculos historicos"

def _referential_constraints(cursor: CursorLike, table_name: str) -> dict[str, tuple[str, str]]:
    cursor.execute(
        """
        SELECT CONSTRAINT_NAME, UPDATE_RULE, DELETE_RULE
        FROM information_schema.REFERENTIAL_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
        """,
        (table_name,),
    )
    rows = cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())
    resultado: dict[str, tuple[str, str]] = {}
    for row in rows:
        if not row:
            continue
        if isinstance(row, Mapping):
            nome = str(row.get("CONSTRAINT_NAME") or "")
            update_rule = str(row.get("UPDATE_RULE") or "")
            delete_rule = str(row.get("DELETE_RULE") or "")
        else:
            nome = str(row[0] or "")
            update_rule = str(row[1] or "")
            delete_rule = str(row[2] or "")
        resultado[nome] = (update_rule.upper(), delete_rule.upper())
    return resultado

def _ensure_fk(
    cursor: CursorLike,
    *,
    table_name: str,
    constraint_name: str,
    add_sql: str,
    expected_update_rule: str,
    expected_delete_rule: str,
) -> None:
    constraints = _referential_constraints(cursor, table_name)
    atual = constraints.get(constraint_name)
    esperado = (expected_update_rule.upper(), expected_delete_rule.upper())
    if atual == esperado:
        return
    if atual is not None:
        cursor.execute(f"ALTER TABLE {table_name} DROP FOREIGN KEY {constraint_name}")
    cursor.execute(add_sql)

def apply(cursor: CursorLike) -> None:
    _ensure_fk(
        cursor,
        table_name="vendas",
        constraint_name="fk_vendas_usuario",
        add_sql="""
            ALTER TABLE vendas
            ADD CONSTRAINT fk_vendas_usuario
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            ON DELETE SET NULL
            ON UPDATE RESTRICT
        """,
        expected_update_rule="RESTRICT",
        expected_delete_rule="SET NULL",
    )
    _ensure_fk(
        cursor,
        table_name="contas_receber",
        constraint_name="fk_contas_receber_caixa",
        add_sql="""
            ALTER TABLE contas_receber
            ADD CONSTRAINT fk_contas_receber_caixa
            FOREIGN KEY (caixa_id) REFERENCES caixas (id)
            ON DELETE SET NULL
            ON UPDATE RESTRICT
        """,
        expected_update_rule="RESTRICT",
        expected_delete_rule="SET NULL",
    )
    _ensure_fk(
        cursor,
        table_name="venda_reembolsos",
        constraint_name="fk_venda_reembolsos_usuario_aut",
        add_sql="""
            ALTER TABLE venda_reembolsos
            ADD CONSTRAINT fk_venda_reembolsos_usuario_aut
            FOREIGN KEY (usuario_autorizador_id) REFERENCES usuarios (id)
            ON DELETE SET NULL
            ON UPDATE RESTRICT
        """,
        expected_update_rule="RESTRICT",
        expected_delete_rule="SET NULL",
    )
