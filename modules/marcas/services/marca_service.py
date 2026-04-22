from modules.marcas.models.marca_model import MarcaModel

class MarcaService:
    @staticmethod
    def cadastrar_marca(dados):
        nome = str(dados.get("nome_marca", "")).strip()
        ativo = str(dados.get("ativo", "")).strip().upper()

        if len(nome) < 2:
            return False, "O nome da marca deve ter pelo menos 2 caracteres."

        if ativo not in {"S", "N"}:
            return False, "O status da marca e obrigatorio."

        try:
            marca_id = MarcaModel.inserir(dados)
        except Exception as exc:
            return False, f"Erro ao salvar marca:\n{exc}"

        if not marca_id:
            return False, "Nao foi possivel cadastrar a marca."

        return True, "Marca cadastrada com sucesso!"
