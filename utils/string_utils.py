import re

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

def somente_digitos(valor: str) -> str:
    return "".join(char for char in valor if char.isdigit())

def texto_limpo(valor: str) -> str:
    return valor.strip()

def texto_maiusculo(valor: str) -> str:
    return texto_limpo(valor).upper()

def email_valido(email: str) -> bool:
    if not email:
        return True
    return bool(EMAIL_REGEX.match(email))