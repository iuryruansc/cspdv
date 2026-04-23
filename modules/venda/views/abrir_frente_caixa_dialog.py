from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from modules.venda.views.abertura_caixa_view import AberturaCaixaView


class AbrirFrenteCaixaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Abrir Frente de Caixa")
        self.setModal(True)
        self.resize(1100, 720)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.caixa_data = None

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)

        self.abertura_view = AberturaCaixaView(self)
        self.abertura_view.caixa_aberto.connect(self._on_caixa_aberto)
        self.layout_principal.addWidget(self.abertura_view)

    def _on_caixa_aberto(self, caixa_data: dict) -> None:
        self.caixa_data = caixa_data
        self.accept()
