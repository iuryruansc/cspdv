import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication, QDialog

from modules.venda.views.selecionar_cliente_dialog import SelecionarClienteDialog

_app = QApplication.instance() or QApplication(sys.argv)

def _cliente_base(**overrides):
    cliente = {
        "id": 1,
        "nome": "Iury Santos",
        "cpf": "12345678900",
        "telefone": "11999999999",
    }
    cliente.update(overrides)
    return cliente

class TestSelecionarClienteDialog:
    @patch("modules.venda.views.selecionar_cliente_dialog.ClienteService.buscar_para_venda")
    def test_busca_nao_dispara_com_menos_de_dois_caracteres(self, mock_busca):
        dialog = SelecionarClienteDialog()
        dialog.lineBusca.setText("A")

        dialog._buscar_clientes()

        assert dialog.lblStatus.text() == "Digite ao menos 2 caracteres para buscar."
        assert dialog.listaClientes.count() == 0
        mock_busca.assert_not_called()

    @patch("modules.venda.views.selecionar_cliente_dialog.ClienteService.buscar_para_venda")
    def test_busca_preenche_lista_e_seleciona_primeiro_cliente(self, mock_busca):
        mock_busca.return_value = [
            _cliente_base(),
            _cliente_base(id=2, nome="Ana Souza", cpf="99887766554"),
        ]
        dialog = SelecionarClienteDialog()
        dialog.lineBusca.setText("an")

        dialog._buscar_clientes()

        assert dialog.lblStatus.text() == "2 cliente(s) encontrado(s)."
        assert dialog.listaClientes.count() == 2
        assert dialog.listaClientes.currentRow() == 0
        assert "Iury Santos" in dialog.listaClientes.item(0).text()

    @patch("modules.venda.views.selecionar_cliente_dialog.ClienteService.buscar_para_venda", return_value=[])
    def test_busca_sem_resultados_exibe_status(self, _mock_busca):
        dialog = SelecionarClienteDialog()
        dialog.lineBusca.setText("zz")

        dialog._buscar_clientes()

        assert dialog.lblStatus.text() == "Nenhum cliente encontrado."
        assert dialog.listaClientes.count() == 0

    def test_usar_consumidor_final_limpa_cliente_e_aceita_dialog(self):
        dialog = SelecionarClienteDialog()
        dialog._cliente_selecionado = _cliente_base()

        dialog._usar_consumidor_final()

        assert dialog.cliente_selecionado is None
        assert dialog.result() == QDialog.Accepted

    @patch("modules.venda.views.selecionar_cliente_dialog.ClienteService.buscar_para_venda")
    def test_selecionar_cliente_confirma_item_atual(self, mock_busca):
        mock_busca.return_value = [_cliente_base()]
        dialog = SelecionarClienteDialog()
        dialog.lineBusca.setText("iu")
        dialog._buscar_clientes()

        dialog._selecionar_cliente()

        assert dialog.cliente_selecionado is not None
        assert dialog.cliente_selecionado["nome"] == "Iury Santos"
        assert dialog.result() == QDialog.Accepted
