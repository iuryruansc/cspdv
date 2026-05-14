"""
    python -m pytest tests/test_currency_runtime.py -v
"""

from unittest.mock import patch

from utils.currency_runtime import codigo_moeda_padrao, simbolo_moeda_padrao
from utils.format_utils import formatar_moeda

class TestCurrencyRuntime:
    @patch("modules.admin.services.configuracoes_service.ConfiguracoesModel.carregar_empresa_pdv")
    def test_codigo_moeda_padrao_retorna_brl_por_default(self, mock_carregar):
        mock_carregar.return_value = {}

        assert codigo_moeda_padrao() == "BRL"
        assert simbolo_moeda_padrao() == "R$"

    @patch("modules.admin.services.configuracoes_service.ConfiguracoesModel.carregar_empresa_pdv")
    def test_simbolo_moeda_padrao_reflete_usd(self, mock_carregar):
        mock_carregar.return_value = {"moeda_padrao": "USD"}

        assert codigo_moeda_padrao() == "USD"
        assert simbolo_moeda_padrao() == "US$"
        assert formatar_moeda(12.5) == "US$ 12,50"
