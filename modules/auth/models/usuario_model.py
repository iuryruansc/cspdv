import hashlib
import bcrypt
from typing import List, Optional, Dict, Any, cast
from database.connection import get_connection

class UsuarioModel:
    @staticmethod
    def _carregar_usuario_com_permissoes(usuario: Dict[str, Any]) -> Dict[str, Any]:
        perfil_id = usuario.get("perfil_acesso_id")
        usuario["permissoes"] = UsuarioModel.buscar_permissoes(int(perfil_id)) if perfil_id is not None else []
        usuario.pop("senha", None)
        return usuario

    @staticmethod
    def buscar_por_login(login: str) -> Optional[Dict[str, Any]]:
        conn = get_connection() # Erro que crasha a aplicação
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, funcionario_id, nome, email, senha, cargo, ativo, perfil_acesso_id
                FROM   usuarios
                WHERE  (LOWER(nome) = LOWER(%s) OR LOWER(email) = LOWER(%s))
                LIMIT  1
                """,
                (login, login),
            )
            return cast(Optional[Dict[str, Any]], cursor.fetchone())
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def verificar_senha(senha_digitada: str, senha_banco: str) -> bool:
        # ── bcrypt ──────────────────────────────────────────────────────
        if senha_banco.startswith(('$2b$', '$2a$', '$2y$')):
            try:
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
        usuario = UsuarioModel.buscar_por_login(login)

        if usuario is None:
            return None

        if not isinstance(usuario, dict):
            raise TypeError(f"Esperado dict, recebido {type(usuario)}")

        if not UsuarioModel.verificar_senha(senha, usuario['senha']):
            return None

        if usuario['ativo'] != 'S':
            raise ValueError('Conta inativa. Contate o administrador.')

        return UsuarioModel._carregar_usuario_com_permissoes(usuario)

    @staticmethod
    def buscar_sessao_por_id(usuario_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, funcionario_id, nome, email, cargo, ativo, perfil_acesso_id
                FROM usuarios
                WHERE id = %s
                LIMIT 1
                """,
                (usuario_id,),
            )
            usuario = cast(Optional[Dict[str, Any]], cursor.fetchone())
            if usuario is None or usuario.get("ativo") != "S":
                return None
            return UsuarioModel._carregar_usuario_com_permissoes(usuario)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def autenticar_admin_por_senha(senha: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT DISTINCT
                    u.id,
                    u.funcionario_id,
                    u.nome,
                    u.email,
                    u.senha,
                    u.cargo,
                    u.ativo,
                    u.perfil_acesso_id
                FROM usuarios u
                INNER JOIN perfil_permissoes pp ON pp.perfil_id = u.perfil_acesso_id
                INNER JOIN permissoes p ON p.id = pp.permissao_id
                WHERE u.ativo = 'S'
                  AND p.chave = 'sistema.master'
                """
            )
            usuarios = cast(List[Dict[str, Any]], cursor.fetchall())
            for usuario in usuarios:
                senha_banco = str(usuario.get("senha") or "")
                if senha_banco and UsuarioModel.verificar_senha(senha, senha_banco):
                    return UsuarioModel._carregar_usuario_com_permissoes(usuario)
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_permissoes(perfil_id: int) -> list:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT p.chave
                FROM permissoes p
                INNER JOIN perfil_permissoes pp ON pp.permissao_id = p.id
                WHERE pp.perfil_id = %s
            """
            cursor.execute(sql, (perfil_id,))
            resultados = cast(List[Dict[str, Any]], cursor.fetchall())
            return [row['chave'] for row in resultados]
        finally:
            cursor.close()
            conn.close()
