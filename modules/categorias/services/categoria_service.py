from modules.categorias.models.categoria_model import CategoriaModel

class CategoriaService:
    @staticmethod
    def _validar_dados(dados):
        nome = str(dados.get("nome", "")).strip()
        ativo = str(dados.get("ativo", "")).strip().upper()

        if len(nome) < 2:
            return False, "O nome da categoria deve ter pelo menos 2 caracteres."

        if ativo not in {"S", "N"}:
            return False, "O status da categoria e obrigatorio."

        return True, ""

    @staticmethod
    def cadastrar_categoria(dados):
        valido, mensagem = CategoriaService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            categoria_id = CategoriaModel.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao salvar categoria:\n{exc}"

        if not categoria_id:
            return False, "Nao foi possivel cadastrar a categoria."

        return True, "Categoria cadastrada com sucesso!"

    @staticmethod
    def atualizar_categoria(categoria_id, dados):
        valido, mensagem = CategoriaService._validar_dados(dados)
        if not valido:
            return False, mensagem

        try:
            atualizado = CategoriaModel.atualizar(int(categoria_id), dados)
        except Exception as exc:
            return False, f"Erro ao atualizar categoria:\n{exc}"

        if not atualizado:
            return False, "Nao foi possivel atualizar a categoria."

        return True, "Categoria atualizada com sucesso!"

    @staticmethod
    def alternar_status(categoria_id):
        categoria = CategoriaModel.buscar_por_id(int(categoria_id))
        if not categoria:
            return False, "Categoria nao encontrada."

        ativo_atual = str(categoria.get("ativo") or "N").strip().upper()
        novo_status = "N" if ativo_atual == "S" else "S"

        try:
            atualizado = CategoriaModel.atualizar_status(int(categoria_id), novo_status)
        except Exception as exc:
            return False, f"Erro ao atualizar status da categoria:\n{exc}"

        if not atualizado:
            return False, "Nao foi possivel atualizar o status da categoria."

        acao = "ativada" if novo_status == "S" else "desativada"
        return True, f"Categoria {acao} com sucesso!"
