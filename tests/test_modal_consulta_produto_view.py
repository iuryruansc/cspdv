import sys

from unittest.mock import patch

from PyQt5.QtWidgets import QApplication, QDialog

from modules.venda.views.modal_consulta_produto_view import ModalConsultaProdutoView

_app = QApplication.instance() or QApplication(sys.argv)


def _produto_base(**overrides):
    produto = {
        "codigo_barras": "7891000100301",
        "nome": "Chocolate ao Leite 90G",
        "unidade": "UN",
        "quantidade_estoque": 26,
        "preco_venda": 7.49,
    }
    produto.update(overrides)
    return produto


class TestModalConsultaProdutoView:
    @patch("modules.venda.views.modal_consulta_produto_view.ProdutoService.buscar_para_venda")
    def test_busca_preenche_tabela_e_detalhes_do_primeiro_resultado(self, mock_busca):
        mock_busca.return_value = [
            _produto_base(),
            _produto_base(codigo_barras="7891000100302", nome="Chocolate Branco 90G"),
        ]
        dialog = ModalConsultaProdutoView()
        dialog.lineEditBusca.setText("Chocolate")

        dialog._buscar_produtos()

        assert dialog.tableResultados.rowCount() == 2
        assert dialog.produto_selecionado is not None
        assert dialog.produto_selecionado["codigo_barras"] == "7891000100301"
        assert dialog.lblInfoCodValor.text() == "7891000100301"
        assert dialog.lblInfoDescValor.text() == "Chocolate ao Leite 90G"
        assert dialog.lblInfoEstoqueValor.text() == "26"
        assert dialog.lblInfoPrecoValor.text().endswith("7,49")

    @patch("modules.venda.views.modal_consulta_produto_view.ProdutoService.buscar_para_venda", return_value=[])
    def test_busca_sem_resultados_limpa_detalhes(self, _mock_busca):
        dialog = ModalConsultaProdutoView()
        dialog.lineEditBusca.setText("Inexistente")

        dialog._buscar_produtos()

        assert dialog.tableResultados.rowCount() == 0
        assert dialog.produto_selecionado is None
        assert dialog.lblInfoCodValor.text() == "-"
        assert dialog.lblInfoDescValor.text() == "-"
        assert dialog.lblInfoEstoqueValor.text() == "-"
        assert dialog.lblInfoPrecoValor.text() == "R$ -"

    @patch("modules.venda.views.modal_consulta_produto_view.ProdutoService.buscar_para_venda")
    def test_atualizar_detalhes_reflete_linha_selecionada(self, mock_busca):
        mock_busca.return_value = [
            _produto_base(),
            _produto_base(codigo_barras="7891000100302", nome="Chocolate Branco 90G", preco_venda=8.99),
        ]
        dialog = ModalConsultaProdutoView()

        dialog._buscar_produtos()
        dialog.tableResultados.selectRow(1)
        dialog._atualizar_detalhes_selecao()

        assert dialog.produto_selecionado is not None
        assert dialog.produto_selecionado["codigo_barras"] == "7891000100302"
        assert dialog.lblInfoDescValor.text() == "Chocolate Branco 90G"
        assert dialog.lblInfoPrecoValor.text().endswith("8,99")

    def test_confirmar_selecao_sem_produto_nao_aceita_dialog(self):
        dialog = ModalConsultaProdutoView()

        dialog._confirmar_selecao()

        assert dialog.result() != QDialog.Accepted

    @patch("modules.venda.views.modal_consulta_produto_view.ProdutoService.buscar_para_venda", return_value=[_produto_base()])
    def test_confirmar_selecao_com_produto_aceita_dialog(self, _mock_busca):
        dialog = ModalConsultaProdutoView()

        dialog._buscar_produtos()
        dialog._confirmar_selecao()

        assert dialog.result() == QDialog.Accepted
