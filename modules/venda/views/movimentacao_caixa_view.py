from PyQt5.QtWidgets import QWidget

from ui.venda.tela_movimentacao_caixa import Ui_TelaMovimentacaoCaixa


class MovimentacaoCaixaView(QWidget, Ui_TelaMovimentacaoCaixa):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
