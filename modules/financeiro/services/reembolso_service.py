from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Tuple

from core.session_manager import SessionManager
from modules.financeiro.models.reembolso_model import ReembolsoModel
from modules.financeiro.services.financeiro_service import FinanceiroService


CENT = Decimal("0.01")


class ReembolsoService:
    @staticmethod
    def preparar_pagamentos_reembolso(venda_id: int, valor_reembolso: Decimal) -> List[Dict[str, Any]]:
        detalhes = FinanceiroService.obter_venda_detalhada(venda_id) or {}
        pagamentos = list(detalhes.get("pagamentos") or [])
        if not pagamentos:
            return []

        totais = [Decimal(str(item.get("valor_pago") or 0)).quantize(CENT, rounding=ROUND_HALF_UP) for item in pagamentos]
        total_pago = sum(totais, Decimal("0.00"))
        if total_pago <= Decimal("0.00"):
            return []

        distribuicao: List[Dict[str, Any]] = []
        acumulado = Decimal("0.00")
        for index, pagamento in enumerate(pagamentos):
            if index == len(pagamentos) - 1:
                valor = valor_reembolso - acumulado
            else:
                valor = (valor_reembolso * totais[index] / total_pago).quantize(CENT, rounding=ROUND_HALF_UP)
                acumulado += valor
            distribuicao.append(
                {
                    "forma_pagamento": str(pagamento.get("forma_pagamento") or "Forma"),
                    "valor": valor,
                    "observacao": "Reembolso proporcional à forma original da venda",
                }
            )
        return distribuicao

    @staticmethod
    def registrar_reembolso(payload: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        usuario = SessionManager.current_user() or {}
        usuario_id = int(usuario.get("id") or 0)
        if usuario_id <= 0:
            return False, "Não foi possível identificar o operador do reembolso.", None

        venda_id = int(payload.get("venda_id") or 0)
        if venda_id <= 0:
            return False, "Selecione uma venda válida para continuar.", None

        motivo = str(payload.get("motivo") or "").strip()
        if not motivo:
            return False, "Informe o motivo do reembolso.", None

        itens = list(payload.get("itens") or [])
        if not itens:
            return False, "Selecione pelo menos um item para reembolso.", None

        detalhes = FinanceiroService.obter_venda_detalhada(venda_id)
        if not detalhes:
            return False, "A venda selecionada não foi localizada.", None

        mapa_itens = {
            int(item["item_venda_id"]): item
            for item in (detalhes.get("itens") or [])
        }
        itens_validos: List[Dict[str, Any]] = []
        valor_total = Decimal("0.00")
        for item in itens:
            item_venda_id = int(item.get("item_venda_id") or 0)
            quantidade = int(item.get("quantidade") or 0)
            original = mapa_itens.get(item_venda_id)
            if not original:
                return False, "Um dos itens do reembolso não existe mais na venda original.", None
            quantidade_disponivel = int(original.get("quantidade_disponivel") or 0)
            if quantidade <= 0 or quantidade > quantidade_disponivel:
                return False, "A quantidade de reembolso excede o saldo disponível de um item.", None

            valor_unitario = Decimal(str(original.get("preco_unitario") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
            valor_item = (valor_unitario * Decimal(quantidade)).quantize(CENT, rounding=ROUND_HALF_UP)
            valor_total += valor_item
            itens_validos.append(
                {
                    "item_venda_id": item_venda_id,
                    "produto_id": int(original.get("produto_id") or 0),
                    "lote_id": int(original.get("lote_id") or 0),
                    "quantidade": quantidade,
                    "valor_unitario": valor_unitario,
                    "valor_total": valor_item,
                }
            )

        pagamentos = ReembolsoService.preparar_pagamentos_reembolso(venda_id, valor_total)

        try:
            reembolso_id = ReembolsoModel.registrar_reembolso(
                venda_id=venda_id,
                tipo=str(payload.get("tipo") or "PARCIAL"),
                motivo=motivo,
                observacao=str(payload.get("observacao") or ""),
                usuario_id=usuario_id,
                itens=itens_validos,
                pagamentos=pagamentos,
            )
        except Exception as exc:
            return False, f"Erro ao registrar o reembolso: {exc}", None

        return True, "Reembolso registrado com sucesso.", {
            "reembolso_id": reembolso_id,
            "venda_id": venda_id,
            "valor_total": valor_total,
            "tipo": str(payload.get("tipo") or "PARCIAL"),
        }
