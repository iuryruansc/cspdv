from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtWidgets import QDialog, QPlainTextEdit, QPushButton

from ui.venda.tela_cupom_nao_fiscal import Ui_CupomNaoFiscal
from utils.format_utils import formatar_inteiro, formatar_moeda


class PosPagamentoDialog(QDialog, Ui_CupomNaoFiscal):
    textCupom: QPlainTextEdit
    btnImprimir: QPushButton
    btnSair: QPushButton
    btnFechar: QPushButton

    def __init__(self, *, venda_data: Dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.resultado = "sair"
        self._venda_data = venda_data
        self._configurar_interface()
        self._preencher_cupom()

    def _configurar_interface(self) -> None:
        self.resize(540, 700)
        self.setMinimumSize(520, 680)
        self.setWindowTitle("CSPdv - Pós-pagamento")
        self.lblTitulo.setText("Pós-pagamento")
        self.btnImprimir.clicked.disconnect()
        self.btnSair.clicked.disconnect()
        self.btnFechar.clicked.disconnect()

        self.btnImprimir.setText("Imprimir Cupom")
        self.btnImprimir.setMinimumWidth(150)
        self.btnImprimir.clicked.connect(self._acao_imprimir)

        self.btnSair.setText("Sair")
        self.btnSair.setMinimumWidth(120)
        self.btnSair.clicked.connect(self._acao_sair)

        self.btnFechar.setText("x")
        self.btnFechar.clicked.connect(self._acao_sair)

        self.btnFinalizarSemImpressao = QPushButton("Finalizar sem impressão", self.frameConteudo)
        self.btnFinalizarSemImpressao.setMinimumSize(210, 36)
        self.btnFinalizarSemImpressao.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                 stop:0 #eef8ee, stop:1 #d6efd6);
                border: 1px solid #79ad79;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                color: #245224;
                padding: 4px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                 stop:0 #e0f4e0, stop:1 #c0e6c0);
                border-color: #4c914c;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                 stop:0 #c8e6c8, stop:1 #a8d6a8);
            }
            """
        )
        self.btnFinalizarSemImpressao.clicked.connect(self._acao_sem_impressao)
        self.botoesHLayout.insertWidget(2, self.btnFinalizarSemImpressao)

    def _preencher_cupom(self) -> None:
        self.textCupom.setPlainText(self._montar_texto_cupom())

    def _montar_texto_cupom(self) -> str:
        itens: List[Dict[str, Any]] = list(self._venda_data.get("itens") or [])
        pagamentos: List[Dict[str, Any]] = list(self._venda_data.get("pagamentos") or [])
        linhas = [
            "********* DOCUMENTO NAO FISCAL *********",
            "                CSPdv",
            "          COMPROVANTE DE VENDA",
            "",
            f"Venda: {self._venda_data.get('numero_venda', '---')}",
            f"Data/Hora: {self._venda_data.get('data_hora_venda', '--/--/---- --:--:--')}",
            f"Cliente: {self._venda_data.get('cliente_nome', 'Consumidor Final')}",
            "",
            "-" * 40,
            "ITENS",
            "-" * 40,
        ]
        for item in itens:
            nome = str(item.get("nome") or "")[:24]
            qtd = formatar_inteiro(item.get("quantidade") or 0)
            subtotal = formatar_moeda(item.get("total") or 0.0)
            linhas.append(f"{nome}")
            linhas.append(f"Qtd: {qtd}    Subtotal: {subtotal}")
            linhas.append("")

        linhas.extend(
            [
                "-" * 40,
                f"Subtotal: {formatar_moeda(self._venda_data.get('subtotal') or 0.0)}",
                f"Desconto: {formatar_moeda(self._venda_data.get('desconto_total') or 0.0)}",
                f"Total:    {formatar_moeda(self._venda_data.get('total') or 0.0)}",
                "-" * 40,
                "PAGAMENTOS",
                "-" * 40,
            ]
        )
        for pagamento in pagamentos:
            linhas.append(
                f"{pagamento.get('forma', '-'):20} {formatar_moeda(pagamento.get('valor') or 0.0)}"
            )
        linhas.extend(
            [
                "-" * 40,
                f"Troco: {formatar_moeda(self._venda_data.get('troco') or 0.0)}",
                "",
                "Obrigado pela preferencia.",
            ]
        )
        return "\n".join(linhas)

    def _acao_imprimir(self) -> None:
        self.resultado = "imprimir"
        self.accept()

    def _acao_sem_impressao(self) -> None:
        self.resultado = "sem_impressao"
        self.accept()

    def _acao_sair(self) -> None:
        self.resultado = "sair"
        self.reject()
