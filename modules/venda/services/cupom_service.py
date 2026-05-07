from __future__ import annotations

from typing import Any, Dict, List


ItemCupom = Dict[str, Any]


def criar_item_cupom(produto: Dict[str, Any], quantidade: int) -> ItemCupom:
    preco = float(produto.get("preco_venda") or 0.0)
    preco_tabela = float(produto.get("preco_venda_base") or preco)
    preco_promocional = (
        float(produto.get("preco_promocional") or 0.0)
        if produto.get("promocao_id")
        else 0.0
    )
    return {
        "id": int(produto.get("id") or 0),
        "codigo_barras": str(produto.get("codigo_barras") or ""),
        "nome": str(produto.get("nome") or ""),
        "quantidade": int(quantidade),
        "preco_venda": preco,
        "preco_tabela": preco_tabela,
        "preco_promocional": preco_promocional,
        "promocao_id": int(produto.get("promocao_id") or 0),
        "promocao_nome": str(produto.get("promocao_nome") or ""),
        "imagem_path": produto.get("imagem_path"),
        "desconto_item": 0.0,
        "total": preco * quantidade,
    }


def recalcular_item_cupom(item: ItemCupom) -> None:
    subtotal_bruto = float(item["preco_venda"]) * float(item["quantidade"])
    desconto_item = min(float(item.get("desconto_item") or 0.0), subtotal_bruto)
    item["total"] = max(0.0, subtotal_bruto - desconto_item)


def somar_quantidade_item(item: ItemCupom, quantidade: int) -> None:
    item["quantidade"] = int(item.get("quantidade") or 0) + int(quantidade)
    recalcular_item_cupom(item)


def definir_quantidade_item(item: ItemCupom, quantidade: int) -> None:
    item["quantidade"] = int(quantidade)
    recalcular_item_cupom(item)


def aplicar_desconto_item(item: ItemCupom, desconto: float) -> None:
    item["desconto_item"] = float(desconto)
    recalcular_item_cupom(item)


def remover_desconto_item(item: ItemCupom) -> None:
    item["desconto_item"] = 0.0
    recalcular_item_cupom(item)


def item_tem_promocao(item: ItemCupom) -> bool:
    return int(item.get("promocao_id") or 0) > 0 and float(item.get("preco_promocional") or 0.0) > 0


def restaurar_preco_promocional_item(item: ItemCupom) -> None:
    if item_tem_promocao(item):
        item["preco_venda"] = float(item.get("preco_promocional") or item.get("preco_tabela") or 0.0)
    else:
        item["preco_venda"] = float(item.get("preco_tabela") or item.get("preco_venda") or 0.0)
    recalcular_item_cupom(item)


def priorizar_desconto_manual_item(item: ItemCupom) -> None:
    item["preco_venda"] = float(item.get("preco_tabela") or item.get("preco_venda") or 0.0)
    recalcular_item_cupom(item)


def desconto_itens_total(itens: List[ItemCupom]) -> float:
    return sum(float(item.get("desconto_item") or 0.0) for item in itens)


def subtotal_itens(itens: List[ItemCupom]) -> float:
    return sum(float(item.get("total") or 0.0) for item in itens)


def quantidade_total_itens(itens: List[ItemCupom]) -> int:
    return sum(int(item.get("quantidade") or 0) for item in itens)


def total_geral(itens: List[ItemCupom], desconto_global: float) -> float:
    return max(0.0, subtotal_itens(itens) - float(desconto_global))
