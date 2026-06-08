from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QShortcut, QWidget
from PyQt5.QtGui import QKeySequence

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.auth.views.troca_operador_dialog import TrocaOperadorDialog
from ui.login.selecao_modo import Ui_SelecaoModo
from utils.system_runtime import descricao_ambiente, versao_referencia
from utils.ui_messages import confirmar_acao
from utils.window_size_utils import aplicar_tamanho_proporcional_tela

class SelecaoModoView(QWidget, Ui_SelecaoModo):
    COLUNAS_CARDS = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        aplicar_tamanho_proporcional_tela(self, proporcao_largura=0.88, proporcao_altura=0.86)
        self.lblAtalhosTitulo.setText("Atalhos rápidos")
        self.lblAtalhosTexto.setText(
            "<html><head/><body><table cellspacing=\"0\" cellpadding=\"0\" style=\"line-height:1.6;\">"
            "<tr>"
            "<td style=\"padding-right:10px;\"><span style=\"display:inline-block; min-width:32px; padding:2px 8px; border-radius:10px; background:#2a4f75; color:#d8ecff; font-weight:700; text-align:center;\">F1</span></td>"
            "<td style=\"padding-right:22px;\">Frente de Caixa</td>"
            "<td style=\"padding-right:10px;\"><span style=\"display:inline-block; min-width:32px; padding:2px 8px; border-radius:10px; background:#2a4f75; color:#d8ecff; font-weight:700; text-align:center;\">F2</span></td>"
            "<td style=\"padding-right:22px;\">Administração</td>"
            "<td style=\"padding-right:10px;\"><span style=\"display:inline-block; min-width:32px; padding:2px 8px; border-radius:10px; background:#2a4f75; color:#d8ecff; font-weight:700; text-align:center;\">F3</span></td>"
            "<td style=\"padding-right:22px;\">Estoque</td>"
            "<td style=\"padding-right:10px;\"><span style=\"display:inline-block; min-width:32px; padding:2px 8px; border-radius:10px; background:#2a4f75; color:#d8ecff; font-weight:700; text-align:center;\">F4</span></td>"
            "<td style=\"padding-right:22px;\">Financeiro</td>"
            "<td style=\"padding-right:10px;\"><span style=\"display:inline-block; min-width:32px; padding:2px 8px; border-radius:10px; background:#2a4f75; color:#d8ecff; font-weight:700; text-align:center;\">F5</span></td>"
            "<td style=\"padding-right:22px;\">Promoções</td>"
            "<td style=\"padding-right:10px;\"><span style=\"display:inline-block; min-width:32px; padding:2px 8px; border-radius:10px; background:#2a4f75; color:#d8ecff; font-weight:700; text-align:center;\">F6</span></td>"
            "<td>Relatórios</td>"
            "</tr></table></body></html>"
        )
        self.lblResumoBadge.setText("F6 • RELATÓRIOS")
        self.lblResumoBadge.setProperty("moduleBadge", "true")
        self.lblResumoTitle.setText("Relatórios")
        self.lblResumoTitle.setProperty("moduleTitle", "true")
        self.lblResumoText3.setText("Indicadores, análises e exportações para apoiar a gestão operacional e o acompanhamento do negócio.")
        self.lblResumoText3.setWordWrap(True)
        self.lblResumoText3.setProperty("moduleDesc", "true")
        self.btnResumoRelatorios.setText("Abrir Relatórios")
        self.btnResumoRelatorios.setToolTip("[F6] Relatórios")
        self.btnResumoRelatorios.setProperty("moduleCard", "true")
        self._montar_atalhos_rapidos()
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

        self.shortcut_f6 = QShortcut(QKeySequence("F6"), self)
        self.shortcut_f6.activated.connect(self._open_relatorios)

        self.shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_esc.activated.connect(self._exit)

    def _montar_atalhos_rapidos(self) -> None:
        self.lblAtalhosTexto.hide()
        self._atalhos_rapidos_widget = QWidget(self.frameAtalhos)
        layout = QHBoxLayout(self._atalhos_rapidos_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.setObjectName("atalhosRapidosLayout")

        atalhos = [
            ("F1", "Frente de Caixa"),
            ("F2", "Administração"),
            ("F3", "Estoque"),
            ("F4", "Financeiro"),
            ("F5", "Promoções"),
            ("F6", "Relatórios"),
        ]
        for indice, (tecla, descricao) in enumerate(atalhos):
            chip = QLabel(tecla, self._atalhos_rapidos_widget)
            chip.setAlignment(Qt.AlignCenter)
            chip.setMinimumWidth(34)
            chip.setStyleSheet(
                "QLabel {"
                " padding: 2px 8px;"
                " border-radius: 10px;"
                " background: #2a4f75;"
                " color: #d8ecff;"
                " font-weight: 700;"
                "}"
            )
            texto = QLabel(descricao, self._atalhos_rapidos_widget)
            texto.setStyleSheet("QLabel { color: #d8ebfb; font-size: 11px; }")
            layout.addWidget(chip)
            layout.addWidget(texto)
            if indice < len(atalhos) - 1:
                layout.addSpacing(14)

        self.frameAtalhosLayout.addWidget(self._atalhos_rapidos_widget, 1)

    def _conectar_eventos(self):
        self.btnFrenteCaixa.clicked.connect(self._open_pdv)
        self.btnPainelAdmin.clicked.connect(self._open_painel_admin)
        self.btnEstoque.clicked.connect(self._open_estoque)
        self.btnFinanceiro.clicked.connect(self._open_financeiro)
        self.btnRelatorios.clicked.connect(self._open_promocoes)
        self.btnResumoRelatorios.clicked.connect(self._open_relatorios)
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

        tem_relatorios = self._tem_permissao("relatorios.ver")
        self.cardResumo.setVisible(tem_relatorios)
        self.shortcut_f6.setEnabled(tem_relatorios)
        if tem_relatorios:
            cards_visiveis.append(self.cardResumo)

        self._reorganizar_cards(cards_visiveis)

    def _reorganizar_cards(self, cards_visiveis):
        for _, card, _ in self._cards_modulos:
            self.layoutContent.removeWidget(card)
        self.layoutContent.removeWidget(self.cardResumo)

        for indice, card in enumerate(cards_visiveis):
            linha = indice // self.COLUNAS_CARDS
            coluna = indice % self.COLUNAS_CARDS
            self.layoutContent.addWidget(card, linha, coluna)

    def _abrir_modulo(self, view_cls, attr_name: str) -> None:
        self.hide()
        view = view_cls()
        setattr(self, attr_name, view)
        view.showMaximized()

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

    def _open_relatorios(self):
        if not self._tem_permissao("relatorios.ver"):
            return
        from modules.relatorios.views.painel_relatorios_view import PainelRelatoriosView

        self._abrir_modulo(PainelRelatoriosView, "painel_relatorios")

    def _exit(self):
        if self._deve_bloquear_logout_por_caixa_aberto():
            acao = self._mostrar_dialogo_saida_caixa_aberto()
            if acao == "fechamento":
                self._abrir_fechamento_caixa()
            elif acao == "trocar_operador":
                self._trocar_operador()
            return

        usuario = self._usuario_atual()
        nome = usuario.get("nome", "") if usuario else ""
        if not confirmar_acao(self, "Confirmar Logout", f"Deseja realmente sair da sessão de {nome}?"):
            return

        SessionManager.logout()
        self._abrir_login()

    def _deve_bloquear_logout_por_caixa_aberto(self) -> bool:
        return SessionManager.should_block_close_with_open_caixa() and CaixaSession.has_open_caixa()

    def _mostrar_dialogo_saida_caixa_aberto(self) -> str:
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Caixa aberto")
        box.setText(
            "Existe um caixa aberto neste PDV.\n\n"
            "Para evitar que o caixa fique aberto por muito tempo, escolha como deseja continuar."
        )
        box.setStyleSheet(
            """
            QMessageBox {
                background-color: #122c46;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
                min-width: 340px;
            }
            QPushButton {
                min-width: 132px;
                min-height: 34px;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #4b6f91;
                background-color: #f4f8fc;
                color: #16324f;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dceaf7;
            }
            """
        )

        botao_fechamento = box.addButton("Ir para fechamento", QMessageBox.AcceptRole)
        botao_trocar_operador = box.addButton("Trocar operador", QMessageBox.ActionRole)
        botao_cancelar = box.addButton("Cancelar", QMessageBox.RejectRole)
        botao_fechamento.setStyleSheet(
            "QPushButton { background-color: #f5b23c; color: #16324f; border: 1px solid #dc9215; }"
            "QPushButton:hover { background-color: #e3a225; }"
        )
        botao_trocar_operador.setStyleSheet(
            "QPushButton { background-color: #3b84cf; color: white; border: 1px solid #2d6ca8; }"
            "QPushButton:hover { background-color: #2f72b4; }"
        )
        botao_cancelar.setStyleSheet(
            "QPushButton { background-color: #eef3f8; color: #16324f; border: 1px solid #90a9c1; }"
            "QPushButton:hover { background-color: #dbe6f0; }"
        )
        box.setDefaultButton(botao_cancelar)
        box.exec_()

        clicado = box.clickedButton()
        if clicado is botao_fechamento:
            return "fechamento"
        if clicado is botao_trocar_operador:
            return "trocar_operador"
        return "cancelar"

    def _abrir_fechamento_caixa(self) -> None:
        from modules.venda.views.fechar_caixa_dialog import FecharCaixaDialog

        dialog = FecharCaixaDialog(self)
        dialog.exec_()

    def _trocar_operador(self) -> None:
        dialog = TrocaOperadorDialog(self)
        if dialog.exec_() == dialog.Accepted:
            self._atualizar_operador()
            self._verificar_acessos()

    def _abrir_login(self) -> None:
        from modules.auth.views.login_view import LoginView

        self.hide()
        self.login = LoginView()
        if self.login.exec_() == LoginView.Accepted:
            self._atualizar_operador()
            self._verificar_acessos()
            self.showMaximized()
            return
        self.close()
