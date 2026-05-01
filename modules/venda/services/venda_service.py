from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.venda.models.venda_model import VendaModel


class VendaService:
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
            return False, "Nao foi possivel identificar o operador da venda.", None
        if caixa_id <= 0:
            return False, "Nao ha caixa aberto para registrar a venda.", None
        if not itens:
            return False, "Adicione pelo menos um item antes de finalizar a venda.", None
        if not pagamentos:
            return False, "Lance pelo menos um pagamento antes de finalizar a venda.", None

        data_hora = datetime.now()
        cliente_id_raw = venda_data.get("cliente_id")
        cliente_id = int(cliente_id_raw) if cliente_id_raw not in (None, "", 0) else None
        valor_total = float(venda_data.get("total") or 0.0)
        desconto_global = float(venda_data.get("desconto_global") or 0.0)
        venda_com_pendencia = bool(venda_data.get("finalizar_com_pendencia"))
        valor_pago = sum(float(item.get("valor") or 0.0) for item in pagamentos)
        valor_em_aberto = float(venda_data.get("valor_em_aberto") or max(0.0, valor_total - valor_pago))

        if venda_com_pendencia:
            if cliente_id is None:
                return False, "Selecione um cliente para concluir a venda com pendência.", None
            if valor_pago <= 0 or valor_pago >= valor_total or valor_em_aberto <= 0:
                return False, "O pagamento parcial informado não gera uma pendência válida.", None

        try:
            venda_id = VendaModel.registrar_venda(
                cliente_id=cliente_id,
                usuario_id=usuario_id,
                funcionario_id=funcionario_id,
                caixa_id=caixa_id,
                itens=itens,
                pagamentos=pagamentos,
                desconto_global=desconto_global,
                valor_total=valor_total,
                data_hora=data_hora,
                status_venda="CONCLUIDA_COM_PENDENCIA" if venda_com_pendencia else "CONCLUIDA",
                conta_receber=(
                    {
                        "cliente_id": cliente_id,
                        "descricao": f"Saldo pendente da venda #{venda_data.get('numero_venda') or '---'}",
                        "observacao": str(venda_data.get("observacao_pendencia") or "").strip(),
                        "valor_total": valor_em_aberto,
                        "valor_recebido": 0.0,
                        "valor_aberto": valor_em_aberto,
                        "data_vencimento": str(venda_data.get("data_vencimento") or ""),
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
            "status": "CONCLUIDA_COM_PENDENCIA" if venda_com_pendencia else "CONCLUIDA",
        }
        return True, "Venda registrada com sucesso.", venda_finalizada
