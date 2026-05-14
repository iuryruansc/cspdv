from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from modules.produtos.models.produto_model import ProdutoModel
from utils.format_utils import formatar_decimal
from utils.image_utils import atualizar_preview_label
from utils.ui_messages import mostrar_info

class ConsultaPrecoDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._produto_encontrado: Optional[Dict[str, Any]] = None
        self._montar_interface()

    def _montar_interface(self) -> None:
        self.setWindowTitle("Consulta de Preço")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(540, 520)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #dceaf6;
                color: #14324c;
            }
            QFrame#frameCard {
                background-color: #ffffff;
                border: 1px solid #b9d0e3;
                border-radius: 12px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #9ebcd4;
                border-radius: 8px;
                font-size: 16px;
                color: #14324c;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border: 2px solid #2f79c8;
            }
            QPushButton {
                background-color: #2f79c8;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 8px 14px;
                min-height: 34px;
            }
            QPushButton:hover {
                background-color: #2566ab;
            }
            QPushButton#btnFechar {
                background-color: #eef4fa;
                color: #23425f;
                border: 1px solid #b9d0e3;
            }
            QPushButton#btnFechar:hover {
                background-color: #ddeaf5;
            }
            QLabel#lblTitulo {
                font-size: 18px;
                font-weight: 700;
                color: #14324c;
            }
            QLabel#lblHint {
                font-size: 11px;
                color: #4d6f8e;
            }
            QLabel#lblImagem {
                background-color: #eff5fb;
                border: 1px dashed #9ebcd4;
                border-radius: 10px;
                color: #5f7d98;
                font-size: 12px;
            }
            QLabel#lblCampoTitulo {
                font-size: 11px;
                font-weight: 700;
                color: #4d6f8e;
                letter-spacing: 0.4px;
            }
            QLabel#lblCampoValor {
                font-size: 18px;
                font-weight: 700;
                color: #163552;
                padding-top: 2px;
                padding-bottom: 6px;
            }
            QLabel#lblPrecoValor {
                font-size: 28px;
                font-weight: 800;
                color: #1a5fa0;
                padding-top: 4px;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.frameCard = QFrame(self)
        self.frameCard.setObjectName("frameCard")
        layout.addWidget(self.frameCard)

        card_layout = QVBoxLayout(self.frameCard)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(12)

        self.lblTitulo = QLabel("Consulta de Preço", self.frameCard)
        self.lblTitulo.setObjectName("lblTitulo")
        card_layout.addWidget(self.lblTitulo)

        self.lblHint = QLabel(
            "Busque por código interno do produto ou código de barras exato.",
            self.frameCard,
        )
        self.lblHint.setObjectName("lblHint")
        card_layout.addWidget(self.lblHint)

        busca_layout = QHBoxLayout()
        busca_layout.setSpacing(8)
        card_layout.addLayout(busca_layout)

        self.lineBusca = QLineEdit(self.frameCard)
        self.lineBusca.setPlaceholderText("Digite o código do produto ou código de barras...")
        self.lineBusca.returnPressed.connect(self._buscar_produto)
        busca_layout.addWidget(self.lineBusca)

        self.btnBuscar = QPushButton("Buscar", self.frameCard)
        self.btnBuscar.clicked.connect(self._buscar_produto)
        busca_layout.addWidget(self.btnBuscar)

        self.lblImagem = QLabel("Imagem do produto", self.frameCard)
        self.lblImagem.setObjectName("lblImagem")
        self.lblImagem.setAlignment(Qt.AlignCenter)
        self.lblImagem.setMinimumHeight(230)
        card_layout.addWidget(self.lblImagem)

        self.lblCodigoTitulo = QLabel("Código", self.frameCard)
        self.lblCodigoTitulo.setObjectName("lblCampoTitulo")
        card_layout.addWidget(self.lblCodigoTitulo)

        self.lblCodigoValor = QLabel("—", self.frameCard)
        self.lblCodigoValor.setObjectName("lblCampoValor")
        card_layout.addWidget(self.lblCodigoValor)

        self.lblDescricaoTitulo = QLabel("Descrição", self.frameCard)
        self.lblDescricaoTitulo.setObjectName("lblCampoTitulo")
        card_layout.addWidget(self.lblDescricaoTitulo)

        self.lblDescricaoValor = QLabel("—", self.frameCard)
        self.lblDescricaoValor.setObjectName("lblCampoValor")
        self.lblDescricaoValor.setWordWrap(True)
        card_layout.addWidget(self.lblDescricaoValor)

        rodape_layout = QHBoxLayout()
        rodape_layout.setSpacing(18)
        card_layout.addLayout(rodape_layout)

        estoque_layout = QVBoxLayout()
        estoque_layout.setSpacing(0)
        rodape_layout.addLayout(estoque_layout, 1)

        self.lblEstoqueTitulo = QLabel("Estoque", self.frameCard)
        self.lblEstoqueTitulo.setObjectName("lblCampoTitulo")
        estoque_layout.addWidget(self.lblEstoqueTitulo)

        self.lblEstoqueValor = QLabel("—", self.frameCard)
        self.lblEstoqueValor.setObjectName("lblCampoValor")
        estoque_layout.addWidget(self.lblEstoqueValor)

        preco_layout = QVBoxLayout()
        preco_layout.setSpacing(0)
        rodape_layout.addLayout(preco_layout, 1)

        self.lblPrecoTitulo = QLabel("Preço", self.frameCard)
        self.lblPrecoTitulo.setObjectName("lblCampoTitulo")
        preco_layout.addWidget(self.lblPrecoTitulo)

        self.lblPrecoValor = QLabel("R$ —", self.frameCard)
        self.lblPrecoValor.setObjectName("lblPrecoValor")
        self.lblPrecoValor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        preco_layout.addWidget(self.lblPrecoValor)

        botoes_layout = QHBoxLayout()
        botoes_layout.addStretch(1)
        card_layout.addLayout(botoes_layout)

        self.btnFechar = QPushButton("Fechar", self.frameCard)
        self.btnFechar.setObjectName("btnFechar")
        self.btnFechar.clicked.connect(self.reject)
        botoes_layout.addWidget(self.btnFechar)

        self.lineBusca.setFocus()

    def _buscar_produto(self) -> None:
        termo = self.lineBusca.text().strip()
        self._produto_encontrado = None
        self._limpar_resultado()
        if not termo:
            return

        produto = self._buscar_produto_exato(termo)
        if not produto:
            mostrar_info(
                self,
                "Produto não encontrado",
                "Não foi localizado um produto com o código informado.",
            )
            return

        self._produto_encontrado = produto
        self._preencher_resultado(termo, produto)

    def _buscar_produto_exato(self, termo: str) -> Optional[Dict[str, Any]]:
        produto_codigo_barras = ProdutoModel.buscar_por_codigo_barras(termo)
        if produto_codigo_barras:
            return produto_codigo_barras

        produto_codigo = ProdutoModel.buscar_por_codigo(termo)
        if produto_codigo:
            return produto_codigo

        if termo.isdigit():
            return ProdutoModel.buscar_por_id(int(termo))
        return None

    def _preencher_resultado(self, termo: str, produto: Dict[str, Any]) -> None:
        self.lblCodigoValor.setText(termo)
        self.lblDescricaoValor.setText(str(produto.get("nome") or "—"))
        self.lblEstoqueValor.setText(str(int(float(produto.get("quantidade_estoque") or 0))))
        self.lblPrecoValor.setText(f"R$ {formatar_decimal(produto.get('preco_venda'))}")
        atualizar_preview_label(
            self.lblImagem,
            produto.get("imagem_path"),
            texto_padrao="Sem imagem para este produto",
        )

    def _limpar_resultado(self) -> None:
        self.lblCodigoValor.setText("—")
        self.lblDescricaoValor.setText("—")
        self.lblEstoqueValor.setText("—")
        self.lblPrecoValor.setText("R$ —")
        atualizar_preview_label(self.lblImagem, None, texto_padrao="Imagem do produto")
