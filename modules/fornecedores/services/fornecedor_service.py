from modules.fornecedores.models.fornecedor_model import FornecedorModel

class FornecedorService:
    @staticmethod
    def _validar_dados(dados):
        nome = str(dados.get("nome_fantasia", "")).strip()
        email = str(dados.get("email", "")).strip()
        cnpj_cpf = str(dados.get("cnpj_cpf", "")).strip()
        telefone = str(dados.get("telefone", "")).strip()
        estado = str(dados.get("estado", "")).strip()
        cep = str(dados.get("cep", "")).strip()

        if not nome:
            return False, "Nome Fantasia: preencha o nome principal do fornecedor."

        if email and "@" not in email:
            return False, "E-mail: informe um endereco valido."

        if cnpj_cpf and len(cnpj_cpf) not in (11, 14):
            return False, "CPF/CNPJ: use 11 digitos para CPF ou 14 para CNPJ."

        if telefone and len(telefone) not in (10, 11):
            return False, "Telefone: informe DDD e numero completos."

        if estado and len(estado) != 2:
            return False, "Estado: use a sigla da UF com 2 letras."

        if cep and len(cep) != 8:
            return False, "CEP: informe os 8 digitos do CEP."

        return True, ""

    @staticmethod
    def cadastrar_fornecedor(dados):
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
    def atualizar_fornecedor(fornecedor_id, dados):
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
    def alternar_status(fornecedor_id):
        fornecedor = FornecedorModel.buscar_por_id(int(fornecedor_id))
        if not fornecedor:
            return False, "Fornecedor não encontrado."

        ativo_atual = str(fornecedor.get("ativo") or "N").strip().upper()
        novo_status = "N" if ativo_atual == "S" else "S"

        try:
            atualizado = FornecedorModel.atualizar_status(int(fornecedor_id), novo_status)
        except Exception as exc:
            return False, f"Erro ao atualizar status do fornecedor:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o status do fornecedor."

        acao = "ativado" if novo_status == "S" else "desativado"
        return True, f"Fornecedor {acao} com sucesso!"
