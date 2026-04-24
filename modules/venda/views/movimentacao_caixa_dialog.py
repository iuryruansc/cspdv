from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from modules.venda.views.movimentacao_caixa_view import MovimentacaoCaixaView


class MovimentacaoCaixaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Movimentação de Caixa")
        self.setModal(True)
        self.resize(1280, 780)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)

        self.movimentacao_view = MovimentacaoCaixaView(self)
        self.movimentacao_view.movimentacao_registrada.connect(self.accept)
        self.layout_principal.addWidget(self.movimentacao_view)
