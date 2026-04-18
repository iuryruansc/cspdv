import os
from PyQt5.QtWidgets import QWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.uic import loadUi
from views.login_view import LoginView

UI_DIR = os.path.join(os.path.dirname(__file__), '..', 'ui')

class SelecaoModoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(os.path.join(UI_DIR, 'login','SelecaoModo.ui'), self)

        # Define o nome do operador logado no label
        if LoginView.usuario_logado:
            self.lblOperadorNome.setText(LoginView.usuario_logado['nome'].upper())
        else:
            self.lblOperadorNome.setText("Não logado")

        self.btnSairSessao.clicked.connect(self._exit)

        self.btnPainelAdmin.clicked.connect(self._open_painel_admin)
        self.shortcut_f2 = QShortcut(QKeySequence("F2"), self)
        self.shortcut_f2.activated.connect(self._open_painel_admin)

    def _open_painel_admin(self):
        from views.painel_admin_view import PainelAdminView
        self.admin = PainelAdminView()
        self.admin.show()
        self.close()

    def _exit(self):
        LoginView.usuario_logado = None  # Encerra a sessão do usuário atual
        self.hide()
        self.login = LoginView()
        if self.login.exec_() == LoginView.Accepted:
            self.show()
        else:
            self.close()