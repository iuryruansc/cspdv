from __future__ import annotations

from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QStackedLayout, QVBoxLayout, QWidget

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.venda.services.venda_service import VendaService
from modules.venda.views.frente_venda_view import FrenteVendaView
from modules.venda.views.pagamento_view import PagamentoView
from modules.venda.views.pos_pagamento_dialog import PosPagamentoDialog
from utils.ui_messages import mostrar_aviso, mostrar_info


class VendaRapidaDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("CSPdv - Venda Rapida")
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(1460, 900)
        self.setMinimumSize(1320, 820)
        self.setModal(True)

        self._build_ui()
        self._configurar_contexto()
        self._configurar_fluxo()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #edf4f9, stop:1 #dce8f1);
            }
            QWidget#frameHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #163552, stop:0.6 #224e76, stop:1 #2f6b9d);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 16px;
            }
            QLabel#lblTitulo {
                color: white;
                font-size: 22px;
                font-weight: 800;
            }
            QLabel#lblSubtitulo {
                color: #dbeaf7;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#lblOperador, QLabel#lblCaixa {
                color: #eef6fc;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 12px;
                background-color: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 10px;
            }
            QWidget#contentWrap {
                background-color: rgba(255,255,255,0.42);
                border: 1px solid #c9d9e6;
                border-radius: 18px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        self.frameHeader = QWidget(self)
        self.frameHeader.setObjectName("frameHeader")
        header_layout = QHBoxLayout(self.frameHeader)
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(14)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        self.lblTitulo = QLabel("Venda Rapida", self.frameHeader)
        self.lblTitulo.setObjectName("lblTitulo")
        self.lblSubtitulo = QLabel(
            "Fluxo compacto de venda sem sair do painel administrativo.",
            self.frameHeader,
        )
        self.lblSubtitulo.setObjectName("lblSubtitulo")
        title_col.addWidget(self.lblTitulo)
        title_col.addWidget(self.lblSubtitulo)
        header_layout.addLayout(title_col)
        header_layout.addStretch()

        status_col = QVBoxLayout()
        status_col.setSpacing(4)
        self.lblOperador = QLabel(self.frameHeader)
        self.lblOperador.setObjectName("lblOperador")
        self.lblCaixa = QLabel(self.frameHeader)
        self.lblCaixa.setObjectName("lblCaixa")
        status_col.addWidget(self.lblOperador)
        status_col.addWidget(self.lblCaixa)
        header_layout.addLayout(status_col)

        root.addWidget(self.frameHeader)

        self.contentWrap = QWidget(self)
        self.contentWrap.setObjectName("contentWrap")
        self.contentLayout = QStackedLayout(self.contentWrap)
        self.contentLayout.setContentsMargins(12, 12, 12, 12)
        root.addWidget(self.contentWrap, 1)

    def _configurar_contexto(self) -> None:
        usuario = SessionManager.current_user() or {}
        caixa = CaixaSession.current() or {}
        self.lblOperador.setText(f"Operador: {str(usuario.get('nome') or '---').upper()}")
        self.lblCaixa.setText(f"Caixa: {str(caixa.get('pdv_label') or 'Nao identificado')}")

    def _configurar_fluxo(self) -> None:
        self.frente_venda_view = FrenteVendaView(self)
        self.pagamento_view = PagamentoView(self)

        self.frente_venda_view.pagamento_solicitado.connect(self._abrir_pagamento)
        self.pagamento_view.voltar_venda.connect(self._voltar_para_venda)
        self.pagamento_view.venda_finalizada.connect(self._finalizar_venda)

        self.contentLayout.addWidget(self.frente_venda_view)
        self.contentLayout.addWidget(self.pagamento_view)
        self.contentLayout.setCurrentWidget(self.frente_venda_view)

    def _abrir_pagamento(self, venda_data: Dict[str, Any]) -> None:
        self.pagamento_view.carregar_venda(venda_data)
        self.contentLayout.setCurrentWidget(self.pagamento_view)

    def _voltar_para_venda(self) -> None:
        self.contentLayout.setCurrentWidget(self.frente_venda_view)

    def _finalizar_venda(self, venda_data: Dict[str, Any]) -> None:
        sucesso, mensagem, venda_registrada = VendaService.finalizar_venda(venda_data)
        if not sucesso or venda_registrada is None:
            mostrar_aviso(self, "Venda nao registrada", mensagem)
            return

        dialog = PosPagamentoDialog(venda_data=venda_registrada, parent=self)
        dialog.exec_()

        parent = self.parent()
        if parent is not None and hasattr(parent, "_load_dashboard_cards"):
            parent._load_dashboard_cards()

        if dialog.resultado == "imprimir":
            mostrar_info(
                self,
                "Impressao",
                "A impressao do cupom sera conectada na proxima etapa. A venda ja foi finalizada com sucesso.",
            )
            self._reiniciar_fluxo()
            return

        if dialog.resultado == "sem_impressao":
            self._reiniciar_fluxo()
            return

        self.accept()

    def _reiniciar_fluxo(self) -> None:
        self.contentLayout.removeWidget(self.frente_venda_view)
        self.frente_venda_view.deleteLater()
        self.frente_venda_view = FrenteVendaView(self)
        self.frente_venda_view.pagamento_solicitado.connect(self._abrir_pagamento)
        self.contentLayout.insertWidget(0, self.frente_venda_view)
        self.contentLayout.setCurrentWidget(self.frente_venda_view)
