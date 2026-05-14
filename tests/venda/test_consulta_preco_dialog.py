import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.venda.views.consulta_preco_dialog import ConsultaPrecoDialog

_app = QApplication.instance() or QApplication(sys.argv)

def _produto_base(**overrides):
    produto = {
        "id": 15,
        "nome": "Chocolate ao Leite 90G",
        "quantidade_estoque": 26,
        "preco_venda": 7.49,
        "imagem_path": "media/produtos/chocolate_90g.png",
    }
    produto.update(overrides)
    return produto

class TestConsultaPrecoDialog:
    @patch("modules.venda.views.consulta_preco_dialog.atualizar_preview_label")
    @patch("modules.venda.views.consulta_preco_dialog.ProdutoModel.buscar_por_codigo")
    def test_busca_por_codigo_de_barras_preenche_resultado(self, mock_buscar_codigo, mock_preview):
        mock_buscar_codigo.return_value = _produto_base()
        dialog = ConsultaPrecoDialog()
        dialog.lineBusca.setText("7891000100301")

        dialog._buscar_produto()

        assert dialog.lblCodigoValor.text() == "7891000100301"
        assert dialog.lblDescricaoValor.text() == "CHOCOLATE AO LEITE 90G"
        assert dialog.lblEstoqueValor.text() == "26"
        assert dialog.lblPrecoValor.text() == "R$ 7,49"
        assert dialog._produto_encontrado is not None
        mock_preview.assert_called()

    @patch("modules.venda.views.consulta_preco_dialog.ProdutoModel.buscar_por_id")
    @patch("modules.venda.views.consulta_preco_dialog.ProdutoModel.buscar_por_codigo", return_value=None)
    def test_busca_por_codigo_interno_quando_termo_e_numerico(self, _mock_buscar_codigo, mock_buscar_id):
        mock_buscar_id.return_value = _produto_base(id=1821, nome="Bombom Recheado")
        dialog = ConsultaPrecoDialog()

        produto = dialog._buscar_produto_exato("1821")

        assert produto is not None
        assert produto["id"] == 1821
        assert produto["nome"] == "Bombom Recheado"
        mock_buscar_id.assert_called_once_with(1821)

    @patch("modules.venda.views.consulta_preco_dialog.ProdutoModel.buscar_por_id")
    @patch("modules.venda.views.consulta_preco_dialog.ProdutoModel.buscar_por_codigo", return_value=None)
    def test_nao_busca_por_id_quando_termo_nao_e_numerico(self, mock_buscar_codigo, mock_buscar_id):
        dialog = ConsultaPrecoDialog()

        produto = dialog._buscar_produto_exato("ABC-123")

        assert produto is None
        mock_buscar_codigo.assert_called_once_with("ABC-123")
        mock_buscar_id.assert_not_called()

    @patch("modules.venda.views.consulta_preco_dialog.mostrar_info")
    @patch("modules.venda.views.consulta_preco_dialog.ProdutoModel.buscar_por_codigo", return_value=None)
    def test_exibe_aviso_quando_produto_nao_e_encontrado(self, _mock_buscar_codigo, mock_info):
        dialog = ConsultaPrecoDialog()
        dialog.lineBusca.setText("9999999999999")

        dialog._buscar_produto()

        assert dialog._produto_encontrado is None
        assert dialog.lblCodigoValor.text() == "—"
        assert dialog.lblDescricaoValor.text() == "—"
        assert dialog.lblEstoqueValor.text() == "—"
        assert dialog.lblPrecoValor.text() == "R$ —"
        mock_info.assert_called_once()

    @patch("modules.venda.views.consulta_preco_dialog.atualizar_preview_label")
    def test_limpar_resultado_restabelece_estado_inicial(self, mock_preview):
        dialog = ConsultaPrecoDialog()
        dialog.lblCodigoValor.setText("1821")
        dialog.lblDescricaoValor.setText("Produto")
        dialog.lblEstoqueValor.setText("10")
        dialog.lblPrecoValor.setText("R$ 9,99")

        dialog._limpar_resultado()

        assert dialog.lblCodigoValor.text() == "—"
        assert dialog.lblDescricaoValor.text() == "—"
        assert dialog.lblEstoqueValor.text() == "—"
        assert dialog.lblPrecoValor.text() == "R$ —"
        mock_preview.assert_called()
