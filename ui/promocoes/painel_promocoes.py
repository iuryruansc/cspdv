# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_PainelPromocoes(object):
    def setupUi(self, PainelPromocoes):
        PainelPromocoes.setObjectName("PainelPromocoes")
        PainelPromocoes.resize(1440, 860)
        PainelPromocoes.setMinimumSize(QtCore.QSize(1320, 820))
        self.centralWidget = QtWidgets.QWidget(PainelPromocoes)
        self.centralWidget.setObjectName("centralWidget")
        self.centralWidget.setStyleSheet(
            """
            QWidget#centralWidget {
                background-color: #eef4f8;
                color: #18324a;
                font-family: "Segoe UI";
            }
            QFrame#frameHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #153552, stop:0.55 #1d4c74, stop:1 #2f75b0);
                border-bottom: 1px solid rgba(255,255,255,28);
            }
            QLabel#lblLogo {
                color: white;
                font-size: 30px;
                font-weight: 800;
            }
            QLabel#lblModulo {
                color: #ffe59d;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 14px;
                border-radius: 8px;
                background-color: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.18);
            }
            QLabel#lblOperadorInfo, QLabel#lblDataHora {
                color: #dbeaf7;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#btnVoltarSelecao {
                background-color: #d92b2b;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btnVoltarSelecao:hover {
                background-color: #c11f1f;
            }
            QFrame#toolbarCard, QFrame#framePromocoes, QFrame#frameAgenda {
                background-color: white;
                border: 1px solid #d6e2ec;
                border-radius: 16px;
            }
            QLineEdit, QComboBox {
                min-height: 42px;
                background-color: #f7fafc;
                border: 1px solid #c8d7e6;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 12px;
                color: #18324a;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3a8ad3;
                background-color: white;
            }
            QPushButton {
                min-height: 42px;
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
            QPushButton#btnAtualizar:hover {
                background-color: #d8ebfa;
            }
            QPushButton#btnNovaPromocao, QPushButton#btnDuplicarPromocao {
                background-color: #2f80c9;
                color: white;
            }
            QPushButton#btnNovaPromocao:hover, QPushButton#btnDuplicarPromocao:hover {
                background-color: #276faa;
            }
            QPushButton#btnVincularProdutos {
                background-color: #f4a329;
                color: #1f2a36;
            }
            QPushButton#btnVincularProdutos:hover {
                background-color: #e19215;
            }
            QFrame[metricCard="true"] {
                border-radius: 16px;
                border: 1px solid rgba(0,0,0,0.04);
            }
            QLabel[metricValue="true"] {
                font-size: 34px;
                font-weight: 800;
            }
            QLabel[metricTitle="true"] {
                font-size: 12px;
                font-weight: 600;
            }
            QLabel[sectionTitle="true"] {
                font-size: 14px;
                font-weight: 800;
                color: #153552;
                background-color: transparent;
            }
            QLabel[sectionHint="true"] {
                font-size: 11px;
                color: #65829b;
                background-color: transparent;
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
            QTableWidget::item {
                padding: 6px 8px;
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
            QFrame#frameStatusBar {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #153552, stop:1 #2f75b0);
            }
            QLabel#lblStatusSistema {
                color: #8ff09a;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#lblStatusBar {
                color: white;
                font-size: 11px;
                font-weight: 600;
            }
            """
        )
        self.mainVLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.mainVLayout.setContentsMargins(0, 0, 0, 0)
        self.mainVLayout.setSpacing(0)
        self.mainVLayout.setObjectName("mainVLayout")

        self.frameHeader = QtWidgets.QFrame(self.centralWidget)
        self.frameHeader.setObjectName("frameHeader")
        self.headerHLayout = QtWidgets.QHBoxLayout(self.frameHeader)
        self.headerHLayout.setContentsMargins(18, 12, 18, 12)
        self.headerHLayout.setSpacing(14)
        self.headerHLayout.setObjectName("headerHLayout")
        self.lblLogo = QtWidgets.QLabel(self.frameHeader)
        self.lblLogo.setObjectName("lblLogo")
        self.headerHLayout.addWidget(self.lblLogo)
        self.frameSepHeader = QtWidgets.QFrame(self.frameHeader)
        self.frameSepHeader.setFrameShape(QtWidgets.QFrame.VLine)
        self.frameSepHeader.setStyleSheet("background-color: rgba(255,255,255,0.25);")
        self.frameSepHeader.setObjectName("frameSepHeader")
        self.headerHLayout.addWidget(self.frameSepHeader)
        self.lblModulo = QtWidgets.QLabel(self.frameHeader)
        self.lblModulo.setObjectName("lblModulo")
        self.headerHLayout.addWidget(self.lblModulo)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.headerHLayout.addItem(spacerItem)
        self.lblOperadorInfo = QtWidgets.QLabel(self.frameHeader)
        self.lblOperadorInfo.setObjectName("lblOperadorInfo")
        self.headerHLayout.addWidget(self.lblOperadorInfo)
        self.lblDataHora = QtWidgets.QLabel(self.frameHeader)
        self.lblDataHora.setObjectName("lblDataHora")
        self.headerHLayout.addWidget(self.lblDataHora)
        self.btnVoltarSelecao = QtWidgets.QPushButton(self.frameHeader)
        self.btnVoltarSelecao.setMinimumSize(QtCore.QSize(140, 42))
        self.btnVoltarSelecao.setObjectName("btnVoltarSelecao")
        self.headerHLayout.addWidget(self.btnVoltarSelecao)
        self.mainVLayout.addWidget(self.frameHeader)

        self.contentWrap = QtWidgets.QWidget(self.centralWidget)
        self.contentWrap.setObjectName("contentWrap")
        self.contentWrapLayout = QtWidgets.QVBoxLayout(self.contentWrap)
        self.contentWrapLayout.setContentsMargins(18, 18, 18, 18)
        self.contentWrapLayout.setSpacing(14)
        self.contentWrapLayout.setObjectName("contentWrapLayout")

        self.toolbarCard = QtWidgets.QFrame(self.contentWrap)
        self.toolbarCard.setObjectName("toolbarCard")
        self.toolbarLayout = QtWidgets.QHBoxLayout(self.toolbarCard)
        self.toolbarLayout.setContentsMargins(14, 14, 14, 14)
        self.toolbarLayout.setSpacing(10)
        self.toolbarLayout.setObjectName("toolbarLayout")
        self.txtBuscaPromocao = QtWidgets.QLineEdit(self.toolbarCard)
        self.txtBuscaPromocao.setMinimumWidth(420)
        self.txtBuscaPromocao.setObjectName("txtBuscaPromocao")
        self.toolbarLayout.addWidget(self.txtBuscaPromocao, 1)
        self.cmbStatusFiltro = QtWidgets.QComboBox(self.toolbarCard)
        self.cmbStatusFiltro.setMinimumWidth(180)
        self.cmbStatusFiltro.setObjectName("cmbStatusFiltro")
        self.cmbStatusFiltro.addItem("")
        self.cmbStatusFiltro.addItem("")
        self.cmbStatusFiltro.addItem("")
        self.cmbStatusFiltro.addItem("")
        self.toolbarLayout.addWidget(self.cmbStatusFiltro)
        self.cmbTipoFiltro = QtWidgets.QComboBox(self.toolbarCard)
        self.cmbTipoFiltro.setMinimumWidth(180)
        self.cmbTipoFiltro.setObjectName("cmbTipoFiltro")
        self.cmbTipoFiltro.addItem("")
        self.cmbTipoFiltro.addItem("")
        self.cmbTipoFiltro.addItem("")
        self.cmbTipoFiltro.addItem("")
        self.toolbarLayout.addWidget(self.cmbTipoFiltro)
        self.btnAtualizar = QtWidgets.QPushButton(self.toolbarCard)
        self.btnAtualizar.setObjectName("btnAtualizar")
        self.toolbarLayout.addWidget(self.btnAtualizar)
        self.btnNovaPromocao = QtWidgets.QPushButton(self.toolbarCard)
        self.btnNovaPromocao.setObjectName("btnNovaPromocao")
        self.toolbarLayout.addWidget(self.btnNovaPromocao)
        self.btnDuplicarPromocao = QtWidgets.QPushButton(self.toolbarCard)
        self.btnDuplicarPromocao.setObjectName("btnDuplicarPromocao")
        self.toolbarLayout.addWidget(self.btnDuplicarPromocao)
        self.btnVincularProdutos = QtWidgets.QPushButton(self.toolbarCard)
        self.btnVincularProdutos.setObjectName("btnVincularProdutos")
        self.toolbarLayout.addWidget(self.btnVincularProdutos)
        self.contentWrapLayout.addWidget(self.toolbarCard)

        self.cardsLayout = QtWidgets.QHBoxLayout()
        self.cardsLayout.setSpacing(14)
        self.cardsLayout.setObjectName("cardsLayout")
        self.cardPromocoesAtivas = self._criar_card_metrica("cardPromocoesAtivas", "#2f80c9", "#dceeff")
        self.lblPromocoesAtivasValor = self.cardPromocoesAtivas.findChild(QtWidgets.QLabel, "metricValue")
        self.lblPromocoesAtivasValor.setObjectName("lblPromocoesAtivasValor")
        self.lblPromocoesAtivasTitulo = self.cardPromocoesAtivas.findChild(QtWidgets.QLabel, "metricTitle")
        self.lblPromocoesAtivasTitulo.setObjectName("lblPromocoesAtivasTitulo")
        self.cardsLayout.addWidget(self.cardPromocoesAtivas)
        self.cardAgendadas = self._criar_card_metrica("cardAgendadas", "#46b464", "#dff7e6")
        self.lblAgendadasValor = self.cardAgendadas.findChild(QtWidgets.QLabel, "metricValue")
        self.lblAgendadasValor.setObjectName("lblAgendadasValor")
        self.lblAgendadasTitulo = self.cardAgendadas.findChild(QtWidgets.QLabel, "metricTitle")
        self.lblAgendadasTitulo.setObjectName("lblAgendadasTitulo")
        self.cardsLayout.addWidget(self.cardAgendadas)
        self.cardProdutosPromocao = self._criar_card_metrica("cardProdutosPromocao", "#f0a126", "#fff0c9", dark=True)
        self.lblProdutosPromocaoValor = self.cardProdutosPromocao.findChild(QtWidgets.QLabel, "metricValue")
        self.lblProdutosPromocaoValor.setObjectName("lblProdutosPromocaoValor")
        self.lblProdutosPromocaoTitulo = self.cardProdutosPromocao.findChild(QtWidgets.QLabel, "metricTitle")
        self.lblProdutosPromocaoTitulo.setObjectName("lblProdutosPromocaoTitulo")
        self.cardsLayout.addWidget(self.cardProdutosPromocao)
        self.cardEncerradas = self._criar_card_metrica("cardEncerradas", "#697da3", "#e0e6f5")
        self.lblEncerradasValor = self.cardEncerradas.findChild(QtWidgets.QLabel, "metricValue")
        self.lblEncerradasValor.setObjectName("lblEncerradasValor")
        self.lblEncerradasTitulo = self.cardEncerradas.findChild(QtWidgets.QLabel, "metricTitle")
        self.lblEncerradasTitulo.setObjectName("lblEncerradasTitulo")
        self.cardsLayout.addWidget(self.cardEncerradas)
        self.contentWrapLayout.addLayout(self.cardsLayout)

        self.mainGridLayout = QtWidgets.QHBoxLayout()
        self.mainGridLayout.setSpacing(14)
        self.mainGridLayout.setObjectName("mainGridLayout")

        self.framePromocoes = QtWidgets.QFrame(self.contentWrap)
        self.framePromocoes.setMinimumWidth(860)
        self.framePromocoes.setObjectName("framePromocoes")
        self.framePromocoesLayout = QtWidgets.QVBoxLayout(self.framePromocoes)
        self.framePromocoesLayout.setContentsMargins(16, 16, 16, 16)
        self.framePromocoesLayout.setSpacing(12)
        self.framePromocoesLayout.setObjectName("framePromocoesLayout")
        self.lblPromocoesSection = QtWidgets.QLabel(self.framePromocoes)
        self.lblPromocoesSection.setProperty("sectionTitle", "true")
        self.lblPromocoesSection.setObjectName("lblPromocoesSection")
        self.framePromocoesLayout.addWidget(self.lblPromocoesSection)
        self.lblPromocoesHint = QtWidgets.QLabel(self.framePromocoes)
        self.lblPromocoesHint.setProperty("sectionHint", "true")
        self.lblPromocoesHint.setObjectName("lblPromocoesHint")
        self.framePromocoesLayout.addWidget(self.lblPromocoesHint)
        self.tablePromocoes = QtWidgets.QTableWidget(self.framePromocoes)
        self.tablePromocoes.setRowCount(0)
        self.tablePromocoes.setColumnCount(6)
        self.tablePromocoes.setAlternatingRowColors(True)
        self.tablePromocoes.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tablePromocoes.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tablePromocoes.setObjectName("tablePromocoes")
        for idx in range(6):
            item = QtWidgets.QTableWidgetItem()
            self.tablePromocoes.setHorizontalHeaderItem(idx, item)
        self.tablePromocoes.setColumnWidth(0, 90)
        self.tablePromocoes.setColumnWidth(1, 250)
        self.tablePromocoes.setColumnWidth(2, 180)
        self.tablePromocoes.setColumnWidth(3, 320)
        self.tablePromocoes.setColumnWidth(4, 120)
        self.tablePromocoes.horizontalHeader().setStretchLastSection(True)
        self.tablePromocoes.horizontalHeader().setDefaultSectionSize(138)
        self.tablePromocoes.horizontalHeader().setMinimumSectionSize(88)
        self.tablePromocoes.verticalHeader().setVisible(False)
        self.framePromocoesLayout.addWidget(self.tablePromocoes)
        self.mainGridLayout.addWidget(self.framePromocoes, 5)

        self.frameAgenda = QtWidgets.QFrame(self.contentWrap)
        self.frameAgenda.setMinimumWidth(430)
        self.frameAgenda.setMaximumWidth(500)
        self.frameAgenda.setObjectName("frameAgenda")
        self.frameAgendaLayout = QtWidgets.QVBoxLayout(self.frameAgenda)
        self.frameAgendaLayout.setContentsMargins(16, 16, 16, 16)
        self.frameAgendaLayout.setSpacing(12)
        self.frameAgendaLayout.setObjectName("frameAgendaLayout")
        self.lblAgendaSection = QtWidgets.QLabel(self.frameAgenda)
        self.lblAgendaSection.setProperty("sectionTitle", "true")
        self.lblAgendaSection.setObjectName("lblAgendaSection")
        self.frameAgendaLayout.addWidget(self.lblAgendaSection)
        self.lblAgendaHint = QtWidgets.QLabel(self.frameAgenda)
        self.lblAgendaHint.setProperty("sectionHint", "true")
        self.lblAgendaHint.setObjectName("lblAgendaHint")
        self.frameAgendaLayout.addWidget(self.lblAgendaHint)
        self.tableItensPromocao = QtWidgets.QTableWidget(self.frameAgenda)
        self.tableItensPromocao.setRowCount(0)
        self.tableItensPromocao.setColumnCount(5)
        self.tableItensPromocao.setAlternatingRowColors(True)
        self.tableItensPromocao.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableItensPromocao.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableItensPromocao.setObjectName("tableItensPromocao")
        for idx in range(5):
            item = QtWidgets.QTableWidgetItem()
            self.tableItensPromocao.setHorizontalHeaderItem(idx, item)
        self.tableItensPromocao.setColumnWidth(0, 200)
        self.tableItensPromocao.setColumnWidth(1, 90)
        self.tableItensPromocao.setColumnWidth(2, 90)
        self.tableItensPromocao.setColumnWidth(3, 80)
        self.tableItensPromocao.horizontalHeader().setStretchLastSection(True)
        self.tableItensPromocao.verticalHeader().setVisible(False)
        self.frameAgendaLayout.addWidget(self.tableItensPromocao)
        self.mainGridLayout.addWidget(self.frameAgenda, 2)
        self.contentWrapLayout.addLayout(self.mainGridLayout, 1)
        self.mainVLayout.addWidget(self.contentWrap, 1)

        self.frameStatusBar = QtWidgets.QFrame(self.centralWidget)
        self.frameStatusBar.setMinimumHeight(32)
        self.frameStatusBar.setObjectName("frameStatusBar")
        self.statusLayout = QtWidgets.QHBoxLayout(self.frameStatusBar)
        self.statusLayout.setContentsMargins(12, 0, 12, 0)
        self.statusLayout.setObjectName("statusLayout")
        self.lblStatusSistema = QtWidgets.QLabel(self.frameStatusBar)
        self.lblStatusSistema.setObjectName("lblStatusSistema")
        self.statusLayout.addWidget(self.lblStatusSistema)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.statusLayout.addItem(spacerItem1)
        self.lblStatusBar = QtWidgets.QLabel(self.frameStatusBar)
        self.lblStatusBar.setObjectName("lblStatusBar")
        self.statusLayout.addWidget(self.lblStatusBar)
        self.mainVLayout.addWidget(self.frameStatusBar)

        PainelPromocoes.setCentralWidget(self.centralWidget)

        self.retranslateUi(PainelPromocoes)
        QtCore.QMetaObject.connectSlotsByName(PainelPromocoes)

    def _criar_card_metrica(self, object_name, color, soft_color, dark=False):
        frame = QtWidgets.QFrame(self.centralWidget)
        frame.setObjectName(object_name)
        frame.setProperty("metricCard", "true")
        text_color = "#13283d" if dark else "white"
        title_color = "#5b4312" if dark else soft_color
        frame.setStyleSheet(
            f"""
            QFrame#{object_name} {{
                background-color: {color};
            }}
            QLabel {{
                color: {text_color};
                background-color: transparent;
            }}
            QLabel[metricTitle="true"] {{
                color: {title_color};
            }}
            """
        )
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        value = QtWidgets.QLabel(frame)
        value.setObjectName("metricValue")
        value.setProperty("metricValue", "true")
        layout.addWidget(value)
        title = QtWidgets.QLabel(frame)
        title.setObjectName("metricTitle")
        title.setProperty("metricTitle", "true")
        layout.addWidget(title)
        layout.addStretch()
        return frame

    def retranslateUi(self, PainelPromocoes):
        _translate = QtCore.QCoreApplication.translate
        PainelPromocoes.setWindowTitle(_translate("PainelPromocoes", "CSPdv - Promocoes"))
        self.lblLogo.setText(_translate("PainelPromocoes", "CSPdv"))
        self.lblModulo.setText(_translate("PainelPromocoes", "PROMOCOES E CAMPANHAS"))
        self.lblOperadorInfo.setText(_translate("PainelPromocoes", "Operador: ---"))
        self.lblDataHora.setText(_translate("PainelPromocoes", "--/--/---- --:--:--"))
        self.btnVoltarSelecao.setText(_translate("PainelPromocoes", "Voltar"))
        self.txtBuscaPromocao.setPlaceholderText(_translate("PainelPromocoes", "Buscar por nome da promocao, codigo, campanha ou produto vinculado"))
        self.cmbStatusFiltro.setItemText(0, _translate("PainelPromocoes", "Todos os status"))
        self.cmbStatusFiltro.setItemText(1, _translate("PainelPromocoes", "Ativas"))
        self.cmbStatusFiltro.setItemText(2, _translate("PainelPromocoes", "Agendadas"))
        self.cmbStatusFiltro.setItemText(3, _translate("PainelPromocoes", "Encerradas"))
        self.cmbTipoFiltro.setItemText(0, _translate("PainelPromocoes", "Todos os tipos"))
        self.cmbTipoFiltro.setItemText(1, _translate("PainelPromocoes", "Desconto por percentual"))
        self.cmbTipoFiltro.setItemText(2, _translate("PainelPromocoes", "Desconto por valor"))
        self.cmbTipoFiltro.setItemText(3, _translate("PainelPromocoes", "Preco promocional"))
        self.btnAtualizar.setText(_translate("PainelPromocoes", "Editar"))
        self.btnNovaPromocao.setText(_translate("PainelPromocoes", "Nova Promocao"))
        self.btnDuplicarPromocao.setText(_translate("PainelPromocoes", "Duplicar"))
        self.btnVincularProdutos.setText(_translate("PainelPromocoes", "Vincular Produtos"))
        self.lblPromocoesAtivasValor.setText(_translate("PainelPromocoes", "0"))
        self.lblPromocoesAtivasTitulo.setText(_translate("PainelPromocoes", "Promocoes Ativas"))
        self.lblAgendadasValor.setText(_translate("PainelPromocoes", "0"))
        self.lblAgendadasTitulo.setText(_translate("PainelPromocoes", "Campanhas Agendadas"))
        self.lblProdutosPromocaoValor.setText(_translate("PainelPromocoes", "0"))
        self.lblProdutosPromocaoTitulo.setText(_translate("PainelPromocoes", "Produtos em Promocao"))
        self.lblEncerradasValor.setText(_translate("PainelPromocoes", "0"))
        self.lblEncerradasTitulo.setText(_translate("PainelPromocoes", "Promocoes Encerradas"))
        self.lblPromocoesSection.setText(_translate("PainelPromocoes", "Promocoes Cadastradas"))
        self.lblPromocoesHint.setText(_translate("PainelPromocoes", "Gerencie campanhas, vigencias e regras promocionais em um painel unico."))
        item = self.tablePromocoes.horizontalHeaderItem(0)
        item.setText(_translate("PainelPromocoes", "Codigo"))
        item = self.tablePromocoes.horizontalHeaderItem(1)
        item.setText(_translate("PainelPromocoes", "Promocao"))
        item = self.tablePromocoes.horizontalHeaderItem(2)
        item.setText(_translate("PainelPromocoes", "Tipo"))
        item = self.tablePromocoes.horizontalHeaderItem(3)
        item.setText(_translate("PainelPromocoes", "Vigencia"))
        item = self.tablePromocoes.horizontalHeaderItem(4)
        item.setText(_translate("PainelPromocoes", "Status"))
        item = self.tablePromocoes.horizontalHeaderItem(5)
        item.setText(_translate("PainelPromocoes", "Alcance"))
        self.lblAgendaSection.setText(_translate("PainelPromocoes", "Itens Vinculados"))
        self.lblAgendaHint.setText(_translate("PainelPromocoes", "Visualize rapidamente os produtos ou grupos afetados pela promocao selecionada."))
        item = self.tableItensPromocao.horizontalHeaderItem(0)
        item.setText(_translate("PainelPromocoes", "Produto"))
        item = self.tableItensPromocao.horizontalHeaderItem(1)
        item.setText(_translate("PainelPromocoes", "Preco Atual"))
        item = self.tableItensPromocao.horizontalHeaderItem(2)
        item.setText(_translate("PainelPromocoes", "Preco Promo"))
        item = self.tableItensPromocao.horizontalHeaderItem(3)
        item.setText(_translate("PainelPromocoes", "Desconto"))
        item = self.tableItensPromocao.horizontalHeaderItem(4)
        item.setText(_translate("PainelPromocoes", "Observacao"))
        self.lblStatusSistema.setText(_translate("PainelPromocoes", "Sistema online"))
        self.lblStatusBar.setText(_translate("PainelPromocoes", "CSPdv - Modulo de Promocoes"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    PainelPromocoes = QtWidgets.QMainWindow()
    ui = Ui_PainelPromocoes()
    ui.setupUi(PainelPromocoes)
    PainelPromocoes.show()
    sys.exit(app.exec_())
