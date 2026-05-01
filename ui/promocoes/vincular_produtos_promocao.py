# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_VincularProdutosPromocao(object):
    def setupUi(self, VincularProdutosPromocao):
        VincularProdutosPromocao.setObjectName("VincularProdutosPromocao")
        VincularProdutosPromocao.resize(1320, 840)
        VincularProdutosPromocao.setMinimumSize(QtCore.QSize(1220, 780))
        VincularProdutosPromocao.setStyleSheet(
            """
            QDialog {
                background-color: #eef4f8;
                color: #18324a;
                font-family: "Segoe UI";
            }
            QFrame#frameHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #153552, stop:0.55 #1d4c74, stop:1 #2f75b0);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            QLabel#lblBadge {
                color: #ffe59d;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 14px;
                border-radius: 8px;
                background-color: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.18);
            }
            QLabel#lblTitulo, QLabel#lblSubtitulo, QLabel[headerMeta="true"] {
                color: white;
            }
            QLabel#lblTitulo {
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#lblSubtitulo {
                font-size: 12px;
            }
            QLabel[headerMeta="true"] {
                font-size: 12px;
                font-weight: 600;
            }
            QFrame#frameCard, QFrame[sectionCard="true"] {
                background-color: white;
                border: 1px solid #d6e2ec;
                border-radius: 14px;
            }
            QLabel[sectionTitle="true"] {
                color: #153552;
                font-size: 14px;
                font-weight: 800;
            }
            QLabel[sectionHint="true"] {
                color: #65829b;
                font-size: 11px;
            }
            QLabel[summaryLabel="true"] {
                color: #5d7a93;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel[summaryValue="true"] {
                color: #18324a;
                font-size: 13px;
                font-weight: 800;
            }
            QLineEdit {
                background-color: #f7fafc;
                border: 1px solid #c8d7e6;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
                color: #18324a;
            }
            QLineEdit {
                min-height: 42px;
            }
            QLineEdit:focus {
                border: 2px solid #3a8ad3;
                background-color: white;
            }
            QTableWidget {
                background-color: #fbfdff;
                border: 1px solid #e3edf4;
                border-radius: 12px;
                gridline-color: #e6eef5;
                font-size: 12px;
                color: #18324a;
                selection-background-color: #d9ecfb;
                selection-color: #153552;
            }
            QHeaderView::section {
                background-color: #f2f7fb;
                color: #315676;
                font-size: 11px;
                font-weight: 700;
                border: none;
                border-right: 1px solid #dce7ef;
                border-bottom: 1px solid #dce7ef;
                padding: 8px 8px;
            }
            QPushButton {
                min-height: 40px;
                border: none;
                border-radius: 10px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btnAtualizar {
                background-color: #e9f3fb;
                color: #205d8f;
                border: 1px solid #b8d3ea;
            }
            QPushButton#btnVincularProduto {
                background-color: #2f80c9;
                color: white;
            }
            QPushButton#btnRemoverProduto {
                background-color: #f4a329;
                color: #1f2a36;
            }
            QPushButton#btnFechar {
                background-color: #d92b2b;
                color: white;
            }
            """
        )
        self.verticalLayout = QtWidgets.QVBoxLayout(VincularProdutosPromocao)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frameHeader = QtWidgets.QFrame(VincularProdutosPromocao)
        self.frameHeader.setObjectName("frameHeader")
        self.headerLayout = QtWidgets.QHBoxLayout(self.frameHeader)
        self.headerLayout.setContentsMargins(24, 20, 24, 20)
        self.headerLayout.setSpacing(16)
        self.headerLayout.setObjectName("headerLayout")
        self.headerTextLayout = QtWidgets.QVBoxLayout()
        self.headerTextLayout.setSpacing(8)
        self.lblBadge = QtWidgets.QLabel(self.frameHeader)
        self.lblBadge.setObjectName("lblBadge")
        self.headerTextLayout.addWidget(self.lblBadge, 0, QtCore.Qt.AlignLeft)
        self.lblTitulo = QtWidgets.QLabel(self.frameHeader)
        self.lblTitulo.setObjectName("lblTitulo")
        self.headerTextLayout.addWidget(self.lblTitulo)
        self.lblSubtitulo = QtWidgets.QLabel(self.frameHeader)
        self.lblSubtitulo.setObjectName("lblSubtitulo")
        self.headerTextLayout.addWidget(self.lblSubtitulo)
        self.headerLayout.addLayout(self.headerTextLayout, 1)
        self.headerMetaLayout = QtWidgets.QVBoxLayout()
        self.headerMetaLayout.setSpacing(8)
        self.lblCodigoPromocao = QtWidgets.QLabel(self.frameHeader)
        self.lblCodigoPromocao.setProperty("headerMeta", "true")
        self.lblCodigoPromocao.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.lblCodigoPromocao.setObjectName("lblCodigoPromocao")
        self.headerMetaLayout.addWidget(self.lblCodigoPromocao)
        self.lblTipoPromocao = QtWidgets.QLabel(self.frameHeader)
        self.lblTipoPromocao.setProperty("headerMeta", "true")
        self.lblTipoPromocao.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.lblTipoPromocao.setObjectName("lblTipoPromocao")
        self.headerMetaLayout.addWidget(self.lblTipoPromocao)
        self.headerLayout.addLayout(self.headerMetaLayout)
        self.verticalLayout.addWidget(self.frameHeader)

        self.frameCard = QtWidgets.QFrame(VincularProdutosPromocao)
        self.frameCard.setObjectName("frameCard")
        self.contentLayout = QtWidgets.QVBoxLayout(self.frameCard)
        self.contentLayout.setContentsMargins(24, 22, 24, 22)
        self.contentLayout.setSpacing(16)
        self.contentLayout.setObjectName("contentLayout")

        self.frameResumo = QtWidgets.QFrame(self.frameCard)
        self.frameResumo.setProperty("sectionCard", "true")
        self.frameResumo.setObjectName("frameResumo")
        self.resumoLayout = QtWidgets.QGridLayout(self.frameResumo)
        self.resumoLayout.setContentsMargins(16, 14, 16, 14)
        self.resumoLayout.setHorizontalSpacing(18)
        self.resumoLayout.setVerticalSpacing(10)
        self.resumoLayout.setObjectName("resumoLayout")
        self.lblResumoNomeTitulo = QtWidgets.QLabel(self.frameResumo)
        self.lblResumoNomeTitulo.setProperty("summaryLabel", "true")
        self.lblResumoNomeTitulo.setObjectName("lblResumoNomeTitulo")
        self.resumoLayout.addWidget(self.lblResumoNomeTitulo, 0, 0, 1, 1)
        self.lblResumoNomeValor = QtWidgets.QLabel(self.frameResumo)
        self.lblResumoNomeValor.setProperty("summaryValue", "true")
        self.lblResumoNomeValor.setObjectName("lblResumoNomeValor")
        self.resumoLayout.addWidget(self.lblResumoNomeValor, 1, 0, 1, 1)
        self.lblResumoVigenciaTitulo = QtWidgets.QLabel(self.frameResumo)
        self.lblResumoVigenciaTitulo.setProperty("summaryLabel", "true")
        self.lblResumoVigenciaTitulo.setObjectName("lblResumoVigenciaTitulo")
        self.resumoLayout.addWidget(self.lblResumoVigenciaTitulo, 0, 1, 1, 1)
        self.lblResumoVigenciaValor = QtWidgets.QLabel(self.frameResumo)
        self.lblResumoVigenciaValor.setProperty("summaryValue", "true")
        self.lblResumoVigenciaValor.setObjectName("lblResumoVigenciaValor")
        self.resumoLayout.addWidget(self.lblResumoVigenciaValor, 1, 1, 1, 1)
        self.lblResumoRegraTitulo = QtWidgets.QLabel(self.frameResumo)
        self.lblResumoRegraTitulo.setProperty("summaryLabel", "true")
        self.lblResumoRegraTitulo.setObjectName("lblResumoRegraTitulo")
        self.resumoLayout.addWidget(self.lblResumoRegraTitulo, 0, 2, 1, 1)
        self.lblResumoRegraValor = QtWidgets.QLabel(self.frameResumo)
        self.lblResumoRegraValor.setProperty("summaryValue", "true")
        self.lblResumoRegraValor.setObjectName("lblResumoRegraValor")
        self.resumoLayout.addWidget(self.lblResumoRegraValor, 1, 2, 1, 1)
        self.contentLayout.addWidget(self.frameResumo)

        self.middleLayout = QtWidgets.QHBoxLayout()
        self.middleLayout.setSpacing(16)
        self.middleLayout.setObjectName("middleLayout")

        self.frameBusca = QtWidgets.QFrame(self.frameCard)
        self.frameBusca.setProperty("sectionCard", "true")
        self.frameBusca.setObjectName("frameBusca")
        self.buscaLayout = QtWidgets.QVBoxLayout(self.frameBusca)
        self.buscaLayout.setContentsMargins(16, 16, 16, 16)
        self.buscaLayout.setSpacing(12)
        self.buscaLayout.setObjectName("buscaLayout")
        self.lblBuscaTitulo = QtWidgets.QLabel(self.frameBusca)
        self.lblBuscaTitulo.setProperty("sectionTitle", "true")
        self.lblBuscaTitulo.setObjectName("lblBuscaTitulo")
        self.buscaLayout.addWidget(self.lblBuscaTitulo)
        self.lblBuscaHint = QtWidgets.QLabel(self.frameBusca)
        self.lblBuscaHint.setProperty("sectionHint", "true")
        self.lblBuscaHint.setObjectName("lblBuscaHint")
        self.buscaLayout.addWidget(self.lblBuscaHint)
        self.txtBuscaProduto = QtWidgets.QLineEdit(self.frameBusca)
        self.txtBuscaProduto.setObjectName("txtBuscaProduto")
        self.buscaLayout.addWidget(self.txtBuscaProduto)
        self.tableProdutos = QtWidgets.QTableWidget(self.frameBusca)
        self.tableProdutos.setRowCount(0)
        self.tableProdutos.setColumnCount(5)
        self.tableProdutos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableProdutos.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableProdutos.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableProdutos.setAlternatingRowColors(True)
        self.tableProdutos.setObjectName("tableProdutos")
        for idx in range(5):
            item = QtWidgets.QTableWidgetItem()
            self.tableProdutos.setHorizontalHeaderItem(idx, item)
        self.tableProdutos.horizontalHeader().setStretchLastSection(True)
        self.tableProdutos.verticalHeader().setVisible(False)
        self.buscaLayout.addWidget(self.tableProdutos, 1)
        self.btnVincularProduto = QtWidgets.QPushButton(self.frameBusca)
        self.btnVincularProduto.setObjectName("btnVincularProduto")
        self.buscaLayout.addWidget(self.btnVincularProduto)
        self.middleLayout.addWidget(self.frameBusca, 1)

        self.frameItens = QtWidgets.QFrame(self.frameCard)
        self.frameItens.setProperty("sectionCard", "true")
        self.frameItens.setObjectName("frameItens")
        self.itensLayout = QtWidgets.QVBoxLayout(self.frameItens)
        self.itensLayout.setContentsMargins(16, 16, 16, 16)
        self.itensLayout.setSpacing(12)
        self.itensLayout.setObjectName("itensLayout")
        self.lblItensTitulo = QtWidgets.QLabel(self.frameItens)
        self.lblItensTitulo.setProperty("sectionTitle", "true")
        self.lblItensTitulo.setObjectName("lblItensTitulo")
        self.itensLayout.addWidget(self.lblItensTitulo)
        self.lblItensHint = QtWidgets.QLabel(self.frameItens)
        self.lblItensHint.setProperty("sectionHint", "true")
        self.lblItensHint.setObjectName("lblItensHint")
        self.itensLayout.addWidget(self.lblItensHint)
        self.tableItensVinculados = QtWidgets.QTableWidget(self.frameItens)
        self.tableItensVinculados.setRowCount(0)
        self.tableItensVinculados.setColumnCount(5)
        self.tableItensVinculados.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableItensVinculados.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableItensVinculados.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableItensVinculados.setAlternatingRowColors(True)
        self.tableItensVinculados.setObjectName("tableItensVinculados")
        for idx in range(5):
            item = QtWidgets.QTableWidgetItem()
            self.tableItensVinculados.setHorizontalHeaderItem(idx, item)
        self.tableItensVinculados.horizontalHeader().setStretchLastSection(True)
        self.tableItensVinculados.verticalHeader().setVisible(False)
        self.itensLayout.addWidget(self.tableItensVinculados, 1)
        self.btnRemoverProduto = QtWidgets.QPushButton(self.frameItens)
        self.btnRemoverProduto.setObjectName("btnRemoverProduto")
        self.itensLayout.addWidget(self.btnRemoverProduto)
        self.middleLayout.addWidget(self.frameItens, 1)

        self.contentLayout.addLayout(self.middleLayout, 1)

        self.bottomLayout = QtWidgets.QHBoxLayout()
        self.bottomLayout.setSpacing(10)
        self.bottomLayout.setObjectName("bottomLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.bottomLayout.addItem(spacerItem)
        self.btnAtualizar = QtWidgets.QPushButton(self.frameCard)
        self.btnAtualizar.setObjectName("btnAtualizar")
        self.bottomLayout.addWidget(self.btnAtualizar)
        self.btnFechar = QtWidgets.QPushButton(self.frameCard)
        self.btnFechar.setObjectName("btnFechar")
        self.bottomLayout.addWidget(self.btnFechar)
        self.contentLayout.addLayout(self.bottomLayout)

        self.verticalLayout.addWidget(self.frameCard)

        self.retranslateUi(VincularProdutosPromocao)
        QtCore.QMetaObject.connectSlotsByName(VincularProdutosPromocao)

    def retranslateUi(self, VincularProdutosPromocao):
        _translate = QtCore.QCoreApplication.translate
        VincularProdutosPromocao.setWindowTitle(_translate("VincularProdutosPromocao", "CSPdv - Vincular Produtos"))
        self.lblBadge.setText(_translate("VincularProdutosPromocao", "PROMOÇÕES"))
        self.lblTitulo.setText(_translate("VincularProdutosPromocao", "Vincular Produtos à Promoção"))
        self.lblSubtitulo.setText(_translate("VincularProdutosPromocao", "Selecione produtos ativos e aplique automaticamente a regra financeira da promoção escolhida."))
        self.lblCodigoPromocao.setText(_translate("VincularProdutosPromocao", "Código: ---"))
        self.lblTipoPromocao.setText(_translate("VincularProdutosPromocao", "Tipo: ---"))
        self.lblResumoNomeTitulo.setText(_translate("VincularProdutosPromocao", "PROMOÇÃO"))
        self.lblResumoNomeValor.setText(_translate("VincularProdutosPromocao", "---"))
        self.lblResumoVigenciaTitulo.setText(_translate("VincularProdutosPromocao", "VIGÊNCIA"))
        self.lblResumoVigenciaValor.setText(_translate("VincularProdutosPromocao", "---"))
        self.lblResumoRegraTitulo.setText(_translate("VincularProdutosPromocao", "REGRA"))
        self.lblResumoRegraValor.setText(_translate("VincularProdutosPromocao", "---"))
        self.lblBuscaTitulo.setText(_translate("VincularProdutosPromocao", "Buscar Produtos"))
        self.lblBuscaHint.setText(_translate("VincularProdutosPromocao", "Pesquise por nome, código de barras, marca ou categoria."))
        self.txtBuscaProduto.setPlaceholderText(_translate("VincularProdutosPromocao", "Buscar por produto, código, marca ou categoria"))
        item = self.tableProdutos.horizontalHeaderItem(0)
        item.setText(_translate("VincularProdutosPromocao", "Código"))
        item = self.tableProdutos.horizontalHeaderItem(1)
        item.setText(_translate("VincularProdutosPromocao", "Produto"))
        item = self.tableProdutos.horizontalHeaderItem(2)
        item.setText(_translate("VincularProdutosPromocao", "Preço Atual"))
        item = self.tableProdutos.horizontalHeaderItem(3)
        item.setText(_translate("VincularProdutosPromocao", "Estoque"))
        item = self.tableProdutos.horizontalHeaderItem(4)
        item.setText(_translate("VincularProdutosPromocao", "Situação"))
        self.btnVincularProduto.setText(_translate("VincularProdutosPromocao", "Vincular Produto Selecionado"))
        self.lblItensTitulo.setText(_translate("VincularProdutosPromocao", "Produtos Já Vinculados"))
        self.lblItensHint.setText(_translate("VincularProdutosPromocao", "Confira os preços calculados e remova vínculos quando necessário."))
        item = self.tableItensVinculados.horizontalHeaderItem(0)
        item.setText(_translate("VincularProdutosPromocao", "Produto"))
        item = self.tableItensVinculados.horizontalHeaderItem(1)
        item.setText(_translate("VincularProdutosPromocao", "Preço Atual"))
        item = self.tableItensVinculados.horizontalHeaderItem(2)
        item.setText(_translate("VincularProdutosPromocao", "Preço Promo"))
        item = self.tableItensVinculados.horizontalHeaderItem(3)
        item.setText(_translate("VincularProdutosPromocao", "Desconto"))
        item = self.tableItensVinculados.horizontalHeaderItem(4)
        item.setText(_translate("VincularProdutosPromocao", "Observação"))
        self.btnRemoverProduto.setText(_translate("VincularProdutosPromocao", "Remover Produto Selecionado"))
        self.btnAtualizar.setText(_translate("VincularProdutosPromocao", "Atualizar"))
        self.btnFechar.setText(_translate("VincularProdutosPromocao", "Fechar"))
