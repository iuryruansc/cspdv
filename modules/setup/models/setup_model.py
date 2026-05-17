import bcrypt
from typing import Any, Dict

from database.connection import get_connection

class SetupModel:
    @staticmethod
    def _scalar_value(row: Any) -> Any | None:
        if not row:
            return None
        if isinstance(row, dict):
            return next(iter(row.values()), None)
        return row[0]

    @staticmethod
    def _buscar_id_por_nome(cursor: Any, tabela: str, coluna: str, valor: str) -> int:
        cursor.execute(
            f"SELECT id FROM {tabela} WHERE UPPER(TRIM({coluna})) = UPPER(TRIM(%s)) LIMIT 1",
            (valor,),
        )
        row = cursor.fetchone()
        id_encontrado = SetupModel._scalar_value(row)
        if id_encontrado is None:
            raise RuntimeError(
                f"Dado base nao encontrado em {tabela}: {valor}. "
                "Execute os seeds do sistema antes de continuar o setup."
            )
        return int(id_encontrado)

    @staticmethod
    def is_first_run() -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM config_empresa")
            result = cursor.fetchone()
            if not result:
                return True

            if isinstance(result, dict):
                count = list(result.values())[0]
            else:
                count = result[0]
            return count == 0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def salvar_tudo(empresa: Dict[str, Any], pdv: Dict[str, Any], admin: Dict[str, Any]) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO config_empresa
                    (razao_social, nome_fantasia, cnpj, inscricao_estadual,
                     email, telefone, logradouro, numero, bairro,
                     cidade, estado, cep, regime_tributario)
                VALUES
                    (%(razao_social)s, %(nome_fantasia)s, %(cnpj)s, %(inscricao_estadual)s,
                     %(email)s, %(telefone)s, %(logradouro)s, %(numero)s, %(bairro)s,
                     %(cidade)s, %(estado)s, %(cep)s, %(regime_tributario)s)
                """,
                empresa,
            )

            cursor.execute(
                """
                INSERT INTO pdvs (identificacao, descricao, status, createdAt, updatedAt, ativo)
                VALUES (%(identificacao)s, %(descricao)s, 'ativo', NOW(), NOW(), 'S')
                """,
                pdv,
            )

            cargo_id = SetupModel._buscar_id_por_nome(cursor, "cargos", "nome_cargo", "Administrador")
            perfil_id = SetupModel._buscar_id_por_nome(cursor, "perfis", "nome", "Admin Master")

            cursor.execute(
                """
                INSERT INTO funcionarios
                    (nome, cpf, cargo_id, createdAt, updatedAt, ativo, data_admissao)
                VALUES
                    (%(nome_completo)s, '00000000000', %(cargo_id)s, NOW(), NOW(), 'S', CURDATE())
                """,
                {**admin, "cargo_id": cargo_id},
            )
            funcionario_id = cursor.lastrowid

            senha_hash = bcrypt.hashpw(admin["senha"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute(
                """
                INSERT INTO usuarios
                    (funcionario_id, nome, email, senha, cargo, createdAt, updatedAt, ativo, perfil_acesso_id)
                VALUES
                    (%(funcionario_id)s, %(login)s, %(email)s, %(senha_hash)s,
                     'Administrador', NOW(), NOW(), 'S', %(perfil_id)s)
                """,
                {
                    "funcionario_id": funcionario_id,
                    "login": admin["login"],
                    "email": admin.get("email", ""),
                    "senha_hash": senha_hash,
                    "perfil_id": perfil_id,
                },
            )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
