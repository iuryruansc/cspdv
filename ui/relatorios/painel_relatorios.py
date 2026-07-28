# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel


class Ui_PainelRelatorios(object):
    def setupUi(self, PainelRelatorios):
        PainelRelatorios.setObjectName("PainelRelatorios")
        PainelRelatorios.resize(1366, 768)
        self.centralWidget = QtWidgets.QWidget(PainelRelatorios)
        self.centralWidget.setObjectName("centralWidget")
        self.mainVLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.mainVLayout.setContentsMargins(0, 0, 0, 0)
        self.mainVLayout.setSpacing(0)
        self.mainVLayout.setObjectName("mainVLayout")

        # ── Header ────────────────────────────────────────────────────
        self.frameHeader = QtWidgets.QFrame(self.centralWidget)
        self.frameHeader.setStyleSheet(
            "QFrame#frameHeader {\n"
            " background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #153552, stop:0.55 #1d4c74, stop:1 #2f75b0);\n"
            " border-bottom: 1px solid rgba(255,255,255,28);\n"
            "}\n"
            "QLabel#lblLogo { color: white; font-size: 30px; font-weight: 800; }\n"
            "QLabel#lblModulo {\n"
            " color: #ffe59d; font-size: 12px; font-weight: 700;\n"
            " padding: 8px 14px; border-radius: 8px;\n"
            " background-color: rgba(255,255,255,0.10);\n"
            " border: 1px solid rgba(255,255,255,0.18);\n"
            "}\n"
            "QLabel#lblOperadorInfo, QLabel#lblPeriodoAtual {\n"
            " color: #dbeaf7; font-size: 12px; font-weight: 600;\n"
            "}\n"
            "QPushButton#btnVoltarSelecao {\n"
            " background-color: #d92b2b; color: white; border: none;\n"
            " border-radius: 10px; padding: 10px 24px;\n"
            " font-size: 12px; font-weight: 700;\n"
            "}\n"
            "QPushButton#btnVoltarSelecao:hover { background-color: #c11f1f; }\n"
        )
        self.frameHeader.setObjectName("frameHeader")
        self.headerLayout = QtWidgets.QHBoxLayout(self.frameHeader)
        self.headerLayout.setContentsMargins(18, 12, 18, 12)
        self.headerLayout.setSpacing(14)
        self.headerLayout.setObjectName("headerLayout")
        self.lblLogo = QtWidgets.QLabel(self.frameHeader)
        self.lblLogo.setObjectName("lblLogo")
        self.headerLayout.addWidget(self.lblLogo)
        self.frameSepHeader = QtWidgets.QFrame(self.frameHeader)
        self.frameSepHeader.setStyleSheet("background-color: rgba(255,255,255,0.25);")
        self.frameSepHeader.setFrameShape(QtWidgets.QFrame.VLine)
        self.frameSepHeader.setObjectName("frameSepHeader")
        self.headerLayout.addWidget(self.frameSepHeader)
        self.lblModulo = QtWidgets.QLabel(self.frameHeader)
        self.lblModulo.setObjectName("lblModulo")
        self.headerLayout.addWidget(self.lblModulo)
        spacerHeader = QtWidgets.QSpacerItem(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.headerLayout.addItem(spacerHeader)
        self.lblOperadorInfo = QtWidgets.QLabel(self.frameHeader)
        self.lblOperadorInfo.setObjectName("lblOperadorInfo")
        self.headerLayout.addWidget(self.lblOperadorInfo)
        self.lblPeriodoAtual = QtWidgets.QLabel(self.frameHeader)
        self.lblPeriodoAtual.setObjectName("lblPeriodoAtual")
        self.headerLayout.addWidget(self.lblPeriodoAtual)
        self.btnVoltarSelecao = QtWidgets.QPushButton(self.frameHeader)
        self.btnVoltarSelecao.setMinimumSize(QtCore.QSize(140, 42))
        self.btnVoltarSelecao.setObjectName("btnVoltarSelecao")
        self.headerLayout.addWidget(self.btnVoltarSelecao)
        self.mainVLayout.addWidget(self.frameHeader)

        # ── Toolbar (single line) ─────────────────────────────────────
        self.frameToolbar = QtWidgets.QFrame(self.centralWidget)
        self.frameToolbar.setMinimumSize(QtCore.QSize(0, 56))
        self.frameToolbar.setStyleSheet(
            "QFrame#frameToolbar { background-color: #eef5fb; border-bottom: 1px solid #c8d8e8; }\n"
            "QFrame#frameToolbarInner {\n"
            " background-color: rgba(255,255,255,0.88);\n"
            " border: 1px solid #d7e4ef; border-radius: 8px;\n"
            "}\n"
            "QTabBar::tab {\n"
            " background-color: #e8f0f8; color: #46627d;\n"
            " border: 1px solid #c8d8e8; border-bottom: none;\n"
            " border-radius: 6px 6px 0 0;\n"
            " padding: 8px 18px; font-size: 12px; font-weight: 600;\n"
            " margin-right: 2px;\n"
            "}\n"
            "QTabBar::tab:selected { background-color: #3585c8; color: white; border-color: #3585c8; }\n"
            "QTabBar::tab:hover:!selected { background-color: #d0e2f2; }\n"
            "QComboBox, QDateEdit {\n"
            " background-color: white; border: 1px solid #b8cde0; border-radius: 4px;\n"
            " padding: 6px 8px; font-size: 12px; min-height: 34px;\n"
            "}\n"
            "QPushButton {\n"
            " background-color: #3585c8; color: white; border: none; border-radius: 4px;\n"
            " padding: 6px 12px; font-size: 12px; font-weight: bold; min-height: 34px;\n"
            "}\n"
            "QPushButton:hover { background-color: #2b74b4; }\n"
            "QPushButton#btnExportarCsv { background-color: #5cb85c; }\n"
            "QPushButton#btnExportarCsv:hover { background-color: #4aa14a; }\n"
        )
        self.frameToolbar.setObjectName("frameToolbar")
        self.toolbarLayout = QtWidgets.QHBoxLayout(self.frameToolbar)
        self.toolbarLayout.setContentsMargins(12, 6, 12, 6)
        self.toolbarLayout.setSpacing(8)
        self.toolbarLayout.setObjectName("toolbarLayout")
        self.frameToolbarInner = QtWidgets.QFrame(self.frameToolbar)
        self.frameToolbarInner.setObjectName("frameToolbarInner")
        self.toolbarInnerLayout = QtWidgets.QHBoxLayout(self.frameToolbarInner)
        self.toolbarInnerLayout.setContentsMargins(10, 6, 10, 6)
        self.toolbarInnerLayout.setSpacing(8)
        self.toolbarInnerLayout.setObjectName("toolbarInnerLayout")
        self.tabTipoRelatorio = QtWidgets.QTabBar(self.frameToolbarInner)
        self.tabTipoRelatorio.setObjectName("tabTipoRelatorio")
        self.tabTipoRelatorio.addTab("Matriz Anual")
        self.tabTipoRelatorio.addTab("Produtos")
        self.tabTipoRelatorio.addTab("Clientes")
        self.tabTipoRelatorio.addTab("Caixa")
        self.toolbarInnerLayout.addWidget(self.tabTipoRelatorio)
        self.framePeriodoFiltro = QtWidgets.QFrame(self.frameToolbarInner)
        self.framePeriodoFiltro.setObjectName("framePeriodoFiltro")
        self.periodoLayout = QtWidgets.QHBoxLayout(self.framePeriodoFiltro)
        self.periodoLayout.setContentsMargins(0, 0, 0, 0)
        self.periodoLayout.setSpacing(6)
        self.periodoLayout.setObjectName("periodoLayout")
        self.lblPeriodoDe = QtWidgets.QLabel(self.framePeriodoFiltro)
        self.lblPeriodoDe.setObjectName("lblPeriodoDe")
        self.periodoLayout.addWidget(self.lblPeriodoDe)
        self.dateInicial = QtWidgets.QDateEdit(self.framePeriodoFiltro)
        self.dateInicial.setMinimumWidth(96)
        self.dateInicial.setMaximumWidth(106)
        self.dateInicial.setCalendarPopup(True)
        self.dateInicial.setObjectName("dateInicial")
        self.periodoLayout.addWidget(self.dateInicial)
        self.lblPeriodoAte = QtWidgets.QLabel(self.framePeriodoFiltro)
        self.lblPeriodoAte.setObjectName("lblPeriodoAte")
        self.periodoLayout.addWidget(self.lblPeriodoAte)
        self.dateFinal = QtWidgets.QDateEdit(self.framePeriodoFiltro)
        self.dateFinal.setMinimumWidth(96)
        self.dateFinal.setMaximumWidth(106)
        self.dateFinal.setCalendarPopup(True)
        self.dateFinal.setObjectName("dateFinal")
        self.periodoLayout.addWidget(self.dateFinal)
        self.toolbarInnerLayout.addWidget(self.framePeriodoFiltro)
        spacerToolbar = QtWidgets.QSpacerItem(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.toolbarInnerLayout.addItem(spacerToolbar)
        self.btnGerarRelatorio = QtWidgets.QPushButton(self.frameToolbarInner)
        self.btnGerarRelatorio.setMinimumWidth(140)
        self.btnGerarRelatorio.setObjectName("btnGerarRelatorio")
        self.toolbarInnerLayout.addWidget(self.btnGerarRelatorio)
        self.btnExportarCsv = QtWidgets.QPushButton(self.frameToolbarInner)
        self.btnExportarCsv.setMinimumWidth(140)
        self.btnExportarCsv.setObjectName("btnExportarCsv")
        self.toolbarInnerLayout.addWidget(self.btnExportarCsv)
        self.toolbarLayout.addWidget(self.frameToolbarInner)
        self.mainVLayout.addWidget(self.frameToolbar)

        # ── Content ───────────────────────────────────────────────────
        self.contentLayout = QtWidgets.QVBoxLayout()
        self.contentLayout.setContentsMargins(16, 12, 16, 8)
        self.contentLayout.setSpacing(10)
        self.contentLayout.setObjectName("contentLayout")

        # Chips row (shared across tabs 1-3, hidden on tab 0)
        self.chipsFrame = QtWidgets.QFrame(self.centralWidget)
        self.chipsFrame.setObjectName("chipsFrame")
        self.chipsFrame.setStyleSheet("QFrame#chipsFrame { background: transparent; border: none; }")
        self.chipsLayout = QtWidgets.QHBoxLayout(self.chipsFrame)
        self.chipsLayout.setContentsMargins(0, 0, 0, 0)
        self.chipsLayout.setSpacing(10)
        self.chipsLayout.setObjectName("chipsLayout")
        self.chipVendas = self._criar_chip("#3585c8", "#d8ebfb", "chipVendas")
        self.chipsLayout.addWidget(self.chipVendas)
        self.chipFaturamento = self._criar_chip("#5cb85c", "#daf0da", "chipFaturamento")
        self.chipsLayout.addWidget(self.chipFaturamento)
        self.chipTicketMedio = self._criar_chip("#9b59b6", "#ebd7f5", "chipTicketMedio")
        self.chipsLayout.addWidget(self.chipTicketMedio)
        self.chipClientes = self._criar_chip("#e67e22", "#fbe0c3", "chipClientes")
        self.chipsLayout.addWidget(self.chipClientes)
        spacerChips = QtWidgets.QSpacerItem(
            40, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.chipsLayout.addItem(spacerChips)
        self.contentLayout.addWidget(self.chipsFrame)

        # Stacked widget for per-tab content
        self.stackedContent = QtWidgets.QStackedWidget(self.centralWidget)
        self.stackedContent.setObjectName("stackedContent")

        _TABELA_STYLE = (
            "QFrame#frame { background-color: white; border: 1px solid #b8cde0; border-radius: 6px; }\n"
            "QLabel[sectionTitle=\"true\"] {\n"
            " background-color: #f0f6fc; color: #1a3a5c; font-size: 13px; font-weight: bold;\n"
            " padding: 8px 12px; border-bottom: 1px solid #d8e3ee;\n"
            " border-top-left-radius: 6px; border-top-right-radius: 6px;\n"
            "}\n"
            "QTableWidget {\n"
            " border: none; background-color: white; gridline-color: #e8eff5;\n"
            " font-size: 12px; selection-background-color: #dbeafe; selection-color: #102a43;\n"
            " alternate-background-color: #f7fafd;\n"
            "}\n"
            "QTableWidget::item { padding: 4px 8px; }\n"
            "QHeaderView::section {\n"
            " background-color: #f0f6fc; color: #1a3a5c; font-size: 11px; font-weight: bold;\n"
            " border: none; border-right: 1px solid #dce8f0;\n"
            " border-bottom: 2px solid #3585c8; padding: 5px 8px;\n"
            "}\n"
        )

        # ── Tab 0: Matriz Anual ───────────────────────────────────────
        self.pageMatriz = QtWidgets.QWidget()
        self.pageMatriz.setObjectName("pageMatriz")
        layMatriz = QtWidgets.QVBoxLayout(self.pageMatriz)
        layMatriz.setContentsMargins(0, 0, 0, 0)
        layMatriz.setSpacing(10)

        # Stock KPI cards + Year selector row
        self.matrizCardsLayout = QtWidgets.QHBoxLayout()
        self.matrizCardsLayout.setSpacing(10)
        self.matrizCardsLayout.setObjectName("matrizCardsLayout")
        self.lblAnoLabel = QtWidgets.QLabel("Ano:")
        self.lblAnoLabel.setStyleSheet("font-size: 13px; font-weight: bold; color: #1a3a5c; padding: 0 4px;")
        self.matrizCardsLayout.addWidget(self.lblAnoLabel)
        self.cmbAno = QtWidgets.QComboBox()
        self.cmbAno.setMinimumWidth(100)
        self.cmbAno.setMaximumWidth(120)
        self.matrizCardsLayout.addWidget(self.cmbAno)
        self.cardEstoqueBruto = self._criar_chip("#3585c8", "#d8ebfb", "cardEstoqueBruto")
        self.matrizCardsLayout.addWidget(self.cardEstoqueBruto)
        self.cardEstoqueLiquido = self._criar_chip("#17a2b8", "#cceff0", "cardEstoqueLiquido")
        self.matrizCardsLayout.addWidget(self.cardEstoqueLiquido)
        self.cardTotalBruto = self._criar_chip("#5cb85c", "#daf0da", "cardTotalBruto")
        self.matrizCardsLayout.addWidget(self.cardTotalBruto)
        self.cardTotalLiquido = self._criar_chip("#9b59b6", "#ebd7f5", "cardTotalLiquido")
        self.matrizCardsLayout.addWidget(self.cardTotalLiquido)
        spacerMatriz = QtWidgets.QSpacerItem(
            40, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.matrizCardsLayout.addItem(spacerMatriz)
        layMatriz.addLayout(self.matrizCardsLayout)

        # Matrix table frame
        self.frameMatriz = QtWidgets.QFrame(self.pageMatriz)
        self.frameMatriz.setObjectName("frame")
        self.frameMatriz.setStyleSheet(_TABELA_STYLE)
        layFrameMatriz = QtWidgets.QVBoxLayout(self.frameMatriz)
        layFrameMatriz.setContentsMargins(0, 0, 0, 0)
        layFrameMatriz.setSpacing(0)
        self.lblMatrizSecao = QtWidgets.QLabel(self.frameMatriz)
        self.lblMatrizSecao.setProperty("sectionTitle", "true")
        self.lblMatrizSecao.setObjectName("lblMatrizSecao")
        layFrameMatriz.addWidget(self.lblMatrizSecao)
        self.tableMatriz = QtWidgets.QTableWidget(self.frameMatriz)
        self.tableMatriz.setRowCount(0)
        self.tableMatriz.setColumnCount(24)
        self.tableMatriz.setObjectName("tableMatriz")
        self.tableMatriz.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableMatriz.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableMatriz.verticalHeader().setVisible(True)
        self.tableMatriz.horizontalHeader().setVisible(True)
        self.tableMatriz.setAlternatingRowColors(True)
        self.tableMatriz.setShowGrid(True)
        layFrameMatriz.addWidget(self.tableMatriz)
        layMatriz.addWidget(self.frameMatriz, 1)
        self.stackedContent.addWidget(self.pageMatriz)

        # ── Tab 1: Produtos ────────────────────────────────────────────
        self.pageProdutos = QtWidgets.QWidget()
        self.pageProdutos.setObjectName("pageProdutos")
        layProd = QtWidgets.QHBoxLayout(self.pageProdutos)
        layProd.setContentsMargins(0, 0, 0, 0)
        layProd.setSpacing(12)
        frameChart = QtWidgets.QFrame(self.pageProdutos)
        frameChart.setObjectName("frame")
        frameChart.setStyleSheet(_TABELA_STYLE)
        layFC = QtWidgets.QVBoxLayout(frameChart)
        layFC.setContentsMargins(0, 0, 0, 0)
        layFC.setSpacing(0)
        lbl = QtWidgets.QLabel("Produtos Mais Vendidos")
        lbl.setProperty("sectionTitle", "true")
        layFC.addWidget(lbl)
        self.chartProdutosWidget = QtWidgets.QWidget(frameChart)
        layFC.addWidget(self.chartProdutosWidget, 1)
        layProd.addWidget(frameChart, 2)
        frameTab = QtWidgets.QFrame(self.pageProdutos)
        frameTab.setObjectName("frame")
        frameTab.setStyleSheet(_TABELA_STYLE)
        layFT = QtWidgets.QVBoxLayout(frameTab)
        layFT.setContentsMargins(0, 0, 0, 0)
        layFT.setSpacing(0)
        lblTab = QtWidgets.QLabel("Ranking")
        lblTab.setProperty("sectionTitle", "true")
        layFT.addWidget(lblTab)
        self.tableProdutos = QtWidgets.QTableWidget(frameTab)
        self.tableProdutos.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableProdutos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableProdutos.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableProdutos.verticalHeader().setVisible(False)
        self.tableProdutos.horizontalHeader().setStretchLastSection(True)
        self.tableProdutos.setAlternatingRowColors(True)
        self.tableProdutos.setRowCount(0)
        self.tableProdutos.setColumnCount(3)
        layFT.addWidget(self.tableProdutos)
        layProd.addWidget(frameTab, 1)
        self.stackedContent.addWidget(self.pageProdutos)

        # ── Tab 2: Clientes ────────────────────────────────────────────
        self.pageClientes = QtWidgets.QWidget()
        self.pageClientes.setObjectName("pageClientes")
        layCli = QtWidgets.QVBoxLayout(self.pageClientes)
        layCli.setContentsMargins(0, 0, 0, 0)
        layCli.setSpacing(8)
        lblCli = QtWidgets.QLabel("Clientes em Destaque")
        lblCli.setProperty("sectionTitle", "true")
        lblCli.setStyleSheet(
            "QLabel { background-color: #f0f6fc; color: #1a3a5c; font-size: 13px; "
            "font-weight: bold; padding: 8px 12px; border: 1px solid #b8cde0; "
            "border-radius: 6px 6px 0 0; }"
        )
        layCli.addWidget(lblCli)
        self.scrollClientes = QtWidgets.QScrollArea(self.pageClientes)
        self.scrollClientes.setWidgetResizable(True)
        self.scrollClientes.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.containerClientes = QtWidgets.QWidget()
        self.gridClientes = QtWidgets.QGridLayout(self.containerClientes)
        self.gridClientes.setContentsMargins(8, 8, 8, 8)
        self.gridClientes.setSpacing(10)
        self.scrollClientes.setWidget(self.containerClientes)
        layCli.addWidget(self.scrollClientes, 1)
        self.stackedContent.addWidget(self.pageClientes)

        # ── Tab 3: Caixa ──────────────────────────────────────────────
        self.pageCaixa = QtWidgets.QWidget()
        self.pageCaixa.setObjectName("pageCaixa")
        layCx = QtWidgets.QHBoxLayout(self.pageCaixa)
        layCx.setContentsMargins(0, 0, 0, 0)
        layCx.setSpacing(12)
        frameCxChart = QtWidgets.QFrame(self.pageCaixa)
        frameCxChart.setObjectName("frame")
        frameCxChart.setStyleSheet(_TABELA_STYLE)
        layFCX = QtWidgets.QVBoxLayout(frameCxChart)
        layFCX.setContentsMargins(0, 0, 0, 0)
        layFCX.setSpacing(0)
        lblCx = QtWidgets.QLabel("Faturamento por Periodo")
        lblCx.setProperty("sectionTitle", "true")
        layFCX.addWidget(lblCx)
        self.chartCaixaWidget = QtWidgets.QWidget(frameCxChart)
        layFCX.addWidget(self.chartCaixaWidget, 1)
        layCx.addWidget(frameCxChart, 1)
        frameCxTab = QtWidgets.QFrame(self.pageCaixa)
        frameCxTab.setObjectName("frame")
        frameCxTab.setStyleSheet(_TABELA_STYLE)
        layFCT = QtWidgets.QVBoxLayout(frameCxTab)
        layFCT.setContentsMargins(0, 0, 0, 0)
        layFCT.setSpacing(0)
        lblCxTab = QtWidgets.QLabel("Resumo")
        lblCxTab.setProperty("sectionTitle", "true")
        layFCT.addWidget(lblCxTab)
        self.tableCaixa = QtWidgets.QTableWidget(frameCxTab)
        self.tableCaixa.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableCaixa.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableCaixa.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableCaixa.verticalHeader().setVisible(False)
        self.tableCaixa.horizontalHeader().setStretchLastSection(True)
        self.tableCaixa.setAlternatingRowColors(True)
        self.tableCaixa.setRowCount(0)
        self.tableCaixa.setColumnCount(4)
        layFCT.addWidget(self.tableCaixa)
        layCx.addWidget(frameCxTab, 1)
        self.stackedContent.addWidget(self.pageCaixa)

        self.contentLayout.addWidget(self.stackedContent, 1)
        self.mainVLayout.addLayout(self.contentLayout)

        # ── Status Bar ────────────────────────────────────────────────
        self.frameStatusBar = QtWidgets.QFrame(self.centralWidget)
        self.frameStatusBar.setStyleSheet(
            "QFrame#frameStatusBar {\n"
            " background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            " stop:0 #3585c8, stop:1 #1a5fa0);\n"
            "}\n"
            "QLabel { color: white; font-size: 11px; }\n"
            "QLabel#lblStatusSistema { color: #80ff80; font-weight: bold; }\n"
        )
        self.frameStatusBar.setObjectName("frameStatusBar")
        self.statusLayout = QtWidgets.QHBoxLayout(self.frameStatusBar)
        self.statusLayout.setContentsMargins(12, -1, 12, -1)
        self.statusLayout.setObjectName("statusLayout")
        self.lblStatusSistema = QtWidgets.QLabel(self.frameStatusBar)
        self.lblStatusSistema.setObjectName("lblStatusSistema")
        self.statusLayout.addWidget(self.lblStatusSistema)
        spacerStatus = QtWidgets.QSpacerItem(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.statusLayout.addItem(spacerStatus)
        self.lblStatusBar = QtWidgets.QLabel(self.frameStatusBar)
        self.lblStatusBar.setObjectName("lblStatusBar")
        self.statusLayout.addWidget(self.lblStatusBar)
        self.mainVLayout.addWidget(self.frameStatusBar)

        PainelRelatorios.setCentralWidget(self.centralWidget)
        self.retranslateUi(PainelRelatorios)
        QtCore.QMetaObject.connectSlotsByName(PainelRelatorios)

    # ── Helpers ───────────────────────────────────────────────────────
    def _criar_chip(self, bg, sub_color, name):
        chip = QtWidgets.QFrame()
        chip.setMinimumSize(180, 78)
        chip.setMaximumHeight(78)
        chip.setStyleSheet(
            f"QFrame#{name} {{ background-color: {bg}; border-radius: 8px; }}"
            f" QLabel {{ color: white; background: transparent; }}"
            f" QLabel[role='value'] {{ font-size: 24px; font-weight: bold; }}"
            f" QLabel[role='title'] {{ color: {sub_color}; font-size: 11px; font-weight: 600; }}"
        )
        chip.setObjectName(name)
        lay = QtWidgets.QVBoxLayout(chip)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(2)
        val = QLabel("")
        val.setProperty("role", "value")
        tit = QLabel("")
        tit.setProperty("role", "title")
        lay.addWidget(val)
        lay.addWidget(tit)
        chip._lbl_valor = val
        chip._lbl_titulo = tit
        return chip

    def retranslateUi(self, PainelRelatorios):
        _translate = QtCore.QCoreApplication.translate
        PainelRelatorios.setWindowTitle(_translate("PainelRelatorios", "CSPdv - Relatorios"))
        self.lblLogo.setText(_translate("PainelRelatorios", "CSPdv"))
        self.lblModulo.setText(_translate("PainelRelatorios", "RELATORIOS E INDICADORES"))
        self.lblOperadorInfo.setText(_translate("PainelRelatorios", "Operador: ---"))
        self.lblPeriodoAtual.setText(_translate("PainelRelatorios", "Periodo: Hoje"))
        self.btnVoltarSelecao.setText(_translate("PainelRelatorios", "Voltar"))
        self.tabTipoRelatorio.setTabText(0, _translate("PainelRelatorios", "Matriz Anual"))
        self.tabTipoRelatorio.setTabText(1, _translate("PainelRelatorios", "Produtos"))
        self.tabTipoRelatorio.setTabText(2, _translate("PainelRelatorios", "Clientes"))
        self.tabTipoRelatorio.setTabText(3, _translate("PainelRelatorios", "Caixa"))
        self.lblPeriodoDe.setText(_translate("PainelRelatorios", "De"))
        self.lblPeriodoAte.setText(_translate("PainelRelatorios", "Ate"))
        self.btnGerarRelatorio.setText(_translate("PainelRelatorios", "Atualizar"))
        self.btnExportarCsv.setText(_translate("PainelRelatorios", "Exportar CSV"))
        self.lblMatrizSecao.setText(_translate("PainelRelatorios", "Vendas Diarias por Mes"))
        self.lblStatusSistema.setText(_translate("PainelRelatorios", "Sistema online"))
        self.lblStatusBar.setText(_translate("PainelRelatorios", "CSPdv - Central de Relatorios"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PainelRelatorios = QtWidgets.QMainWindow()
    ui = Ui_PainelRelatorios()
    ui.setupUi(PainelRelatorios)
    PainelRelatorios.show()
    sys.exit(app.exec_())
