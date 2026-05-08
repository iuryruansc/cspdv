from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from core.session_manager import SessionManager
from modules.produtos.services.produto_service import ProdutoService
from ui.produtos.ajuste_quantidade_dialog import Ui_AjusteQuantidadeDialog
from utils.ui_messages import mostrar_aviso, mostrar_info

class AjusteQuantidadeDialog(QDialog, Ui_AjusteQuantidadeDialog):
    def __init__(self, produto: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.produto = produto
        self.quantidade_atual = float(produto.get("quantidade_estoque") or 0)

        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)

        self.lblTitulo.setText(f"{produto.get('nome', 'Produto')}")
        self.lblCodigo.setText(f"Codigo de barras: {produto.get('codigo_barras', '-')}")
        self.lblQuantidadeAtual.setText(self._formatar_quantidade(self.quantidade_atual))

        self.comboModo.addItems(["Definir", "Somar", "Subtrair"])
        self.comboModo.currentTextChanged.connect(self._atualizar_previsao)

        self.spinQuantidade.setRange(0, 999999999)
        self.spinQuantidade.setSingleStep(1)
        self.spinQuantidade.setValue(int(self.quantidade_atual))
        self.spinQuantidade.valueChanged.connect(self._atualizar_previsao)

        self.textObservacao.setMaximumBlockCount(6)
        self.btnCancelar.clicked.connect(self.reject)
        self.btnSalvar.clicked.connect(self._aplicar_ajuste)

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
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
            return

        mostrar_aviso(self, "Ajuste não realizado", mensagem)
