from __future__ import annotations

import json
from typing import Any, Dict, List

ItemCupom = Dict[str, Any]
PromocaoData = Dict[str, Any]

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


def calcular_desconto_leve_x_pague_y(
    itens: List[ItemCupom],
    promocao: PromocaoData,
    produto_ids: set[int],
) -> float:
    leve_x = int(promocao.get("leve_x") or 0)
    pague_y = int(promocao.get("pague_y") or 0)
    aplicacao = str(promocao.get("aplicacao_desconto_xpy") or "MAIS_BARATO").upper()
    if leve_x <= 0 or pague_y <= 0 or pague_y >= leve_x:
        return 0.0

    itens_elegiveis = [
        item for item in itens
        if int(item.get("id") or 0) in produto_ids and int(item.get("quantidade") or 0) > 0
    ]
    if not itens_elegiveis:
        return 0.0

    total_unidades = sum(int(item["quantidade"]) for item in itens_elegiveis)
    conjuntos = total_unidades // leve_x
    if conjuntos <= 0:
        return 0.0

    desconto = 0.0
    if aplicacao == "MAIS_BARATO":
        precos_ordenados = []
        for item in itens_elegiveis:
            preco_unit = float(item.get("preco_promocional") or item.get("preco_venda") or 0.0)
            for _ in range(int(item["quantidade"])):
                precos_ordenados.append(preco_unit)
        precos_ordenados.sort()
        unidades_desconto = conjuntos * (leve_x - pague_y)
        for i in range(min(unidades_desconto, len(precos_ordenados))):
            desconto += precos_ordenados[i]
    else:
        for item in itens_elegiveis:
            subtotal = float(item["preco_venda"]) * int(item["quantidade"])
            desconto += subtotal * (1 - pague_y / leve_x) * conjuntos / max(1, total_unidades // leve_x)

    return desconto


def calcular_desconto_progressivo(
    itens: List[ItemCupom],
    promocao: PromocaoData,
    produto_ids: set[int],
) -> float:
    regras_raw = promocao.get("regras_progressivas")
    if not regras_raw:
        return 0.0
    try:
        regras = json.loads(str(regras_raw)) if isinstance(regras_raw, str) else regras_raw
    except (json.JSONDecodeError, TypeError):
        return 0.0
    if not isinstance(regras, list) or not regras:
        return 0.0

    regras_ordenadas = sorted(regras, key=lambda r: int(r.get("qtd_min", 0)), reverse=True)

    total_unidades = 0
    for item in itens:
        if int(item.get("id") or 0) in produto_ids:
            total_unidades += int(item.get("quantidade") or 0)

    melhor_percentual = 0.0
    for regra in regras_ordenadas:
        qtd_min = int(regra.get("qtd_min", 0))
        if total_unidades >= qtd_min:
            melhor_percentual = float(regra.get("desconto", 0))
            break

    if melhor_percentual <= 0:
        return 0.0

    desconto = 0.0
    for item in itens:
        if int(item.get("id") or 0) in produto_ids:
            subtotal = float(item["preco_venda"]) * int(item["quantidade"])
            desconto += subtotal * melhor_percentual / 100.0
    return desconto


def calcular_desconto_combo(
    itens: List[ItemCupom],
    promocao: PromocaoData,
    produto_ids: set[int],
) -> float:
    combo_qtd = int(promocao.get("combo_qtd") or 0)
    combo_preco = float(promocao.get("combo_preco") or 0.0)
    if combo_qtd <= 0 or combo_preco <= 0:
        return 0.0

    total_unidades = 0
    subtotal_normal = 0.0
    for item in itens:
        if int(item.get("id") or 0) in produto_ids:
            qtd = int(item.get("quantidade") or 0)
            total_unidades += qtd
            subtotal_normal += float(item["preco_venda"]) * qtd

    conjuntos = total_unidades // combo_qtd
    if conjuntos <= 0:
        return 0.0

    custo_normal_combos = float(promocao.get("preco_original", 0.0)) * combo_qtd * conjuntos
    if custo_normal_combos <= 0:
        custo_normal_combos = subtotal_normal * conjuntos / max(1, total_unidades / combo_qtd)
    custo_combo = combo_preco * conjuntos
    desconto = custo_normal_combos - custo_combo
    return max(0.0, desconto)


def calcular_desconto_promocao_avancada(
    itens: List[ItemCupom],
    promocao: PromocaoData,
    produto_ids: set[int],
) -> float:
    tipo = str(promocao.get("tipo_desconto") or "").upper()
    if tipo == "LEVE_X_PAGUE_Y":
        return calcular_desconto_leve_x_pague_y(itens, promocao, produto_ids)
    if tipo == "DESCONTO_PROGRESSIVO":
        return calcular_desconto_progressivo(itens, promocao, produto_ids)
    if tipo == "COMBO":
        return calcular_desconto_combo(itens, promocao, produto_ids)
    return 0.0
