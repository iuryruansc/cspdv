from __future__ import annotations

from typing import Any

from modules.categorias.models.categoria_model import CategoriaModel
from modules.shared.constants import ResultadoOperacao
from modules.shared.services.simple_named_status_service import (
    alternar_status_entidade_simples,
    atualizar_entidade_simples,
    cadastrar_entidade_simples,
    validar_entidade_simples,
)

class CategoriaService:
    @staticmethod
    def _validar_dados(dados: dict[str, Any]) -> ResultadoOperacao:
        return validar_entidade_simples(
            dados,
            nome_campo="nome",
            entidade="categoria",
        )

    @staticmethod
    def cadastrar_categoria(dados: dict[str, Any]) -> ResultadoOperacao:
        return cadastrar_entidade_simples(
            dados,
            nome_campo="nome",
            entidade="categoria",
            inserir_fn=CategoriaModel.inserir,
        )

    @staticmethod
    def atualizar_categoria(categoria_id: int, dados: dict[str, Any]) -> ResultadoOperacao:
        return atualizar_entidade_simples(
            int(categoria_id),
            dados,
            nome_campo="nome",
            entidade="categoria",
            atualizar_fn=CategoriaModel.atualizar,
        )

    @staticmethod
    def alternar_status(categoria_id: int) -> ResultadoOperacao:
        return alternar_status_entidade_simples(
            int(categoria_id),
            entidade="categoria",
            buscar_fn=CategoriaModel.buscar_por_id,
            atualizar_status_fn=CategoriaModel.atualizar_status,
        )
