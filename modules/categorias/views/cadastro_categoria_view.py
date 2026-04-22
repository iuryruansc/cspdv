from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox

from modules.categorias.services.categoria_service import CategoriaService
from ui.admin.cadastros.cadastro_categoria import Ui_CadastroCategoria
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import texto_limpo, texto_maiusculo

class CadastroCategoriaView(QDialog, Ui_CadastroCategoria, ValidacaoFormMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)

        self.registrar_estilos([self.lineEditNomeCategoria])
        self.conectar_limpeza_em_tempo_real()

        self.btnSalvar.clicked.connect(self._salvar_categoria)
        self.btnVoltar.clicked.connect(self.reject)
        self.btnLimpar.clicked.connect(self._limpar_campos)

    def _salvar_categoria(self):
        self.limpar_erros()

        nome = texto_maiusculo(texto_limpo(self.lineEditNomeCategoria.text()))
        ativo = "S" if self.checkBoxAtivo.isChecked() else "N"

        if not nome:
            self.marcar_invalido(self.lineEditNomeCategoria)
            QMessageBox.warning(
                self,
                "Revise os campos",
                "Nome da Categoria: preencha o nome principal da categoria.",
            )
            return

        sucesso, mensagem = CategoriaService.cadastrar_categoria(
            {"nome": nome, "ativo": ativo}
        )
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.accept()
            return

        if "nome da categoria" in mensagem.lower():
            self.marcar_invalido(self.lineEditNomeCategoria)

        QMessageBox.warning(self, "Atencao", mensagem)

    def _limpar_campos(self):
        self.limpar_erros()
        self.lineEditNomeCategoria.clear()
        self.checkBoxAtivo.setChecked(True)
        self.lineEditNomeCategoria.setFocus()
