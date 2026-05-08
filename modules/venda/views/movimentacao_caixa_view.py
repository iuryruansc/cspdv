from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtCore import QDateTime, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from modules.admin.services.configuracoes_service import ConfiguracoesService
from modules.venda.services.caixa_service import CaixaService
from ui.venda.tela_movimentacao_caixa import Ui_TelaMovimentacaoCaixa
from utils.format_utils import aplicar_mascara_monetaria
from utils.ui_messages import mostrar_aviso, mostrar_info

class MovimentacaoCaixaView(QWidget, Ui_TelaMovimentacaoCaixa):
    movimentacao_registrada = pyqtSignal()
    lblSaldoValor: QLabel
    lblSaldoAtualValor2: QLabel
    lblTotalSangriaValor: QLabel
    lblTotalSupValor: QLabel
    lblStatus: QLabel
    lblStatusCaixaAberto: QLabel
    lblHSub: QLabel
    lineEditValor: QLineEdit
    lineEditDescricao: QLineEdit
    lineEditSenhaAdmin: QLineEdit
    btnTipoSangria: QPushButton
    btnTipoSuprimento: QPushButton
    btnTipoTroco: QPushButton
    btnRegistrar: QPushButton
    comboFiltroHist: QComboBox
    tableHistorico: QTableWidget

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._grupo_tipos = QButtonGroup(self)
        self._grupo_tipos.setExclusive(True)
        self._grupo_tipos.addButton(self.btnTipoSangria)
        self._grupo_tipos.addButton(self.btnTipoSuprimento)
        self._grupo_tipos.addButton(self.btnTipoTroco)
        self._tipo_atual = "sangria"
        self._parametros_caixa = ConfiguracoesService.carregar_parametros_caixa()

        self._configurar_formulario()
        self._conectar_sinais()
        self._atualizar_data_hora()
        self._recarregar_tela()

        self._timer_data_hora = QTimer(self)
        self._timer_data_hora.setInterval(1000)
        self._timer_data_hora.timeout.connect(self._atualizar_data_hora)
        self._timer_data_hora.start()

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self._parametros_caixa = ConfiguracoesService.carregar_parametros_caixa()
        self._recarregar_tela()

    def _configurar_formulario(self) -> None:
        aplicar_mascara_monetaria(self.lineEditValor)
        self.lineEditValor.setText("0,00")

    def _conectar_sinais(self) -> None:
        self.btnTipoSangria.clicked.connect(lambda: self._definir_tipo("sangria"))
        self.btnTipoSuprimento.clicked.connect(lambda: self._definir_tipo("suprimento"))
        self.btnTipoTroco.clicked.connect(lambda: self._definir_tipo("troco"))
        self.btnRegistrar.clicked.connect(self._registrar_movimentacao)
        self.comboFiltroHist.currentIndexChanged.connect(self._carregar_historico)

    def _atualizar_data_hora(self) -> None:
        self.lblStatus.setText(
            "CSPdv  |  Movimentação de Caixa  |  "
            + QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm:ss")
        )

    def _definir_tipo(self, tipo: str) -> None:
        self._tipo_atual = tipo
        self.btnTipoSangria.setChecked(tipo == "sangria")
        self.btnTipoSuprimento.setChecked(tipo == "suprimento")
        self.btnTipoTroco.setChecked(tipo == "troco")
        self._atualizar_regra_admin()

    def _recarregar_tela(self) -> None:
        self._carregar_resumo()
        self._carregar_historico()
        self.lineEditValor.setText("0,00")
        self.lineEditDescricao.clear()
        self.lineEditSenhaAdmin.clear()
        self._definir_tipo("sangria")

    def _atualizar_regra_admin(self) -> None:
        exigir_admin = self._tipo_atual == "sangria" and bool(
            self._parametros_caixa.get("exigir_admin_sangria", True)
        )
        self.lineEditSenhaAdmin.setEnabled(exigir_admin)
        if exigir_admin:
            self.lineEditSenhaAdmin.setPlaceholderText("Senha do administrador")
        else:
            self.lineEditSenhaAdmin.clear()
            self.lineEditSenhaAdmin.setPlaceholderText("Autorização não exigida para esta operação")

    def _carregar_resumo(self) -> None:
        resumo = CaixaService.obter_resumo_movimentacoes()
        self.lblSaldoValor.setText(self._formatar_moeda(float(resumo.get("saldo_atual") or 0.0)))
        self.lblSaldoAtualValor2.setText(self._formatar_moeda(float(resumo.get("saldo_atual") or 0.0)))
        self.lblTotalSangriaValor.setText(self._formatar_moeda(float(resumo.get("total_sangrias") or 0.0)))
        entradas = float(resumo.get("total_suprimentos") or 0.0) + float(resumo.get("total_troco") or 0.0)
        self.lblTotalSupValor.setText(self._formatar_moeda(entradas))

    def _carregar_historico(self) -> None:
        filtro = self.comboFiltroHist.currentText().strip().lower()
        historico = CaixaService.listar_movimentacoes(filtro)
        self.tableHistorico.setRowCount(len(historico))

        for row_index, row in enumerate(historico):
            valores = (
                str(row.get("hora_fmt") or "-"),
                str(row.get("tipo_descricao") or "-"),
                self._formatar_moeda(float(row.get("valor") or 0.0)),
                str(row.get("operador") or "-"),
                str(row.get("observacao") or "-"),
            )
            for col_index, valor in enumerate(valores):
                item = QTableWidgetItem(valor)
                self.tableHistorico.setItem(row_index, col_index, item)

    def _valor_digitado(self) -> float:
        texto = self.lineEditValor.text().strip().replace(".", "").replace(",", ".")
        if not texto:
            return 0.0
        return float(texto)

    def _registrar_movimentacao(self) -> None:
        sucesso, mensagem = CaixaService.registrar_movimentacao(
            tipo=self._tipo_atual,
            valor=self._valor_digitado(),
            observacao=self.lineEditDescricao.text().strip(),
            admin_password=self.lineEditSenhaAdmin.text().strip(),
        )
        if not sucesso:
            mostrar_aviso(self, "Movimentação não registrada", mensagem)
            return

        mostrar_info(self, "Sucesso", mensagem)
        self._recarregar_tela()
        self.movimentacao_registrada.emit()

    @staticmethod
    def _formatar_moeda(valor: float) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
