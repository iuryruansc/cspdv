from unittest.mock import patch

from modules.produtos.services.produto_service import ProdutoService

def _dados_base(**overrides):
    dados = {
        "cod_produto": "FAB-001",
        "codigo_barras": "7891000100010",
        "nome": "Chocolate ao leite 90g",
        "preco_venda": 7.49,
        "categoria_id": 1,
        "marca_id": 2,
        "fornecedor_id": 3,
        "ativo": "S",
    }
    dados.update(overrides)
    return dados

class TestProdutoService:
    @patch("modules.produtos.services.produto_service.ProdutoModel.buscar_por_codigo_barras", return_value=None)
    @patch("modules.produtos.services.produto_service.ProdutoModel.buscar_por_codigo", return_value=None)
    def test_valida_codigo_do_fabricante_como_obrigatorio(self, _mock_codigo, _mock_barras):
        sucesso, mensagem = ProdutoService._validar_dados_produto(_dados_base(cod_produto=""))

        assert sucesso is False
        assert "código do produto" in mensagem.lower()

    @patch("modules.produtos.services.produto_service.ProdutoModel.buscar_por_codigo_barras", return_value=None)
    @patch("modules.produtos.services.produto_service.ProdutoModel.buscar_por_codigo", return_value={"id": 9})
    def test_bloqueia_codigo_do_fabricante_duplicado(self, _mock_codigo, _mock_barras):
        sucesso, mensagem = ProdutoService._validar_dados_produto(_dados_base(), produto_id=1)

        assert sucesso is False
        assert "código do produto" in mensagem.lower()

    @patch("modules.produtos.services.produto_service.ProdutoModel.buscar_por_codigo_barras", return_value={"id": 9})
    @patch("modules.produtos.services.produto_service.ProdutoModel.buscar_por_codigo", return_value=None)
    def test_bloqueia_codigo_de_barras_duplicado(self, _mock_codigo, _mock_barras):
        sucesso, mensagem = ProdutoService._validar_dados_produto(_dados_base(), produto_id=1)

        assert sucesso is False
        assert "código de barras" in mensagem.lower()

    @patch("modules.produtos.services.produto_service.ProdutoModel.buscar_por_codigo_barras", return_value=None)
    @patch("modules.produtos.services.produto_service.ProdutoModel.buscar_por_codigo", return_value=None)
    def test_aceita_dados_validos_com_codigo_do_fabricante(self, _mock_codigo, _mock_barras):
        sucesso, mensagem = ProdutoService._validar_dados_produto(_dados_base())

        assert sucesso is True
        assert mensagem == ""
