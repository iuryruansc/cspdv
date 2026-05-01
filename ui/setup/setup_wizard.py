from PyQt5.QtCore import QEvent, QTimer, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

BG = "#0f2030"
BG_DARK = "#081828"
BG_CARD = "#0d2030"
BORDER = "#1a4060"
BORDER_FOCUS = "#3585c8"
BLUE = "#3585c8"
BLUE_DARK = "#1a5fa0"
TEXT = "#c0dff4"
TEXT_MUTED = "#3a6a8a"
TEXT_LABEL = "#3a6a8a"
ERROR_BG = "rgba(180,30,30,40)"
ERROR_BORDER = "rgba(180,30,30,80)"
ERROR_TEXT = "#ff8080"
SUCCESS_BG = "rgba(30,120,30,40)"
SUCCESS_BG2 = "rgba(30,120,30,80)"
SUCCESS_TEXT = "#80ff80"


def _input_style() -> str:
    return (
        f"QLineEdit{{"
        f"background-color:{BG_CARD};border:2px solid {BORDER};"
        f"border-radius:6px;font-size:14px;color:{TEXT};"
        f"padding:4px 12px;selection-background-color:{BLUE};selection-color:white;}}"
        f"QLineEdit:focus{{border:2px solid {BORDER_FOCUS};background-color:#0f2840;}}"
        f"QLineEdit:hover:!focus{{border:2px solid #2a5a80;}}"
        f"QLineEdit[readOnly='true']{{background-color:#081828;color:#2a5a7a;}}"
    )


def _combo_style() -> str:
    return (
        f"QComboBox{{background-color:{BG_CARD};border:2px solid {BORDER};"
        f"border-radius:6px;font-size:14px;color:{TEXT};padding:4px 12px;}}"
        f"QComboBox:focus{{border:2px solid {BORDER_FOCUS};}}"
        f"QComboBox::drop-down{{border:none;width:24px;}}"
        f"QComboBox QAbstractItemView{{background-color:{BG_CARD};"
        f"border:1px solid {BORDER};selection-background-color:{BLUE};"
        f"color:{TEXT};font-size:13px;}}"
    )


def _btn_primary() -> str:
    return (
        f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        f"stop:0 #2a7ad8,stop:1 {BLUE_DARK});color:white;font-size:14px;"
        f"font-weight:bold;border:none;border-radius:7px;padding:10px 24px;}}"
        f"QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        f"stop:0 #3a88e8,stop:1 #2a68c8);}}"
        f"QPushButton:pressed{{background:#1a5098;}}"
        f"QPushButton:disabled{{background:#1a3a5a;color:#2a5a7a;}}"
    )


def _btn_secondary() -> str:
    return (
        f"QPushButton{{background-color:transparent;color:{TEXT_MUTED};"
        f"font-size:13px;border:1px solid {BORDER};border-radius:6px;padding:8px 20px;}}"
        f"QPushButton:hover{{background-color:rgba(255,255,255,6);color:#4a8ab0;"
        f"border-color:#2a5a80;}}"
        f"QPushButton:pressed{{background-color:rgba(255,255,255,10);}}"
    )


def _field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(
        f"font-size:11px;font-weight:bold;color:{TEXT_LABEL};letter-spacing:1px;"
    )
    return label


def _sep() -> QFrame:
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setStyleSheet(
        f"color:{BORDER};background-color:{BORDER};border:none;max-height:1px;"
    )
    return separator


