from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut, QWidget

from core.session_manager import SessionManager
from ui.login.selecao_modo import Ui_SelecaoModo
from utils.system_runtime import descricao_ambiente, versao_referencia
from utils.window_size_utils import aplicar_tamanho_proporcional_tela


class SelecaoModoView(QWidget, Ui_SelecaoModo):
    COLUNAS_CARDS = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        aplicar_tamanho_proporcional_tela(self, proporcao_largura=0.88, proporcao_altura=0.86)
        self._configurar_atalhos()
        self._cards_modulos = [
            ("vendas.pdv", self.cardFrenteCaixa, self.shortcut_f1),
            ("sistema.master", self.cardAdmin, self.shortcut_f2),
            ("estoque.gerenciar", self.cardEstoque, self.shortcut_f3),
            ("financeiro.total", self.cardFinanceiro, self.shortcut_f4),
            ("relatorios.ver", self.cardRelatorios, self.shortcut_f5),
        ]
        self._conectar_eventos()
        self._atualizar_operador()
        self.lblVersao.setText(versao_referencia())
        self.lblVersao.setToolTip(descricao_ambiente())
        self._verificar_acessos()

    def _usuario_atual(self):
        return SessionManager.current_user()

    def _atualizar_operador(self):
        usuario = self._usuario_atual()
        if usuario:
            nome = usuario.get("nome", "Utilizador").upper()
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
        self.shortcut_f5.activated.connect(self._open_promocoes)

        self.shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_esc.activated.connect(self._exit)

    def _conectar_eventos(self):
        self.btnFrenteCaixa.clicked.connect(self._open_pdv)
        self.btnPainelAdmin.clicked.connect(self._open_painel_admin)
        self.btnEstoque.clicked.connect(self._open_estoque)
        self.btnFinanceiro.clicked.connect(self._open_financeiro)
        self.btnRelatorios.clicked.connect(self._open_promocoes)
        self.btnSairSessao.clicked.connect(self._exit)

    def _tem_permissao(self, chave_requerida):
        return SessionManager.has_permission(chave_requerida)

    def _verificar_acessos(self):
        cards_visiveis = []

        for chave, card, atalho in self._cards_modulos:
            tem_acesso = self._tem_permissao(chave)
            card.setVisible(tem_acesso)
            atalho.setEnabled(tem_acesso)
            if tem_acesso:
                cards_visiveis.append(card)

        self._reorganizar_cards(cards_visiveis)

    def _reorganizar_cards(self, cards_visiveis):
        for _, card, _ in self._cards_modulos:
            self.layoutContent.removeWidget(card)

        for indice, card in enumerate(cards_visiveis):
            linha = indice // self.COLUNAS_CARDS
            coluna = indice % self.COLUNAS_CARDS
            self.layoutContent.addWidget(card, linha, coluna)

        linha_resumo = len(cards_visiveis) // self.COLUNAS_CARDS
        coluna_resumo = len(cards_visiveis) % self.COLUNAS_CARDS
        self.layoutContent.removeWidget(self.cardResumo)
        self.layoutContent.addWidget(self.cardResumo, linha_resumo, coluna_resumo)

    def _abrir_modulo(self, view_cls, attr_name: str) -> None:
        self.hide()
        view = view_cls()
        setattr(self, attr_name, view)
        view.show()

    def _open_pdv(self):
        if not self._tem_permissao("vendas.pdv"):
            return
        from modules.venda.views.frente_loja_view import FrenteLojaView

        self._abrir_modulo(FrenteLojaView, "frente_loja")

    def _open_painel_admin(self):
        if not self._tem_permissao("sistema.master"):
            return
        from modules.admin.views.painel_admin_view import PainelAdminView

        self._abrir_modulo(PainelAdminView, "painel_admin")

    def _open_estoque(self):
        if not self._tem_permissao("estoque.gerenciar"):
            return
        from modules.estoque.views.painel_estoque_view import PainelEstoqueView

        self._abrir_modulo(PainelEstoqueView, "painel_estoque")

    def _open_financeiro(self):
        if not self._tem_permissao("financeiro.total"):
            return
        from modules.financeiro.views.painel_financeiro_view import PainelFinanceiroView

        self._abrir_modulo(PainelFinanceiroView, "painel_financeiro")

    def _open_promocoes(self):
        if not self._tem_permissao("relatorios.ver"):
            return
        from modules.promocoes.views.painel_promocoes_view import PainelPromocoesView

        self._abrir_modulo(PainelPromocoesView, "painel_promocoes")

    def _exit(self):
        from utils.ui_messages import confirmar_acao

        usuario = self._usuario_atual()
        nome = usuario.get("nome", "") if usuario else ""
        if not confirmar_acao(self, "Confirmar Logout", f"Deseja realmente sair da sessão de {nome}?"):
            return

        from modules.auth.views.login_view import LoginView

        SessionManager.logout()
        LoginView.usuario_logado = None
        self.hide()
        self.login = LoginView()
        if self.login.exec_() == LoginView.Accepted:
            self._atualizar_operador()
            self._verificar_acessos()
            self.show()
