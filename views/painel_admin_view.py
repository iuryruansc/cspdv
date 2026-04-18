import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.uic import loadUi
from views.login_view import LoginView

UI_DIR = os.path.join(os.path.dirname(__file__), '..', 'ui')

class PainelAdminView(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(os.path.join(UI_DIR, 'admin','PainelAdmin.ui'), self)

        # Define o nome do operador logado
        if LoginView.usuario_logado:
            self.lblOperadorInfo.setText(f"Operador: {LoginView.usuario_logado['nome'].upper()}")
            self.lblStatusBar.setText(f"CSPdv - Operador: {LoginView.usuario_logado['nome'].upper()}  |  Painel Administrativo")
        else:
            self.lblOperadorInfo.setText("Operador: Não logado")
            self.lblStatusBar.setText("CSPdv - Painel Administrativo")

        # Atualiza a data e hora dinamicamente
        self._update_datetime()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000)  # Atualiza a cada segundo

        self.btnSair.clicked.connect(self._exit)

    def _update_datetime(self):
        current = QDateTime.currentDateTime()
        self.lblDataHora.setText(current.toString("dd/MM/yyyy  hh:mm:ss"))

    def _exit(self):
        from views.selecao_modo_view import SelecaoModoView
        self.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()