class FormField(QVBoxLayout):
    def __init__(
        self,
        label: str,
        placeholder: str = "",
        password: bool = False,
        combo_items=None,
        required: bool = False,
        mask: str | None = None,
    ):
        super().__init__()
        self.setSpacing(5)
        self.addWidget(_field_label(label + (" *" if required else "")))

        if combo_items:
            self.field_widget = QComboBox()
            self.field_widget.setStyleSheet(_combo_style())
            self.field_widget.setMinimumHeight(42)
            for item in combo_items:
                self.field_widget.addItem(item)
        else:
            self.field_widget = QLineEdit()
            self.field_widget.setStyleSheet(_input_style())
            self.field_widget.setMinimumHeight(42)
            self.field_widget.setPlaceholderText(placeholder)
            self.field_widget.setCursorPosition(0)
            if mask:
                self.field_widget.setInputMask(mask)
                self.field_widget.installEventFilter(self)
            if password:
                self.field_widget.setEchoMode(QLineEdit.Password)

        self.addWidget(self.field_widget)

    def eventFilter(self, a0, a1):
        if a0 == self.field_widget and a1.type() in (QEvent.FocusIn, QEvent.MouseButtonPress):
            if isinstance(a0, QLineEdit) and a0.inputMask() and not a0.text().strip("_ -./()"):
                QTimer.singleShot(0, lambda: a0.setCursorPosition(0))
        return False

    def value(self) -> str:
        if isinstance(self.field_widget, QComboBox):
            return self.field_widget.currentText()
        return self.field_widget.text().strip()

    def set_value(self, value: str):
        if isinstance(self.field_widget, QComboBox):
            index = self.field_widget.findText(value)
            if index >= 0:
                self.field_widget.setCurrentIndex(index)
        else:
            self.field_widget.setText(value)


class WizardPageUi(QWidget):
    def __init__(self, icon: str, title: str, subtitle: str):
        super().__init__()
        self.setStyleSheet(f"background-color:{BG};")

        root = QVBoxLayout(self)
        root.setContentsMargins(44, 28, 44, 20)
        root.setSpacing(18)

        header = QVBoxLayout()
        header.setSpacing(4)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size:28px;")
        header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size:18px;font-weight:bold;color:white;")
        header.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"font-size:12px;color:{TEXT_MUTED};")
        subtitle_label.setWordWrap(True)
        header.addWidget(subtitle_label)

        root.addLayout(header)
        root.addWidget(_sep())

        self.content = QVBoxLayout()
        self.content.setSpacing(12)
        root.addLayout(self.content)
        root.addStretch()

        self.lbl_erro = QLabel()
        self.lbl_erro.setVisible(False)
        self.lbl_erro.setAlignment(Qt.AlignCenter)
        self.lbl_erro.setWordWrap(True)
        self.lbl_erro.setStyleSheet(
            f"background-color:{ERROR_BG};border:1px solid {ERROR_BORDER};"
            f"border-radius:4px;font-size:12px;font-weight:bold;"
            f"color:{ERROR_TEXT};padding:6px 10px;"
        )
        root.addWidget(self.lbl_erro)

    def show_error(self, message: str):
        self.lbl_erro.setText(f"●  {message}")
        self.lbl_erro.setVisible(True)

    def hide_error(self):
        self.lbl_erro.setVisible(False)


class PageBoasVindasUi(WizardPageUi):
    def __init__(self):
        super().__init__(
            "🚀",
            "Bem-vindo ao CSPdv",
            "Este assistente irá configurar o sistema para o primeiro uso.\n"
            "Você precisará de alguns minutos para preencher as informações básicas.",
        )
        items = [
            ("📋", "Dados da empresa", "Razão social, CNPJ e informações fiscais"),
            ("📍", "Endereço", "Localização da empresa para documentos"),
            ("🖥️", "PDV principal", "Identificação do terminal de vendas"),
            ("👤", "Conta administrador", "Login e senha do primeiro usuário"),
        ]
        for icon, title, description in items:
            row = QHBoxLayout()
            row.setSpacing(12)
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size:20px;min-width:28px;")
            icon_label.setFixedWidth(28)
            row.addWidget(icon_label)

            column = QVBoxLayout()
            column.setSpacing(2)
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size:13px;font-weight:bold;color:white;")
            desc_label = QLabel(description)
            desc_label.setStyleSheet(f"font-size:11px;color:{TEXT_MUTED};")
            column.addWidget(title_label)
            column.addWidget(desc_label)
            row.addLayout(column)

            self.content.addLayout(row)


