from modules.produtos.models.produto_model import ProdutoModel

class ProdutoService:
    @staticmethod
    def _validar_dados_produto(dados, produto_id=None):
        nome = str(dados.get("nome", "")).strip()
        codigo_barras = str(dados.get("codigo_barras", "")).strip()
        ativo = str(dados.get("ativo", "")).strip().upper()
        categoria_id = dados.get("categoria_id")
        marca_id = dados.get("marca_id")
        fornecedor_id = dados.get("fornecedor_id")

        if len(nome) < 3:
            return False, "O nome do produto deve ter pelo menos 3 caracteres."

        if not codigo_barras:
            return False, "O codigo de barras e obrigatorio."

        if categoria_id is None:
            return False, "A categoria do produto e obrigatoria."

        if marca_id is None:
            return False, "A marca do produto e obrigatoria."

        if fornecedor_id is None:
            return False, "O fornecedor do produto e obrigatorio."

        if ativo not in {"S", "N"}:
            return False, "O status ativo do produto e obrigatorio."

        if float(dados.get("preco_venda", 0)) <= 0:
            return False, "O preco de venda deve ser maior que zero."

        produto_existente = ProdutoModel.buscar_por_codigo(codigo_barras)
        if produto_existente and int(produto_existente.get("id")) != int(produto_id or 0):
            return False, "Este codigo de barras ja esta em uso."

        return True, ""

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
        valido, mensagem = ProdutoService._validar_dados_produto(dados)
        if not valido:
            return False, mensagem

        try:
            ProdutoModel.inserir(dados)
            return True, "Produto cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar no banco: {str(e)}"

    @staticmethod
    def atualizar_produto(produto_id, dados):
        produto = ProdutoModel.buscar_por_id(int(produto_id))
        if not produto:
            return False, "Produto nao localizado para edicao."

        valido, mensagem = ProdutoService._validar_dados_produto(dados, produto_id=produto_id)
        if not valido:
            return False, mensagem

        try:
            ProdutoModel.atualizar(int(produto_id), dados)
            return True, "Produto atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar no banco: {str(e)}"

    @staticmethod
    def ajustar_quantidade(produto_id, modo, quantidade, observacao, usuario_id):
        if not usuario_id:
            return False, "Nao foi possivel identificar o usuario logado para registrar o ajuste."

        if quantidade <= 0:
            return False, "Informe uma quantidade maior que zero para o ajuste."

        produto = ProdutoModel.buscar_por_id(int(produto_id))
        if not produto:
            return False, "Produto nao localizado para ajuste."

        quantidade_atual = float(produto.get("quantidade_estoque") or 0)
        modo_normalizado = str(modo).strip().lower()

        if modo_normalizado == "definir":
            nova_quantidade = quantidade
        elif modo_normalizado == "somar":
            nova_quantidade = quantidade_atual + quantidade
        elif modo_normalizado == "subtrair":
            nova_quantidade = quantidade_atual - quantidade
        else:
            return False, "Modo de ajuste invalido."

        if nova_quantidade < 0:
            return False, "O ajuste resultaria em estoque negativo."

        if nova_quantidade == quantidade_atual:
            return False, "Nenhuma alteracao foi realizada, pois o estoque final seria igual ao atual."

        quantidade_ajuste = nova_quantidade - quantidade_atual
        observacao_final = (
            f"Ajuste manual ({modo_normalizado})"
            if not observacao
            else f"Ajuste manual ({modo_normalizado}) - {str(observacao).strip()}"
        )

        try:
            ProdutoModel.ajustar_quantidade(
                produto_id=int(produto_id),
                nova_quantidade=nova_quantidade,
                quantidade_anterior=quantidade_atual,
                quantidade_ajuste=quantidade_ajuste,
                usuario_id=int(usuario_id),
                observacoes=observacao_final,
            )
            return True, "Quantidade ajustada com sucesso."
        except Exception as e:
            return False, f"Erro ao registrar ajuste de estoque: {str(e)}"

    @staticmethod
    def alternar_status(produto_id):
        produto = ProdutoModel.buscar_por_id(int(produto_id))
        if not produto:
            return False, "Produto nao localizado."

        ativo_atual = str(produto.get("ativo") or "N").strip().upper()
        novo_status = "N" if ativo_atual == "S" else "S"

        try:
            ProdutoModel.atualizar_status(int(produto_id), novo_status)
            acao = "ativado" if novo_status == "S" else "desativado"
            return True, f"Produto {acao} com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar status do produto: {str(e)}"
