"""
    python -m pytest tests/test_venda.py -v
"""

from modules.venda.services.cupom_service import (
    aplicar_desconto_item,
    criar_item_cupom,
    definir_quantidade_item,
    desconto_itens_total,
    item_tem_promocao,
    priorizar_desconto_manual_item,
    quantidade_total_itens,
    recalcular_item_cupom,
    remover_desconto_item,
    restaurar_preco_promocional_item,
    somar_quantidade_item,
    subtotal_itens,
    total_geral,
)

def _produto_base(**overrides):
    produto = {
        "id": 10,
        "codigo_barras": "7891000100010",
        "nome": "Refrigerante Zero",
        "preco_venda": 8.5,
        "preco_venda_base": 8.5,
        "promocao_id": 0,
        "promocao_nome": "",
        "preco_promocional": 0.0,
        "imagem_path": "media/produtos/refrigerante_zero.png",
    }
    produto.update(overrides)
    return produto

def test_criar_item_cupom_sem_promocao():
    item = criar_item_cupom(_produto_base(), 3)

    assert item["id"] == 10
    assert item["codigo_barras"] == "7891000100010"
    assert item["nome"] == "Refrigerante Zero"
    assert item["quantidade"] == 3
    assert item["preco_venda"] == 8.5
    assert item["preco_tabela"] == 8.5
    assert item["preco_promocional"] == 0.0
    assert item["promocao_id"] == 0
    assert item["desconto_item"] == 0.0
    assert item["total"] == 25.5

def test_criar_item_cupom_com_promocao_ativa():
    item = criar_item_cupom(
        _produto_base(
            preco_venda=6.9,
            preco_venda_base=8.5,
            promocao_id=22,
            promocao_nome="Semana Zero",
            preco_promocional=6.9,
        ),
        2,
    )

    assert item["preco_venda"] == 6.9
    assert item["preco_tabela"] == 8.5
    assert item["preco_promocional"] == 6.9
    assert item["promocao_id"] == 22
    assert item["promocao_nome"] == "Semana Zero"
    assert item["total"] == 13.8

def test_recalcular_item_cupom_limita_desconto_ao_subtotal():
    item = criar_item_cupom(_produto_base(), 2)
    item["desconto_item"] = 50.0

    recalcular_item_cupom(item)

    assert item["total"] == 0.0

def test_somar_quantidade_item_recalcula_total():
    item = criar_item_cupom(_produto_base(), 1)

    somar_quantidade_item(item, 2)

    assert item["quantidade"] == 3
    assert item["total"] == 25.5

def test_definir_quantidade_item_recalcula_total():
    item = criar_item_cupom(_produto_base(), 4)

    definir_quantidade_item(item, 2)

    assert item["quantidade"] == 2
    assert item["total"] == 17.0

def test_aplicar_desconto_item_recalcula_total():
    item = criar_item_cupom(_produto_base(), 2)

    aplicar_desconto_item(item, 3.5)

    assert item["desconto_item"] == 3.5
    assert item["total"] == 13.5

def test_remover_desconto_item_restabelece_total():
    item = criar_item_cupom(_produto_base(), 2)
    aplicar_desconto_item(item, 4.0)

    remover_desconto_item(item)

    assert item["desconto_item"] == 0.0
    assert item["total"] == 17.0

def test_item_tem_promocao_identifica_promocao_valida():
    item = criar_item_cupom(
        _produto_base(preco_venda=6.0, preco_promocional=6.0, promocao_id=7),
        1,
    )

    assert item_tem_promocao(item) is True

def test_item_tem_promocao_rejeita_item_sem_preco_promocional():
    item = criar_item_cupom(
        _produto_base(preco_venda=8.5, preco_promocional=0.0, promocao_id=7),
        1,
    )

    assert item_tem_promocao(item) is False

def test_restaurar_preco_promocional_item_volta_para_preco_promocional():
    item = criar_item_cupom(
        _produto_base(preco_venda=6.9, preco_venda_base=8.5, preco_promocional=6.9, promocao_id=5),
        2,
    )
    item["preco_venda"] = 8.5
    item["desconto_item"] = 2.0

    restaurar_preco_promocional_item(item)

    assert item["preco_venda"] == 6.9
    assert item["total"] == 11.8

def test_restaurar_preco_promocional_item_sem_promocao_usa_preco_tabela():
    item = criar_item_cupom(_produto_base(preco_venda=7.5, preco_venda_base=8.5), 2)

    restaurar_preco_promocional_item(item)

    assert item["preco_venda"] == 8.5
    assert item["total"] == 17.0

def test_priorizar_desconto_manual_item_volta_para_preco_tabela():
    item = criar_item_cupom(
        _produto_base(preco_venda=6.9, preco_venda_base=8.5, preco_promocional=6.9, promocao_id=5),
        2,
    )
    aplicar_desconto_item(item, 1.5)

    priorizar_desconto_manual_item(item)

    assert item["preco_venda"] == 8.5
    assert item["total"] == 15.5

def test_agregadores_do_cupom_somam_corretamente():
    item_1 = criar_item_cupom(_produto_base(id=1, nome="Cola Zero"), 2)
    item_2 = criar_item_cupom(_produto_base(id=2, nome="Agua", preco_venda=3.0, preco_venda_base=3.0), 3)
    aplicar_desconto_item(item_1, 1.0)
    aplicar_desconto_item(item_2, 0.5)
    itens = [item_1, item_2]

    assert desconto_itens_total(itens) == 1.5
    assert subtotal_itens(itens) == 24.5
    assert quantidade_total_itens(itens) == 5
    assert total_geral(itens, 2.0) == 22.5

def test_total_geral_nunca_fica_negativo():
    item = criar_item_cupom(_produto_base(preco_venda=5.0, preco_venda_base=5.0), 1)

    assert total_geral([item], 9.0) == 0.0