class PageEmpresaUi(WizardPageUi):
    def __init__(self):
        super().__init__(
            "🏢",
            "Dados da Empresa",
            "Informações que aparecem nos documentos fiscais e relatórios.",
        )
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        self.f_razao = FormField("Razão Social", "Ex: Empresa LTDA", required=True)
        self.f_fantasia = FormField("Nome Fantasia", "Como aparece ao cliente")
        row1.addLayout(self.f_razao, 3)
        row1.addLayout(self.f_fantasia, 2)
        self.content.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)
        self.f_cnpj = FormField("CNPJ", required=True, mask="00.000.000/0000-00;_")
        self.f_ie = FormField("Inscrição Estadual", "Opcional")
        self.f_regime = FormField(
            "Regime Tributário",
            combo_items=["Simples Nacional", "Lucro Presumido", "Lucro Real", "MEI"],
        )
        row2.addLayout(self.f_cnpj, 2)
        row2.addLayout(self.f_ie, 2)
        row2.addLayout(self.f_regime, 2)
        self.content.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(12)
        self.f_email = FormField("E-mail", "empresa@email.com")
        self.f_telefone = FormField("Telefone", mask="(00) 00000-0000;_")
        row3.addLayout(self.f_email, 2)
        row3.addLayout(self.f_telefone, 1)
        self.content.addLayout(row3)


class PageEnderecoUi(WizardPageUi):
    def __init__(self):
        super().__init__(
            "📍",
            "Endereço da Empresa",
            "Utilizado em notas fiscais e documentos gerados pelo sistema.",
        )
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        self.f_cep = FormField("CEP", mask="00000-000;_")
        self.f_logr = FormField("Logradouro", "Rua, Av., etc.")
        self.f_numero = FormField("Número", "Nº")
        row1.addLayout(self.f_cep, 1)
        row1.addLayout(self.f_logr, 3)
        row1.addLayout(self.f_numero, 1)
        self.content.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)
        self.f_bairro = FormField("Bairro", "Bairro")
        self.f_cidade = FormField("Cidade", "Cidade")
        self.f_estado = FormField(
            "UF",
            combo_items=[
                "",
                "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
                "MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC",
                "SP","SE","TO",
            ],
        )
        row2.addLayout(self.f_bairro, 2)
        row2.addLayout(self.f_cidade, 3)
        row2.addLayout(self.f_estado, 1)
        self.content.addLayout(row2)


class PagePDVUi(WizardPageUi):
    def __init__(self):
        super().__init__(
            "🖥️",
            "Terminal de Vendas (PDV)",
            "Configure o primeiro terminal. Outros podem ser adicionados depois.",
        )
        self.f_id = FormField("Identificação", "Ex: PDV-01 ou CAIXA-01", required=True)
        self.f_desc = FormField("Descrição", "Ex: Caixa Principal - Recepção")
        self.content.addLayout(self.f_id)
        self.content.addLayout(self.f_desc)
        self.f_id.set_value("PDV-01")
        self.f_desc.set_value("Caixa Principal")


class PageAdminUi(WizardPageUi):
    def __init__(self):
        super().__init__(
            "👤",
            "Conta Administrador",
            "Será o primeiro usuário com acesso total ao sistema.",
        )
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        self.f_nome = FormField("Nome Completo", "Nome para exibição", required=True)
        self.f_login = FormField("Login (usuário)", "Nome de usuário para entrar", required=True)
        row1.addLayout(self.f_nome, 2)
        row1.addLayout(self.f_login, 1)
        self.content.addLayout(row1)

        self.f_email = FormField("E-mail", "admin@empresa.com")
        self.content.addLayout(self.f_email)

        row2 = QHBoxLayout()
        row2.setSpacing(12)
        self.f_senha = FormField("Senha", "Mínimo 6 caracteres", password=True, required=True)
        self.f_confirma = FormField("Confirmar Senha", "Repita a senha", password=True, required=True)
        row2.addLayout(self.f_senha)
        row2.addLayout(self.f_confirma)
        self.content.addLayout(row2)


class PageConclusaoUi(WizardPageUi):
    def __init__(self):
        super().__init__(
            "✅",
            "Tudo pronto!",
            "Revise o resumo abaixo e clique em Concluir para salvar.",
        )
        self.lbl_resumo = QLabel()
        self.lbl_resumo.setWordWrap(True)
        self.lbl_resumo.setStyleSheet(
            f"background-color:{BG_CARD};border:1px solid {BORDER};"
            f"border-radius:6px;font-size:12px;color:{TEXT};"
            f"padding:14px;line-height:1.6;"
        )
        self.content.addWidget(self.lbl_resumo)

        self.lbl_salvo = QLabel("✓  Dados salvos com sucesso!")
        self.lbl_salvo.setVisible(False)
        self.lbl_salvo.setAlignment(Qt.AlignCenter)
        self.lbl_salvo.setStyleSheet(
            f"background-color:{SUCCESS_BG};border:1px solid {SUCCESS_BG2};"
            f"border-radius:4px;font-size:13px;font-weight:bold;"
            f"color:{SUCCESS_TEXT};padding:8px;"
        )
        self.content.addWidget(self.lbl_salvo)


