import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.venda.views.movimentacao_caixa_view import MovimentacaoCaixaView

_app = QApplication.instance() or QApplication(sys.argv)


def _parametros_caixa(**overrides):
    params = {
        "exigir_admin_sangria": True,
    }
    params.update(overrides)
    return params


def _resumo_movimentacoes(**overrides):
    resumo = {
        "saldo_atual": 120.0,
        "total_sangrias": 15.0,
        "total_suprimentos": 10.0,
        "total_troco": 5.0,
    }
    resumo.update(overrides)
    return resumo


def _historico_item(**overrides):
    item = {
        "hora_fmt": "10:15",
        "tipo_descricao": "Sangria",
        "valor": 15.0,
        "operador": "Iury",
        "observacao": "Retirada",
    }
    item.update(overrides)
    return item


class TestMovimentacaoCaixaView:
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.listar_movimentacoes")
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.obter_resumo_movimentacoes")
    @patch("modules.venda.views.movimentacao_caixa_view.ConfiguracoesService.carregar_parametros_caixa")
    def test_carrega_resumo_e_historico(
        self,
        mock_parametros,
        mock_resumo,
        mock_historico,
    ):
        mock_parametros.return_value = _parametros_caixa()
        mock_resumo.return_value = _resumo_movimentacoes()
        mock_historico.return_value = [_historico_item()]

        view = MovimentacaoCaixaView()

        assert view.lblSaldoValor.text() == "R$ 120,00"
        assert view.lblSaldoAtualValor2.text() == "R$ 120,00"
        assert view.lblTotalSangriaValor.text() == "R$ 15,00"
        assert view.lblTotalSupValor.text() == "R$ 15,00"
        assert view.tableHistorico.rowCount() == 1

    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.listar_movimentacoes", return_value=[])
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.obter_resumo_movimentacoes")
    @patch("modules.venda.views.movimentacao_caixa_view.ConfiguracoesService.carregar_parametros_caixa")
    def test_regra_admin_muda_conforme_tipo(
        self,
        mock_parametros,
        mock_resumo,
        _mock_historico,
    ):
        mock_parametros.return_value = _parametros_caixa(exigir_admin_sangria=True)
        mock_resumo.return_value = _resumo_movimentacoes()
        view = MovimentacaoCaixaView()

        view._definir_tipo("sangria")
        assert view.lineEditSenhaAdmin.isEnabled() is True

        view._definir_tipo("suprimento")
        assert view.lineEditSenhaAdmin.isEnabled() is False

    @patch("modules.venda.views.movimentacao_caixa_view.mostrar_info")
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.registrar_movimentacao")
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.listar_movimentacoes", return_value=[])
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.obter_resumo_movimentacoes")
    @patch("modules.venda.views.movimentacao_caixa_view.ConfiguracoesService.carregar_parametros_caixa")
    def test_registrar_movimentacao_com_sucesso_recarrega_tela_e_emite_sinal(
        self,
        mock_parametros,
        mock_resumo,
        _mock_historico,
        mock_registrar,
        mock_info,
    ):
        mock_parametros.return_value = _parametros_caixa()
        mock_resumo.return_value = _resumo_movimentacoes()
        mock_registrar.return_value = (True, "Movimentação registrada com sucesso.")
        view = MovimentacaoCaixaView()
        emitidos = []
        view.movimentacao_registrada.connect(lambda: emitidos.append(True))
        view.lineEditValor.setText("12,50")
        view.lineEditDescricao.setText("Suprimento do caixa")
        view.lineEditSenhaAdmin.setText("123")

        view._registrar_movimentacao()

        mock_registrar.assert_called_once()
        mock_info.assert_called_once()
        assert emitidos == [True]
        assert view.lineEditValor.text() == "0,00"
        assert view.lineEditDescricao.text() == ""

    @patch("modules.venda.views.movimentacao_caixa_view.mostrar_aviso")
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.registrar_movimentacao")
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.listar_movimentacoes", return_value=[])
    @patch("modules.venda.views.movimentacao_caixa_view.CaixaService.obter_resumo_movimentacoes")
    @patch("modules.venda.views.movimentacao_caixa_view.ConfiguracoesService.carregar_parametros_caixa")
    def test_registrar_movimentacao_com_falha_exibe_aviso(
        self,
        mock_parametros,
        mock_resumo,
        _mock_historico,
        mock_registrar,
        mock_aviso,
    ):
        mock_parametros.return_value = _parametros_caixa()
        mock_resumo.return_value = _resumo_movimentacoes()
        mock_registrar.return_value = (False, "Senha de administrador obrigatória.")
        view = MovimentacaoCaixaView()
        view.lineEditValor.setText("12,50")

        view._registrar_movimentacao()

        mock_registrar.assert_called_once()
        mock_aviso.assert_called_once()
