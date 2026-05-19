from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtCore import QDateTime, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QWidget,
)

from modules.admin.services.configuracoes_service import ConfiguracoesService
from modules.venda.services.caixa_service import CaixaService
from modules.venda.views.confirmar_fechamento_caixa_dialog import (
    ConfirmarFechamentoCaixaDialog,
    FechamentoRealizadoDialog,
)
from ui.venda.tela_fechamento_caixa import Ui_TelaFechamentoCaixa
from utils.format_utils import aplicar_mascara_monetaria
from utils.table_widget_utils import set_table_item
from utils.ui_messages import mostrar_aviso

class FechamentoCaixaView(QWidget, Ui_TelaFechamentoCaixa):
    caixa_fechado = pyqtSignal(dict)

    lblHDataHora: QLabel
    lblCardVendasValor: QLabel
    lblCardVendasTotalValor: QLabel
    lblCardFundoValor: QLabel
    lblCardDifValor: QLabel
    lblFundoInicialValor: QLabel
    lblTotalSangriaValor: QLabel
    lblTotalSupValor: QLabel
    lblFaturamentoValor: QLabel
    lblTotalEspValor: QLabel
    lblStatus: QLabel
    lblStatusCaixaAberto: QLabel
    lineEditValorContado: QLineEdit
    plainTextObs: QPlainTextEdit
    btnFecharCaixa: QPushButton
    tableTotaisPgto: QTableWidget

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._resumo: Dict[str, Any] = {}
        self._ultimo_total_esperado = 0.0
        self._configurar_formulario()
        self._atualizar_data_hora()
        self._carregar_resumo()

        self.timer_data_hora = QTimer(self)
        self.timer_data_hora.timeout.connect(self._atualizar_data_hora)
        self.timer_data_hora.start(1000)

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self._carregar_resumo()

    def _configurar_formulario(self) -> None:
        aplicar_mascara_monetaria(self.lineEditValorContado)
        self.lineEditValorContado.setText("0,00")
        self.btnFecharCaixa.clicked.connect(self._confirmar_fechamento)
        self.cardFundoCaixa.hide()
        self.cardDiferenca.hide()
        self.frameTotalEsperado.hide()
        self.lblStatusCaixaAberto.setText("● Caixa aberto")
        self._aplicar_status_caixa("#78dd8b")

    def _atualizar_data_hora(self) -> None:
        self.lblHDataHora.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm"))

    def _carregar_resumo(self) -> None:
        self._resumo = CaixaService.obter_resumo_fechamento()
        total_esperado = float(self._resumo["total_esperado"])
        self.lblCardVendasValor.setText(str(int(self._resumo["vendas_dia"])))
        self.lblCardVendasTotalValor.setText(self._formatar_moeda(float(self._resumo["faturamento_total"])))
        self.lblCardFundoValor.setText(self._formatar_moeda(total_esperado))
        self.lblFundoInicialValor.setText(self._formatar_moeda(float(self._resumo["fundo_inicial"])))
        self.lblTotalSangriaValor.setText(f"- {self._formatar_moeda(float(self._resumo['total_sangrias']))}")
        self.lblTotalSupValor.setText(f"+ {self._formatar_moeda(float(self._resumo['total_suprimentos']))}")
        self.lblFaturamentoValor.setText(f"+ {self._formatar_moeda(float(self._resumo['faturamento_dinheiro']))}")
        self.lblTotalEspValor.setText(self._formatar_moeda(total_esperado))
        self._ultimo_total_esperado = total_esperado
        self._popular_totais_pagamento(self._resumo.get("totais_forma_pagamento", []))

    def _popular_totais_pagamento(self, totais: List[Dict[str, Any]]) -> None:
        self.tableTotaisPgto.setRowCount(len(totais))
        for row_index, row in enumerate(totais):
            valores = (
                str(row.get("forma_pagamento") or "-"),
                str(row.get("qtd_vendas") or "0"),
                self._formatar_moeda(float(row.get("total") or 0.0)),
            )
            for col_index, valor in enumerate(valores):
                set_table_item(self.tableTotaisPgto, row_index, col_index, valor)

    def _valor_contado(self) -> float:
        texto = self.lineEditValorContado.text().strip().replace(".", "").replace(",", ".")
        if not texto:
            return 0.0
        return float(texto)

    def _confirmar_fechamento(self) -> None:
        valor_contado = self._valor_contado()
        total_esperado = float(self._resumo.get("total_esperado") or 0.0)
        diferenca = round(valor_contado - total_esperado, 2)
        parametros_caixa = ConfiguracoesService.carregar_parametros_caixa()

        dialog = ConfirmarFechamentoCaixaDialog(
            total_esperado=total_esperado,
            valor_contado=valor_contado,
            diferenca=diferenca,
            exigir_admin_diferenca=bool(parametros_caixa.get("exigir_admin_diferenca_fechamento", True)),
            parent=self,
        )
        if dialog.exec_() != dialog.Accepted:
            return

        sucesso, mensagem, fechamento = CaixaService.fechar_caixa(
            valor_contado=valor_contado,
            observacoes=self.plainTextObs.toPlainText().strip(),
            admin_password=dialog.admin_password,
        )
        if not sucesso or fechamento is None:
            mostrar_aviso(self, "Fechamento não realizado", mensagem)
            return

        self.lblStatus.setText(
            f"CSPdv | Caixa fechado com valor contado {self._formatar_moeda(float(fechamento['valor_contado']))}"
        )
        self.lblStatusCaixaAberto.setText("● Caixa fechado")
        self._aplicar_status_caixa("#72d88f")
        self.btnFecharCaixa.setEnabled(False)
        self.lineEditValorContado.setEnabled(False)
        self.plainTextObs.setEnabled(False)
        self.caixa_fechado.emit(fechamento)
        FechamentoRealizadoDialog(mensagem, self).exec_()

    @staticmethod
    def _formatar_moeda(valor: float) -> str:
        sinal = "-" if valor < 0 else ""
        absoluto = abs(valor)
        texto = f"{absoluto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{sinal}R$ {texto}"

    def _aplicar_status_caixa(self, cor: str) -> None:
        self.lblStatusCaixaAberto.setStyleSheet(f"color:{cor};font-size:11px;font-weight:bold;")
