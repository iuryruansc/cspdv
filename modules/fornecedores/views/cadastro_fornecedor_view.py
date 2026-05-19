import os

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt5.QtWidgets import QLineEdit, QWidget

from modules.fornecedores.models.fornecedor_model import FornecedorModel
from modules.fornecedores.services.fornecedor_service import FornecedorService
from ui.admin.cadastros.cadastro_fornecedor import Ui_CadastroFornecedor
from utils.admin_return_mixin import RetornoPainelAdminMixin
from utils.format_utils import formatar_cpf_cnpj, formatar_cep, formatar_telefone
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import email_valido, somente_digitos, texto_limpo, texto_maiusculo
from utils.ui_messages import mostrar_aviso, mostrar_campos_invalidos, mostrar_erro, mostrar_info

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "ui")

class CadastroFornecedorView(QWidget, Ui_CadastroFornecedor, ValidacaoFormMixin, RetornoPainelAdminMixin):
    def __init__(self, parent=None, fornecedor_id=None, admin_view=None):
        super().__init__(None)
        self.setupUi(self)
        self._fornecedor_id = int(fornecedor_id) if fornecedor_id is not None else None
        self._parent_admin = admin_view

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
        self.btnVoltar.clicked.connect(self._cancelar)
        self.btnLimpar.clicked.connect(self._limpar_campos)
        self._configurar_modo()

    def _configurar_modo(self):
        if self._fornecedor_id is None:
            self.lineEditCodigo.setText("Auto-gerado")
            return

        fornecedor = FornecedorModel.buscar_por_id(self._fornecedor_id)
        if not fornecedor:
            mostrar_aviso(self, "Fornecedor não encontrado", "Não foi possível carregar o fornecedor para edição.")
            self._cancelar()
            return

        self.lblBadge.setText("EDICAO DE FORNECEDOR")
        self.lblTabCadFornecedor.setText("Edicao de Fornecedor")
        self.lblFormTitle.setText("Dados do Fornecedor")
        self.lineEditCodigo.setText(str(fornecedor.get("id_fornecedor") or ""))
        self.lineEditNomeFantasia.setText(str(fornecedor.get("nome_fantasia") or ""))
        self.lineEditRazaoSocial.setText(str(fornecedor.get("razao_social") or ""))
        self.lineEditCnpjCpf.setText(str(fornecedor.get("cnpj_cpf") or ""))
        self.lineEditIe.setText(str(fornecedor.get("ie") or ""))
        self.lineEditTelefone.setText(str(fornecedor.get("telefone") or ""))
        self.lineEditEmail.setText(str(fornecedor.get("email") or ""))
        self.lineEditLogradouro.setText(str(fornecedor.get("logradouro") or ""))
        self.lineEditNumero.setText(str(fornecedor.get("numero") or ""))
        self.lineEditCep.setText(str(fornecedor.get("cep") or ""))
        self.lineEditCidade.setText(str(fornecedor.get("cidade") or ""))
        self.lineEditEstado.setText(str(fornecedor.get("estado") or ""))
        self.lineEditBairro.setText(str(fornecedor.get("bairro") or ""))
        self.checkBoxAtivo.setChecked(str(fornecedor.get("ativo") or "N").upper() == "S")
        self.plainTextObservacao.setPlainText(str(fornecedor.get("observacao") or ""))
        self.btnSalvar.setText("Atualizar")

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
            mostrar_campos_invalidos(
                self,
                erros,
                cabecalho="Preencha os seguintes campos:",
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
            mostrar_erro(self, "Erro", f"Erro ao coletar dados: {e}")
            return

        if self._fornecedor_id is None:
            sucesso, mensagem = FornecedorService.cadastrar_fornecedor(dados)
        else:
            sucesso, mensagem = FornecedorService.atualizar_fornecedor(self._fornecedor_id, dados)
        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            if self._fornecedor_id is None:
                self._limpar_campos()
            else:
                self._cancelar(refresh=True)
        else:
            mostrar_aviso(self, "Atenção", mensagem)

    def _limpar_campos(self):
        for campo_texto in self.findChildren(QLineEdit):
            if campo_texto.objectName() != "lineEditCodigo":
                campo_texto.clear()

        self.limpar_erros()
        self.checkBoxAtivo.setChecked(True)
        self.plainTextObservacao.clear()

    def _cancelar(self, refresh=False):
        self.hide()
        self._mostrar_painel_admin(refresh=refresh)

    def closeEvent(self, a0):
        super().closeEvent(a0)
        self._mostrar_painel_admin()
