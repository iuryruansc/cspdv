import os

from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtWidgets import QMainWindow

from services.session_manager import SessionManager
from ui.admin.painel_admin import Ui_PainelAdmin

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "ui")

class PainelAdminView(QMainWindow, Ui_PainelAdmin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        usuario = SessionManager.current_user()
        if usuario:
            nome = usuario["nome"].upper()
            self.lblOperadorInfo.setText(f"Operador: {nome}")
            self.lblStatusBar.setText(f"CSPdv - Operador: {nome}  |  Painel Administrativo")
        else:
            self.lblOperadorInfo.setText("Operador: Nao logado")
            self.lblStatusBar.setText("CSPdv - Painel Administrativo")

        self._update_datetime()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000)

        self.btnAcaoCadProduto.clicked.connect(self._open_cadastro_produto)
        self.btnSair.clicked.connect(self._exit)

    def _open_cadastro_produto(self):
        from views.admin.cadastro.cadastro_produto_view import CadastroProdutoView

        self.hide()
        self.cadastro_produto = CadastroProdutoView()
        self.cadastro_produto.show()

    def _update_datetime(self):
        current = QDateTime.currentDateTime()
        self.lblDataHora.setText(current.toString("dd/MM/yyyy  hh:mm:ss"))

    def _exit(self):
        from views.login.selecao_modo_view import SelecaoModoView

        self.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()
