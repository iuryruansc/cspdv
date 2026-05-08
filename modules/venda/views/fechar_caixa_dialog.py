from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from modules.venda.views.fechamento_caixa_view import FechamentoCaixaView
from ui.venda.fechar_caixa_dialog import Ui_FecharCaixaDialog

class FecharCaixaDialog(QDialog, Ui_FecharCaixaDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.fechamento_data = None

        self.fechamento_view = FechamentoCaixaView(self)
        self.fechamento_view.caixa_fechado.connect(self._on_caixa_fechado)
        self.contentLayout.addWidget(self.fechamento_view)

    def _on_caixa_fechado(self, fechamento_data: dict) -> None:
        self.fechamento_data = fechamento_data
        self.accept()
