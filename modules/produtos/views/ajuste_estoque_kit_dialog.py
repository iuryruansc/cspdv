from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QComboBox,
    QPlainTextEdit,
    QVBoxLayout,
)

from modules.produtos.services.kit_service import KitService
from utils.ui_messages import mostrar_aviso, mostrar_info


class AjusteEstoqueKitDialog(QDialog):
    def __init__(self, kit: dict[str, Any], parent=None):
        super().__init__(parent)
        self._kit = kit
        self._kit_id = int(kit.get("id") or 0)
        self._quantidade_atual = int(kit.get("quantidade_estoque") or 0)
        self._montar_interface()

    def _montar_interface(self) -> None:
        self.setWindowTitle("Ajustar Estoque do Kit")
        self.setMinimumSize(400, 350)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("Ajustar Estoque do Kit", self)
        titulo.setStyleSheet("font-size:16px;font-weight:bold;color:#14324c;")
        layout.addWidget(titulo)

        self.lblNomeKit = QLabel(str(self._kit.get("nome") or ""), self)
        self.lblNomeKit.setStyleSheet("font-size:14px;font-weight:bold;color:#1a3a5c;")
        layout.addWidget(self.lblNomeKit)

        self.lblQuantidadeAtual = QLabel(f"Estoque atual: {self._quantidade_atual}", self)
        self.lblQuantidadeAtual.setStyleSheet("font-size:12px;color:#46627d;")
        layout.addWidget(self.lblQuantidadeAtual)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.comboModo = QComboBox(self)
        self.comboModo.addItems(["Definir", "Somar", "Subtrair"])
        self.comboModo.currentTextChanged.connect(self._atualizar_previsao)
        form.addRow("Modo:", self.comboModo)

        self.spinQuantidade = QSpinBox(self)
        self.spinQuantidade.setRange(0, 999999)
        self.spinQuantidade.setValue(self._quantidade_atual)
        self.spinQuantidade.valueChanged.connect(self._atualizar_previsao)
        form.addRow("Quantidade:", self.spinQuantidade)

        layout.addLayout(form)

        self.lblResultadoTitulo = QLabel("Estoque previsto:", self)
        self.lblResultadoTitulo.setStyleSheet("font-weight:bold;color:#46627d;")
        layout.addWidget(self.lblResultadoTitulo)

        self.lblResultado = QLabel(str(self._quantidade_atual), self)
        self.lblResultado.setStyleSheet("font-size:16px;font-weight:bold;color:#1a5fa0;")
        layout.addWidget(self.lblResultado)

        self.lblImpacto = QLabel("", self)
        self.lblImpacto.setStyleSheet("font-size:11px;color:#46627d;")
        self.lblImpacto.setWordWrap(True)
        layout.addWidget(self.lblImpacto)

        self.textObservacao = QPlainTextEdit(self)
        self.textObservacao.setMaximumBlockCount(6)
        self.textObservacao.setPlaceholderText("Observacao (opcional)")
        layout.addWidget(self.textObservacao)

        botoesLayout = QHBoxLayout()
        botoesLayout.addStretch()
        self.btnCancelar = QPushButton("Cancelar", self)
        self.btnCancelar.setStyleSheet(
            "QPushButton { background-color: #e8eef5; color: #274764; border: 1px solid #c5d6e4; border-radius: 6px; padding: 8px 20px; font-weight: bold; }"
        )
        self.btnCancelar.clicked.connect(self.reject)
        botoesLayout.addWidget(self.btnCancelar)

        self.btnSalvar = QPushButton("Aplicar Ajuste", self)
        self.btnSalvar.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3585c8, stop:1 #1a5fa0); color: white; border: none; border-radius: 6px; padding: 8px 20px; font-weight: bold; }"
            "QPushButton:hover { background: #2a74b8; }"
        )
        self.btnSalvar.clicked.connect(self._aplicar_ajuste)
        botoesLayout.addWidget(self.btnSalvar)
        layout.addLayout(botoesLayout)

        self._atualizar_previsao()

    def _saldo_previsto(self) -> int:
        quantidade = int(self.spinQuantidade.value())
        modo = self.comboModo.currentText().lower()
        if modo == "definir":
            return quantidade
        if modo == "somar":
            return self._quantidade_atual + quantidade
        return self._quantidade_atual - quantidade

    def _atualizar_previsao(self) -> None:
        saldo = self._saldo_previsto()
        self.lblResultado.setText(str(saldo))
        if saldo < 0:
            self.lblResultado.setStyleSheet("font-size:16px;font-weight:bold;color:#cc2222;")
        else:
            self.lblResultado.setStyleSheet("font-size:16px;font-weight:bold;color:#1a5fa0;")

        diferenca = saldo - self._quantidade_atual
        itens = KitService.listar_itens(self._kit_id)
        if diferenca > 0:
            self.lblImpacto.setText(
                f"Estoque dos componentes sera REDUZIDO em {diferenca} unidade(s) de cada item."
            )
            self.lblImpacto.setStyleSheet("font-size:11px;color:#e67e22;")
        elif diferenca < 0:
            self.lblImpacto.setText(
                f"Estoque dos componentes sera AUMENTADO em {abs(diferenca)} unidade(s) de cada item."
            )
            self.lblImpacto.setStyleSheet("font-size:11px;color:#27ae60;")
        else:
            self.lblImpacto.setText("Nenhuma alteração nos componentes.")
            self.lblImpacto.setStyleSheet("font-size:11px;color:#46627d;")

    def _aplicar_ajuste(self) -> None:
        novo_estoque = self._saldo_previsto()
        if novo_estoque < 0:
            mostrar_aviso(self, "Estoque invalido", "O estoque nao pode ser negativo.")
            return

        sucesso, mensagem = KitService.ajustar_estoque(
            kit_id=self._kit_id,
            quantidade_atual=self._quantidade_atual,
            nova_quantidade=novo_estoque,
            observacao=self.textObservacao.toPlainText().strip(),
        )
        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
        else:
            mostrar_aviso(self, "Ajuste nao realizado", mensagem)
