from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from modules.venda.views.abertura_caixa_view import AberturaCaixaView
from ui.venda.abrir_frente_caixa_dialog import Ui_AbrirFrenteCaixaDialog

class AbrirFrenteCaixaDialog(QDialog, Ui_AbrirFrenteCaixaDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.caixa_data = None

        self.abertura_view = AberturaCaixaView(self)
        self.abertura_view.caixa_aberto.connect(self._on_caixa_aberto)
        self.contentLayout.addWidget(self.abertura_view)

    def _on_caixa_aberto(self, caixa_data: dict) -> None:
        self.caixa_data = caixa_data
        self.accept()
