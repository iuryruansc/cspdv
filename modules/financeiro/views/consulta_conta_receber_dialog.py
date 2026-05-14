from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from ui.financeiro.consulta_conta_receber_dialog import Ui_ConsultaContaReceberDialog
from utils.format_utils import formatar_data, formatar_data_hora, formatar_moeda
from utils.table_widget_utils import set_table_item

class ConsultaContaReceberDialog(QDialog, Ui_ConsultaContaReceberDialog):
    def __init__(self, detalhes: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._detalhes = detalhes
        self._conta = detalhes.get("conta") or {}
        self.solicitar_recebimento = False
        self.setupUi(self)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.btnFechar.clicked.connect(self.accept)
        self.btnReceberAgora.clicked.connect(self._receber_agora)
        self._populate()

    def _populate(self) -> None:
        conta = self._conta
        self.lblContaValor.setText(f"#{int(conta.get('id') or 0)}")
        self.lblClienteValor.setText(str(conta.get("cliente") or "Consumidor Final"))
        self.lblVendaValor.setText(f"#{int(conta.get('venda_id') or 0)}")
        self.lblStatusValor.setText(str(conta.get("status") or "-"))
        self.lblVencimentoValor.setText(formatar_data(conta.get("data_vencimento")))
        self.lblTotalValor.setText(formatar_moeda(conta.get("valor_total")))
        self.lblRecebidoValor.setText(formatar_moeda(conta.get("valor_recebido")))
        self.lblAbertoValor.setText(formatar_moeda(conta.get("valor_aberto")))
        resumo = self._detalhes.get("resumo") or {}
        self.lblQtdRecebimentosValor.setText(str(int(resumo.get("quantidade_recebimentos") or 0)))
        self.lblUltimoRecebimentoValor.setText(formatar_data_hora(resumo.get("ultimo_recebimento")))
        self.lblDiasAtrasoValor.setText(str(int(resumo.get("dias_atraso") or 0)))
        self.plainObservacao.setPlainText(str(conta.get("observacao") or "Sem observações registradas."))
        self._aplicar_estilo_status()
        aberto = Decimal(str(conta.get("valor_aberto") or 0))
        conta_aberta = str(conta.get("status") or "").upper() in {"PENDENTE", "PARCIALMENTE_RECEBIDA"} and aberto > Decimal("0.00")
        self.btnReceberAgora.setVisible(conta_aberta)
        self.btnReceberAgora.setEnabled(conta_aberta)
        self._fill_recebimentos(self._detalhes.get("recebimentos") or [])

    def _fill_recebimentos(self, recebimentos: List[Dict[str, Any]]) -> None:
        self.tableRecebimentos.setRowCount(len(recebimentos))
        for row, item in enumerate(recebimentos):
            set_table_item(self.tableRecebimentos, row, 0, formatar_data_hora(item.get("data_recebimento")), alignment=Qt.AlignCenter)
            set_table_item(self.tableRecebimentos, row, 1, str(item.get("forma_pagamento") or "-"))
            set_table_item(self.tableRecebimentos, row, 2, formatar_moeda(item.get("valor_recebido")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableRecebimentos, row, 3, str(item.get("observacao") or "-"))

    def _aplicar_estilo_status(self) -> None:
        status = str(self._conta.get("status") or "").upper()
        dias_atraso = int((self._detalhes.get("resumo") or {}).get("dias_atraso") or 0)
        if status in {"PENDENTE", "PARCIALMENTE_RECEBIDA"} and dias_atraso > 0:
            self.lblStatusValor.setProperty("status", "atrasada")
            self.lblDiasAtrasoValor.setStyleSheet("color:#b42318;")
        elif status == "QUITADA":
            self.lblStatusValor.setProperty("status", "quitada")
            self.lblDiasAtrasoValor.setStyleSheet("color:#123f6f;")
        else:
            self.lblStatusValor.setProperty("status", "aberto")
            self.lblDiasAtrasoValor.setStyleSheet("color:#123f6f;")
        self.lblStatusValor.style().unpolish(self.lblStatusValor)
        self.lblStatusValor.style().polish(self.lblStatusValor)
        self.lblStatusValor.update()

    def _receber_agora(self) -> None:
        self.solicitar_recebimento = True
        self.accept()

