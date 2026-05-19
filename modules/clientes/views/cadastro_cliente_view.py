from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt5.QtWidgets import QCheckBox, QLineEdit, QPlainTextEdit, QWidget

from modules.clientes.models.cliente_model import ClienteModel
from modules.clientes.services.cliente_service import ClienteService
from ui.admin.cadastros.cadastro_cliente import Ui_CadastroCliente
from utils.format_utils import formatar_cep, formatar_telefone
from utils.admin_return_mixin import RetornoPainelAdminMixin
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import email_valido, somente_digitos, texto_limpo, texto_maiusculo
from utils.ui_messages import mostrar_aviso, mostrar_campos_invalidos, mostrar_info

class CadastroClienteView(QWidget, Ui_CadastroCliente, ValidacaoFormMixin, RetornoPainelAdminMixin):
    def __init__(self, parent=None, cliente_id=None, admin_view=None):
        super().__init__(None)
        self.setupUi(self)
        self._cliente_id = int(cliente_id) if cliente_id is not None else None
        self._cliente_sistema = False
        self._parent_admin = admin_view

        self._configurar_validadores()
        self.registrar_estilos(
            [
                self.lineEditNome,
                self.lineEditCpf,
                self.lineEditTelefone,
                self.lineEditEmail,
                self.lineEditLogradouro,
                self.lineEditNumero,
                self.lineEditBairro,
                self.lineEditCep,
                self.lineEditCidade,
                self.lineEditEstado,
            ]
        )
        self.conectar_limpeza_em_tempo_real()

        self.lineEditTelefone.editingFinished.connect(
            lambda: self.lineEditTelefone.setText(formatar_telefone(self.lineEditTelefone.text()))
        )
        self.lineEditCep.editingFinished.connect(
            lambda: self.lineEditCep.setText(formatar_cep(self.lineEditCep.text()))
        )

        self.btnSalvar.clicked.connect(self._save_cliente)
        self.btnVoltar.clicked.connect(self._cancelar)
        self.btnLimpar.clicked.connect(self._limpar_campos)

        self._configurar_modo()

    def _configurar_validadores(self):
        validador_cpf = QRegularExpressionValidator(
            QRegularExpression(r"^[0-9.\-]{0,14}$"), self
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

        self.lineEditNome.setMaxLength(255)
        self.lineEditCpf.setValidator(validador_cpf)
        self.lineEditCpf.setMaxLength(14)
        self.lineEditTelefone.setValidator(validador_telefone)
        self.lineEditTelefone.setInputMask("(00) 00000-0000;_")
        self.lineEditEmail.setValidator(validador_email)
        self.lineEditEmail.setMaxLength(255)
        self.lineEditLogradouro.setMaxLength(50)
        self.lineEditNumero.setValidator(QIntValidator(0, 999999, self))
        self.lineEditNumero.setMaxLength(6)
        self.lineEditBairro.setMaxLength(45)
        self.lineEditCep.setValidator(validador_cep)
        self.lineEditCep.setInputMask("00000-000;_")
        self.lineEditCidade.setMaxLength(45)
        self.lineEditEstado.setMaxLength(2)

    def _configurar_modo(self):
        if self._cliente_id is None:
            self.lineEditCodigo.setText("Auto-gerado")
            return

        cliente = ClienteModel.buscar_por_id(self._cliente_id)
        if not cliente:
            mostrar_aviso(self, "Cliente não encontrado", "Não foi possível carregar o cliente para edição.")
            self._cancelar()
            return

        self.lblBadge.setText("EDICAO DE CLIENTE")
        self.lblTabCadCliente.setText("Edicao de Cliente")
        self.lineEditCodigo.setText(str(cliente.get("id") or ""))
        self.lineEditNome.setText(str(cliente.get("nome") or ""))
        self.lineEditCpf.setText(str(cliente.get("cpf") or ""))
        self.lineEditTelefone.setText(str(cliente.get("telefone") or ""))
        self.lineEditEmail.setText(str(cliente.get("email") or ""))
        self.lineEditLogradouro.setText(str(cliente.get("logradouro") or ""))
        self.lineEditNumero.setText("" if cliente.get("numero") is None else str(cliente.get("numero")))
        self.lineEditBairro.setText(str(cliente.get("bairro") or ""))
        self.lineEditCep.setText(str(cliente.get("cep") or ""))
        self.lineEditCidade.setText(str(cliente.get("cidade") or ""))
        self.lineEditEstado.setText(str(cliente.get("estado") or ""))
        self.plainTextObservacao.setPlainText(str(cliente.get("observacao") or ""))
        self.checkBoxAtivo.setChecked(str(cliente.get("ativo") or "N").upper() == "S")
        self.btnSalvar.setText("Atualizar")
        self._cliente_sistema = str(cliente.get("cliente_sistema") or "N").strip().upper() == "S"
        if self._cliente_sistema:
            self._configurar_modo_somente_leitura()

    def _configurar_modo_somente_leitura(self):
        self.lblBadge.setText("REGISTRO DO SISTEMA")
        self.lblTabCadCliente.setText("Cliente do Sistema")
        self.btnSalvar.setEnabled(False)
        self.btnSalvar.setText("Protegido")
        self.btnLimpar.setEnabled(False)

        for campo in self.findChildren(QLineEdit):
            campo.setReadOnly(True)

        for campo in self.findChildren(QPlainTextEdit):
            campo.setReadOnly(True)

        for campo in self.findChildren(QCheckBox):
            campo.setEnabled(False)

    def _coletar_dados(self):
        nome = texto_maiusculo(self.lineEditNome.text())
        cpf = somente_digitos(texto_limpo(self.lineEditCpf.text()))
        telefone = somente_digitos(texto_limpo(self.lineEditTelefone.text()))
        email = texto_limpo(self.lineEditEmail.text()).lower()
        logradouro = texto_maiusculo(self.lineEditLogradouro.text())
        numero = texto_limpo(self.lineEditNumero.text())
        bairro = texto_maiusculo(self.lineEditBairro.text())
        cep = somente_digitos(texto_limpo(self.lineEditCep.text()))
        cidade = texto_maiusculo(self.lineEditCidade.text())
        estado = texto_maiusculo(self.lineEditEstado.text())
        observacao = self.plainTextObservacao.toPlainText().strip()
        ativo = "S" if self.checkBoxAtivo.isChecked() else "N"

        erros = []
        if not nome:
            erros.append("Nome: preencha o nome principal do cliente.")
            self.marcar_invalido(self.lineEditNome)
        if email and not email_valido(email):
            erros.append("E-mail: informe um endereco valido.")
            self.marcar_invalido(self.lineEditEmail)
        if cpf and len(cpf) != 11:
            erros.append("CPF: informe os 11 digitos.")
            self.marcar_invalido(self.lineEditCpf)
        if telefone and len(telefone) not in (10, 11):
            erros.append("Telefone: informe DDD e numero completos.")
            self.marcar_invalido(self.lineEditTelefone)
        if cep and len(cep) != 8:
            erros.append("CEP: informe os 8 digitos do CEP.")
            self.marcar_invalido(self.lineEditCep)
        if estado and len(estado) != 2:
            erros.append("Estado: use a sigla da UF com 2 letras.")
            self.marcar_invalido(self.lineEditEstado)

        if erros:
            mostrar_campos_invalidos(
                self,
                erros,
                cabecalho="Preencha os seguintes campos:",
            )
            return None

        return {
            "nome": nome,
            "cpf": cpf,
            "telefone": telefone,
            "email": email,
            "logradouro": logradouro,
            "numero": int(numero) if numero else None,
            "bairro": bairro,
            "cep": cep,
            "cidade": cidade,
            "estado": estado,
            "observacao": observacao,
            "ativo": ativo,
        }

    def _save_cliente(self):
        if self._cliente_sistema:
            mostrar_aviso(
                self,
                "Registro protegido",
                "O cliente Consumidor Final e um registro do sistema e nao pode ser editado.",
            )
            return

        self.limpar_erros()
        dados = self._coletar_dados()
        if dados is None:
            return

        if self._cliente_id is None:
            sucesso, mensagem = ClienteService.cadastrar_cliente(dados)
        else:
            sucesso, mensagem = ClienteService.atualizar_cliente(self._cliente_id, dados)

        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            if self._cliente_id is None:
                self._limpar_campos()
            else:
                self._cancelar(refresh=True)
            return

        mostrar_aviso(self, "Atenção", mensagem)

    def _limpar_campos(self):
        for campo_texto in self.findChildren(QLineEdit):
            if campo_texto.objectName() != "lineEditCodigo":
                campo_texto.clear()

        self.limpar_erros()
        self.checkBoxAtivo.setChecked(True)
        self.plainTextObservacao.clear()
        self.lineEditNome.setFocus()

    def _cancelar(self, refresh=False):
        self.hide()
        self._mostrar_painel_admin(refresh=refresh)

    def closeEvent(self, a0):
        super().closeEvent(a0)
        self._mostrar_painel_admin()
