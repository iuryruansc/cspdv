from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.estoque.models.estoque_model import EstoqueModel


class EstoqueService:
    @staticmethod
    def listar_categorias() -> List[Dict[str, Any]]:
        try:
            return EstoqueModel.listar_categorias()
        except Exception as exc:
            print(f"Erro ao listar categorias do estoque: {exc}")
            return []

    @staticmethod
    def listar_fornecedores() -> List[Dict[str, Any]]:
        try:
            return EstoqueModel.listar_fornecedores()
        except Exception as exc:
            print(f"Erro ao listar fornecedores do estoque: {exc}")
            return []

    @staticmethod
    def obter_metricas() -> Dict[str, int]:
        try:
            return EstoqueModel.obter_metricas()
        except Exception as exc:
            print(f"Erro ao carregar metricas do estoque: {exc}")
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
        categoria_id: Optional[int] = None,
        fornecedor_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        try:
            return EstoqueModel.listar_produtos_lotes(
                busca=busca,
                categoria_id=categoria_id,
                fornecedor_id=fornecedor_id,
            )
        except Exception as exc:
            print(f"Erro ao listar produtos e lotes: {exc}")
            return []

    @staticmethod
    def listar_movimentacoes_recentes() -> List[Dict[str, Any]]:
        try:
            return EstoqueModel.listar_movimentacoes_recentes()
        except Exception as exc:
            print(f"Erro ao listar movimentacoes do estoque: {exc}")
            return []
