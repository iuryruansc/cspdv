# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_PainelEstoque(object):
    def setupUi(self, PainelEstoque):
        PainelEstoque.setObjectName("PainelEstoque")
        PainelEstoque.resize(1440, 860)
        PainelEstoque.setMinimumSize(QtCore.QSize(1320, 820))
        self.centralWidget = QtWidgets.QWidget(PainelEstoque)
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
            QFrame#frameToolbar {
                background-color: transparent;
            }
            QFrame#toolbarCard {
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
            QPushButton#btnFiltrar {
                background-color: #e9f3fb;
                color: #205d8f;
                border: 1px solid #b8d3ea;
            }
            QPushButton#btnFiltrar:hover {
                background-color: #d8ebfa;
            }
            QPushButton#btnNovoProduto, QPushButton#btnNovoLote {
                background-color: #2f80c9;
                color: white;
            }
            QPushButton#btnNovoProduto:hover, QPushButton#btnNovoLote:hover {
                background-color: #276faa;
            }
            QPushButton#btnAjusteEstoque {
                background-color: #f4a329;
                color: #1f2a36;
            }
            QPushButton#btnAjusteEstoque:hover {
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
            QFrame#frameMainGrid {
                background-color: transparent;
            }
            QFrame#frameProdutos, QFrame#frameMovimentacoes {
                background-color: white;
                border: 1px solid #d6e2ec;
                border-radius: 16px;
            }
            QLabel[sectionTitle="true"] {
                font-size: 14px;
                font-weight: 800;
                color: #153552;
                padding: 0;
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

        self.frameToolbar = QtWidgets.QFrame(self.contentWrap)
        self.frameToolbar.setObjectName("frameToolbar")
        self.toolbarOuter = QtWidgets.QVBoxLayout(self.frameToolbar)
        self.toolbarOuter.setContentsMargins(0, 0, 0, 0)
        self.toolbarOuter.setObjectName("toolbarOuter")
        self.toolbarCard = QtWidgets.QFrame(self.frameToolbar)
        self.toolbarCard.setObjectName("toolbarCard")
        self.toolbarHLayout = QtWidgets.QHBoxLayout(self.toolbarCard)
        self.toolbarHLayout.setContentsMargins(14, 14, 14, 14)
        self.toolbarHLayout.setSpacing(10)
        self.toolbarHLayout.setObjectName("toolbarHLayout")
        self.txtBuscaProduto = QtWidgets.QLineEdit(self.toolbarCard)
        self.txtBuscaProduto.setMinimumWidth(420)
        self.txtBuscaProduto.setObjectName("txtBuscaProduto")
        self.toolbarHLayout.addWidget(self.txtBuscaProduto, 1)
        self.cmbCategoriaFiltro = QtWidgets.QComboBox(self.toolbarCard)
        self.cmbCategoriaFiltro.setMinimumWidth(170)
        self.cmbCategoriaFiltro.setObjectName("cmbCategoriaFiltro")
        self.cmbCategoriaFiltro.addItem("")
        self.toolbarHLayout.addWidget(self.cmbCategoriaFiltro)
        self.cmbFornecedorFiltro = QtWidgets.QComboBox(self.toolbarCard)
        self.cmbFornecedorFiltro.setMinimumWidth(170)
        self.cmbFornecedorFiltro.setObjectName("cmbFornecedorFiltro")
        self.cmbFornecedorFiltro.addItem("")
        self.toolbarHLayout.addWidget(self.cmbFornecedorFiltro)
        self.btnFiltrar = QtWidgets.QPushButton(self.toolbarCard)
        self.btnFiltrar.setObjectName("btnFiltrar")
        self.toolbarHLayout.addWidget(self.btnFiltrar)
        self.btnNovoProduto = QtWidgets.QPushButton(self.toolbarCard)
        self.btnNovoProduto.setObjectName("btnNovoProduto")
        self.toolbarHLayout.addWidget(self.btnNovoProduto)
        self.btnNovoLote = QtWidgets.QPushButton(self.toolbarCard)
        self.btnNovoLote.setObjectName("btnNovoLote")
        self.toolbarHLayout.addWidget(self.btnNovoLote)
        self.btnAjusteEstoque = QtWidgets.QPushButton(self.toolbarCard)
        self.btnAjusteEstoque.setObjectName("btnAjusteEstoque")
        self.toolbarHLayout.addWidget(self.btnAjusteEstoque)
        self.toolbarOuter.addWidget(self.toolbarCard)
        self.contentWrapLayout.addWidget(self.frameToolbar)

        self.cardsHLayout = QtWidgets.QHBoxLayout()
        self.cardsHLayout.setSpacing(14)
        self.cardsHLayout.setObjectName("cardsHLayout")
        self.cardProdutosAtivos = self._criar_card_metrica("cardProdutosAtivos", "#2f80c9", "#dceeff")
        self.lblProdutosAtivosValor = self.cardProdutosAtivos.findChild(QtWidgets.QLabel, "metricValue")
        self.lblProdutosAtivosValor.setObjectName("lblProdutosAtivosValor")
        self.lblProdutosAtivosTitulo = self.cardProdutosAtivos.findChild(QtWidgets.QLabel, "metricTitle")
        self.lblProdutosAtivosTitulo.setObjectName("lblProdutosAtivosTitulo")
        self.cardsHLayout.addWidget(self.cardProdutosAtivos)
        self.cardLotesAtivos = self._criar_card_metrica("cardLotesAtivos", "#46b464", "#dff7e6")
        self.lblLotesAtivosValor = self.cardLotesAtivos.findChild(QtWidgets.QLabel, "metricValue")
        self.lblLotesAtivosValor.setObjectName("lblLotesAtivosValor")
        self.lblLotesAtivosTitulo = self.cardLotesAtivos.findChild(QtWidgets.QLabel, "metricTitle")
        self.lblLotesAtivosTitulo.setObjectName("lblLotesAtivosTitulo")
        self.cardsHLayout.addWidget(self.cardLotesAtivos)
        self.cardItensBaixoEstoque = self._criar_card_metrica("cardItensBaixoEstoque", "#f0a126", "#fff0c9", dark=True)
        self.lblItensBaixoEstoqueValor = self.cardItensBaixoEstoque.findChild(QtWidgets.QLabel, "metricValue")
        self.lblItensBaixoEstoqueValor.setObjectName("lblItensBaixoEstoqueValor")
        self.lblItensBaixoEstoqueTitulo = self.cardItensBaixoEstoque.findChild(QtWidgets.QLabel, "metricTitle")
        self.lblItensBaixoEstoqueTitulo.setObjectName("lblItensBaixoEstoqueTitulo")
        self.cardsHLayout.addWidget(self.cardItensBaixoEstoque)
        self.cardMovimentacoesDia = self._criar_card_metrica("cardMovimentacoesDia", "#697da3", "#e0e6f5")
        self.lblMovimentacoesDiaValor = self.cardMovimentacoesDia.findChild(QtWidgets.QLabel, "metricValue")
        self.lblMovimentacoesDiaValor.setObjectName("lblMovimentacoesDiaValor")
        self.lblMovimentacoesDiaTitulo = self.cardMovimentacoesDia.findChild(QtWidgets.QLabel, "metricTitle")
        self.lblMovimentacoesDiaTitulo.setObjectName("lblMovimentacoesDiaTitulo")
        self.cardsHLayout.addWidget(self.cardMovimentacoesDia)
        self.contentWrapLayout.addLayout(self.cardsHLayout)

        self.frameMainGrid = QtWidgets.QFrame(self.contentWrap)
        self.frameMainGrid.setObjectName("frameMainGrid")
        self.tablesHLayout = QtWidgets.QHBoxLayout(self.frameMainGrid)
        self.tablesHLayout.setContentsMargins(0, 0, 0, 0)
        self.tablesHLayout.setSpacing(14)
        self.tablesHLayout.setObjectName("tablesHLayout")

        self.frameProdutos = QtWidgets.QFrame(self.frameMainGrid)
        self.frameProdutos.setObjectName("frameProdutos")
        self.frameProdutosLayout = QtWidgets.QVBoxLayout(self.frameProdutos)
        self.frameProdutosLayout.setContentsMargins(16, 16, 16, 16)
        self.frameProdutosLayout.setSpacing(12)
        self.frameProdutosLayout.setObjectName("frameProdutosLayout")
        self.lblProdutosSection = QtWidgets.QLabel(self.frameProdutos)
        self.lblProdutosSection.setProperty("sectionTitle", "true")
        self.lblProdutosSection.setObjectName("lblProdutosSection")
        self.frameProdutosLayout.addWidget(self.lblProdutosSection)
        self.lblProdutosHint = QtWidgets.QLabel(self.frameProdutos)
        self.lblProdutosHint.setProperty("sectionHint", "true")
        self.lblProdutosHint.setObjectName("lblProdutosHint")
        self.frameProdutosLayout.addWidget(self.lblProdutosHint)
        self.tableProdutosEstoque = QtWidgets.QTableWidget(self.frameProdutos)
        self.tableProdutosEstoque.setRowCount(0)
        self.tableProdutosEstoque.setColumnCount(8)
        self.tableProdutosEstoque.setAlternatingRowColors(True)
        self.tableProdutosEstoque.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableProdutosEstoque.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableProdutosEstoque.setObjectName("tableProdutosEstoque")
        for idx in range(8):
            item = QtWidgets.QTableWidgetItem()
            self.tableProdutosEstoque.setHorizontalHeaderItem(idx, item)
        self.tableProdutosEstoque.horizontalHeader().setStretchLastSection(False)
        self.tableProdutosEstoque.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.tableProdutosEstoque.horizontalHeader().setDefaultSectionSize(118)
        self.tableProdutosEstoque.horizontalHeader().setMinimumSectionSize(72)
        self.tableProdutosEstoque.setColumnWidth(0, 110)
        self.tableProdutosEstoque.setColumnWidth(2, 140)
        self.tableProdutosEstoque.setColumnWidth(3, 140)
        self.tableProdutosEstoque.setColumnWidth(4, 120)
        self.tableProdutosEstoque.setColumnWidth(5, 110)
        self.tableProdutosEstoque.setColumnWidth(6, 80)
        self.tableProdutosEstoque.setColumnWidth(7, 110)
        self.tableProdutosEstoque.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableProdutosEstoque.verticalHeader().setVisible(False)
        self.frameProdutosLayout.addWidget(self.tableProdutosEstoque)
        self.tablesHLayout.addWidget(self.frameProdutos, 2)

        self.frameMovimentacoes = QtWidgets.QFrame(self.frameMainGrid)
        self.frameMovimentacoes.setMinimumWidth(430)
        self.frameMovimentacoes.setMaximumWidth(500)
        self.frameMovimentacoes.setObjectName("frameMovimentacoes")
        self.frameMovimentacoesLayout = QtWidgets.QVBoxLayout(self.frameMovimentacoes)
        self.frameMovimentacoesLayout.setContentsMargins(16, 16, 16, 16)
        self.frameMovimentacoesLayout.setSpacing(12)
        self.frameMovimentacoesLayout.setObjectName("frameMovimentacoesLayout")
        self.lblMovimentacoesSection = QtWidgets.QLabel(self.frameMovimentacoes)
        self.lblMovimentacoesSection.setProperty("sectionTitle", "true")
        self.lblMovimentacoesSection.setObjectName("lblMovimentacoesSection")
        self.frameMovimentacoesLayout.addWidget(self.lblMovimentacoesSection)
        self.lblMovimentacoesHint = QtWidgets.QLabel(self.frameMovimentacoes)
        self.lblMovimentacoesHint.setProperty("sectionHint", "true")
        self.lblMovimentacoesHint.setObjectName("lblMovimentacoesHint")
        self.frameMovimentacoesLayout.addWidget(self.lblMovimentacoesHint)
        self.tableMovimentacoesEstoque = QtWidgets.QTableWidget(self.frameMovimentacoes)
        self.tableMovimentacoesEstoque.setRowCount(0)
        self.tableMovimentacoesEstoque.setColumnCount(5)
        self.tableMovimentacoesEstoque.setAlternatingRowColors(True)
        self.tableMovimentacoesEstoque.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableMovimentacoesEstoque.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableMovimentacoesEstoque.setObjectName("tableMovimentacoesEstoque")
        for idx in range(5):
            item = QtWidgets.QTableWidgetItem()
            self.tableMovimentacoesEstoque.setHorizontalHeaderItem(idx, item)
        self.tableMovimentacoesEstoque.horizontalHeader().setStretchLastSection(False)
        self.tableMovimentacoesEstoque.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tableMovimentacoesEstoque.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableMovimentacoesEstoque.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tableMovimentacoesEstoque.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.tableMovimentacoesEstoque.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.tableMovimentacoesEstoque.verticalHeader().setVisible(False)
        self.frameMovimentacoesLayout.addWidget(self.tableMovimentacoesEstoque)
        self.tablesHLayout.addWidget(self.frameMovimentacoes, 1)
        self.contentWrapLayout.addWidget(self.frameMainGrid, 1)
        self.mainVLayout.addWidget(self.contentWrap, 1)

        self.frameStatusBar = QtWidgets.QFrame(self.centralWidget)
        self.frameStatusBar.setMinimumHeight(32)
        self.frameStatusBar.setObjectName("frameStatusBar")
        self.statusHLayout = QtWidgets.QHBoxLayout(self.frameStatusBar)
        self.statusHLayout.setContentsMargins(12, 0, 12, 0)
        self.statusHLayout.setObjectName("statusHLayout")
        self.lblStatusSistema = QtWidgets.QLabel(self.frameStatusBar)
        self.lblStatusSistema.setObjectName("lblStatusSistema")
        self.statusHLayout.addWidget(self.lblStatusSistema)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.statusHLayout.addItem(spacerItem1)
        self.lblStatusBar = QtWidgets.QLabel(self.frameStatusBar)
        self.lblStatusBar.setObjectName("lblStatusBar")
        self.statusHLayout.addWidget(self.lblStatusBar)
        self.mainVLayout.addWidget(self.frameStatusBar)
        PainelEstoque.setCentralWidget(self.centralWidget)

        self.retranslateUi(PainelEstoque)
        QtCore.QMetaObject.connectSlotsByName(PainelEstoque)

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

    def retranslateUi(self, PainelEstoque):
        _translate = QtCore.QCoreApplication.translate
        PainelEstoque.setWindowTitle(_translate("PainelEstoque", "CSPdv - Estoque"))
        self.lblLogo.setText(_translate("PainelEstoque", "CSPdv"))
        self.lblModulo.setText(_translate("PainelEstoque", "ESTOQUE E MOVIMENTACOES"))
        self.lblOperadorInfo.setText(_translate("PainelEstoque", "Operador: ---"))
        self.lblDataHora.setText(_translate("PainelEstoque", "--/--/---- --:--:--"))
        self.btnVoltarSelecao.setText(_translate("PainelEstoque", "Voltar"))
        self.txtBuscaProduto.setPlaceholderText(_translate("PainelEstoque", "Buscar por produto, codigo de barras, lote ou marca"))
        self.cmbCategoriaFiltro.setItemText(0, _translate("PainelEstoque", "Todas as categorias"))
        self.cmbFornecedorFiltro.setItemText(0, _translate("PainelEstoque", "Todos os fornecedores"))
        self.btnFiltrar.setText(_translate("PainelEstoque", "Filtrar"))
        self.btnNovoProduto.setText(_translate("PainelEstoque", "Novo Produto"))
        self.btnNovoLote.setText(_translate("PainelEstoque", "Novo Lote"))
        self.btnAjusteEstoque.setText(_translate("PainelEstoque", "Ajuste de Estoque"))
        self.lblProdutosAtivosValor.setText(_translate("PainelEstoque", "0"))
        self.lblProdutosAtivosTitulo.setText(_translate("PainelEstoque", "Produtos Ativos"))
        self.lblLotesAtivosValor.setText(_translate("PainelEstoque", "0"))
        self.lblLotesAtivosTitulo.setText(_translate("PainelEstoque", "Lotes Ativos"))
        self.lblItensBaixoEstoqueValor.setText(_translate("PainelEstoque", "0"))
        self.lblItensBaixoEstoqueTitulo.setText(_translate("PainelEstoque", "Estoque Critico"))
        self.lblMovimentacoesDiaValor.setText(_translate("PainelEstoque", "0"))
        self.lblMovimentacoesDiaTitulo.setText(_translate("PainelEstoque", "Movimentacoes do Dia"))
        self.lblProdutosSection.setText(_translate("PainelEstoque", "Produtos e Lotes"))
        self.lblProdutosHint.setText(_translate("PainelEstoque", "Acompanhe estoque, validade e precos em uma visao operacional unica."))
        item = self.tableProdutosEstoque.horizontalHeaderItem(0)
        item.setText(_translate("PainelEstoque", "Cod."))
        item = self.tableProdutosEstoque.horizontalHeaderItem(1)
        item.setText(_translate("PainelEstoque", "Produto"))
        item = self.tableProdutosEstoque.horizontalHeaderItem(2)
        item.setText(_translate("PainelEstoque", "Categoria"))
        item = self.tableProdutosEstoque.horizontalHeaderItem(3)
        item.setText(_translate("PainelEstoque", "Marca"))
        item = self.tableProdutosEstoque.horizontalHeaderItem(4)
        item.setText(_translate("PainelEstoque", "Lote"))
        item = self.tableProdutosEstoque.horizontalHeaderItem(5)
        item.setText(_translate("PainelEstoque", "Validade"))
        item = self.tableProdutosEstoque.horizontalHeaderItem(6)
        item.setText(_translate("PainelEstoque", "Qtd."))
        item = self.tableProdutosEstoque.horizontalHeaderItem(7)
        item.setText(_translate("PainelEstoque", "Preco Venda"))
        self.lblMovimentacoesSection.setText(_translate("PainelEstoque", "Ultimas Movimentacoes"))
        self.lblMovimentacoesHint.setText(_translate("PainelEstoque", "Historico recente para conferencias e analise rapida de entradas e saidas."))
        item = self.tableMovimentacoesEstoque.horizontalHeaderItem(0)
        item.setText(_translate("PainelEstoque", "Data/Hora"))
        item = self.tableMovimentacoesEstoque.horizontalHeaderItem(1)
        item.setText(_translate("PainelEstoque", "Produto"))
        item = self.tableMovimentacoesEstoque.horizontalHeaderItem(2)
        item.setText(_translate("PainelEstoque", "Tipo"))
        item = self.tableMovimentacoesEstoque.horizontalHeaderItem(3)
        item.setText(_translate("PainelEstoque", "Qtd."))
        item = self.tableMovimentacoesEstoque.horizontalHeaderItem(4)
        item.setText(_translate("PainelEstoque", "Usuario"))
        self.lblStatusSistema.setText(_translate("PainelEstoque", "Sistema online"))
        self.lblStatusBar.setText(_translate("PainelEstoque", "CSPdv - Modulo de Estoque"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    PainelEstoque = QtWidgets.QMainWindow()
    ui = Ui_PainelEstoque()
    ui.setupUi(PainelEstoque)
    PainelEstoque.show()
    sys.exit(app.exec_())
