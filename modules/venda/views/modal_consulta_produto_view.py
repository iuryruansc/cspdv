from PyQt5.QtWidgets import QDialog

from ui.venda.modal_consulta_produto import Ui_ModalConsultaProduto


class ModalConsultaProdutoView(QDialog, Ui_ModalConsultaProduto):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.btnFechar.clicked.connect(self.reject)
