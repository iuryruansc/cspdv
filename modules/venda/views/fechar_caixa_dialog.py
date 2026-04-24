from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from modules.venda.views.fechamento_caixa_view import FechamentoCaixaView


class FecharCaixaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fechar Caixa")
        self.setModal(True)
        self.resize(1280, 780)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.fechamento_data = None

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)

        self.fechamento_view = FechamentoCaixaView(self)
        self.fechamento_view.caixa_fechado.connect(self._on_caixa_fechado)
        self.layout_principal.addWidget(self.fechamento_view)

    def _on_caixa_fechado(self, fechamento_data: dict) -> None:
        self.fechamento_data = fechamento_data
        self.accept()
