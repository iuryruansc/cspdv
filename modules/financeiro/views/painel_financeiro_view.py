from PyQt5.QtWidgets import QMainWindow

from ui.financeiro.painel_financeiro import Ui_PainelFinanceiro
from utils.operational_panel_mixin import PainelOperacionalMixin

class PainelFinanceiroView(QMainWindow, Ui_PainelFinanceiro, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
