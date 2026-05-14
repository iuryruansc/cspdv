import sys

from PyQt5.QtWidgets import QApplication

from modules.venda.views.resumo_caixa_atual_dialog import ResumoCaixaAtualDialog
from utils.format_utils import formatar_moeda

_app = QApplication.instance() or QApplication(sys.argv)


def _resumo(**overrides):
    resumo = {
        "status": "Aberto",
        "pdv_label": "PDV-01 - Caixa Principal",
        "operador": "Iury",
        "data_abertura": "14/05/2026 09:00",
        "fundo_inicial": 50.0,
        "vendas_dia": 3,
        "faturamento_total": 149.9,
        "faturamento_dinheiro": 80.0,
        "total_sangrias": 10.0,
        "total_suprimentos": 5.0,
        "total_troco": 2.0,
        "total_esperado": 123.5,
        "saldo_atual": 123.5,
        "totais_forma_pagamento": [
            {"forma_pagamento": "Dinheiro", "qtd_vendas": 2, "total": 80.0},
            {"forma_pagamento": "PIX", "qtd_vendas": 1, "total": 69.9},
        ],
    }
    resumo.update(overrides)
    return resumo


class TestResumoCaixaAtualDialog:
    def test_popula_labels_e_pagamentos(self):
        dialog = ResumoCaixaAtualDialog(_resumo())

        assert dialog.lblStatusBadge.text() == "Aberto"
        assert dialog.lblPdvValor.text() == "PDV-01 - Caixa Principal"
        assert dialog.lblFundoInicialValor.text() == formatar_moeda(50.0)
        assert dialog.lblFaturamentoTotalValor.text() == formatar_moeda(149.9)
        assert dialog.tablePagamentos.rowCount() == 2
        assert dialog.tablePagamentos.item(0, 0).text() == "Dinheiro"
        assert dialog.tablePagamentos.item(0, 2).text() == formatar_moeda(80.0)

    def test_exibe_mensagem_quando_nao_ha_pagamentos(self):
        dialog = ResumoCaixaAtualDialog(_resumo(totais_forma_pagamento=[]))

        assert dialog.tablePagamentos.rowCount() == 0
        assert dialog.tablePagamentos.isHidden() is True
        assert dialog.lblPagamentosVazio.isHidden() is False
        assert "nenhuma movimentacao" in dialog.lblPagamentosVazio.text().lower()
