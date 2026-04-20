import bcrypt
from typing import Dict, Any
from database.connection import get_connection

class SetupModel:

    @staticmethod
    def is_first_run() -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM config_empresa")
            result = cursor.fetchone()
            
            if result:
                if isinstance(result, dict):
                    count = list(result.values())[0]
                else:
                    count = result[0]
                
                return count == 0
            return True
        finally:
            cursor.close()

    @staticmethod
    def salvar_tudo(empresa: Dict[str, Any], pdv: Dict[str, Any], admin: Dict[str, Any]) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 1. Empresa
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

            # 2. PDV principal
            cursor.execute(
                """
                INSERT INTO pdvs (identificacao, descricao, status, createdAt, updatedAt, ativo)
                VALUES (%(identificacao)s, %(descricao)s, 'ativo', NOW(), NOW(), 'S')
                """,
                pdv,
            )

            # 3. Cargo Administrador
            cursor.execute(
                "INSERT INTO cargos (nome_cargo, createdAt, updatedAt, ativo) "
                "VALUES ('Administrador', NOW(), NOW(), 'S')"
            )
            cargo_id = cursor.lastrowid

           # 4. Criar o Perfil 'Administrador Master'
            cursor.execute(
                """
                INSERT INTO perfis (nome, descricao, ativo, updateAt) 
                VALUES ('Admin Master', 'Acesso irrestrito a todos os módulos do sistema', 'S', NOW())
                """
            )
            perfil_id = cursor.lastrowid

            # 5. Definir as Permissões Base Iniciais
            permissoes_base = [
                ('sistema.master', 'Acesso Irrestrito (Master)'),
                ('vendas.pdv', 'Acesso ao PDV (Frente de Caixa)'),
                ('estoque.gerenciar', 'Cadastro e Edição de Produtos'),
                ('financeiro.total', 'Acesso Completo ao Módulo Financeiro'),
                ('relatorios.ver', 'Visualização de Relatórios e Dashboards'),
            ]

            permissoes_ids = []
            for chave, nome_amigavel in permissoes_base:
                cursor.execute(
                    "INSERT INTO permissoes (chave, nome_amigavel) VALUES (%s, %s)",
                    (chave, nome_amigavel)
                )
                permissoes_ids.append(cursor.lastrowid)

            # 6. Vincular todas as permissões criadas ao Perfil Master
            for perm_id in permissoes_ids:
                cursor.execute(
                    "INSERT INTO perfil_permissoes (perfil_id, permissao_id) VALUES (%s, %s)",
                    (perfil_id, perm_id)
                )

            # 7. Funcionário
            cursor.execute(
                """
                INSERT INTO funcionarios
                    (nome, cpf, cargo_id, createdAt, updatedAt, ativo, data_admissao)
                VALUES
                    (%(nome_completo)s, '00000000000', %(cargo_id)s, NOW(), NOW(), 'S', CURDATE())
                """,
                {**admin, 'cargo_id': cargo_id},
            )
            funcionario_id = cursor.lastrowid

            # 8. Usuário admin
            password_plain = admin['senha'].encode('utf-8')
            senha_hash = bcrypt.hashpw(password_plain, bcrypt.gensalt()).decode('utf-8')

            cursor.execute(
                """
                INSERT INTO usuarios
                    (funcionario_id, nome, email, senha, cargo, createdAt, updatedAt, ativo, perfil_acesso_id)
                VALUES
                    (%(funcionario_id)s, %(login)s, %(email)s, %(senha_hash)s,
                     'Administrador', NOW(), NOW(), 'S', %(perfil_id)s)
                """,
                {
                    'funcionario_id': funcionario_id,
                    'login': admin['login'],
                    'email': admin.get('email', ''),
                    'senha_hash': senha_hash,
                    'perfil_id': perfil_id  # <--- Vinculando o usuário ao perfil
                },
            )

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Erro na transação: {e}") # Log para debug
            raise
        finally:
            cursor.close()
