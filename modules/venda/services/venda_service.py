from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.shared.constants import (
    STATUS_VENDA_CONCLUIDA,
    STATUS_VENDA_CONCLUIDA_COM_PENDENCIA,
)
from modules.venda.models.venda_model import VendaModel

class VendaService:
    @staticmethod
    def _normalizar_itens(itens: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict[str, Any]]]:
        itens_validos: List[Dict[str, Any]] = []
        for item in itens:
            produto_id = int(item.get("produto_id") or item.get("id") or 0)
            quantidade = int(item.get("quantidade") or 0)
            total_item = float(item.get("total") or 0.0)
            if produto_id <= 0:
                return False, "Existe um item sem produto válido na venda.", []
            if quantidade <= 0:
                return False, "Existe um item com quantidade inválida na venda.", []
            if total_item <= 0:
                return False, "Existe um item com total inválido na venda.", []
            item_normalizado = dict(item)
            item_normalizado["id"] = produto_id
            itens_validos.append(item_normalizado)
        return True, "", itens_validos

    @staticmethod
    def _normalizar_pagamentos(pagamentos: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict[str, Any]]]:
        pagamentos_validos: List[Dict[str, Any]] = []
        for pagamento in pagamentos:
            valor = float(pagamento.get("valor") or 0.0)
            forma = str(pagamento.get("forma") or pagamento.get("forma_pagamento") or "").strip()
            if valor <= 0:
                return False, "Existe um pagamento com valor inválido.", []
            if not forma:
                return False, "Existe um pagamento sem forma de pagamento informada.", []
            pagamentos_validos.append(pagamento)
        return True, "", pagamentos_validos

    @staticmethod
    def finalizar_venda(venda_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        usuario = SessionManager.current_user() or {}
        caixa = CaixaSession.current() or {}

        usuario_id = int(usuario.get("id") or 0)
        funcionario_id = int(usuario.get("funcionario_id") or 0)
        caixa_id = int(caixa.get("id") or 0)
        itens = list(venda_data.get("itens") or [])
        pagamentos = list(venda_data.get("pagamentos") or [])

        if usuario_id <= 0 or funcionario_id <= 0:
            return False, "Não foi possível identificar o operador da venda.", None
        if caixa_id <= 0:
            return False, "Não há caixa aberto para registrar a venda.", None
        if not itens:
            return False, "Adicione pelo menos um item antes de finalizar a venda.", None
        if not pagamentos:
            return False, "Lance pelo menos um pagamento antes de finalizar a venda.", None

        ok_itens, mensagem_itens, itens_validos = VendaService._normalizar_itens(itens)
        if not ok_itens:
            return False, mensagem_itens, None

        ok_pagamentos, mensagem_pagamentos, pagamentos_validos = VendaService._normalizar_pagamentos(
            pagamentos
        )
        if not ok_pagamentos:
            return False, mensagem_pagamentos, None

        data_hora = datetime.now()
        cliente_id_raw = venda_data.get("cliente_id")
        cliente_id = int(cliente_id_raw) if cliente_id_raw not in (None, "", 0) else None
        cliente_eh_consumidor_final = bool(venda_data.get("cliente_eh_consumidor_final"))
        valor_total = float(venda_data.get("total") or 0.0)
        desconto_global = float(venda_data.get("desconto_global") or 0.0)
        venda_com_pendencia = bool(venda_data.get("finalizar_com_pendencia"))
        valor_pago = sum(float(item.get("valor") or 0.0) for item in pagamentos_validos)
        valor_em_aberto = float(venda_data.get("valor_em_aberto") or max(0.0, valor_total - valor_pago))

        if valor_total <= 0:
            return False, "O total da venda precisa ser maior que zero.", None
        if desconto_global < 0:
            return False, "O desconto global da venda não pode ser negativo.", None
        if valor_pago <= 0:
            return False, "O total pago precisa ser maior que zero.", None
        if not venda_com_pendencia and valor_pago + 0.009 < valor_total:
            return False, "O total pago é insuficiente para concluir a venda sem pendência.", None

        if venda_com_pendencia:
            if cliente_id is None:
                return False, "Selecione um cliente para concluir a venda com pendência.", None
            if cliente_eh_consumidor_final:
                return False, "Selecione um cliente diferente de Consumidor Final para concluir a venda com pendencia.", None
            if valor_pago >= valor_total or valor_em_aberto <= 0:
                return False, "O pagamento parcial informado não gera uma pendência válida.", None
            data_vencimento = str(venda_data.get("data_vencimento") or "").strip()
            if not data_vencimento:
                return False, "Informe a data de vencimento da pendência antes de concluir a venda.", None

        try:
            venda_id = VendaModel.registrar_venda(
                cliente_id=cliente_id,
                usuario_id=usuario_id,
                funcionario_id=funcionario_id,
                caixa_id=caixa_id,
                itens=itens_validos,
                pagamentos=pagamentos_validos,
                desconto_global=desconto_global,
                valor_total=valor_total,
                data_hora=data_hora,
                status_venda=(
                    STATUS_VENDA_CONCLUIDA_COM_PENDENCIA
                    if venda_com_pendencia
                    else STATUS_VENDA_CONCLUIDA
                ),
                conta_receber=(
                    {
                        "cliente_id": cliente_id,
                        "descricao": f"Saldo pendente da venda #{venda_data.get('numero_venda') or '---'}",
                        "observacao": str(venda_data.get("observacao_pendencia") or "").strip(),
                        "valor_total": valor_em_aberto,
                        "valor_recebido": 0.0,
                        "valor_aberto": valor_em_aberto,
                        "data_vencimento": str(venda_data.get("data_vencimento") or "").strip(),
                    }
                    if venda_com_pendencia and cliente_id is not None
                    else None
                ),
            )
        except Exception as exc:
            return False, f"Erro ao registrar a venda: {exc}", None

        venda_finalizada = {
            **venda_data,
            "numero_venda": venda_id,
            "data_hora_venda": data_hora.strftime("%d/%m/%Y %H:%M:%S"),
            "status": (
                STATUS_VENDA_CONCLUIDA_COM_PENDENCIA
                if venda_com_pendencia
                else STATUS_VENDA_CONCLUIDA
            ),
        }
        return True, "Venda registrada com sucesso.", venda_finalizada
