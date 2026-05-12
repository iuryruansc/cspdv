"""
    python -m pytest tests/test_caixa_service.py -v
"""

from unittest.mock import patch

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.venda.services.caixa_service import CaixaService


class TestCaixaService:
    def setup_method(self):
        CaixaSession.close()
        SessionManager.logout()

    def teardown_method(self):
        CaixaSession.close()
        SessionManager.logout()

    def test_registrar_movimentacao_sem_caixa_aberto_retorna_erro(self):
        sucesso, mensagem = CaixaService.registrar_movimentacao(
            tipo="sangria",
            valor=10.0,
            observacao="Teste",
            admin_password="123",
        )

        assert sucesso is False
        assert "caixa aberto" in mensagem.lower()

    @patch.object(CaixaService, "_carregar_parametros_caixa", return_value={"exigir_admin_sangria": True})
    @patch.object(CaixaService, "validar_admin_para_diferenca", return_value=False)
    def test_registrar_sangria_exige_admin_quando_configurado(self, _mock_admin, _mock_parametros):
        CaixaSession.open({"id": 1, "valor_abertura": 100.0})
        SessionManager.login({"id": 10, "nome": "Operador", "permissoes": []}, persist=False)

        sucesso, mensagem = CaixaService.registrar_movimentacao(
            tipo="sangria",
            valor=10.0,
            observacao="Retirada",
            admin_password="invalida",
        )

        assert sucesso is False
        assert "administrador" in mensagem.lower()

    @patch.object(CaixaService, "_carregar_parametros_caixa", return_value={"exigir_admin_sangria": True})
    def test_registrar_sangria_exige_senha_quando_nao_informada(self, _mock_parametros):
        CaixaSession.open({"id": 1, "valor_abertura": 100.0})
        SessionManager.login({"id": 10, "nome": "Operador", "permissoes": []}, persist=False)

        sucesso, mensagem = CaixaService.registrar_movimentacao(
            tipo="sangria",
            valor=10.0,
            observacao="Retirada",
            admin_password="",
        )

        assert sucesso is False
        assert "senha" in mensagem.lower()

    @patch.object(CaixaService, "_carregar_parametros_caixa", return_value={"exigir_admin_sangria": False})
    @patch.object(CaixaService, "obter_resumo_movimentacoes", return_value={"saldo_atual": 15.0})
    def test_registrar_sangria_bloqueia_valor_maior_que_saldo(self, _mock_resumo, _mock_parametros):
        CaixaSession.open({"id": 1, "valor_abertura": 100.0})
        SessionManager.login({"id": 10, "nome": "Operador", "permissoes": []}, persist=False)

        sucesso, mensagem = CaixaService.registrar_movimentacao(
            tipo="sangria",
            valor=20.0,
            observacao="Retirada",
            admin_password="",
        )

        assert sucesso is False
        assert "saldo atual" in mensagem.lower()

    @patch("modules.venda.services.caixa_service.UsuarioModel.buscar_sessao_por_id")
    @patch.object(CaixaService, "_carregar_parametros_caixa", return_value={"exigir_admin_diferenca_fechamento": True})
    @patch.object(CaixaService, "obter_resumo_fechamento", return_value={"total_esperado": 100.0})
    @patch.object(CaixaService, "validar_admin_para_diferenca", return_value=False)
    def test_fechar_caixa_com_diferenca_exige_admin_quando_configurado(
        self,
        _mock_admin,
        _mock_resumo,
        _mock_parametros,
        mock_buscar_usuario,
    ):
        CaixaSession.open({"id": 1, "usuario_id": 5})
        mock_buscar_usuario.return_value = {"id": 5, "nome": "Operador"}

        sucesso, mensagem, fechamento = CaixaService.fechar_caixa(
            90.0,
            "Fechamento com diferença",
            admin_password="",
        )

        assert sucesso is False
        assert fechamento is None
        assert "senha de um administrador" in mensagem.lower()

    @patch("modules.venda.services.caixa_service.UsuarioModel.buscar_sessao_por_id")
    def test_fechar_caixa_bloqueia_valor_contado_negativo(self, mock_buscar_usuario):
        CaixaSession.open({"id": 1, "usuario_id": 5})
        mock_buscar_usuario.return_value = {"id": 5, "nome": "Operador"}

        sucesso, mensagem, fechamento = CaixaService.fechar_caixa(
            -1.0,
            "Fechamento inválido",
            admin_password="",
        )

        assert sucesso is False
        assert fechamento is None
        assert "negativo" in mensagem.lower()

    @patch("modules.venda.services.caixa_service.CaixaModel.obter_total_reembolsos", return_value=12.0)
    @patch("modules.venda.services.caixa_service.CaixaModel.obter_resumo_movimentacoes")
    @patch("modules.venda.services.caixa_service.CaixaModel.obter_resumo_operacional")
    def test_resumo_fechamento_desconta_reembolsos_do_total_esperado(
        self,
        mock_resumo_operacional,
        mock_resumo_movimentacoes,
        _mock_reembolsos,
    ):
        CaixaSession.open({"id": 1, "valor_abertura": 100.0})
        mock_resumo_operacional.return_value = {
            "faturamento_dinheiro": 50.0,
            "vendas_dia": 3,
            "faturamento_total": 80.0,
            "totais_forma_pagamento": [],
        }
        mock_resumo_movimentacoes.return_value = {
            "total_sangrias": 10.0,
            "total_entradas_manuais": 5.0,
        }

        resumo = CaixaService.obter_resumo_fechamento()

        assert resumo["total_reembolsos"] == 12.0
        assert resumo["total_esperado"] == 133.0

    @patch("modules.venda.services.caixa_service.CaixaModel.obter_total_reembolsos", return_value=7.0)
    @patch("modules.venda.services.caixa_service.CaixaModel.obter_resumo_movimentacoes")
    @patch("modules.venda.services.caixa_service.CaixaModel.obter_resumo_operacional")
    def test_resumo_movimentacoes_desconta_reembolsos_do_saldo_atual(
        self,
        mock_resumo_operacional,
        mock_resumo_movimentacoes,
        _mock_reembolsos,
    ):
        CaixaSession.open({"id": 1, "valor_abertura": 100.0})
        mock_resumo_operacional.return_value = {"faturamento_dinheiro": 50.0}
        mock_resumo_movimentacoes.return_value = {
            "total_sangrias": 10.0,
            "total_suprimentos": 3.0,
            "total_troco": 2.0,
        }

        resumo = CaixaService.obter_resumo_movimentacoes()

        assert resumo["total_reembolsos"] == 7.0
        assert resumo["saldo_atual"] == 138.0

    @patch("modules.venda.services.caixa_service.CaixaModel.fechar_caixa")
    @patch("modules.venda.services.caixa_service.UsuarioModel.buscar_sessao_por_id")
    @patch.object(CaixaService, "_carregar_parametros_caixa", return_value={"exigir_admin_diferenca_fechamento": False})
    @patch.object(CaixaService, "obter_resumo_fechamento", return_value={"total_esperado": 100.0})
    def test_fechar_caixa_com_sucesso_fecha_sessao_e_retorna_resumo(
        self,
        _mock_resumo,
        _mock_parametros,
        mock_buscar_usuario,
        mock_fechar_caixa,
    ):
        CaixaSession.open({"id": 1, "usuario_id": 5})
        mock_buscar_usuario.return_value = {"id": 5, "nome": "Operador"}

        sucesso, mensagem, fechamento = CaixaService.fechar_caixa(
            110.0,
            "Fechamento ok",
            admin_password="",
        )

        assert sucesso is True
        assert "sucesso" in mensagem.lower()
        assert fechamento is not None
        assert fechamento["caixa_id"] == 1
        assert fechamento["valor_contado"] == 110.0
        assert fechamento["total_esperado"] == 100.0
        assert fechamento["diferenca"] == 10.0
        assert CaixaSession.current() is None
        mock_fechar_caixa.assert_called_once()
