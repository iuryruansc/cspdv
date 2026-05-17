from unittest.mock import patch

from modules.unidades.services.unidade_service import UnidadeService


class TestUnidadeService:
    @patch("modules.unidades.services.unidade_service.UnidadeModel.buscar_por_sigla", return_value=None)
    @patch("modules.unidades.services.unidade_service.UnidadeModel.inserir", return_value=5)
    def test_cadastra_unidade_valida(self, _mock_inserir, _mock_existente):
        sucesso, mensagem = UnidadeService.cadastrar_unidade(
            {"sigla": "UN", "descricao": "Unidade", "codigo_sefaz": "01", "fracionavel": False, "ativo": "S"}
        )

        assert sucesso is True
        assert "sucesso" in mensagem.lower()

    def test_valida_sigla_obrigatoria(self):
        sucesso, mensagem = UnidadeService.cadastrar_unidade(
            {"sigla": "", "descricao": "Unidade", "fracionavel": False, "ativo": "S"}
        )

        assert sucesso is False
        assert "sigla" in mensagem.lower()

    @patch(
        "modules.unidades.services.unidade_service.UnidadeModel.buscar_por_sigla",
        return_value={"id": 3, "sigla": "UN"},
    )
    def test_bloqueia_sigla_duplicada(self, _mock_existente):
        sucesso, mensagem = UnidadeService.cadastrar_unidade(
            {"sigla": "UN", "descricao": "Unidade", "fracionavel": False, "ativo": "S"}
        )

        assert sucesso is False
        assert "já existe" in mensagem.lower()

    @patch(
        "modules.unidades.services.unidade_service.UnidadeModel.buscar_por_id",
        return_value={"id": 1, "sigla": "UN", "ativo": "S"},
    )
    @patch("modules.unidades.services.unidade_service.UnidadeModel.contar_produtos_vinculados", return_value=2)
    def test_bloqueia_desativacao_com_produtos_vinculados(self, _mock_contagem, _mock_unidade):
        sucesso, mensagem = UnidadeService.alternar_status(1)

        assert sucesso is False
        assert "vinculada a produtos" in mensagem.lower()
