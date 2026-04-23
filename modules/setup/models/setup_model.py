import bcrypt
from typing import Any, Dict

from database.connection import get_connection


class SetupModel:
    _FORMAS_PAGAMENTO_PADRAO = [
        {"nome": "Dinheiro", "tipo_sefaz": "01", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
        {"nome": "PIX", "tipo_sefaz": "17", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
        {"nome": "Cartao Debito", "tipo_sefaz": "04", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
        {"nome": "Cartao Credito", "tipo_sefaz": "03", "permite_parcelamento": "S", "taxa_administrativa": 0.00},
        {"nome": "Vale Refeicao", "tipo_sefaz": "10", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
        {"nome": "Cheque", "tipo_sefaz": "02", "permite_parcelamento": "N", "taxa_administrativa": 0.00},
    ]

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

            cursor.execute(
                "INSERT INTO cargos (nome_cargo, createdAt, updatedAt, ativo) "
                "VALUES ('Administrador', NOW(), NOW(), 'S')"
            )
            cargo_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO perfis (nome, descricao, ativo, updateAt)
                VALUES ('Admin Master', 'Acesso irrestrito a todos os modulos do sistema', 'S', NOW())
                """
            )
            perfil_id = cursor.lastrowid

            permissoes_base = [
                ("sistema.master", "Acesso Irrestrito (Master)"),
                ("vendas.pdv", "Acesso ao PDV (Frente de Caixa)"),
                ("estoque.gerenciar", "Cadastro e Edicao de Produtos"),
                ("financeiro.total", "Acesso Completo ao Modulo Financeiro"),
                ("relatorios.ver", "Visualizacao de Relatorios e Dashboards"),
            ]

            permissoes_ids = []
            for chave, nome_amigavel in permissoes_base:
                cursor.execute(
                    "INSERT INTO permissoes (chave, nome_amigavel) VALUES (%s, %s)",
                    (chave, nome_amigavel),
                )
                permissoes_ids.append(cursor.lastrowid)

            for perm_id in permissoes_ids:
                cursor.execute(
                    "INSERT INTO perfil_permissoes (perfil_id, permissao_id) VALUES (%s, %s)",
                    (perfil_id, perm_id),
                )

            SetupModel._criar_formas_pagamento_padrao(cursor)

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

    @staticmethod
    def _criar_formas_pagamento_padrao(cursor) -> None:
        cursor.execute("SHOW COLUMNS FROM formas_pagamento")
        colunas = {str(coluna[0]) for coluna in cursor.fetchall()}

        for forma in SetupModel._FORMAS_PAGAMENTO_PADRAO:
            cursor.execute(
                "SELECT id FROM formas_pagamento WHERE UPPER(nome) = UPPER(%s) LIMIT 1",
                (forma["nome"],),
            )
            if cursor.fetchone():
                continue

            campos = ["nome", "tipo_sefaz", "permite_parcelamento", "taxa_administrativa", "ativo"]
            valores = ["%s", "%s", "%s", "%s", "'S'"]
            parametros = [
                forma["nome"],
                forma["tipo_sefaz"],
                forma["permite_parcelamento"],
                forma["taxa_administrativa"],
            ]

            if "createdAt" in colunas:
                campos.append("createdAt")
                valores.append("NOW()")
            if "updatedAt" in colunas:
                campos.append("updatedAt")
                valores.append("NOW()")

            cursor.execute(
                f"""
                INSERT INTO formas_pagamento ({", ".join(campos)})
                VALUES ({", ".join(valores)})
                """,
                tuple(parametros),
            )
