from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QDialog
from ui.venda.aplicar_desconto_dialog import Ui_AplicarDescontoDialog
from utils.ui_messages import mostrar_aviso


class AplicarDescontoDialog(QDialog, Ui_AplicarDescontoDialog):
    def __init__(self, *, item_disponivel: bool, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.resultado: Optional[dict] = None
        self.comboModo.addItem("Venda inteira", "venda")
        self.comboModo.addItem("Item selecionado", "item")
        if item_disponivel:
            self.comboModo.setCurrentIndex(1)
        self.comboAcao.addItem("Aplicar desconto", "aplicar")
        self.comboAcao.addItem("Remover desconto", "remover")
        self.comboTipo.addItem("Valor (R$)", "valor")
        self.comboTipo.addItem("Percentual (%)", "percentual")
        self.spinValor.setDecimals(2)
        self.spinValor.setRange(0.01, 999999.99)
        self.spinValor.setValue(1.0)
        self.btnCancelar.clicked.connect(self.reject)
        self.btnAplicar.clicked.connect(self._confirmar)
        self.comboAcao.currentIndexChanged.connect(self._atualizar_estado_formulario)
        self._atualizar_estado_formulario()

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
            mostrar_aviso(self, "Desconto inválido", "Informe um desconto maior que zero.")
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
