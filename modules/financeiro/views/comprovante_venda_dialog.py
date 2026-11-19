from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QTextDocument
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QFileDialog, QDialog, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout

from modules.financeiro.services.financeiro_service import FinanceiroService
from utils.format_utils import formatar_data_hora, formatar_moeda
from utils.ui_messages import mostrar_aviso, mostrar_info


class ComprovanteVendaDialog(QDialog):
    def __init__(self, *, detalhes: dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self._detalhes = detalhes
        self._venda = dict(detalhes.get("venda") or {})
        self._conta_detalhada: dict[str, Any] = {}
        self._carregar_conta_atualizada()
        self._montar_interface()

    def _carregar_conta_atualizada(self) -> None:
        conta_id = self._detalhes.get("conta_receber_id")
        if not conta_id:
            return
        try:
            self._conta_detalhada = FinanceiroService.obter_conta_receber_detalhada(int(conta_id)) or {}
        except Exception:
            self._conta_detalhada = {}

    def _montar_interface(self) -> None:
        self.setWindowTitle("Comprovante da Venda")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(650, 680)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        titulo = QLabel("Comprovante da Venda", self)
        titulo.setStyleSheet("font-size:18px;font-weight:700;color:#14324c;")
        layout.addWidget(titulo)
        subtitulo = QLabel("Resumo da venda, pagamentos e saldo atualizado.", self)
        subtitulo.setStyleSheet("font-size:11px;color:#4d6f8e;")
        layout.addWidget(subtitulo)

        self.textComprovante = QPlainTextEdit(self)
        self.textComprovante.setReadOnly(True)
        self.textComprovante.setPlainText(self._montar_texto())
        self.textComprovante.setStyleSheet(
            "QPlainTextEdit { background:#fff; color:#14324c; border:1px solid #b9d0e3; "
            "border-radius:10px; font-family:Consolas, 'Courier New', monospace; "
            "font-size:12px; padding:8px; }"
        )
        layout.addWidget(self.textComprovante, 1)

        botoes = QHBoxLayout()
        botoes.addStretch(1)
        self.btnImprimir = QPushButton("Imprimir", self)
        self.btnImprimir.clicked.connect(self._imprimir)
        botoes.addWidget(self.btnImprimir)
        self.btnSalvar = QPushButton("Salvar comprovante", self)
        self.btnSalvar.clicked.connect(self._salvar)
        botoes.addWidget(self.btnSalvar)
        self.btnCopiar = QPushButton("Copiar", self)
        self.btnCopiar.clicked.connect(self._copiar)
        botoes.addWidget(self.btnCopiar)
        self.btnFechar = QPushButton("Fechar", self)
        self.btnFechar.clicked.connect(self.accept)
        botoes.addWidget(self.btnFechar)
        layout.addLayout(botoes)

    def _montar_texto(self) -> str:
        venda_id = int(self._venda.get("id") or 0)
        cliente = str(self._venda.get("cliente") or "Consumidor Final")
        operador = str(self._venda.get("operador") or "-")
        total = float(self._venda.get("valor_total") or 0)
        pagamentos = list(self._detalhes.get("pagamentos") or [])
        recebimentos = list(self._conta_detalhada.get("recebimentos") or [])
        if recebimentos:
            pagamentos = recebimentos

        valor_pago = sum(float(item.get("valor_pago") or item.get("valor_recebido") or 0) for item in pagamentos)
        valor_pago = max(0.0, valor_pago)
        saldo = max(0.0, total - valor_pago)
        data_venda = formatar_data_hora(self._venda.get("data_hora")) if self._venda.get("data_hora") else "-"

        linhas = [
            "*************** COMPROVANTE DE VENDA ***************",
            "                         CSPdv",
            "",
            f"Venda     : #{venda_id}",
            f"Data/Hora : {data_venda}",
            f"Cliente   : {cliente}",
            f"Operador  : {operador}",
            "-" * 54,
            "ITENS DA VENDA",
        ]
        for item in self._detalhes.get("itens") or []:
            nome = str(item.get("produto") or "-")[:28]
            qtd = int(item.get("quantidade") or 0)
            total_item = formatar_moeda(item.get("total_item") or 0)
            linhas.append(f"{qtd:>3} x {nome:<28} {total_item:>12}")

        linhas.extend([
            "-" * 54,
            f"Valor total : {formatar_moeda(total)}",
            "",
            "PAGAMENTOS",
        ])
        if pagamentos:
            for item in pagamentos:
                forma = str(item.get("forma_pagamento") or item.get("forma") or "-")
                valor = item.get("valor_pago") or item.get("valor_recebido") or item.get("valor") or 0
                data = item.get("data_pagamento") or item.get("data_recebimento")
                data_formatada = formatar_data_hora(data) if data else "-"
                linhas.append(f"{data_formatada:<18} {forma:<18} {formatar_moeda(valor):>12}")
        else:
            linhas.append("Nenhum pagamento registrado")
        linhas.extend([
            "-" * 54,
            f"Total pago  : {formatar_moeda(valor_pago)}",
            f"Saldo aberto: {formatar_moeda(saldo)}",
            f"Status      : {self._venda.get('status') or '-'}",
            "",
            "Comprovante gerado pelo sistema CSPdv.",
        ])
        return "\n".join(linhas)

    def _salvar(self) -> None:
        venda_id = int(self._venda.get("id") or 0)
        caminho, filtro = QFileDialog.getSaveFileName(
            self,
            "Salvar Comprovante",
            f"comprovante_venda_{venda_id}.pdf",
            "PDF (*.pdf);;Arquivo de Texto (*.txt);;Todos os Arquivos (*)",
        )
        if not caminho:
            return
        try:
            caminho_salvo = caminho
            if caminho.lower().endswith(".pdf") or "PDF" in filtro:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                caminho_salvo = caminho if caminho.lower().endswith(".pdf") else f"{caminho}.pdf"
                printer.setOutputFileName(caminho_salvo)
                documento = QTextDocument()
                documento.setPlainText(self.textComprovante.toPlainText())
                documento.print_(printer)
            else:
                with open(caminho, "w", encoding="utf-8") as arquivo:
                    arquivo.write(self.textComprovante.toPlainText())
            mostrar_info(self, "Comprovante salvo", f"O comprovante foi salvo em:\n{caminho_salvo}")
        except Exception as exc:
            mostrar_aviso(self, "Erro ao salvar", f"Não foi possível salvar o comprovante:\n{exc}")

    def _copiar(self) -> None:
        QGuiApplication.clipboard().setText(self.textComprovante.toPlainText())
        mostrar_info(self, "Comprovante copiado", "O conteúdo foi copiado para a área de transferência.")

    def _imprimir(self) -> None:
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != QDialog.Accepted:
            return
        documento = QTextDocument()
        documento.setPlainText(self.textComprovante.toPlainText())
        documento.print_(printer)
