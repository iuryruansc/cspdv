from __future__ import annotations

from typing import Dict

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QLabel, QDateEdit, QPlainTextEdit, QPushButton

from ui.venda.finalizar_pendencia_dialog import Ui_FinalizarPendenciaDialog
from utils.format_utils import formatar_moeda, numero_decimal
from utils.ui_messages import mostrar_aviso


class FinalizarPendenciaDialog(QDialog, Ui_FinalizarPendenciaDialog):
    lblClienteValor: QLabel
    lblTotalValor: QLabel
    lblPagoValor: QLabel
    lblAbertoValor: QLabel
    dateVencimento: QDateEdit
    textObservacao: QPlainTextEdit
    btnCancelar: QPushButton
    btnConfirmar: QPushButton

    def __init__(self, *, venda_data: Dict[str, object], valor_pago: float, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.resultado: Dict[str, object] | None = None
        self._venda_data = venda_data
        self._valor_pago = numero_decimal(valor_pago)
        self._valor_total = numero_decimal(venda_data.get("total"))
        self._valor_aberto = max(0.0, self._valor_total - self._valor_pago)
        self._preencher_dados()
        self._conectar_sinais()

    def _preencher_dados(self) -> None:
        self.lblClienteValor.setText(str(self._venda_data.get("cliente_nome") or "Consumidor Final"))
        self.lblTotalValor.setText(formatar_moeda(self._valor_total))
        self.lblPagoValor.setText(formatar_moeda(self._valor_pago))
        self.lblAbertoValor.setText(formatar_moeda(self._valor_aberto))
        self.dateVencimento.setDisplayFormat("dd/MM/yyyy")
        self.dateVencimento.setDate(QDate.currentDate().addDays(7))

    def _conectar_sinais(self) -> None:
        self.btnCancelar.clicked.connect(self.reject)
        self.btnConfirmar.clicked.connect(self._confirmar)

    def _confirmar(self) -> None:
        if self._valor_aberto <= 0:
            mostrar_aviso(self, "Pendencia", "Nao ha saldo em aberto para gerar uma pendencia.")
            return

        self.resultado = {
            "data_vencimento": self.dateVencimento.date().toString("yyyy-MM-dd"),
            "observacao": self.textObservacao.toPlainText().strip(),
            "valor_em_aberto": self._valor_aberto,
        }
        self.accept()
