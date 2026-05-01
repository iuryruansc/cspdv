from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel

from ui.produtos.detalhes_produto_dialog import Ui_DetalhesProdutoDialog
from utils.format_utils import formatar_inteiro, formatar_moeda
from utils.image_utils import atualizar_preview_label, resolver_caminho_arquivo


class DetalhesProdutoDialog(QDialog, Ui_DetalhesProdutoDialog):
    def __init__(self, produto, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.produto = produto
        self.setModal(True)

        self.lblTitulo.setText(str(produto.get("nome") or "Produto"))

        campos = [
            ("Codigo interno:", produto.get("id")),
            ("Codigo de barras:", produto.get("codigo_barras")),
            ("Categoria:", produto.get("categoria_nome")),
            ("Marca:", produto.get("marca_nome")),
            ("Fornecedor:", produto.get("fornecedor_nome")),
            ("Preco custo:", formatar_moeda(produto.get("preco_compra"))),
            ("Preco venda:", formatar_moeda(produto.get("preco_venda"))),
            ("Estoque:", formatar_inteiro(produto.get("quantidade_estoque"))),
            ("NCM:", produto.get("ncm") or "-"),
            ("CEST:", produto.get("cest") or "-"),
            ("Unidade comercial:", produto.get("unidade_sigla") or "-"),
            ("Unidade tributavel:", produto.get("unidade_tributavel_sigla") or "-"),
            ("Status:", "Ativo" if str(produto.get("ativo") or "N").upper() == "S" else "Desativado"),
            ("Imagem:", produto.get("imagem_path") or "-"),
        ]

        for label, value in campos:
            valor = QLabel(str(value if value not in (None, "") else "-"))
            valor.setWordWrap(True)
            valor.setStyleSheet("color: #1a3a5c;")
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignRight | Qt.AlignTop)
            self.formLayout.addRow(label_widget, valor)

        self._carregar_imagem()
        self.btnFechar.clicked.connect(self.accept)

    def _carregar_imagem(self):
        atualizar_preview_label(
            self.lblImagem,
            resolver_caminho_arquivo(self.produto.get("imagem_path")),
        )
