import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.venda.views.frente_loja_view import FrenteLojaView

_app = QApplication.instance() or QApplication(sys.argv)


class TestFrenteLojaView:
    @patch("modules.venda.views.frente_loja_view.aplicar_tamanho_proporcional_tela")
    @patch("modules.venda.views.frente_loja_view.SessionManager.current_user")
    @patch("modules.venda.views.frente_loja_view.CaixaService.restaurar_caixa_aberto")
    @patch("modules.venda.views.frente_loja_view.CaixaSession.has_open_caixa", return_value=False)
    def test_ao_abrir_caixa_redireciona_para_vendas(
        self,
        _mock_has_open_caixa,
        _mock_restaurar_caixa,
        mock_current_user,
        _mock_tamanho,
    ):
        mock_current_user.return_value = {"id": 1, "nome": "Iury", "permissoes": ["vendas.pdv"]}
        view = FrenteLojaView()

        with patch.object(view, "_aplicar_estado_caixa") as mock_estado, patch.object(
            view, "_atualizar_menu_lateral"
        ) as mock_menu, patch.object(view, "_mostrar_frente_venda") as mock_vendas:
            view._on_caixa_aberto({"pdv_label": "PDV-01 - Caixa Principal"})

        mock_estado.assert_called_once()
        mock_menu.assert_called_once_with(view.btnNavAbertura)
        mock_vendas.assert_called_once()
        assert "Caixa aberto com sucesso" in view.lblDefaultMsg.text()
