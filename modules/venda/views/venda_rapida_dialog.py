from __future__ import annotations

from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.venda.services.venda_service import VendaService
from modules.venda.views.frente_venda_view import FrenteVendaView
from modules.venda.views.pagamento_view import PagamentoView
from modules.venda.views.pos_pagamento_dialog import PosPagamentoDialog
from ui.venda.venda_rapida_dialog import Ui_VendaRapidaDialog
from utils.ui_messages import mostrar_aviso, mostrar_info

class VendaRapidaDialog(QDialog, Ui_VendaRapidaDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setModal(True)

        self._configurar_contexto()
        self._configurar_fluxo()

    def _configurar_contexto(self) -> None:
        usuario = SessionManager.current_user() or {}
        caixa = CaixaSession.current() or {}
        self.lblOperador.setText(f"Operador: {str(usuario.get('nome') or '---').upper()}")
        self.lblCaixa.setText(f"Caixa: {str(caixa.get('pdv_label') or 'Não identificado')}")

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
            mostrar_aviso(self, "Venda não registrada", mensagem)
            return

        dialog = PosPagamentoDialog(venda_data=venda_registrada, parent=self)
        dialog.exec_()

        parent = self.parent()
        if parent is not None:
            atualizar_dashboard = getattr(parent, "_load_dashboard_cards", None)
            if callable(atualizar_dashboard):
                atualizar_dashboard()

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
