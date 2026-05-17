from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.seeds.runner import SeedCursorLike

VERSION = "20260517_001"
DESCRIPTION = "Carga dados base operacionais: formas de pagamento, unidades e motivos de caixa"

FORMAS_PAGAMENTO = [
    {"nome": "Dinheiro", "tipo_sefaz": "01", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    {"nome": "PIX", "tipo_sefaz": "17", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    {"nome": "Cartao Debito", "tipo_sefaz": "04", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    {"nome": "Cartao Credito", "tipo_sefaz": "03", "permite_parcelamento": "S", "taxa_administrativa": 0.00},
    {"nome": "Vale Refeicao", "tipo_sefaz": "10", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    {"nome": "Cheque", "tipo_sefaz": "02", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
]

UNIDADES = [
    {"sigla": "UN", "descricao": "Unidade", "codigo_sefaz": None, "fracionavel": 0},
    {"sigla": "CX", "descricao": "Caixa", "codigo_sefaz": None, "fracionavel": 0},
    {"sigla": "FD", "descricao": "Fardo", "codigo_sefaz": None, "fracionavel": 0},
]

CAIXA_MOTIVOS = [
    {"descricao": "Sangria", "tipo_padrao": "sangria"},
    {"descricao": "Suprimento", "tipo_padrao": "suprimento"},
    {"descricao": "Reforco de Troco", "tipo_padrao": "troco"},
]

def _rows(cursor: SeedCursorLike) -> Sequence[Sequence[Any] | Mapping[str, Any]]:
    return cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())


def _exists_by_name(cursor: SeedCursorLike, table_name: str, column_name: str, value: str) -> bool:
    cursor.execute(
        f"SELECT 1 FROM {table_name} WHERE UPPER(TRIM({column_name})) = UPPER(TRIM(%s)) LIMIT 1",
        (value,),
    )
    return bool(_rows(cursor))

def apply(cursor: SeedCursorLike) -> None:
    for forma in FORMAS_PAGAMENTO:
        if _exists_by_name(cursor, "formas_pagamento", "nome", str(forma["nome"])):
            continue
        cursor.execute(
            """
            INSERT INTO formas_pagamento
                (nome, tipo_sefaz, permite_parcelamento, taxa_administrativa, ativo, createdAt, updatedAt)
            VALUES
                (%s, %s, %s, %s, 'S', NOW(), NOW())
            """,
            (
                forma["nome"],
                forma["tipo_sefaz"],
                forma["permite_parcelamento"],
                forma["taxa_administrativa"],
            ),
        )

    for unidade in UNIDADES:
        if _exists_by_name(cursor, "unidades_medida", "sigla", str(unidade["sigla"])):
            continue
        cursor.execute(
            """
            INSERT INTO unidades_medida
                (sigla, descricao, codigo_sefaz, `fracionável`, ativo, createdAt, updatedAt)
            VALUES
                (%s, %s, %s, %s, 'S', NOW(), NOW())
            """,
            (
                unidade["sigla"],
                unidade["descricao"],
                unidade["codigo_sefaz"],
                unidade["fracionavel"],
            ),
        )

    for motivo in CAIXA_MOTIVOS:
        if _exists_by_name(cursor, "caixa_motivos", "tipo_padrao", str(motivo["tipo_padrao"])):
            continue
        cursor.execute(
            """
            INSERT INTO caixa_motivos
                (descricao, tipo_padrao, ativo, createdAt, updatedAt)
            VALUES
                (%s, %s, 'S', NOW(), NOW())
            """,
            (
                motivo["descricao"],
                motivo["tipo_padrao"],
            ),
        )
