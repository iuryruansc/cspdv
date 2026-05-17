from __future__ import annotations

from typing import Any, Mapping, Sequence, cast

from database.seeds.runner import SeedCursorLike

VERSION = "20260517_003"
DESCRIPTION = "Carga cliente padrao Consumidor Final"

CONSUMIDOR_FINAL = {
    "nome": "Consumidor Final",
    "email": None,
    "telefone": "",
    "cpf": None,
    "logradouro": "",
    "numero": None,
    "bairro": "",
    "cep": "",
    "cidade": "",
    "estado": "",
    "observacao": "Registro padrao do sistema para vendas sem identificacao nominal.",
    "cliente_sistema": "S",
    "ativo": "S",
}

def _rows(cursor: SeedCursorLike) -> Sequence[Sequence[Any] | Mapping[str, Any]]:
    return cast(Sequence[Sequence[Any] | Mapping[str, Any]], cursor.fetchall())

def apply(cursor: SeedCursorLike) -> None:
    cursor.execute(
        """
        SELECT 1
        FROM clientes
        WHERE UPPER(TRIM(nome)) = UPPER(TRIM(%s))
        LIMIT 1
        """,
        (CONSUMIDOR_FINAL["nome"],),
    )
    if _rows(cursor):
        return

    cursor.execute(
        """
        INSERT INTO clientes
            (nome, email, telefone, cpf, logradouro, numero,
             bairro, cep, cidade, estado, observacao, cliente_sistema, ativo)
        VALUES
            (%(nome)s, %(email)s, %(telefone)s, %(cpf)s, %(logradouro)s, %(numero)s,
             %(bairro)s, %(cep)s, %(cidade)s, %(estado)s, %(observacao)s, %(cliente_sistema)s, %(ativo)s)
        """,
        CONSUMIDOR_FINAL,
    )
