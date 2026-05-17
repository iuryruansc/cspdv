from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.seeds.runner import SeedCursorLike

VERSION = "20260517_002"
DESCRIPTION = "Carga dados base de acesso: cargo administrador, perfil master e permissoes base"

CARGO_ADMIN = "Administrador"
PERFIL_MASTER = {
    "nome": "Admin Master",
    "descricao": "Acesso irrestrito a todos os modulos do sistema",
}
PERMISSOES_BASE = [
    {"chave": "sistema.master", "nome_amigavel": "Acesso Irrestrito (Master)"},
    {"chave": "vendas.pdv", "nome_amigavel": "Acesso ao PDV (Frente de Caixa)"},
    {"chave": "estoque.gerenciar", "nome_amigavel": "Cadastro e Edicao de Produtos"},
    {"chave": "financeiro.total", "nome_amigavel": "Acesso Completo ao Modulo Financeiro"},
    {"chave": "relatorios.ver", "nome_amigavel": "Visualizacao de Relatorios e Dashboards"},
]

def _rows(cursor: SeedCursorLike) -> Sequence[Sequence[Any] | Mapping[str, Any]]:
    return cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())

def _first_value(row: Sequence[Any] | Mapping[str, Any] | None) -> Any | None:
    if row is None:
        return None
    if isinstance(row, Mapping):
        return next(iter(row.values()), None)
    if isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)) and row:
        return row[0]
    return None

def _fetch_id(cursor: SeedCursorLike, sql: str, params: Sequence[Any]) -> int | None:
    cursor.execute(sql, params)
    rows = _rows(cursor)
    if not rows:
        return None
    value = _first_value(rows[0])
    return int(value) if value is not None else None


def apply(cursor: SeedCursorLike) -> None:
    cargo_id = _fetch_id(
        cursor,
        "SELECT id FROM cargos WHERE UPPER(TRIM(nome_cargo)) = UPPER(TRIM(%s)) LIMIT 1",
        (CARGO_ADMIN,),
    )
    if cargo_id is None:
        cursor.execute(
            """
            INSERT INTO cargos (nome_cargo, createdAt, updatedAt, ativo)
            VALUES (%s, NOW(), NOW(), 'S')
            """,
            (CARGO_ADMIN,),
        )

    perfil_id = _fetch_id(
        cursor,
        "SELECT id FROM perfis WHERE UPPER(TRIM(nome)) = UPPER(TRIM(%s)) LIMIT 1",
        (PERFIL_MASTER["nome"],),
    )
    if perfil_id is None:
        cursor.execute(
            """
            INSERT INTO perfis (nome, descricao, ativo, updateAt)
            VALUES (%s, %s, 'S', NOW())
            """,
            (PERFIL_MASTER["nome"], PERFIL_MASTER["descricao"]),
        )

    perfil_id = _fetch_id(
        cursor,
        "SELECT id FROM perfis WHERE UPPER(TRIM(nome)) = UPPER(TRIM(%s)) LIMIT 1",
        (PERFIL_MASTER["nome"],),
    )
    if perfil_id is None:
        raise RuntimeError("Nao foi possivel localizar o perfil base Admin Master apos o seed.")

    for permissao in PERMISSOES_BASE:
        permissao_id = _fetch_id(
            cursor,
            "SELECT id FROM permissoes WHERE UPPER(TRIM(chave)) = UPPER(TRIM(%s)) LIMIT 1",
            (permissao["chave"],),
        )
        if permissao_id is None:
            cursor.execute(
                "INSERT INTO permissoes (chave, nome_amigavel) VALUES (%s, %s)",
                (permissao["chave"], permissao["nome_amigavel"]),
            )
            permissao_id = _fetch_id(
                cursor,
                "SELECT id FROM permissoes WHERE UPPER(TRIM(chave)) = UPPER(TRIM(%s)) LIMIT 1",
                (permissao["chave"],),
            )

        if permissao_id is None:
            raise RuntimeError(f"Nao foi possivel localizar a permissao base {permissao['chave']}.")

        cursor.execute(
            """
            SELECT 1
            FROM perfil_permissoes
            WHERE perfil_id = %s AND permissao_id = %s
            LIMIT 1
            """,
            (perfil_id, permissao_id),
        )
        if not _rows(cursor):
            cursor.execute(
                "INSERT INTO perfil_permissoes (perfil_id, permissao_id) VALUES (%s, %s)",
                (perfil_id, permissao_id),
            )
