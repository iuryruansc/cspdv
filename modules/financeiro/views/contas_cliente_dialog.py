from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QDialog, QDialogButtonBox, QHeaderView, QLabel, QPushButton, QTableWidget, QVBoxLayout

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.financeiro.services.financeiro_service import FinanceiroService
from utils.format_utils import formatar_data, formatar_moeda
from utils.table_widget_utils import set_table_item
from utils.ui_messages import mostrar_aviso


class ContasClienteDialog(QDialog):
    """Consulta as contas em aberto de um cliente."""

    def __init__(self, cliente: dict[str, Any], parent=None):
        super().__init__(parent)
        self._cliente = cliente
        self.setWindowTitle("Contas do cliente")
        self.resize(900, 500)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet(
            "QDialog{background:#edf4fb;} QLabel{color:#153d68;} "
            "QTableWidget{background:#fff;border:1px solid #c8d9ea;gridline-color:#dce8f0;} "
            "QHeaderView::section{background:#f0f6fc;color:#1a3a5c;font-weight:bold;padding:6px;} "
            "QDialogButtonBox QPushButton{min-width:90px;min-height:30px;}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        self.lblTitulo = QLabel(f"Contas em aberto — {cliente.get('nome') or 'Cliente'}")
        self.lblTitulo.setStyleSheet("font-size:18px;font-weight:bold;color:#123f6f;")
        layout.addWidget(self.lblTitulo)
        self.table = QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels(["Conta", "Venda", "Emissão", "Vencimento", "Status", "Valor total", "Em aberto"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        for column in range(7):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)
        self.lblResumo = QLabel()
        self.lblResumo.setStyleSheet("font-weight:bold;color:#1a5fa0;")
        layout.addWidget(self.lblResumo)
        botoes = QDialogButtonBox(parent=self)
        self.btnPagarAgora = QPushButton("Pagar Agora", self)
        self.btnPagarAgora.setStyleSheet("background:#f0a039;color:#fff;font-weight:bold;padding:7px 16px;border-radius:5px;")
        self.btnPagarAgora.setEnabled(False)
        botoes.addButton(self.btnPagarAgora, QDialogButtonBox.AcceptRole)
        botoes.addButton(QDialogButtonBox.Close)
        self.table.itemSelectionChanged.connect(lambda: self.btnPagarAgora.setEnabled(self.table.currentRow() >= 0))
        self.btnPagarAgora.clicked.connect(self._pagar_agora)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)
        self._carregar()

    def _carregar(self) -> None:
        contas = FinanceiroService.listar_contas_receber_cliente(int(self._cliente.get("id") or 0))
        self.table.setRowCount(len(contas))
        total_aberto = 0.0
        for row, conta in enumerate(contas):
            set_table_item(self.table, row, 0, f"#{conta.get('conta_id') or 0}", alignment=Qt.AlignCenter)
            set_table_item(self.table, row, 1, f"#{conta.get('venda_id') or 0}", alignment=Qt.AlignCenter)
            set_table_item(self.table, row, 2, formatar_data(conta.get("data_emissao")), alignment=Qt.AlignCenter)
            vencimento = set_table_item(self.table, row, 3, formatar_data(conta.get("data_vencimento")), alignment=Qt.AlignCenter)
            set_table_item(self.table, row, 4, str(conta.get("status") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.table, row, 5, formatar_moeda(conta.get("valor_total")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            saldo = set_table_item(self.table, row, 6, formatar_moeda(conta.get("valor_aberto")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            try:
                total_aberto += float(conta.get("valor_aberto") or 0)
            except (TypeError, ValueError):
                pass
            if bool(conta.get("vencida")):
                for column in range(self.table.columnCount()):
                    item = self.table.item(row, column)
                    if item:
                        item.setForeground(Qt.darkRed)
                vencimento.setToolTip(f"Vencida há {int(conta.get('dias_atraso') or 0)} dia(s).")
            saldo.setToolTip("Saldo que ainda precisa ser pago pelo cliente.")
        self.lblResumo.setText(f"{len(contas)} conta(s) em aberto • Total: {formatar_moeda(total_aberto)}")

    def _pagar_agora(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            mostrar_aviso(self, "Selecione uma conta", "Selecione a conta que será paga.")
            return
        conta_item = self.table.item(row, 0)
        conta_id = int(str(conta_item.text()).lstrip("#")) if conta_item else 0
        if not conta_id:
            mostrar_aviso(self, "Conta inválida", "Não foi possível identificar a conta selecionada.")
            return
        if not CaixaSession.has_open_caixa():
            mostrar_aviso(self, "Caixa não encontrado", "Abra um caixa antes de registrar pagamentos de pendências.")
            return

        detalhes = FinanceiroService.obter_conta_receber_detalhada(conta_id)
        if not detalhes:
            mostrar_aviso(self, "Conta não encontrada", "Não foi possível localizar os dados da conta selecionada.")
            return
        from modules.financeiro.views.receber_pendencia_dialog import ReceberPendenciaDialog

        pagamento = ReceberPendenciaDialog(detalhes, self)
        if pagamento.exec_() != pagamento.Accepted or not pagamento.resultado:
            return
        usuario = SessionManager.current_user() or {}
        caixa = CaixaSession.current() or {}
        try:
            resultado = FinanceiroService.registrar_recebimento_conta(
                conta_id=int(pagamento.resultado["conta_id"]),
                usuario_id=int(usuario.get("id") or 0),
                caixa_id=int(caixa.get("id") or 0),
                forma_pagamento_id=int(pagamento.resultado["forma_pagamento_id"]),
                valor_recebido=Decimal(str(pagamento.resultado["valor_recebido"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                observacao=str(pagamento.resultado.get("observacao") or "").strip(),
                data_recebimento=pagamento.resultado.get("data_recebimento") or datetime.now(),
            )
        except Exception as exc:
            mostrar_aviso(self, "Pagamento não registrado", str(exc))
            return

        self._carregar()
        self.btnPagarAgora.setEnabled(False)
        from modules.financeiro.views.comprovante_recebimento_dialog import ComprovanteRecebimentoDialog

        ComprovanteRecebimentoDialog(
            conta=dict(detalhes.get("conta") or {}),
            recebimento={**resultado, "observacao": pagamento.resultado.get("observacao") or "", "data_recebimento": pagamento.resultado.get("data_recebimento") or datetime.now()},
            operador_nome=str(usuario.get("nome") or "Operador"),
            caixa_label=str(caixa.get("pdv_label") or "Caixa"),
            parent=self,
        ).exec_()
