"""
    python -m pytest tests/test_abertura_caixa_view.py -v
"""

import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.venda.views.abertura_caixa_view import AberturaCaixaView

_app = QApplication.instance() or QApplication(sys.argv)

class TestAberturaCaixaView:
    @patch("modules.venda.views.abertura_caixa_view.CaixaService.listar_ultimas_aberturas", return_value=[])
    @patch("modules.venda.views.abertura_caixa_view.ConfiguracoesService.carregar_parametros_caixa")
    @patch("modules.venda.views.abertura_caixa_view.ConfiguracoesService.carregar_empresa_pdv")
    @patch("modules.venda.views.abertura_caixa_view.CaixaService.listar_pdvs_ativos")
    @patch("modules.venda.views.abertura_caixa_view.SessionManager.current_user")
    def test_preseleciona_pdv_padrao_quando_configurado(
        self,
        mock_usuario,
        mock_pdvs,
        mock_empresa,
        mock_parametros_caixa,
        _mock_historico,
    ):
        mock_usuario.return_value = {"id": 1, "nome": "Operador"}
        mock_parametros_caixa.return_value = {"fundo_inicial_sugerido": 50.0}
        mock_empresa.return_value = {"empresa": {"pdv_padrao_id": 2, "moeda_padrao": "BRL"}, "pdvs": []}
        mock_pdvs.return_value = [
            {"id": 1, "identificacao": "PDV-01", "descricao": "Caixa 1"},
            {"id": 2, "identificacao": "PDV-02", "descricao": "Caixa 2"},
        ]

        view = AberturaCaixaView()

        assert view.comboNumCaixa.currentIndex() == 1
        assert view.comboNumCaixa.currentText() == "PDV-02 - Caixa 2"
        assert view.lineEditTrocoInicial.text() == "50,00"
