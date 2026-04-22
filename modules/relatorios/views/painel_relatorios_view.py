import os

from PyQt5.QtWidgets import QMainWindow

from core.session_manager import SessionManager
from ui.relatorios.painel_relatorios import Ui_PainelRelatorios

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "ui")

class PainelRelatoriosView(QMainWindow, Ui_PainelRelatorios):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        usuario = SessionManager.current_user()
        if usuario:
            nome = usuario["nome"].upper()
            self.lblOperadorInfo.setText(f"Operador: {nome}")
        else:
            self.lblOperadorInfo.setText("Operador: Nao logado")

        self.btnVoltarSelecao.clicked.connect(self._exit)

    def _exit(self):
        from modules.auth.views.selecao_modo_view import SelecaoModoView

        self.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()
