import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Carrega o .env que está na raiz do projeto (cspdv/.env)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

_connection = None

def get_connection():
    global _connection

    # Reconecta se a conexão não existe ou foi perdida
    if _connection is None or not _connection.is_connected():
        try:
            _connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                charset='utf8mb4',
                use_unicode=True,
                autocommit=False,
                connection_timeout=10,
                use_pure=True
            )
        except Error as e:
            raise ConnectionError(
                f"Não foi possível conectar ao banco de dados.\n"
                f"Verifique as credenciais no arquivo .env\n"
                f"Erro original: {e}"
            )
    return _connection


def close_connection():
    global _connection
    if _connection and _connection.is_connected():
        _connection.close()
        _connection = None


# Teste rápido: # python database/connection.py
if __name__ == '__main__':
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tabelas = cursor.fetchall()
            
        print(f"✓ Conectado ao banco '{os.getenv('DB_NAME')}' em {os.getenv('DB_HOST')}")
        print(f"  Tabelas encontradas ({len(tabelas)}):")
        for (nome,) in tabelas:
            print(f"    - {nome}")
            
    except ConnectionError as e:
        print(f"✗ Erro de Conexão: {e}")
    except Error as e:
        print(f"✗ Erro no banco de dados: {e}")
    finally:
        close_connection()