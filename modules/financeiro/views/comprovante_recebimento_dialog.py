from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit, QVBoxLayout

from utils.format_utils import formatar_moeda
from utils.ui_messages import mostrar_info

class ComprovanteRecebimentoDialog(QDialog):
    def __init__(
        self,
        *,
        conta: Dict[str, Any],
        recebimento: Dict[str, Any],
        operador_nome: str,
        caixa_label: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._conta = dict(conta)
        self._recebimento = dict(recebimento)
        self._operador_nome = str(operador_nome or "Operador")
        self._caixa_label = str(caixa_label or "Caixa")
        self._montar_interface()

    def _montar_interface(self) -> None:
        self.setWindowTitle("Comprovante de Recebimento")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(560, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        titulo = QLabel("Comprovante de Recebimento", self)
        titulo.setStyleSheet("font-size:18px;font-weight:700;color:#14324c;")
        layout.addWidget(titulo)

        subtitulo = QLabel(
            "Resumo da baixa registrada em contas a receber.",
            self,
        )
        subtitulo.setStyleSheet("font-size:11px;color:#4d6f8e;")
        layout.addWidget(subtitulo)

        self.textComprovante = QPlainTextEdit(self)
        self.textComprovante.setReadOnly(True)
        self.textComprovante.setPlainText(self._montar_texto_comprovante())
        self.textComprovante.setStyleSheet(
            "QPlainTextEdit {"
            "background-color:#ffffff;"
            "color:#14324c;"
            "border:1px solid #b9d0e3;"
            "border-radius:10px;"
            "font-family:Consolas, 'Courier New', monospace;"
            "font-size:12px;"
            "padding:8px;"
            "}"
        )
        layout.addWidget(self.textComprovante, 1)

        botoes = QHBoxLayout()
        botoes.addStretch(1)
        layout.addLayout(botoes)

        self.btnCopiar = QPushButton("Copiar comprovante", self)
        self.btnCopiar.clicked.connect(self._copiar_comprovante)
        botoes.addWidget(self.btnCopiar)

        self.btnFechar = QPushButton("Fechar", self)
        self.btnFechar.clicked.connect(self.accept)
        botoes.addWidget(self.btnFechar)

    def _montar_texto_comprovante(self) -> str:
        agora = self._recebimento.get("data_recebimento") or datetime.now()
        data_hora = (
            agora.strftime("%d/%m/%Y %H:%M")
            if hasattr(agora, "strftime")
            else str(agora or "-")
        )
        conta_id = int(self._recebimento.get("conta_id") or self._conta.get("id") or 0)
        venda_id = int(self._recebimento.get("venda_id") or self._conta.get("venda_id") or 0)
        cliente = str(self._conta.get("cliente") or "Consumidor Final")
        forma = str(self._recebimento.get("forma_pagamento") or "-")
        valor_recebido = formatar_moeda(self._recebimento.get("valor_recebido") or 0)
        valor_aberto = formatar_moeda(self._recebimento.get("valor_aberto") or 0)
        status = str(self._recebimento.get("status") or self._conta.get("status") or "-")
        observacao = str(self._conta.get("observacao") or self._recebimento.get("observacao") or "-").strip() or "-"

        linhas = [
            "******** COMPROVANTE DE RECEBIMENTO ********",
            "                 CSPdv",
            "",
            f"Data/Hora : {data_hora}",
            f"Operador  : {self._operador_nome}",
            f"Caixa     : {self._caixa_label}",
            "-" * 42,
            f"Conta     : #{conta_id}",
            f"Venda     : #{venda_id}",
            f"Cliente   : {cliente}",
            f"Forma     : {forma}",
            f"Recebido  : {valor_recebido}",
            f"Saldo     : {valor_aberto}",
            f"Status    : {status}",
            f"Observação: {observacao}",
            "-" * 42,
            "Comprovante gerado pelo módulo financeiro.",
        ]
        return "\n".join(linhas)

    def _copiar_comprovante(self) -> None:
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.textComprovante.toPlainText())
        mostrar_info(
            self,
            "Comprovante copiado",
            "O comprovante de recebimento foi copiado para a área de transferência.",
        )
