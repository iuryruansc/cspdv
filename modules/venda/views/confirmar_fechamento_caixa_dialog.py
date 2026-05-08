from __future__ import annotations

from PyQt5.QtWidgets import QDialog
from ui.venda.confirmar_fechamento_caixa_dialog import (
    Ui_ConfirmarFechamentoCaixaDialog,
    Ui_FechamentoRealizadoDialog,
)
from utils.ui_messages import mostrar_aviso

class ConfirmarFechamentoCaixaDialog(QDialog, Ui_ConfirmarFechamentoCaixaDialog):
    def __init__(
        self,
        *,
        total_esperado: float,
        valor_contado: float,
        diferenca: float,
        exigir_admin_diferenca: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self._diferenca = diferenca
        self._exigir_admin_diferenca = exigir_admin_diferenca
        self.admin_password = ""
        cor = "#2f9e44" if abs(diferenca) < 0.009 else "#d94841"
        self.valueTotal.setText(self._formatar_moeda(total_esperado))
        self.valueContado.setText(self._formatar_moeda(valor_contado))
        self.valueDiferenca.setText(self._formatar_moeda(diferenca))
        self.valueDiferenca.setStyleSheet(f"color: {cor}; font-size: 15px; font-weight: bold;")
        self.lineSenhaAdmin.setEchoMode(self.lineSenhaAdmin.Password)
        self.btnConfirmar.setDefault(True)
        self.btnCancelar.clicked.connect(self.reject)
        self.btnConfirmar.clicked.connect(self._confirmar)

        if abs(diferenca) > 0.009 and self._exigir_admin_diferenca:
            self.lblAviso.setText(
                "Ha diferenca entre o valor esperado e o valor contado. "
                "O fechamento so pode ser concluido mediante a senha de um administrador."
            )
            self.lblAviso.setStyleSheet(
                "color: #c0392b; font-size: 12px; font-weight: bold; "
                "background-color: #fff1ef; border: 1px solid #f2c4bc; border-radius: 8px; padding: 10px 12px;"
            )
            self.lineSenhaAdmin.setVisible(True)
        elif abs(diferenca) > 0.009:
            self.lblAviso.setText(
                "Ha diferenca entre o valor esperado e o valor contado. "
                "Pela configuracao atual, o fechamento pode continuar sem autorizacao administrativa."
            )
            self.lblAviso.setStyleSheet(
                "color: #9a6700; font-size: 12px; font-weight: bold; "
                "background-color: #fff7e6; border: 1px solid #f2d09b; border-radius: 8px; padding: 10px 12px;"
            )
            self.lineSenhaAdmin.setVisible(False)
        else:
            self.lblAviso.setText("Os valores estao conciliados. Voce pode confirmar o fechamento.")
            self.lblAviso.setStyleSheet(
                "color: #2f8f3d; font-size: 12px; font-weight: bold; "
                "background-color: #edf9f0; border: 1px solid #c7e8cf; border-radius: 8px; padding: 10px 12px;"
            )
            self.lineSenhaAdmin.setVisible(False)

    def _confirmar(self) -> None:
        if (
            self._exigir_admin_diferenca
            and abs(self._diferenca) > 0.009
            and not self.lineSenhaAdmin.text().strip()
        ):
            mostrar_aviso(
                self,
                "Autorizacao necessaria",
                "Informe a senha do administrador para concluir o fechamento com diferenca.",
            )
            self.lineSenhaAdmin.setFocus()
            return

        self.admin_password = self.lineSenhaAdmin.text().strip()
        self.accept()

    @staticmethod
    def _formatar_moeda(valor: float) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

class FechamentoRealizadoDialog(QDialog, Ui_FechamentoRealizadoDialog):
    def __init__(self, mensagem: str, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.lblMensagem.setText(mensagem)
        self.btnOk.clicked.connect(self.accept)
