"""
    python -m pytest tests/test_session_manager.py -v
"""

from core.session_manager import SessionManager

class TestSessionManager:
    def setup_method(self):
        SessionManager.logout()

    def teardown_method(self):
        SessionManager.logout()

    def test_login_autentica_usuario(self):
        usuario = {
            "id": 1,
            "nome": "Admin",
            "permissoes": ["vendas.pdv"],
        }

        SessionManager.login(usuario)

        current_user = SessionManager.current_user()
        assert SessionManager.is_authenticated() is True
        assert current_user is not None
        assert current_user["nome"] == "Admin"

    def test_logout_limpa_sessao(self):
        SessionManager.login({"id": 1, "nome": "Admin", "permissoes": []})

        SessionManager.logout()

        assert SessionManager.is_authenticated() is False
        assert SessionManager.current_user() is None

    def test_current_user_retorna_copia(self):
        usuario = {
            "id": 1,
            "nome": "Admin",
            "permissoes": ["vendas.pdv"],
        }
        SessionManager.login(usuario)

        atual = SessionManager.current_user()
        assert atual is not None
        atual["nome"] = "Alterado"
        atual["permissoes"].append("financeiro.total")

        persistido = SessionManager.current_user()
        assert persistido is not None
        assert persistido["nome"] == "Admin"
        assert persistido["permissoes"] == ["vendas.pdv"]

    def test_has_permission_sem_usuario_retorna_false(self):
        assert SessionManager.has_permission("vendas.pdv") is False

    def test_has_permission_retorna_true_para_permissao_explicita(self):
        SessionManager.login(
            {"id": 1, "nome": "Operador", "permissoes": ["vendas.pdv"]}
        )

        assert SessionManager.has_permission("vendas.pdv") is True
        assert SessionManager.has_permission("financeiro.total") is False

    def test_has_permission_master_liberaliza_tudo(self):
        SessionManager.login(
            {"id": 1, "nome": "Master", "permissoes": ["sistema.master"]}
        )

        assert SessionManager.has_permission("vendas.pdv") is True
        assert SessionManager.has_permission("financeiro.total") is True

    def test_diagnostics_reflete_estado_da_sessao(self):
        SessionManager.login(
            {
                "id": 10,
                "nome": "Supervisor",
                "permissoes": ["vendas.pdv", "estoque.gerenciar"],
            }
        )

        diagnostics = SessionManager.diagnostics()

        assert diagnostics["authenticated"] is True
        assert diagnostics["user_id"] == 10
        assert diagnostics["user_name"] == "Supervisor"
        assert diagnostics["permissions_count"] == 2
        assert diagnostics["started_at"] is not None
