from utils.string_utils import somente_digitos, texto_limpo

def formatar_cpf_cnpj(valor: str) -> str:
    digits = somente_digitos(valor)
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    if len(digits) == 14:
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    return digits

def formatar_telefone(valor: str) -> str:
    digits = somente_digitos(valor)
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    return texto_limpo(valor)

def formatar_cep(valor: str) -> str:
    digits = somente_digitos(valor)
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return digits