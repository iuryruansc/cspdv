from __future__ import annotations

from typing import Any, cast
from database.connection import db_cursor, db_transaction
from utils.app_logger import log_error

class FornecedorModel:
    @staticmethod
    def listar_resumo() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            try:
                cur.execute(
                    """
                    SELECT
                        id_fornecedor,
                        nome_fantasia,
                        cnpj_cpf,
                        telefone,
                        cidade,
                        estado,
                        ativo
                    FROM fornecedores
                    ORDER BY nome_fantasia
                    """
                )
                return cast(list[dict[str, Any]], cur.fetchall())
            except Exception as e:
                log_error("Erro ao listar fornecedores.", e)
                raise
    @staticmethod
    def inserir(dados: dict[str, Any]) -> int | None:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                INSERT INTO fornecedores
                    (nome_fantasia, razao_social, cnpj_cpf, ie,
                     telefone, email, logradouro, numero,
                     cep, cidade, estado, bairro, ativo, observacao)
                VALUES
                    (%(nome_fantasia)s, %(razao_social)s, %(cnpj_cpf)s, %(ie)s,
                     %(telefone)s, %(email)s, %(logradouro)s, %(numero)s,
                     %(cep)s, %(cidade)s, %(estado)s, %(bairro)s, %(ativo)s, %(observacao)s)
                """,
                dados,
            )
            return cur.lastrowid
    @staticmethod
    def buscar_por_id(fornecedor_id: int) -> dict[str, Any] | None:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    id_fornecedor,
                    nome_fantasia,
                    razao_social,
                    cnpj_cpf,
                    ie,
                    telefone,
                    email,
                    logradouro,
                    numero,
                    cep,
                    cidade,
                    estado,
                    bairro,
                    ativo,
                    observacao
                FROM fornecedores
                WHERE id_fornecedor = %s
                LIMIT 1
                """,
                (fornecedor_id,),
            )
            return cast(dict[str, Any] | None, cur.fetchone())
    @staticmethod
    def atualizar(fornecedor_id: int, dados: dict[str, Any]) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                """
                UPDATE fornecedores
                SET nome_fantasia = %(nome_fantasia)s,
                    razao_social = %(razao_social)s,
                    cnpj_cpf = %(cnpj_cpf)s,
                    ie = %(ie)s,
                    telefone = %(telefone)s,
                    email = %(email)s,
                    logradouro = %(logradouro)s,
                    numero = %(numero)s,
                    cep = %(cep)s,
                    cidade = %(cidade)s,
                    estado = %(estado)s,
                    bairro = %(bairro)s,
                    ativo = %(ativo)s,
                    observacao = %(observacao)s
                WHERE id_fornecedor = %(id_fornecedor)s
                """,
                {**dados, "id_fornecedor": fornecedor_id},
            )
            return cur.rowcount > 0
    @staticmethod
    def atualizar_status(fornecedor_id: int, ativo: str) -> bool:
        with db_transaction(dictionary=False) as cur:
            cur.execute(
                "UPDATE fornecedores SET ativo = %s WHERE id_fornecedor = %s",
                (ativo, fornecedor_id),
            )
            return cur.rowcount > 0
