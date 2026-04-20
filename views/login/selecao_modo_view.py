from PyQt5.QtWidgets import QWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from ui.login.selecao_modo import Ui_SelecaoModo
from views.login.login_view import LoginView

class SelecaoModoView(QWidget, Ui_SelecaoModo):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._verificar_acessos()

        # Define o nome do operador logado no label
        if LoginView.usuario_logado:
            self.lblOperadorNome.setText(LoginView.usuario_logado['nome'].upper())
        else:
            self.lblOperadorNome.setText("Não logado")

        self.btnSairSessao.clicked.connect(self._exit)

        self.btnPainelAdmin.clicked.connect(self._open_painel_admin)
        self.shortcut_f2 = QShortcut(QKeySequence("F2"), self)
        self.shortcut_f2.activated.connect(self._open_painel_admin)

    def _tem_permissao(self, chave_requerida):
        if not LoginView.usuario_logado:
            return False

        permissoes = LoginView.usuario_logado.get('permissoes', [])

        if 'sistema.master' in permissoes:
            return True
        
        return chave_requerida in permissoes
        
    def _verificar_acessos(self):
        controles = [
            ('sistema.master', [self.btnPainelAdmin, self.frameCardAdmin]),
            ('vendas.pdv',     [self.btnFrenteCaixa, self.frameCardCaixa]),
            # ('estoque.gerenciar', [self.btnEstoque, self.frameEstoque]),
        ]

        for chave, objetos in controles:
            tem_acesso = self._tem_permissao(chave)

            for obj in objetos:
                if hasattr(obj, 'setVisible'):
                    obj.setVisible(tem_acesso) 
                elif hasattr(obj, 'setEnabled'):
                    obj.setEnabled(tem_acesso)

    def _open_painel_admin(self):
        if not self._tem_permissao('sistema.master'):
            return

        from views.admin.painel_admin_view import PainelAdminView
        self.hide()
        self.painel_admin = PainelAdminView()
        self.painel_admin.show()
        
    def _exit(self):
        LoginView.usuario_logado = None  # Encerra a sessão do usuário atual
        self.hide()
        self.login = LoginView()
        if self.login.exec_() == LoginView.Accepted:
            self.show()
        else:
            self.close()