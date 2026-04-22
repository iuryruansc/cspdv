from typing import Optional, Dict, Any, cast
from database.connection import get_connection

class FornecedorModel:
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
