from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox

from modules.marcas.services.marca_service import MarcaService
from ui.admin.cadastros.cadastro_marca import Ui_CadastroMarca
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import texto_limpo, texto_maiusculo

class CadastroMarcaView(QDialog, Ui_CadastroMarca, ValidacaoFormMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)

        self.registrar_estilos([self.lineEditNomeMarca])
        self.conectar_limpeza_em_tempo_real()

        self.btnSalvar.clicked.connect(self._salvar_marca)
        self.btnVoltar.clicked.connect(self.reject)
        self.btnLimpar.clicked.connect(self._limpar_campos)

    def _salvar_marca(self):
        self.limpar_erros()

        nome_marca = texto_maiusculo(texto_limpo(self.lineEditNomeMarca.text()))
        ativo = "S" if self.checkBoxAtivo.isChecked() else "N"

        if not nome_marca:
            self.marcar_invalido(self.lineEditNomeMarca)
            QMessageBox.warning(
                self,
                "Revise os campos",
                "Nome da Marca: preencha o nome principal da marca.",
            )
            return

        dados = {
            "nome_marca": nome_marca,
            "ativo": ativo,
        }

        sucesso, mensagem = MarcaService.cadastrar_marca(dados)
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.accept()
            return

        if "nome da marca" in mensagem.lower():
            self.marcar_invalido(self.lineEditNomeMarca)

        QMessageBox.warning(self, "Atencao", mensagem)

    def _limpar_campos(self):
        self.limpar_erros()
        self.lineEditNomeMarca.clear()
        self.checkBoxAtivo.setChecked(True)
        self.lineEditNomeMarca.setFocus()
