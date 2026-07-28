from __future__ import annotations

from typing import Any, cast

from database.connection import db_cursor, db_transaction

class FormaPagamentoModel:
    @staticmethod
    def listar() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome,
                    tipo_sefaz,
                    permite_parcelamento,
                    taxa_administrativa,
                    ativo
                FROM formas_pagamento
                ORDER BY nome
                """
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def buscar_por_id(forma_pagamento_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome,
                    tipo_sefaz,
                    permite_parcelamento,
                    taxa_administrativa,
                    ativo
                FROM formas_pagamento
                WHERE id = %s
                LIMIT 1
                """,
                (int(forma_pagamento_id),),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def buscar_por_nome(nome: str) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, nome, tipo_sefaz, permite_parcelamento, taxa_administrativa, ativo
                FROM formas_pagamento
                WHERE UPPER(TRIM(nome)) = UPPER(TRIM(%s))
                LIMIT 1
                """,
                (nome,),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def inserir(dados: dict[str, Any]) -> int | None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                INSERT INTO formas_pagamento
                    (nome, tipo_sefaz, permite_parcelamento, taxa_administrativa, ativo, createdAt, updatedAt)
                VALUES
                    (%(nome)s, %(tipo_sefaz)s, %(permite_parcelamento)s, %(taxa_administrativa)s, %(ativo)s, NOW(), NOW())
                """,
                dados,
            )
            return cur.lastrowid
    @staticmethod
    def atualizar(forma_pagamento_id: int, dados: dict[str, Any]) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE formas_pagamento
                SET
                    nome = %(nome)s,
                    tipo_sefaz = %(tipo_sefaz)s,
                    permite_parcelamento = %(permite_parcelamento)s,
                    taxa_administrativa = %(taxa_administrativa)s,
                    ativo = %(ativo)s,
                    updatedAt = NOW()
                WHERE id = %(id)s
                """,
                {**dados, "id": int(forma_pagamento_id)},
            )
            return cur.rowcount > 0
    @staticmethod
    def atualizar_status(forma_pagamento_id: int, ativo: str) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                "UPDATE formas_pagamento SET ativo = %s WHERE id = %s",
                (ativo, int(forma_pagamento_id)),
            )
            return cur.rowcount > 0
