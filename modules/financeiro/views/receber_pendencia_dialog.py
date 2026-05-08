from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QComboBox, QDateEdit, QDialog, QLabel, QLineEdit, QPlainTextEdit, QPushButton

from modules.financeiro.services.financeiro_service import FinanceiroService
from ui.financeiro.receber_pendencia_dialog import Ui_ReceberPendenciaDialog
from utils.format_utils import formatar_moeda, numero_decimal
from utils.ui_messages import mostrar_aviso

class ReceberPendenciaDialog(QDialog, Ui_ReceberPendenciaDialog):
    lblContaValor: QLabel
    lblClienteValor: QLabel
    lblVencimentoValor: QLabel
    lblTotalValor: QLabel
    lblRecebidoValor: QLabel
    lblAbertoValor: QLabel
    cmbFormaPagamento: QComboBox
    lineEditValor: QLineEdit
    dateRecebimento: QDateEdit
    textObservacao: QPlainTextEdit
    btnCancelar: QPushButton
    btnConfirmar: QPushButton

    def __init__(self, conta_detalhada: Dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.resultado: Optional[Dict[str, Any]] = None
        self._conta = dict(conta_detalhada.get("conta") or {})
        self._carregar_formas()
        self._preencher()
        self._conectar()

    def _carregar_formas(self) -> None:
        self.cmbFormaPagamento.clear()
        for forma in FinanceiroService.listar_formas_pagamento():
            self.cmbFormaPagamento.addItem(str(forma.get("nome") or "Forma"), int(forma.get("id") or 0))

    def _preencher(self) -> None:
        self.lblContaValor.setText(f"#{int(self._conta.get('id') or 0)}")
        self.lblClienteValor.setText(str(self._conta.get("cliente") or "Consumidor Final"))
        vencimento = self._conta.get("data_vencimento")
        if hasattr(vencimento, "strftime"):
            self.lblVencimentoValor.setText(vencimento.strftime("%d/%m/%Y"))
        else:
            self.lblVencimentoValor.setText(str(vencimento or "--/--/----"))
        self.lblTotalValor.setText(formatar_moeda(self._conta.get("valor_total") or 0))
        self.lblRecebidoValor.setText(formatar_moeda(self._conta.get("valor_recebido") or 0))
        self.lblAbertoValor.setText(formatar_moeda(self._conta.get("valor_aberto") or 0))
        self.lineEditValor.setText(formatar_moeda(self._conta.get("valor_aberto") or 0).replace("R$ ", ""))
        self.dateRecebimento.setDisplayFormat("dd/MM/yyyy")
        self.dateRecebimento.setDate(QDate.currentDate())
        self.textObservacao.setPlainText(str(self._conta.get("observacao") or "").strip())

    def _conectar(self) -> None:
        self.btnCancelar.clicked.connect(self.reject)
        self.btnConfirmar.clicked.connect(self._confirmar)

    def _confirmar(self) -> None:
        forma_id = int(self.cmbFormaPagamento.currentData() or 0)
        valor = numero_decimal(self.lineEditValor.text())
        valor_aberto = numero_decimal(self._conta.get("valor_aberto") or 0)

        if forma_id <= 0:
            mostrar_aviso(self, "Recebimento", "Selecione uma forma de pagamento para registrar o recebimento.")
            return
        if valor <= 0:
            mostrar_aviso(self, "Recebimento", "Informe um valor maior que zero para o recebimento.")
            return
        if valor > valor_aberto:
            mostrar_aviso(self, "Recebimento", "O valor informado é maior que o saldo em aberto da conta.")
            return

        self.resultado = {
            "conta_id": int(self._conta.get("id") or 0),
            "forma_pagamento_id": forma_id,
            "valor_recebido": valor,
            "observacao": self.textObservacao.toPlainText().strip(),
            "data_recebimento": datetime.combine(self.dateRecebimento.date().toPyDate(), datetime.now().time()),
        }
        self.accept()
