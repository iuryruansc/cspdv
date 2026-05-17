from typing import Any, Dict, Tuple

from modules.formas_pagamento.models.forma_pagamento_model import FormaPagamentoModel

ResultadoOperacao = Tuple[bool, str]


class FormaPagamentoService:
    @staticmethod
    def _normalizar_dados(dados: Dict[str, Any]) -> Dict[str, Any]:
        nome = str(dados.get("nome") or "").strip()
        tipo_sefaz = str(dados.get("tipo_sefaz") or "").strip()
        permite_parcelamento = "S" if str(dados.get("permite_parcelamento") or "N").strip().upper() == "S" else "N"
        ativo = "S" if str(dados.get("ativo") or "N").strip().upper() == "S" else "N"
        try:
            taxa = float(dados.get("taxa_administrativa") or 0.0)
        except (TypeError, ValueError):
            taxa = -1.0

        return {
            "nome": nome,
            "tipo_sefaz": tipo_sefaz,
            "permite_parcelamento": permite_parcelamento,
            "taxa_administrativa": taxa,
            "ativo": ativo,
        }

    @staticmethod
    def _validar_dados(dados: Dict[str, Any], *, forma_pagamento_id: int | None = None) -> ResultadoOperacao:
        normalizados = FormaPagamentoService._normalizar_dados(dados)

        if len(normalizados["nome"]) < 2:
            return False, "O nome da forma de pagamento deve ter pelo menos 2 caracteres."
        if not normalizados["tipo_sefaz"]:
            return False, "O tipo SEFAZ da forma de pagamento é obrigatório."
        if len(normalizados["tipo_sefaz"]) > 2:
            return False, "O tipo SEFAZ deve ter no máximo 2 caracteres."
        if normalizados["ativo"] not in {"S", "N"}:
            return False, "O status da forma de pagamento é obrigatório."
        if normalizados["taxa_administrativa"] < 0:
            return False, "A taxa administrativa da forma de pagamento deve ser maior ou igual a zero."

        existente = FormaPagamentoModel.buscar_por_nome(normalizados["nome"])
        if existente and int(existente.get("id") or 0) != int(forma_pagamento_id or 0):
            return False, "Já existe uma forma de pagamento cadastrada com este nome."

        return True, ""

    @staticmethod
    def cadastrar_forma_pagamento(dados: Dict[str, Any]) -> ResultadoOperacao:
        normalizados = FormaPagamentoService._normalizar_dados(dados)
        valido, mensagem = FormaPagamentoService._validar_dados(normalizados)
        if not valido:
            return False, mensagem

        try:
            registro_id = FormaPagamentoModel.inserir(normalizados)
        except Exception as exc:
            return False, f"Erro ao salvar forma de pagamento:\n{exc}"

        if not registro_id:
            return False, "Não foi possível cadastrar a forma de pagamento."
        return True, "Forma de pagamento cadastrada com sucesso!"

    @staticmethod
    def atualizar_forma_pagamento(forma_pagamento_id: int, dados: Dict[str, Any]) -> ResultadoOperacao:
        normalizados = FormaPagamentoService._normalizar_dados(dados)
        valido, mensagem = FormaPagamentoService._validar_dados(normalizados, forma_pagamento_id=int(forma_pagamento_id))
        if not valido:
            return False, mensagem

        try:
            atualizado = FormaPagamentoModel.atualizar(int(forma_pagamento_id), normalizados)
        except Exception as exc:
            return False, f"Erro ao atualizar forma de pagamento:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar a forma de pagamento."
        return True, "Forma de pagamento atualizada com sucesso!"

    @staticmethod
    def alternar_status(forma_pagamento_id: int) -> ResultadoOperacao:
        registro = FormaPagamentoModel.buscar_por_id(int(forma_pagamento_id))
        if not registro:
            return False, "Forma de pagamento não encontrada."

        ativo_atual = str(registro.get("ativo") or "N").strip().upper()
        novo_status = "N" if ativo_atual == "S" else "S"
        try:
            atualizado = FormaPagamentoModel.atualizar_status(int(forma_pagamento_id), novo_status)
        except Exception as exc:
            return False, f"Erro ao atualizar status da forma de pagamento:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o status da forma de pagamento."
        acao = "ativada" if novo_status == "S" else "desativada"
        return True, f"Forma de pagamento {acao} com sucesso!"
