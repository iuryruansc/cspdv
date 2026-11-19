from __future__ import annotations

from typing import Any

from modules.estoque.models.estoque_model import EstoqueModel
from modules.clientes.models.cliente_model import ClienteModel
from utils.app_logger import log_error

class EstoqueService:
    @staticmethod
    def listar_clientes_fornecimento() -> list[dict[str, Any]]:
        try:
            clientes = ClienteModel.listar_resumo()
            return [
                cliente
                for cliente in clientes
                if str(cliente.get("ativo") or "N").upper() == "S"
                and str(cliente.get("cliente_sistema") or "N").upper() != "S"
            ]
        except Exception as exc:
            log_error("Erro ao listar destinatários do fornecimento.", exc)
            return []

    @staticmethod
    def buscar_produtos_fornecimento(termo: str) -> list[dict[str, Any]]:
        try:
            return EstoqueModel.buscar_produtos_fornecimento(termo)
        except Exception as exc:
            log_error("Erro ao buscar produtos para fornecimento.", exc)
            return []

    @staticmethod
    def registrar_fornecimento(
        produto_id: int,
        cliente_id: int,
        cliente_nome: str,
        quantidade: int,
        usuario_id: int,
        observacao: str = "",
    ) -> tuple[bool, str]:
        if not usuario_id:
            return False, "Não foi possível identificar o usuário logado."
        try:
            EstoqueModel.registrar_fornecimento(
                produto_id=int(produto_id),
                cliente_id=int(cliente_id),
                cliente_nome=cliente_nome,
                quantidade=int(quantidade),
                usuario_id=int(usuario_id),
                observacao=observacao,
            )
            return True, "Fornecimento registrado com sucesso."
        except Exception as exc:
            return False, f"Não foi possível registrar o fornecimento:\n{exc}"

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
        pagina: int | None = None,
        por_pagina: int = 50,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        try:
            return EstoqueModel.listar_produtos_lotes(
                busca=busca,
                categoria_id=categoria_id,
                fornecedor_id=fornecedor_id,
                pagina=pagina,
                por_pagina=por_pagina,
            )
        except Exception as exc:
            log_error("Erro ao listar produtos e lotes do estoque.", exc)
            if pagina is not None:
                return {"registros": [], "total": 0, "pagina": 1, "por_pagina": por_pagina}
            return []

    @staticmethod
    def listar_movimentacoes_recentes(
        *,
        limite: int = 20,
        tipos: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        try:
            return EstoqueModel.listar_movimentacoes_recentes(limite=limite, tipos=tipos)
        except Exception as exc:
            log_error("Erro ao listar movimentações recentes do estoque.", exc)
            return []

    @staticmethod
    def listar_fornecimentos_recentes() -> list[dict[str, Any]]:
        try:
            return EstoqueModel.listar_fornecimentos_recentes()
        except Exception as exc:
            log_error("Erro ao listar fornecimentos recentes do estoque.", exc)
            return []
