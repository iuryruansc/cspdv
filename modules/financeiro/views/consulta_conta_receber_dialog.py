from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem

from ui.financeiro.consulta_conta_receber_dialog import Ui_ConsultaContaReceberDialog
from utils.format_utils import formatar_moeda


class ConsultaContaReceberDialog(QDialog, Ui_ConsultaContaReceberDialog):
    def __init__(self, detalhes: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._detalhes = detalhes
        self._conta = detalhes.get("conta") or {}
        self.setupUi(self)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.btnFechar.clicked.connect(self.accept)
        self._populate()

    def _populate(self) -> None:
        conta = self._conta
        self.lblContaValor.setText(f"#{int(conta.get('id') or 0)}")
        self.lblClienteValor.setText(str(conta.get("cliente") or "Consumidor Final"))
        self.lblVendaValor.setText(f"#{int(conta.get('venda_id') or 0)}")
        self.lblStatusValor.setText(str(conta.get("status") or "-"))
        self.lblVencimentoValor.setText(self._formatar_data(conta.get("data_vencimento")))
        self.lblTotalValor.setText(formatar_moeda(conta.get("valor_total")))
        self.lblRecebidoValor.setText(formatar_moeda(conta.get("valor_recebido")))
        self.lblAbertoValor.setText(formatar_moeda(conta.get("valor_aberto")))
        self._fill_recebimentos(self._detalhes.get("recebimentos") or [])

    def _fill_recebimentos(self, recebimentos: List[Dict[str, Any]]) -> None:
        self.tableRecebimentos.setRowCount(len(recebimentos))
        for row, item in enumerate(recebimentos):
            self._set_item(self.tableRecebimentos, row, 0, self._formatar_data_hora(item.get("data_recebimento")), Qt.AlignCenter)
            self._set_item(self.tableRecebimentos, row, 1, str(item.get("forma_pagamento") or "-"))
            self._set_item(self.tableRecebimentos, row, 2, formatar_moeda(item.get("valor_recebido")), Qt.AlignRight | Qt.AlignVCenter)
            self._set_item(self.tableRecebimentos, row, 3, str(item.get("observacao") or "-"))

    @staticmethod
    def _set_item(table: QTableWidget, row: int, column: int, value: str, alignment: Any = Qt.AlignLeft | Qt.AlignVCenter) -> None:
        item = QTableWidgetItem(value)
        item.setTextAlignment(int(alignment))
        table.setItem(row, column, item)

    @staticmethod
    def _formatar_data_hora(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y %H:%M")
        return "-"

    @staticmethod
    def _formatar_data(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        return str(value or "-")
