from PyQt5.QtWidgets import QWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from ui.login.selecao_modo import Ui_SelecaoModo
from views.login.login_view import LoginView

class SelecaoModoView(QWidget, Ui_SelecaoModo):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._configurar_atalhos()
        self._conectar_eventos()
        self._verificar_acessos()

        if LoginView.usuario_logado:
            nome = LoginView.usuario_logado.get('nome', 'Utilizador').upper()
            self.lblOperadorNome.setText(f"OPERADOR: {nome}")
        else:
            self.lblOperadorNome.setText("OPERADOR: NÃO LOGADO")

    def _configurar_atalhos(self):
        self.shortcut_f1 = QShortcut(QKeySequence("F1"), self)
        self.shortcut_f1.activated.connect(self._open_pdv)

        self.shortcut_f2 = QShortcut(QKeySequence("F2"), self)
        self.shortcut_f2.activated.connect(self._open_painel_admin)

        self.shortcut_f3 = QShortcut(QKeySequence("F3"), self)
        self.shortcut_f3.activated.connect(self._open_estoque)

        self.shortcut_f4 = QShortcut(QKeySequence("F4"), self)
        self.shortcut_f4.activated.connect(self._open_financeiro)

        self.shortcut_f5 = QShortcut(QKeySequence("F5"), self)
        self.shortcut_f5.activated.connect(self._open_relatorios)
        
        self.shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_esc.activated.connect(self._exit)

    def _conectar_eventos(self):
        self.btnFrenteCaixa.clicked.connect(self._open_pdv)
        self.btnPainelAdmin.clicked.connect(self._open_painel_admin)
        self.btnEstoque.clicked.connect(self._open_estoque)
        self.btnFinanceiro.clicked.connect(self._open_financeiro)
        self.btnRelatorios.clicked.connect(self._open_relatorios)
        self.btnSairSessao.clicked.connect(self._exit)


    # Permissões e Visibilidade

    def _tem_permissao(self, chave_requerida):
        if not LoginView.usuario_logado:
            return False
        permissoes = LoginView.usuario_logado.get('permissoes', [])
        if 'sistema.master' in permissoes:
            return True
        return chave_requerida in permissoes
        
    def _verificar_acessos(self):
        controles = [
            ('vendas.pdv',        [self.btnFrenteCaixa, self.lblFrenteCaixa, self.shortcut_f1]),
            ('sistema.master',    [self.btnPainelAdmin, self.lblPainelAdmin, self.shortcut_f2]),
            ('estoque.gerenciar', [self.btnEstoque, self.lblEstoque, self.shortcut_f3]),
            ('financeiro.total',  [self.btnFinanceiro, self.lblFinanceiro, self.shortcut_f4]),
            ('relatorios.ver',    [self.btnRelatorios, self.lblRelatorios, self.shortcut_f5]),
        ]

        for chave, objetos in controles:
            tem_acesso = self._tem_permissao(chave)
            for obj in objetos:
                if hasattr(obj, 'setVisible'):
                    obj.setVisible(tem_acesso)
                elif hasattr(obj, 'setEnabled'):
                    obj.setEnabled(tem_acesso)

    # Navegação

    def _open_pdv(self):
        if not self._tem_permissao('vendas.pdv'): return
        print("Abrir Frente de Caixa...")

    def _open_painel_admin(self):
        if not self._tem_permissao('sistema.master'): return
        from views.admin.painel_admin_view import PainelAdminView
        self.hide()
        self.painel_admin = PainelAdminView()
        self.painel_admin.show()

    def _open_estoque(self):
        if not self._tem_permissao('estoque.gerenciar'): return
        print("Abrir Gestão de Estoque...")

    def _open_financeiro(self):
        if not self._tem_permissao('financeiro.total'): return
        print("Abrir Financeiro...")

    def _open_relatorios(self):
        if not self._tem_permissao('relatorios.ver'): return
        print("Abrir Relatórios...")
        
    def _exit(self):
        LoginView.usuario_logado = None
        self.hide()
        from views.login.login_view import LoginView as LV
        self.login = LV()
        self.login.show()