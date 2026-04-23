import os

from PyQt5.QtCore import QDate, QTime, QTimer
from PyQt5.QtGui import QCloseEvent, QKeySequence
from PyQt5.QtWidgets import QLabel, QMainWindow, QMessageBox, QPushButton, QShortcut, QStackedWidget

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.venda.services.caixa_service import CaixaService
from modules.venda.views.fechamento_caixa_view import FechamentoCaixaView
from modules.venda.views.frente_venda_view import FrenteVendaView
from modules.venda.views.modal_consulta_produto_view import ModalConsultaProdutoView
from modules.venda.views.movimentacao_caixa_view import MovimentacaoCaixaView
from ui.venda.frente_loja import Ui_FrenteLoja


class FrenteLojaView(QMainWindow, Ui_FrenteLoja):
    lblOpNome: QLabel
    lblCaixaStatus: QLabel
    lblSecaoPrincipal: QLabel
    lblDefaultMsg: QLabel
    lblSidebarDataHora: QLabel
    lblSidebarHora: QLabel
    btnSairLoja: QPushButton
    btnNavAbertura: QPushButton
    btnNavVendas: QPushButton
    btnNavPreVenda: QPushButton
    btnNavConsulta: QPushButton
    btnNavMovimentacao: QPushButton
    btnNavFechamento: QPushButton
    stackedContent: QStackedWidget

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._configurar_contexto_usuario()
        self._configurar_eventos()
        self._configurar_atalhos()
        self._configurar_fluxo_inicial()
        self._atualizar_data_hora()

        self.timer_data_hora = QTimer(self)
        self.timer_data_hora.timeout.connect(self._atualizar_data_hora)
        self.timer_data_hora.start(1000)

    def _configurar_contexto_usuario(self) -> None:
        usuario = SessionManager.current_user() or {}
        nome = str(usuario.get("nome", "Operador")).upper()
        self.lblOpNome.setText(nome)
        self.lblCaixaStatus.setText("CAIXA: AGUARDANDO ABERTURA")
        self.lblSecaoPrincipal.setText("FRENTE DE LOJA")
        self.lblDefaultMsg.setText(
            "A area de vendas foi iniciada pela Frente de Loja.\n"
            "Os fluxos de abertura, venda, pre-venda e consulta serao conectados apos a abertura de caixa."
        )

    def _configurar_eventos(self) -> None:
        self.btnSairLoja.clicked.connect(self._voltar_para_selecao)
        self.btnNavAbertura.clicked.connect(self._mostrar_abertura_caixa)
        self.btnNavVendas.clicked.connect(self._mostrar_frente_venda)
        self.btnNavPreVenda.clicked.connect(lambda: self._selecionar_secao("PRE-VENDA"))
        self.btnNavConsulta.clicked.connect(self._mostrar_consulta_produto)
        self.btnNavMovimentacao.clicked.connect(self._mostrar_movimentacao_caixa)
        self.btnNavFechamento.clicked.connect(self._mostrar_fechamento_caixa)

    def _configurar_atalhos(self) -> None:
        self.shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_esc.activated.connect(self._voltar_para_selecao)

    def _atualizar_data_hora(self) -> None:
        self.lblSidebarDataHora.setText(QDate.currentDate().toString("dd/MM/yyyy"))
        self.lblSidebarHora.setText(QTime.currentTime().toString("HH:mm:ss"))

    def _selecionar_secao(self, titulo: str) -> None:
        self.lblSecaoPrincipal.setText(titulo)

    def _configurar_fluxo_inicial(self) -> None:
        self.abertura_caixa_view = None
        self.frente_venda_view = None
        self.movimentacao_caixa_view = None
        self.fechamento_caixa_view = None
        if not CaixaSession.has_open_caixa():
            usuario = SessionManager.current_user() or {}
            CaixaService.restaurar_caixa_aberto(usuario.get("id"))
        self._aplicar_estado_caixa()

    def _aplicar_estado_caixa(self) -> None:
        caixa_aberto = CaixaSession.current()
        liberado = caixa_aberto is not None

        self.btnNavVendas.setEnabled(liberado)
        self.btnNavPreVenda.setEnabled(liberado)
        self.btnNavConsulta.setEnabled(liberado)
        self.btnNavMovimentacao.setEnabled(liberado)
        self.btnNavFechamento.setEnabled(liberado)

        if caixa_aberto:
            self.lblCaixaStatus.setText(
                f"CAIXA: ABERTO | {caixa_aberto.get('pdv_label', 'PDV')} | R$ {caixa_aberto.get('valor_abertura', 0):.2f}"
            )
            self.btnNavAbertura.setEnabled(False)
            return

        self.lblCaixaStatus.setText("CAIXA: AGUARDANDO ABERTURA")
        self.btnNavAbertura.setEnabled(True)

    def _mostrar_abertura_caixa(self) -> None:
        from modules.venda.views.abertura_caixa_view import AberturaCaixaView

        if self.abertura_caixa_view is None:
            self.abertura_caixa_view = AberturaCaixaView(self)
            self.abertura_caixa_view.caixa_aberto.connect(self._on_caixa_aberto)
            self.stackedContent.addWidget(self.abertura_caixa_view)

        caixa_aberto = CaixaSession.current()
        if caixa_aberto:
            self.abertura_caixa_view.preencher_caixa_existente(caixa_aberto)

        self.lblSecaoPrincipal.setText("ABERTURA DE CAIXA")
        self.stackedContent.setCurrentWidget(self.abertura_caixa_view)

    def _mostrar_frente_venda(self) -> None:
        if self.frente_venda_view is None:
            self.frente_venda_view = FrenteVendaView(self)
            self.stackedContent.addWidget(self.frente_venda_view)

        self.lblSecaoPrincipal.setText("VENDAS")
        self.stackedContent.setCurrentWidget(self.frente_venda_view)

    def _mostrar_consulta_produto(self) -> None:
        self.lblSecaoPrincipal.setText("CONSULTA DE PRECOS")
        dialog = ModalConsultaProdutoView(self)
        dialog.exec_()

    def _mostrar_movimentacao_caixa(self) -> None:
        if self.movimentacao_caixa_view is None:
            self.movimentacao_caixa_view = MovimentacaoCaixaView(self)
            self.stackedContent.addWidget(self.movimentacao_caixa_view)

        self.lblSecaoPrincipal.setText("MOVIMENTACAO DE CAIXA")
        self.stackedContent.setCurrentWidget(self.movimentacao_caixa_view)

    def _mostrar_fechamento_caixa(self) -> None:
        if self.fechamento_caixa_view is None:
            self.fechamento_caixa_view = FechamentoCaixaView(self)
            self.fechamento_caixa_view.caixa_fechado.connect(self._on_caixa_fechado)
            self.stackedContent.addWidget(self.fechamento_caixa_view)

        self.lblSecaoPrincipal.setText("FECHAMENTO DE CAIXA")
        self.stackedContent.setCurrentWidget(self.fechamento_caixa_view)

    def _on_caixa_aberto(self, caixa_data: dict) -> None:
        self._aplicar_estado_caixa()
        self.lblDefaultMsg.setText(
            f"Caixa aberto com sucesso para {caixa_data.get('pdv_label', 'o PDV selecionado')}.\n"
            "Os fluxos de venda, pre-venda e consulta ja podem ser conectados."
        )

    def _on_caixa_fechado(self, fechamento: dict) -> None:
        self._aplicar_estado_caixa()
        self.lblDefaultMsg.setText(
            "O caixa foi fechado com sucesso.\n"
            "Abra um novo caixa para retomar os fluxos de venda."
        )
        self._descartar_widget_fluxo("abertura_caixa_view")
        self._descartar_widget_fluxo("frente_venda_view")
        self._descartar_widget_fluxo("movimentacao_caixa_view")
        self._descartar_widget_fluxo("fechamento_caixa_view")
        self.stackedContent.setCurrentIndex(0)
        self.lblSecaoPrincipal.setText("FRENTE DE LOJA")

    def _descartar_widget_fluxo(self, atributo: str) -> None:
        widget = getattr(self, atributo, None)
        if widget is None:
            return
        self.stackedContent.removeWidget(widget)
        widget.deleteLater()
        setattr(self, atributo, None)

    def _voltar_para_selecao(self) -> None:
        if not self._permitir_saida():
            return

        from modules.auth.views.selecao_modo_view import SelecaoModoView

        self.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()

    def _permitir_saida(self) -> bool:
        if os.getenv("CSPDV_ALLOW_TEST_CAIXA_EXIT", "").lower() in {"1", "true", "yes", "on"}:
            return True

        if not CaixaSession.has_open_caixa():
            return True

        QMessageBox.warning(
            self,
            "Caixa aberto",
            "Nao e possivel sair da frente de loja com um caixa aberto.\n\n"
            "Feche o caixa primeiro para encerrar a operacao com seguranca.",
        )
        return False

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self._permitir_saida():
            super().closeEvent(a0)
            return

        a0.ignore()
