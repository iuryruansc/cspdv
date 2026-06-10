from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from modules.venda.models.pre_venda_model import PreVendaModel


class PreVendaService:

    @staticmethod
    def salvar_pre_venda(
        *,
        usuario_id: int,
        caixa_id: int,
        cliente_id: Optional[int],
        itens: List[Dict[str, Any]],
        desconto_global: float = 0.0,
        desconto_itens: float = 0.0,
        desconto_total: float = 0.0,
        valor_total: float,
    ) -> Tuple[bool, str, Optional[int]]:
        if usuario_id <= 0:
            return False, "Não foi possível identificar o operador.", None
        if caixa_id <= 0:
            return False, "Não há caixa aberto para salvar a pré-venda.", None
        if not itens:
            return False, "Adicione pelo menos um item antes de salvar a pré-venda.", None
        if valor_total <= 0:
            return False, "O total da pré-venda precisa ser maior que zero.", None

        try:
            pre_venda_id = PreVendaModel.salvar_pre_venda(
                usuario_id=usuario_id,
                caixa_id=caixa_id,
                cliente_id=cliente_id,
                itens=itens,
                desconto_global=desconto_global,
                desconto_itens=desconto_itens,
                desconto_total=desconto_total,
                valor_total=valor_total,
            )
            return True, f"Pré-venda #{pre_venda_id} salva com sucesso.", pre_venda_id
        except Exception as exc:
            return False, f"Erro ao salvar pré-venda: {exc}", None

    @staticmethod
    def listar_pre_vendas_pendentes(
        *,
        usuario_id: Optional[int] = None,
        caixa_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        return PreVendaModel.listar_pre_vendas_pendentes(
            usuario_id=usuario_id,
            caixa_id=caixa_id,
        )

    @staticmethod
    def carregar_pre_venda(pre_venda_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        if pre_venda_id <= 0:
            return False, "Pré-venda inválida.", None

        pre_venda = PreVendaModel.carregar_pre_venda(pre_venda_id)
        if not pre_venda:
            return False, "Pré-venda não encontrada.", None
        if pre_venda.get("status") != "PENDENTE":
            return False, "Esta pré-venda já foi importada ou cancelada.", None

        return True, "", pre_venda

    @staticmethod
    def cancelar_pre_venda(pre_venda_id: int) -> Tuple[bool, str]:
        if pre_venda_id <= 0:
            return False, "Pré-venda inválida."

        pre_venda = PreVendaModel.carregar_pre_venda(pre_venda_id)
        if not pre_venda:
            return False, "Pré-venda não encontrada."
        if pre_venda.get("status") != "PENDENTE":
            return False, "Esta pré-venda já foi processada."

        try:
            PreVendaModel.cancelar_pre_venda(pre_venda_id)
            return True, f"Pré-venda #{pre_venda_id} cancelada com sucesso."
        except Exception as exc:
            return False, f"Erro ao cancelar pré-venda: {exc}"

    @staticmethod
    def marcar_importada(pre_venda_id: int, nova_venda_id: int) -> Tuple[bool, str]:
        if pre_venda_id <= 0:
            return False, "Pré-venda inválida."

        pre_venda = PreVendaModel.carregar_pre_venda(pre_venda_id)
        if not pre_venda:
            return False, "Pré-venda não encontrada."
        if pre_venda.get("status") != "PENDENTE":
            return False, "Esta pré-venda já foi processada."

        try:
            PreVendaModel.marcar_importada(pre_venda_id, nova_venda_id)
            return True, f"Pré-venda #{pre_venda_id} marcada como importada."
        except Exception as exc:
            return False, f"Erro ao marcar pré-venda: {exc}"
