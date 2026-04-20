import os
from mysql.connector import Error, pooling
from dotenv import load_dotenv

# Carrega o .env que está na raiz do projeto (cspdv/.env)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

_connection_pool = None

def get_connection_pool():
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name="cspdv_pool",
                pool_size=10,
                pool_reset_session=True,
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                charset='utf8mb4',
                autocommit=False
            )
        except Error as e:
            raise ConnectionError(f"Erro ao criar o pool de conexões: {e}")
    return _connection_pool


def get_connection():
    try:
        pool = get_connection_pool()
        return pool.get_connection()
    except Error as e:
        raise ConnectionError(f"Não foi possível obter conexão do pool: {e}")

def close_connection():
    pass

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