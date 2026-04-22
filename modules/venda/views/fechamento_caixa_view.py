from PyQt5.QtWidgets import QWidget

from ui.venda.tela_fechamento_caixa import Ui_TelaFechamentoCaixa


class FechamentoCaixaView(QWidget, Ui_TelaFechamentoCaixa):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
