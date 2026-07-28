# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_CadastroPromocao(object):
    def setupUi(self, CadastroPromocao):
        CadastroPromocao.setObjectName("CadastroPromocao")
        CadastroPromocao.resize(980, 820)
        CadastroPromocao.setMinimumSize(QtCore.QSize(920, 760))
        CadastroPromocao.setStyleSheet(
            """
            QDialog {
                background-color: #eef4f8;
                color: #18324a;
                font-family: "Segoe UI";
            }
            QFrame#frameHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #153552, stop:0.55 #1d4c74, stop:1 #2f75b0);
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
            }
            QLabel#lblBadge {
                color: #ffe59d;
                font-size: 11px;
                font-weight: 700;
                padding: 6px 12px;
                border-radius: 8px;
                background-color: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.18);
            }
            QLabel#lblFormTitle { color: white; background: transparent; font-size: 22px; font-weight: 800; }
            QLabel#lblFormHint  { color: #c5ddf0; background: transparent; font-size: 11px; }
            QFrame#frameCard {
                background-color: white;
                border: 1px solid #d6e2ec;
                border-bottom-left-radius: 14px;
                border-bottom-right-radius: 14px;
            }
            QFrame[sectionCard="true"] {
                background-color: #f9fbfd;
                border: 1px solid #dbe7f0;
                border-radius: 12px;
            }
            QLabel[sectionTitle="true"] { color: #153552; font-size: 13px; font-weight: 800; }
            QLabel[sectionHint="true"]  { color: #67819b; font-size: 11px; }
            QLabel[sectionLabel="true"] { color: #244866; font-size: 12px; font-weight: 700; }
            QLineEdit, QComboBox, QDateTimeEdit {
                background-color: white;
                border: 1px solid #c8d7e6;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
                color: #18324a;
                min-height: 40px;
            }
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus {
                border: 2px solid #3a8ad3;
                background-color: white;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #c8d7e6;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
                color: #18324a;
                min-height: 80px;
            }
            QTextEdit:focus { border: 2px solid #3a8ad3; }
            QPushButton {
                min-height: 38px;
                border: none;
                border-radius: 10px;
                padding: 0 18px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btnSalvar   { background-color: #2f80c9; color: white; }
            QPushButton#btnSalvar:hover { background-color: #276faa; }
            QPushButton#btnLimpar   { background-color: white; color: #315676; border: 1px solid #c6d6e5; }
            QPushButton#btnVoltar   { background-color: #d92b2b; color: white; }
            QPushButton#btnAplicarRegra {
                background-color: #e9f3fb; color: #205d8f;
                border: 1px solid #b8d3ea; font-size: 11px; min-height: 34px;
            }
            QPushButton#btnAplicarRegra:hover { background-color: #d8ebfa; }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: #edf3f8; width: 10px; border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c5d6e5; border-radius: 5px; min-height: 24px;
            }

            /* ---- Tipo cards ---- */
            QFrame#tipoCard {
                background-color: #f4f7fa;
                border: 2px solid #d6e2ec;
                border-radius: 12px;
                padding: 0;
            }
            QFrame#tipoCard:hover {
                border-color: #3a8ad3;
                background-color: #eaf3fc;
            }
            QFrame#tipoCard[selecionado="true"] {
                border-color: #2f80c9;
                background-color: #dceeff;
            }
            QLabel[tipoIcon="true"] {
                font-size: 22px;
                background: transparent;
            }
            QLabel[tipoLabel="true"] {
                font-size: 11px;
                font-weight: 700;
                color: #315676;
                background: transparent;
            }
            QFrame#tipoCard[selecionado="true"] QLabel[tipoLabel="true"] {
                color: #153552;
            }
            """
        )

        self.rootLayout = QtWidgets.QVBoxLayout(CadastroPromocao)
        self.rootLayout.setContentsMargins(0, 0, 0, 0)
        self.rootLayout.setSpacing(0)

        # ---------- Header ----------
        self.frameHeader = QtWidgets.QFrame(CadastroPromocao)
        self.frameHeader.setObjectName("frameHeader")
        self.headerLayout = QtWidgets.QVBoxLayout(self.frameHeader)
        self.headerLayout.setContentsMargins(24, 18, 24, 18)
        self.headerLayout.setSpacing(6)
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

        # ---------- Card principal ----------
        self.frameCard = QtWidgets.QFrame(CadastroPromocao)
        self.frameCard.setObjectName("frameCard")
        self.frameCardLayout = QtWidgets.QVBoxLayout(self.frameCard)
        self.frameCardLayout.setContentsMargins(0, 0, 0, 0)
        self.frameCardLayout.setSpacing(0)

        self.scrollArea = QtWidgets.QScrollArea(self.frameCard)
        self.scrollArea.setWidgetResizable(True)
        self.scrollContent = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollContent)
        self.scrollLayout.setContentsMargins(22, 18, 22, 18)
        self.scrollLayout.setSpacing(12)

        # ---- 1. Dados basicos ----
        self.frameDados = self._criar_secao_card("frameDados")
        self.scrollLayout.addWidget(self.frameDados)
        self._montar_dados_basicos()

        # ---- 2. Tipo de desconto (cards) ----
        self.frameTipo = self._criar_secao_card("frameTipo")
        self.scrollLayout.addWidget(self.frameTipo)
        self._montar_tipo_desconto()

        # ---- 3. Configuracao do desconto (dinamico) ----
        self.frameConfig = self._criar_secao_card("frameConfig")
        self.scrollLayout.addWidget(self.frameConfig)
        self._montar_config_desconto()

        # ---- 4. Vigencia ----
        self.frameVigencia = self._criar_secao_card("frameVigencia")
        self.scrollLayout.addWidget(self.frameVigencia)
        self._montar_vigencia()

        # ---- 5. Vinculacao de Produtos (colapsavel) ----
        self.frameVinculacao = self._criar_secao_card("frameVinculacao")
        self.scrollLayout.addWidget(self.frameVinculacao)
        self._montar_vinculacao()

        # ---- 6. Descricao / Observacao (colapsavel) ----
        self.frameTextos = self._criar_secao_card("frameTextos")
        self.scrollLayout.addWidget(self.frameTextos)
        self._montar_textos()

        # ---- Botoes ----
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setSpacing(10)
        self.buttonsLayout.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        )
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

    # ------------------------------------------------------------------ helpers
    def _criar_secao_card(self, object_name):
        frame = QtWidgets.QFrame(self.scrollContent)
        frame.setProperty("sectionCard", "true")
        frame.setObjectName(object_name)
        return frame

    def _criar_campo(self, parent, label_text, field_name, readonly=False, placeholder=""):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(4)
        lbl = QtWidgets.QLabel(parent)
        lbl.setProperty("sectionLabel", "true")
        lbl.setText(label_text)
        field = QtWidgets.QLineEdit(parent)
        field.setObjectName(field_name)
        if readonly:
            field.setReadOnly(True)
        if placeholder:
            field.setPlaceholderText(placeholder)
        setattr(self, field_name, field)
        layout.addWidget(lbl)
        layout.addWidget(field)
        return layout

    def _criar_combo(self, parent, label_text, combo_name, items):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(4)
        lbl = QtWidgets.QLabel(parent)
        lbl.setProperty("sectionLabel", "true")
        lbl.setText(label_text)
        combo = QtWidgets.QComboBox(parent)
        combo.setObjectName(combo_name)
        combo.addItems(items)
        setattr(self, combo_name, combo)
        layout.addWidget(lbl)
        layout.addWidget(combo)
        return layout

    def _criar_data(self, parent, label_text, field_name):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(4)
        lbl = QtWidgets.QLabel(parent)
        lbl.setProperty("sectionLabel", "true")
        lbl.setText(label_text)
        field = QtWidgets.QDateTimeEdit(parent)
        field.setObjectName(field_name)
        field.setCalendarPopup(True)
        setattr(self, field_name, field)
        layout.addWidget(lbl)
        layout.addWidget(field)
        return layout

    # --------------------------------------------------------- 1. Dados basicos
    def _montar_dados_basicos(self):
        lay = QtWidgets.QVBoxLayout(self.frameDados)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        lbl = QtWidgets.QLabel(self.frameDados)
        lbl.setProperty("sectionTitle", "true")
        lbl.setText("Dados da Promocao")
        lay.addWidget(lbl)

        r1 = QtWidgets.QHBoxLayout()
        r1.setSpacing(12)
        r1.addLayout(self._criar_campo(self.frameDados, "Codigo", "lineEditCodigo", readonly=True), 2)
        r1.addLayout(self._criar_campo(self.frameDados, "Nome da Promocao *", "lineEditNomePromocao"), 8)
        lay.addLayout(r1)

        r2 = QtWidgets.QHBoxLayout()
        r2.setSpacing(12)
        r2.addLayout(self._criar_combo(self.frameDados, "Classificacao", "comboClassificacao", ["PROMOCAO", "CAMPANHA"]), 1)
        r2.addLayout(self._criar_combo(self.frameDados, "Status", "comboStatus", ["RASCUNHO", "AGENDADA", "ATIVA", "ENCERRADA", "CANCELADA"]), 1)
        r2.addStretch(1)
        lay.addLayout(r2)

    # --------------------------------------------------------- 2. Tipo cards
    def _montar_tipo_desconto(self):
        lay = QtWidgets.QVBoxLayout(self.frameTipo)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        lbl = QtWidgets.QLabel(self.frameTipo)
        lbl.setProperty("sectionTitle", "true")
        lbl.setText("Tipo de Desconto")
        lay.addWidget(lbl)

        hint = QtWidgets.QLabel(self.frameTipo)
        hint.setProperty("sectionHint", "true")
        hint.setText("Selecione o tipo de desconto desejado.")
        lay.addWidget(hint)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)

        tipos = [
            ("PERCENTUAL", "%", "Percentual"),
            ("VALOR", "R$", "Desconto em R$"),
            ("PRECO_FIXO", "$!", "Preco Fixo"),
            ("LEVE_X_PAGUE_Y", "2x1", "Leve X Pague Y"),
            ("DESCONTO_PROGRESSIVO", "++", "Progressivo"),
            ("COMBO", "C", "Combo"),
        ]

        self._tipo_cards: dict[str, QtWidgets.QFrame] = {}
        for i, (tipo_id, icon, label) in enumerate(tipos):
            card = QtWidgets.QFrame(self.frameTipo)
            card.setObjectName("tipoCard")
            card.setCursor(QtCore.Qt.PointingHandCursor)
            card.setProperty("tipo_id", tipo_id)
            card.setProperty("selecionado", False)
            card.setFixedHeight(72)

            card_lay = QtWidgets.QVBoxLayout(card)
            card_lay.setContentsMargins(8, 8, 8, 8)
            card_lay.setSpacing(2)

            icon_lbl = QtWidgets.QLabel(card)
            icon_lbl.setProperty("tipoIcon", "true")
            icon_lbl.setText(icon)
            icon_lbl.setAlignment(QtCore.Qt.AlignCenter)
            card_lay.addWidget(icon_lbl)

            txt_lbl = QtWidgets.QLabel(card)
            txt_lbl.setProperty("tipoLabel", "true")
            txt_lbl.setText(label)
            txt_lbl.setAlignment(QtCore.Qt.AlignCenter)
            card_lay.addWidget(txt_lbl)

            card.mousePressEvent = lambda e, t=tipo_id: self._selecionar_tipo(t)
            self._tipo_cards[tipo_id] = card
            grid.addWidget(card, i // 3, i % 3)

        lay.addLayout(grid)

        self._tipo_selecionado_label = QtWidgets.QLabel(self.frameTipo)
        self._tipo_selecionado_label.setStyleSheet(
            "color: #2f80c9; font-size: 12px; font-weight: 700; padding-top: 4px;"
        )
        lay.addWidget(self._tipo_selecionado_label)

        self.comboTipoDesconto = QtWidgets.QComboBox()
        self.comboTipoDesconto.addItems([t[0] for t in tipos])
        self.comboTipoDesconto.hide()

    # --------------------------------------------------------- 3. Config dinamico
    def _montar_config_desconto(self):
        lay = QtWidgets.QVBoxLayout(self.frameConfig)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        self._configTitle = QtWidgets.QLabel(self.frameConfig)
        self._configTitle.setProperty("sectionTitle", "true")
        lay.addWidget(self._configTitle)

        self._configHint = QtWidgets.QLabel(self.frameConfig)
        self._configHint.setProperty("sectionHint", "true")
        self._configHint.setWordWrap(True)
        lay.addWidget(self._configHint)

        # --- PERCENTUAL ---
        self.framePercentual = QtWidgets.QFrame(self.frameConfig)
        fl = QtWidgets.QHBoxLayout(self.framePercentual)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(12)
        fl.addLayout(self._criar_campo(self.framePercentual, "Desconto (%)", "lineEditDescontoPercentual", placeholder="Ex: 15"))
        fl.addStretch(1)
        lay.addWidget(self.framePercentual)

        # --- VALOR ---
        self.frameValor = QtWidgets.QFrame(self.frameConfig)
        fl = QtWidgets.QHBoxLayout(self.frameValor)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(12)
        fl.addLayout(self._criar_campo(self.frameValor, "Desconto (R$)", "lineEditDescontoValor", placeholder="Ex: 5,00"))
        fl.addStretch(1)
        lay.addWidget(self.frameValor)

        # --- PRECO FIXO ---
        self.framePrecoFixo = QtWidgets.QFrame(self.frameConfig)
        fl = QtWidgets.QHBoxLayout(self.framePrecoFixo)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(12)
        fl.addLayout(self._criar_campo(self.framePrecoFixo, "Preco Promocional (R$)", "lineEditPrecoFixo", placeholder="Ex: 9,99"))
        fl.addStretch(1)
        lay.addWidget(self.framePrecoFixo)

        # --- LEVE X PAGUE Y ---
        self.frameLeveXPagueY = QtWidgets.QFrame(self.frameConfig)
        fl = QtWidgets.QHBoxLayout(self.frameLeveXPagueY)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(12)
        fl.addLayout(self._criar_campo(self.frameLeveXPagueY, "Leve (un)", "lineEditLeveX", placeholder="3"))
        fl.addLayout(self._criar_campo(self.frameLeveXPagueY, "Pague (un)", "lineEditPagueY", placeholder="2"))
        fl.addLayout(self._criar_combo(self.frameLeveXPagueY, "Desconto em", "comboAplicacaoDesconto", ["MAIS_BARATO", "PROPORCIONAL"]))
        fl.addStretch(1)
        lay.addWidget(self.frameLeveXPagueY)

        # --- PROGRESSIVO ---
        self.frameProgressivo = QtWidgets.QFrame(self.frameConfig)
        fl = QtWidgets.QVBoxLayout(self.frameProgressivo)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(6)
        self.tableFaixas = QtWidgets.QTableWidget(self.frameProgressivo)
        self.tableFaixas.setObjectName("tableFaixas")
        self.tableFaixas.setColumnCount(2)
        self.tableFaixas.setHorizontalHeaderLabels(["Qtd Minima", "Desconto (%)"])
        self.tableFaixas.horizontalHeader().setStretchLastSection(True)
        self.tableFaixas.setMaximumHeight(160)
        fl.addWidget(self.tableFaixas)
        br = QtWidgets.QHBoxLayout()
        self.btnAdicionarFaixa = QtWidgets.QPushButton(self.frameProgressivo)
        self.btnAdicionarFaixa.setObjectName("btnAdicionarFaixa")
        self.btnAdicionarFaixa.setText("+ Adicionar")
        self.btnAdicionarFaixa.setFixedHeight(30)
        br.addWidget(self.btnAdicionarFaixa)
        self.btnRemoverFaixa = QtWidgets.QPushButton(self.frameProgressivo)
        self.btnRemoverFaixa.setObjectName("btnRemoverFaixa")
        self.btnRemoverFaixa.setText("- Remover")
        self.btnRemoverFaixa.setFixedHeight(30)
        br.addWidget(self.btnRemoverFaixa)
        br.addStretch(1)
        fl.addLayout(br)
        lay.addWidget(self.frameProgressivo)

        # --- COMBO ---
        self.frameCombo = QtWidgets.QFrame(self.frameConfig)
        fl = QtWidgets.QHBoxLayout(self.frameCombo)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(12)
        fl.addLayout(self._criar_campo(self.frameCombo, "Quantidade", "lineEditComboQtd", placeholder="3"))
        fl.addLayout(self._criar_campo(self.frameCombo, "Preco do Combo (R$)", "lineEditComboPreco", placeholder="Ex: 24,90"))
        fl.addStretch(1)
        lay.addWidget(self.frameCombo)

        # frame placeholder vazio quando nada selecionado
        self.frameConfigVazio = QtWidgets.QLabel(self.frameConfig)
        self.frameConfigVazio.setText("Selecione um tipo de desconto acima.")
        self.frameConfigVazio.setAlignment(QtCore.Qt.AlignCenter)
        self.frameConfigVazio.setStyleSheet("color: #8aa0b4; font-size: 12px; padding: 16px;")
        lay.addWidget(self.frameConfigVazio)

        self._config_frames: dict[str, QtWidgets.QFrame] = {
            "PERCENTUAL": self.framePercentual,
            "VALOR": self.frameValor,
            "PRECO_FIXO": self.framePrecoFixo,
            "LEVE_X_PAGUE_Y": self.frameLeveXPagueY,
            "DESCONTO_PROGRESSIVO": self.frameProgressivo,
            "COMBO": self.frameCombo,
        }

    # --------------------------------------------------------- 4. Vigencia
    def _montar_vigencia(self):
        lay = QtWidgets.QVBoxLayout(self.frameVigencia)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        lbl = QtWidgets.QLabel(self.frameVigencia)
        lbl.setProperty("sectionTitle", "true")
        lbl.setText("Vigencia")
        lay.addWidget(lbl)

        r = QtWidgets.QHBoxLayout()
        r.setSpacing(12)
        r.addLayout(self._criar_data(self.frameVigencia, "Inicio *", "dateTimeInicio"), 4)
        r.addLayout(self._criar_data(self.frameVigencia, "Fim *", "dateTimeFim"), 4)
        r.addStretch(1)
        lay.addLayout(r)

    # --------------------------------------------------------- 5. Vinculacao
    def _montar_vinculacao(self):
        lay = QtWidgets.QVBoxLayout(self.frameVinculacao)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        hdr = QtWidgets.QHBoxLayout()
        self._lblVincTitle = QtWidgets.QLabel(self.frameVinculacao)
        self._lblVincTitle.setProperty("sectionTitle", "true")
        self._lblVincTitle.setText("Vinculacao Automatica de Produtos")
        hdr.addWidget(self._lblVincTitle)
        self._btnToggleVinc = QtWidgets.QPushButton(self.frameVinculacao)
        self._btnToggleVinc.setText("expandir  v")
        self._btnToggleVinc.setFlat(True)
        self._btnToggleVinc.setStyleSheet("color: #3a8ad3; font-size: 11px; font-weight: 600; min-height: 20px;")
        self._btnToggleVinc.setCheckable(True)
        self._btnToggleVinc.toggled.connect(self._toggle_vinculacao)
        hdr.addWidget(self._btnToggleVinc, 0, QtCore.Qt.AlignRight)
        lay.addLayout(hdr)

        self._vincBody = QtWidgets.QFrame(self.frameVinculacao)
        self._vincBody.hide()
        vbl = QtWidgets.QVBoxLayout(self._vincBody)
        vbl.setContentsMargins(0, 4, 0, 0)
        vbl.setSpacing(8)

        hint = QtWidgets.QLabel(self._vincBody)
        hint.setProperty("sectionHint", "true")
        hint.setText("Vincule produtos por Marca, Categoria, Fornecedor ou faixa de preco.")
        hint.setWordWrap(True)
        vbl.addWidget(hint)

        r = QtWidgets.QHBoxLayout()
        r.setSpacing(12)
        r.addLayout(self._criar_combo(self._vincBody, "Regra", "comboTipoRegra", ["ITEM", "MARCA", "CATEGORIA", "FORNECEDOR", "FAIXA_PRECO", "LISTA_ITENS"]), 1)
        r.addLayout(self._criar_campo(self._vincBody, "Valor", "lineEditValorRegra"), 2)
        vbl.addLayout(r)

        self.frameFaixaPreco = QtWidgets.QFrame(self._vincBody)
        fp = QtWidgets.QHBoxLayout(self.frameFaixaPreco)
        fp.setContentsMargins(0, 0, 0, 0)
        fp.setSpacing(12)
        self.lineEditFaixaPrecoMin = QtWidgets.QLineEdit(self.frameFaixaPreco)
        self.lineEditFaixaPrecoMin.setPlaceholderText("Min (R$)")
        fp.addWidget(self.lineEditFaixaPrecoMin)
        self.lineEditFaixaPrecoMax = QtWidgets.QLineEdit(self.frameFaixaPreco)
        self.lineEditFaixaPrecoMax.setPlaceholderText("Max (R$)")
        fp.addWidget(self.lineEditFaixaPrecoMax)
        vbl.addWidget(self.frameFaixaPreco)
        self.frameFaixaPreco.hide()

        br = QtWidgets.QHBoxLayout()
        self.btnAplicarRegra = QtWidgets.QPushButton(self._vincBody)
        self.btnAplicarRegra.setObjectName("btnAplicarRegra")
        self.btnAplicarRegra.setText("Aplicar Regra e Vincular Produtos")
        br.addWidget(self.btnAplicarRegra)
        br.addStretch(1)
        vbl.addLayout(br)

        self.lblResultadoRegra = QtWidgets.QLabel(self._vincBody)
        self.lblResultadoRegra.setWordWrap(True)
        self.lblResultadoRegra.setStyleSheet("color: #2e7d32; font-size: 12px; font-weight: 600;")
        vbl.addWidget(self.lblResultadoRegra)

        lay.addWidget(self._vincBody)

    # --------------------------------------------------------- 6. Textos
    def _montar_textos(self):
        lay = QtWidgets.QVBoxLayout(self.frameTextos)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        hdr = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(self.frameTextos)
        lbl.setProperty("sectionTitle", "true")
        lbl.setText("Descricao e Observacao")
        hdr.addWidget(lbl)
        self._btnToggleTxt = QtWidgets.QPushButton(self.frameTextos)
        self._btnToggleTxt.setText("expandir  v")
        self._btnToggleTxt.setFlat(True)
        self._btnToggleTxt.setStyleSheet("color: #3a8ad3; font-size: 11px; font-weight: 600; min-height: 20px;")
        self._btnToggleTxt.setCheckable(True)
        self._btnToggleTxt.toggled.connect(self._toggle_textos)
        hdr.addWidget(self._btnToggleTxt, 0, QtCore.Qt.AlignRight)
        lay.addLayout(hdr)

        self._txtBody = QtWidgets.QFrame(self.frameTextos)
        self._txtBody.hide()
        tbl = QtWidgets.QVBoxLayout(self._txtBody)
        tbl.setContentsMargins(0, 4, 0, 0)
        tbl.setSpacing(8)

        self.lblDescricao = QtWidgets.QLabel(self._txtBody)
        self.lblDescricao.setProperty("sectionLabel", "true")
        self.lblDescricao.setText("Descricao")
        tbl.addWidget(self.lblDescricao)
        self.textEditDescricao = QtWidgets.QTextEdit(self._txtBody)
        self.textEditDescricao.setObjectName("textEditDescricao")
        self.textEditDescricao.setPlaceholderText("Descricao da promocao (opcional)")
        tbl.addWidget(self.textEditDescricao)

        self.lblObservacao = QtWidgets.QLabel(self._txtBody)
        self.lblObservacao.setProperty("sectionLabel", "true")
        self.lblObservacao.setText("Observacao")
        tbl.addWidget(self.lblObservacao)
        self.textEditObservacao = QtWidgets.QTextEdit(self._txtBody)
        self.textEditObservacao.setObjectName("textEditObservacao")
        self.textEditObservacao.setPlaceholderText("Observacao interna (opcional)")
        tbl.addWidget(self.textEditObservacao)

        lay.addWidget(self._txtBody)

    # --------------------------------------------------------- toggles
    def _toggle_vinculacao(self, checked):
        self._vincBody.setVisible(checked)
        self._btnToggleVinc.setText("recolher  ^" if checked else "expandir  v")

    def _toggle_textos(self, checked):
        self._txtBody.setVisible(checked)
        self._btnToggleTxt.setText("recolher  ^" if checked else "expandir  v")

    # --------------------------------------------------------- retranslateUi
    def retranslateUi(self, CadastroPromocao):
        _t = QtCore.QCoreApplication.translate
        CadastroPromocao.setWindowTitle(_t("CadastroPromocao", "CSPdv - Cadastro de Promocao"))
        self.lblBadge.setText(_t("CadastroPromocao", "CADASTRO DE PROMOCAO"))
        self.lblFormTitle.setText(_t("CadastroPromocao", "Nova Promocao"))
        self.lblFormHint.setText(_t("CadastroPromocao", "Cadastre a promocao, selecione o tipo de desconto e configure os detalhes."))
        self.lineEditCodigo.setText(_t("CadastroPromocao", "Auto-gerado"))
        self.btnLimpar.setText(_t("CadastroPromocao", "Limpar"))
        self.btnVoltar.setText(_t("CadastroPromocao", "Voltar"))
        self.btnSalvar.setText(_t("CadastroPromocao", "Salvar"))
