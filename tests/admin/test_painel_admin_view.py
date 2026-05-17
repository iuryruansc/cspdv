import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.admin.views.painel_admin_view import PainelAdminView

_app = QApplication.instance() or QApplication(sys.argv)


class TestPainelAdminView:
    @staticmethod
    def _criar_view():
        with patch.object(PainelAdminView, "_show_dashboard", lambda self: None), patch(
            "modules.admin.views.painel_admin_view.aplicar_tamanho_proporcional_tela"
        ), patch(
            "modules.admin.views.painel_admin_view.SessionManager.current_user",
            return_value={"id": 1, "nome": "Iury", "permissoes": ["vendas.pdv"]},
        ):
            return PainelAdminView()

    @patch("modules.venda.services.caixa_service.CaixaService.listar_caixas_admin", return_value=[])
    @patch("core.caixa_session.CaixaSession.has_open_caixa", return_value=True)
    def test_area_caixas_mostra_fechar_quando_ha_caixa_aberto(self, _mock_caixa_aberto, _mock_listar):
        view = self._criar_view()

        with patch.object(view, "_open_fechamento_caixa_dashboard") as mock_fechar:
            view._show_management_page("caixas")
            view._atualizar_acao_caixa_management_page()
            view.managementPage.btnNovo.click()

        assert view.managementPage.btnNovo.text() == "Fechar caixa"
        mock_fechar.assert_called_once()

    @patch("modules.venda.services.caixa_service.CaixaService.listar_caixas_admin", return_value=[])
    @patch("modules.venda.services.caixa_service.CaixaService.restaurar_caixa_aberto", return_value=None)
    @patch("core.caixa_session.CaixaSession.has_open_caixa", side_effect=[False, False, False, False])
    def test_area_caixas_mostra_abrir_quando_nao_ha_caixa_aberto(
        self,
        _mock_caixa_aberto,
        mock_restaurar,
        _mock_listar,
    ):
        view = self._criar_view()

        with patch.object(view, "_open_frente_caixa") as mock_abrir:
            view._show_management_page("caixas")
            view._atualizar_acao_caixa_management_page()
            view.managementPage.btnNovo.click()

        assert view.managementPage.btnNovo.text() == "Abrir caixa"
        mock_restaurar.assert_called()
        mock_abrir.assert_called_once()