class SetupWizardUi:
    def setupUi(self, dialog: QDialog, pages: list[QWidget]):
        dialog.setWindowTitle("CSPdv - Configuração Inicial")
        dialog.setMinimumSize(780, 620)
        dialog.setModal(True)
        dialog.setStyleSheet(f"QDialog{{background-color:{BG};font-family:Arial;}}")

        root = QVBoxLayout(dialog)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame(dialog)
        header.setMinimumHeight(64)
        header.setMaximumHeight(64)
        header.setStyleSheet(
            f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 #1a3a5a,stop:1 {BG_DARK});border-bottom:2px solid {BLUE};}}"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)

        self.lblLogo = QLabel("CSPdv")
        self.lblLogo.setStyleSheet(
            "color:white;font-size:26px;font-weight:bold;letter-spacing:2px;"
        )
        header_layout.addWidget(self.lblLogo)

        self.lineHeader = QFrame()
        self.lineHeader.setFrameShape(QFrame.VLine)
        self.lineHeader.setStyleSheet(f"color:{BORDER};max-width:1px;")
        header_layout.addWidget(self.lineHeader)

        self.lblTag = QLabel("Configuração Inicial")
        self.lblTag.setStyleSheet(f"color:{BLUE};font-size:12px;letter-spacing:1px;")
        header_layout.addWidget(self.lblTag)
        header_layout.addStretch()

        self.step_labels = []
        step_names = ["Início", "Empresa", "Endereço", "PDV", "Admin", "Concluir"]
        for index, name in enumerate(step_names):
            label = QLabel(f"{'●' if index == 0 else '○'}  {name}")
            label.setStyleSheet(
                f"font-size:11px;color:{'white' if index == 0 else TEXT_MUTED};"
                f"{'font-weight:bold;' if index == 0 else ''}"
            )
            self.step_labels.append(label)
            header_layout.addWidget(label)
            if index < len(step_names) - 1:
                arrow = QLabel("›")
                arrow.setStyleSheet(f"font-size:14px;color:{BORDER};")
                header_layout.addWidget(arrow)

        root.addWidget(header)

        self.progress = QProgressBar(dialog)
        self.progress.setMaximumHeight(4)
        self.progress.setRange(0, 5)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            f"QProgressBar{{border:none;background-color:{BG_DARK};}}"
            f"QProgressBar::chunk{{background:{BLUE};border-radius:0px;}}"
        )
        root.addWidget(self.progress)

        self.stack = QStackedWidget(dialog)
        self.stack.setStyleSheet(f"background-color:{BG};")
        for page in pages:
            self.stack.addWidget(page)
        root.addWidget(self.stack)

        footer = QFrame(dialog)
        footer.setMinimumHeight(68)
        footer.setMaximumHeight(68)
        footer.setStyleSheet(
            f"QFrame{{background-color:{BG_DARK};border-top:1px solid {BORDER};}}"
        )
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 0, 24, 0)
        footer_layout.setSpacing(12)

        self.lbl_status = QLabel("Pronto.")
        self.lbl_status.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;")
        footer_layout.addWidget(self.lbl_status)
        footer_layout.addStretch()

        self.btn_voltar = QPushButton("◀  Voltar")
        self.btn_voltar.setStyleSheet(_btn_secondary())
        self.btn_voltar.setMinimumSize(120, 40)
        self.btn_voltar.setVisible(False)

        self.btn_avancar = QPushButton("Avançar  ▶")
        self.btn_avancar.setStyleSheet(_btn_primary())
        self.btn_avancar.setMinimumSize(140, 40)

        footer_layout.addWidget(self.btn_voltar)
        footer_layout.addWidget(self.btn_avancar)
        root.addWidget(footer)

