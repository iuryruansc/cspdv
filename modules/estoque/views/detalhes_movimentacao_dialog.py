from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QPlainTextEdit, QVBoxLayout

from utils.format_utils import formatar_data_hora, formatar_inteiro


class DetalhesMovimentacaoDialog(QDialog):
    def __init__(self, movimentacao: dict[str, Any], tipo_formatado: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalhes da Movimentação")
        self.setMinimumWidth(440)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        titulo = QLabel("Detalhes da Movimentação", self)
        titulo.setStyleSheet("font-size:16px;font-weight:bold;color:#153552;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._adicionar_valor(form, "Produto:", movimentacao.get("produto") or "-")
        self._adicionar_valor(form, "Tipo:", tipo_formatado)
        self._adicionar_valor(form, "Quantidade:", formatar_inteiro(movimentacao.get("quantidade")))
        self._adicionar_valor(form, "Data da movimentação:", formatar_data_hora(movimentacao.get("data_hora")))
        self._adicionar_valor(form, "Usuário:", movimentacao.get("usuario") or "-")
        layout.addLayout(form)

        motivo = QPlainTextEdit(self)
        motivo.setReadOnly(True)
        motivo.setMaximumHeight(90)
        motivo.setPlainText(str(movimentacao.get("observacao") or "Não informado"))
        layout.addWidget(QLabel("Motivo:", self))
        layout.addWidget(motivo)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok, parent=self)
        botoes.accepted.connect(self.accept)
        layout.addWidget(botoes)

    @staticmethod
    def _adicionar_valor(form: QFormLayout, rotulo: str, valor: Any) -> None:
        label = QLabel(str(valor), form.parentWidget())
        label.setWordWrap(True)
        label.setStyleSheet("color:#18324a;font-weight:600;")
        form.addRow(rotulo, label)
