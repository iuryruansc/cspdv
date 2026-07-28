from __future__ import annotations

from typing import Any

from modules.marcas.models.marca_model import MarcaModel
from modules.shared.constants import ResultadoOperacao
from modules.shared.services.simple_named_status_service import (
    alternar_status_entidade_simples,
    atualizar_entidade_simples,
    cadastrar_entidade_simples,
    validar_entidade_simples,
)

class MarcaService:
    @staticmethod
    def _validar_dados(dados: dict[str, Any]) -> ResultadoOperacao:
        return validar_entidade_simples(
            dados,
            nome_campo="nome_marca",
            entidade="marca",
        )

    @staticmethod
    def cadastrar_marca(dados: dict[str, Any]) -> ResultadoOperacao:
        return cadastrar_entidade_simples(
            dados,
            nome_campo="nome_marca",
            entidade="marca",
            inserir_fn=MarcaModel.inserir,
        )

    @staticmethod
    def atualizar_marca(marca_id: int, dados: dict[str, Any]) -> ResultadoOperacao:
        return atualizar_entidade_simples(
            int(marca_id),
            dados,
            nome_campo="nome_marca",
            entidade="marca",
            atualizar_fn=MarcaModel.atualizar,
        )

    @staticmethod
    def alternar_status(marca_id: int) -> ResultadoOperacao:
        return alternar_status_entidade_simples(
            int(marca_id),
            entidade="marca",
            buscar_fn=MarcaModel.buscar_por_id,
            atualizar_status_fn=MarcaModel.atualizar_status,
        )
