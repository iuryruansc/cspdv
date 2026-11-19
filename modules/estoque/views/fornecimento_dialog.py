from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QLineEdit,
)

from core.session_manager import SessionManager
from modules.estoque.services.estoque_service import EstoqueService
from utils.ui_messages import confirmar_acao, mostrar_aviso, mostrar_info


class _BuscaProdutoSignals(QObject):
    concluido = pyqtSignal(object, int)


class _BuscaProdutoRunnable(QRunnable):
    def __init__(self, termo: str, geracao: int):
        super().__init__()
        self._termo = termo
        self._geracao = geracao
        self.signals = _BuscaProdutoSignals()

    def run(self) -> None:
        resultados = EstoqueService.buscar_produtos_fornecimento(self._termo)
        self.signals.concluido.emit(resultados, self._geracao)


class FornecimentoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fornecimento de Produto")
        self.setMinimumSize(540, 500)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self._clientes: list[dict[str, Any]] = []
        self._cliente: dict[str, Any] | None = None
        self._produto: dict[str, Any] | None = None
        self._busca_pool = QThreadPool(self)
        self._busca_pool.setMaxThreadCount(1)
        self._busca_geracao = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("Fornecimento de Produto", self)
        titulo.setStyleSheet("font-size:16px;font-weight:bold;color:#153552;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._carregar_destinatarios()
        self.lineBuscaCliente = QLineEdit(self)
        self.lineBuscaCliente.setPlaceholderText("Digite nome, CPF ou telefone")
        self.lineBuscaCliente.textChanged.connect(self._filtrar_clientes)
        form.addRow("Fornecer para:", self.lineBuscaCliente)
        layout.addLayout(form)

        self.listaClientes = QListWidget(self)
        self.listaClientes.setMaximumHeight(115)
        self.listaClientes.itemClicked.connect(self._selecionar_cliente)
        layout.addWidget(self.listaClientes)

        self.lblClienteSelecionado = QLabel("Nenhum destinatário selecionado", self)
        self.lblClienteSelecionado.setStyleSheet("font-weight:bold;color:#1a5fa0;")
        layout.addWidget(self.lblClienteSelecionado)

        form_produto = QFormLayout()
        form_produto.setSpacing(10)
        form_produto.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lineBuscaProduto = QLineEdit(self)
        self.lineBuscaProduto.setPlaceholderText("Código de barras, código do produto ou nome")
        self.lineBuscaProduto.returnPressed.connect(self._buscar_produtos)
        form_produto.addRow("Produto:", self.lineBuscaProduto)
        layout.addLayout(form_produto)

        self.listaProdutos = QListWidget(self)
        self.listaProdutos.setMaximumHeight(130)
        self.listaProdutos.itemClicked.connect(self._selecionar_produto)
        self.listaProdutos.itemDoubleClicked.connect(self._selecionar_produto)
        layout.addWidget(self.listaProdutos)

        self.lblProdutoSelecionado = QLabel("Nenhum produto selecionado", self)
        self.lblProdutoSelecionado.setStyleSheet("font-weight:bold;color:#1a5fa0;")
        layout.addWidget(self.lblProdutoSelecionado)

        self.lblEstoqueDisponivel = QLabel("Estoque disponível: -", self)
        layout.addWidget(self.lblEstoqueDisponivel)

        self.spinQuantidade = QSpinBox(self)
        self.spinQuantidade.setRange(1, 999999999)
        self.spinQuantidade.setValue(1)
        form_quantidade = QFormLayout()
        form_quantidade.addRow("Quantidade:", self.spinQuantidade)
        layout.addLayout(form_quantidade)

        self.textObservacao = QPlainTextEdit(self)
        self.textObservacao.setMaximumHeight(75)
        self.textObservacao.setPlaceholderText("Observação opcional")
        layout.addWidget(QLabel("Observação:", self))
        layout.addWidget(self.textObservacao)

        botoes = QHBoxLayout()
        botoes.addStretch()
        btn_cancelar = QPushButton("Cancelar", self)
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_cancelar)
        self.btnRegistrar = QPushButton("Registrar Fornecimento", self)
        self.btnRegistrar.setStyleSheet("background:#1a5fa0;color:white;font-weight:bold;padding:8px 14px;")
        self.btnRegistrar.clicked.connect(self._registrar)
        botoes.addWidget(self.btnRegistrar)
        layout.addLayout(botoes)

        self._busca_timer = QTimer(self)
        self._busca_timer.setSingleShot(True)
        self._busca_timer.setInterval(250)
        self._busca_timer.timeout.connect(self._buscar_produtos)
        self.lineBuscaProduto.textChanged.connect(lambda: self._busca_timer.start())

    def _carregar_destinatarios(self) -> None:
        self._clientes = EstoqueService.listar_clientes_fornecimento()

    def _filtrar_clientes(self, texto: str) -> None:
        termo = str(texto or "").strip().casefold()
        self._cliente = None
        self.lblClienteSelecionado.setText("Nenhum destinatário selecionado")
        self.listaClientes.clear()
        if len(termo) < 2:
            return

        encontrados = []
        for cliente in self._clientes:
            nome = str(cliente.get("nome") or "")
            cpf = str(cliente.get("cpf") or "")
            telefone = str(cliente.get("telefone") or "")
            if termo in nome.casefold() or termo in cpf.casefold() or termo in telefone.casefold():
                encontrados.append(cliente)
            if len(encontrados) >= 20:
                break

        for cliente in encontrados:
            documento = str(cliente.get("cpf") or cliente.get("telefone") or "").strip()
            texto_item = str(cliente.get("nome") or "-")
            if documento:
                texto_item = f"{texto_item} — {documento}"
            item = QListWidgetItem(texto_item)
            item.setData(Qt.UserRole, cliente)
            self.listaClientes.addItem(item)

    def _selecionar_cliente(self, item: QListWidgetItem) -> None:
        cliente = item.data(Qt.UserRole)
        if not cliente:
            return
        self._cliente = cliente
        nome = str(cliente.get("nome") or "-")
        self.lineBuscaCliente.blockSignals(True)
        self.lineBuscaCliente.setText(nome)
        self.lineBuscaCliente.blockSignals(False)
        self.listaClientes.clear()
        self.lblClienteSelecionado.setText(f"Destinatário selecionado: {nome}")

    def _buscar_produtos(self) -> None:
        termo = self.lineBuscaProduto.text().strip()
        self.listaProdutos.clear()
        if len(termo) < 2:
            return
        self._busca_geracao += 1
        worker = _BuscaProdutoRunnable(termo, self._busca_geracao)
        worker.signals.concluido.connect(self._renderizar_produtos)
        self._busca_pool.start(worker)

    def _renderizar_produtos(self, produtos: object, geracao: int) -> None:
        if geracao != self._busca_geracao:
            return
        if self.lineBuscaProduto.text().strip().lower() == "":
            return
        for produto in produtos or []:
            texto = (
                f"{produto.get('nome') or '-'} | "
                f"Código: {produto.get('codigo_barras') or produto.get('cod_produto') or '-'} | "
                f"Estoque: {int(produto.get('quantidade_estoque') or 0)}"
            )
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, produto)
            self.listaProdutos.addItem(item)

    def _selecionar_produto(self, item: QListWidgetItem) -> None:
        self._produto = item.data(Qt.UserRole)
        if not self._produto:
            return
        self.lblProdutoSelecionado.setText(str(self._produto.get("nome") or "-"))
        self.lblEstoqueDisponivel.setText(
            f"Estoque disponível: {int(self._produto.get('quantidade_estoque') or 0)}"
        )
        self.spinQuantidade.setMaximum(max(1, int(self._produto.get("quantidade_estoque") or 1)))

    def _registrar(self) -> None:
        cliente = self._cliente
        if not cliente:
            mostrar_aviso(self, "Destinatário obrigatório", "Selecione um cliente para o fornecimento.")
            return
        if not self._produto:
            mostrar_aviso(self, "Produto obrigatório", "Busque e selecione o produto que será fornecido.")
            return

        quantidade = int(self.spinQuantidade.value())
        cliente_nome = str(cliente.get("nome") or "-")
        produto_nome = str(self._produto.get("nome") or "-")
        if not confirmar_acao(
            self,
            "Confirmar fornecimento",
            f"Confirma o fornecimento de {quantidade} unidade(s) de {produto_nome} para {cliente_nome}?",
        ):
            return

        usuario = SessionManager.current_user() or {}
        sucesso, mensagem = EstoqueService.registrar_fornecimento(
            produto_id=int(self._produto["id"]),
            cliente_id=int(cliente["id"]),
            cliente_nome=cliente_nome,
            quantidade=quantidade,
            usuario_id=usuario.get("id"),
            observacao=self.textObservacao.toPlainText().strip(),
        )
        if sucesso:
            mostrar_info(self, "Fornecimento", mensagem)
            self.accept()
        else:
            mostrar_aviso(self, "Fornecimento não realizado", mensagem)
