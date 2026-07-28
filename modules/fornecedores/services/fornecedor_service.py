from __future__ import annotations

from typing import Any

from modules.fornecedores.models.fornecedor_model import FornecedorModel
from modules.shared.constants import FLAG_NAO, FLAG_SIM, ResultadoOperacao, alternar_flag
from modules.shared.validators import validar_cnpj_cpf, validar_cep, validar_email, validar_estado, validar_telefone

class FornecedorService:
    @staticmethod
    def _validar_dados(dados: dict[str, Any]) -> ResultadoOperacao:
        nome = str(dados.get("nome_fantasia", "")).strip()

        if not nome:
            return False, "Nome Fantasia: preencha o nome principal do fornecedor."

        for validator in (
            lambda: validar_email(dados.get("email", "")),
            lambda: validar_cnpj_cpf(dados.get("cnpj_cpf", "")),
            lambda: validar_telefone(dados.get("telefone", "")),
            lambda: validar_estado(dados.get("estado", "")),
            lambda: validar_cep(dados.get("cep", "")),
        ):
            ok, msg = validator()
            if not ok:
                return False, msg

        return True, ""

    @staticmethod
    def cadastrar_fornecedor(dados: dict[str, Any]) -> ResultadoOperacao:
        valido, mensagem = FornecedorService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            fornecedor_id = FornecedorModel.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao salvar fornecedor:\n{exc}"

        if not fornecedor_id:
            return False, "Não foi possível cadastrar o fornecedor."

        return True, "Fornecedor cadastrado com sucesso!"

    @staticmethod
    def atualizar_fornecedor(fornecedor_id: int, dados: dict[str, Any]) -> ResultadoOperacao:
        valido, mensagem = FornecedorService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            atualizado = FornecedorModel.atualizar(int(fornecedor_id), dados)
        except Exception as exc:
            return False, f"Erro ao atualizar fornecedor:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o fornecedor."

        return True, "Fornecedor atualizado com sucesso!"

    @staticmethod
    def alternar_status(fornecedor_id: int) -> ResultadoOperacao:
        fornecedor = FornecedorModel.buscar_por_id(int(fornecedor_id))
        if not fornecedor:
            return False, "Fornecedor não encontrado."

        ativo_atual = str(fornecedor.get("ativo") or FLAG_NAO).strip().upper()
        novo_status = alternar_flag(ativo_atual)

        try:
            atualizado = FornecedorModel.atualizar_status(int(fornecedor_id), novo_status)
        except Exception as exc:
            return False, f"Erro ao atualizar status do fornecedor:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o status do fornecedor."

        acao = "ativado" if novo_status == FLAG_SIM else "desativado"
        return True, f"Fornecedor {acao} com sucesso!"
