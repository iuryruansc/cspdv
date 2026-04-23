from __future__ import annotations

from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from utils.ui_messages import mostrar_aviso


class ConfirmarFechamentoCaixaDialog(QDialog):
    def __init__(
        self,
        *,
        total_esperado: float,
        valor_contado: float,
        diferenca: float,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Fechamento")
        self.setModal(True)
        self.resize(460, 260)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #eef4fa;
            }
            QLabel {
                background-color: transparent;
                color: #17324d;
                font-size: 12px;
            }
            QLineEdit {
                background-color: white;
                color: #17324d;
                border: 1px solid #b8cee0;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3585c8;
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

        self._diferenca = diferenca
        self.admin_password = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.lblTitulo = QLabel("Confirme os dados do fechamento do caixa", self)
        self.lblTitulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #163a59;")
        layout.addWidget(self.lblTitulo)

        summary_card = QFrame(self)
        summary_card.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #d5e2ee; border-radius: 12px;"
        )
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(16, 14, 16, 14)
        summary_layout.setSpacing(10)

        form_container = QWidget(summary_card)
        form_container.setStyleSheet("background-color: transparent;")
        form = QFormLayout(form_container)
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(22)
        form.setVerticalSpacing(10)

        label_total = QLabel("Total esperado:", summary_card)
        label_total.setStyleSheet("color: #5f7891; font-size: 12px; font-weight: bold;")
        value_total = QLabel(self._formatar_moeda(total_esperado), summary_card)
        value_total.setStyleSheet("color: #17324d; font-size: 13px; font-weight: bold;")
        form.addRow(label_total, value_total)

        label_contado = QLabel("Valor contado:", summary_card)
        label_contado.setStyleSheet("color: #5f7891; font-size: 12px; font-weight: bold;")
        value_contado = QLabel(self._formatar_moeda(valor_contado), summary_card)
        value_contado.setStyleSheet("color: #17324d; font-size: 13px; font-weight: bold;")
        form.addRow(label_contado, value_contado)

        label_diff = QLabel("Diferenca:", summary_card)
        label_diff.setStyleSheet("color: #5f7891; font-size: 12px; font-weight: bold;")
        label_diferenca = QLabel(self._formatar_moeda(diferenca), summary_card)
        cor = "#2f9e44" if abs(diferenca) < 0.009 else "#d94841"
        label_diferenca.setStyleSheet(f"color: {cor}; font-size: 15px; font-weight: bold;")
        form.addRow(label_diff, label_diferenca)

        summary_layout.addWidget(form_container)
        layout.addWidget(summary_card)

        self.lblAviso = QLabel("", self)
        self.lblAviso.setWordWrap(True)
        layout.addWidget(self.lblAviso)

        self.lineSenhaAdmin = QLineEdit(self)
        self.lineSenhaAdmin.setEchoMode(QLineEdit.Password)
        self.lineSenhaAdmin.setPlaceholderText("Senha do administrador")
        self.lineSenhaAdmin.setVisible(False)
        layout.addWidget(self.lineSenhaAdmin)

        botoes = QHBoxLayout()
        botoes.addStretch(1)
        self.btnCancelar = QPushButton("Cancelar", self)
        self.btnConfirmar = QPushButton("Confirmar fechamento", self)
        self.btnCancelar.setStyleSheet(
            """
            QPushButton {
                background-color: #e8eef5;
                color: #274764;
                border: 1px solid #c5d6e4;
            }
            QPushButton:hover {
                background-color: #dce7f1;
            }
            """
        )
        self.btnConfirmar.setStyleSheet(
            """
            QPushButton {
                background-color: #2f78bd;
                color: white;
                border: 1px solid #2869a5;
            }
            QPushButton:hover {
                background-color: #2769a8;
            }
            """
        )
        self.btnConfirmar.setDefault(True)
        botoes.addWidget(self.btnCancelar)
        botoes.addWidget(self.btnConfirmar)
        layout.addLayout(botoes)

        self.btnCancelar.clicked.connect(self.reject)
        self.btnConfirmar.clicked.connect(self._confirmar)

        if abs(diferenca) > 0.009:
            self.lblAviso.setText(
                "Ha diferenca entre o valor esperado e o valor contado. "
                "O fechamento so pode ser concluido mediante a senha de um administrador."
            )
            self.lblAviso.setStyleSheet(
                "color: #c0392b; font-size: 12px; font-weight: bold; "
                "background-color: #fff1ef; border: 1px solid #f2c4bc; border-radius: 8px; padding: 10px 12px;"
            )
            self.lineSenhaAdmin.setVisible(True)
        else:
            self.lblAviso.setText("Os valores estao conciliados. Voce pode confirmar o fechamento.")
            self.lblAviso.setStyleSheet(
                "color: #2f8f3d; font-size: 12px; font-weight: bold; "
                "background-color: #edf9f0; border: 1px solid #c7e8cf; border-radius: 8px; padding: 10px 12px;"
            )

    def _confirmar(self) -> None:
        if abs(self._diferenca) > 0.009 and not self.lineSenhaAdmin.text().strip():
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


class FechamentoRealizadoDialog(QDialog):
    def __init__(self, mensagem: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Caixa fechado")
        self.setModal(True)
        self.resize(420, 170)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #eef4fa;
            }
            QLabel {
                background-color: transparent;
                color: #17324d;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #d5e2ee;
                border-radius: 12px;
            }
            QPushButton {
                min-width: 120px;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
                background-color: #2f78bd;
                color: white;
                border: 1px solid #2869a5;
            }
            QPushButton:hover {
                background-color: #2769a8;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        titulo = QLabel("Caixa fechado com sucesso", self)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #163a59;")
        layout.addWidget(titulo)

        card = QFrame(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(8)

        descricao = QLabel(mensagem, card)
        descricao.setWordWrap(True)
        descricao.setStyleSheet("font-size: 13px; color: #31506b;")
        card_layout.addWidget(descricao)
        layout.addWidget(card)

        botoes = QHBoxLayout()
        botoes.addStretch(1)
        botao_ok = QPushButton("OK", self)
        botao_ok.clicked.connect(self.accept)
        botoes.addWidget(botao_ok)
        layout.addLayout(botoes)
