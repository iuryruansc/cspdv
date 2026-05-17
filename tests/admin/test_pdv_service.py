from unittest.mock import patch

from modules.pdvs.services.pdv_service import PdvService


class TestPdvService:
    @patch("modules.pdvs.services.pdv_service.PdvModel.buscar_por_identificacao", return_value=None)
    @patch("modules.pdvs.services.pdv_service.PdvModel.inserir", return_value=7)
    def test_cadastra_pdv_valido(self, _mock_inserir, _mock_existente):
        sucesso, mensagem = PdvService.cadastrar_pdv(
            {"identificacao": "pdv-02", "descricao": "Caixa Loja 2", "ativo": "S"}
        )

        assert sucesso is True
        assert "sucesso" in mensagem.lower()

    def test_valida_identificacao_obrigatoria(self):
        sucesso, mensagem = PdvService.cadastrar_pdv(
            {"identificacao": "", "descricao": "Caixa Loja 2", "ativo": "S"}
        )

        assert sucesso is False
        assert "identificação" in mensagem.lower()

    @patch(
        "modules.pdvs.services.pdv_service.PdvModel.buscar_por_identificacao",
        return_value={"id": 3, "identificacao": "PDV-01"},
    )
    def test_bloqueia_identificacao_duplicada(self, _mock_existente):
        sucesso, mensagem = PdvService.cadastrar_pdv(
            {"identificacao": "PDV-01", "descricao": "Caixa Principal", "ativo": "S"}
        )

        assert sucesso is False
        assert "já existe" in mensagem.lower()

    @patch(
        "modules.pdvs.services.pdv_service.PdvModel.buscar_por_id",
        return_value={"id": 1, "identificacao": "PDV-01", "ativo": "S"},
    )
    @patch(
        "modules.pdvs.services.pdv_service.CaixaModel.buscar_caixa_aberto_por_pdv",
        return_value={"id": 99},
    )
    def test_bloqueia_desativacao_com_caixa_aberto(self, _mock_caixa, _mock_pdv):
        sucesso, mensagem = PdvService.alternar_status(1)

        assert sucesso is False
        assert "caixa aberto" in mensagem.lower()

    @patch(
        "modules.pdvs.services.pdv_service.PdvModel.buscar_por_id",
        return_value={"id": 1, "identificacao": "PDV-01", "ativo": "S"},
    )
    @patch("modules.pdvs.services.pdv_service.CaixaModel.buscar_caixa_aberto_por_pdv", return_value=None)
    @patch(
        "modules.pdvs.services.pdv_service.ConfiguracoesModel.carregar_empresa_pdv",
        return_value={"pdv_padrao_id": 1},
    )
    def test_bloqueia_desativacao_do_pdv_padrao(self, _mock_empresa, _mock_caixa, _mock_pdv):
        sucesso, mensagem = PdvService.alternar_status(1)

        assert sucesso is False
        assert "pdv padrão" in mensagem.lower()
