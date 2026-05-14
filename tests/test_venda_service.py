"""
    python -m pytest tests/test_venda_service.py -v
"""

from unittest.mock import patch

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.venda.services.venda_service import VendaService

class TestVendaService:
    def setup_method(self):
        CaixaSession.close()
        SessionManager.logout()

    def teardown_method(self):
        CaixaSession.close()
        SessionManager.logout()

    @staticmethod
    def _venda_base():
        return {
            "numero_venda": 12,
            "cliente_id": 5,
            "itens": [{"id": 10, "quantidade": 2, "total": 15.0}],
            "pagamentos": [{"forma": "Dinheiro", "valor": 15.0}],
            "total": 15.0,
            "desconto_global": 0.0,
        }

    def _abrir_contexto(self):
        CaixaSession.open({"id": 1})
        SessionManager.login(
            {"id": 7, "funcionario_id": 70, "nome": "Operador", "permissoes": []},
            persist=False,
        )

    def test_bloqueia_item_sem_produto_valido(self):
        self._abrir_contexto()
        venda = self._venda_base()
        venda["itens"] = [{"id": 0, "quantidade": 1, "total": 10.0}]

        sucesso, mensagem, resultado = VendaService.finalizar_venda(venda)

        assert sucesso is False
        assert resultado is None
        assert "produto válido" in mensagem

    def test_bloqueia_pagamento_sem_forma(self):
        self._abrir_contexto()
        venda = self._venda_base()
        venda["pagamentos"] = [{"valor": 15.0}]

        sucesso, mensagem, resultado = VendaService.finalizar_venda(venda)

        assert sucesso is False
        assert resultado is None
        assert "forma de pagamento" in mensagem

    def test_bloqueia_venda_sem_pendencia_com_total_pago_insuficiente(self):
        self._abrir_contexto()
        venda = self._venda_base()
        venda["pagamentos"] = [{"forma": "Dinheiro", "valor": 10.0}]

        sucesso, mensagem, resultado = VendaService.finalizar_venda(venda)

        assert sucesso is False
        assert resultado is None
        assert "insuficiente" in mensagem

    def test_bloqueia_pendencia_sem_data_vencimento(self):
        self._abrir_contexto()
        venda = self._venda_base()
        venda["pagamentos"] = [{"forma": "Dinheiro", "valor": 5.0}]
        venda["finalizar_com_pendencia"] = True
        venda["valor_em_aberto"] = 10.0
        venda["data_vencimento"] = ""

        sucesso, mensagem, resultado = VendaService.finalizar_venda(venda)

        assert sucesso is False
        assert resultado is None
        assert "data de vencimento" in mensagem

    @patch("modules.venda.services.venda_service.VendaModel.registrar_venda")
    def test_aceita_item_com_id_do_cupom_sem_produto_id(self, mock_registrar):
        self._abrir_contexto()
        mock_registrar.return_value = 321
        venda = self._venda_base()

        sucesso, mensagem, resultado = VendaService.finalizar_venda(venda)

        assert sucesso is True
        assert resultado is not None

        _, kwargs = mock_registrar.call_args
        assert kwargs["itens"][0]["id"] == 10

    @patch("modules.venda.services.venda_service.VendaModel.registrar_venda")
    def test_finaliza_venda_com_payload_normalizado(self, mock_registrar):
        self._abrir_contexto()
        mock_registrar.return_value = 123
        venda = self._venda_base()

        sucesso, mensagem, resultado = VendaService.finalizar_venda(venda)

        assert sucesso is True
        assert "sucesso" in mensagem.lower()
        assert resultado is not None
        assert resultado["numero_venda"] == 123

        _, kwargs = mock_registrar.call_args
        assert kwargs["cliente_id"] == 5
        assert kwargs["caixa_id"] == 1
        assert kwargs["status_venda"] == "CONCLUIDA"
        assert kwargs["itens"][0]["id"] == 10
        assert kwargs["pagamentos"][0]["forma"] == "Dinheiro"
