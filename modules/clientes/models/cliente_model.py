from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection


class ClienteModel:
    @staticmethod
    def buscar_para_venda(termo: str, limite: int = 20) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        termo_limpo = str(termo or "").strip()
        termo_nome = f"%{termo_limpo.upper()}%"
        termo_cpf = f"{termo_limpo}%"
        try:
            cursor.execute(
                """
                SELECT
                    id,
                    nome,
                    cpf,
                    telefone,
                    cidade,
                    estado,
                    ativo
                FROM clientes
                WHERE ativo = 'S'
                  AND (
                    UPPER(nome) LIKE %s
                    OR cpf LIKE %s
                  )
                ORDER BY
                    CASE
                        WHEN cpf = %s THEN 0
                        WHEN UPPER(nome) = UPPER(%s) THEN 1
                        ELSE 2
                    END,
                    nome
                LIMIT %s
                """,
                (termo_nome, termo_cpf, termo_limpo, termo_limpo, limite),
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_resumo() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id,
                    nome,
                    cpf,
                    telefone,
                    cidade,
                    estado,
                    ativo
                FROM clientes
                ORDER BY nome
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id(cliente_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id,
                    nome,
                    email,
                    telefone,
                    cpf,
                    logradouro,
                    numero,
                    bairro,
                    cep,
                    cidade,
                    estado,
                    observacao,
                    ativo
                FROM clientes
                WHERE id = %s
                LIMIT 1
                """,
                (cliente_id,),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def inserir(dados: Dict[str, Any]) -> Optional[int]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO clientes
                    (nome, email, telefone, cpf, logradouro, numero,
                     bairro, cep, cidade, estado, observacao, ativo)
                VALUES
                    (%(nome)s, %(email)s, %(telefone)s, %(cpf)s, %(logradouro)s, %(numero)s,
                     %(bairro)s, %(cep)s, %(cidade)s, %(estado)s, %(observacao)s, %(ativo)s)
                """,
                dados,
            )
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar(cliente_id: int, dados: Dict[str, Any]) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE clientes
                SET nome = %(nome)s,
                    email = %(email)s,
                    telefone = %(telefone)s,
                    cpf = %(cpf)s,
                    logradouro = %(logradouro)s,
                    numero = %(numero)s,
                    bairro = %(bairro)s,
                    cep = %(cep)s,
                    cidade = %(cidade)s,
                    estado = %(estado)s,
                    observacao = %(observacao)s,
                    ativo = %(ativo)s
                WHERE id = %(id)s
                """,
                {**dados, "id": cliente_id},
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_status(cliente_id: int, ativo: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE clientes SET ativo = %s WHERE id = %s",
                (ativo, cliente_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
