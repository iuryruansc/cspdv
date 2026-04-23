from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QSpinBox,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from core.session_manager import SessionManager
from modules.produtos.services.produto_service import ProdutoService

class AjusteQuantidadeDialog(QDialog):
    def __init__(self, produto: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.produto = produto
        self.quantidade_atual = float(produto.get("quantidade_estoque") or 0)

        self.setWindowTitle("Ajustar Quantidade")
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.resize(460, 280)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        self.lblTitulo = QLabel(f"{produto.get('nome', 'Produto')}")
        self.lblTitulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a3a5c;")
        root_layout.addWidget(self.lblTitulo)

        self.lblCodigo = QLabel(f"Codigo de barras: {produto.get('codigo_barras', '-')}")
        self.lblCodigo.setStyleSheet("color: #5d7f99; font-size: 12px;")
        root_layout.addWidget(self.lblCodigo)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.lblQuantidadeAtual = QLabel(self._formatar_quantidade(self.quantidade_atual))
        form_layout.addRow("Quantidade atual:", self.lblQuantidadeAtual)

        self.comboModo = QComboBox()
        self.comboModo.addItems(["Definir", "Somar", "Subtrair"])
        self.comboModo.currentTextChanged.connect(self._atualizar_previsao)
        form_layout.addRow("Operacao:", self.comboModo)

        self.spinQuantidade = QSpinBox()
        self.spinQuantidade.setRange(0, 999999999)
        self.spinQuantidade.setSingleStep(1)
        self.spinQuantidade.setValue(int(self.quantidade_atual))
        self.spinQuantidade.valueChanged.connect(self._atualizar_previsao)
        form_layout.addRow("Quantidade:", self.spinQuantidade)

        self.lblResultado = QLabel(self._formatar_quantidade(self.quantidade_atual))
        self.lblResultado.setStyleSheet("font-weight: bold; color: #1a5fa0;")
        form_layout.addRow("Saldo previsto:", self.lblResultado)

        self.textObservacao = QPlainTextEdit()
        self.textObservacao.setPlaceholderText("Motivo do ajuste ou observacao operacional...")
        self.textObservacao.setMaximumBlockCount(6)
        form_layout.addRow("Observacao:", self.textObservacao)

        root_layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.btnCancelar = QPushButton("Cancelar")
        self.btnSalvar = QPushButton("Aplicar Ajuste")
        self.btnSalvar.setStyleSheet(
            "QPushButton { background-color: #1a5fa0; color: white; font-weight: bold; border: none; border-radius: 4px; padding: 8px 14px; }"
            "QPushButton:hover { background-color: #2a74b8; }"
        )
        self.btnCancelar.clicked.connect(self.reject)
        self.btnSalvar.clicked.connect(self._aplicar_ajuste)

        buttons_layout.addWidget(self.btnCancelar)
        buttons_layout.addWidget(self.btnSalvar)
        root_layout.addLayout(buttons_layout)

        self._atualizar_previsao()

    def _formatar_quantidade(self, valor: float) -> str:
        return str(int(valor))

    def _saldo_previsto(self) -> float:
        quantidade = int(self.spinQuantidade.value())
        modo = self.comboModo.currentText().lower()
        if modo == "definir":
            return quantidade
        if modo == "somar":
            return self.quantidade_atual + quantidade
        return self.quantidade_atual - quantidade

    def _atualizar_previsao(self) -> None:
        saldo = self._saldo_previsto()
        self.lblResultado.setText(self._formatar_quantidade(saldo))
        if saldo < 0:
            self.lblResultado.setStyleSheet("font-weight: bold; color: #cc2222;")
        else:
            self.lblResultado.setStyleSheet("font-weight: bold; color: #1a5fa0;")

    def _aplicar_ajuste(self) -> None:
        usuario = SessionManager.current_user() or {}
        sucesso, mensagem = ProdutoService.ajustar_quantidade(
            produto_id=self.produto["id"],
            modo=self.comboModo.currentText(),
            quantidade=int(self.spinQuantidade.value()),
            observacao=self.textObservacao.toPlainText().strip(),
            usuario_id=usuario.get("id"),
        )
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.accept()
            return

        QMessageBox.warning(self, "Ajuste nao realizado", mensagem)
