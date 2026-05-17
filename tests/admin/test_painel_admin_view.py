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

    def test_dashboard_reorganizado_destaca_alertas_e_enxuga_acoes(self):
        view = self._criar_view()

        assert view.lblAcoesTitle.text() == "Ações Essenciais"
        assert view.lblConfigEstruturalTitle.text() == "Operação e Sistema"
        assert view.lblAlertasDashboardTitle.text() == "Alertas Prioritários"
        assert view.btnAcaoCadUsuario.isHidden() is True
        assert view.btnAcaoCadPermissao.isHidden() is True


    def test_subnav_por_grupo_filtra_botoes_relevantes(self):
        view = self._criar_view()

        view._show_management_page("produtos")
        assert view.btnNavProdutosCadastro.isHidden() is False
        assert view.btnNavMarcas.isHidden() is False
        assert view.btnNavCaixas.isHidden() is True
        assert view.frameSubNavBar.isHidden() is False

        view._show_management_page("formas_pagamento")
        assert view.btnNavFormasPagamento.isHidden() is False
        assert view.btnNavCaixas.isHidden() is False
        assert view.btnNavProdutosCadastro.isHidden() is True

        view._show_dashboard()
        assert view.frameSubNavBar.isHidden() is True

        view._show_management_page("auditoria")
        assert view.frameSubNavBar.isHidden() is True
        assert view.btnNavAuditoria.isChecked() is True

    @patch("modules.auditoria.services.auditoria_service.AuditoriaService.listar_eventos", return_value=[])
    def test_area_auditoria_abre_management_page_real(self, _mock_listar):
        view = self._criar_view()

        view.btnNavAuditoria.click()

        assert view.managementPage.isHidden() is False
        assert view.managementPage.lblTitle.text() == "Auditoria"
        assert view.managementPage.btnNovo.isHidden() is True
        assert view.managementPage.btnDetalhes.isHidden() is False

    @patch(
        "modules.auditoria.services.auditoria_service.AuditoriaService.obter_evento_detalhado",
        return_value={
            "id": 7,
            "data_hora": "17/05/2026 17:30:00",
            "categoria_label": "Caixa",
            "evento_label": "Abertura",
            "usuario_label": "Iury",
            "caixa_label": "Caixa #3",
            "pdv_identificacao": "PDV-01",
            "entidade_label": "Caixa",
            "entidade_id": 3,
            "detalhes_formatados": "{\n  \"fundo\": 50\n}",
        },
    )
    def test_detalhes_auditoria_abre_resumo_do_evento(self, _mock_detalhes):
        view = self._criar_view()
        row = {"id": 7}

        with patch.object(view, "_obter_registro_selecionado", return_value=row), patch(
            "modules.admin.views.painel_admin_view.mostrar_info"
        ) as mock_info:
            view._abrir_detalhes_auditoria()

        mock_info.assert_called_once()
        assert "Auditoria #7" in mock_info.call_args[0][1]

    @patch("modules.pdvs.models.pdv_model.PdvModel.listar", return_value=[])
    def test_area_pdvs_abre_management_page_real(self, _mock_listar):
        view = self._criar_view()

        view.btnNavPdvs.click()

        assert view.managementPage.isHidden() is False
        assert view.placeholderPage.isHidden() is True
        assert view.managementPage.lblTitle.text() == "PDVs"
        assert view.btnNavPdvs.isHidden() is False

    @patch("modules.unidades.models.unidade_model.UnidadeModel.listar", return_value=[])
    def test_area_unidades_abre_management_page_real(self, _mock_listar):
        view = self._criar_view()

        view.btnNavUnidades.click()

        assert view.managementPage.isHidden() is False
        assert view.placeholderPage.isHidden() is True
        assert view.managementPage.lblTitle.text() == "Unidades"
        assert view.btnNavUnidades.isHidden() is False

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

    def test_cliente_sistema_nao_abre_edicao(self):
        view = self._criar_view()
        row = {"id": 1, "nome": "Consumidor Final", "cliente_sistema": "S"}

        with patch.object(view, "_obter_registro_selecionado", return_value=row), patch(
            "modules.admin.views.painel_admin_view.mostrar_aviso"
        ) as mock_aviso:
            view._current_management_key = "clientes"
            view._editar_registro()

        mock_aviso.assert_called_once()

    def test_cliente_sistema_nao_altera_status(self):
        view = self._criar_view()
        row = {"id": 1, "nome": "Consumidor Final", "cliente_sistema": "S", "ativo": "S"}

        with patch.object(view, "_obter_registro_selecionado", return_value=row), patch(
            "modules.admin.views.painel_admin_view.mostrar_aviso"
        ) as mock_aviso:
            view._current_management_key = "clientes"
            view._toggle_registro_ativo()

        mock_aviso.assert_called_once()
