# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets

class Ui_CadastroPromocao(object):
    def setupUi(self, CadastroPromocao):
        CadastroPromocao.setObjectName("CadastroPromocao")
        CadastroPromocao.resize(1120, 900)
        CadastroPromocao.setMinimumSize(QtCore.QSize(1060, 840))
        CadastroPromocao.setStyleSheet(
            """
            QDialog {
                background-color: #eef4f8;
                color: #18324a;
                font-family: "Segoe UI";
            }
            QFrame#frameHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #153552, stop:0.55 #1d4c74, stop:1 #2f75b0);
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
            }
            QLabel#lblBadge {
                color: #ffe59d;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 14px;
                border-radius: 9px;
                background-color: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.18);
            }
            QLabel#lblFormTitle, QLabel#lblFormHint {
                color: white;
                background-color: transparent;
            }
            QLabel#lblFormTitle {
                font-size: 25px;
                font-weight: 800;
            }
            QLabel#lblFormHint {
                font-size: 12px;
            }
            QFrame#frameCard {
                background-color: white;
                border: 1px solid #d6e2ec;
                border-bottom-left-radius: 14px;
                border-bottom-right-radius: 14px;
            }
            QFrame[sectionCard="true"] {
                background-color: #f9fbfd;
                border: 1px solid #dbe7f0;
                border-radius: 14px;
            }
            QLabel[sectionTitle="true"] {
                color: #153552;
                font-size: 14px;
                font-weight: 800;
            }
            QLabel[sectionHint="true"] {
                color: #67819b;
                font-size: 11px;
            }
            QLabel[sectionLabel="true"] {
                color: #244866;
                font-size: 12px;
                font-weight: 700;
                margin-bottom: 2px;
            }
            QLineEdit, QComboBox, QDateTimeEdit, QTextEdit {
                background-color: white;
                border: 1px solid #c8d7e6;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
                color: #18324a;
            }
            QLineEdit, QComboBox, QDateTimeEdit {
                min-height: 44px;
            }
            QTextEdit {
                min-height: 120px;
            }
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QTextEdit:focus {
                border: 2px solid #3a8ad3;
                background-color: white;
            }
            QCheckBox {
                font-size: 12px;
                font-weight: 600;
                color: #244866;
                spacing: 8px;
            }
            QPushButton {
                min-height: 42px;
                border: none;
                border-radius: 10px;
                padding: 0 20px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btnSalvar {
                background-color: #2f80c9;
                color: white;
            }
            QPushButton#btnSalvar:hover {
                background-color: #276faa;
            }
            QPushButton#btnLimpar {
                background-color: white;
                color: #315676;
                border: 1px solid #c6d6e5;
            }
            QPushButton#btnVoltar {
                background-color: #d92b2b;
                color: white;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #edf3f8;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c5d6e5;
                border-radius: 6px;
                min-height: 28px;
            }
            """
        )

        self.rootLayout = QtWidgets.QVBoxLayout(CadastroPromocao)
        self.rootLayout.setContentsMargins(0, 0, 0, 0)
        self.rootLayout.setSpacing(0)
        self.rootLayout.setObjectName("rootLayout")

        self.frameHeader = QtWidgets.QFrame(CadastroPromocao)
        self.frameHeader.setObjectName("frameHeader")
        self.headerLayout = QtWidgets.QVBoxLayout(self.frameHeader)
        self.headerLayout.setContentsMargins(24, 20, 24, 22)
        self.headerLayout.setSpacing(10)
        self.headerLayout.setObjectName("headerLayout")
        self.lblBadge = QtWidgets.QLabel(self.frameHeader)
        self.lblBadge.setObjectName("lblBadge")
        self.headerLayout.addWidget(self.lblBadge, 0, QtCore.Qt.AlignLeft)
        self.lblFormTitle = QtWidgets.QLabel(self.frameHeader)
        self.lblFormTitle.setObjectName("lblFormTitle")
        self.headerLayout.addWidget(self.lblFormTitle)
        self.lblFormHint = QtWidgets.QLabel(self.frameHeader)
        self.lblFormHint.setObjectName("lblFormHint")
        self.headerLayout.addWidget(self.lblFormHint)
        self.rootLayout.addWidget(self.frameHeader)

        self.frameCard = QtWidgets.QFrame(CadastroPromocao)
        self.frameCard.setObjectName("frameCard")
        self.frameCardLayout = QtWidgets.QVBoxLayout(self.frameCard)
        self.frameCardLayout.setContentsMargins(0, 0, 0, 0)
        self.frameCardLayout.setSpacing(0)
        self.frameCardLayout.setObjectName("frameCardLayout")

        self.scrollArea = QtWidgets.QScrollArea(self.frameCard)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollContent = QtWidgets.QWidget()
        self.scrollContent.setObjectName("scrollContent")
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollContent)
        self.scrollLayout.setContentsMargins(24, 22, 24, 22)
        self.scrollLayout.setSpacing(16)
        self.scrollLayout.setObjectName("scrollLayout")

        self.frameIdentificacao = self._criar_secao_card("frameIdentificacao")
        self.scrollLayout.addWidget(self.frameIdentificacao)
        self._montar_identificacao()

        self.frameVigencia = self._criar_secao_card("frameVigencia")
        self.scrollLayout.addWidget(self.frameVigencia)
        self._montar_vigencia()

        self.frameRegra = self._criar_secao_card("frameRegra")
        self.scrollLayout.addWidget(self.frameRegra)
        self._montar_regra_financeira()

        self.frameLeveXPagueY = self._criar_secao_card("frameLeveXPagueY")
        self.scrollLayout.addWidget(self.frameLeveXPagueY)
        self._montar_leve_x_pague_y()
        self.frameLeveXPagueY.hide()

        self.frameDescontoProgressivo = self._criar_secao_card("frameDescontoProgressivo")
        self.scrollLayout.addWidget(self.frameDescontoProgressivo)
        self._montar_desconto_progressivo()
        self.frameDescontoProgressivo.hide()

        self.frameCombo = self._criar_secao_card("frameCombo")
        self.scrollLayout.addWidget(self.frameCombo)
        self._montar_combo()
        self.frameCombo.hide()

        self.frameRegraVinculacao = self._criar_secao_card("frameRegraVinculacao")
        self.scrollLayout.addWidget(self.frameRegraVinculacao)
        self._montar_regra_vinculacao()

        self.frameTextos = self._criar_secao_card("frameTextos")
        self.scrollLayout.addWidget(self.frameTextos, 1)
        self._montar_textos()

        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setSpacing(10)
        self.buttonsLayout.setObjectName("buttonsLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonsLayout.addItem(spacerItem)
        self.btnLimpar = QtWidgets.QPushButton(self.scrollContent)
        self.btnLimpar.setObjectName("btnLimpar")
        self.buttonsLayout.addWidget(self.btnLimpar)
        self.btnVoltar = QtWidgets.QPushButton(self.scrollContent)
        self.btnVoltar.setObjectName("btnVoltar")
        self.buttonsLayout.addWidget(self.btnVoltar)
        self.btnSalvar = QtWidgets.QPushButton(self.scrollContent)
        self.btnSalvar.setObjectName("btnSalvar")
        self.buttonsLayout.addWidget(self.btnSalvar)
        self.scrollLayout.addLayout(self.buttonsLayout)

        self.scrollArea.setWidget(self.scrollContent)
        self.frameCardLayout.addWidget(self.scrollArea)
        self.rootLayout.addWidget(self.frameCard)

        self.retranslateUi(CadastroPromocao)
        QtCore.QMetaObject.connectSlotsByName(CadastroPromocao)

    def _criar_secao_card(self, object_name):
        frame = QtWidgets.QFrame(self.scrollContent)
        frame.setProperty("sectionCard", "true")
        frame.setObjectName(object_name)
        return frame

    def _criar_campo_texto(self, parent, label_name, field_name, readonly=False):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        label = QtWidgets.QLabel(parent)
        label.setProperty("sectionLabel", "true")
        label.setObjectName(label_name)
        field = QtWidgets.QLineEdit(parent)
        field.setObjectName(field_name)
        if readonly:
            field.setReadOnly(True)
        setattr(self, label_name, label)
        setattr(self, field_name, field)
        layout.addWidget(label)
        layout.addWidget(field)
        return layout

    def _criar_campo_combo(self, parent, label_name, combo_name, items):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        label = QtWidgets.QLabel(parent)
        label.setProperty("sectionLabel", "true")
        label.setObjectName(label_name)
        combo = QtWidgets.QComboBox(parent)
        combo.setObjectName(combo_name)
        for _ in items:
            combo.addItem("")
        setattr(self, label_name, label)
        setattr(self, combo_name, combo)
        layout.addWidget(label)
        layout.addWidget(combo)
        return layout

    def _criar_campo_data(self, parent, label_name, field_name):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        label = QtWidgets.QLabel(parent)
        label.setProperty("sectionLabel", "true")
        label.setObjectName(label_name)
        field = QtWidgets.QDateTimeEdit(parent)
        field.setObjectName(field_name)
        field.setCalendarPopup(True)
        setattr(self, label_name, label)
        setattr(self, field_name, field)
        layout.addWidget(label)
        layout.addWidget(field)
        return layout

    def _adicionar_titulo_secao(self, layout, title_name, hint_name=None):
        title = QtWidgets.QLabel(self.scrollContent)
        title.setProperty("sectionTitle", "true")
        title.setObjectName(title_name)
        layout.addWidget(title)
        setattr(self, title_name, title)
        if hint_name:
            hint = QtWidgets.QLabel(self.scrollContent)
            hint.setProperty("sectionHint", "true")
            hint.setWordWrap(True)
            hint.setObjectName(hint_name)
            layout.addWidget(hint)
            setattr(self, hint_name, hint)

    def _montar_identificacao(self):
        layout = QtWidgets.QVBoxLayout(self.frameIdentificacao)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(16)
        self._adicionar_titulo_secao(layout, "lblIdentificacaoTitulo", "lblIdentificacaoHint")

        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(16)
        row1.addLayout(self._criar_campo_texto(self.frameIdentificacao, "lblCodigo", "lineEditCodigo", readonly=True), 3)
        row1.addLayout(self._criar_campo_texto(self.frameIdentificacao, "lblNomePromocao", "lineEditNomePromocao"), 9)
        layout.addLayout(row1)

        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(16)
        row2.addLayout(self._criar_campo_combo(self.frameIdentificacao, "lblClassificacao", "comboClassificacao", ["PROMOCAO", "CAMPANHA"]), 1)
        row2.addLayout(self._criar_campo_combo(self.frameIdentificacao, "lblTipoDesconto", "comboTipoDesconto", ["PERCENTUAL", "VALOR", "PRECO_FIXO", "LEVE_X_PAGUE_Y", "DESCONTO_PROGRESSIVO", "COMBO"]), 1)
        row2.addLayout(self._criar_campo_combo(self.frameIdentificacao, "lblStatus", "comboStatus", ["RASCUNHO", "AGENDADA", "ATIVA", "ENCERRADA", "CANCELADA"]), 1)
        layout.addLayout(row2)

    def _montar_vigencia(self):
        layout = QtWidgets.QVBoxLayout(self.frameVigencia)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(16)
        self._adicionar_titulo_secao(layout, "lblSecaoVigencia")

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(self._criar_campo_data(self.frameVigencia, "lblDataInicio", "dateTimeInicio"), 4)
        row.addLayout(self._criar_campo_data(self.frameVigencia, "lblDataFim", "dateTimeFim"), 4)
        row.addStretch(1)
        layout.addLayout(row)

    def _montar_regra_financeira(self):
        layout = QtWidgets.QVBoxLayout(self.frameRegra)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(16)
        self._adicionar_titulo_secao(layout, "lblSecaoValores")

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(self._criar_campo_texto(self.frameRegra, "lblDescontoPercentual", "lineEditDescontoPercentual"), 1)
        row.addLayout(self._criar_campo_texto(self.frameRegra, "lblDescontoValor", "lineEditDescontoValor"), 1)
        row.addLayout(self._criar_campo_texto(self.frameRegra, "lblPrecoFixo", "lineEditPrecoFixo"), 1)
        layout.addLayout(row)

    def _montar_leve_x_pague_y(self):
        layout = QtWidgets.QVBoxLayout(self.frameLeveXPagueY)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(16)
        self._adicionar_titulo_secao(layout, "lblSecaoLeveXPagueY", "lblSecaoLeveXPagueYHint")

        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(16)
        row1.addLayout(self._criar_campo_texto(self.frameLeveXPagueY, "lblLeveX", "lineEditLeveX"), 1)
        row1.addLayout(self._criar_campo_texto(self.frameLeveXPagueY, "lblPagueY", "lineEditPagueY"), 1)
        layout.addLayout(row1)

        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(16)
        row2.addLayout(self._criar_campo_combo(self.frameLeveXPagueY, "lblAplicacaoDesconto", "comboAplicacaoDesconto", ["MAIS_BARATO", "PROPORCIONAL"]), 1)
        layout.addLayout(row2)

    def _montar_desconto_progressivo(self):
        layout = QtWidgets.QVBoxLayout(self.frameDescontoProgressivo)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(16)
        self._adicionar_titulo_secao(layout, "lblSecaoProgressivo", "lblSecaoProgressivoHint")

        self.tableFaixas = QtWidgets.QTableWidget(self.frameDescontoProgressivo)
        self.tableFaixas.setObjectName("tableFaixas")
        self.tableFaixas.setColumnCount(2)
        self.tableFaixas.setHorizontalHeaderLabels(["Quantidade Minima", "Desconto (%)"])
        self.tableFaixas.horizontalHeader().setStretchLastSection(True)
        self.tableFaixas.setMinimumHeight(150)
        layout.addWidget(self.tableFaixas)

        btnRow = QtWidgets.QHBoxLayout()
        self.btnAdicionarFaixa = QtWidgets.QPushButton(self.frameDescontoProgressivo)
        self.btnAdicionarFaixa.setObjectName("btnAdicionarFaixa")
        self.btnAdicionarFaixa.setText("+ Adicionar Faixa")
        btnRow.addWidget(self.btnAdicionarFaixa)
        self.btnRemoverFaixa = QtWidgets.QPushButton(self.frameDescontoProgressivo)
        self.btnRemoverFaixa.setObjectName("btnRemoverFaixa")
        self.btnRemoverFaixa.setText("- Remover Faixa")
        btnRow.addWidget(self.btnRemoverFaixa)
        btnRow.addStretch(1)
        layout.addLayout(btnRow)

    def _montar_combo(self):
        layout = QtWidgets.QVBoxLayout(self.frameCombo)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(16)
        self._adicionar_titulo_secao(layout, "lblSecaoCombo", "lblSecaoComboHint")

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(self._criar_campo_texto(self.frameCombo, "lblComboQtd", "lineEditComboQtd"), 1)
        row.addLayout(self._criar_campo_texto(self.frameCombo, "lblComboPreco", "lineEditComboPreco"), 1)
        layout.addLayout(row)

    def _montar_regra_vinculacao(self):
        layout = QtWidgets.QVBoxLayout(self.frameRegraVinculacao)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(16)
        self._adicionar_titulo_secao(layout, "lblSecaoRegraVinculacao", "lblSecaoRegraVinculacaoHint")

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(self._criar_campo_combo(self.frameRegraVinculacao, "lblTipoRegra", "comboTipoRegra", ["ITEM", "MARCA", "CATEGORIA", "FORNECEDOR", "FAIXA_PRECO", "LISTA_ITENS"]), 1)
        row.addLayout(self._criar_campo_texto(self.frameRegraVinculacao, "lblValorRegra", "lineEditValorRegra"), 1)
        layout.addLayout(row)

        self.frameFaixaPreco = QtWidgets.QFrame(self.frameRegraVinculacao)
        self.frameFaixaPreco.setObjectName("frameFaixaPreco")
        faixaLayout = QtWidgets.QHBoxLayout(self.frameFaixaPreco)
        faixaLayout.setContentsMargins(0, 0, 0, 0)
        faixaLayout.setSpacing(16)
        self.lineEditFaixaPrecoMin = QtWidgets.QLineEdit(self.frameFaixaPreco)
        self.lineEditFaixaPrecoMin.setObjectName("lineEditFaixaPrecoMin")
        self.lineEditFaixaPrecoMin.setPlaceholderText("Min (R$)")
        faixaLayout.addWidget(self.lineEditFaixaPrecoMin)
        self.lineEditFaixaPrecoMax = QtWidgets.QLineEdit(self.frameFaixaPreco)
        self.lineEditFaixaPrecoMax.setObjectName("lineEditFaixaPrecoMax")
        self.lineEditFaixaPrecoMax.setPlaceholderText("Max (R$)")
        faixaLayout.addWidget(self.lineEditFaixaPrecoMax)
        layout.addWidget(self.frameFaixaPreco)
        self.frameFaixaPreco.hide()

        btnAplicarLayout = QtWidgets.QHBoxLayout()
        self.btnAplicarRegra = QtWidgets.QPushButton(self.frameRegraVinculacao)
        self.btnAplicarRegra.setObjectName("btnAplicarRegra")
        self.btnAplicarRegra.setText("Aplicar Regra e Vincular Produtos")
        btnAplicarLayout.addWidget(self.btnAplicarRegra)
        btnAplicarLayout.addStretch(1)
        layout.addLayout(btnAplicarLayout)

        self.lblResultadoRegra = QtWidgets.QLabel(self.frameRegraVinculacao)
        self.lblResultadoRegra.setObjectName("lblResultadoRegra")
        self.lblResultadoRegra.setWordWrap(True)
        self.lblResultadoRegra.setStyleSheet("color: #2e7d32; font-size: 12px; font-weight: 600;")
        layout.addWidget(self.lblResultadoRegra)

    def _montar_textos(self):
        layout = QtWidgets.QVBoxLayout(self.frameTextos)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(14)

        self.lblDescricao = QtWidgets.QLabel(self.frameTextos)
        self.lblDescricao.setProperty("sectionLabel", "true")
        self.lblDescricao.setObjectName("lblDescricao")
        layout.addWidget(self.lblDescricao)
        self.textEditDescricao = QtWidgets.QTextEdit(self.frameTextos)
        self.textEditDescricao.setObjectName("textEditDescricao")
        layout.addWidget(self.textEditDescricao)

        self.lblObservacao = QtWidgets.QLabel(self.frameTextos)
        self.lblObservacao.setProperty("sectionLabel", "true")
        self.lblObservacao.setObjectName("lblObservacao")
        layout.addWidget(self.lblObservacao)
        self.textEditObservacao = QtWidgets.QTextEdit(self.frameTextos)
        self.textEditObservacao.setObjectName("textEditObservacao")
        layout.addWidget(self.textEditObservacao)

    def retranslateUi(self, CadastroPromocao):
        _translate = QtCore.QCoreApplication.translate
        CadastroPromocao.setWindowTitle(_translate("CadastroPromocao", "CSPdv - Cadastro de Promocao"))
        self.lblBadge.setText(_translate("CadastroPromocao", "CADASTRO DE PROMOCAO"))
        self.lblFormTitle.setText(_translate("CadastroPromocao", "Nova Promocao"))
        self.lblFormHint.setText(_translate("CadastroPromocao", "Cadastre a base da promocao ou campanha antes de vincular produtos e regras avancadas."))
        self.lblIdentificacaoTitulo.setText(_translate("CadastroPromocao", "Identificação da Promoção"))
        self.lblIdentificacaoHint.setText(_translate("CadastroPromocao", "Defina código, nome, tipo de desconto e status operacional com uma estrutura estável para futuras campanhas."))
        self.lblCodigo.setText(_translate("CadastroPromocao", "Codigo"))
        self.lineEditCodigo.setText(_translate("CadastroPromocao", "Auto-gerado"))
        self.lblNomePromocao.setText(_translate("CadastroPromocao", "Nome da Promocao *"))
        self.lblClassificacao.setText(_translate("CadastroPromocao", "Classificacao *"))
        self.comboClassificacao.setItemText(0, _translate("CadastroPromocao", "PROMOCAO"))
        self.comboClassificacao.setItemText(1, _translate("CadastroPromocao", "CAMPANHA"))
        self.lblTipoDesconto.setText(_translate("CadastroPromocao", "Tipo de Desconto *"))
        self.comboTipoDesconto.setItemText(0, _translate("CadastroPromocao", "PERCENTUAL"))
        self.comboTipoDesconto.setItemText(1, _translate("CadastroPromocao", "VALOR"))
        self.comboTipoDesconto.setItemText(2, _translate("CadastroPromocao", "PRECO_FIXO"))
        self.comboTipoDesconto.setItemText(3, _translate("CadastroPromocao", "LEVE_X_PAGUE_Y"))
        self.comboTipoDesconto.setItemText(4, _translate("CadastroPromocao", "DESCONTO_PROGRESSIVO"))
        self.comboTipoDesconto.setItemText(5, _translate("CadastroPromocao", "COMBO"))
        self.lblStatus.setText(_translate("CadastroPromocao", "Status *"))
        self.comboStatus.setItemText(0, _translate("CadastroPromocao", "RASCUNHO"))
        self.comboStatus.setItemText(1, _translate("CadastroPromocao", "AGENDADA"))
        self.comboStatus.setItemText(2, _translate("CadastroPromocao", "ATIVA"))
        self.comboStatus.setItemText(3, _translate("CadastroPromocao", "ENCERRADA"))
        self.comboStatus.setItemText(4, _translate("CadastroPromocao", "CANCELADA"))
        self.lblSecaoVigencia.setText(_translate("CadastroPromocao", "Vigencia"))
        self.lblDataInicio.setText(_translate("CadastroPromocao", "Inicio *"))
        self.lblDataFim.setText(_translate("CadastroPromocao", "Fim *"))
        self.lblSecaoValores.setText(_translate("CadastroPromocao", "Regra Financeira"))
        self.lblDescontoPercentual.setText(_translate("CadastroPromocao", "Desconto Percentual (%)"))
        self.lblDescontoValor.setText(_translate("CadastroPromocao", "Desconto em Valor (R$)"))
        self.lblPrecoFixo.setText(_translate("CadastroPromocao", "Preco Fixo Promocional (R$)"))
        self.lblSecaoLeveXPagueY.setText(_translate("CadastroPromocao", "Regra Leve X Pague Y"))
        self.lblSecaoLeveXPagueYHint.setText(_translate("CadastroPromocao", "Configure a quantidade minima para o desconto e a forma de aplicacao."))
        self.lblLeveX.setText(_translate("CadastroPromocao", "Leve (unidades) *"))
        self.lblPagueY.setText(_translate("CadastroPromocao", "Pague (unidades) *"))
        self.lblAplicacaoDesconto.setText(_translate("CadastroPromocao", "Aplicar desconto em *"))
        self.comboAplicacaoDesconto.setItemText(0, _translate("CadastroPromocao", "MAIS_BARATO"))
        self.comboAplicacaoDesconto.setItemText(1, _translate("CadastroPromocao", "PROPORCIONAL"))
        self.lblSecaoProgressivo.setText(_translate("CadastroPromocao", "Regra de Desconto Progressivo"))
        self.lblSecaoProgressivoHint.setText(_translate("CadastroPromocao", "Quanto mais unidades, maior o desconto. Adicione faixas com quantidade minima e percentual."))
        self.lblSecaoCombo.setText(_translate("CadastroPromocao", "Regra de Combo"))
        self.lblSecaoComboHint.setText(_translate("CadastroPromocao", "Compre X unidades por um preco fixo. Configure a quantidade e o preco do combo."))
        self.lblComboQtd.setText(_translate("CadastroPromocao", "Quantidade do Combo *"))
        self.lblComboPreco.setText(_translate("CadastroPromocao", "Preco do Combo (R$) *"))
        self.lblSecaoRegraVinculacao.setText(_translate("CadastroPromocao", "Regra de Vinculacao de Produtos"))
        self.lblSecaoRegraVinculacaoHint.setText(_translate("CadastroPromocao", "Configure o tipo de regra para vincular automaticamente os produtos que atendem aos criterios."))
        self.lblTipoRegra.setText(_translate("CadastroPromocao", "Tipo da Regra *"))
        self.comboTipoRegra.setItemText(0, _translate("CadastroPromocao", "ITEM"))
        self.comboTipoRegra.setItemText(1, _translate("CadastroPromocao", "MARCA"))
        self.comboTipoRegra.setItemText(2, _translate("CadastroPromocao", "CATEGORIA"))
        self.comboTipoRegra.setItemText(3, _translate("CadastroPromocao", "FORNECEDOR"))
        self.comboTipoRegra.setItemText(4, _translate("CadastroPromocao", "FAIXA_PRECO"))
        self.comboTipoRegra.setItemText(5, _translate("CadastroPromocao", "LISTA_ITENS"))
        self.lblValorRegra.setText(_translate("CadastroPromocao", "Valor da Regra (ID ou Nome) *"))
        self.lblDescricao.setText(_translate("CadastroPromocao", "Descricao"))
        self.lblObservacao.setText(_translate("CadastroPromocao", "Observacao"))
        self.btnLimpar.setText(_translate("CadastroPromocao", "Limpar"))
        self.btnVoltar.setText(_translate("CadastroPromocao", "Voltar"))
        self.btnSalvar.setText(_translate("CadastroPromocao", "Salvar"))
