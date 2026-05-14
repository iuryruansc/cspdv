import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.promocoes.views.painel_promocoes_view import PainelPromocoesView
from utils.format_utils import formatar_moeda

_app = QApplication.instance() or QApplication(sys.argv)


def _promocao(**overrides):
    promocao = {
        "id": 1,
        "codigo": "PROMO-001",
        "nome": "Oferta de Teste",
        "tipo_desconto": "PERCENTUAL",
        "status": "ATIVA",
        "vigencia": "14/05/2026 a 20/05/2026",
        "alcance": "3 produtos",
        "qtd_produtos": 3,
    }
    promocao.update(overrides)
    return promocao


def _item_promocao(**overrides):
    item = {
        "produto": "Chocolate 90G",
        "preco_original": 10.0,
        "preco_promocional": 8.0,
        "desconto_aplicado": 2.0,
        "observacao": "Desconto de campanha",
    }
    item.update(overrides)
    return item


class TestPainelPromocoesView:
    @patch("modules.promocoes.views.painel_promocoes_view.PromocaoService.listar_itens_promocao")
    @patch("modules.promocoes.views.painel_promocoes_view.PromocaoService.listar_promocoes")
    def test_renderiza_promocoes_e_metricas(self, mock_listar, mock_itens):
        mock_listar.return_value = [
            _promocao(),
            _promocao(id=2, codigo="PROMO-002", status="AGENDADA", qtd_produtos=1),
            _promocao(id=3, codigo="PROMO-003", status="ENCERRADA", qtd_produtos=0),
        ]
        mock_itens.return_value = [_item_promocao()]

        view = PainelPromocoesView()

        assert view.tablePromocoes.rowCount() == 3
        assert view.tablePromocoes.item(0, 0).text() == "PROMO-001"
        assert view.lblPromocoesAtivasValor.text() == "1"
        assert view.lblAgendadasValor.text() == "1"
        assert view.lblEncerradasValor.text() == "1"
        assert view.lblProdutosPromocaoValor.text() == "4"
        assert view.tableItensPromocao.rowCount() == 1
        assert view.tableItensPromocao.item(0, 1).text() == formatar_moeda(10.0)

    @patch("modules.promocoes.views.painel_promocoes_view.PromocaoService.listar_itens_promocao", return_value=[])
    @patch("modules.promocoes.views.painel_promocoes_view.PromocaoService.listar_promocoes")
    def test_filtro_por_busca_reduz_resultados(self, mock_listar, _mock_itens):
        mock_listar.return_value = [
            _promocao(nome="Oferta de Chocolate"),
            _promocao(id=2, codigo="PROMO-002", nome="Oferta de Refrigerante"),
        ]

        view = PainelPromocoesView()
        view.txtBuscaPromocao.setText("chocolate")
        view._aplicar_filtros()

        assert view.tablePromocoes.rowCount() == 1
        assert view.tablePromocoes.item(0, 1).text() == "Oferta de Chocolate"
