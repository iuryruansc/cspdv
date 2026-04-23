from pathlib import Path
from typing import Any, Dict, Optional

from PyQt5.QtCore import QDateTime, QTimer, Qt
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget

from modules.produtos.services.produto_service import ProdutoService

from ui.venda.frente_venda import Ui_FrenteVenda


class FrenteVendaView(QWidget, Ui_FrenteVenda):
    lineEditDescricaoProduto: QLineEdit
    lineEditCodigo: QLineEdit
    lineEditQuantidade: QLineEdit
    lineEditPrecoUnitario: QLineEdit
    lineEditSubtotalItem: QLineEdit
    lineEditDesconto: QLineEdit
    lineEditTotalItens: QLineEdit
    lblImagemProduto: QLabel
    lblTotalAPagarValor: QLabel
    lblStatusVenda: QLabel
    lblDataHora: QLabel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._produto_atual: Optional[Dict[str, Any]] = None
        self._busca_timer = QTimer(self)
        self._busca_timer.setSingleShot(True)
        self._busca_timer.setInterval(180)
        self._busca_timer.timeout.connect(self._executar_busca_produto)

        self._relogio_timer = QTimer(self)
        self._relogio_timer.setInterval(1000)
        self._relogio_timer.timeout.connect(self._atualizar_data_hora)

        self._configurar_interface()
        self._conectar_sinais()
        self._limpar_preview_produto()
        self._atualizar_data_hora()
        self._relogio_timer.start()
        QTimer.singleShot(0, self.lineEditDescricaoProduto.setFocus)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self.lineEditDescricaoProduto.setFocus)
        self.lineEditDescricaoProduto.selectAll()

    def _configurar_interface(self) -> None:
        self.lineEditDescricaoProduto.setReadOnly(False)
        self.lineEditDescricaoProduto.setPlaceholderText(
            "Digite o nome do produto ou leia o código de barras..."
        )
        self.lineEditQuantidade.setValidator(QIntValidator(1, 999999, self))
        self.lineEditQuantidade.setText("1")

        # A área de status de leitura foi removida do fluxo para dar mais altura
        # ao preview do produto sem mexer na lógica principal da tela.
        self.lblStatusVenda.hide()
        self.lblImagemProduto.setMinimumHeight(250)
        self.frameImagem.setMinimumHeight(320)
        self.rightPanelVLayout.setStretch(0, 5)
        self.rightPanelVLayout.setStretch(1, 2)

    def _conectar_sinais(self) -> None:
        self.lineEditDescricaoProduto.textChanged.connect(self._agendar_busca_produto)
        self.lineEditDescricaoProduto.returnPressed.connect(self._executar_busca_produto)
        self.lineEditQuantidade.textChanged.connect(self._atualizar_subtotal)

    def _atualizar_data_hora(self) -> None:
        self.lblDataHora.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm:ss"))

    def _agendar_busca_produto(self) -> None:
        termo = self.lineEditDescricaoProduto.text().strip()
        if not termo:
            self._produto_atual = None
            self._limpar_preview_produto()
            return
        self._busca_timer.start()

    def _executar_busca_produto(self) -> None:
        termo = self.lineEditDescricaoProduto.text().strip()
        if not termo:
            self._produto_atual = None
            self._limpar_preview_produto()
            return

        produtos = ProdutoService.buscar_para_venda(termo)
        if not produtos:
            self._produto_atual = None
            self._limpar_preview_produto(manter_descricao=True, mensagem_imagem="Nenhum produto encontrado")
            return

        self._produto_atual = produtos[0]
        self._preencher_preview_produto(self._produto_atual)

    def _preencher_preview_produto(self, produto: Dict[str, Any]) -> None:
        codigo = str(produto.get("codigo_barras") or "")
        preco = float(produto.get("preco_venda") or 0)

        self.lineEditCodigo.setText(codigo)

        if not self.lineEditQuantidade.text().strip():
            self.lineEditQuantidade.setText("1")

        self.lineEditPrecoUnitario.setText(f"{preco:.2f}".replace(".", ","))
        self.lineEditTotalItens.setText("1")
        self._atualizar_subtotal()
        self._atualizar_imagem_produto(produto.get("imagem_path"))

    def _atualizar_subtotal(self) -> None:
        preco = 0.0
        quantidade = int(self.lineEditQuantidade.text().strip() or "1")
        if self._produto_atual:
            preco = float(self._produto_atual.get("preco_venda") or 0)

        subtotal = preco * quantidade
        texto_valor = f"{subtotal:.2f}".replace(".", ",")
        self.lineEditSubtotalItem.setText(texto_valor if preco else "")
        self.lblTotalAPagarValor.setText(texto_valor if preco else "0,00")

    def _resolver_caminho_imagem(self, caminho_relativo: Any) -> Optional[str]:
        if not caminho_relativo:
            return None

        caminho = Path(str(caminho_relativo))
        if caminho.is_absolute():
            return str(caminho)

        return str(Path(__file__).resolve().parents[3] / caminho)

    def _atualizar_imagem_produto(self, imagem_path: Any) -> None:
        caminho = self._resolver_caminho_imagem(imagem_path)
        if not caminho:
            self.lblImagemProduto.setPixmap(QPixmap())
            self.lblImagemProduto.setText("Sem imagem")
            return

        pixmap = QPixmap(caminho)
        if pixmap.isNull():
            self.lblImagemProduto.setPixmap(QPixmap())
            self.lblImagemProduto.setText("Sem imagem")
            return

        self.lblImagemProduto.setText("")
        self.lblImagemProduto.setPixmap(
            pixmap.scaled(self.lblImagemProduto.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        if self._produto_atual:
            self._atualizar_imagem_produto(self._produto_atual.get("imagem_path"))

    def _limpar_preview_produto(
        self,
        manter_descricao: bool = False,
        mensagem_imagem: str = "Imagem do produto",
    ) -> None:
        self.lineEditCodigo.clear()
        if not manter_descricao:
            self.lineEditDescricaoProduto.clear()
        self.lineEditQuantidade.setText("1")
        self.lineEditPrecoUnitario.clear()
        self.lineEditSubtotalItem.clear()
        self.lineEditTotalItens.setText("0")
        self.lblTotalAPagarValor.setText("0,00")
        self.lblImagemProduto.setPixmap(QPixmap())
        self.lblImagemProduto.setText(mensagem_imagem)
