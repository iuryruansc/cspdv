# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_ConsultaVendaDialog(object):
    def setupUi(self, ConsultaVendaDialog):
        ConsultaVendaDialog.setObjectName("ConsultaVendaDialog")
        ConsultaVendaDialog.resize(980, 720)
        ConsultaVendaDialog.setMinimumSize(QtCore.QSize(920, 680))
        ConsultaVendaDialog.setWindowTitle("Consulta da Venda")
        ConsultaVendaDialog.setStyleSheet(
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
        self.verticalLayout = QtWidgets.QVBoxLayout(ConsultaVendaDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(14)

        self.headerCard = QtWidgets.QWidget(ConsultaVendaDialog)
        self.headerCard.setProperty("card", "true")
        self.headerLayout = QtWidgets.QVBoxLayout(self.headerCard)
        self.headerLayout.setContentsMargins(18, 18, 18, 18)
        self.headerLayout.setSpacing(12)
        self.lblHeaderTitulo = QtWidgets.QLabel(self.headerCard)
        self.lblHeaderTitulo.setProperty("title", "true")
        self.headerLayout.addWidget(self.lblHeaderTitulo)
        self.infoGrid = QtWidgets.QHBoxLayout()
        self.infoGrid.setSpacing(28)
        self.headerLayout.addLayout(self.infoGrid)
        self.lblCliente = self._add_info_block(self.infoGrid, "CLIENTE")
        self.lblOperador = self._add_info_block(self.infoGrid, "OPERADOR")
        self.lblDataHora = self._add_info_block(self.infoGrid, "DATA / HORA")
        self.lblPdv = self._add_info_block(self.infoGrid, "PDV")
        self.lblStatus = self._add_info_block(self.infoGrid, "STATUS")
        self.lblTotal = self._add_info_block(self.infoGrid, "TOTAL")
        self.verticalLayout.addWidget(self.headerCard)

        self.itensCard = self._create_card(ConsultaVendaDialog, "Itens da Venda")
        self.tableItens = QtWidgets.QTableWidget(self.itensCard)
        self._setup_table(self.tableItens, ["Código", "Descrição", "Qtd.", "Vl. Unit.", "Total"], no_selection=True)
        self.itensCard.layout().addWidget(self.tableItens)
        self.verticalLayout.addWidget(self.itensCard, 1)

        self.tablesRow = QtWidgets.QHBoxLayout()
        self.tablesRow.setSpacing(14)
        self.pagamentosCard = self._create_card(ConsultaVendaDialog, "Pagamentos")
        self.tablePagamentos = QtWidgets.QTableWidget(self.pagamentosCard)
        self._setup_table(self.tablePagamentos, ["Forma", "Valor", "Data"], no_selection=True)
        self.pagamentosCard.layout().addWidget(self.tablePagamentos)
        self.tablesRow.addWidget(self.pagamentosCard, 1)
        self.reembolsosCard = self._create_card(ConsultaVendaDialog, "Reembolsos")
        self.tableReembolsos = QtWidgets.QTableWidget(self.reembolsosCard)
        self._setup_table(self.tableReembolsos, ["Tipo", "Motivo", "Status", "Valor"], no_selection=True)
        self.reembolsosCard.layout().addWidget(self.tableReembolsos)
        self.tablesRow.addWidget(self.reembolsosCard, 1)
        self.verticalLayout.addLayout(self.tablesRow, 1)

        self.footerLayout = QtWidgets.QHBoxLayout()
        self.footerLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.btnFechar = QtWidgets.QPushButton(ConsultaVendaDialog)
        self.footerLayout.addWidget(self.btnFechar)
        self.verticalLayout.addLayout(self.footerLayout)

        self.retranslateUi(ConsultaVendaDialog)
        QtCore.QMetaObject.connectSlotsByName(ConsultaVendaDialog)

    def _add_info_block(self, parent_layout, caption):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(4)
        lbl_caption = QtWidgets.QLabel(caption)
        lbl_caption.setProperty("caption", "true")
        layout.addWidget(lbl_caption)
        lbl_value = QtWidgets.QLabel("-")
        lbl_value.setProperty("value", "true")
        layout.addWidget(lbl_value)
        parent_layout.addLayout(layout, 1)
        return lbl_value

    def _create_card(self, parent, title):
        card = QtWidgets.QWidget(parent)
        card.setProperty("card", "true")
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        title_label = QtWidgets.QLabel(title, card)
        title_label.setProperty("title", "true")
        layout.addWidget(title_label)
        return card

    def _setup_table(self, table, headers, *, no_selection=False):
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(
            QtWidgets.QAbstractItemView.NoSelection if no_selection else QtWidgets.QAbstractItemView.SingleSelection
        )
        table.horizontalHeader().setStretchLastSection(True)

    def retranslateUi(self, ConsultaVendaDialog):
        _translate = QtCore.QCoreApplication.translate
        self.lblHeaderTitulo.setText(_translate("ConsultaVendaDialog", "Venda #-"))
        self.btnFechar.setText(_translate("ConsultaVendaDialog", "Fechar"))
