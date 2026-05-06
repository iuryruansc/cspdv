from modules.clientes.models.cliente_model import ClienteModel


class ClienteService:
    @staticmethod
    def buscar_para_venda(termo):
        termo_limpo = str(termo or "").strip()
        if len(termo_limpo) < 2:
            return []
        try:
            return ClienteModel.buscar_para_venda(termo_limpo)
        except Exception as exc:
            print(f"Erro ao buscar cliente para venda: {exc}")
            return []

    @staticmethod
    def _validar_dados(dados):
        nome = str(dados.get("nome", "")).strip()
        email = str(dados.get("email", "")).strip()
        cpf = str(dados.get("cpf", "")).strip()
        telefone = str(dados.get("telefone", "")).strip()
        estado = str(dados.get("estado", "")).strip()
        cep = str(dados.get("cep", "")).strip()

        if not nome:
            return False, "Nome: preencha o nome principal do cliente."

        if email and "@" not in email:
            return False, "E-mail: informe um endereco valido."

        if cpf and len(cpf) != 11:
            return False, "CPF: informe os 11 digitos."

        if telefone and len(telefone) not in (10, 11):
            return False, "Telefone: informe DDD e numero completos."

        if estado and len(estado) != 2:
            return False, "Estado: use a sigla da UF com 2 letras."

        if cep and len(cep) != 8:
            return False, "CEP: informe os 8 digitos do CEP."

        return True, ""

    @staticmethod
    def cadastrar_cliente(dados):
        valido, mensagem = ClienteService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            cliente_id = ClienteModel.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao salvar cliente:\n{exc}"

        if not cliente_id:
            return False, "Não foi possível cadastrar o cliente."

        return True, "Cliente cadastrado com sucesso!"

    @staticmethod
    def atualizar_cliente(cliente_id, dados):
        valido, mensagem = ClienteService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            atualizado = ClienteModel.atualizar(int(cliente_id), dados)
        except Exception as exc:
            return False, f"Erro ao atualizar cliente:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o cliente."

        return True, "Cliente atualizado com sucesso!"

    @staticmethod
    def alternar_status(cliente_id):
        cliente = ClienteModel.buscar_por_id(int(cliente_id))
        if not cliente:
            return False, "Cliente não encontrado."

        ativo_atual = str(cliente.get("ativo") or "N").strip().upper()
        novo_status = "N" if ativo_atual == "S" else "S"

        try:
            atualizado = ClienteModel.atualizar_status(int(cliente_id), novo_status)
        except Exception as exc:
            return False, f"Erro ao atualizar status do cliente:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o status do cliente."

        acao = "ativado" if novo_status == "S" else "desativado"
        return True, f"Cliente {acao} com sucesso!"
