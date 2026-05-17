import sys
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.venda.services.cupom_service import criar_item_cupom
from modules.venda.views.frente_venda_view import FrenteVendaView

_app = QApplication.instance() or QApplication(sys.argv)

def _produto_base(**overrides):
    produto = {
        "id": 1,
        "cod_produto": "FAB-001",
        "codigo_barras": "789100000001",
        "nome": "Bombom Recheado",
        "preco_venda": 5.0,
        "preco_venda_base": 6.5,
        "preco_promocional": 5.0,
        "promocao_id": 10,
        "promocao_nome": "Promo Bombom",
        "quantidade_estoque": 20,
        "imagem_path": None,
    }
    produto.update(overrides)
    return produto

def _params_venda(**overrides):
    params = {
        "cliente_padrao_venda": "CONSUMIDOR_FINAL",
        "regra_desconto_venda": "EXIGIR_AUTORIZACAO",
        "permitir_venda_sem_estoque": True,
    }
    params.update(overrides)
    return params

def _params_promocoes(**overrides):
    params = {
        "prioridade_promocional": "PROMOCAO_ANTES_DESCONTO",
    }
    params.update(overrides)
    return params

def _criar_view(*, params_venda=None, params_promocoes=None):
    with (
        patch(
            "modules.venda.views.frente_venda_view.ConfiguracoesService.carregar_parametros_venda",
            return_value=params_venda or _params_venda(),
        ),
        patch(
            "modules.venda.views.frente_venda_view.ConfiguracoesService.carregar_parametros_promocoes",
            return_value=params_promocoes or _params_promocoes(),
        ),
        patch(
            "modules.venda.views.frente_venda_view.ClienteService.obter_consumidor_final",
            return_value={"id": 1, "nome": "Consumidor Final"},
        ),
        patch("modules.venda.views.frente_venda_view.atualizar_preview_label", return_value=None),
    ):
        view = FrenteVendaView()
    view.show()
    return view

