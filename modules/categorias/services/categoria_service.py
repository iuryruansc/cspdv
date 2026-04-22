from modules.categorias.models.categoria_model import CategoriaModel

class CategoriaService:
    @staticmethod
    def cadastrar_categoria(dados):
        nome = str(dados.get("nome", "")).strip()
        ativo = str(dados.get("ativo", "")).strip().upper()

        if len(nome) < 2:
            return False, "O nome da categoria deve ter pelo menos 2 caracteres."

        if ativo not in {"S", "N"}:
            return False, "O status da categoria e obrigatorio."

        try:
            categoria_id = CategoriaModel.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao salvar categoria:\n{exc}"

        if not categoria_id:
            return False, "Nao foi possivel cadastrar a categoria."

        return True, "Categoria cadastrada com sucesso!"
