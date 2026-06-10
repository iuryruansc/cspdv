# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_TelaPreVendas(object):
    def setupUi(self, TelaPreVendas):
        TelaPreVendas.setObjectName("TelaPreVendas")
        TelaPreVendas.resize(1176, 744)
        TelaPreVendas.setStyleSheet(
            "QWidget { font-family: Arial; background-color: #102233; }"
            "QLabel { background-color: transparent; }"
        )

        self.mainVLayout = QtWidgets.QVBoxLayout(TelaPreVendas)
        self.mainVLayout.setContentsMargins(0, 0, 0, 0)
        self.mainVLayout.setSpacing(0)
        self.mainVLayout.setObjectName("mainVLayout")

        self.frameHeader = QtWidgets.QFrame(TelaPreVendas)
        self.frameHeader.setMinimumHeight(56)
        self.frameHeader.setMaximumHeight(56)
        self.frameHeader.setStyleSheet(
            "QFrame#frameHeader{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 #1a3a5a,stop:1 #0a1828);border-bottom:1px solid #1a3a5a;}"
        )
        self.frameHeader.setObjectName("frameHeader")

        self.headerHL = QtWidgets.QHBoxLayout(self.frameHeader)
        self.headerHL.setContentsMargins(24, 0, 24, 0)
        self.headerHL.setObjectName("headerHL")

        self.lblHIco = QtWidgets.QLabel(self.frameHeader)
        self.lblHIco.setStyleSheet("font-size:22px;")
        self.lblHIco.setObjectName("lblHIco")
        self.headerHL.addWidget(self.lblHIco)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.setSpacing(1)
        self.vboxlayout.setObjectName("vboxlayout")

        self.lblHTitulo = QtWidgets.QLabel(self.frameHeader)
        self.lblHTitulo.setStyleSheet("color:#f5fbff;font-size:16px;font-weight:bold;")
        self.lblHTitulo.setObjectName("lblHTitulo")
        self.vboxlayout.addWidget(self.lblHTitulo)

        self.lblHSub = QtWidgets.QLabel(self.frameHeader)
        self.lblHSub.setStyleSheet("color:#8bb7d8;font-size:11px;")
        self.lblHSub.setObjectName("lblHSub")
        self.vboxlayout.addWidget(self.lblHSub)

        self.headerHL.addLayout(self.vboxlayout)

        spacerItem = QtWidgets.QSpacerItem(
            20, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.headerHL.addItem(spacerItem)

        self.frameResumo = QtWidgets.QFrame(self.frameHeader)
        self.frameResumo.setStyleSheet(
            "QFrame#frameResumo{background-color:rgba(53,133,200,12);"
            "border:1px solid #29567a;border-radius:8px;}"
        )
        self.frameResumo.setObjectName("frameResumo")

        self.resumoHL = QtWidgets.QHBoxLayout(self.frameResumo)
        self.resumoHL.setContentsMargins(14, 6, 14, 6)
        self.resumoHL.setObjectName("resumoHL")

        self.lblPendentesLabel = QtWidgets.QLabel(self.frameResumo)
        self.lblPendentesLabel.setStyleSheet("font-size:11px;color:#9bc3df;")
        self.lblPendentesLabel.setObjectName("lblPendentesLabel")
        self.resumoHL.addWidget(self.lblPendentesLabel)

        self.lblPendentesValor = QtWidgets.QLabel(self.frameResumo)
        self.lblPendentesValor.setStyleSheet(
            "font-size:16px;font-weight:bold;color:white;"
        )
        self.lblPendentesValor.setObjectName("lblPendentesValor")
        self.resumoHL.addWidget(self.lblPendentesValor)

        self.headerHL.addWidget(self.frameResumo)

        self.mainVLayout.addWidget(self.frameHeader)

        self.widgetContent = QtWidgets.QWidget(TelaPreVendas)
        self.widgetContent.setObjectName("widgetContent")

        self.contentVL = QtWidgets.QVBoxLayout(self.widgetContent)
        self.contentVL.setContentsMargins(20, 20, 20, 14)
        self.contentVL.setSpacing(14)
        self.contentVL.setObjectName("contentVL")

        self.frameTabela = QtWidgets.QFrame(self.widgetContent)
        self.frameTabela.setStyleSheet(
            "QFrame#frameTabela{background-color:#12283a;"
            "border:1px solid #214b6a;border-radius:12px;}"
        )
        self.frameTabela.setObjectName("frameTabela")

        self.tabelaVLayout = QtWidgets.QVBoxLayout(self.frameTabela)
        self.tabelaVLayout.setContentsMargins(16, 16, 16, 16)
        self.tabelaVLayout.setSpacing(10)
        self.tabelaVLayout.setObjectName("tabelaVLayout")

        self.frameCabecalhoTabela = QtWidgets.QFrame(self.frameTabela)
        self.frameCabecalhoTabela.setStyleSheet("background:transparent;border:none;")
        self.frameCabecalhoTabela.setObjectName("frameCabecalhoTabela")

        self.cabecalhoHL = QtWidgets.QHBoxLayout(self.frameCabecalhoTabela)
        self.cabecalhoHL.setContentsMargins(0, 0, 0, 0)
        self.cabecalhoHL.setObjectName("cabecalhoHL")

        self.lblTituloTabela = QtWidgets.QLabel(self.frameCabecalhoTabela)
        self.lblTituloTabela.setStyleSheet(
            "font-size:13px;font-weight:bold;color:#8bb7d8;"
        )
        self.lblTituloTabela.setObjectName("lblTituloTabela")
        self.cabecalhoHL.addWidget(self.lblTituloTabela)

        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.cabecalhoHL.addItem(spacerItem1)

        self.btnAtualizar = QtWidgets.QPushButton(self.frameCabecalhoTabela)
        self.btnAtualizar.setMinimumSize(QtCore.QSize(100, 32))
        self.btnAtualizar.setStyleSheet(
            "QPushButton{background-color:#2a6fa8;color:white;border:none;"
            "border-radius:6px;font-size:12px;font-weight:bold;}"
            "QPushButton:hover{background-color:#3585c8;}"
            "QPushButton:pressed{background-color:#1e5a8a;}"
        )
        self.btnAtualizar.setObjectName("btnAtualizar")
        self.cabecalhoHL.addWidget(self.btnAtualizar)

        self.tabelaVLayout.addWidget(self.frameCabecalhoTabela)

        self.tablePreVendas = QtWidgets.QTableWidget(self.frameTabela)
        self.tablePreVendas.setStyleSheet(
            "QTableWidget{background-color:#0d1f2d;color:#e0e8f0;"
            "border:1px solid #1a3a5a;border-radius:6px;"
            "gridline-color:#1a3a5a;font-size:12px;}"
            "QTableWidget::item{padding:8px;}"
            "QTableWidget::item:selected{background-color:#2a6fa8;color:white;}"
            "QHeaderView::section{background-color:#1a3a5a;color:#8bb7d8;"
            "border:none;border-bottom:1px solid #214b6a;padding:8px;"
            "font-weight:bold;font-size:11px;}"
        )
        self.tablePreVendas.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.tablePreVendas.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        self.tablePreVendas.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.tablePreVendas.verticalHeader().setVisible(False)
        self.tablePreVendas.setObjectName("tablePreVendas")
        self.tablePreVendas.setColumnCount(6)
        self.tablePreVendas.setHorizontalHeaderLabels(
            ["Nº", "Data/Hora", "Cliente", "Valor Total", "Itens", "Ações"]
        )

        header = self.tablePreVendas.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

        self.tabelaVLayout.addWidget(self.tablePreVendas)

        self.frameVazio = QtWidgets.QFrame(self.frameTabela)
        self.frameVazio.setStyleSheet("background:transparent;border:none;")
        self.frameVazio.setObjectName("frameVazio")

        self.vazioVL = QtWidgets.QVBoxLayout(self.frameVazio)
        self.vazioVL.setObjectName("vazioVL")

        self.lblVazioIcone = QtWidgets.QLabel(self.frameVazio)
        self.lblVazioIcone.setStyleSheet("font-size:48px;")
        self.lblVazioIcone.setAlignment(QtCore.Qt.AlignCenter)
        self.lblVazioIcone.setObjectName("lblVazioIcone")
        self.vazioVL.addWidget(self.lblVazioIcone)

        self.lblVazioTexto = QtWidgets.QLabel(self.frameVazio)
        self.lblVazioTexto.setStyleSheet(
            "font-size:13px;color:#5a7a9a;font-style:italic;"
        )
        self.lblVazioTexto.setAlignment(QtCore.Qt.AlignCenter)
        self.lblVazioTexto.setObjectName("lblVazioTexto")
        self.vazioVL.addWidget(self.lblVazioTexto)

        self.tabelaVLayout.addWidget(self.frameVazio)
        self.frameVazio.hide()

        self.contentVL.addWidget(self.frameTabela)

        self.mainVLayout.addWidget(self.widgetContent)

        self.retranslateUi(TelaPreVendas)
        QtCore.QMetaObject.connectSlotsByName(TelaPreVendas)

    def retranslateUi(self, TelaPreVendas):
        _translate = QtCore.QCoreApplication.translate
        TelaPreVendas.setWindowTitle(_translate("TelaPreVendas", "Pré-Vendas"))
        self.lblHIco.setText(_translate("TelaPreVendas", "📋"))
        self.lblHTitulo.setText(_translate("TelaPreVendas", "Pré-Vendas"))
        self.lblHSub.setText(
            _translate("TelaPreVendas", "Gerenciar pré-vendas salvas")
        )
        self.lblPendentesLabel.setText(
            _translate("TelaPreVendas", "Pendentes: ")
        )
        self.lblPendentesValor.setText(_translate("TelaPreVendas", "0"))
        self.lblTituloTabela.setText(
            _translate("TelaPreVendas", "Pré-Vendas Pendentes")
        )
        self.btnAtualizar.setText(_translate("TelaPreVendas", "Atualizar"))
        self.lblVazioIcone.setText(_translate("TelaPreVendas", "📄"))
        self.lblVazioTexto.setText(
            _translate(
                "TelaPreVendas",
                "Nenhuma pré-venda pendente.\n"
                "Use F8 na tela de venda para salvar uma pré-venda.",
            )
        )
