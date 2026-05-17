from typing import Any, Dict, List, Optional, cast

from database.connection import get_connection


class FormaPagamentoModel:
    @staticmethod
    def _colunas_tabela() -> set[str]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SHOW COLUMNS FROM formas_pagamento")
            return {str(coluna[0]) for coluna in cursor.fetchall()}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id,
                    nome,
                    tipo_sefaz,
                    permite_parcelamento,
                    taxa_administrativa,
                    ativo
                FROM formas_pagamento
                ORDER BY nome
                """
            )
            return cast(List[Dict[str, Any]], cursor.fetchall())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_id(forma_pagamento_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id,
                    nome,
                    tipo_sefaz,
                    permite_parcelamento,
                    taxa_administrativa,
                    ativo
                FROM formas_pagamento
                WHERE id = %s
                LIMIT 1
                """,
                (int(forma_pagamento_id),),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_nome(nome: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome, tipo_sefaz, permite_parcelamento, taxa_administrativa, ativo
                FROM formas_pagamento
                WHERE UPPER(TRIM(nome)) = UPPER(TRIM(%s))
                LIMIT 1
                """,
                (nome,),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def inserir(dados: Dict[str, Any]) -> Optional[int]:
        colunas = FormaPagamentoModel._colunas_tabela()
        conn = get_connection()
        cursor = conn.cursor()
        try:
            campos = ["nome", "tipo_sefaz", "permite_parcelamento", "taxa_administrativa", "ativo"]
            valores = ["%(nome)s", "%(tipo_sefaz)s", "%(permite_parcelamento)s", "%(taxa_administrativa)s", "%(ativo)s"]
            if "createdAt" in colunas:
                campos.append("createdAt")
                valores.append("NOW()")
            if "updatedAt" in colunas:
                campos.append("updatedAt")
                valores.append("NOW()")

            cursor.execute(
                f"""
                INSERT INTO formas_pagamento
                    ({", ".join(campos)})
                VALUES
                    ({", ".join(valores)})
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
    def atualizar(forma_pagamento_id: int, dados: Dict[str, Any]) -> bool:
        colunas = FormaPagamentoModel._colunas_tabela()
        conn = get_connection()
        cursor = conn.cursor()
        try:
            atualizacao_updated_at = ", updatedAt = NOW()" if "updatedAt" in colunas else ""
            cursor.execute(
                f"""
                UPDATE formas_pagamento
                SET
                    nome = %(nome)s,
                    tipo_sefaz = %(tipo_sefaz)s,
                    permite_parcelamento = %(permite_parcelamento)s,
                    taxa_administrativa = %(taxa_administrativa)s,
                    ativo = %(ativo)s
                    {atualizacao_updated_at}
                WHERE id = %(id)s
                """,
                {**dados, "id": int(forma_pagamento_id)},
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
    def atualizar_status(forma_pagamento_id: int, ativo: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE formas_pagamento SET ativo = %s WHERE id = %s",
                (ativo, int(forma_pagamento_id)),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
