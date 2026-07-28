from __future__ import annotations

from typing import Any

from modules.shared.models.simple_named_status_model import (
    atualizar_registro,
    atualizar_status_registro,
    buscar_registro_por_id,
    inserir_registro,
    listar_registros,
)

class CategoriaModel:
    @staticmethod
    def listar() -> list[dict[str, Any]]:
        return listar_registros(
            table="categorias",
            id_column="id",
            name_column="nome",
        )

    @staticmethod
    def inserir(dados: dict[str, Any]) -> int | None:
        return inserir_registro(
            table="categorias",
            columns=("nome", "ativo"),
            dados=dados,
        )

    @staticmethod
    def buscar_por_id(categoria_id: int) -> dict[str, Any] | None:
        return buscar_registro_por_id(
            table="categorias",
            id_column="id",
            columns=("id", "nome", "ativo"),
            record_id=categoria_id,
        )

    @staticmethod
    def atualizar(categoria_id: int, dados: dict[str, Any]) -> bool:
        return atualizar_registro(
            table="categorias",
            id_column="id",
            columns=("nome", "ativo"),
            record_id=categoria_id,
            dados=dados,
        )

    @staticmethod
    def atualizar_status(categoria_id: int, ativo: str) -> bool:
        return atualizar_status_registro(
            table="categorias",
            id_column="id",
            status_column="ativo",
            record_id=categoria_id,
            ativo=ativo,
        )
