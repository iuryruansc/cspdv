import re
import requests
from typing import Union
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QStackedWidget, QComboBox, QWidget,
    QProgressBar, QMessageBox
)
from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models.setup_model import SetupModel

# ─── Paleta e helpers de estilo ─────────────────────────────────────────────
BG          = '#0f2030'
BG_DARK     = '#081828'
BG_CARD     = '#0d2030'
BORDER      = '#1a4060'
BORDER_FOCUS= '#3585c8'
BLUE        = '#3585c8'
BLUE_DARK   = '#1a5fa0'
TEXT        = '#c0dff4'
TEXT_MUTED  = '#3a6a8a'
TEXT_LABEL  = '#3a6a8a'
ERROR_BG    = 'rgba(180,30,30,40)'
ERROR_BORDER= 'rgba(180,30,30,80)'
ERROR_TEXT  = '#ff8080'
SUCCESS_BG  = 'rgba(30,120,30,40)'
SUCCESS_BG2 = 'rgba(30,120,30,80)'
SUCCESS_TEXT= '#80ff80'


def _input_style():
    return (
        f"QLineEdit{{"
        f"background-color:{BG_CARD};border:2px solid {BORDER};"
        f"border-radius:6px;font-size:14px;color:{TEXT};"
        f"padding:4px 12px;selection-background-color:{BLUE};selection-color:white;}}"
        f"QLineEdit:focus{{border:2px solid {BORDER_FOCUS};background-color:#0f2840;}}"
        f"QLineEdit:hover:!focus{{border:2px solid #2a5a80;}}"
        f"QLineEdit[readOnly='true']{{background-color:#081828;color:#2a5a7a;}}"
    )

def _combo_style():
    return (
        f"QComboBox{{background-color:{BG_CARD};border:2px solid {BORDER};"
        f"border-radius:6px;font-size:14px;color:{TEXT};padding:4px 12px;}}"
        f"QComboBox:focus{{border:2px solid {BORDER_FOCUS};}}"
        f"QComboBox::drop-down{{border:none;width:24px;}}"
        f"QComboBox QAbstractItemView{{background-color:{BG_CARD};"
        f"border:1px solid {BORDER};selection-background-color:{BLUE};"
        f"color:{TEXT};font-size:13px;}}"
    )

def _btn_primary():
    return (
        f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        f"stop:0 #2a7ad8,stop:1 {BLUE_DARK});color:white;font-size:14px;"
        f"font-weight:bold;border:none;border-radius:7px;padding:10px 24px;}}"
        f"QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        f"stop:0 #3a88e8,stop:1 #2a68c8);}}"
        f"QPushButton:pressed{{background:#1a5098;}}"
        f"QPushButton:disabled{{background:#1a3a5a;color:#2a5a7a;}}"
    )

def _btn_secondary():
    return (
        f"QPushButton{{background-color:transparent;color:{TEXT_MUTED};"
        f"font-size:13px;border:1px solid {BORDER};border-radius:6px;padding:8px 20px;}}"
        f"QPushButton:hover{{background-color:rgba(255,255,255,6);color:#4a8ab0;"
        f"border-color:#2a5a80;}}"
        f"QPushButton:pressed{{background-color:rgba(255,255,255,10);}}"
    )

def _label(text, size=11, bold=False, color=None):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:{size}px;"
        f"{'font-weight:bold;' if bold else ''}"
        f"color:{color or TEXT_LABEL};"
        "letter-spacing:1px;"
    )
    return lbl

def _field_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size:11px;font-weight:bold;color:{TEXT_LABEL};letter-spacing:1px;")
    return lbl

def _sep():
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet(f"color:{BORDER};background-color:{BORDER};border:none;max-height:1px;")
    return sep


