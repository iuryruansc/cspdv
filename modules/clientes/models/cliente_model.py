from __future__ import annotations

from typing import Any, cast

from database.connection import db_cursor, db_transaction

class ClienteModel:
    @staticmethod
    def buscar_consumidor_final() -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome,
                    cpf,
                    telefone,
                    cidade,
                    estado,
                    cliente_sistema,
                    ativo
                FROM clientes
                WHERE cliente_sistema = 'S'
                ORDER BY id
                LIMIT 1
                """
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def buscar_para_venda(termo: str, limite: int = 20) -> list[dict[str, Any]]:
        termo_limpo = str(termo or "").strip()
        termo_nome = f"%{termo_limpo.upper()}%"
        termo_cpf = f"{termo_limpo}%"
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome,
                    cpf,
                    telefone,
                    cidade,
                    estado,
                    cliente_sistema,
                    ativo
                FROM clientes
                WHERE ativo = 'S'
                  AND cliente_sistema = 'N'
                  AND (
                    UPPER(nome) LIKE %s
                    OR cpf LIKE %s
                  )
                ORDER BY
                    CASE
                        WHEN cpf = %s THEN 0
                        WHEN UPPER(nome) = UPPER(%s) THEN 1
                        ELSE 2
                    END,
                    nome
                LIMIT %s
                """,
                (termo_nome, termo_cpf, termo_limpo, termo_limpo, limite),
            )
            return cast(list[dict[str, Any]], cur.fetchall())

    @staticmethod
    def listar_resumo() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome,
                    cpf,
                    telefone,
                    cidade,
                    estado,
                    cliente_sistema,
                    ativo
                FROM clientes
                ORDER BY nome
                """
            )
            return cast(list[dict[str, Any]], cur.fetchall())
    @staticmethod
    def buscar_por_id(cliente_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome,
                    email,
                    telefone,
                    cpf,
                    logradouro,
                    numero,
                    bairro,
                    cep,
                    cidade,
                    estado,
                    observacao,
                    cliente_sistema,
                    ativo
                FROM clientes
                WHERE id = %s
                LIMIT 1
                """,
                (cliente_id,),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def _sanitizar(dados: dict[str, Any]) -> dict[str, Any]:
        campos_texto = (
            "email", "cpf", "logradouro", "bairro",
            "cep", "cidade", "estado", "observacao",
        )
        copia = dict(dados)
        for campo in campos_texto:
            if copia.get(campo) == "":
                copia[campo] = None
        return copia

    @staticmethod
    def inserir(dados: dict[str, Any]) -> int | None:
        dados = ClienteModel._sanitizar(dados)
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                INSERT INTO clientes
                    (nome, email, telefone, cpf, logradouro, numero,
                     bairro, cep, cidade, estado, observacao, ativo)
                VALUES
                    (%(nome)s, %(email)s, %(telefone)s, %(cpf)s, %(logradouro)s, %(numero)s,
                     %(bairro)s, %(cep)s, %(cidade)s, %(estado)s, %(observacao)s, %(ativo)s)
                """,
                dados,
            )
            return cur.lastrowid
    @staticmethod
    def atualizar(cliente_id: int, dados: dict[str, Any]) -> bool:
        dados = ClienteModel._sanitizar(dados)
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE clientes
                SET nome = %(nome)s,
                    email = %(email)s,
                    telefone = %(telefone)s,
                    cpf = %(cpf)s,
                    logradouro = %(logradouro)s,
                    numero = %(numero)s,
                    bairro = %(bairro)s,
                    cep = %(cep)s,
                    cidade = %(cidade)s,
                    estado = %(estado)s,
                    observacao = %(observacao)s,
                    ativo = %(ativo)s
                WHERE id = %(id)s
                """,
                {**dados, "id": cliente_id},
            )
            return cur.rowcount > 0
    @staticmethod
    def atualizar_status(cliente_id: int, ativo: str) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                "UPDATE clientes SET ativo = %s WHERE id = %s",
                (ativo, cliente_id),
            )
            return cur.rowcount > 0
