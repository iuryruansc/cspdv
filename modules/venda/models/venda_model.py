from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, cast

from database.connection import get_connection

CENT = Decimal("0.01")

@dataclass(frozen=True)
class LoteAlocacao:
    lote_id: int
    quantidade: int

class VendaModel:
    _STATUS_VENDA_OPERACIONAL = (
        "CONCLUIDA",
        "CONCLUIDA_COM_PENDENCIA",
        "PARCIALMENTE_REEMBOLSADA",
        "REEMBOLSADA",
    )

    @staticmethod
    def registrar_venda(
        *,
        cliente_id: int | None,
        usuario_id: int,
        funcionario_id: int,
        caixa_id: int,
        itens: Sequence[Dict[str, Any]],
        pagamentos: Sequence[Dict[str, Any]],
        desconto_global: float,
        valor_total: float,
        data_hora: datetime,
        status_venda: str = "CONCLUIDA",
        conta_receber: Optional[Dict[str, Any]] = None,
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            venda_id = VendaModel._inserir_venda(
                cursor=cursor,
                cliente_id=cliente_id,
                usuario_id=usuario_id,
                caixa_id=caixa_id,
                valor_total=valor_total,
                data_hora=data_hora,
                status_venda=status_venda,
            )

            totais_finais = VendaModel._ratear_total_final_itens(
                itens=itens,
                desconto_global=desconto_global,
                valor_total=valor_total,
            )

            for item, total_item in zip(itens, totais_finais):
                produto_id = int(item.get("id") or 0)
                quantidade = int(item.get("quantidade") or 0)
                if produto_id <= 0 or quantidade <= 0:
                    raise ValueError("Existe item inválido na venda.")

                alocacoes = VendaModel._alocar_lotes_saida(
                    cursor=cursor,
                    produto_id=produto_id,
                    quantidade=quantidade,
                )
                precos_unitarios = VendaModel._ratear_preco_unitario(
                    quantidade=quantidade,
                    total_item=total_item,
                )

                indice_preco = 0
                total_saida_produto = 0
                for alocacao in alocacoes:
                    fatia_precos = precos_unitarios[indice_preco : indice_preco + alocacao.quantidade]
                    indice_preco += alocacao.quantidade
                    total_saida_produto += alocacao.quantidade

                    for preco_unitario, quantidade_grupo in VendaModel._agrupar_precos(fatia_precos):
                        cursor.execute(
                            """
                            INSERT INTO itens_venda
                                (venda_id, lote_id, produto_id, quantidade, preco_unitario)
                            VALUES
                                (%s, %s, %s, %s, %s)
                            """,
                            (
                                venda_id,
                                alocacao.lote_id,
                                produto_id,
                                quantidade_grupo,
                                float(preco_unitario),
                            ),
                        )

                    cursor.execute(
                        """
                        UPDATE lotes
                        SET quantidade = quantidade - %s,
                            updatedAt = NOW()
                        WHERE id = %s
                        """,
                        (alocacao.quantidade, alocacao.lote_id),
                    )

                    cursor.execute(
                        """
                        INSERT INTO movimentacao_estoque
                            (lote_id, venda_id, data_hora, tipo, quantidade, usuario_id, observacao, tipo_movimento_id, ativo, createdAt, updatedAt)
                        VALUES
                            (%s, %s, %s, %s, %s, %s, %s, NULL, 'S', NOW(), NOW())
                        """,
                        (
                            alocacao.lote_id,
                            venda_id,
                            data_hora,
                            "saida_venda",
                            alocacao.quantidade,
                            funcionario_id,
                            f"Saida por venda #{venda_id}",
                        ),
                    )

                cursor.execute(
                    """
                    UPDATE produtos
                    SET quantidade_estoque = quantidade_estoque - %s,
                        updatedAt = NOW()
                    WHERE id = %s
                    """,
                    (total_saida_produto, produto_id),
                )

            for pagamento in pagamentos:
                forma_pagamento = str(pagamento.get("forma") or "").strip()
                valor_pago = Decimal(str(pagamento.get("valor") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
                if not forma_pagamento or valor_pago <= 0:
                    continue
                cursor.execute(
                    """
                    INSERT INTO pagamento_parcial
                        (venda_id, data_pagamento, valor_pago, forma_pagamento, observacao, createdAt, updatedAt)
                    VALUES
                        (%s, %s, %s, %s, NULL, NOW(), NOW())
                    """,
                    (venda_id, data_hora, float(valor_pago), forma_pagamento),
                )

            if conta_receber:
                VendaModel._inserir_conta_receber(
                    cursor=cursor,
                    venda_id=venda_id,
                    cliente_id=int(conta_receber.get("cliente_id") or 0),
                    usuario_id=usuario_id,
                    caixa_id=caixa_id,
                    data_hora=data_hora,
                    dados=conta_receber,
                )

            conn.commit()
            return venda_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_resumo_por_caixa(caixa_id: int) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS vendas_dia,
                    COALESCE(SUM(valor_total), 0) AS faturamento_total
                FROM vendas
                WHERE caixa_id = %s
                  AND status IN ('CONCLUIDA', 'CONCLUIDA_COM_PENDENCIA', 'PARCIALMENTE_REEMBOLSADA', 'REEMBOLSADA')
                """,
                (caixa_id,),
            )
            vendas = cursor.fetchone() or {}

            cursor.execute(
                """
                SELECT
                    pp.forma_pagamento,
                    COUNT(*) AS qtd_vendas,
                    COALESCE(SUM(pp.valor_pago), 0) AS total
                FROM pagamento_parcial pp
                INNER JOIN vendas v ON v.id = pp.venda_id
                WHERE v.caixa_id = %s
                  AND v.status IN ('CONCLUIDA', 'CONCLUIDA_COM_PENDENCIA', 'PARCIALMENTE_REEMBOLSADA', 'REEMBOLSADA')
                GROUP BY pp.forma_pagamento
                ORDER BY pp.forma_pagamento
                """,
                (caixa_id,),
            )
            totais_forma_pagamento = list(cursor.fetchall())

            cursor.execute(
                """
                SELECT COALESCE(SUM(pp.valor_pago), 0) AS faturamento_dinheiro
                FROM pagamento_parcial pp
                INNER JOIN vendas v ON v.id = pp.venda_id
                WHERE v.caixa_id = %s
                  AND v.status IN ('CONCLUIDA', 'CONCLUIDA_COM_PENDENCIA', 'PARCIALMENTE_REEMBOLSADA', 'REEMBOLSADA')
                  AND LOWER(pp.forma_pagamento) = 'dinheiro'
                """,
                (caixa_id,),
            )
            vendas_dict = cast(Dict[str, Any], vendas)
            dinheiro = cast(Dict[str, Any], cursor.fetchone() or {})

            return {
                "vendas_dia": int(vendas_dict.get("vendas_dia") or 0),
                "faturamento_total": float(vendas_dict.get("faturamento_total") or 0.0),
                "faturamento_dinheiro": float(dinheiro.get("faturamento_dinheiro") or 0.0),
                "totais_forma_pagamento": totais_forma_pagamento,
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _inserir_venda(
        *,
        cursor,
        cliente_id: int | None,
        usuario_id: int,
        caixa_id: int,
        valor_total: float,
        data_hora: datetime,
        status_venda: str,
    ) -> int:
        cursor.execute(
            """
            INSERT INTO vendas
                (data_hora, cliente_id, usuario_id, caixa_id, valor_total, status, createdAt, updatedAt)
            VALUES
                (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """,
            (data_hora, cliente_id, usuario_id, caixa_id, valor_total, status_venda),
        )
        venda_id = cursor.lastrowid
        if venda_id is None:
            raise RuntimeError("Não foi possível obter o ID da venda registrada.")
        return int(venda_id)

    @staticmethod
    def _inserir_conta_receber(
        *,
        cursor,
        venda_id: int,
        cliente_id: int,
        usuario_id: int,
        caixa_id: int,
        data_hora: datetime,
        dados: Dict[str, Any],
    ) -> None:
        if cliente_id <= 0:
            raise ValueError("Cliente inválido para gerar conta a receber.")

        valor_total = Decimal(str(dados.get("valor_total") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
        valor_recebido = Decimal(str(dados.get("valor_recebido") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
        valor_aberto = Decimal(str(dados.get("valor_aberto") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
        data_vencimento = str(dados.get("data_vencimento") or "").strip()
        if not data_vencimento:
            raise ValueError("Informe a data de vencimento da pendência.")

        cursor.execute(
            """
            INSERT INTO contas_receber
                (
                    venda_id, cliente_id, usuario_id, caixa_id, descricao, observacao,
                    valor_total, valor_recebido, valor_aberto, data_emissao, data_vencimento,
                    status, ativo, createdAt, updatedAt
                )
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDENTE', 'S', NOW(), NOW())
            """,
            (
                venda_id,
                cliente_id,
                usuario_id,
                caixa_id,
                f"Saldo pendente da venda #{venda_id}",
                str(dados.get("observacao") or "").strip() or None,
                float(valor_total),
                float(valor_recebido),
                float(valor_aberto),
                data_hora,
                data_vencimento,
            ),
        )

    @staticmethod
    def _alocar_lotes_saida(*, cursor, produto_id: int, quantidade: int) -> List[LoteAlocacao]:
        produto = VendaModel._obter_produto_para_saida(cursor=cursor, produto_id=produto_id)
        estoque_atual = int(produto.get("quantidade_estoque") or 0)
        if quantidade > estoque_atual:
            raise ValueError(f"Estoque insuficiente para o produto ID {produto_id}.")

        lotes = VendaModel._listar_lotes_ativos_produto(cursor=cursor, produto_id=produto_id)
        if not lotes:
            VendaModel._criar_lote_padrao(cursor=cursor, produto=produto, quantidade_inicial=estoque_atual)
            lotes = VendaModel._listar_lotes_ativos_produto(cursor=cursor, produto_id=produto_id)
        elif len(lotes) == 1 and str(lotes[0].get("numero_lote") or "").startswith("AUTO-"):
            lote_id = int(lotes[0]["id"])
            cursor.execute(
                """
                UPDATE lotes
                SET quantidade = %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (estoque_atual, lote_id),
            )
            lotes[0]["quantidade"] = estoque_atual

        restante = quantidade
        alocacoes: List[LoteAlocacao] = []
        for lote in lotes:
            disponivel = int(lote.get("quantidade") or 0)
            if disponivel <= 0:
                continue
            usar = min(disponivel, restante)
            if usar <= 0:
                continue
            alocacoes.append(LoteAlocacao(lote_id=int(lote["id"]), quantidade=usar))
            restante -= usar
            if restante == 0:
                break

        if restante > 0:
            raise ValueError(f"Não foi possível alocar lotes suficientes para o produto ID {produto_id}.")

        return alocacoes

    @staticmethod
    def _obter_produto_para_saida(*, cursor, produto_id: int) -> Dict[str, Any]:
        cursor.execute(
            """
            SELECT id, nome, preco_compra, preco_venda, quantidade_estoque, ativo
            FROM produtos
            WHERE id = %s
            LIMIT 1
            """,
            (produto_id,),
        )
        produto = cursor.fetchone()
        if not produto:
            raise ValueError(f"Produto ID {produto_id} não encontrado.")
        if str(produto.get("ativo") or "N") != "S":
            raise ValueError(f"O produto ID {produto_id} esta inativo.")
        return produto

    @staticmethod
    def _listar_lotes_ativos_produto(*, cursor, produto_id: int) -> List[Dict[str, Any]]:
        cursor.execute(
            """
            SELECT id, numero_lote, quantidade, data_validade
            FROM lotes
            WHERE produto_id = %s
              AND ativo = 'S'
            ORDER BY data_validade, id
            """,
            (produto_id,),
        )
        return list(cursor.fetchall())

    @staticmethod
    def _criar_lote_padrao(*, cursor, produto: Dict[str, Any], quantidade_inicial: int) -> None:
        produto_id = int(produto["id"])
        cursor.execute(
            """
            INSERT INTO lotes
                (produto_id, preco_compra, preco_venda, numero_lote, quantidade, data_validade, localizacao, createdAt, updatedAt, ativo)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 'S')
            """,
            (
                produto_id,
                float(produto.get("preco_compra") or 0.0),
                float(produto.get("preco_venda") or 0.0),
                f"AUTO-{produto_id:06d}",
                quantidade_inicial,
                date(2099, 12, 31),
                "AUTO",
            ),
        )

    @staticmethod
    def _ratear_total_final_itens(
        *,
        itens: Sequence[Dict[str, Any]],
        desconto_global: float,
        valor_total: float,
    ) -> List[Decimal]:
        totais_item = [
            Decimal(str(item.get("total") or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
            for item in itens
        ]
        total_itens = sum(totais_item, Decimal("0.00"))
        desconto_global_dec = Decimal(str(desconto_global or 0)).quantize(CENT, rounding=ROUND_HALF_UP)
        valor_total_dec = Decimal(str(valor_total or 0)).quantize(CENT, rounding=ROUND_HALF_UP)

        if desconto_global_dec <= Decimal("0.00") or total_itens <= Decimal("0.00"):
            return totais_item

        shares: List[Decimal] = []
        acumulado = Decimal("0.00")
        for index, total_item in enumerate(totais_item):
            if index == len(totais_item) - 1:
                share = desconto_global_dec - acumulado
            else:
                share = (desconto_global_dec * total_item / total_itens).quantize(CENT, rounding=ROUND_HALF_UP)
                acumulado += share
            shares.append(share)

        totais_finais = [
            max(Decimal("0.00"), total_item - shares[index])
            for index, total_item in enumerate(totais_item)
        ]
        diferenca = valor_total_dec - sum(totais_finais, Decimal("0.00"))
        if totais_finais:
            totais_finais[-1] = max(Decimal("0.00"), totais_finais[-1] + diferenca)
        return totais_finais

    @staticmethod
    def _ratear_preco_unitario(*, quantidade: int, total_item: Decimal) -> List[Decimal]:
        if quantidade <= 0:
            return []
        total_centavos = int((total_item * 100).to_integral_value(rounding=ROUND_HALF_UP))
        base_centavos = total_centavos // quantidade
        resto = total_centavos % quantidade
        valores = [Decimal(base_centavos) / 100 for _ in range(quantidade)]
        for index in range(resto):
            valores[index] += CENT
        return valores

    @staticmethod
    def _agrupar_precos(precos_unitarios: Iterable[Decimal]) -> List[Tuple[Decimal, int]]:
        grupos: Dict[Decimal, int] = {}
        for preco in precos_unitarios:
            preco_limpo = Decimal(preco).quantize(CENT, rounding=ROUND_HALF_UP)
            grupos[preco_limpo] = grupos.get(preco_limpo, 0) + 1
        return list(grupos.items())
