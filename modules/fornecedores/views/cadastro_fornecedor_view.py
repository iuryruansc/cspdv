import os

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt5.QtWidgets import QLineEdit, QMessageBox, QWidget

from modules.fornecedores.services.fornecedor_service import FornecedorService
from ui.admin.cadastros.cadastro_fornecedor import Ui_CadastroFornecedor
from utils.format_utils import formatar_cpf_cnpj, formatar_cep, formatar_telefone
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import email_valido, somente_digitos, texto_limpo, texto_maiusculo

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "ui")

class CadastroFornecedorView(QWidget, Ui_CadastroFornecedor, ValidacaoFormMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._configurar_validadores()
        self.registrar_estilos([
            self.lineEditNomeFantasia,
            self.lineEditRazaoSocial,
            self.lineEditCnpjCpf,
            self.lineEditIe,
            self.lineEditTelefone,
            self.lineEditEmail,
            self.lineEditLogradouro,
            self.lineEditNumero,
            self.lineEditCep,
            self.lineEditCidade,
            self.lineEditEstado,
            self.lineEditBairro,
        ])
        self.conectar_limpeza_em_tempo_real()

        self.lineEditCnpjCpf.editingFinished.connect(
            lambda: self.lineEditCnpjCpf.setText(formatar_cpf_cnpj(self.lineEditCnpjCpf.text()))
        )
        self.lineEditTelefone.editingFinished.connect(
            lambda: self.lineEditTelefone.setText(formatar_telefone(self.lineEditTelefone.text()))
        )
        self.lineEditCep.editingFinished.connect(
            lambda: self.lineEditCep.setText(formatar_cep(self.lineEditCep.text()))
        )

        self.btnSalvar.clicked.connect(self._save_fornecedor)
        self.btnVoltar.clicked.connect(self._back_to_painel)
        self.btnLimpar.clicked.connect(self._limpar_campos)

    def _configurar_validadores(self):
        validador_documento = QRegularExpressionValidator(
            QRegularExpression(r"^[0-9.\-\/]{0,18}$"), self
        )
        validador_ie = QRegularExpressionValidator(
            QRegularExpression(r"^[0-9A-Za-z.\-]{0,20}$"), self
        )
        validador_telefone = QRegularExpressionValidator(
            QRegularExpression(r"^[0-9()\-\s+]{0,20}$"), self
        )
        validador_cep = QRegularExpressionValidator(
            QRegularExpression(r"^[0-9\-]{0,9}$"), self
        )
        validador_email = QRegularExpressionValidator(
            QRegularExpression(r"^[A-Za-z0-9._%+\-@]{0,120}$"), self
        )
        validador_numero = QIntValidator(0, 999999, self)

        self.lineEditNomeFantasia.setMaxLength(120)
        self.lineEditRazaoSocial.setMaxLength(150)
        self.lineEditCnpjCpf.setValidator(validador_documento)
        self.lineEditIe.setValidator(validador_ie)
        self.lineEditTelefone.setValidator(validador_telefone)
        self.lineEditEmail.setValidator(validador_email)
        self.lineEditEmail.setMaxLength(120)
        self.lineEditLogradouro.setMaxLength(150)
        self.lineEditNumero.setValidator(validador_numero)
        self.lineEditNumero.setMaxLength(6)
        self.lineEditCep.setValidator(validador_cep)
        self.lineEditCep.setInputMask("00000-000;_")
        self.lineEditBairro.setMaxLength(80)
        self.lineEditCidade.setMaxLength(80)
        self.lineEditEstado.setMaxLength(2)
        self.lineEditTelefone.setInputMask("(00) 00000-0000;_")

    def _save_fornecedor(self):
        self.limpar_erros()

        nome = texto_maiusculo(self.lineEditNomeFantasia.text())
        razao_social = texto_maiusculo(self.lineEditRazaoSocial.text())
        cnpj_cpf = somente_digitos(texto_limpo(self.lineEditCnpjCpf.text()))
        ie = somente_digitos(texto_limpo(self.lineEditIe.text()))
        telefone = somente_digitos(texto_limpo(self.lineEditTelefone.text()))
        email = texto_limpo(self.lineEditEmail.text()).lower()
        logradouro = texto_maiusculo(self.lineEditLogradouro.text())
        numero = texto_limpo(self.lineEditNumero.text())
        cep = somente_digitos(texto_limpo(self.lineEditCep.text()))
        cidade = texto_maiusculo(self.lineEditCidade.text())
        estado = texto_maiusculo(self.lineEditEstado.text())
        bairro = texto_maiusculo(self.lineEditBairro.text())
        ativo = "S" if self.checkBoxAtivo.isChecked() else "N"
        observacao = self.plainTextObservacao.toPlainText().strip()

        erros = []
        if not nome:
            erros.append("Nome Fantasia: preencha o nome principal do fornecedor.")
            self.marcar_invalido(self.lineEditNomeFantasia)
        if email and not email_valido(email):
            erros.append("E-mail: informe um endereco valido, como contato@empresa.com.")
            self.marcar_invalido(self.lineEditEmail)
        if cep and len(cep) != 8:
            erros.append("CEP: informe os 8 digitos do CEP.")
            self.marcar_invalido(self.lineEditCep)
        if cnpj_cpf and len(cnpj_cpf) not in (11, 14):
            erros.append("CPF/CNPJ: use 11 digitos para CPF ou 14 para CNPJ.")
            self.marcar_invalido(self.lineEditCnpjCpf)
        if telefone and len(telefone) not in (10, 11):
            erros.append("Telefone: informe DDD e numero completos.")
            self.marcar_invalido(self.lineEditTelefone)
        if estado and len(estado) != 2:
            erros.append("Estado: use a sigla da UF com 2 letras.")
            self.marcar_invalido(self.lineEditEstado)

        if erros:
            QMessageBox.warning(
                self,
                "Revise os campos",
                "Preencha os seguintes campos:\n" + "\n".join(erros),
            )
            return

        try:
            dados = {
                "nome_fantasia": nome,
                "razao_social": razao_social,
                "cnpj_cpf": cnpj_cpf,
                "ie": ie,
                "telefone": telefone,
                "email": email,
                "logradouro": logradouro,
                "numero": numero,
                "cep": cep,
                "cidade": cidade,
                "estado": estado,
                "bairro": bairro,
                "ativo": ativo,
                "observacao": observacao,
            }
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao coletar dados: {e}")
            return

        sucesso, mensagem = FornecedorService.cadastrar_fornecedor(dados)
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self._limpar_campos()
        else:
            QMessageBox.warning(self, "Atencao", mensagem)

    def _limpar_campos(self):
        for campo_texto in self.findChildren(QLineEdit):
            if campo_texto.objectName() != "lineEditCodigo":
                campo_texto.clear()

        self.limpar_erros()
        self.checkBoxAtivo.setChecked(True)
        self.plainTextObservacao.clear()

    def _back_to_painel(self):
        from modules.admin.views.painel_admin_view import PainelAdminView

        self.hide()
        self.painel_admin = PainelAdminView()
        self.painel_admin.show()
