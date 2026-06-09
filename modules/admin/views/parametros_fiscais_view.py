from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.admin.services.configuracoes_service import ConfiguracoesService
from utils.ui_messages import mostrar_aviso, mostrar_info


class ParametrosFiscaisView(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("frameParametrosFiscais")
        self.setStyleSheet(
            """
            QFrame#frameParametrosFiscais {
                background-color: white;
                border: 1px solid #a8c4d8;
                border-radius: 6px;
            }
            QLabel[sectionTitle="true"] {
                color: #1a3a5c;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel[sectionHint="true"] {
                color: #5d7f99;
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                background-color: #f7fbff;
                border: 1px solid #c5d8e6;
                border-radius: 4px;
                padding: 7px 10px;
                font-size: 12px;
                min-height: 18px;
            }
            QCheckBox {
                color: #1a3a5c;
                font-size: 12px;
            }
            QPushButton[primaryButton="true"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3585c8, stop:1 #1a5fa0);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton[primaryButton="true"]:hover {
                background: #2a74b8;
            }
            """
        )

        self._montar_ui()
        self._carregar_dados()

    def _montar_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self.lblTitle = QLabel("Parâmetros Fiscais", self)
        self.lblTitle.setProperty("sectionTitle", True)
        root.addWidget(self.lblTitle)

        self.lblHint = QLabel(
            "Configure os padrões fiscais da operação e as exigências mínimas do cadastro de produto.",
            self,
        )
        self.lblHint.setWordWrap(True)
        self.lblHint.setProperty("sectionHint", True)
        root.addWidget(self.lblHint)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(10)

        self.comboRegime = QComboBox(self)
        self.comboRegime.addItems(ConfiguracoesService.opcoes_regime_tributario())
        form.addRow("Regime tributário padrão", self.comboRegime)

        self.comboOrigem = QComboBox(self)
        self.comboOrigem.addItems(ConfiguracoesService.opcoes_origem_mercadoria())
        form.addRow("Origem da mercadoria", self.comboOrigem)

        self.lineCfopVenda = QLineEdit(self)
        self.lineCfopVenda.setPlaceholderText("5102")
        form.addRow("CFOP padrão de venda", self.lineCfopVenda)

        self.lineCfopDevolucao = QLineEdit(self)
        self.lineCfopDevolucao.setPlaceholderText("1202")
        form.addRow("CFOP padrão de devolução", self.lineCfopDevolucao)

        self.lineCsosn = QLineEdit(self)
        self.lineCsosn.setPlaceholderText("102")
        form.addRow("CSOSN / CST padrão", self.lineCsosn)

        self.lineNatureza = QLineEdit(self)
        self.lineNatureza.setPlaceholderText("VENDA DE MERCADORIA")
        form.addRow("Natureza da operação", self.lineNatureza)

        root.addLayout(form)

        self.boxRegras = QFrame(self)
        regras_layout = QVBoxLayout(self.boxRegras)
        regras_layout.setContentsMargins(0, 6, 0, 6)
        regras_layout.setSpacing(10)

        self.lblRegras = QLabel("Exigências no cadastro de produto", self.boxRegras)
        self.lblRegras.setProperty("sectionTitle", True)
        self.lblRegras.setStyleSheet("font-size: 14px;")
        regras_layout.addWidget(self.lblRegras)

        self.checkExigirNcmCest = QCheckBox("Exigir NCM e CEST no cadastro de produto", self.boxRegras)
        regras_layout.addWidget(self.checkExigirNcmCest)

        self.checkExigirUnidadeTrib = QCheckBox(
            "Exigir unidade tributável no cadastro de produto",
            self.boxRegras,
        )
        regras_layout.addWidget(self.checkExigirUnidadeTrib)

        root.addWidget(self.boxRegras)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.btnSalvar = QPushButton("Salvar parâmetros fiscais", self)
        self.btnSalvar.setProperty("primaryButton", True)
        self.btnSalvar.clicked.connect(self._salvar)
        buttons.addWidget(self.btnSalvar)
        root.addLayout(buttons)

    def _carregar_dados(self) -> None:
        try:
            dados = ConfiguracoesService.carregar_parametros_fiscais()
        except Exception as exc:
            mostrar_aviso(self, "Parâmetros Fiscais", f"Não foi possível carregar os parâmetros fiscais.\n\nDetalhes: {exc}")
            return

        self.comboRegime.setCurrentText(
            ConfiguracoesService.label_regime_tributario(dados.get("regime_tributario_padrao"))
        )
        self.comboOrigem.setCurrentText(
            ConfiguracoesService.label_origem_mercadoria(dados.get("origem_mercadoria_padrao"))
        )
        self.lineCfopVenda.setText(str(dados.get("cfop_venda_padrao") or "5102"))
        self.lineCfopDevolucao.setText(str(dados.get("cfop_devolucao_padrao") or "1202"))
        self.lineCsosn.setText(str(dados.get("csosn_cst_padrao") or "102"))
        self.lineNatureza.setText(str(dados.get("natureza_operacao_padrao") or "VENDA DE MERCADORIA"))
        self.checkExigirNcmCest.setChecked(bool(dados.get("exigir_ncm_cest_produto", True)))
        self.checkExigirUnidadeTrib.setChecked(bool(dados.get("exigir_unidade_tributavel_produto", True)))

    def _salvar(self) -> None:
        sucesso, mensagem = ConfiguracoesService.salvar_parametros_fiscais(
            regime_tributario_label=self.comboRegime.currentText(),
            origem_mercadoria_label=self.comboOrigem.currentText(),
            cfop_venda_padrao=self.lineCfopVenda.text(),
            cfop_devolucao_padrao=self.lineCfopDevolucao.text(),
            csosn_cst_padrao=self.lineCsosn.text(),
            natureza_operacao_padrao=self.lineNatureza.text(),
            exigir_ncm_cest_produto=self.checkExigirNcmCest.isChecked(),
            exigir_unidade_tributavel_produto=self.checkExigirUnidadeTrib.isChecked(),
        )
        if not sucesso:
            mostrar_aviso(self, "Parâmetros Fiscais", mensagem)
            return

        mostrar_info(self, "Parâmetros Fiscais", mensagem)
