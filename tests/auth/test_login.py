"""
    python -m pytest tests/test_login.py -v
"""

import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication, QDialog

from core.session_manager import SessionManager
from modules.auth.views.login_view import LoginView
from modules.auth.views.selecao_modo_view import SelecaoModoView

_app = QApplication.instance() or QApplication(sys.argv)

class TestLoginView:
    def setup_method(self):
        SessionManager.logout()
        LoginView.usuario_logado = None

    def teardown_method(self):
        SessionManager.logout()
        LoginView.usuario_logado = None

    @patch("modules.auth.views.login_view.UsuarioModel.autenticar")
    def test_exibe_erro_quando_campos_obrigatorios_estao_vazios(self, mock_autenticar):
        view = LoginView()
        view.show()

        view.lineEditLogin.setText("")
        view.lineEditSenha.setText("")
        view._login()

        assert view.labelErro.isVisible() is True
        assert "preencha os campos corretamente" in view.labelErro.text().lower()
        mock_autenticar.assert_not_called()

    @patch("modules.auth.views.login_view.UsuarioModel.autenticar", return_value=None)
    def test_exibe_erro_quando_credenciais_sao_invalidas(self, _mock_autenticar):
        view = LoginView()
        view.show()

        view.lineEditLogin.setText("operador")
        view.lineEditSenha.setText("errada")
        view._login()

        assert view.labelErro.isVisible() is True
        assert "inv" in view.labelErro.text().lower()
        assert view.result() != QDialog.Accepted

    @patch("modules.auth.views.login_view.SessionManager.session_persistence_enabled", return_value=False)
    @patch("modules.auth.views.login_view.UsuarioModel.autenticar")
    def test_login_valido_autentica_sessao_e_aceita_dialog(self, mock_autenticar, _mock_persistencia):
        usuario = {
            "id": 1,
            "nome": "Operador Teste",
            "login": "operador",
            "permissoes": ["vendas.pdv"],
        }
        mock_autenticar.return_value = usuario
        view = LoginView()

        view.lineEditLogin.setText("operador")
        view.lineEditSenha.setText("123")
        view._login()

        atual = SessionManager.current_user()
        assert view.result() == QDialog.Accepted
        assert atual is not None
        assert atual["nome"] == "Operador Teste"
        assert LoginView.usuario_logado is not None
        assert LoginView.usuario_logado["id"] == 1

class TestSelecaoModoView:
    @patch("modules.auth.views.selecao_modo_view.aplicar_tamanho_proporcional_tela")
    @patch("modules.auth.views.selecao_modo_view.descricao_ambiente", return_value="Ambiente de teste")
    @patch("modules.auth.views.selecao_modo_view.versao_referencia", return_value="CSPdv v1.0.0")
    @patch("modules.auth.views.selecao_modo_view.SessionManager.current_user")
    @patch("modules.auth.views.selecao_modo_view.SessionManager.has_permission")
    def test_exibe_operador_e_respeita_permissoes(
        self,
        mock_has_permission,
        mock_current_user,
        _mock_versao,
        _mock_ambiente,
        _mock_tamanho,
    ):
        mock_current_user.return_value = {
            "id": 7,
            "nome": "Iury",
            "permissoes": ["vendas.pdv", "financeiro.total"],
        }
        permissoes = {"vendas.pdv", "financeiro.total"}
        mock_has_permission.side_effect = lambda chave: chave in permissoes

        view = SelecaoModoView()

        assert view.lblOperadorNome.text() == "OPERADOR: IURY"
        assert view.lblVersao.text() == "CSPdv v1.0.0"
        assert view.shortcut_f1.isEnabled() is True
        assert view.shortcut_f2.isEnabled() is False
        assert view.shortcut_f3.isEnabled() is False
        assert view.shortcut_f4.isEnabled() is True
        assert view.shortcut_f5.isEnabled() is False
        assert view.cardFrenteCaixa.isHidden() is False
        assert view.cardAdmin.isHidden() is True
        assert view.cardEstoque.isHidden() is True
        assert view.cardFinanceiro.isHidden() is False
        assert view.cardRelatorios.isHidden() is True

    @patch("modules.auth.views.selecao_modo_view.aplicar_tamanho_proporcional_tela")
    @patch("modules.auth.views.selecao_modo_view.descricao_ambiente", return_value="Ambiente de teste")
    @patch("modules.auth.views.selecao_modo_view.versao_referencia", return_value="CSPdv v1.0.0")
    @patch("modules.auth.views.selecao_modo_view.SessionManager.current_user", return_value=None)
    @patch("modules.auth.views.selecao_modo_view.SessionManager.has_permission", return_value=False)
    def test_exibe_operador_nao_logado_sem_permissoes(
        self,
        _mock_has_permission,
        _mock_current_user,
        _mock_versao,
        _mock_ambiente,
        _mock_tamanho,
    ):
        view = SelecaoModoView()

        assert view.lblOperadorNome.text() == "OPERADOR: NÃO LOGADO"
        assert view.shortcut_f1.isEnabled() is False
        assert view.shortcut_f2.isEnabled() is False
        assert view.shortcut_f3.isEnabled() is False
        assert view.shortcut_f4.isEnabled() is False
        assert view.shortcut_f5.isEnabled() is False
