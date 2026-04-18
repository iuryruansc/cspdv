from PyQt5.QtWidgets import QWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from views.login.SelecaoModo import Ui_SelecaoModo
from views.login_view import LoginView

class SelecaoModoView(QWidget, Ui_SelecaoModo):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

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