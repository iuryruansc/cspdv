from typing import Optional, Dict, Any, List, cast
from database.connection import get_connection
from utils.app_logger import log_error

class FornecedorModel:
    @staticmethod
    def listar_resumo() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id_fornecedor,
                    nome_fantasia,
                    cnpj_cpf,
                    telefone,
                    cidade,
                    estado,
                    ativo
                FROM fornecedores
                ORDER BY nome_fantasia
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        except Exception as e:
            log_error("Erro ao listar fornecedores.", e)
            raise
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
                INSERT INTO fornecedores
                    (nome_fantasia, razao_social, cnpj_cpf, ie,
                     telefone, email, logradouro, numero,
                     cep, cidade, estado, bairro, ativo, observacao)
                VALUES
                    (%(nome_fantasia)s, %(razao_social)s, %(cnpj_cpf)s, %(ie)s,
                     %(telefone)s, %(email)s, %(logradouro)s, %(numero)s,
                     %(cep)s, %(cidade)s, %(estado)s, %(bairro)s, %(ativo)s, %(observacao)s)
                """,
                dados,
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            log_error("Erro ao inserir fornecedor.", e)
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id(fornecedor_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id_fornecedor,
                    nome_fantasia,
                    razao_social,
                    cnpj_cpf,
                    ie,
                    telefone,
                    email,
                    logradouro,
                    numero,
                    cep,
                    cidade,
                    estado,
                    bairro,
                    ativo,
                    observacao
                FROM fornecedores
                WHERE id_fornecedor = %s
                LIMIT 1
                """,
                (fornecedor_id,),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar(fornecedor_id: int, dados: Dict[str, Any]) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE fornecedores
                SET nome_fantasia = %(nome_fantasia)s,
                    razao_social = %(razao_social)s,
                    cnpj_cpf = %(cnpj_cpf)s,
                    ie = %(ie)s,
                    telefone = %(telefone)s,
                    email = %(email)s,
                    logradouro = %(logradouro)s,
                    numero = %(numero)s,
                    cep = %(cep)s,
                    cidade = %(cidade)s,
                    estado = %(estado)s,
                    bairro = %(bairro)s,
                    ativo = %(ativo)s,
                    observacao = %(observacao)s
                WHERE id_fornecedor = %(id_fornecedor)s
                """,
                {**dados, "id_fornecedor": fornecedor_id},
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            log_error("Erro ao atualizar fornecedor.", e)
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def atualizar_status(fornecedor_id: int, ativo: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE fornecedores SET ativo = %s WHERE id_fornecedor = %s",
                (ativo, fornecedor_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            log_error("Erro ao atualizar status do fornecedor.", e)
            raise
        finally:
            cursor.close()
            conn.close()
