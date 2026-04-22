import os

from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtWidgets import QMainWindow

from core.session_manager import SessionManager
from ui.financeiro.painel_financeiro import Ui_PainelFinanceiro

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "ui")

class PainelFinanceiroView(QMainWindow, Ui_PainelFinanceiro):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        usuario = SessionManager.current_user()
        if usuario:
            nome = usuario["nome"].upper()
            self.lblOperadorInfo.setText(f"Operador: {nome}")
        else:
            self.lblOperadorInfo.setText("Operador: Nao logado")

        self._update_datetime()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000)

        self.btnVoltarSelecao.clicked.connect(self._exit)

    def _update_datetime(self):
        current = QDateTime.currentDateTime()
        self.lblDataHora.setText(current.toString("dd/MM/yyyy  hh:mm:ss"))

    def _exit(self):
        from modules.auth.views.selecao_modo_view import SelecaoModoView

        self.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()
