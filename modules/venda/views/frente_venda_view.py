from PyQt5.QtWidgets import QWidget

from ui.venda.frente_venda import Ui_FrenteVenda


class FrenteVendaView(QWidget, Ui_FrenteVenda):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
