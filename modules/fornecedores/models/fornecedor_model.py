from typing import Optional, Dict, Any, List, cast
from database.connection import get_connection

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
            print(f"Erro ao listar fornecedores: {e}")
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
            print(f"Erro ao inserir fornecedor: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
