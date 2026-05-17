import sys
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QApplication, QDialog

from modules.venda.views.pagamento_view import PagamentoView
from utils.format_utils import formatar_moeda

_app = QApplication.instance() or QApplication(sys.argv)


FORMAS_PAGAMENTO_PADRAO = [
    {"id": 1, "nome": "Dinheiro"},
    {"id": 2, "nome": "PIX"},
    {"id": 3, "nome": "Cartao Debito"},
    {"id": 4, "nome": "Cartao Credito"},
    {"id": 5, "nome": "Vale Refeicao"},
    {"id": 6, "nome": "Cheque"},
]


def _venda_data(**overrides):
    venda = {
        "numero_venda": 14,
        "cliente_id": 1,
        "cliente_nome": "Consumidor Final",
        "subtotal": 14.99,
        "desconto_global": 0.0,
        "desconto_itens": 0.0,
        "desconto_total": 0.0,
        "total": 14.99,
        "itens": [{"nome": "Bombom", "quantidade": 1, "total": 14.99}],
    }
    venda.update(overrides)
    return venda


class TestPagamentoView:
    @staticmethod
    def _criar_view():
        with patch(
            "modules.venda.views.pagamento_view.FinanceiroService.listar_formas_pagamento",
            return_value=FORMAS_PAGAMENTO_PADRAO,
        ):
            return PagamentoView()

    def test_lanca_pagamento_atualiza_tabela_e_resumo(self):
        view = self._criar_view()
        view.carregar_venda(_venda_data())
        view.lineEditValor.setText("10,00")

        view._lancar_pagamento()

        assert view.tableFormasPagamento.rowCount() == 1
        assert view.tableFormasPagamento.item(0, 0).text() == "Dinheiro"
        assert view.tableFormasPagamento.item(0, 1).text() == formatar_moeda(10.0)
        assert view.lblSomaTotalValor.text() == formatar_moeda(10.0)
        assert view.lblRestanteValor.text() == formatar_moeda(4.99)
        assert view.btnFinalizarPendencia.isEnabled() is True
        assert view.btnFecharPedido.isEnabled() is False

    def test_pagamento_exato_preenche_valor_restante(self):
        view = self._criar_view()
        view.carregar_venda(_venda_data(total=20.0))
        view._pagamentos = [{"forma": "PIX", "valor": 7.5}]

        view._usar_pagamento_exato()

        assert view.lineEditValor.text() == "12,50"

    def test_remover_pagamento_recalcula_resumo(self):
        view = self._criar_view()
        view.carregar_venda(_venda_data())
        view._pagamentos = [
            {"forma": "Dinheiro", "valor": 10.0},
            {"forma": "PIX", "valor": 4.99},
        ]
        view._renderizar_pagamentos()
        view._atualizar_resumo()

        view._ao_clicar_pagamento(0, 2)

        assert len(view._pagamentos) == 1
        assert view.tableFormasPagamento.rowCount() == 1
        assert view.lblSomaTotalValor.text() == formatar_moeda(4.99)

    def test_finalizar_pagamento_emite_payload(self):
        view = self._criar_view()
        view.carregar_venda(_venda_data())
        view._pagamentos = [{"forma": "Dinheiro", "valor": 14.99}]
        emitidos = []
        view.venda_finalizada.connect(lambda payload: emitidos.append(payload))

        view._finalizar_pagamento()

        assert len(emitidos) == 1
        payload = emitidos[0]
        assert payload["numero_venda"] == 14
        assert payload["cliente_nome"] == "Consumidor Final"
        assert payload["pagamentos"] == [{"forma": "Dinheiro", "valor": 14.99}]
        assert payload["troco"] == 0.0

    @patch("modules.venda.views.pagamento_view.FinalizarPendenciaDialog")
    def test_finalizar_com_pendencia_emite_payload_com_vencimento(self, mock_dialog_cls):
        dialog = MagicMock()
        dialog.exec_.return_value = QDialog.Accepted
        dialog.Accepted = QDialog.Accepted
        dialog.resultado = {"data_vencimento": "20/05/2026", "observacao": "Retorno"}
        mock_dialog_cls.return_value = dialog

        view = self._criar_view()
        view.carregar_venda(_venda_data(total=20.0))
        view._pagamentos = [{"forma": "Dinheiro", "valor": 5.0}]
        emitidos = []
        view.venda_finalizada.connect(lambda payload: emitidos.append(payload))

        view._finalizar_com_pendencia()

        assert len(emitidos) == 1
        payload = emitidos[0]
        assert payload["finalizar_com_pendencia"] is True
        assert payload["valor_em_aberto"] == 15.0
        assert payload["data_vencimento"] == "20/05/2026"
        assert payload["observacao_pendencia"] == "Retorno"

    def test_sincroniza_botoes_com_formas_ativas_do_admin(self):
        formas = [
            {"id": 7, "nome": "PIX"},
            {"id": 8, "nome": "Dinheiro"},
            {"id": 9, "nome": "Voucher Loja"},
        ]
        with patch("modules.venda.views.pagamento_view.FinanceiroService.listar_formas_pagamento", return_value=formas):
            view = PagamentoView()

        assert "Dinheiro" in view.btnDinheiro.text()
        assert "PIX" in view.btnPix.text()
        assert "Voucher Loja" in view.btnCartaoDebito.text()
        assert view.btnCartaoCredito.isHidden() is True
        assert view._forma_selecionada == "Dinheiro"
