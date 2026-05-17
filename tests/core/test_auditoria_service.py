import json
from unittest.mock import patch

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.auditoria.services.auditoria_service import AuditoriaService


class TestAuditoriaService:
    def setup_method(self):
        CaixaSession.close()
        SessionManager.logout()

    def teardown_method(self):
        CaixaSession.close()
        SessionManager.logout()

    @patch("modules.auditoria.services.auditoria_service.AuditoriaModel.registrar_evento")
    def test_registrar_evento_usa_contexto_de_sessao_e_serializa_detalhes(self, mock_registrar):
        SessionManager.login({"id": 10, "nome": "Operador", "permissoes": []}, persist=False)
        CaixaSession.open({"id": 7, "usuario_id": 10, "pdv_label": "PDV-01"})

        sucesso = AuditoriaService.registrar_evento(
            evento="Recebimento_Pendencia",
            categoria="Financeiro",
            entidade="Conta_Receber",
            entidade_id=55,
            detalhes={"valor": "10.00", "status": "RECEBIDO"},
        )

        assert sucesso is True
        _, kwargs = mock_registrar.call_args
        assert kwargs["evento"] == "recebimento_pendencia"
        assert kwargs["categoria"] == "financeiro"
        assert kwargs["entidade"] == "conta_receber"
        assert kwargs["entidade_id"] == 55
        assert kwargs["usuario_id"] == 10
        assert kwargs["caixa_id"] == 7
        assert json.loads(kwargs["detalhes_json"]) == {"status": "RECEBIDO", "valor": "10.00"}

    @patch("modules.auditoria.services.auditoria_service.log_warning")
    @patch("modules.auditoria.services.auditoria_service.AuditoriaModel.registrar_evento", side_effect=RuntimeError("falha"))
    def test_registrar_evento_retorna_false_quando_model_falha(self, _mock_registrar, mock_warning):
        sucesso = AuditoriaService.registrar_evento(evento="teste", categoria="core")

        assert sucesso is False
        mock_warning.assert_called_once()
