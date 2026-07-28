from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.financeiro.services.financeiro_service import FinanceiroService
from modules.shared.constants import STATUS_VENDA_CONCLUIDA_COM_PENDENCIA
from ui.financeiro.consulta_venda_dialog import Ui_ConsultaVendaDialog
from utils.format_utils import formatar_data_hora, formatar_inteiro, formatar_moeda
from utils.table_widget_utils import set_table_item
from utils.ui_messages import mostrar_aviso

class ConsultaVendaDialog(QDialog, Ui_ConsultaVendaDialog):
    def __init__(self, detalhes: dict[str, Any], parent=None):
        super().__init__(parent)
        self._detalhes = detalhes
        self._venda = detalhes.get("venda") or {}
        self._payment_registered = False

        self.setupUi(self)
        self.setWindowTitle(f"Consulta da Venda #{self._venda.get('id') or '-'}")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.btnFechar.clicked.connect(self.accept)
        self._configure_pendencia_button()
        self._populate()

    @property
    def payment_registered(self) -> bool:
        return self._payment_registered

    def _configure_pendencia_button(self) -> None:
        status = str(self._venda.get("status") or "").strip()
        if status == STATUS_VENDA_CONCLUIDA_COM_PENDENCIA:
            self.btnReceberPendencia.setVisible(True)
            self.btnReceberPendencia.clicked.connect(self._receber_pendencia)
        else:
            self.btnReceberPendencia.setVisible(False)

    def _receber_pendencia(self) -> None:
        from modules.financeiro.views.receber_pendencia_dialog import ReceberPendenciaDialog

        conta_id = self._detalhes.get("conta_receber_id")
        if not conta_id:
            mostrar_aviso(self, "Recebimento", "Não foi possível localizar a conta a receber desta venda.")
            return
        conta_detalhada = FinanceiroService.obter_conta_receber_detalhada(conta_id)
        if not conta_detalhada:
            mostrar_aviso(self, "Recebimento", "Conta a receber não encontrada.")
            return

        dialog = ReceberPendenciaDialog(conta_detalhada, parent=self)
        if dialog.exec_() != dialog.Accepted or not dialog.resultado:
            return

        usuario = SessionManager.current_user() or {}
        caixa = CaixaSession.current() or {}
        try:
            FinanceiroService.registrar_recebimento_conta(
                conta_id=int(dialog.resultado["conta_id"]),
                usuario_id=int(usuario.get("id") or 0),
                caixa_id=int(caixa.get("id") or 0),
                forma_pagamento_id=int(dialog.resultado["forma_pagamento_id"]),
                valor_recebido=Decimal(str(dialog.resultado["valor_recebido"])).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP,
                ),
                observacao=str(dialog.resultado.get("observacao") or "").strip(),
                data_recebimento=dialog.resultado.get("data_recebimento") or datetime.now(),
            )
        except Exception as exc:
            mostrar_aviso(self, "Recebimento não registrado", str(exc))
            return

        self._payment_registered = True
        self.accept()

    def _populate(self) -> None:
        venda = self._venda
        self.lblHeaderTitulo.setText(f"Venda #{self._venda.get('id') or '-'}")
        self.lblCliente.setText(str(venda.get("cliente") or "Consumidor Final"))
        self.lblOperador.setText(str(venda.get("operador") or "-"))
        self.lblDataHora.setText(formatar_data_hora(venda.get("data_hora")))
        self.lblPdv.setText(str(venda.get("pdv") or "-"))
        self.lblStatus.setText(str(venda.get("status") or "-"))
        self.lblTotal.setText(formatar_moeda(venda.get("valor_total")))

        self._fill_itens(self._detalhes.get("itens") or [])
        self._fill_pagamentos(self._detalhes.get("pagamentos") or [])
        self._fill_reembolsos(self._detalhes.get("reembolsos") or [])
        self._fill_desconto_global()

    def _fill_itens(self, itens: list[dict[str, Any]]) -> None:
        self.tableItens.setRowCount(len(itens))
        for row, item in enumerate(itens):
            set_table_item(self.tableItens, row, 0, str(item.get("codigo_barras") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 1, str(item.get("produto") or "-"))
            set_table_item(self.tableItens, row, 2, formatar_inteiro(item.get("quantidade")), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 3, formatar_moeda(item.get("preco_original")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableItens, row, 4, formatar_moeda(item.get("preco_unitario")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            desconto = float(item.get("preco_original") or 0) - float(item.get("preco_unitario") or 0)
            desconto *= int(item.get("quantidade") or 0)
            set_table_item(self.tableItens, row, 5, formatar_moeda(desconto) if desconto > 0 else "-", alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableItens, row, 6, formatar_moeda(item.get("total_item")), alignment=Qt.AlignRight | Qt.AlignVCenter)

    def _fill_pagamentos(self, pagamentos: list[dict[str, Any]]) -> None:
        self.tablePagamentos.setRowCount(len(pagamentos))
        for row, item in enumerate(pagamentos):
            set_table_item(self.tablePagamentos, row, 0, str(item.get("forma_pagamento") or "-"))
            set_table_item(self.tablePagamentos, row, 1, formatar_moeda(item.get("valor_pago")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tablePagamentos, row, 2, formatar_data_hora(item.get("data_pagamento")), alignment=Qt.AlignCenter)

    def _fill_reembolsos(self, reembolsos: list[dict[str, Any]]) -> None:
        self.tableReembolsos.setRowCount(len(reembolsos))
        for row, item in enumerate(reembolsos):
            set_table_item(self.tableReembolsos, row, 0, str(item.get("tipo") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableReembolsos, row, 1, str(item.get("motivo") or "-"))
            set_table_item(self.tableReembolsos, row, 2, str(item.get("status") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableReembolsos, row, 3, formatar_moeda(item.get("valor_total")), alignment=Qt.AlignRight | Qt.AlignVCenter)

    def _fill_desconto_global(self) -> None:
        itens = self._detalhes.get("itens") or []
        total_bruto = sum(
            float(item.get("preco_original") or 0) * int(item.get("quantidade") or 0)
            for item in itens
        )
        valor_total = float(self._venda.get("valor_total") or 0)
        desconto_global = total_bruto - valor_total
        desconto_itens = sum(
            (float(item.get("preco_original") or 0) - float(item.get("preco_unitario") or 0))
            * int(item.get("quantidade") or 0)
            for item in itens
        )
        desconto_global_real = desconto_global - desconto_itens
        if desconto_global_real > 0:
            self.lblDescontoGlobalValor.setText(formatar_moeda(desconto_global_real))
            self.descontoGlobalCard.setVisible(True)
        else:
            self.descontoGlobalCard.setVisible(False)

