import sys
from pathlib import Path
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.produtos.views.cadastro_produto_view import CadastroProdutoView

_app = QApplication.instance() or QApplication(sys.argv)


def _itens_combo():
    return [{"id": 1, "nome": "Opcao Teste"}]


def _produto(**overrides):
    produto = {
        "id": 10,
        "cod_produto": "FAB-123",
        "codigo_barras": "7891000100301",
        "nome": "CHOCOLATE 90G",
        "ncm": "18063110",
        "cest": "1703900",
        "preco_compra": 4.2,
        "preco_venda": 7.49,
        "quantidade_estoque": 26,
        "categoria_id": 1,
        "marca_id": 1,
        "fornecedor_id": 1,
        "unidade_id": 1,
        "unidade_tributavel_id": 1,
        "ativo": "S",
        "imagem_path": None,
    }
    produto.update(overrides)
    return produto


def _patch_combos():
    return patch.multiple(
        "modules.produtos.views.cadastro_produto_view",
        **{
            "CategoriaModel.listar_ativas": lambda: _itens_combo(),
            "MarcaModel.listar_ativas": lambda: _itens_combo(),
            "FornecedorModel.listar_ativos": lambda: _itens_combo(),
            "UnidadeModel.listar_ativas": lambda: _itens_combo(),
        },
    )


class TestCadastroProdutoView:
    @patch("modules.produtos.views.cadastro_produto_view.atualizar_preview_label")
    @patch("modules.produtos.views.cadastro_produto_view.UnidadeModel.listar_ativas", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.FornecedorModel.listar_ativos", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.MarcaModel.listar_ativas", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.CategoriaModel.listar_ativas", return_value=_itens_combo())
    def test_modo_cadastro_deixa_codigo_livre_e_vazio(
        self,
        _mock_categoria,
        _mock_marca,
        _mock_fornecedor,
        _mock_unidade,
        _mock_preview,
    ):
        view = CadastroProdutoView()

        assert view.lineEditCodigo.text() == ""
        assert view.lineEditCodigo.isReadOnly() is False

    @patch("modules.produtos.views.cadastro_produto_view.atualizar_preview_label")
    @patch("modules.produtos.views.cadastro_produto_view.ProdutoModel.buscar_por_id", return_value=_produto())
    @patch("modules.produtos.views.cadastro_produto_view.UnidadeModel.listar_ativas", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.FornecedorModel.listar_ativos", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.MarcaModel.listar_ativas", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.CategoriaModel.listar_ativas", return_value=_itens_combo())
    def test_modo_edicao_carrega_codigo_do_fabricante(
        self,
        _mock_categoria,
        _mock_marca,
        _mock_fornecedor,
        _mock_unidade,
        _mock_buscar,
        _mock_preview,
    ):
        view = CadastroProdutoView(produto_id=10)

        assert view.lineEditCodigo.text() == "FAB-123"
        assert view.lineEditCodigoBarras.text() == "7891000100301"
        assert view.lineEditDescricao.text() == "CHOCOLATE 90G"

    @patch("modules.produtos.views.cadastro_produto_view.mostrar_info")
    @patch("modules.produtos.views.cadastro_produto_view.atualizar_preview_label")
    @patch("modules.produtos.views.cadastro_produto_view.ProdutoService.cadastrar_produto", return_value=(True, "Produto cadastrado"))
    @patch(
        "modules.produtos.views.cadastro_produto_view.ConfiguracoesService.carregar_parametros_fiscais",
        return_value={
            "exigir_ncm_cest_produto": False,
            "exigir_unidade_tributavel_produto": False,
        },
    )
    @patch("modules.produtos.views.cadastro_produto_view.UnidadeModel.listar_ativas", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.FornecedorModel.listar_ativos", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.MarcaModel.listar_ativas", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.CategoriaModel.listar_ativas", return_value=_itens_combo())
    def test_salvar_envia_cod_produto_no_payload(
        self,
        _mock_categoria,
        _mock_marca,
        _mock_fornecedor,
        _mock_unidade,
        _mock_parametros_fiscais,
        mock_cadastrar,
        _mock_preview,
        mock_info,
    ):
        view = CadastroProdutoView()
        view.lineEditCodigo.setText("fab-123")
        view.lineEditCodigoBarras.setText("7891000100301")
        view.lineEditDescricao.setText("Chocolate")
        view.lineEditPrecoCusto.setText("4.20")
        view.lineEditPrecoVenda.setText("7.49")
        view.lineEditQuantidadeEstoque.setText("10")
        view.comboCategoria.setCurrentIndex(1)
        view.comboMarca.setCurrentIndex(1)
        view.comboBox.setCurrentIndex(1)
        view.comboUnidade.setCurrentIndex(1)
        view.comboUnidadeTributavel.setCurrentIndex(1)

        view._salvar_produto()

        payload = mock_cadastrar.call_args.args[0]
        assert payload["cod_produto"] == "FAB-123"
        assert payload["codigo_barras"] == "7891000100301"
        mock_info.assert_called_once()

    @patch("modules.produtos.views.cadastro_produto_view.mostrar_info")
    @patch("modules.produtos.views.cadastro_produto_view.atualizar_preview_label")
    @patch("modules.produtos.views.cadastro_produto_view.ProdutoService.cadastrar_produto", return_value=(True, "Produto cadastrado"))
    @patch(
        "modules.produtos.views.cadastro_produto_view.ConfiguracoesService.carregar_parametros_fiscais",
        return_value={
            "exigir_ncm_cest_produto": False,
            "exigir_unidade_tributavel_produto": False,
        },
    )
    @patch("modules.produtos.views.cadastro_produto_view.UnidadeModel.listar_ativas", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.FornecedorModel.listar_ativos", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.MarcaModel.listar_ativas", return_value=_itens_combo())
    @patch("modules.produtos.views.cadastro_produto_view.CategoriaModel.listar_ativas", return_value=_itens_combo())
    def test_salvar_aceita_campos_fiscais_vazios_quando_parametro_desabilita_exigencia(
        self,
        _mock_categoria,
        _mock_marca,
        _mock_fornecedor,
        _mock_unidade,
        _mock_parametros_fiscais,
        mock_cadastrar,
        _mock_preview,
        mock_info,
    ):
        view = CadastroProdutoView()
        view.lineEditCodigo.setText("fab-999")
        view.lineEditCodigoBarras.setText("7891000100301")
        view.lineEditDescricao.setText("Chocolate")
        view.lineEditPrecoCusto.setText("4.20")
        view.lineEditPrecoVenda.setText("7.49")
        view.lineEditQuantidadeEstoque.setText("10")
        view.comboCategoria.setCurrentIndex(1)
        view.comboMarca.setCurrentIndex(1)
        view.comboBox.setCurrentIndex(1)
        view.comboUnidade.setCurrentIndex(1)
        view.comboUnidadeTributavel.setCurrentIndex(0)
        view.lineEditNcm.clear()
        view.lineEditCest.clear()

        view._salvar_produto()

        payload = mock_cadastrar.call_args.args[0]
        assert payload["ncm"] == ""
        assert payload["cest"] == ""
        assert payload["unidade_tributavel_id"] is None
        mock_info.assert_called_once()
