"""Shared field validation helpers."""

from __future__ import annotations

def validar_email(email: str | None) -> tuple[bool, str]:
    if email and "@" not in email:
        return False, "E-mail: informe um endereco valido."
    return True, ""

def validar_telefone(telefone: str | None) -> tuple[bool, str]:
    if telefone and len(telefone) not in (10, 11):
        return False, "Telefone: informe DDD e numero completos."
    return True, ""

def validar_estado(estado: str | None) -> tuple[bool, str]:
    if estado and len(estado) != 2:
        return False, "Estado: use a sigla da UF com 2 letras."
    return True, ""

def validar_cep(cep: str | None) -> tuple[bool, str]:
    if cep and len(cep) != 8:
        return False, "CEP: informe os 8 digitos do CEP."
    return True, ""

def validar_cpf(cpf: str | None) -> tuple[bool, str]:
    if cpf and len(cpf) != 11:
        return False, "CPF: informe os 11 digitos."
    return True, ""

def validar_cnpj_cpf(valor: str | None) -> tuple[bool, str]:
    if valor and len(valor) not in (11, 14):
        return False, "CPF/CNPJ: use 11 digitos para CPF ou 14 para CNPJ."
    return True, ""
