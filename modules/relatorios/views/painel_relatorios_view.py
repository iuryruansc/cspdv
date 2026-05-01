from PyQt5.QtWidgets import QMainWindow

from ui.relatorios.painel_relatorios import Ui_PainelRelatorios
from utils.operational_panel_mixin import PainelOperacionalMixin

class PainelRelatoriosView(QMainWindow, Ui_PainelRelatorios, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._configurar_tamanho_responsivo()
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
