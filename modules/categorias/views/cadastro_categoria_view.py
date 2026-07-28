from __future__ import annotations
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from modules.categorias.models.categoria_model import CategoriaModel
from modules.categorias.services.categoria_service import CategoriaService
from ui.admin.cadastros.cadastro_categoria import Ui_CadastroCategoria
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import texto_limpo, texto_maiusculo
from utils.ui_messages import mostrar_aviso, mostrar_campos_invalidos, mostrar_info
from modules.shared.constants import FLAG_NAO, FLAG_SIM, TEXTO_AUTO_GERADO

class CadastroCategoriaView(QDialog, Ui_CadastroCategoria, ValidacaoFormMixin):
    def __init__(self, parent=None, categoria_id=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self._categoria_id = int(categoria_id) if categoria_id is not None else None

        self.registrar_estilos([self.lineEditNomeCategoria])
        self.conectar_limpeza_em_tempo_real()

        self.btnSalvar.clicked.connect(self._salvar_categoria)
        self.btnVoltar.clicked.connect(self.reject)
        self.btnLimpar.clicked.connect(self._limpar_campos)
        self._configurar_modo()

    def _configurar_modo(self):
        if self._categoria_id is None:
            self.lineEditCodigo.setText(TEXTO_AUTO_GERADO)
            return

        categoria = CategoriaModel.buscar_por_id(self._categoria_id)
        if not categoria:
            mostrar_aviso(self, "Categoria não encontrada", "Não foi possível carregar a categoria para edição.")
            self.reject()
            return

        self.lblBadge.setText("EDICAO DE CATEGORIA")
        self.lblTabCadCategoria.setText("Edicao de Categoria")
        self.lineEditCodigo.setText(str(categoria.get("id") or ""))
        self.lineEditNomeCategoria.setText(str(categoria.get("nome") or ""))
        self.checkBoxAtivo.setChecked(str(categoria.get("ativo") or FLAG_NAO).upper() == FLAG_SIM)
        self.btnSalvar.setText("Atualizar")

    def _salvar_categoria(self):
        self.limpar_erros()

        nome = texto_maiusculo(texto_limpo(self.lineEditNomeCategoria.text()))
        ativo = FLAG_SIM if self.checkBoxAtivo.isChecked() else FLAG_NAO

        if not nome:
            self.marcar_invalido(self.lineEditNomeCategoria)
            mostrar_campos_invalidos(
                self,
                ["Nome da Categoria: preencha o nome principal da categoria."],
                cabecalho="Corrija os seguintes pontos:",
            )
            return

        if self._categoria_id is None:
            sucesso, mensagem = CategoriaService.cadastrar_categoria(
                {"nome": nome, "ativo": ativo}
            )
        else:
            sucesso, mensagem = CategoriaService.atualizar_categoria(
                self._categoria_id,
                {"nome": nome, "ativo": ativo},
            )
        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
            return

        if "nome da categoria" in mensagem.lower():
            self.marcar_invalido(self.lineEditNomeCategoria)

        mostrar_aviso(self, "Atenção", mensagem)

    def _limpar_campos(self):
        self.limpar_erros()
        self.lineEditNomeCategoria.clear()
        self.checkBoxAtivo.setChecked(True)
        self.lineEditNomeCategoria.setFocus()