# ─── Campo de formulário (label + input) ────────────────────────────────────
class FormField(QVBoxLayout):
    def __init__(self, label, placeholder='', password=False, combo_items=None, required=False, mask=None):

        super().__init__()
        self.setSpacing(5)
        lbl_text = label + (' *' if required else '')
        self.addWidget(_field_label(lbl_text))

        self.field_widget: Union[QLineEdit, QComboBox]
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
            if isinstance(a0, QLineEdit) and a0.inputMask():
                raw_text = re.sub(r'[^a-zA-Z0-9]', '', a0.text())
                if not raw_text:
                    QTimer.singleShot(0, lambda: a0.setCursorPosition(0))
                    
        return super().eventFilter(a0, a1)

    def value(self):
        if isinstance(self.field_widget, QComboBox):
            return self.field_widget.currentText()
        return self.field_widget.text().strip()

    def set_value(self, v):
        if isinstance(self.field_widget, QComboBox):
            idx = self.field_widget.findText(v)
            if idx >= 0:
                self.field_widget.setCurrentIndex(idx)
        else:
            self.field_widget.setText(v)


# ─── Página base ────────────────────────────────────────────────────────────
class WizardPage(QWidget):
    def __init__(self, icon, title, subtitle):
        super().__init__()
        self.setStyleSheet(f"background-color:{BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 28, 44, 20)
        root.setSpacing(18)

        # Cabeçalho da página
        hdr = QVBoxLayout()
        hdr.setSpacing(4)
        ico = QLabel(icon)
        ico.setStyleSheet("font-size:28px;")
        hdr.addWidget(ico)
        ttl = QLabel(title)
        ttl.setStyleSheet(f"font-size:18px;font-weight:bold;color:white;")
        hdr.addWidget(ttl)
        sub = QLabel(subtitle)
        sub.setStyleSheet(f"font-size:12px;color:{TEXT_MUTED};")
        sub.setWordWrap(True)
        hdr.addWidget(sub)
        root.addLayout(hdr)
        root.addWidget(_sep())

        # Área de conteúdo (subclasse preenche)
        self.content = QVBoxLayout()
        self.content.setSpacing(12)
        root.addLayout(self.content)
        root.addStretch()

        # Label de erro/aviso
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

    def show_error(self, msg):
        self.lbl_erro.setText(f'●  {msg}')
        self.lbl_erro.setVisible(True)

    def hide_error(self):
        self.lbl_erro.setVisible(False)

    def validate(self) -> bool:
        """Subclasse sobrescreve. Retorna True se pode avançar."""
        return True

    def get_data(self) -> dict:
        """Subclasse sobrescreve. Retorna dict com os dados da página."""
        return {}


# ─── Página 1: Boas-vindas ──────────────────────────────────────────────────
class PageBoasVindas(WizardPage):
    def __init__(self):
        super().__init__(
            '🚀', 'Bem-vindo ao CSPdv',
            'Este assistente irá configurar o sistema para o primeiro uso.\n'
            'Você precisará de alguns minutos para preencher as informações básicas.'
        )
        items = [
            ('📋', 'Dados da empresa',    'Razão social, CNPJ e informações fiscais'),
            ('📍', 'Endereço',            'Localização da empresa para documentos'),
            ('🖥️', 'PDV principal',       'Identificação do terminal de vendas'),
            ('👤', 'Conta administrador', 'Login e senha do primeiro usuário'),
        ]
        for icon, title, desc in items:
            row = QHBoxLayout()
            row.setSpacing(12)
            ico = QLabel(icon)
            ico.setStyleSheet("font-size:20px;min-width:28px;")
            ico.setFixedWidth(28)
            row.addWidget(ico)
            col = QVBoxLayout()
            col.setSpacing(2)
            t = QLabel(title)
            t.setStyleSheet(f"font-size:13px;font-weight:bold;color:white;")
            d = QLabel(desc)
            d.setStyleSheet(f"font-size:11px;color:{TEXT_MUTED};")
            col.addWidget(t)
            col.addWidget(d)
            row.addLayout(col)
            self.content.addLayout(row)


# ─── Página 2: Dados da empresa ─────────────────────────────────────────────
class PageEmpresa(WizardPage):
    def __init__(self):
        super().__init__(
            '🏢', 'Dados da Empresa',
            'Informações que aparecem nos documentos fiscais e relatórios.'
        )
        row1 = QHBoxLayout(); row1.setSpacing(12)
        self.f_razao    = FormField('Razão Social', 'Ex: Empresa LTDA', required=True)
        self.f_fantasia = FormField('Nome Fantasia', 'Como aparece ao cliente')
        row1.addLayout(self.f_razao, 3)
        row1.addLayout(self.f_fantasia, 2)
        self.content.addLayout(row1)

        row2 = QHBoxLayout(); row2.setSpacing(12)
        self.f_cnpj = FormField('CNPJ', required=True, mask='00.000.000/0000-00;_')
        self.f_ie   = FormField('Inscrição Estadual', 'Opcional')
        self.f_regime = FormField('Regime Tributário', combo_items=[
            'Simples Nacional',
            'Lucro Presumido',
            'Lucro Real',
            'MEI',
        ])
        row2.addLayout(self.f_cnpj, 2)
        row2.addLayout(self.f_ie, 2)
        row2.addLayout(self.f_regime, 2)
        self.content.addLayout(row2)

        row3 = QHBoxLayout(); row3.setSpacing(12)
        self.f_email    = FormField('E-mail', 'empresa@email.com')
        self.f_telefone = FormField('Telefone', mask='(00) 00000-0000;_')
        row3.addLayout(self.f_email, 2)
        row3.addLayout(self.f_telefone, 1)
        self.content.addLayout(row3)

    def validate(self):
        razao = self.f_razao.value()
        cnpj = re.sub(r'\D', '', self.f_cnpj.value())
        email = self.f_email.value()
        tel_limpo = re.sub(r'\D', '', self.f_telefone.value())

        if tel_limpo and len(tel_limpo) < 10:
            self.show_error('Telefone incompleto.')
            return False

        if not razao or len(razao) < 3:
            self.show_error('Razão Social é obrigatória.')
            return False
        
        if not self.validar_cnpj(cnpj):
            self.show_error('CNPJ inválido ou mal formatado.')
            return False
        
        if email and not self.validar_email(email):
            self.show_error('O formato do e-mail informado é inválido.')
            return False
        
        self.hide_error()
        return True
    
    def validar_email(self, email):
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        return re.search(regex, email.lower())
    
    def validar_cnpj(self, cnpj):
        cnpj = re.sub(r'\D', '', cnpj)
        if len(cnpj) != 14 or len(set(cnpj)) == 1:
            return False
    
        def calcular_digito(cnpj, pesos):
            soma = sum(int(a) * b for a, b in zip(cnpj, pesos))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
        digito1 = calcular_digito(cnpj[:12], pesos1)
        digito2 = calcular_digito(cnpj[:13], pesos2)
    
        return cnpj[-2:] == f"{digito1}{digito2}"

    def get_data(self):
        return {
            'razao_social':       self.f_razao.value(),
            'nome_fantasia':      self.f_fantasia.value(),
            'cnpj':               re.sub(r'\D', '', self.f_cnpj.value()),
            'inscricao_estadual': self.f_ie.value(),
            'regime_tributario':  self.f_regime.value(),
            'email':              self.f_email.value(),
            'telefone':           self.f_telefone.value(),
        }

# ─── Página 3: Endereço ─────────────────────────────────────────────────────
class PageEndereco(WizardPage):
    def __init__(self):
        super().__init__(
            '📍', 'Endereço da Empresa',
            'Utilizado em notas fiscais e documentos gerados pelo sistema.'
        )
        row1 = QHBoxLayout(); row1.setSpacing(12)
        self.f_cep    = FormField('CEP', mask='00000-000;_')
        self.f_logr   = FormField('Logradouro', 'Rua, Av., etc.')
        self.f_numero = FormField('Número', 'Nº')
        row1.addLayout(self.f_cep, 1)
        row1.addLayout(self.f_logr, 3)
        row1.addLayout(self.f_numero, 1)
        self.content.addLayout(row1)

        row2 = QHBoxLayout(); row2.setSpacing(12)
        self.f_bairro = FormField('Bairro', 'Bairro')
        self.f_cidade = FormField('Cidade', 'Cidade')
        self.f_estado = FormField('UF', combo_items=[
            '','AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS',
            'MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC',
            'SP','SE','TO'
        ])
        row2.addLayout(self.f_bairro, 2)
        row2.addLayout(self.f_cidade, 3)
        row2.addLayout(self.f_estado, 1)
        self.content.addLayout(row2)

        if isinstance(self.f_cep.field_widget, QLineEdit):
            self.f_cep.field_widget.editingFinished.connect(self.consultar_cep)

    def consultar_cep(self):
        cep = re.sub(r'\D', '', self.f_cep.value())
        if len(cep) == 8:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=3)
                data = response.json()
                if "erro" not in data:
                    self.f_logr.set_value(data.get('logradouro', ''))
                    self.f_bairro.set_value(data.get('bairro', ''))
                    self.f_cidade.set_value(data.get('localidade', ''))
                    self.f_estado.set_value(data.get('uf', ''))
                    self.f_numero.field_widget.setFocus() # Pula para o número
            except:
                pass # Falha silenciosa se estiver sem internet

    def get_data(self):
        return {
            'cep':      re.sub(r'\D', '', self.f_cep.value()),
            'logradouro': self.f_logr.value(),
            'numero':   self.f_numero.value(),
            'bairro':   self.f_bairro.value(),
            'cidade':   self.f_cidade.value(),
            'estado':   self.f_estado.value(),
        }


