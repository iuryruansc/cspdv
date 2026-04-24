from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from utils.format_utils import formatar_inteiro, formatar_moeda


class ConsultaVendaDialog(QDialog):
    def __init__(self, detalhes: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._detalhes = detalhes
        self._venda = detalhes.get("venda") or {}

        self.setWindowTitle(f"Consulta da Venda #{self._venda.get('id') or '-'}")
        self.setModal(True)
        self.resize(980, 720)
        self.setMinimumSize(920, 680)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet(
            """
QDialog { background: #eef5fb; }
QWidget[card="true"] { background: white; border: 1px solid #c8d8ea; border-radius: 14px; }
QLabel[title="true"] { color: #173a5f; font-size: 16px; font-weight: bold; }
QLabel[caption="true"] { color: #4c6b8b; font-size: 11px; font-weight: bold; }
QLabel[value="true"] { color: #173a5f; font-size: 18px; font-weight: bold; }
QTableWidget { background: white; border: 1px solid #c8d8ea; border-radius: 10px; gridline-color: #d9e6f2; color: #173a5f; }
QHeaderView::section { background: #e7f0f8; color: #1e4e79; padding: 8px; border: none; border-right: 1px solid #d1e0ee; border-bottom: 1px solid #d1e0ee; font-weight: bold; }
QPushButton { background: #2f75b0; color: white; border: none; border-radius: 10px; padding: 10px 20px; font-weight: bold; }
QPushButton:hover { background: #225d8e; }
            """
        )

        self._build_ui()
        self._populate()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        header_card = QWidget(self)
        header_card.setProperty("card", True)
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(12)

        title = QLabel(f"Venda #{self._venda.get('id') or '-'}", header_card)
        title.setProperty("title", True)
        header_layout.addWidget(title)

        info_grid = QHBoxLayout()
        info_grid.setSpacing(28)
        header_layout.addLayout(info_grid)

        self.lblCliente = self._create_info_block(info_grid, "CLIENTE")
        self.lblOperador = self._create_info_block(info_grid, "OPERADOR")
        self.lblDataHora = self._create_info_block(info_grid, "DATA / HORA")
        self.lblPdv = self._create_info_block(info_grid, "PDV")
        self.lblStatus = self._create_info_block(info_grid, "STATUS")
        self.lblTotal = self._create_info_block(info_grid, "TOTAL")

        root.addWidget(header_card)

        self.tableItens = self._create_table(["Código", "Descrição", "Qtd.", "Vl. Unit.", "Total"])
        root.addWidget(self._wrap_table("Itens da Venda", self.tableItens), 1)

        tables_row = QHBoxLayout()
        tables_row.setSpacing(14)
        self.tablePagamentos = self._create_table(["Forma", "Valor", "Data"])
        self.tableReembolsos = self._create_table(["Tipo", "Motivo", "Status", "Valor"])
        tables_row.addWidget(self._wrap_table("Pagamentos", self.tablePagamentos), 1)
        tables_row.addWidget(self._wrap_table("Reembolsos", self.tableReembolsos), 1)
        root.addLayout(tables_row, 1)

        footer = QHBoxLayout()
        footer.addStretch(1)
        btn_fechar = QPushButton("Fechar", self)
        btn_fechar.clicked.connect(self.accept)
        footer.addWidget(btn_fechar)
        root.addLayout(footer)

    def _create_info_block(self, parent_layout: QHBoxLayout, caption: str) -> QLabel:
        container = QVBoxLayout()
        container.setSpacing(4)
        lbl_caption = QLabel(caption)
        lbl_caption.setProperty("caption", True)
        lbl_value = QLabel("-")
        lbl_value.setProperty("value", True)
        container.addWidget(lbl_caption)
        container.addWidget(lbl_value)
        parent_layout.addLayout(container, 1)
        return lbl_value

    def _wrap_table(self, title: str, table: QTableWidget) -> QWidget:
        card = QWidget(self)
        card.setProperty("card", True)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        lbl = QLabel(title, card)
        lbl.setProperty("title", True)
        layout.addWidget(lbl)
        layout.addWidget(table)
        return card

    def _create_table(self, headers: List[str]) -> QTableWidget:
        table = QTableWidget(self)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def _populate(self) -> None:
        venda = self._venda
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
    def _set_item(table: QTableWidget, row: int, column: int, value: str, alignment: int = Qt.AlignLeft | Qt.AlignVCenter) -> None:
        item = QTableWidgetItem(value)
        item.setTextAlignment(int(alignment))
        table.setItem(row, column, item)

    @staticmethod
    def _formatar_data_hora(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y %H:%M")
        return "-"
