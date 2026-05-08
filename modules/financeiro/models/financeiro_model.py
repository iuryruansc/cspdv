from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple, cast

from database.connection import get_connection

class FinanceiroModel:
    @staticmethod
    def listar_pdvs() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, identificacao, descricao
                FROM pdvs
                WHERE ativo = 'S'
                  AND status = 'ativo'
                ORDER BY identificacao
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_formas_pagamento() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome
                FROM formas_pagamento
                WHERE ativo = 'S'
                ORDER BY nome
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_resumo_financeiro(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: Optional[int] = None,
        forma_pagamento: Optional[str] = None,
    ) -> Dict[str, Any]:
        inicio, fim = FinanceiroModel._periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            pdv_clause, pdv_params = FinanceiroModel._pdv_clause("v.caixa_id", pdv_id, alias_caixa="cx")

            params_recebimentos: List[Any] = [inicio, fim]
            params_recebimentos.extend(pdv_params)
            forma_clause = ""
            if forma_pagamento:
                forma_clause = " AND pp.forma_pagamento = %s"
                params_recebimentos.append(forma_pagamento)

            cursor.execute(
                f"""
                SELECT COALESCE(SUM(pp.valor_pago), 0) AS total
                FROM pagamento_parcial pp
                INNER JOIN vendas v ON v.id = pp.venda_id
                LEFT JOIN caixas cx ON cx.id = v.caixa_id
                WHERE pp.data_pagamento >= %s
                  AND pp.data_pagamento < %s
                  AND v.status IN ('CONCLUIDA', 'CONCLUIDA_COM_PENDENCIA', 'PARCIALMENTE_REEMBOLSADA', 'REEMBOLSADA')
                  {pdv_clause}
                  {forma_clause}
                """,
                tuple(params_recebimentos),
            )
            recebimentos = cast(Dict[str, Any], cursor.fetchone() or {})

            params_entradas: List[Any] = [inicio, fim]
            params_entradas.extend(FinanceiroModel._caixa_filter_params(pdv_id))
            cursor.execute(
                f"""
                SELECT COALESCE(SUM(cm.valor), 0) AS total
                FROM caixa_movimentacoes cm
                INNER JOIN caixa_motivos mot ON mot.id = cm.caixa_motivo_id
                INNER JOIN caixas c ON c.id = cm.caixa_id
                WHERE cm.data_hora >= %s
                  AND cm.data_hora < %s
                  AND cm.ativo = 'S'
                  AND cm.estornado = 0
                  AND mot.tipo_padrao IN ('suprimento', 'troco')
                  {FinanceiroModel._caixa_filter_clause(pdv_id)}
                """,
                tuple(params_entradas),
            )
            entradas_manuais = cast(Dict[str, Any], cursor.fetchone() or {})

            params_saidas: List[Any] = [inicio, fim]
            params_saidas.extend(FinanceiroModel._caixa_filter_params(pdv_id))
            cursor.execute(
                f"""
                SELECT COALESCE(SUM(cm.valor), 0) AS total
                FROM caixa_movimentacoes cm
                INNER JOIN caixa_motivos mot ON mot.id = cm.caixa_motivo_id
                INNER JOIN caixas c ON c.id = cm.caixa_id
                WHERE cm.data_hora >= %s
                  AND cm.data_hora < %s
                  AND cm.ativo = 'S'
                  AND cm.estornado = 0
                  AND mot.tipo_padrao = 'sangria'
                  {FinanceiroModel._caixa_filter_clause(pdv_id)}
                """,
                tuple(params_saidas),
            )
            sangrias = cast(Dict[str, Any], cursor.fetchone() or {})

            params_reembolsos: List[Any] = [inicio, fim]
            params_reembolsos.extend(pdv_params)
            reembolso_forma_clause = ""
            if forma_pagamento:
                reembolso_forma_clause = """
                  AND EXISTS (
                        SELECT 1
                        FROM venda_reembolso_pagamentos vrp
                        WHERE vrp.reembolso_id = vr.id
                          AND vrp.forma_pagamento = %s
                  )
                """
                params_reembolsos.append(forma_pagamento)

            cursor.execute(
                f"""
                SELECT
                    COUNT(*) AS quantidade,
                    COALESCE(SUM(vr.valor_total), 0) AS total
                FROM venda_reembolsos vr
                INNER JOIN vendas v ON v.id = vr.venda_id
                LEFT JOIN caixas cx ON cx.id = v.caixa_id
                WHERE vr.ativo = 'S'
                  AND vr.status = 'CONCLUIDO'
                  AND vr.data_hora >= %s
                  AND vr.data_hora < %s
                  {pdv_clause}
                  {reembolso_forma_clause}
                """,
                tuple(params_reembolsos),
            )
            reembolsos = cast(Dict[str, Any], cursor.fetchone() or {})

            params_saldo = FinanceiroModel._caixa_filter_params(pdv_id)
            cursor.execute(
                f"""
                SELECT
                    c.id,
                    c.valor_abertura
                FROM caixas c
                WHERE c.status = 'aberto'
                  {FinanceiroModel._caixa_filter_clause(pdv_id)}
                """,
                tuple(params_saldo),
            )
            caixas_abertos = cast(List[Dict[str, Any]], cursor.fetchall() or [])

            saldo_atual = Decimal("0")
            for caixa in caixas_abertos:
                caixa_id = int(caixa.get("id") or 0)
                saldo_atual += Decimal(caixa.get("valor_abertura") or 0)
                saldo_atual += FinanceiroModel._somar_pagamentos_dinheiro_caixa(cursor, caixa_id)
                saldo_atual += FinanceiroModel._somar_movimentacao_caixa(cursor, caixa_id, ("suprimento", "troco"))
                saldo_atual -= FinanceiroModel._somar_movimentacao_caixa(cursor, caixa_id, ("sangria",))
                saldo_atual -= FinanceiroModel._somar_reembolsos_caixa(cursor, caixa_id)

            total_entradas = Decimal(recebimentos.get("total") or 0) + Decimal(entradas_manuais.get("total") or 0)
            total_saidas = Decimal(sangrias.get("total") or 0) + Decimal(reembolsos.get("total") or 0)

            return {
                "saldo_atual_caixa": saldo_atual,
                "entradas_periodo": total_entradas,
                "saidas_periodo": total_saidas,
                "reembolsos_periodo": int(reembolsos.get("quantidade") or 0),
                "contas_abertas_periodo": FinanceiroModel._contar_contas_abertas(
                    cursor,
                    data_inicial=data_inicial,
                    data_final=data_final,
                    pdv_id=pdv_id,
                ),
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_movimentacoes_caixa(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: Optional[int] = None,
        limite: int = 100,
    ) -> List[Dict[str, Any]]:
        inicio, fim = FinanceiroModel._periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            params: List[Any] = [inicio, fim]
            params.extend(FinanceiroModel._caixa_filter_params(pdv_id))
            params.append(int(limite))
            cursor.execute(
                f"""
                SELECT
                    cm.data_hora,
                    p.identificacao AS pdv,
                    COALESCE(u.nome, '-') AS operador,
                    mot.descricao AS motivo,
                    COALESCE(fp.nome, cm.forma_pagamento_id, '-') AS forma_pagamento,
                    cm.valor
                FROM caixa_movimentacoes cm
                INNER JOIN caixa_motivos mot ON mot.id = cm.caixa_motivo_id
                INNER JOIN caixas c ON c.id = cm.caixa_id
                INNER JOIN pdvs p ON p.id = c.pdv_id
                LEFT JOIN usuarios u ON u.id = cm.usuario_id
                LEFT JOIN formas_pagamento fp ON fp.id = cm.forma_pagamento_id
                WHERE cm.ativo = 'S'
                  AND cm.estornado = 0
                  AND cm.data_hora >= %s
                  AND cm.data_hora < %s
                  {FinanceiroModel._caixa_filter_clause(pdv_id)}
                ORDER BY cm.data_hora DESC, cm.id DESC
                LIMIT %s
                """,
                tuple(params),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_recebimentos(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: Optional[int] = None,
        forma_pagamento: Optional[str] = None,
        limite: int = 100,
    ) -> List[Dict[str, Any]]:
        inicio, fim = FinanceiroModel._periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            pdv_clause, pdv_params = FinanceiroModel._pdv_clause("v.caixa_id", pdv_id, alias_caixa="cx")
            params: List[Any] = [inicio, fim]
            params.extend(pdv_params)
            forma_clause = ""
            if forma_pagamento:
                forma_clause = " AND pp.forma_pagamento = %s"
                params.append(forma_pagamento)
            params.append(int(limite))

            cursor.execute(
                f"""
                SELECT
                    v.id AS venda_id,
                    COALESCE(c.nome, 'Consumidor Final') AS cliente,
                    pp.forma_pagamento,
                    v.status,
                    pp.valor_pago
                FROM pagamento_parcial pp
                INNER JOIN vendas v ON v.id = pp.venda_id
                LEFT JOIN clientes c ON c.id = v.cliente_id
                LEFT JOIN caixas cx ON cx.id = v.caixa_id
                WHERE pp.data_pagamento >= %s
                  AND pp.data_pagamento < %s
                  AND v.status IN ('CONCLUIDA', 'CONCLUIDA_COM_PENDENCIA', 'PARCIALMENTE_REEMBOLSADA', 'REEMBOLSADA')
                  {pdv_clause}
                  {forma_clause}
                ORDER BY pp.data_pagamento DESC, pp.id DESC
                LIMIT %s
                """,
                tuple(params),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_vendas_registradas(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: Optional[int] = None,
        forma_pagamento: Optional[str] = None,
        busca: Optional[str] = None,
        limite: int = 100,
    ) -> List[Dict[str, Any]]:
        inicio, fim = FinanceiroModel._periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            pdv_clause, pdv_params = FinanceiroModel._pdv_clause("v.caixa_id", pdv_id, alias_caixa="cx")
            params: List[Any] = [inicio, fim]
            params.extend(pdv_params)
            forma_clause = ""
            if forma_pagamento:
                forma_clause = " AND pp.forma_pagamento = %s"
                params.append(forma_pagamento)
            busca_clause = ""
            if busca:
                busca_clause = """
                    AND (
                          COALESCE(c.nome, 'Consumidor Final') LIKE %s
                          OR CAST(v.id AS CHAR) LIKE %s
                    )
                """
                termo = f"%{busca.strip()}%"
                params.extend([termo, termo])
            params.append(int(limite))

            cursor.execute(
                f"""
                SELECT
                    v.id AS venda_id,
                    COALESCE(c.nome, 'Consumidor Final') AS cliente,
                    COALESCE(GROUP_CONCAT(DISTINCT pp.forma_pagamento ORDER BY pp.id SEPARATOR ' + '), '-') AS forma_pagamento,
                    v.status,
                    v.valor_total
                FROM vendas v
                LEFT JOIN clientes c ON c.id = v.cliente_id
                LEFT JOIN pagamento_parcial pp ON pp.venda_id = v.id
                LEFT JOIN caixas cx ON cx.id = v.caixa_id
                  WHERE pp.data_pagamento >= %s
                    AND pp.data_pagamento < %s
                    AND v.status IN ('CONCLUIDA', 'CONCLUIDA_COM_PENDENCIA', 'PARCIALMENTE_REEMBOLSADA', 'REEMBOLSADA')
                    {pdv_clause}
                    {forma_clause}
                    {busca_clause}
                  GROUP BY v.id, c.nome, v.status, v.valor_total
                ORDER BY MAX(pp.data_pagamento) DESC, v.id DESC
                LIMIT %s
                """,
                tuple(params),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_contas_receber(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: Optional[int] = None,
        busca: Optional[str] = None,
        status_filtro: Optional[str] = None,
        limite: int = 100,
    ) -> List[Dict[str, Any]]:
        inicio, fim = FinanceiroModel._periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            pdv_clause, pdv_params = FinanceiroModel._pdv_clause("cr.caixa_id", pdv_id, alias_caixa="cx")
            params: List[Any] = [inicio.date(), fim.date()]
            params.extend(pdv_params)
            busca_clause = ""
            if busca:
                busca_clause = """
                  AND (
                        c.nome LIKE %s
                        OR CAST(cr.id AS CHAR) LIKE %s
                        OR CAST(cr.venda_id AS CHAR) LIKE %s
                        OR COALESCE(cr.descricao, '') LIKE %s
                  )
                """
                termo = f"%{busca.strip()}%"
                params.extend([termo, termo, termo, termo])
            status_clause = ""
            if status_filtro == "TODAS":
                status_clause = ""
            elif status_filtro in (None, "ABERTAS"):
                status_clause = " AND cr.status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA')"
            elif status_filtro == "PENDENTE":
                status_clause = " AND cr.status = 'PENDENTE'"
            elif status_filtro == "PARCIALMENTE_RECEBIDA":
                status_clause = " AND cr.status = 'PARCIALMENTE_RECEBIDA'"
            elif status_filtro == "QUITADA":
                status_clause = " AND cr.status = 'QUITADA'"
            elif status_filtro == "VENCIDA":
                status_clause = " AND cr.status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA') AND cr.data_vencimento < CURDATE()"
            elif status_filtro == "VENCE_HOJE":
                status_clause = " AND cr.status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA') AND cr.data_vencimento = CURDATE()"
            elif status_filtro == "PROXIMOS_7_DIAS":
                status_clause = (
                    " AND cr.status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA')"
                    " AND cr.data_vencimento > CURDATE()"
                    " AND cr.data_vencimento <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)"
                )
            params.append(int(limite))
            cursor.execute(
                f"""
                SELECT
                    cr.id AS conta_id,
                    cr.venda_id,
                    COALESCE(c.nome, 'Consumidor Final') AS cliente,
                    cr.data_vencimento,
                    cr.status,
                    cr.valor_total,
                    cr.valor_recebido,
                    cr.valor_aberto,
                    COALESCE((
                        SELECT COUNT(*)
                        FROM contas_receber_recebimentos crr
                        WHERE crr.conta_receber_id = cr.id
                          AND crr.ativo = 'S'
                    ), 0) AS total_recebimentos,
                    (
                        SELECT MAX(crr.data_recebimento)
                        FROM contas_receber_recebimentos crr
                        WHERE crr.conta_receber_id = cr.id
                          AND crr.ativo = 'S'
                    ) AS ultimo_recebimento,
                    CASE
                        WHEN cr.status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA') AND cr.data_vencimento < CURDATE() THEN 1
                        ELSE 0
                    END AS vencida,
                    CASE
                        WHEN cr.status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA') AND cr.data_vencimento < CURDATE()
                        THEN DATEDIFF(CURDATE(), cr.data_vencimento)
                        ELSE 0
                    END AS dias_atraso
                FROM contas_receber cr
                LEFT JOIN clientes c ON c.id = cr.cliente_id
                LEFT JOIN caixas cx ON cx.id = cr.caixa_id
                WHERE cr.ativo = 'S'
                  AND cr.data_vencimento >= %s
                  AND cr.data_vencimento < %s
                  {pdv_clause}
                  {busca_clause}
                  {status_clause}
                ORDER BY cr.data_vencimento ASC, cr.id DESC
                LIMIT %s
                """,
                tuple(params),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_conta_receber_detalhada(conta_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    cr.id,
                    cr.venda_id,
                    cr.cliente_id,
                    COALESCE(c.nome, 'Consumidor Final') AS cliente,
                    cr.descricao,
                    cr.observacao,
                    cr.valor_total,
                    cr.valor_recebido,
                    cr.valor_aberto,
                    cr.data_emissao,
                    cr.data_vencimento,
                    cr.status,
                    CASE
                        WHEN cr.status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA') AND cr.data_vencimento < CURDATE()
                        THEN DATEDIFF(CURDATE(), cr.data_vencimento)
                        ELSE 0
                    END AS dias_atraso
                FROM contas_receber cr
                LEFT JOIN clientes c ON c.id = cr.cliente_id
                WHERE cr.id = %s
                  AND cr.ativo = 'S'
                LIMIT 1
                """,
                (int(conta_id),),
            )
            conta = cursor.fetchone()
            if not conta:
                return None

            cursor.execute(
                """
                SELECT
                    crr.data_recebimento,
                    COALESCE(fp.nome, '-') AS forma_pagamento,
                    crr.valor_recebido,
                    COALESCE(u.nome, '-') AS operador,
                    COALESCE(crr.observacao, '') AS observacao
                FROM contas_receber_recebimentos crr
                LEFT JOIN formas_pagamento fp ON fp.id = crr.forma_pagamento_id
                LEFT JOIN usuarios u ON u.id = crr.usuario_id
                WHERE crr.conta_receber_id = %s
                  AND crr.ativo = 'S'
                ORDER BY crr.data_recebimento DESC, crr.id DESC
                """,
                (int(conta_id),),
            )
            recebimentos = list(cursor.fetchall())
            ultimo_recebimento = recebimentos[0]["data_recebimento"] if recebimentos else None
            return {
                "conta": conta,
                "recebimentos": recebimentos,
                "resumo": {
                    "quantidade_recebimentos": len(recebimentos),
                    "ultimo_recebimento": ultimo_recebimento,
                    "dias_atraso": int(conta.get("dias_atraso") or 0),
                    "em_aberto": Decimal(str(conta.get("valor_aberto") or 0)),
                    "valor_recebido": Decimal(str(conta.get("valor_recebido") or 0)),
                },
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def registrar_recebimento_conta(
        *,
        conta_id: int,
        usuario_id: int,
        caixa_id: int,
        forma_pagamento_id: int,
        valor_recebido: Decimal,
        observacao: str,
        data_recebimento: datetime,
    ) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    cr.id,
                    cr.venda_id,
                    cr.valor_total,
                    cr.valor_recebido,
                    cr.valor_aberto,
                    cr.status
                FROM contas_receber cr
                WHERE cr.id = %s
                  AND cr.ativo = 'S'
                LIMIT 1
                """,
                (int(conta_id),),
            )
            conta = cursor.fetchone()
            if not conta:
                raise ValueError("Conta a receber não encontrada.")

            aberto_atual = Decimal(str(conta.get("valor_aberto") or 0))
            if valor_recebido <= Decimal("0.00"):
                raise ValueError("Informe um valor maior que zero para o recebimento.")
            if valor_recebido > aberto_atual:
                raise ValueError("O valor informado é maior que o saldo em aberto da conta.")

            cursor.execute(
                """
                SELECT id, nome
                FROM formas_pagamento
                WHERE id = %s
                LIMIT 1
                """,
                (int(forma_pagamento_id),),
            )
            forma = cursor.fetchone()
            if not forma:
                raise ValueError("Forma de pagamento não encontrada.")

            cursor.execute(
                """
                INSERT INTO contas_receber_recebimentos
                    (conta_receber_id, usuario_id, caixa_id, forma_pagamento_id, valor_recebido, data_recebimento, observacao, ativo, createdAt, updatedAt)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, 'S', NOW(), NOW())
                """,
                (
                    int(conta_id),
                    int(usuario_id),
                    int(caixa_id),
                    int(forma_pagamento_id),
                    float(valor_recebido),
                    data_recebimento,
                    observacao or None,
                ),
            )

            cursor.execute(
                """
                INSERT INTO pagamento_parcial
                    (venda_id, data_pagamento, valor_pago, forma_pagamento, observacao, createdAt, updatedAt)
                VALUES
                    (%s, %s, %s, %s, %s, NOW(), NOW())
                """,
                (
                    int(conta["venda_id"]),
                    data_recebimento,
                    float(valor_recebido),
                    str(forma.get("nome") or "Forma"),
                    observacao or "Recebimento posterior de pendência",
                ),
            )

            novo_recebido = Decimal(str(conta.get("valor_recebido") or 0)) + valor_recebido
            novo_aberto = aberto_atual - valor_recebido
            novo_status = "QUITADA" if novo_aberto <= Decimal("0.00") else "PARCIALMENTE_RECEBIDA"

            cursor.execute(
                """
                UPDATE contas_receber
                SET valor_recebido = %s,
                    valor_aberto = %s,
                    status = %s,
                    updatedAt = NOW()
                WHERE id = %s
                """,
                (float(novo_recebido), float(novo_aberto), novo_status, int(conta_id)),
            )

            if novo_status == "QUITADA":
                cursor.execute(
                    """
                    UPDATE vendas
                    SET status = 'CONCLUIDA',
                        updatedAt = NOW()
                    WHERE id = %s
                      AND status = 'CONCLUIDA_COM_PENDENCIA'
                    """,
                    (int(conta["venda_id"]),),
                )

            conn.commit()
            return {
                "conta_id": int(conta_id),
                "venda_id": int(conta["venda_id"]),
                "valor_recebido": valor_recebido,
                "valor_aberto": novo_aberto,
                "status": novo_status,
                "forma_pagamento": str(forma.get("nome") or "Forma"),
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_reembolsos(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: Optional[int] = None,
        forma_pagamento: Optional[str] = None,
        limite: int = 100,
    ) -> List[Dict[str, Any]]:
        inicio, fim = FinanceiroModel._periodo(data_inicial, data_final)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            pdv_clause, pdv_params = FinanceiroModel._pdv_clause("v.caixa_id", pdv_id, alias_caixa="cx")
            params: List[Any] = [inicio, fim]
            params.extend(pdv_params)
            forma_clause = ""
            if forma_pagamento:
                forma_clause = """
                  AND EXISTS (
                        SELECT 1
                        FROM venda_reembolso_pagamentos vrp
                        WHERE vrp.reembolso_id = vr.id
                          AND vrp.forma_pagamento = %s
                  )
                """
                params.append(forma_pagamento)
            params.append(int(limite))

            cursor.execute(
                f"""
                SELECT
                    vr.id AS reembolso_id,
                    vr.venda_id,
                    vr.tipo,
                    vr.motivo,
                    vr.status,
                    vr.valor_total,
                    vr.data_hora
                FROM venda_reembolsos vr
                INNER JOIN vendas v ON v.id = vr.venda_id
                LEFT JOIN caixas cx ON cx.id = v.caixa_id
                WHERE vr.ativo = 'S'
                  AND vr.data_hora >= %s
                  AND vr.data_hora < %s
                  {pdv_clause}
                  {forma_clause}
                ORDER BY vr.data_hora DESC, vr.id DESC
                LIMIT %s
                """,
                tuple(params),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obter_venda_detalhada(venda_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    v.id,
                    v.data_hora,
                    v.valor_total,
                    v.status,
                    COALESCE(c.nome, 'Consumidor Final') AS cliente,
                    COALESCE(u.nome, '-') AS operador,
                    COALESCE(p.identificacao, '-') AS pdv
                FROM vendas v
                LEFT JOIN clientes c ON c.id = v.cliente_id
                LEFT JOIN usuarios u ON u.id = v.usuario_id
                LEFT JOIN caixas cx ON cx.id = v.caixa_id
                LEFT JOIN pdvs p ON p.id = cx.pdv_id
                WHERE v.id = %s
                LIMIT 1
                """,
                (int(venda_id),),
            )
            venda = cursor.fetchone()
            if not venda:
                return None

            cursor.execute(
                """
                SELECT
                    iv.id AS item_venda_id,
                    iv.lote_id,
                    iv.produto_id,
                    COALESCE(pr.codigo_barras, '-') AS codigo_barras,
                    COALESCE(pr.nome, '-') AS produto,
                    iv.quantidade,
                    iv.preco_unitario,
                    (iv.quantidade * iv.preco_unitario) AS total_item,
                    COALESCE((
                        SELECT SUM(vri.quantidade)
                        FROM venda_reembolso_itens vri
                        INNER JOIN venda_reembolsos vr ON vr.id = vri.reembolso_id
                        WHERE vri.item_venda_id = iv.id
                          AND vr.ativo = 'S'
                          AND vr.status = 'CONCLUIDO'
                    ), 0) AS quantidade_reembolsada
                FROM itens_venda iv
                LEFT JOIN produtos pr ON pr.id = iv.produto_id
                WHERE iv.venda_id = %s
                ORDER BY iv.id
                """,
                (int(venda_id),),
            )
            itens = list(cursor.fetchall())
            for item in itens:
                quantidade = int(item.get("quantidade") or 0)
                quantidade_reembolsada = int(item.get("quantidade_reembolsada") or 0)
                item["quantidade_disponivel"] = max(0, quantidade - quantidade_reembolsada)

            cursor.execute(
                """
                SELECT
                    forma_pagamento,
                    valor_pago,
                    data_pagamento
                FROM pagamento_parcial
                WHERE venda_id = %s
                ORDER BY id
                """,
                (int(venda_id),),
            )
            pagamentos = list(cursor.fetchall())

            cursor.execute(
                """
                SELECT
                    tipo,
                    motivo,
                    status,
                    valor_total,
                    data_hora
                FROM venda_reembolsos
                WHERE venda_id = %s
                  AND ativo = 'S'
                ORDER BY data_hora DESC, id DESC
                """,
                (int(venda_id),),
            )
            reembolsos = list(cursor.fetchall())

            return {
                "venda": venda,
                "itens": itens,
                "pagamentos": pagamentos,
                "reembolsos": reembolsos,
            }
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _periodo(data_inicial: date, data_final: date) -> Tuple[datetime, datetime]:
        inicio = datetime.combine(data_inicial, time.min)
        fim = datetime.combine(data_final + timedelta(days=1), time.min)
        return inicio, fim

    @staticmethod
    def _caixa_filter_clause(pdv_id: Optional[int]) -> str:
        return " AND c.pdv_id = %s" if pdv_id else ""

    @staticmethod
    def _caixa_filter_params(pdv_id: Optional[int]) -> List[Any]:
        return [int(pdv_id)] if pdv_id else []

    @staticmethod
    def _pdv_clause(caixa_field: str, pdv_id: Optional[int], *, alias_caixa: str) -> Tuple[str, List[Any]]:
        if not pdv_id:
            return "", []
        return f" AND {alias_caixa}.pdv_id = %s", [int(pdv_id)]

    @staticmethod
    def _somar_pagamentos_dinheiro_caixa(cursor: Any, caixa_id: int) -> Decimal:
        cursor.execute(
            """
            SELECT COALESCE(SUM(pp.valor_pago), 0) AS total
            FROM pagamento_parcial pp
            INNER JOIN vendas v ON v.id = pp.venda_id
            WHERE v.caixa_id = %s
              AND v.status IN ('CONCLUIDA', 'CONCLUIDA_COM_PENDENCIA', 'PARCIALMENTE_REEMBOLSADA', 'REEMBOLSADA')
              AND LOWER(TRIM(pp.forma_pagamento)) = 'dinheiro'
            """,
            (caixa_id,),
        )
        row = cast(Dict[str, Any], cursor.fetchone() or {})
        return Decimal(row.get("total") or 0)

    @staticmethod
    def _somar_movimentacao_caixa(cursor: Any, caixa_id: int, tipos: Sequence[str]) -> Decimal:
        marcadores = ", ".join(["%s"] * len(tipos))
        cursor.execute(
            f"""
            SELECT COALESCE(SUM(cm.valor), 0) AS total
            FROM caixa_movimentacoes cm
            INNER JOIN caixa_motivos mot ON mot.id = cm.caixa_motivo_id
            WHERE cm.caixa_id = %s
              AND cm.ativo = 'S'
              AND cm.estornado = 0
              AND mot.tipo_padrao IN ({marcadores})
            """,
            tuple([caixa_id, *tipos]),
        )
        row = cast(Dict[str, Any], cursor.fetchone() or {})
        return Decimal(row.get("total") or 0)

    @staticmethod
    def _somar_reembolsos_caixa(cursor: Any, caixa_id: int) -> Decimal:
        cursor.execute(
            """
            SELECT COALESCE(SUM(vr.valor_total), 0) AS total
            FROM venda_reembolsos vr
            INNER JOIN vendas v ON v.id = vr.venda_id
            WHERE v.caixa_id = %s
              AND vr.ativo = 'S'
              AND vr.status = 'CONCLUIDO'
            """,
            (caixa_id,),
        )
        row = cast(Dict[str, Any], cursor.fetchone() or {})
        return Decimal(row.get("total") or 0)

    @staticmethod
    def _contar_contas_abertas(
        cursor: Any,
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: Optional[int],
    ) -> int:
        inicio, fim = FinanceiroModel._periodo(data_inicial, data_final)
        params: List[Any] = [inicio.date(), fim.date()]
        if pdv_id:
            params.append(int(pdv_id))
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM contas_receber cr
            LEFT JOIN caixas cx ON cx.id = cr.caixa_id
            WHERE cr.ativo = 'S'
              AND cr.data_vencimento >= %s
              AND cr.data_vencimento < %s
              AND cr.status IN ('PENDENTE', 'PARCIALMENTE_RECEBIDA')
              {FinanceiroModel._pdv_clause('cr.caixa_id', pdv_id, alias_caixa='cx')[0]}
            """,
            tuple(params),
        )
        row = cast(Dict[str, Any], cursor.fetchone() or {})
        return int(row.get("total") or 0)
