from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from modules.venda.views.movimentacao_caixa_view import MovimentacaoCaixaView
from ui.venda.movimentacao_caixa_dialog import Ui_MovimentacaoCaixaDialog

class MovimentacaoCaixaDialog(QDialog, Ui_MovimentacaoCaixaDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.movimentacao_view = MovimentacaoCaixaView(self)
        self.movimentacao_view.movimentacao_registrada.connect(self.accept)
        self.contentLayout.addWidget(self.movimentacao_view)