# ─── Página 4: PDV ──────────────────────────────────────────────────────────
class PagePDV(WizardPage):
    def __init__(self):
        super().__init__(
            '🖥️', 'Terminal de Vendas (PDV)',
            'Configure o primeiro terminal. Outros podem ser adicionados depois.'
        )
        self.f_id   = FormField('Identificação', 'Ex: PDV-01 ou CAIXA-01', required=True)
        self.f_desc = FormField('Descrição', 'Ex: Caixa principal — Recepção')
        self.content.addLayout(self.f_id)
        self.content.addLayout(self.f_desc)
        self.f_id.set_value('PDV-01')
        self.f_desc.set_value('Caixa Principal')

    def validate(self):
        if not self.f_id.value():
            self.show_error('Identificação do PDV é obrigatória.')
            return False
        self.hide_error()
        return True

    def get_data(self):
        return {
            'identificacao': self.f_id.value(),
            'descricao':     self.f_desc.value() or self.f_id.value(),
        }


# ─── Página 5: Administrador ────────────────────────────────────────────────
class PageAdmin(WizardPage):
    def __init__(self):
        super().__init__(
            '👤', 'Conta Administrador',
            'Será o primeiro usuário com acesso total ao sistema.'
        )
        row1 = QHBoxLayout(); row1.setSpacing(12)
        self.f_nome  = FormField('Nome Completo', 'Nome para exibição', required=True)
        self.f_login = FormField('Login (usuário)', 'Nome de usuário para entrar', required=True)
        row1.addLayout(self.f_nome, 2)
        row1.addLayout(self.f_login, 1)
        self.content.addLayout(row1)

        self.f_email = FormField('E-mail', 'admin@empresa.com')
        self.content.addLayout(self.f_email)

        row2 = QHBoxLayout(); row2.setSpacing(12)
        self.f_senha   = FormField('Senha', 'Mínimo 6 caracteres', password=True, required=True)
        self.f_confirma= FormField('Confirmar Senha', 'Repita a senha', password=True, required=True)
        row2.addLayout(self.f_senha)
        row2.addLayout(self.f_confirma)
        self.content.addLayout(row2)

    def validate(self):
        if not self.f_nome.value():
            self.show_error('Nome completo é obrigatório.')
            return False
        if not self.f_login.value():
            self.show_error('Login é obrigatório.')
            return False
        if len(self.f_senha.value()) < 6:
            self.show_error('Senha deve ter pelo menos 6 caracteres.')
            return False
        if self.f_senha.value() != self.f_confirma.value():
            self.show_error('As senhas não coincidem.')
            return False
        if self.f_email.value() and not self.validar_email(self.f_email.value()):
            self.show_error('O formato do e-mail informado é inválido.')
            return False
        self.hide_error()
        return True
    
    def validar_email(self, email):
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        return re.search(regex, email.lower())

    def get_data(self):
        return {
            'nome_completo': self.f_nome.value(),
            'login':         self.f_login.value(),
            'email':         self.f_email.value(),
            'senha':         self.f_senha.value(),
        }


