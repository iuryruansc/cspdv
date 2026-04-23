from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from modules.marcas.models.marca_model import MarcaModel
from modules.marcas.services.marca_service import MarcaService
from ui.admin.cadastros.cadastro_marca import Ui_CadastroMarca
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import texto_limpo, texto_maiusculo
from utils.ui_messages import mostrar_aviso, mostrar_campos_invalidos, mostrar_info

class CadastroMarcaView(QDialog, Ui_CadastroMarca, ValidacaoFormMixin):
    def __init__(self, parent=None, marca_id=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self._marca_id = int(marca_id) if marca_id is not None else None

        self.registrar_estilos([self.lineEditNomeMarca])
        self.conectar_limpeza_em_tempo_real()

        self.btnSalvar.clicked.connect(self._salvar_marca)
        self.btnVoltar.clicked.connect(self.reject)
        self.btnLimpar.clicked.connect(self._limpar_campos)
        self._configurar_modo()

    def _configurar_modo(self):
        if self._marca_id is None:
            self.lineEditCodigo.setText("Auto-gerado")
            return

        marca = MarcaModel.buscar_por_id(self._marca_id)
        if not marca:
            mostrar_aviso(self, "Marca nao encontrada", "Nao foi possivel carregar a marca para edicao.")
            self.reject()
            return

        self.lblFormTitle.setText("Dados da Marca")
        self.lblBadge.setText("EDICAO DE MARCA")
        self.lblTabCadMarca.setText("Edicao de Marca")
        self.lineEditCodigo.setText(str(marca.get("id") or ""))
        self.lineEditNomeMarca.setText(str(marca.get("nome_marca") or ""))
        self.checkBoxAtivo.setChecked(str(marca.get("ativo") or "N").upper() == "S")
        self.btnSalvar.setText("Atualizar")

    def _salvar_marca(self):
        self.limpar_erros()

        nome_marca = texto_maiusculo(texto_limpo(self.lineEditNomeMarca.text()))
        ativo = "S" if self.checkBoxAtivo.isChecked() else "N"

        if not nome_marca:
            self.marcar_invalido(self.lineEditNomeMarca)
            mostrar_campos_invalidos(
                self,
                ["Nome da Marca: preencha o nome principal da marca."],
                cabecalho="Corrija os seguintes pontos:",
            )
            return

        dados = {
            "nome_marca": nome_marca,
            "ativo": ativo,
        }

        if self._marca_id is None:
            sucesso, mensagem = MarcaService.cadastrar_marca(dados)
        else:
            sucesso, mensagem = MarcaService.atualizar_marca(self._marca_id, dados)
        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
            return

        if "nome da marca" in mensagem.lower():
            self.marcar_invalido(self.lineEditNomeMarca)

        mostrar_aviso(self, "Atencao", mensagem)

    def _limpar_campos(self):
        self.limpar_erros()
        self.lineEditNomeMarca.clear()
        self.checkBoxAtivo.setChecked(True)
        self.lineEditNomeMarca.setFocus()
