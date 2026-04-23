from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection

class CaixaModel:
    @staticmethod
    def listar_pdvs_ativos() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, identificacao, descricao
                FROM pdvs
                WHERE ativo = 'S' AND status = 'ativo'
                ORDER BY identificacao
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_caixa_aberto_por_pdv(pdv_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, pdv_id, usuario_abertura_id, data_abertura, valor_abertura, status
                FROM caixas
                WHERE pdv_id = %s AND status = 'aberto' AND ativo = 'S'
                ORDER BY data_abertura DESC
                LIMIT 1
                """,
                (pdv_id,),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_caixa_aberto_por_usuario(usuario_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    c.id,
                    c.pdv_id,
                    c.usuario_abertura_id,
                    c.data_abertura,
                    c.valor_abertura,
                    c.status,
                    p.identificacao,
                    p.descricao,
                    u.nome AS usuario_nome
                FROM caixas c
                INNER JOIN pdvs p ON p.id = c.pdv_id
                INNER JOIN usuarios u ON u.id = c.usuario_abertura_id
                WHERE c.usuario_abertura_id = %s
                  AND c.status = 'aberto'
                  AND c.ativo = 'S'
                ORDER BY c.data_abertura DESC
                LIMIT 1
                """,
                (usuario_id,),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def abrir_caixa(
        pdv_id: int,
        usuario_id: int,
        valor_abertura: float,
    ) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO caixas
                    (pdv_id, usuario_abertura_id, data_abertura, valor_abertura,
                     status, usuario_fechamento_id, ativo, createdAt, updatedAt)
                VALUES
                    (%s, %s, NOW(), %s, 'aberto', %s, 'S', NOW(), NOW())
                """,
                (pdv_id, usuario_id, valor_abertura, usuario_id),
            )
            conn.commit()
            lastrowid = cursor.lastrowid
            if lastrowid is None:
                raise RuntimeError("Nao foi possivel obter o ID da abertura de caixa criada.")
            return int(lastrowid)
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_ultimas_aberturas(limit: int = 10) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    DATE_FORMAT(c.data_abertura, '%d/%m %H:%i') AS data_abertura_fmt,
                    u.nome AS operador,
                    c.valor_abertura
                FROM caixas c
                INNER JOIN usuarios u ON u.id = c.usuario_abertura_id
                ORDER BY c.data_abertura DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def fechar_caixa(
        caixa_id: int,
        usuario_fechamento_id: int,
        valor_fechamento: float,
        diferenca: float,
        observacoes: str,
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SHOW COLUMNS FROM caixas")
            colunas = {str(coluna[0]) for coluna in cursor.fetchall()}

            atribuicoes = ["status = 'fechado'"]
            parametros: List[Any] = []

            if "usuario_fechamento_id" in colunas:
                atribuicoes.append("usuario_fechamento_id = %s")
                parametros.append(usuario_fechamento_id)
            if "data_fechamento" in colunas:
                atribuicoes.append("data_fechamento = NOW()")
            if "valor_fechamento" in colunas:
                atribuicoes.append("valor_fechamento = %s")
                parametros.append(valor_fechamento)
            if "valor_contado" in colunas:
                atribuicoes.append("valor_contado = %s")
                parametros.append(valor_fechamento)
            if "diferenca_fechamento" in colunas:
                atribuicoes.append("diferenca_fechamento = %s")
                parametros.append(diferenca)
            if "diferenca" in colunas:
                atribuicoes.append("diferenca = %s")
                parametros.append(diferenca)
            if "observacoes_fechamento" in colunas:
                atribuicoes.append("observacoes_fechamento = %s")
                parametros.append(observacoes or "")
            if "observacao_fechamento" in colunas:
                atribuicoes.append("observacao_fechamento = %s")
                parametros.append(observacoes or "")
            if "updatedAt" in colunas:
                atribuicoes.append("updatedAt = NOW()")

            parametros.append(caixa_id)
            cursor.execute(
                f"""
                UPDATE caixas
                SET {", ".join(atribuicoes)}
                WHERE id = %s
                """,
                tuple(parametros),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