# ─── Página 6: Conclusão ────────────────────────────────────────────────────
class PageConclusao(WizardPage):
    def __init__(self):
        super().__init__(
            '✅', 'Tudo pronto!',
            'Revise o resumo abaixo e clique em Concluir para salvar.'
        )
        self.lbl_resumo = QLabel()
        self.lbl_resumo.setWordWrap(True)
        self.lbl_resumo.setStyleSheet(
            f"background-color:{BG_CARD};border:1px solid {BORDER};"
            f"border-radius:6px;font-size:12px;color:{TEXT};"
            f"padding:14px;line-height:1.6;"
        )
        self.content.addWidget(self.lbl_resumo)

        self.lbl_salvo = QLabel('✓  Dados salvos com sucesso!')
        self.lbl_salvo.setVisible(False)
        self.lbl_salvo.setAlignment(Qt.AlignCenter)
        self.lbl_salvo.setStyleSheet(
            f"background-color:{SUCCESS_BG};border:1px solid {SUCCESS_BG2};"
            f"border-radius:4px;font-size:13px;font-weight:bold;"
            f"color:{SUCCESS_TEXT};padding:8px;"
        )
        self.content.addWidget(self.lbl_salvo)

    def preencher_resumo(self, empresa, pdv, admin):
        regime = empresa.get('regime_tributario', '')
        cidade = empresa.get('cidade', '')
        estado = empresa.get('estado', '')
        local  = f"{cidade}/{estado}" if cidade else '—'
        self.lbl_resumo.setText(
            f"<b>Empresa:</b>  {empresa.get('razao_social', '—')}<br>"
            f"<b>CNPJ:</b>  {empresa.get('cnpj', '—')}<br>"
            f"<b>Regime:</b>  {regime}<br>"
            f"<b>Localização:</b>  {local}<br>"
            f"<br>"
            f"<b>PDV:</b>  {pdv.get('identificacao', '—')}"
            f"  —  {pdv.get('descricao', '')}<br>"
            f"<br>"
            f"<b>Administrador:</b>  {admin.get('nome_completo', '—')}<br>"
            f"<b>Login:</b>  {admin.get('login', '—')}"
        )


