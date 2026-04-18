import hashlib
from typing import Optional, Dict, Any, cast
from database.connection import get_connection

class UsuarioModel:

    @staticmethod
    def buscar_por_login(login: str) -> Optional[Dict[str, Any]]:
        conn = get_connection() # Erro que crasha a aplicação
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, nome, email, senha, cargo, ativo, perfil_acesso_id
                FROM   usuarios
                WHERE  (nome = %s OR email = %s)
                LIMIT  1
                """,
                (login, login),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()

    @staticmethod
    def verificar_senha(senha_digitada: str, senha_banco: str) -> bool:
        # ── bcrypt ──────────────────────────────────────────────────────
        if senha_banco.startswith(('$2b$', '$2a$', '$2y$')):
            try:
                import bcrypt
                return bcrypt.checkpw(
                    senha_digitada.encode('utf-8'),
                    senha_banco.encode('utf-8'),
                )
            except ImportError:
                raise ImportError(
                    "O banco usa bcrypt mas o pacote não está instalado.\n"
                    "Execute:  pip install bcrypt"
                )

        # ── SHA-256 hex ─────────────────────────────────────────────────
        if len(senha_banco) == 64:
            return (
                hashlib.sha256(senha_digitada.encode('utf-8')).hexdigest()
                == senha_banco
            )

        # ── Texto puro (apenas dev) ─────────────────────────────────────
        return senha_digitada == senha_banco

    @staticmethod
    def autenticar(login: str, senha: str) -> Optional[Dict[str, Any]]:
        print(f"Autenticando usuário: {login}")
        usuario = UsuarioModel.buscar_por_login(login)

        if usuario is None:
            return None

        if not isinstance(usuario, dict):
            raise TypeError(f"Esperado dict, recebido {type(usuario)}")

        if not UsuarioModel.verificar_senha(senha, usuario['senha']):
            return None

        if usuario['ativo'] != 'S':
            raise ValueError('Conta inativa. Contate o administrador.')

        return usuario