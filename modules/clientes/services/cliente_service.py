from __future__ import annotations

from typing import Any

from modules.clientes.models.cliente_model import ClienteModel
from modules.shared.constants import ResultadoOperacao, alternar_flag, flag_ativa
from modules.shared.validators import validar_cep, validar_cpf, validar_email, validar_estado, validar_telefone
from utils.app_logger import log_error

class ClienteService:
    @staticmethod
    def _cliente_eh_sistema(cliente: dict[str, Any]) -> bool:
        return flag_ativa((cliente or {}).get("cliente_sistema"))

    @staticmethod
    def obter_consumidor_final() -> dict[str, Any] | None:
        try:
            return ClienteModel.buscar_consumidor_final()
        except Exception as exc:
            log_error("Erro ao obter cliente padrao Consumidor Final.", exc)
            return None

    @staticmethod
    def buscar_para_venda(termo: str) -> list[dict[str, Any]]:
        termo_limpo = str(termo or "").strip()
        if len(termo_limpo) < 2:
            return []
        try:
            return ClienteModel.buscar_para_venda(termo_limpo)
        except Exception as exc:
            log_error("Erro ao buscar cliente para venda.", exc)
            return []

    @staticmethod
    def _validar_dados(dados: dict[str, Any]) -> ResultadoOperacao:
        nome = str(dados.get("nome", "")).strip()

        if not nome:
            return False, "Nome: preencha o nome principal do cliente."

        for validator in (
            lambda: validar_email(dados.get("email", "")),
            lambda: validar_cpf(dados.get("cpf", "")),
            lambda: validar_telefone(dados.get("telefone", "")),
            lambda: validar_estado(dados.get("estado", "")),
            lambda: validar_cep(dados.get("cep", "")),
        ):
            ok, msg = validator()
            if not ok:
                return False, msg

        return True, ""

    @staticmethod
    def cadastrar_cliente(dados: dict[str, Any]) -> ResultadoOperacao:
        valido, mensagem = ClienteService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            cliente_id = ClienteModel.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao salvar cliente:\n{exc}"

        if not cliente_id:
            return False, "Nao foi possivel cadastrar o cliente."

        return True, "Cliente cadastrado com sucesso!"

    @staticmethod
    def atualizar_cliente(cliente_id: int, dados: dict[str, Any]) -> ResultadoOperacao:
        valido, mensagem = ClienteService._validar_dados(dados)
        if not valido:
            return False, mensagem

        cliente = ClienteModel.buscar_por_id(int(cliente_id))
        if not cliente:
            return False, "Cliente nao encontrado."
        if ClienteService._cliente_eh_sistema(cliente):
            return False, "O cliente Consumidor Final e um registro do sistema e nao pode ser editado."

        try:
            atualizado = ClienteModel.atualizar(int(cliente_id), dados)
        except Exception as exc:
            return False, f"Erro ao atualizar cliente:\n{exc}"

        if not atualizado:
            return False, "Nao foi possivel atualizar o cliente."

        return True, "Cliente atualizado com sucesso!"

    @staticmethod
    def alternar_status(cliente_id: int) -> ResultadoOperacao:
        cliente = ClienteModel.buscar_por_id(int(cliente_id))
        if not cliente:
            return False, "Cliente nao encontrado."
        if ClienteService._cliente_eh_sistema(cliente):
            return False, "O cliente Consumidor Final e um registro do sistema e nao pode ser desativado."

        novo_status = alternar_flag(cliente.get("ativo"))

        try:
            atualizado = ClienteModel.atualizar_status(int(cliente_id), novo_status)
        except Exception as exc:
            return False, f"Erro ao atualizar status do cliente:\n{exc}"

        if not atualizado:
            return False, "Nao foi possivel atualizar o status do cliente."

        acao = "ativado" if flag_ativa(novo_status) else "desativado"
        return True, f"Cliente {acao} com sucesso!"
