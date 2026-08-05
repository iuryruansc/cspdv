from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from ui.financeiro.consulta_reembolso_dialog import Ui_ConsultaReembolsoDialog
from modules.shared.constants import STATUS_REEMBOLSO_CANCELADO, STATUS_REEMBOLSO_CONCLUIDO
from utils.format_utils import formatar_data_hora, formatar_moeda
from utils.table_widget_utils import set_table_item


class ConsultaReembolsoDialog(QDialog, Ui_ConsultaReembolsoDialog):
    def __init__(self, detalhes: dict[str, Any], parent=None):
        super().__init__(parent)
        self._detalhes = detalhes
        self._reembolso = detalhes.get("reembolso") or {}
        self.venda_id = int(self._reembolso.get("venda_id") or 0)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.btnFechar.clicked.connect(self.accept)
        self.btnAbrirVenda.clicked.connect(self._abrir_venda)
        self._populate()

    def _populate(self) -> None:
        r = self._reembolso
        self.lblReembolsoValor.setText(f"#{int(r.get('id') or 0)}")
        self.lblVendaValor.setText(f"#{int(r.get('venda_id') or 0)}")
        self.lblTipoValor.setText(str(r.get("tipo") or "-"))
        self.lblStatusValor.setText(str(r.get("status") or "-"))
        self.lblDataHoraValor.setText(formatar_data_hora(r.get("data_hora")))
        self.lblOperadorValor.setText(str(r.get("operador") or "-"))
        self.lblTotalValor.setText(formatar_moeda(r.get("valor_total")))
        self.lblMotivoValor.setText(str(r.get("motivo") or "-"))
        self.plainObservacao.setPlainText(str(r.get("observacao") or "Sem observacoes registradas."))
        self._aplicar_estilo_status()
        self._fill_itens(self._detalhes.get("itens") or [])
        self._fill_pagamentos(self._detalhes.get("pagamentos") or [])

    def _fill_itens(self, itens: list[dict[str, Any]]) -> None:
        self.tableItens.setRowCount(len(itens))
        for row, item in enumerate(itens):
            set_table_item(self.tableItens, row, 0, str(item.get("codigo_barras") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 1, str(item.get("produto") or "-"))
            set_table_item(self.tableItens, row, 2, str(int(item.get("quantidade") or 0)), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 3, formatar_moeda(item.get("valor_unitario")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableItens, row, 4, formatar_moeda(item.get("valor_total")), alignment=Qt.AlignRight | Qt.AlignVCenter)

    def _fill_pagamentos(self, pagamentos: list[dict[str, Any]]) -> None:
        self.tablePagamentos.setRowCount(len(pagamentos))
        for row, item in enumerate(pagamentos):
            set_table_item(self.tablePagamentos, row, 0, str(item.get("forma_pagamento") or "-"))
            set_table_item(self.tablePagamentos, row, 1, str(item.get("observacao") or "-"))
            set_table_item(self.tablePagamentos, row, 2, formatar_moeda(item.get("valor")), alignment=Qt.AlignRight | Qt.AlignVCenter)

    def _aplicar_estilo_status(self) -> None:
        status = str(self._reembolso.get("status") or "").upper()
        if status == STATUS_REEMBOLSO_CONCLUIDO:
            self.lblStatusValor.setProperty("status", "concluido")
        elif status == STATUS_REEMBOLSO_CANCELADO:
            self.lblStatusValor.setProperty("status", "cancelado")
        else:
            self.lblStatusValor.setProperty("status", "")
        self.lblStatusValor.style().unpolish(self.lblStatusValor)
        self.lblStatusValor.style().polish(self.lblStatusValor)
        self.lblStatusValor.update()

    def _abrir_venda(self) -> None:
        if self.venda_id <= 0:
            return
        self.accept()
