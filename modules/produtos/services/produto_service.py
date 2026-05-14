from modules.produtos.models.produto_model import ProdutoModel
from utils.app_logger import log_error

class ProdutoService:
    @staticmethod
    def buscar_para_venda(termo):
        termo_limpo = str(termo or "").strip()
        if len(termo_limpo) < 2:
            return []
        try:
            return ProdutoModel.buscar_para_venda(termo_limpo)
        except Exception as e:
            log_error("Erro ao buscar produtos para venda no serviço.", e)
            return []

    @staticmethod
    def _validar_dados_produto(dados, produto_id=None):
        nome = str(dados.get("nome", "")).strip()
        cod_produto = str(dados.get("cod_produto", "")).strip()
        codigo_barras = str(dados.get("codigo_barras", "")).strip()
        ativo = str(dados.get("ativo", "")).strip().upper()
        categoria_id = dados.get("categoria_id")
        marca_id = dados.get("marca_id")
        fornecedor_id = dados.get("fornecedor_id")

        if len(nome) < 3:
            return False, "O nome do produto deve ter pelo menos 3 caracteres."

        if not cod_produto:
            return False, "O código do produto é obrigatório."

        if not codigo_barras:
            return False, "O código de barras é obrigatório."

        if categoria_id is None:
            return False, "A categoria do produto é obrigatória."

        if marca_id is None:
            return False, "A marca do produto é obrigatória."

        if fornecedor_id is None:
            return False, "O fornecedor do produto é obrigatório."

        if ativo not in {"S", "N"}:
            return False, "O status ativo do produto é obrigatório."

        if float(dados.get("preco_venda", 0)) <= 0:
            return False, "O preço de venda deve ser maior que zero."

        produto_existente = ProdutoModel.buscar_por_codigo(cod_produto)
        produto_existente_id = int((produto_existente or {}).get("id") or 0)
        if produto_existente and produto_existente_id != int(produto_id or 0):
            return False, "Este código do produto já está em uso."

        produto_existente_barras = ProdutoModel.buscar_por_codigo_barras(codigo_barras)
        produto_existente_barras_id = int((produto_existente_barras or {}).get("id") or 0)
        if produto_existente_barras and produto_existente_barras_id != int(produto_id or 0):
            return False, "Este código de barras já está em uso."

        return True, ""

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
            return None, "Produto não localizado no sistema.", False

        except Exception as e:
            log_error("Erro ao validar e buscar produto por código.", e)
            return None, "Erro técnico ao consultar o banco de dados.", False

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
            return False, "Produto não localizado para edição."

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
            return False, "Não foi possível identificar o usuário logado para registrar o ajuste."

        if quantidade <= 0:
            return False, "Informe uma quantidade maior que zero para o ajuste."

        produto = ProdutoModel.buscar_por_id(int(produto_id))
        if not produto:
            return False, "Produto não localizado para ajuste."

        quantidade_atual = float(produto.get("quantidade_estoque") or 0)
        modo_normalizado = str(modo).strip().lower()

        if modo_normalizado == "definir":
            nova_quantidade = quantidade
        elif modo_normalizado == "somar":
            nova_quantidade = quantidade_atual + quantidade
        elif modo_normalizado == "subtrair":
            nova_quantidade = quantidade_atual - quantidade
        else:
            return False, "Modo de ajuste inválido."

        if nova_quantidade < 0:
            return False, "O ajuste resultaria em estoque negativo."

        if nova_quantidade == quantidade_atual:
            return False, "Nenhuma alteração foi realizada, pois o estoque final seria igual ao atual."

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
            return False, "Produto não localizado."

        ativo_atual = str(produto.get("ativo") or "N").strip().upper()
        novo_status = "N" if ativo_atual == "S" else "S"

        try:
            ProdutoModel.atualizar_status(int(produto_id), novo_status)
            acao = "ativado" if novo_status == "S" else "desativado"
            return True, f"Produto {acao} com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar status do produto: {str(e)}"
