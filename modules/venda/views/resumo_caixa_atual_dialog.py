from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QTableWidget

from ui.venda.resumo_caixa_atual_dialog import Ui_ResumoCaixaAtualDialog
from utils.format_utils import formatar_moeda
from utils.table_widget_utils import set_table_item

class ResumoCaixaAtualDialog(QDialog, Ui_ResumoCaixaAtualDialog):
    def __init__(self, resumo: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._resumo = resumo
        self.setupUi(self)
        self.lblStatusBadge: QLabel
        self.lblPdvValor: QLabel
        self.lblOperadorValor: QLabel
        self.lblAberturaValor: QLabel
        self.lblFundoInicialValor: QLabel
        self.lblVendasDiaValor: QLabel
        self.lblFaturamentoTotalValor: QLabel
        self.lblFaturamentoDinheiroValor: QLabel
        self.lblSangriasValor: QLabel
        self.lblSuprimentosValor: QLabel
        self.lblTrocoValor: QLabel
        self.lblEsperadoValor: QLabel
        self.lblSaldoAtualValor: QLabel
        self.lblPagamentosVazio: QLabel
        self.tablePagamentos: QTableWidget
        self.setModal(True)
        self.btnFechar.clicked.connect(self.accept)
        self._popular_dados()

    def _popular_dados(self) -> None:
        self.lblStatusBadge.setText(str(self._resumo.get("status") or "Aberto"))
        self.lblPdvValor.setText(str(self._resumo.get("pdv_label") or "-"))
        self.lblOperadorValor.setText(str(self._resumo.get("operador") or "-"))
        self.lblAberturaValor.setText(str(self._resumo.get("data_abertura") or "-"))
        self.lblFundoInicialValor.setText(formatar_moeda(float(self._resumo.get("fundo_inicial") or 0.0)))
        self.lblVendasDiaValor.setText(str(int(self._resumo.get("vendas_dia") or 0)))
        self.lblFaturamentoTotalValor.setText(formatar_moeda(float(self._resumo.get("faturamento_total") or 0.0)))
        self.lblFaturamentoDinheiroValor.setText(formatar_moeda(float(self._resumo.get("faturamento_dinheiro") or 0.0)))
        self.lblSangriasValor.setText(formatar_moeda(float(self._resumo.get("total_sangrias") or 0.0)))
        self.lblSuprimentosValor.setText(formatar_moeda(float(self._resumo.get("total_suprimentos") or 0.0)))
        self.lblTrocoValor.setText(formatar_moeda(float(self._resumo.get("total_troco") or 0.0)))
        self.lblEsperadoValor.setText(formatar_moeda(float(self._resumo.get("total_esperado") or 0.0)))
        self.lblSaldoAtualValor.setText(formatar_moeda(float(self._resumo.get("saldo_atual") or 0.0)))
        self._popular_pagamentos()

    def _popular_pagamentos(self) -> None:
        totais = list(self._resumo.get("totais_forma_pagamento") or [])
        if totais:
            self.lblPagamentosVazio.hide()
            self.tablePagamentos.show()
            self.tablePagamentos.setRowCount(len(totais))
            for row_index, forma in enumerate(totais):
                set_table_item(self.tablePagamentos, row_index, 0, str(forma.get("forma_pagamento") or "Forma"))
                set_table_item(self.tablePagamentos, row_index, 1, f"{int(forma.get('qtd_vendas') or 0)} venda(s)")
                set_table_item(
                    self.tablePagamentos,
                    row_index,
                    2,
                    formatar_moeda(float(forma.get("total") or 0.0)),
                    alignment=Qt.AlignRight | Qt.AlignVCenter,
                )
        else:
            self.tablePagamentos.hide()
            self.tablePagamentos.setRowCount(0)
            self.lblPagamentosVazio.setText(
                "Nenhuma movimentacao de pagamento registrada ainda para este caixa."
            )
            self.lblPagamentosVazio.show()
