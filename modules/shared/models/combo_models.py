from __future__ import annotations
from typing import Any, cast

from database.connection import db_cursor

class CategoriaModel:
    @staticmethod
    def listar_ativas() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, nome FROM categorias WHERE ativo = 'S' ORDER BY nome"
            )
            return cast(list[dict[str, Any]], cur.fetchall())

class MarcaModel:
    @staticmethod
    def listar_ativas() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, nome_marca AS nome FROM marcas WHERE ativo = 'S' ORDER BY nome_marca"
            )
            return cast(list[dict[str, Any]], cur.fetchall())

class FornecedorModel:
    @staticmethod
    def listar_ativos() -> list[dict[str, Any]]:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id_fornecedor AS id, nome_fantasia AS nome
                FROM   fornecedores
                WHERE  ativo = 'S'
                ORDER  BY nome_fantasia
                """
            )
            return cast(list[dict[str, Any]], cur.fetchall())

class UnidadeModel:
    @staticmethod
    def listar_ativas() -> list[dict[str, Any]]:
        """Retorna sigla + descricao como texto visivel: 'UN - Unidade'."""
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id,
                       CONCAT(sigla, ' - ', descricao) AS nome
                FROM   unidades_medida
                WHERE  ativo = 'S'
                ORDER  BY sigla
                """
            )
            return cast(list[dict[str, Any]], cur.fetchall())


def listar_categorias_ativas() -> list[dict[str, Any]]:
    return CategoriaModel.listar_ativas()

def listar_marcas_ativas() -> list[dict[str, Any]]:
    return MarcaModel.listar_ativas()

def listar_fornecedores_ativos() -> list[dict[str, Any]]:
    return FornecedorModel.listar_ativos()

def listar_unidades_ativas() -> list[dict[str, Any]]:
    return UnidadeModel.listar_ativas()