# ─── Wizard principal ────────────────────────────────────────────────────────
class SetupWizardView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('CSPdv — Configuração Inicial')
        self.setMinimumSize(780, 620)
        self.setModal(True)
        self.setStyleSheet(f"QDialog{{background-color:{BG};font-family:Arial;}}")

        self._dados_empresa  = {}
        self._dados_pdv      = {}
        self._dados_admin    = {}
        self._finalizado     = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header fixo ──────────────────────────────────────────────────
        header = QFrame()
        header.setMinimumHeight(64)
        header.setMaximumHeight(64)
        header.setStyleSheet(
            f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 #1a3a5a,stop:1 {BG_DARK});"
            f"border-bottom:2px solid {BLUE};}}"
        )
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)

        logo = QLabel('CSPdv')
        logo.setStyleSheet("color:white;font-size:26px;font-weight:bold;letter-spacing:2px;")
        h_layout.addWidget(logo)

        sep = QFrame(); sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color:{BORDER};max-width:1px;")
        h_layout.addWidget(sep)

        tag = QLabel('Configuração Inicial')
        tag.setStyleSheet(f"color:{BLUE};font-size:12px;letter-spacing:1px;")
        h_layout.addWidget(tag)
        h_layout.addStretch()

        # Indicador de etapas
        self.step_labels = []
        step_names = ['Início','Empresa','Endereço','PDV','Admin','Concluir']
        for i, name in enumerate(step_names):
            lbl = QLabel(f'{"●" if i == 0 else "○"}  {name}')
            lbl.setStyleSheet(
                f"font-size:11px;color:{'white' if i == 0 else TEXT_MUTED};"
                f"{'font-weight:bold;' if i == 0 else ''}"
            )
            self.step_labels.append(lbl)
            h_layout.addWidget(lbl)
            if i < len(step_names) - 1:
                arr = QLabel('›')
                arr.setStyleSheet(f"font-size:14px;color:{BORDER};")
                h_layout.addWidget(arr)

        root.addWidget(header)

        # Barra de progresso fina
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(4)
        self.progress.setRange(0, 5)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            f"QProgressBar{{border:none;background-color:{BG_DARK};}}"
            f"QProgressBar::chunk{{background:{BLUE};border-radius:0px;}}"
        )
        root.addWidget(self.progress)

        # ── Páginas ──────────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color:{BG};")
        self.pages = [
            PageBoasVindas(),
            PageEmpresa(),
            PageEndereco(),
            PagePDV(),
            PageAdmin(),
            PageConclusao(),
        ]
        for page in self.pages:
            self.stack.addWidget(page)
        root.addWidget(self.stack)

        # ── Rodapé ───────────────────────────────────────────────────────
        footer = QFrame()
        footer.setMinimumHeight(68)
        footer.setMaximumHeight(68)
        footer.setStyleSheet(
            f"QFrame{{background-color:{BG_DARK};"
            f"border-top:1px solid {BORDER};}}"
        )
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 0, 24, 0)
        f_layout.setSpacing(12)

        self.lbl_status = QLabel('Pronto.')
        self.lbl_status.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;")
        f_layout.addWidget(self.lbl_status)
        f_layout.addStretch()

        self.btn_voltar = QPushButton('◀  Voltar')
        self.btn_voltar.setStyleSheet(_btn_secondary())
        self.btn_voltar.setMinimumSize(120, 40)
        self.btn_voltar.setVisible(False)

        self.btn_avancar = QPushButton('Avançar  ▶')
        self.btn_avancar.setStyleSheet(_btn_primary())
        self.btn_avancar.setMinimumSize(140, 40)

        f_layout.addWidget(self.btn_voltar)
        f_layout.addWidget(self.btn_avancar)
        root.addWidget(footer)

        # ── Sinais ───────────────────────────────────────────────────────
        self.btn_avancar.clicked.connect(self._avancar)
        self.btn_voltar.clicked.connect(self._voltar)

        self._current = 0

    # ── Navegação ────────────────────────────────────────────────────────────
    def _avancar(self):
        page = self.pages[self._current]

        if not page.validate():
            return

        # Última página → salvar
        if self._current == len(self.pages) - 1:
            self._salvar()
            return

        self._current += 1
        self.stack.setCurrentIndex(self._current)
        self._atualizar_ui()

        # Preencher resumo ao chegar na última página
        if self._current == len(self.pages) - 1:
            self._dados_empresa = {
                **self.pages[1].get_data(),
                **self.pages[2].get_data(),
            }
            self._dados_pdv   = self.pages[3].get_data()
            self._dados_admin = self.pages[4].get_data()
            self.pages[5].preencher_resumo(
                self._dados_empresa, self._dados_pdv, self._dados_admin
            )

    def _voltar(self):
        if self._current > 0:
            self._current -= 1
            self.stack.setCurrentIndex(self._current)
            self._atualizar_ui()

    def _atualizar_ui(self):
        i = self._current
        n = len(self.pages)

        self.progress.setValue(i)
        self.btn_voltar.setVisible(i > 0)

        if i == n - 1:
            self.btn_avancar.setText('✓  Concluir')
        elif i == 0:
            self.btn_avancar.setText('Começar  ▶')
        else:
            self.btn_avancar.setText('Avançar  ▶')

        for j, lbl in enumerate(self.step_labels):
            name = lbl.text().split('  ', 1)[1] if '  ' in lbl.text() else lbl.text()
            if j == i:
                lbl.setText(f'●  {name}')
                lbl.setStyleSheet(
                    f"font-size:11px;color:white;font-weight:bold;"
                )
            elif j < i:
                lbl.setText(f'✓  {name}')
                lbl.setStyleSheet(f"font-size:11px;color:{BLUE};")
            else:
                lbl.setText(f'○  {name}')
                lbl.setStyleSheet(f"font-size:11px;color:{TEXT_MUTED};")

    def _salvar(self):
        self.btn_avancar.setEnabled(False)
        self.btn_voltar.setEnabled(False)
        self.lbl_status.setText('Salvando...')

        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            SetupModel.salvar_tudo(
                self._dados_empresa,
                self._dados_pdv,
                self._dados_admin,
            )
            self._finalizado = True
            self.pages[5].lbl_salvo.setVisible(True)
            self.lbl_status.setText('Configuração concluída!')
            self.btn_avancar.setText('Ir para o Login  →')
            self.btn_avancar.setEnabled(True)
            self.btn_avancar.clicked.disconnect()
            self.btn_avancar.clicked.connect(self.accept)

        except Exception as e:
            self.lbl_status.setText('Erro ao salvar.')
            self.pages[5].show_error(f'Erro ao salvar: {e}')
            self.btn_avancar.setEnabled(True)
            self.btn_voltar.setEnabled(True)

    def foi_concluido(self) -> bool:
        return self._finalizado
