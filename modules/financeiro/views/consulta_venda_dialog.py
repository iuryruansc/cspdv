from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from ui.financeiro.consulta_venda_dialog import Ui_ConsultaVendaDialog
from utils.format_utils import formatar_data_hora, formatar_inteiro, formatar_moeda
from utils.table_widget_utils import set_table_item

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
        self.lblDataHora.setText(formatar_data_hora(venda.get("data_hora")))
        self.lblPdv.setText(str(venda.get("pdv") or "-"))
        self.lblStatus.setText(str(venda.get("status") or "-"))
        self.lblTotal.setText(formatar_moeda(venda.get("valor_total")))

        self._fill_itens(self._detalhes.get("itens") or [])
        self._fill_pagamentos(self._detalhes.get("pagamentos") or [])
        self._fill_reembolsos(self._detalhes.get("reembolsos") or [])

    def _fill_itens(self, itens: List[Dict[str, Any]]) -> None:
        self.tableItens.setRowCount(len(itens))
        for row, item in enumerate(itens):
            set_table_item(self.tableItens, row, 0, str(item.get("codigo_barras") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 1, str(item.get("produto") or "-"))
            set_table_item(self.tableItens, row, 2, formatar_inteiro(item.get("quantidade")), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 3, formatar_moeda(item.get("preco_unitario")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableItens, row, 4, formatar_moeda(item.get("total_item")), alignment=Qt.AlignRight | Qt.AlignVCenter)

    def _fill_pagamentos(self, pagamentos: List[Dict[str, Any]]) -> None:
        self.tablePagamentos.setRowCount(len(pagamentos))
        for row, item in enumerate(pagamentos):
            set_table_item(self.tablePagamentos, row, 0, str(item.get("forma_pagamento") or "-"))
            set_table_item(self.tablePagamentos, row, 1, formatar_moeda(item.get("valor_pago")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tablePagamentos, row, 2, formatar_data_hora(item.get("data_pagamento")), alignment=Qt.AlignCenter)

    def _fill_reembolsos(self, reembolsos: List[Dict[str, Any]]) -> None:
        self.tableReembolsos.setRowCount(len(reembolsos))
        for row, item in enumerate(reembolsos):
            set_table_item(self.tableReembolsos, row, 0, str(item.get("tipo") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableReembolsos, row, 1, str(item.get("motivo") or "-"))
            set_table_item(self.tableReembolsos, row, 2, str(item.get("status") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableReembolsos, row, 3, formatar_moeda(item.get("valor_total")), alignment=Qt.AlignRight | Qt.AlignVCenter)

