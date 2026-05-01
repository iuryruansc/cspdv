from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem

from ui.financeiro.consulta_venda_dialog import Ui_ConsultaVendaDialog
from utils.format_utils import formatar_inteiro, formatar_moeda


class ConsultaVendaDialog(QDialog, Ui_ConsultaVendaDialog):
    def __init__(self, detalhes: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._detalhes = detalhes
        self._venda = detalhes.get("venda") or {}

        self.setupUi(self)
        self.setWindowTitle(f"Consulta da Venda #{self._venda.get('id') or '-'}")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.btnFechar.clicked.connect(self.accept)
        self._populate()

    def _populate(self) -> None:
        venda = self._venda
        self.lblHeaderTitulo.setText(f"Venda #{self._venda.get('id') or '-'}")
        self.lblCliente.setText(str(venda.get("cliente") or "Consumidor Final"))
        self.lblOperador.setText(str(venda.get("operador") or "-"))
        self.lblDataHora.setText(self._formatar_data_hora(venda.get("data_hora")))
        self.lblPdv.setText(str(venda.get("pdv") or "-"))
        self.lblStatus.setText(str(venda.get("status") or "-"))
        self.lblTotal.setText(formatar_moeda(venda.get("valor_total")))

        self._fill_itens(self._detalhes.get("itens") or [])
        self._fill_pagamentos(self._detalhes.get("pagamentos") or [])
        self._fill_reembolsos(self._detalhes.get("reembolsos") or [])

    def _fill_itens(self, itens: List[Dict[str, Any]]) -> None:
        self.tableItens.setRowCount(len(itens))
        for row, item in enumerate(itens):
            self._set_item(self.tableItens, row, 0, str(item.get("codigo_barras") or "-"), Qt.AlignCenter)
            self._set_item(self.tableItens, row, 1, str(item.get("produto") or "-"))
            self._set_item(self.tableItens, row, 2, formatar_inteiro(item.get("quantidade")), Qt.AlignCenter)
            self._set_item(self.tableItens, row, 3, formatar_moeda(item.get("preco_unitario")), Qt.AlignRight | Qt.AlignVCenter)
            self._set_item(self.tableItens, row, 4, formatar_moeda(item.get("total_item")), Qt.AlignRight | Qt.AlignVCenter)

    def _fill_pagamentos(self, pagamentos: List[Dict[str, Any]]) -> None:
        self.tablePagamentos.setRowCount(len(pagamentos))
        for row, item in enumerate(pagamentos):
            self._set_item(self.tablePagamentos, row, 0, str(item.get("forma_pagamento") or "-"))
            self._set_item(self.tablePagamentos, row, 1, formatar_moeda(item.get("valor_pago")), Qt.AlignRight | Qt.AlignVCenter)
            self._set_item(self.tablePagamentos, row, 2, self._formatar_data_hora(item.get("data_pagamento")), Qt.AlignCenter)

    def _fill_reembolsos(self, reembolsos: List[Dict[str, Any]]) -> None:
        self.tableReembolsos.setRowCount(len(reembolsos))
        for row, item in enumerate(reembolsos):
            self._set_item(self.tableReembolsos, row, 0, str(item.get("tipo") or "-"), Qt.AlignCenter)
            self._set_item(self.tableReembolsos, row, 1, str(item.get("motivo") or "-"))
            self._set_item(self.tableReembolsos, row, 2, str(item.get("status") or "-"), Qt.AlignCenter)
            self._set_item(self.tableReembolsos, row, 3, formatar_moeda(item.get("valor_total")), Qt.AlignRight | Qt.AlignVCenter)

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