class TestFrenteVendaView:
    def test_extrai_quantidade_embutida_com_asterisco(self):
        view = _criar_view()

        quantidade, descricao = view._extrair_quantidade_descricao("3*Bombom Recheado")

        assert quantidade == 3
        assert descricao == "Bombom Recheado"

    def test_extrai_quantidade_embutida_com_espacos(self):
        view = _criar_view()

        quantidade, descricao = view._extrair_quantidade_descricao("  12 *  Coca Cola Zero  ")

        assert quantidade == 12
        assert descricao == "Coca Cola Zero"

    def test_mantem_descricao_quando_nao_ha_quantidade_embutida(self):
        view = _criar_view()

        quantidade, descricao = view._extrair_quantidade_descricao("Bombom Recheado")

        assert quantidade is None
        assert descricao == "Bombom Recheado"

    @patch("modules.venda.views.frente_venda_view.ProdutoService.buscar_para_venda")
    def test_executar_busca_preenche_quantidade_embutida_e_sugestoes(self, mock_busca):
        mock_busca.return_value = [
            _produto_base(),
            _produto_base(id=2, nome="Bombom Branco", codigo_barras="789100000002"),
        ]
        view = _criar_view()
        view.lineEditDescricaoProduto.setText("3*Bombom")

        view._executar_busca_produto()

        assert view.lineEditQuantidade.text() == "3"
        assert view._produto_atual is not None
        assert int(view._produto_atual["id"]) == 1
        assert view.listaSugestoesProdutos.count() == 2
        assert "Bombom Recheado" in view.listaSugestoesProdutos.item(0).text()
        assert "FAB-001" in view.listaSugestoesProdutos.item(0).text()

    def test_calcula_desconto_percentual_e_fixo(self):
        assert FrenteVendaView._calcular_desconto(100.0, "percentual", 12.5) == 12.5
        assert FrenteVendaView._calcular_desconto(100.0, "valor", 18.0) == 18.0

    def test_reconciliar_precos_promocionais_nao_muda_quando_promocao_tem_prioridade(self):
        view = _criar_view(params_promocoes=_params_promocoes(prioridade_promocional="PROMOCAO_ANTES_DESCONTO"))
        item = criar_item_cupom(_produto_base(), 2)
        item["preco_venda"] = 6.5
        view._itens_venda = [item]

        view._reconciliar_precos_promocionais()

        assert view._itens_venda[0]["preco_venda"] == 6.5

    def test_reconciliar_precos_promocionais_restaura_preco_promocional_sem_desconto(self):
        view = _criar_view(params_promocoes=_params_promocoes(prioridade_promocional="DESCONTO_ANTES_PROMOCAO"))
        item = criar_item_cupom(_produto_base(), 2)
        item["preco_venda"] = 6.5
        view._itens_venda = [item]

        view._reconciliar_precos_promocionais()

        assert view._itens_venda[0]["preco_venda"] == 5.0

    def test_reconciliar_precos_promocionais_prioriza_preco_tabela_com_desconto_global(self):
        view = _criar_view(params_promocoes=_params_promocoes(prioridade_promocional="DESCONTO_ANTES_PROMOCAO"))
        item = criar_item_cupom(_produto_base(), 2)
        item["preco_venda"] = 5.0
        view._itens_venda = [item]
        view._desconto_global_valor = 2.0

        view._reconciliar_precos_promocionais()

        assert view._itens_venda[0]["preco_venda"] == 6.5

    def test_reconciliar_precos_promocionais_prioriza_preco_tabela_com_desconto_item(self):
        view = _criar_view(params_promocoes=_params_promocoes(prioridade_promocional="DESCONTO_ANTES_PROMOCAO"))
        item = criar_item_cupom(_produto_base(), 2)
        item["preco_venda"] = 5.0
        item["desconto_item"] = 1.0
        view._itens_venda = [item]

        view._reconciliar_precos_promocionais()

        assert view._itens_venda[0]["preco_venda"] == 6.5

    @patch("modules.venda.views.frente_venda_view.ProdutoService.buscar_para_venda")
    def test_adiciona_mesmo_produto_em_linhas_separadas(self, mock_busca):
        mock_busca.return_value = [_produto_base()]
        view = _criar_view()

        view.lineEditDescricaoProduto.setText("Bombom Recheado")
        view._adicionar_produto_pelo_enter()
        view.lineEditDescricaoProduto.setText("Bombom Recheado")
        view._adicionar_produto_pelo_enter()

        assert len(view._itens_venda) == 2
        assert view._itens_venda[0]["id"] == 1
        assert view._itens_venda[1]["id"] == 1
        assert view._itens_venda[0]["quantidade"] == 1
        assert view._itens_venda[1]["quantidade"] == 1

    @patch("modules.venda.views.frente_venda_view.mostrar_aviso")
    @patch("modules.venda.views.frente_venda_view.ProdutoService.buscar_para_venda")
    def test_bloqueia_linha_nova_quando_total_do_mesmo_produto_excede_estoque(self, mock_busca, mock_aviso):
        mock_busca.return_value = [_produto_base(quantidade_estoque=3)]
        view = _criar_view(params_venda=_params_venda(permitir_venda_sem_estoque=False))

        view.lineEditDescricaoProduto.setText("2*Bombom Recheado")
        view._adicionar_produto_pelo_enter()
        view.lineEditDescricaoProduto.setText("2*Bombom Recheado")
        view._adicionar_produto_pelo_enter()

        assert len(view._itens_venda) == 1
        assert view._itens_venda[0]["quantidade"] == 2
        mock_aviso.assert_called_once()

    def test_venda_padrao_emite_cliente_seeded_com_flag_de_consumidor_final(self):
        view = _criar_view()
        view._itens_venda = [criar_item_cupom(_produto_base(), 1)]
        emitidos = []
        view.pagamento_solicitado.connect(lambda payload: emitidos.append(payload))

        with patch("modules.venda.views.frente_venda_view.ConfirmarVendaDialog") as mock_dialog_cls:
            dialog = mock_dialog_cls.return_value
            dialog.Accepted = 1
            dialog.exec_.return_value = 1
            view._abrir_confirmacao_venda()

        assert len(emitidos) == 1
        assert emitidos[0]["cliente_id"] == 1
        assert emitidos[0]["cliente_eh_consumidor_final"] is True
