"""
    python -m pytest tests/test_reembolso_service.py -v
"""

from decimal import Decimal
from unittest.mock import patch

from core.session_manager import SessionManager
from modules.financeiro.services.reembolso_service import ReembolsoService

class TestReembolsoService:
    def setup_method(self):
        SessionManager.logout()

    def teardown_method(self):
        SessionManager.logout()

    @patch("modules.financeiro.services.reembolso_service.FinanceiroService.obter_venda_detalhada")
    def test_preparar_pagamentos_reembolso_distribui_proporcionalmente(self, mock_obter_venda):
        mock_obter_venda.return_value = {
            "pagamentos": [
                {"forma_pagamento": "Dinheiro", "valor_pago": Decimal("10.00")},
                {"forma_pagamento": "Cartão", "valor_pago": Decimal("20.00")},
            ]
        }

        distribuicao = ReembolsoService.preparar_pagamentos_reembolso(99, Decimal("15.00"))

        assert len(distribuicao) == 2
        assert distribuicao[0]["forma_pagamento"] == "Dinheiro"
        assert distribuicao[0]["valor"] == Decimal("5.00")
        assert distribuicao[1]["forma_pagamento"] == "Cartão"
        assert distribuicao[1]["valor"] == Decimal("10.00")
        assert sum((item["valor"] for item in distribuicao), Decimal("0.00")) == Decimal("15.00")

    def test_registrar_reembolso_sem_usuario_logado_retorna_erro(self):
        sucesso, mensagem, resultado = ReembolsoService.registrar_reembolso({"venda_id": 1})

        assert sucesso is False
        assert resultado is None
        assert "operador" in mensagem.lower()

    @patch("modules.financeiro.services.reembolso_service.FinanceiroService.obter_venda_detalhada")
    def test_registrar_reembolso_bloqueia_quantidade_maior_que_disponivel(self, mock_obter_venda):
        SessionManager.login({"id": 7, "nome": "Operador", "permissoes": []}, persist=False)
        mock_obter_venda.return_value = {
            "itens": [
                {
                    "item_venda_id": 10,
                    "produto_id": 1,
                    "lote_id": 0,
                    "quantidade_disponivel": 2,
                    "preco_unitario": "7.50",
                }
            ]
        }

        sucesso, mensagem, resultado = ReembolsoService.registrar_reembolso(
            {
                "venda_id": 1,
                "motivo": "Cliente desistiu",
                "tipo": "PARCIAL",
                "itens": [{"item_venda_id": 10, "quantidade": 3}],
            }
        )

        assert sucesso is False
        assert resultado is None
        assert "excede o saldo disponível" in mensagem

    @patch("modules.financeiro.services.reembolso_service.FinanceiroService.obter_venda_detalhada")
    def test_registrar_reembolso_soma_quantidades_repetidas_do_mesmo_item(self, mock_obter_venda):
        SessionManager.login({"id": 7, "nome": "Operador", "permissoes": []}, persist=False)
        mock_obter_venda.return_value = {
            "itens": [
                {
                    "item_venda_id": 10,
                    "produto_id": 1,
                    "lote_id": 0,
                    "quantidade_disponivel": 2,
                    "preco_unitario": "7.50",
                }
            ]
        }

        sucesso, mensagem, resultado = ReembolsoService.registrar_reembolso(
            {
                "venda_id": 1,
                "motivo": "Cliente desistiu",
                "tipo": "PARCIAL",
                "itens": [
                    {"item_venda_id": 10, "quantidade": 1},
                    {"item_venda_id": 10, "quantidade": 2},
                ],
            }
        )

        assert sucesso is False
        assert resultado is None
        assert "excede o saldo disponível" in mensagem

    @patch("modules.financeiro.services.reembolso_service.FinanceiroService.obter_venda_detalhada")
    def test_registrar_reembolso_bloqueia_item_com_produto_invalido(self, mock_obter_venda):
        SessionManager.login({"id": 7, "nome": "Operador", "permissoes": []}, persist=False)
        mock_obter_venda.return_value = {
            "itens": [
                {
                    "item_venda_id": 10,
                    "produto_id": 0,
                    "lote_id": 0,
                    "quantidade_disponivel": 2,
                    "preco_unitario": "7.50",
                }
            ]
        }

        sucesso, mensagem, resultado = ReembolsoService.registrar_reembolso(
            {
                "venda_id": 1,
                "motivo": "Cliente desistiu",
                "tipo": "PARCIAL",
                "itens": [{"item_venda_id": 10, "quantidade": 1}],
            }
        )

        assert sucesso is False
        assert resultado is None
        assert "produto válido" in mensagem

    @patch("modules.financeiro.services.reembolso_service.ReembolsoModel.registrar_reembolso")
    @patch("modules.financeiro.services.reembolso_service.FinanceiroService.obter_venda_detalhada")
    def test_registrar_reembolso_monta_payload_valido(self, mock_obter_venda, mock_registrar):
        SessionManager.login({"id": 7, "nome": "Operador", "permissoes": []}, persist=False)
        mock_registrar.return_value = 501
        mock_obter_venda.return_value = {
            "itens": [
                {
                    "item_venda_id": 10,
                    "produto_id": 1,
                    "lote_id": 0,
                    "quantidade_disponivel": 3,
                    "preco_unitario": "7.50",
                }
            ],
            "pagamentos": [{"forma_pagamento": "Dinheiro", "valor_pago": Decimal("15.00")}],
        }

        sucesso, mensagem, resultado = ReembolsoService.registrar_reembolso(
            {
                "venda_id": 22,
                "motivo": "Item avariado",
                "observacao": "Produto retornado ao balcão",
                "tipo": "PARCIAL",
                "itens": [{"item_venda_id": 10, "quantidade": 2}],
            }
        )

        assert sucesso is True
        assert "sucesso" in mensagem.lower()
        assert resultado is not None
        assert resultado["reembolso_id"] == 501
        assert resultado["venda_id"] == 22
        assert resultado["valor_total"] == Decimal("15.00")

        _, kwargs = mock_registrar.call_args
        assert kwargs["venda_id"] == 22
        assert kwargs["usuario_id"] == 7
        assert kwargs["tipo"] == "PARCIAL"
        assert kwargs["itens"][0]["item_venda_id"] == 10
        assert kwargs["itens"][0]["quantidade"] == 2
        assert kwargs["itens"][0]["valor_total"] == Decimal("15.00")
        assert kwargs["pagamentos"][0]["valor"] == Decimal("15.00")
