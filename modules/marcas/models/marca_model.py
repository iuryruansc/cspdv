from __future__ import annotations

from typing import Any

from modules.shared.models.simple_named_status_model import (
    atualizar_registro,
    atualizar_status_registro,
    buscar_registro_por_id,
    inserir_registro,
    listar_registros,
)

class MarcaModel:
    @staticmethod
    def listar() -> list[dict[str, Any]]:
        return listar_registros(
            table="marcas",
            id_column="id",
            name_column="nome_marca",
        )

    @staticmethod
    def inserir(dados: dict[str, Any]) -> int | None:
        return inserir_registro(
            table="marcas",
            columns=("nome_marca", "ativo"),
            dados=dados,
        )

    @staticmethod
    def buscar_por_id(marca_id: int) -> dict[str, Any] | None:
        return buscar_registro_por_id(
            table="marcas",
            id_column="id",
            columns=("id", "nome_marca", "ativo"),
            record_id=marca_id,
        )

    @staticmethod
    def atualizar(marca_id: int, dados: dict[str, Any]) -> bool:
        return atualizar_registro(
            table="marcas",
            id_column="id",
            columns=("nome_marca", "ativo"),
            record_id=marca_id,
            dados=dados,
        )

    @staticmethod
    def atualizar_status(marca_id: int, ativo: str) -> bool:
        return atualizar_status_registro(
            table="marcas",
            id_column="id",
            status_column="ativo",
            record_id=marca_id,
            ativo=ativo,
        )
