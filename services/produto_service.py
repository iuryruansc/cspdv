from models.produto_model import ProdutoModel

class ProdutoService:
    @staticmethod
    def validar_e_buscar_por_codigo(codigo_bruto):
        codigo = str(codigo_bruto).strip()

        if not codigo:
            return None, "O campo de código está vazio.", False
        
        if len(codigo) < 3:
            return None, "Código muito curto para ser válido.", False

        try:
            produto = ProdutoModel.buscar_por_codigo(codigo)

            if produto:
                return produto, "Produto encontrado com sucesso!", True
            else:
                return None, "Produto não localizado no sistema.", False

        except Exception as e:
            print(f"Erro no ProdutoService: {e}")
            return None, "Erro técnico ao consultar o banco de dados.", False
        
    @staticmethod
    def cadastrar_produto(dados):
        if not dados.get('descricao') or len(dados['descricao']) < 3:
            return False, "A descrição deve ter pelo menos 3 caracteres."
        
        if float(dados.get('preco_venda', 0)) <= 0:
            return False, "O preço de venda deve ser maior que zero."

        if ProdutoModel.buscar_por_codigo(dados['codigo_barras']):
            return False, "Este código de barras já está em uso."

        try:
            ProdutoModel.inserir(dados)
            return True, "Produto cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar no banco: {str(e)}"