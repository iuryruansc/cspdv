import os

from PyQt5.QtCore import QDate, QTime, QTimer, Qt
from PyQt5.QtGui import QCloseEvent, QKeySequence
from PyQt5.QtWidgets import QLabel, QMainWindow, QPushButton, QShortcut, QStackedWidget

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.venda.services.caixa_service import CaixaService
from modules.venda.services.venda_service import VendaService
from modules.venda.views.fechamento_caixa_view import FechamentoCaixaView
from modules.venda.views.frente_venda_view import FrenteVendaView
from modules.venda.views.modal_consulta_produto_view import ModalConsultaProdutoView
from modules.venda.views.movimentacao_caixa_view import MovimentacaoCaixaView
from modules.venda.views.pagamento_view import PagamentoView
from modules.venda.views.pos_pagamento_dialog import PosPagamentoDialog
from modules.venda.views.resumo_caixa_atual_dialog import ResumoCaixaAtualDialog
from ui.venda.frente_loja import Ui_FrenteLoja
from utils.ui_messages import mostrar_aviso, mostrar_info
from utils.window_size_utils import aplicar_tamanho_proporcional_tela

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

    def __init__(self, parent=None, *, admin_view=None):
        super().__init__(parent)
        self.setupUi(self)
        aplicar_tamanho_proporcional_tela(self, proporcao_largura=0.94, proporcao_altura=0.9)
        self._admin_view = admin_view

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
        self.lblCaixaStatus.setCursor(Qt.PointingHandCursor)
        self.lblCaixaStatus.setToolTip("Clique para ver o resumo do caixa atual")
        self.lblCaixaStatus.mousePressEvent = self._abrir_resumo_caixa_atual_evento
        self.lblSecaoPrincipal.setText("VENDAS")
        self.btnSairLoja.setText("➜ Voltar ao Admin" if self._admin_view is not None else "➜ Sair da Loja")
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
        self.lblSecaoPrincipal.setText("VENDAS")

    def _atualizar_menu_lateral(self, botao_ativo: QPushButton | None = None) -> None:
        botoes = (
            self.btnNavAbertura,
            self.btnNavVendas,
            self.btnNavPreVenda,
            self.btnNavConsulta,
            self.btnNavMovimentacao,
            self.btnNavFechamento,
        )
        for botao in botoes:
            botao.setChecked(botao is botao_ativo)

    def _configurar_fluxo_inicial(self) -> None:
        self.abertura_caixa_view = None
        self.frente_venda_view = None
        self.pagamento_view = None
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

    def _abrir_resumo_caixa_atual_evento(self, _event) -> None:
        self._mostrar_resumo_caixa_atual()

    def _mostrar_resumo_caixa_atual(self) -> None:
        resumo = CaixaService.obter_resumo_caixa_atual()
        if resumo is None:
            mostrar_aviso(
                self,
                "Resumo do caixa",
                "Não há um caixa aberto nesta sessão para exibir o resumo operacional.",
            )
            return

        dialog = ResumoCaixaAtualDialog(resumo, self)
        dialog.exec_()

    def _obter_ou_criar_widget_fluxo(
        self,
        atributo: str,
        view_cls,
        *,
        signal_name: str | None = None,
        handler=None,
    ):
        widget = getattr(self, atributo, None)
        if widget is None:
            widget = view_cls(self)
            if signal_name and handler is not None:
                getattr(widget, signal_name).connect(handler)
            self.stackedContent.addWidget(widget)
            setattr(self, atributo, widget)
        return widget

    def _mostrar_widget_fluxo(
        self,
        *,
        widget,
        botao_ativo: QPushButton,
        titulo: str,
    ) -> None:
        self._atualizar_menu_lateral(botao_ativo)
        self.stackedContent.setCurrentWidget(widget)

    def _mostrar_abertura_caixa(self) -> None:
        from modules.venda.views.abertura_caixa_view import AberturaCaixaView

        self.abertura_caixa_view = self._obter_ou_criar_widget_fluxo(
            "abertura_caixa_view",
            AberturaCaixaView,
            signal_name="caixa_aberto",
            handler=self._on_caixa_aberto,
        )

        caixa_aberto = CaixaSession.current()
        if caixa_aberto:
            self.abertura_caixa_view.preencher_caixa_existente(caixa_aberto)

        self._mostrar_widget_fluxo(
            widget=self.abertura_caixa_view,
            botao_ativo=self.btnNavAbertura,
            titulo="ABERTURA DE CAIXA",
        )

    def _mostrar_frente_venda(self) -> None:
        self.frente_venda_view = self._obter_ou_criar_widget_fluxo(
            "frente_venda_view",
            FrenteVendaView,
            signal_name="pagamento_solicitado",
            handler=self._mostrar_pagamento_venda,
        )

        self._mostrar_widget_fluxo(
            widget=self.frente_venda_view,
            botao_ativo=self.btnNavVendas,
            titulo="VENDAS",
        )

    def _mostrar_consulta_produto(self) -> None:
        self._atualizar_menu_lateral(self.btnNavConsulta)
        self.lblSecaoPrincipal.setText("VENDAS")
        dialog = ModalConsultaProdutoView(self)
        dialog.exec_()

    def _mostrar_movimentacao_caixa(self) -> None:
        self.movimentacao_caixa_view = self._obter_ou_criar_widget_fluxo(
            "movimentacao_caixa_view",
            MovimentacaoCaixaView,
        )

        self._mostrar_widget_fluxo(
            widget=self.movimentacao_caixa_view,
            botao_ativo=self.btnNavMovimentacao,
            titulo="MOVIMENTACAO DE CAIXA",
        )

    def _mostrar_pagamento_venda(self, venda_data: dict) -> None:
        self.pagamento_view = self._obter_ou_criar_widget_fluxo(
            "pagamento_view",
            PagamentoView,
            signal_name="voltar_venda",
            handler=self._mostrar_frente_venda,
        )
        if not hasattr(self.pagamento_view, "_cspdv_finalizacao_conectada"):
            self.pagamento_view.venda_finalizada.connect(self._on_venda_finalizada)
            self.pagamento_view._cspdv_finalizacao_conectada = True
        self.pagamento_view.carregar_venda(venda_data)
        self._mostrar_widget_fluxo(
            widget=self.pagamento_view,
            botao_ativo=self.btnNavVendas,
            titulo="PAGAMENTO",
        )

    def _mostrar_fechamento_caixa(self) -> None:
        self.fechamento_caixa_view = self._obter_ou_criar_widget_fluxo(
            "fechamento_caixa_view",
            FechamentoCaixaView,
            signal_name="caixa_fechado",
            handler=self._on_caixa_fechado,
        )

        self._mostrar_widget_fluxo(
            widget=self.fechamento_caixa_view,
            botao_ativo=self.btnNavFechamento,
            titulo="FECHAMENTO DE CAIXA",
        )

    def _on_caixa_aberto(self, caixa_data: dict) -> None:
        self._aplicar_estado_caixa()
        self._atualizar_menu_lateral(self.btnNavAbertura)
        self.lblDefaultMsg.setText(
            f"Caixa aberto com sucesso para {caixa_data.get('pdv_label', 'o PDV selecionado')}.\n"
            "Os fluxos de venda, pre-venda e consulta ja podem ser conectados."
        )

    def _on_caixa_fechado(self, fechamento: dict) -> None:
        self._aplicar_estado_caixa()
        self._atualizar_menu_lateral(None)
        self.lblDefaultMsg.setText(
            "O caixa foi fechado com sucesso.\n"
            "Abra um novo caixa para retomar os fluxos de venda."
        )
        self._descartar_widgets_fluxo(
            "abertura_caixa_view",
            "frente_venda_view",
            "pagamento_view",
            "movimentacao_caixa_view",
            "fechamento_caixa_view",
        )
        self.stackedContent.setCurrentIndex(0)
        self.lblSecaoPrincipal.setText("VENDAS")

    def _on_venda_finalizada(self, venda_data: dict) -> None:
        sucesso, mensagem, venda_registrada = VendaService.finalizar_venda(venda_data)
        if not sucesso or venda_registrada is None:
            mostrar_aviso(self, "Venda não registrada", mensagem)
            return

        dialog = PosPagamentoDialog(venda_data=venda_registrada, parent=self)
        dialog.exec_()

        if dialog.resultado == "imprimir":
            mostrar_info(
                self,
                "Impressão",
                "A impressão do cupom será conectada na próxima etapa. A venda já foi finalizada com sucesso.",
            )
            self._reiniciar_fluxo_venda()
            return

        if dialog.resultado == "sem_impressao":
            self._reiniciar_fluxo_venda()
            return

        self._descartar_widget_fluxo("frente_venda_view")
        self._descartar_widget_fluxo("pagamento_view")
        self._atualizar_menu_lateral(None)
        self.stackedContent.setCurrentIndex(0)
        self.lblSecaoPrincipal.setText("VENDAS")
        self.lblDefaultMsg.setText(
            f"Venda n° {venda_registrada.get('numero_venda')} finalizada com sucesso.\n"
            "Selecione o próximo fluxo operacional."
        )

    def _reiniciar_fluxo_venda(self) -> None:
        self._descartar_widget_fluxo("frente_venda_view")
        self._descartar_widget_fluxo("pagamento_view")
        self._mostrar_frente_venda()

    def _descartar_widget_fluxo(self, atributo: str) -> None:
        widget = getattr(self, atributo, None)
        if widget is None:
            return
        self.stackedContent.removeWidget(widget)
        widget.deleteLater()
        setattr(self, atributo, None)

    def _descartar_widgets_fluxo(self, *atributos: str) -> None:
        for atributo in atributos:
            self._descartar_widget_fluxo(atributo)

    def _voltar_para_selecao(self) -> None:
        if self._admin_view is not None:
            self.hide()
            self._admin_view.show()
            self._admin_view.raise_()
            self._admin_view.activateWindow()
            return

        if not self._permitir_navegacao():
            return

        from modules.auth.views.selecao_modo_view import SelecaoModoView

        self.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()

    def _usuario_tem_acessos_multiplos(self) -> bool:
        usuario = SessionManager.current_user() or {}
        permissoes = {
            str(permissao).strip()
            for permissao in usuario.get("permissoes", [])
            if str(permissao).strip()
        }
        return "sistema.master" in permissoes or len(permissoes) > 1

    def _permitir_navegacao(self) -> bool:
        if os.getenv("CSPDV_ALLOW_TEST_CAIXA_EXIT", "").lower() in {"1", "true", "yes", "on"}:
            return True

        if not CaixaSession.has_open_caixa():
            return True

        if self._usuario_tem_acessos_multiplos():
            return True

        mostrar_aviso(
            self,
            "Caixa aberto",
            "Não é possível sair da frente de loja enquanto houver um caixa aberto.\n\n"
            "Feche o caixa primeiro ou acesse outro módulo com um usuário que tenha mais de uma permissão operacional.",
        )
        return False

    def _permitir_fechamento_programa(self) -> bool:
        if os.getenv("CSPDV_ALLOW_TEST_CAIXA_EXIT", "").lower() in {"1", "true", "yes", "on"}:
            return True

        if not SessionManager.should_block_close_with_open_caixa():
            return True

        if not CaixaSession.has_open_caixa():
            return True

        mostrar_aviso(
            self,
            "Caixa aberto",
            "Não é possível fechar o programa enquanto houver um caixa aberto.\n\n"
            "Feche o caixa primeiro para encerrar a operacao com seguranca.",
        )
        return False

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self._permitir_fechamento_programa():
            super().closeEvent(a0)
            return

        a0.ignore()
