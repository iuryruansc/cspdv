from typing import Any, Callable, Dict, Optional, Tuple

ResultadoOperacao = Tuple[bool, str]

def validar_entidade_simples(
    dados: Dict[str, Any],
    *,
    nome_campo: str,
    entidade: str,
) -> ResultadoOperacao:
    nome = str(dados.get(nome_campo, "")).strip()
    ativo = str(dados.get("ativo", "")).strip().upper()

    if len(nome) < 2:
        return False, f"O nome da {entidade} deve ter pelo menos 2 caracteres."

    if ativo not in {"S", "N"}:
        return False, f"O status da {entidade} é obrigatório."

    return True, ""

def cadastrar_entidade_simples(
    dados: Dict[str, Any],
    *,
    nome_campo: str,
    entidade: str,
    inserir_fn: Callable[[Dict[str, Any]], Optional[int]],
) -> ResultadoOperacao:
    valido, mensagem = validar_entidade_simples(
        dados,
        nome_campo=nome_campo,
        entidade=entidade,
    )
    if not valido:
        return False, mensagem

    try:
        registro_id = inserir_fn(dados)
    except Exception as exc:
        return False, f"Erro ao salvar {entidade}:\n{exc}"

    if not registro_id:
        return False, f"Não foi possível cadastrar a {entidade}."

    return True, f"{entidade.capitalize()} cadastrada com sucesso!"

def atualizar_entidade_simples(
    record_id: int,
    dados: Dict[str, Any],
    *,
    nome_campo: str,
    entidade: str,
    atualizar_fn: Callable[[int, Dict[str, Any]], bool],
) -> ResultadoOperacao:
    valido, mensagem = validar_entidade_simples(
        dados,
        nome_campo=nome_campo,
        entidade=entidade,
    )
    if not valido:
        return False, mensagem

    try:
        atualizado = atualizar_fn(int(record_id), dados)
    except Exception as exc:
        return False, f"Erro ao atualizar {entidade}:\n{exc}"

    if not atualizado:
        return False, f"Não foi possível atualizar a {entidade}."

    return True, f"{entidade.capitalize()} atualizada com sucesso!"

def alternar_status_entidade_simples(
    record_id: int,
    *,
    entidade: str,
    buscar_fn: Callable[[int], Optional[Dict[str, Any]]],
    atualizar_status_fn: Callable[[int, str], bool],
) -> ResultadoOperacao:
    registro = buscar_fn(int(record_id))
    if not registro:
        return False, f"{entidade.capitalize()} não encontrada."

    ativo_atual = str(registro.get("ativo") or "N").strip().upper()
    novo_status = "N" if ativo_atual == "S" else "S"

    try:
        atualizado = atualizar_status_fn(int(record_id), novo_status)
    except Exception as exc:
        return False, f"Erro ao atualizar status da {entidade}:\n{exc}"

    if not atualizado:
        return False, f"Não foi possível atualizar o status da {entidade}."

    acao = "ativada" if novo_status == "S" else "desativada"
    return True, f"{entidade.capitalize()} {acao} com sucesso!"
