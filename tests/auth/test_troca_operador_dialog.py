import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication, QDialog

from core.session_manager import SessionManager
from modules.auth.views.troca_operador_dialog import TrocaOperadorDialog

_app = QApplication.instance() or QApplication(sys.argv)


class TestTrocaOperadorDialog:
    def setup_method(self):
        SessionManager.logout()

    def teardown_method(self):
        SessionManager.logout()

    @patch("modules.auth.views.troca_operador_dialog.CaixaSession.current", return_value={"pdv_label": "PDV-01", "valor_abertura": 50.0})
    @patch("modules.auth.views.troca_operador_dialog.SessionManager.session_persistence_enabled", return_value=False)
    @patch("modules.auth.views.troca_operador_dialog.UsuarioModel.autenticar")
    def test_confirma_troca_de_operador_valida(
        self,
        mock_autenticar,
        _mock_persistencia,
        _mock_caixa,
    ):
        SessionManager.login({"id": 1, "nome": "Operador Atual", "permissoes": ["vendas.pdv"]}, persist=False)
        mock_autenticar.return_value = {"id": 2, "nome": "Operador Novo", "permissoes": ["vendas.pdv"]}

        dialog = TrocaOperadorDialog()
        dialog.lineEditLogin.setText("novo")
        dialog.lineEditSenha.setText("123")
        dialog._confirmar_troca()

        atual = SessionManager.current_user()
        assert dialog.result() == QDialog.Accepted
        assert atual is not None
        assert atual["id"] == 2
        assert dialog.novo_operador is not None

    @patch("modules.auth.views.troca_operador_dialog.CaixaSession.current", return_value={"pdv_label": "PDV-01", "valor_abertura": 50.0})
    @patch("modules.auth.views.troca_operador_dialog.SessionManager.session_persistence_enabled", return_value=False)
    @patch("modules.auth.views.troca_operador_dialog.UsuarioModel.autenticar")
    def test_bloqueia_quando_operador_novo_e_igual_ao_atual(
        self,
        mock_autenticar,
        _mock_persistencia,
        _mock_caixa,
    ):
        SessionManager.login({"id": 1, "nome": "Operador Atual", "permissoes": ["vendas.pdv"]}, persist=False)
        mock_autenticar.return_value = {"id": 1, "nome": "Operador Atual", "permissoes": ["vendas.pdv"]}

        dialog = TrocaOperadorDialog()
        dialog.lineEditLogin.setText("mesmo")
        dialog.lineEditSenha.setText("123")
        dialog._confirmar_troca()

        assert dialog.result() != QDialog.Accepted
        assert "operador diferente" in dialog.lblErro.text().lower()

    @patch("modules.auth.views.troca_operador_dialog.CaixaSession.current", return_value={"pdv_label": "PDV-01", "valor_abertura": 50.0})
    @patch("modules.auth.views.troca_operador_dialog.SessionManager.session_persistence_enabled", return_value=False)
    @patch("modules.auth.views.troca_operador_dialog.UsuarioModel.autenticar")
    def test_bloqueia_operador_sem_permissao_de_pdv(
        self,
        mock_autenticar,
        _mock_persistencia,
        _mock_caixa,
    ):
        SessionManager.login({"id": 1, "nome": "Operador Atual", "permissoes": ["vendas.pdv"]}, persist=False)
        mock_autenticar.return_value = {"id": 2, "nome": "Sem PDV", "permissoes": ["financeiro.total"]}

        dialog = TrocaOperadorDialog()
        dialog.lineEditLogin.setText("sem_pdv")
        dialog.lineEditSenha.setText("123")
        dialog._confirmar_troca()

        assert dialog.result() != QDialog.Accepted
        assert "não possui permissão" in dialog.lblErro.text().lower()
