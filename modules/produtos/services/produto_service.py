from modules.produtos.models.produto_model import ProdutoModel

class ProdutoService:
    @staticmethod
    def validar_e_buscar_por_codigo(codigo_bruto):
        codigo = str(codigo_bruto).strip()

        if not codigo:
            return None, "O campo de codigo esta vazio.", False

        if len(codigo) < 3:
            return None, "Codigo muito curto para ser valido.", False

        try:
            produto = ProdutoModel.buscar_por_codigo(codigo)

            if produto:
                return produto, "Produto encontrado com sucesso!", True
            return None, "Produto nao localizado no sistema.", False

        except Exception as e:
            print(f"Erro no ProdutoService: {e}")
            return None, "Erro tecnico ao consultar o banco de dados.", False

    @staticmethod
    def cadastrar_produto(dados):
        nome = str(dados.get("nome", "")).strip()
        if len(nome) < 3:
            return False, "O nome do produto deve ter pelo menos 3 caracteres."

        if float(dados.get("preco_venda", 0)) <= 0:
            return False, "O preco de venda deve ser maior que zero."

        if ProdutoModel.buscar_por_codigo(dados["codigo_barras"]):
            return False, "Este codigo de barras ja esta em uso."

        try:
            ProdutoModel.inserir(dados)
            return True, "Produto cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar no banco: {str(e)}"
