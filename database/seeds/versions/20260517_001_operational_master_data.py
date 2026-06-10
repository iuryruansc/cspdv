from __future__ import annotations

from database.seeds.runner import SeedCursorLike

VERSION = "20260517_001"
DESCRIPTION = "Carga dados base operacionais: formas de pagamento, unidades e motivos de caixa"

FORMAS_PAGAMENTO = [
    {"nome": "Dinheiro", "tipo_sefaz": "01", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    {"nome": "PIX", "tipo_sefaz": "17", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    {"nome": "Cartao Debito", "tipo_sefaz": "04", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    {"nome": "Cartao Credito", "tipo_sefaz": "03", "permite_parcelamento": "S", "taxa_administrativa": 0.00},
    {"nome": "Vale Refeicao", "tipo_sefaz": "10", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    {"nome": "Pag. Parcial", "tipo_sefaz": "02", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
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


def apply(cursor: SeedCursorLike) -> None:
    for forma in FORMAS_PAGAMENTO:
        cursor.execute(
            """
            INSERT INTO formas_pagamento
                (nome, tipo_sefaz, permite_parcelamento, taxa_administrativa, ativo, createdAt, updatedAt)
            VALUES
                (%s, %s, %s, %s, 'S', NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                permite_parcelamento = VALUES(permite_parcelamento),
                taxa_administrativa = VALUES(taxa_administrativa),
                updatedAt = NOW()
            """,
            (
                forma["nome"],
                forma["tipo_sefaz"],
                forma["permite_parcelamento"],
                forma["taxa_administrativa"],
            ),
        )

    for unidade in UNIDADES:
        cursor.execute(
            """
            INSERT INTO unidades_medida
                (sigla, descricao, codigo_sefaz, `fracionável`, ativo, createdAt, updatedAt)
            VALUES
                (%s, %s, %s, %s, 'S', NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                descricao = VALUES(descricao),
                codigo_sefaz = VALUES(codigo_sefaz),
                `fracionável` = VALUES(`fracionável`),
                updatedAt = NOW()
            """,
            (
                unidade["sigla"],
                unidade["descricao"],
                unidade["codigo_sefaz"],
                unidade["fracionavel"],
            ),
        )

    for motivo in CAIXA_MOTIVOS:
        cursor.execute(
            """
            INSERT INTO caixa_motivos
                (descricao, tipo_padrao, ativo, createdAt, updatedAt)
            VALUES
                (%s, %s, 'S', NOW(), NOW())
            ON DUPLICATE KEY UPDATE
                descricao = VALUES(descricao),
                updatedAt = NOW()
            """,
            (
                motivo["descricao"],
                motivo["tipo_padrao"],
            ),
        )
