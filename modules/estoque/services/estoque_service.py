from __future__ import annotations

from typing import Any

from modules.estoque.models.estoque_model import EstoqueModel
from utils.app_logger import log_error

class EstoqueService:
    @staticmethod
    def listar_categorias() -> list[dict[str, Any]]:
        try:
            return EstoqueModel.listar_categorias()
        except Exception as exc:
            log_error("Erro ao listar categorias do estoque.", exc)
            return []

    @staticmethod
    def listar_fornecedores() -> list[dict[str, Any]]:
        try:
            return EstoqueModel.listar_fornecedores()
        except Exception as exc:
            log_error("Erro ao listar fornecedores do estoque.", exc)
            return []

    @staticmethod
    def obter_metricas() -> dict[str, int]:
        try:
            return EstoqueModel.obter_metricas()
        except Exception as exc:
            log_error("Erro ao carregar métricas do estoque.", exc)
            return {
                "produtos_ativos": 0,
                "lotes_ativos": 0,
                "estoque_critico": 0,
                "movimentacoes_dia": 0,
            }

    @staticmethod
    def listar_produtos_lotes(
        *,
        busca: str = "",
        categoria_id: int | None = None,
        fornecedor_id: int | None = None,
    ) -> list[dict[str, Any]]:
        try:
            return EstoqueModel.listar_produtos_lotes(
                busca=busca,
                categoria_id=categoria_id,
                fornecedor_id=fornecedor_id,
            )
        except Exception as exc:
            log_error("Erro ao listar produtos e lotes do estoque.", exc)
            return []

    @staticmethod
    def listar_movimentacoes_recentes() -> list[dict[str, Any]]:
        try:
            return EstoqueModel.listar_movimentacoes_recentes()
        except Exception as exc:
            log_error("Erro ao listar movimentações recentes do estoque.", exc)
            return []
