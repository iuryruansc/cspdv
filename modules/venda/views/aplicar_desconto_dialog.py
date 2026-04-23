from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from utils.ui_messages import mostrar_aviso


class AplicarDescontoDialog(QDialog):
    def __init__(self, *, item_disponivel: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aplicar desconto")
        self.setModal(True)
        self.resize(420, 220)
        self.resultado: Optional[dict] = None

        self.setStyleSheet(
            """
            QDialog { background-color: #eef4fa; }
            QLabel { color: #17324d; font-size: 12px; background: transparent; }
            QComboBox, QDoubleSpinBox {
                background: white;
                color: #17324d;
                border: 1px solid #b8cee0;
                border-radius: 8px;
                padding: 7px 10px;
                font-size: 12px;
            }
            QPushButton {
                min-width: 110px;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("Escolha onde e como o desconto sera aplicado", self)
        titulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #163a59;")
        layout.addWidget(titulo)

        self.comboModo = QComboBox(self)
        self.comboModo.addItem("Venda inteira", "venda")
        self.comboModo.addItem("Item selecionado", "item")
        if item_disponivel:
            self.comboModo.setCurrentIndex(1)
        layout.addLayout(self._linha("Aplicar em", self.comboModo))

        self.comboAcao = QComboBox(self)
        self.comboAcao.addItem("Aplicar desconto", "aplicar")
        self.comboAcao.addItem("Remover desconto", "remover")
        layout.addLayout(self._linha("Acao", self.comboAcao))

        self.comboTipo = QComboBox(self)
        self.comboTipo.addItem("Valor (R$)", "valor")
        self.comboTipo.addItem("Percentual (%)", "percentual")
        layout.addLayout(self._linha("Tipo", self.comboTipo))

        self.spinValor = QDoubleSpinBox(self)
        self.spinValor.setDecimals(2)
        self.spinValor.setRange(0.01, 999999.99)
        self.spinValor.setValue(1.0)
        layout.addLayout(self._linha("Desconto", self.spinValor))

        self.lblAjuda = QLabel(
            "No modo global, o desconto reduz apenas o total da venda nesta etapa inicial.",
            self,
        )
        self.lblAjuda.setWordWrap(True)
        self.lblAjuda.setStyleSheet("color: #5f7891;")
        layout.addWidget(self.lblAjuda)

        botoes = QHBoxLayout()
        botoes.addStretch(1)
        self.btnCancelar = QPushButton("Cancelar", self)
        self.btnAplicar = QPushButton("Aplicar desconto", self)
        self.btnCancelar.setStyleSheet(
            "QPushButton { background-color: #e8eef5; color: #274764; border: 1px solid #c5d6e4; }"
        )
        self.btnAplicar.setStyleSheet(
            "QPushButton { background-color: #2f78bd; color: white; border: 1px solid #2869a5; }"
        )
        self.btnCancelar.clicked.connect(self.reject)
        self.btnAplicar.clicked.connect(self._confirmar)
        self.comboAcao.currentIndexChanged.connect(self._atualizar_estado_formulario)
        botoes.addWidget(self.btnCancelar)
        botoes.addWidget(self.btnAplicar)
        layout.addLayout(botoes)
        self._atualizar_estado_formulario()

    def _linha(self, texto: str, widget) -> QHBoxLayout:
        linha = QHBoxLayout()
        linha.setSpacing(10)
        label = QLabel(texto, self)
        label.setMinimumWidth(90)
        linha.addWidget(label)
        linha.addWidget(widget, 1)
        return linha

    def _confirmar(self) -> None:
        acao = str(self.comboAcao.currentData())
        if acao == "remover":
            self.resultado = {
                "modo": str(self.comboModo.currentData()),
                "acao": acao,
                "tipo": str(self.comboTipo.currentData()),
                "valor": 0.0,
            }
            self.accept()
            return

        valor = float(self.spinValor.value())
        if valor <= 0:
            mostrar_aviso(self, "Desconto invalido", "Informe um desconto maior que zero.")
            return

        self.resultado = {
            "modo": str(self.comboModo.currentData()),
            "acao": acao,
            "tipo": str(self.comboTipo.currentData()),
            "valor": valor,
        }
        self.accept()

    def _atualizar_estado_formulario(self) -> None:
        remover = str(self.comboAcao.currentData()) == "remover"
        self.comboTipo.setEnabled(not remover)
        self.spinValor.setEnabled(not remover)
        self.lblAjuda.setText(
            "No modo global, o desconto reduz apenas o total da venda nesta etapa inicial."
            if not remover
            else "A remocao limpa o desconto do item selecionado ou o desconto global da venda."
        )
        self.btnAplicar.setText("Remover desconto" if remover else "Aplicar desconto")
