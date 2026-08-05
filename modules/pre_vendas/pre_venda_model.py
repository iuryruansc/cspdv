import json
from typing import Any, Optional
from database.connection import db_cursor, db_transaction

class PreVendaModel:

    @staticmethod
    def criar(dados: dict[str, Any]) -> int:
        """Cria uma pré-venda e retorna o ID gerado."""
        with db_transaction(dictionary=False) as cur:
            itens_json = json.dumps(dados["itens"], ensure_ascii=False)

            cur.execute(
                """
                INSERT INTO pre_vendas
                    (usuario_id, cliente_id, data_hora, valor_total,
                     itens_json, desconto_global, desconto_itens,
                     desconto_total, status, observacao)
                VALUES
                    (%s, %s, NOW(), %s, %s, %s, %s, %s, 'PENDENTE', %s)
                """,
                (
                    dados["usuario_id"],
                    dados.get("cliente_id"),
                    dados["valor_total"],
                    itens_json,
                    dados.get("desconto_global", 0.0),
                    dados.get("desconto_itens", 0.0),
                    dados.get("desconto_total", 0.0),
                    dados.get("observacao"),
                ),
            )
            pre_venda_id = cur.lastrowid

            cur.execute(
                "UPDATE pre_vendas SET numero_venda = %s WHERE id = %s",
                (pre_venda_id, pre_venda_id),
            )

            return pre_venda_id

    @staticmethod
    def listar_pendentes() -> list[dict[str, Any]]:
        """Lista todas as pré-vendas com status PENDENTE."""
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    pv.id,
                    pv.numero_venda,
                    COALESCE(c.nome, 'Consumidor Final') AS cliente_nome,
                    u.nome AS usuario_nome,
                    pv.data_hora,
                    pv.valor_total,
                    pv.desconto_global,
                    pv.desconto_itens,
                    pv.desconto_total,
                    pv.observacao,
                    pv.itens_json
                FROM pre_vendas pv
                LEFT JOIN clientes c ON c.id = pv.cliente_id
                LEFT JOIN usuarios u ON u.id = pv.usuario_id
                WHERE pv.status = 'PENDENTE'
                ORDER BY pv.id DESC
                """
            )
            resultado = cur.fetchall()

            for item in resultado:
                if isinstance(item.get("itens_json"), str):
                    item["itens_json"] = json.loads(item["itens_json"])

            return resultado

    @staticmethod
    def buscar_por_id(pre_venda_id: int) -> Optional[dict[str, Any]]:
        """Busca uma pré-venda pelo ID com todos os seus itens."""
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT
                    pv.id,
                    pv.numero_venda,
                    COALESCE(c.nome, 'Consumidor Final') AS cliente_nome,
                    u.nome AS usuario_nome,
                    pv.data_hora,
                    pv.valor_total,
                    pv.desconto_global,
                    pv.desconto_itens,
                    pv.desconto_total,
                    pv.observacao,
                    pv.itens_json
                FROM pre_vendas pv
                LEFT JOIN clientes c ON c.id = pv.cliente_id
                LEFT JOIN usuarios u ON u.id = pv.usuario_id
                WHERE pv.id = %s
                """,
                (pre_venda_id,),
            )
            resultado = cur.fetchone()

            if resultado and isinstance(resultado.get("itens_json"), str):
                resultado["itens_json"] = json.loads(resultado["itens_json"])

            return resultado

    @staticmethod
    def cancelar(pre_venda_id: int) -> bool:
        """Muda o status de PENDENTE para CANCELADA."""
        with db_cursor(dictionary=True) as cur:
            # Verifica se existe e está pendente
            cur.execute(
                "SELECT id FROM pre_vendas WHERE id = %s AND status = 'PENDENTE'",
                (pre_venda_id,),
            )
            if not cur.fetchone():
                return False

        with db_transaction(dictionary=True) as cur:
            cur.execute(
                "UPDATE pre_vendas SET status = 'CANCELADA' WHERE id = %s AND status = 'PENDENTE'",
                (pre_venda_id,),
            )
            return True

    @staticmethod
    def listar_usuarios() -> list[dict[str, Any]]:
        """Lista todos os usuários ativos."""
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, nome
                FROM usuarios
                WHERE ativo = 'S'
                ORDER BY nome
                """
            )
            return cur.fetchall()

    @staticmethod
    def listar_clientes() -> list[dict[str, Any]]:
        """Lista todos os clientes ativos (não-sistema)."""
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT id, nome, cpf
                FROM clientes
                WHERE ativo = 'S' AND cliente_sistema = 'N'
                ORDER BY nome
                """
            )
            return cur.fetchall()