from modules.marcas.models.marca_model import MarcaModel

class MarcaService:
    @staticmethod
    def _validar_dados(dados):
        nome = str(dados.get("nome_marca", "")).strip()
        ativo = str(dados.get("ativo", "")).strip().upper()

        if len(nome) < 2:
            return False, "O nome da marca deve ter pelo menos 2 caracteres."

        if ativo not in {"S", "N"}:
            return False, "O status da marca e obrigatorio."

        return True, ""

    @staticmethod
    def cadastrar_marca(dados):
        valido, mensagem = MarcaService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            marca_id = MarcaModel.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao salvar marca:\n{exc}"

        if not marca_id:
            return False, "Nao foi possivel cadastrar a marca."

        return True, "Marca cadastrada com sucesso!"

    @staticmethod
    def atualizar_marca(marca_id, dados):
        valido, mensagem = MarcaService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            atualizado = MarcaModel.atualizar(int(marca_id), dados)
        except Exception as exc:
            return False, f"Erro ao atualizar marca:\n{exc}"

        if not atualizado:
            return False, "Nao foi possivel atualizar a marca."

        return True, "Marca atualizada com sucesso!"

    @staticmethod
    def alternar_status(marca_id):
        marca = MarcaModel.buscar_por_id(int(marca_id))
        if not marca:
            return False, "Marca nao encontrada."

        ativo_atual = str(marca.get("ativo") or "N").strip().upper()
        novo_status = "N" if ativo_atual == "S" else "S"

        try:
            atualizado = MarcaModel.atualizar_status(int(marca_id), novo_status)
        except Exception as exc:
            return False, f"Erro ao atualizar status da marca:\n{exc}"

        if not atualizado:
            return False, "Nao foi possivel atualizar o status da marca."

        acao = "ativada" if novo_status == "S" else "desativada"
        return True, f"Marca {acao} com sucesso!"
