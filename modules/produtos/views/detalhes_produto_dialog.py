from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from utils.format_utils import formatar_inteiro, formatar_moeda
from utils.image_utils import atualizar_preview_label, resolver_caminho_arquivo


class DetalhesProdutoDialog(QDialog):
    def __init__(self, produto, parent=None):
        super().__init__(parent)
        self.produto = produto

        self.setWindowTitle("Detalhes do Produto")
        self.setModal(True)
        self.resize(720, 420)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(16)

        self.lblTitulo = QLabel(str(produto.get("nome") or "Produto"))
        self.lblTitulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a3a5c;")
        root_layout.addWidget(self.lblTitulo)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignTop)

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
            form_layout.addRow(label, valor)

        content_layout.addLayout(form_layout, 2)

        self.lblImagem = QLabel("Sem imagem")
        self.lblImagem.setAlignment(Qt.AlignCenter)
        self.lblImagem.setMinimumSize(220, 220)
        self.lblImagem.setStyleSheet(
            "border: 1px solid #c0d8ec; border-radius: 6px; background-color: #f7fbff; color: #5d7f99;"
        )
        self._carregar_imagem()
        content_layout.addWidget(self.lblImagem, 1)

        root_layout.addLayout(content_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.btnFechar = QPushButton("Fechar")
        self.btnFechar.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btnFechar)
        root_layout.addLayout(buttons_layout)

    def _carregar_imagem(self):
        atualizar_preview_label(
            self.lblImagem,
            resolver_caminho_arquivo(self.produto.get("imagem_path")),
        )
