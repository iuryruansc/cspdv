from typing import Any, Dict, List, Optional

from modules.shared.models.simple_named_status_model import (
    atualizar_registro,
    atualizar_status_registro,
    buscar_registro_por_id,
    inserir_registro,
    listar_registros,
)

class CategoriaModel:
    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        return listar_registros(
            table="categorias",
            id_column="id",
            name_column="nome",
        )

    @staticmethod
    def inserir(dados: Dict[str, Any]) -> Optional[int]:
        return inserir_registro(
            table="categorias",
            columns=("nome", "ativo"),
            dados=dados,
        )

    @staticmethod
    def buscar_por_id(categoria_id: int) -> Optional[Dict[str, Any]]:
        return buscar_registro_por_id(
            table="categorias",
            id_column="id",
            columns=("id", "nome", "ativo"),
            record_id=categoria_id,
        )

    @staticmethod
    def atualizar(categoria_id: int, dados: Dict[str, Any]) -> bool:
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
