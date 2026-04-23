from typing import Dict, Optional

from PyQt5.QtCore import QDateTime, QTimer, pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from core.session_manager import SessionManager
from modules.venda.services.caixa_service import CaixaService
from ui.venda.tela_abertura_caixa import Ui_TelaAberturaCaixa
from utils.format_utils import (
    aplicar_mascara_monetaria,
    formatar_decimal,
    formatar_moeda,
    numero_decimal,
)
from utils.ui_messages import mostrar_aviso


class AberturaCaixaView(QWidget, Ui_TelaAberturaCaixa):
    caixa_aberto = pyqtSignal(dict)

    lblHeaderTitulo: QLabel
    lblHeaderSub: QLabel
    lblHeaderDataHora: QLabel
    lblCardTitulo: QLabel
    lblCardSub: QLabel
    lblOpLabel: QLabel
    lblNumCaixaLabel: QLabel
    lblTrocoLabel: QLabel
    lblTrocoObrig: QLabel
    lblObsLabel: QLabel
    lblBreakdownTitulo: QLabel
    lblBreakdownTotal: QLabel
    lblBreakdownTotalValor: QLabel
    lblHistoricoTitulo: QLabel
    lblStatus: QLabel
    lblStatusCaixaFechado: QLabel
    lineEditOperador: QLineEdit
    lineEditTrocoInicial: QLineEdit
    comboNumCaixa: QComboBox
    plainTextObs: QPlainTextEdit
    btnAbrirCaixa: QPushButton
    frameHistoricoAberturas: QFrame
    tableHistoricoAberturas: QTableWidget
    spinNota100: QSpinBox
    spinNota50: QSpinBox
    spinNota20: QSpinBox
    spinNota10: QSpinBox
    spinNota5: QSpinBox
    spinNota2: QSpinBox

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._pdv_map: Dict[int, Optional[int]] = {}
        self._configurar_formulario()
        self._carregar_contexto_inicial()
        self._carregar_historico()

        self.timer_data_hora = QTimer(self)
        self.timer_data_hora.timeout.connect(self._atualizar_data_hora)
        self.timer_data_hora.start(1000)
        self._atualizar_data_hora()

    def _configurar_formulario(self) -> None:
        aplicar_mascara_monetaria(self.lineEditTrocoInicial)
        self.lineEditTrocoInicial.setText("0,00")

        for spin in (
            self.spinNota100,
            self.spinNota50,
            self.spinNota20,
            self.spinNota10,
            self.spinNota5,
            self.spinNota2,
        ):
            spin.valueChanged.connect(self._atualizar_total_breakdown)

        self.btnAbrirCaixa.clicked.connect(self._abrir_caixa)

        self.tableHistoricoAberturas.setColumnCount(3)
        self.tableHistoricoAberturas.setHorizontalHeaderLabels(["Data", "Operador", "Fundo (R$)"])
        self.tableHistoricoAberturas.verticalHeader().setVisible(False)
        header = self.tableHistoricoAberturas.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def _carregar_contexto_inicial(self) -> None:
        usuario = SessionManager.current_user() or {}
        self.lineEditOperador.setText(str(usuario.get("nome", "")).upper())
        self.lineEditOperador.setReadOnly(True)
        self._popular_pdvs()
        self._atualizar_total_breakdown()

    def _popular_pdvs(self) -> None:
        self.comboNumCaixa.clear()
        self._pdv_map.clear()

        pdvs = CaixaService.listar_pdvs_ativos()
        if not pdvs:
            self.comboNumCaixa.addItem("Nenhum PDV ativo cadastrado")
            self._pdv_map[0] = None
            self.btnAbrirCaixa.setEnabled(False)
            self.lblStatusCaixaFechado.setText("- Cadastre um PDV ativo antes de abrir o caixa")
            return

        self.btnAbrirCaixa.setEnabled(True)
        self.lblStatusCaixaFechado.setText("- Caixa nao iniciado")
        for index, pdv in enumerate(pdvs):
            label = f"{pdv['identificacao']} - {pdv['descricao']}"
            self.comboNumCaixa.addItem(label)
            self._pdv_map[index] = int(pdv["id"])

    def _atualizar_data_hora(self) -> None:
        self.lblHeaderDataHora.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm"))

    def _atualizar_total_breakdown(self) -> None:
        total = (
            self.spinNota100.value() * 100
            + self.spinNota50.value() * 50
            + self.spinNota20.value() * 20
            + self.spinNota10.value() * 10
            + self.spinNota5.value() * 5
            + self.spinNota2.value() * 2
        )
        self.lblBreakdownTotalValor.setText(formatar_moeda(total))

    def _breakdown(self) -> Dict[str, int]:
        return {
            "100": int(self.spinNota100.value()),
            "50": int(self.spinNota50.value()),
            "20": int(self.spinNota20.value()),
            "10": int(self.spinNota10.value()),
            "5": int(self.spinNota5.value()),
            "2": int(self.spinNota2.value()),
        }

    def _valor_abertura(self) -> float:
        return numero_decimal(self.lineEditTrocoInicial.text())

    @staticmethod
    def _to_float(valor: object) -> float:
        return numero_decimal(valor)

    def _abrir_caixa(self) -> None:
        usuario = SessionManager.current_user() or {}
        indice = self.comboNumCaixa.currentIndex()
        pdv_id = self._pdv_map.get(indice)
        valor_abertura = self._valor_abertura()
        breakdown = self._breakdown()
        total_breakdown = (
            breakdown["100"] * 100
            + breakdown["50"] * 50
            + breakdown["20"] * 20
            + breakdown["10"] * 10
            + breakdown["5"] * 5
            + breakdown["2"] * 2
        )

        if pdv_id is None:
            self.lblStatusCaixaFechado.setText("- Selecione um PDV valido antes de abrir o caixa")
            self.lblStatusCaixaFechado.setStyleSheet("color:#ff8a7a;font-size:11px;font-weight:bold;")
            mostrar_aviso(
                self,
                "PDV obrigatorio",
                "Selecione um PDV valido antes de iniciar a abertura do caixa.",
            )
            return

        if any(valor > 0 for valor in breakdown.values()) and round(total_breakdown, 2) != round(valor_abertura, 2):
            self.lblStatusCaixaFechado.setText("- O total da composicao deve bater com o troco inicial")
            self.lblStatusCaixaFechado.setStyleSheet("color:#ff8a7a;font-size:11px;font-weight:bold;")
            mostrar_aviso(
                self,
                "Valores inconsistentes",
                "Quando houver composicao do fundo, o total calculado deve ser igual ao troco inicial informado.",
            )
            return

        sucesso, mensagem, caixa_data = CaixaService.abrir_caixa(
            pdv_id=pdv_id,
            pdv_label=self.comboNumCaixa.currentText(),
            usuario_id=usuario.get("id"),
            usuario_nome=str(usuario.get("nome", "")),
            valor_abertura=valor_abertura,
            observacoes=self.plainTextObs.toPlainText().strip(),
            breakdown=breakdown,
        )

        if not sucesso or caixa_data is None:
            self.lblStatusCaixaFechado.setText("- Falha na abertura do caixa")
            self.lblStatusCaixaFechado.setStyleSheet("color:#ff8a7a;font-size:11px;font-weight:bold;")
            mostrar_aviso(self, "Abertura nao realizada", mensagem)
            return

        self.lblStatus.setText(
            f"CSPdv | Caixa {caixa_data['pdv_label']} aberto com fundo R$ {caixa_data['valor_abertura']:.2f}"
        )
        self.lblStatusCaixaFechado.setText("- Caixa aberto e pronto para operacoes")
        self.lblStatusCaixaFechado.setStyleSheet("color:#72d88f;font-size:11px;font-weight:bold;")
        self.btnAbrirCaixa.setEnabled(False)
        self.comboNumCaixa.setEnabled(False)
        self.lineEditTrocoInicial.setEnabled(False)
        self.plainTextObs.setEnabled(False)
        self.caixa_aberto.emit(caixa_data)
        self._carregar_historico()

    def _carregar_historico(self) -> None:
        registros = CaixaService.listar_ultimas_aberturas()
        self.tableHistoricoAberturas.setRowCount(len(registros))

        for row_index, registro in enumerate(registros):
            valores = [
                registro.get("data_abertura_fmt", ""),
                registro.get("operador", ""),
                formatar_decimal(registro.get("valor_abertura")),
            ]
            for col_index, valor in enumerate(valores):
                self.tableHistoricoAberturas.setItem(row_index, col_index, QTableWidgetItem(str(valor)))

    def preencher_caixa_existente(self, caixa_data: Dict[str, object]) -> None:
        pdv_label = str(caixa_data.get("pdv_label", ""))
        valor_abertura = self._to_float(caixa_data.get("valor_abertura"))
        if pdv_label:
            index = self.comboNumCaixa.findText(pdv_label)
            if index >= 0:
                self.comboNumCaixa.setCurrentIndex(index)

        self.lineEditTrocoInicial.setText(formatar_decimal(valor_abertura))
        self.lblStatus.setText(
            f"CSPdv | Caixa {pdv_label} reaberto com fundo R$ {valor_abertura:.2f}"
        )
        self.lblStatusCaixaFechado.setText("- Caixa aberto e pronto para operacoes")
        self.lblStatusCaixaFechado.setStyleSheet("color:#72d88f;font-size:11px;font-weight:bold;")
        self.btnAbrirCaixa.setEnabled(False)
        self.comboNumCaixa.setEnabled(False)
        self.lineEditTrocoInicial.setEnabled(False)
        self.plainTextObs.setEnabled(False)
