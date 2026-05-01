from PyQt5 import QtCore, QtWidgets


class Ui_ConfiguracoesWidget(object):
    def setupUi(self, widget):
        widget.setObjectName("ConfiguracoesWidget")
        widget.setStyleSheet(
            """
            QWidget#ConfiguracoesWidget {
                background-color: white;
                border: 1px solid #a8c4d8;
                border-radius: 6px;
                color: #18324a;
                font-family: "Segoe UI";
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget#scrollContent {
                background: transparent;
            }
            QFrame[configCard="true"] {
                background-color: #fbfdff;
                border: 1px solid #d6e3ee;
                border-radius: 12px;
            }
            QLabel[sectionTitle="true"] {
                color: #1a3a5c;
                font-size: 16px;
                font-weight: 700;
            }
            QLabel[sectionHint="true"] {
                color: #5d7f99;
                font-size: 12px;
            }
            QLabel[cardTitle="true"] {
                color: #153552;
                font-size: 14px;
                font-weight: 800;
            }
            QLabel[cardHint="true"] {
                color: #65829b;
                font-size: 11px;
            }
            QLabel[fieldLabel="true"] {
                color: #315676;
                font-size: 11px;
                font-weight: 700;
            }
            QLineEdit, QComboBox {
                min-height: 40px;
                background-color: #f7fbff;
                border: 1px solid #c5d8e6;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 12px;
                color: #18324a;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3a8ad3;
                background-color: white;
            }
            QCheckBox {
                color: #18324a;
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QPushButton[secondaryButton="true"] {
                background-color: #f0f6fc;
                color: #1a3a5c;
                border: 1px solid #c0d8ec;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton[secondaryButton="true"]:hover {
                background-color: #dceaf4;
            }
            QPushButton[primaryButton="true"] {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3585c8, stop:1 #1a5fa0);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton[primaryButton="true"]:hover {
                background: #2a74b8;
            }
            """
        )

        self.rootLayout = QtWidgets.QVBoxLayout(widget)
        self.rootLayout.setContentsMargins(16, 16, 16, 16)
        self.rootLayout.setSpacing(12)

        self.lblTitle = QtWidgets.QLabel(widget)
        self.lblTitle.setProperty("sectionTitle", True)
        self.lblTitle.setObjectName("lblTitle")
        self.rootLayout.addWidget(self.lblTitle)

        self.lblHint = QtWidgets.QLabel(widget)
        self.lblHint.setProperty("sectionHint", True)
        self.lblHint.setWordWrap(True)
        self.lblHint.setObjectName("lblHint")
        self.rootLayout.addWidget(self.lblHint)

        self.scrollArea = QtWidgets.QScrollArea(widget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollContent = QtWidgets.QWidget()
        self.scrollContent.setObjectName("scrollContent")
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollContent)
        self.scrollLayout.setContentsMargins(4, 4, 4, 4)
        self.scrollLayout.setSpacing(14)

        self.frameEmpresa = self._criar_card("frameEmpresa", "Empresa e PDV", "Defina dados-base da operação, identificação padrão e contexto inicial do terminal.")
        self._montar_empresa()
        self.scrollLayout.addWidget(self.frameEmpresa)

        self.frameVendas = self._criar_card("frameVendas", "Parâmetros de Venda", "Centralize regras gerais da venda rápida, do cliente padrão e do comportamento comercial.")
        self._montar_vendas()
        self.scrollLayout.addWidget(self.frameVendas)

        self.frameCaixa = self._criar_card("frameCaixa", "Parâmetros de Caixa", "Ajuste exigências operacionais para abertura, diferenças, sangrias e reembolsos.")
        self._montar_caixa()
        self.scrollLayout.addWidget(self.frameCaixa)

        self.framePromocoes = self._criar_card("framePromocoes", "Promoções", "Controle o comportamento padrão da aplicação de campanhas e descontos em conflito.")
        self._montar_promocoes()
        self.scrollLayout.addWidget(self.framePromocoes)

        self.frameSeguranca = self._criar_card("frameSeguranca", "Segurança e Sessão", "Concentre políticas de autenticação, restauração de sessão e proteção da operação em andamento.")
        self._montar_seguranca()
        self.scrollLayout.addWidget(self.frameSeguranca)

        self.frameSistema = self._criar_card("frameSistema", "Sistema", "Registre preferências técnicas iniciais para backup, auditoria e exibição do ambiente.")
        self._montar_sistema()
        self.scrollLayout.addWidget(self.frameSistema)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setSpacing(10)
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacer)
        self.btnRestaurarPadroes = QtWidgets.QPushButton(self.scrollContent)
        self.btnRestaurarPadroes.setProperty("secondaryButton", True)
        self.btnRestaurarPadroes.setObjectName("btnRestaurarPadroes")
        self.buttonLayout.addWidget(self.btnRestaurarPadroes)
        self.btnSalvarParametros = QtWidgets.QPushButton(self.scrollContent)
        self.btnSalvarParametros.setProperty("primaryButton", True)
        self.btnSalvarParametros.setObjectName("btnSalvarParametros")
        self.buttonLayout.addWidget(self.btnSalvarParametros)
        self.scrollLayout.addLayout(self.buttonLayout)
        self.scrollLayout.addStretch(1)

        self.scrollArea.setWidget(self.scrollContent)
        self.rootLayout.addWidget(self.scrollArea, 1)

        self.retranslateUi(widget)
        QtCore.QMetaObject.connectSlotsByName(widget)

    def _criar_card(self, object_name: str, titulo: str, subtitulo: str) -> QtWidgets.QFrame:
        frame = QtWidgets.QFrame()
        frame.setObjectName(object_name)
        frame.setProperty("configCard", True)
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl_titulo = QtWidgets.QLabel(frame)
        lbl_titulo.setProperty("cardTitle", True)
        lbl_titulo.setText(titulo)
        layout.addWidget(lbl_titulo)

        lbl_hint = QtWidgets.QLabel(frame)
        lbl_hint.setProperty("cardHint", True)
        lbl_hint.setWordWrap(True)
        lbl_hint.setText(subtitulo)
        layout.addWidget(lbl_hint)
        return frame

    def _adicionar_linha_campo(self, layout: QtWidgets.QGridLayout, row: int, col: int, label: str, editor: QtWidgets.QWidget) -> None:
        lbl = QtWidgets.QLabel(editor.parent())
        lbl.setProperty("fieldLabel", True)
        lbl.setText(label)
        layout.addWidget(lbl, row * 2, col)
        layout.addWidget(editor, row * 2 + 1, col)

    def _montar_empresa(self) -> None:
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        self.lineEditRazaoSocial = QtWidgets.QLineEdit(self.frameEmpresa)
        self.comboPdvPadrao = QtWidgets.QComboBox(self.frameEmpresa)
        self.comboPdvPadrao.addItems(["PDV-01 - Caixa Principal", "PDV-02 - Apoio"])
        self.comboMoeda = QtWidgets.QComboBox(self.frameEmpresa)
        self.comboMoeda.addItems(["Real (BRL)", "Dólar (USD)"])

        self._adicionar_linha_campo(grid, 0, 0, "Razão Social", self.lineEditRazaoSocial)
        self._adicionar_linha_campo(grid, 0, 1, "PDV Padrão", self.comboPdvPadrao)
        self._adicionar_linha_campo(grid, 0, 2, "Moeda", self.comboMoeda)
        self.frameEmpresa.layout().addLayout(grid)

    def _montar_vendas(self) -> None:
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        self.comboClientePadrao = QtWidgets.QComboBox(self.frameVendas)
        self.comboClientePadrao.addItems(["Consumidor Final", "Selecionar no momento da venda"])
        self.comboRegraDesconto = QtWidgets.QComboBox(self.frameVendas)
        self.comboRegraDesconto.addItems(["Permitir desconto manual", "Exigir autorização para desconto"])
        self.checkVendaRapidaAdmin = QtWidgets.QCheckBox("Habilitar Venda Rápida no painel admin", self.frameVendas)
        self.checkPermitirVendaSemEstoque = QtWidgets.QCheckBox("Permitir venda sem estoque", self.frameVendas)

        self._adicionar_linha_campo(grid, 0, 0, "Cliente Padrão", self.comboClientePadrao)
        self._adicionar_linha_campo(grid, 0, 1, "Regra de Desconto", self.comboRegraDesconto)
        grid.addWidget(self.checkVendaRapidaAdmin, 2, 0)
        grid.addWidget(self.checkPermitirVendaSemEstoque, 2, 1)
        self.frameVendas.layout().addLayout(grid)

    def _montar_caixa(self) -> None:
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        self.lineEditFundoSugerido = QtWidgets.QLineEdit(self.frameCaixa)
        self.lineEditFundoSugerido.setPlaceholderText("0,00")
        self.checkExigirAdminSangria = QtWidgets.QCheckBox("Exigir admin em sangria", self.frameCaixa)
        self.checkExigirAdminReembolso = QtWidgets.QCheckBox("Exigir admin em reembolso", self.frameCaixa)
        self.checkExigirAdminDiferenca = QtWidgets.QCheckBox("Exigir admin em diferença no fechamento", self.frameCaixa)

        self._adicionar_linha_campo(grid, 0, 0, "Fundo Inicial Sugerido", self.lineEditFundoSugerido)
        grid.addWidget(self.checkExigirAdminSangria, 1, 1)
        grid.addWidget(self.checkExigirAdminReembolso, 2, 1)
        grid.addWidget(self.checkExigirAdminDiferenca, 3, 1)
        self.frameCaixa.layout().addLayout(grid)

    def _montar_promocoes(self) -> None:
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        self.comboPrioridadePromocao = QtWidgets.QComboBox(self.framePromocoes)
        self.comboPrioridadePromocao.addItems(["Promoção antes do desconto manual", "Desconto manual antes da promoção"])
        self.checkBloquearPromocoesSimultaneas = QtWidgets.QCheckBox("Bloquear promoções simultâneas por produto", self.framePromocoes)
        self.checkAtivarPorVigencia = QtWidgets.QCheckBox("Ativar promoções automaticamente pela vigência", self.framePromocoes)

        self._adicionar_linha_campo(grid, 0, 0, "Prioridade Promocional", self.comboPrioridadePromocao)
        grid.addWidget(self.checkBloquearPromocoesSimultaneas, 1, 0)
        grid.addWidget(self.checkAtivarPorVigencia, 2, 0)
        self.framePromocoes.layout().addLayout(grid)

    def _montar_seguranca(self) -> None:
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        self.lineEditHorasSessao = QtWidgets.QLineEdit(self.frameSeguranca)
        self.lineEditHorasSessao.setPlaceholderText("12")
        self.checkRestaurarLogin = QtWidgets.QCheckBox("Restaurar login automaticamente quando válido", self.frameSeguranca)
        self.checkBloquearFecharAppCaixa = QtWidgets.QCheckBox("Bloquear fechamento do programa com caixa aberto", self.frameSeguranca)

        self._adicionar_linha_campo(grid, 0, 0, "Horas de Sessão Persistida", self.lineEditHorasSessao)
        grid.addWidget(self.checkRestaurarLogin, 1, 1)
        grid.addWidget(self.checkBloquearFecharAppCaixa, 2, 1)
        self.frameSeguranca.layout().addLayout(grid)

    def _montar_sistema(self) -> None:
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        self.lineEditIntervaloBackup = QtWidgets.QLineEdit(self.frameSistema)
        self.lineEditIntervaloBackup.setPlaceholderText("24")
        self.comboPerfilLog = QtWidgets.QComboBox(self.frameSistema)
        self.comboPerfilLog.addItems(["Operacional", "Detalhado", "Silencioso"])
        self.lineEditVersaoReferencia = QtWidgets.QLineEdit(self.frameSistema)
        self.lineEditVersaoReferencia.setReadOnly(True)
        self.lineEditVersaoReferencia.setText("CSPdv v1.0.0")

        self._adicionar_linha_campo(grid, 0, 0, "Intervalo de Backup (h)", self.lineEditIntervaloBackup)
        self._adicionar_linha_campo(grid, 0, 1, "Perfil de Log", self.comboPerfilLog)
        self._adicionar_linha_campo(grid, 0, 2, "Versão de Referência", self.lineEditVersaoReferencia)
        self.frameSistema.layout().addLayout(grid)

    def retranslateUi(self, widget):
        _translate = QtCore.QCoreApplication.translate
        widget.setWindowTitle(_translate("ConfiguracoesWidget", "CSPdv - Configurações"))
        self.lblTitle.setText(_translate("ConfiguracoesWidget", "Configurações do Sistema"))
        self.lblHint.setText(_translate("ConfiguracoesWidget", "Organize parâmetros iniciais de empresa, vendas, caixa, promoções e segurança sem sair do painel administrativo."))
        self.btnRestaurarPadroes.setText(_translate("ConfiguracoesWidget", "Restaurar padrões"))
        self.btnSalvarParametros.setText(_translate("ConfiguracoesWidget", "Salvar parâmetros"))
