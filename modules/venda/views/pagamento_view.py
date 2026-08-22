from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QDateTime, QEvent, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QKeyEvent, QKeySequence
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
    QShortcut,
)

from modules.financeiro.services.financeiro_service import FinanceiroService
from modules.venda.views.finalizar_pendencia_dialog import FinalizarPendenciaDialog
from ui.venda.tela_pagamento import Ui_TelaPagamento
from utils.format_utils import formatar_moeda, numero_decimal
from utils.table_widget_utils import set_table_item
from utils.ui_messages import confirmar_acao, mostrar_info
from modules.shared.constants import FLAG_NAO, FLAG_SIM

class PagamentoView(QWidget, Ui_TelaPagamento):
    voltar_venda = pyqtSignal()
    venda_finalizada = pyqtSignal(dict)

    lblNumVendaValor: QLabel
    lblClienteValor: QLabel
    lblTotalHeaderValor: QLabel
    lblValorTotalValor: QLabel
    lblDescontosValor: QLabel
    lblSomaTotalValor: QLabel
    lblRestanteValor: QLabel
    lblTrocoValor: QLabel
    lblStatusDataHora: QLabel
    lineEditValor: QLineEdit
    tableFormasPagamento: QTableWidget
    btnVoltar: QPushButton
    btnDinheiro: QPushButton
    btnPix: QPushButton
    btnCartaoDebito: QPushButton
    btnCartaoCredito: QPushButton
    btnValeRefeicao: QPushButton
    btnCheque: QPushButton
    btn0: QPushButton
    btn1: QPushButton
    btn2: QPushButton
    btn3: QPushButton
    btn4: QPushButton
    btn5: QPushButton
    btn6: QPushButton
    btn7: QPushButton
    btn8: QPushButton
    btn9: QPushButton
    btnVirgula: QPushButton
    btnLimpar: QPushButton
    btnEnter: QPushButton
    btnPagamentoExato: QPushButton
    btnFecharPedido: QPushButton
    btnFinalizarPendencia: QPushButton
    lblStatusPagamento: QLabel
    lblPagamentosVazio: QLabel

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._venda_data: dict[str, Any] | None = None
        self._pagamentos: list[dict[str, Any]] = []
        self._ultima_linha_pagamento: int | None = None
        self._forma_selecionada = ""
        self._formas_pagamento_dados: dict[str, dict[str, Any]] = {}
        self._botoes_forma_ordenados = [
            self.btnDinheiro,
            self.btnPix,
            self.btnCartaoDebito,
            self.btnCartaoCredito,
            self.btnValeRefeicao,
            self.btnCheque,
        ]
        self._atalhos_forma = ["F1", "F2", "F3", "F4", "F5", "F6"]
        self._atalhos_forma_qt: list[QShortcut] = []
        self._botoes_forma: dict[str, QPushButton] = {}
        self._frame_parcelas: QFrame | None = None
        self._spin_parcelas: QSpinBox | None = None
        self._lbl_parcela_info: QLabel | None = None
        self._lbl_valor_parcela: QLabel | None = None
        self._lbl_status_pagamento: QLabel | None = None
        self._lbl_pagamentos_vazio: QLabel | None = None
        self._cents = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._atualizar_data_hora)
        self._timer.start()
        self._configurar_interface()
        self._criar_widget_parcelas()
        self._carregar_formas_pagamento()
        self._conectar_sinais()
        self._atualizar_data_hora()
        self._atualizar_resumo()

    def carregar_venda(self, venda_data: dict[str, Any]) -> None:
        self._venda_data = dict(venda_data)
        self._pagamentos = []
        self._ultima_linha_pagamento = None
        numero_venda = venda_data.get("numero_venda")
        self.lblNumVendaValor.setText(str(numero_venda) if numero_venda not in (None, "", 0) else "Nova")
        self.lblClienteValor.setText(str(venda_data.get("cliente_nome") or "Consumidor Final"))
        total = numero_decimal(venda_data.get("total"))
        descontos = numero_decimal(venda_data.get("desconto_total"))
        self.lblTotalHeaderValor.setText(formatar_moeda(total))
        self.lblValorTotalValor.setText(formatar_moeda(total))
        self.lblDescontosValor.setText(formatar_moeda(descontos))
        self.tableFormasPagamento.setRowCount(0)
        if self._lbl_pagamentos_vazio:
            self._lbl_pagamentos_vazio.show()
        self._cents = 0
        self._atualizar_display_valor()
        self._atualizar_resumo()
        self._atualizar_status_pagamento("Selecione a forma de pagamento e informe o valor recebido.", "info")

    def _configurar_interface(self) -> None:
        self.btnFecharPedido.setToolTip("Finaliza a venda quando o valor recebido cobre o total.")
        self.btnFinalizarPendencia.setToolTip("Registrar o valor restante como conta a receber.")
        self.btnPagamentoExato.setText("Preencher valor restante")
        self.btnFinalizarPendencia.setText("Registrar como conta a receber")
        self.btnEnter.setText("Lançar pagamento")
        self.btnFecharPedido.setText("Finalizar venda")
        self.btnEnter.setToolTip("Lança o pagamento informado na tabela de pagamentos.")
        self.btnFecharPedido.setToolTip("Confirma os pagamentos lançados e finaliza a venda.")
        self.lineEditValor.setPlaceholderText("Digite o valor recebido")
        self.lineEditValor.setReadOnly(True)
        self.lineEditValor.setToolTip("Use o teclado numérico ou o teclado físico para informar o valor.")
        self.lblHeaderResumo.setText("Pagamentos lançados")
        self.lblRestanteLabel.setText("Falta pagar")
        self.lblSomaTotalLabel.setText("Já pago")
        self.tableFormasPagamento.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableFormasPagamento.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableFormasPagamento.setToolTip("Selecione um pagamento e clique em Excluir para removê-lo.")
        header = self.tableFormasPagamento.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self._lbl_status_pagamento = QLabel("Selecione a forma de pagamento e informe o valor recebido.", self.frameNumpad)
        self._lbl_status_pagamento.setObjectName("lblStatusPagamento")
        self._lbl_status_pagamento.setAlignment(Qt.AlignCenter)
        self._lbl_status_pagamento.setWordWrap(True)
        self.numpadVL.insertWidget(0, self._lbl_status_pagamento)
        self._lbl_ajuda_forma = QLabel("Use o teclado numérico ou digite o valor no teclado físico.", self.frameNumpad)
        self._lbl_ajuda_forma.setAlignment(Qt.AlignCenter)
        self._lbl_ajuda_forma.setWordWrap(True)
        self._lbl_ajuda_forma.setStyleSheet("color:#58758f; font-size:11px; padding:2px;")
        self.numpadVL.insertWidget(1, self._lbl_ajuda_forma)
        self.lineEditValor.installEventFilter(self)

        self._lbl_pagamentos_vazio = QLabel("Nenhum pagamento lançado.", self.frameTabelaLancamentos)
        self._lbl_pagamentos_vazio.setAlignment(Qt.AlignCenter)
        self._lbl_pagamentos_vazio.setStyleSheet("color:#7892a8; font-size:12px; padding:10px;")
        self.tabelaLanVL.insertWidget(1, self._lbl_pagamentos_vazio)

        self._atalhos_teclado = []
        for sequencia, acao in (
            ("Return", self._lancar_pagamento),
            ("Enter", self._lancar_pagamento),
            ("Delete", self._remover_pagamento_selecionado),
            ("Escape", self.voltar_venda.emit),
        ):
            atalho = QShortcut(QKeySequence(sequencia), self)
            atalho.activated.connect(acao)
            self._atalhos_teclado.append(atalho)

    def _criar_widget_parcelas(self) -> None:
        self._frame_parcelas = QFrame(self.frameNumpad)
        self._frame_parcelas.setStyleSheet(
            "QFrame{background-color:#f0f6fc;border:1px solid #7aaac8;border-radius:6px;}"
        )
        self._frame_parcelas.setMaximumHeight(122)
        layout = QVBoxLayout(self._frame_parcelas)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)

        lbl_titulo = QLabel("Parcelamento no cartão")
        lbl_titulo.setStyleSheet("font-size:11px;font-weight:bold;color:#1a3a5c;")
        layout.addWidget(lbl_titulo)

        linha = QHBoxLayout()
        linha.setSpacing(8)
        lbl_qtd = QLabel("Parcelas:")
        lbl_qtd.setStyleSheet("font-size:11px;color:#1a3a5c;")
        linha.addWidget(lbl_qtd)

        self._spin_parcelas = QSpinBox()
        self._spin_parcelas.setRange(1, 18)
        self._spin_parcelas.setValue(1)
        self._spin_parcelas.setStyleSheet(
            "QSpinBox{font-size:12px;font-weight:bold;padding:2px 6px;border:1px solid #a8c4d8;border-radius:4px;}"
        )
        self._spin_parcelas.valueChanged.connect(self._atualizar_info_parcelas)
        linha.addWidget(self._spin_parcelas)
        self._lbl_valor_parcela = QLabel("Valor por parcela: --")
        self._lbl_valor_parcela.setStyleSheet("font-size:11px;font-weight:bold;color:#1a5fa0;")
        linha.addWidget(self._lbl_valor_parcela)
        linha.addStretch()
        layout.addLayout(linha)

        self._lbl_parcela_info = QLabel("")
        self._lbl_parcela_info.setStyleSheet("font-size:10px;color:#4a6a8a;")
        self._lbl_parcela_info.setWordWrap(True)
        layout.addWidget(self._lbl_parcela_info)

        self.numpadVL.insertWidget(0, self._frame_parcelas)
        self._frame_parcelas.hide()

    def eventFilter(self, watched, event) -> bool:
        if watched is self.lineEditValor and event.type() == QEvent.KeyPress:
            key_event = event if isinstance(event, QKeyEvent) else None
            if key_event is not None:
                key = int(key_event.key())
                if int(Qt.Key_0) <= key <= int(Qt.Key_9):
                    self._inserir_valor(str(key - int(Qt.Key_0)))
                    return True
                if key_event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
                    self._limpar_valor()
                    return True
                if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                    self._lancar_pagamento()
                    return True
        return super().eventFilter(watched, event)

    def _atualizar_info_parcelas(self) -> None:
        if not self._frame_parcelas or not self._spin_parcelas or not self._lbl_parcela_info:
            return
        if not self._forma_selecionada:
            if self._lbl_valor_parcela:
                self._lbl_valor_parcela.setText("Valor por parcela: --")
            self._lbl_parcela_info.setText("")
            return

        dados = self._formas_pagamento_dados.get(self._forma_selecionada, {})
        permite = str(dados.get("permite_parcelamento") or FLAG_NAO).upper() == FLAG_SIM
        taxa = float(dados.get("taxa_administrativa") or 0.0)

        if not permite:
            if self._lbl_valor_parcela:
                self._lbl_valor_parcela.setText("Valor por parcela: --")
            self._lbl_parcela_info.setText("")
            return

        valor = self._cents / 100
        parcelas = self._spin_parcelas.value()

        if valor <= 0:
            if self._lbl_valor_parcela:
                self._lbl_valor_parcela.setText("Valor por parcela: --")
            self._lbl_parcela_info.setText("Informe um valor para ver o detalhamento")
            return

        valor_total_com_taxa = valor * (1 + taxa / 100) if taxa > 0 else valor
        valor_parcela = valor_total_com_taxa / parcelas if parcelas > 0 else 0

        if self._lbl_valor_parcela:
            self._lbl_valor_parcela.setText(f"Valor por parcela: {formatar_moeda(valor_parcela)}")

        linhas = []
        if taxa > 0:
            linhas.append(f"Total com taxa: {formatar_moeda(valor_total_com_taxa)} • Taxa: {taxa:.1f}%")
        else:
            linhas.append(f"Total parcelado: {formatar_moeda(valor_total_com_taxa)}")

        self._lbl_parcela_info.setText("\n".join(linhas))

    @staticmethod
    def _normalizar_forma_pagamento(valor: str) -> str:
        return (
            str(valor or "")
            .strip()
            .lower()
            .replace("ã", "a")
            .replace("á", "a")
            .replace("â", "a")
            .replace("é", "e")
            .replace("ê", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ô", "o")
            .replace("õ", "o")
            .replace("ú", "u")
            .replace("ç", "c")
        )

    def _carregar_formas_pagamento(self) -> None:
        formas = FinanceiroService.listar_formas_pagamento()
        ordem_preferida = {
            "dinheiro": 0,
            "pix": 1,
            "cartao debito": 2,
            "cartao credito": 3,
            "vale refeicao": 4,
            "pag. parcial": 5,
        }
        icones = {
            "dinheiro": "💸",
            "pix": "⚡",
            "cartao debito": "💳",
            "cartao credito": "💳",
            "vale refeicao": "🍴",
            "pag. parcial": "",
        }
        formas_ativas = sorted(
            list(formas or []),
            key=lambda forma: (
                ordem_preferida.get(self._normalizar_forma_pagamento(str(forma.get("nome") or "")), 99),
                str(forma.get("nome") or "").upper(),
            ),
        )

        self._botoes_forma.clear()
        self._formas_pagamento_dados.clear()
        for indice, botao in enumerate(self._botoes_forma_ordenados):
            if indice >= len(formas_ativas):
                botao.hide()
                botao.setEnabled(False)
                botao.setText("")
                continue

            forma = formas_ativas[indice]
            nome = str(forma.get("nome") or f"Forma {indice + 1}").strip()
            nome_normalizado = self._normalizar_forma_pagamento(nome)
            icone = icones.get(nome_normalizado, "💳")
            atalho = self._atalhos_forma[indice]

            self._formas_pagamento_dados[nome] = {
                "permite_parcelamento": forma.get("permite_parcelamento", FLAG_NAO),
                "taxa_administrativa": forma.get("taxa_administrativa", 0.0),
            }

            botao.show()
            botao.setEnabled(True)
            botao.setCheckable(True)
            botao.setShortcut(atalho)
            botao.setToolTip(f"Seleciona {nome} e preenche o restante. Atalho: {atalho}.")
            botao.setText(f"{icone}  {nome}   ({atalho})")
            self._botoes_forma[nome] = botao

            atalho_janela = QShortcut(QKeySequence(atalho), self)
            atalho_janela.setContext(Qt.WindowShortcut)
            atalho_janela.activated.connect(
                lambda forma=nome: self._atualizar_forma_selecionada(forma)
            )
            self._atalhos_forma_qt.append(atalho_janela)

        if formas_ativas:
            self._atualizar_forma_selecionada(str(formas_ativas[0].get("nome") or ""))
        else:
            self._forma_selecionada = ""

    def _conectar_sinais(self) -> None:
        self.btnVoltar.clicked.connect(self.voltar_venda.emit)
        for nome, botao in self._botoes_forma.items():
            botao.clicked.connect(lambda _=False, forma=nome: self._atualizar_forma_selecionada(forma))

        for texto, botao in (
            ("0", self.btn0),
            ("1", self.btn1),
            ("2", self.btn2),
            ("3", self.btn3),
            ("4", self.btn4),
            ("5", self.btn5),
            ("6", self.btn6),
            ("7", self.btn7),
            ("8", self.btn8),
            ("9", self.btn9),
            (",", self.btnVirgula),
        ):
            botao.clicked.connect(lambda _=False, t=texto: self._inserir_valor(t))

        self.btnLimpar.clicked.connect(self._limpar_valor)
        self.btnEnter.clicked.connect(self._lancar_pagamento)
        self.btnPagamentoExato.clicked.connect(self._usar_pagamento_exato)
        self.btnFecharPedido.clicked.connect(self._finalizar_pagamento)
        self.btnFinalizarPendencia.clicked.connect(self._finalizar_com_pendencia)
        self.tableFormasPagamento.cellClicked.connect(self._ao_clicar_pagamento)

    def _atualizar_forma_selecionada(self, forma: str) -> None:
        self._forma_selecionada = forma
        for nome, botao in self._botoes_forma.items():
            botao.setChecked(nome == forma)

        dados = self._formas_pagamento_dados.get(forma, {})
        permite = str(dados.get("permite_parcelamento") or FLAG_NAO).upper() == FLAG_SIM

        if permite and self._frame_parcelas:
            self._frame_parcelas.show()
            if self._spin_parcelas:
                self._spin_parcelas.setValue(1)
            self._atualizar_info_parcelas()
        elif self._frame_parcelas:
            self._frame_parcelas.hide()
        if self._valor_restante() > 0 and self._cents == 0:
            self._cents = int(round(self._valor_restante() * 100))
            self._atualizar_display_valor()
        self._atualizar_status_pagamento(f"{forma} selecionado. Confira o valor e pressione Enter.", "info")
        instrucoes = {
            "dinheiro": "Dinheiro: informe o valor recebido. Se for maior, o troco será calculado.",
            "pix": "PIX: confirme o recebimento antes de lançar o pagamento.",
            "cartao debito": "Cartão de débito: confirme a aprovação da transação.",
            "cartao credito": "Cartão de crédito: confirme a aprovação e as parcelas.",
            "vale refeicao": "Vale-refeição: confira o valor autorizado pelo cartão.",
        }
        if hasattr(self, "_lbl_ajuda_forma"):
            self._lbl_ajuda_forma.setText(
                instrucoes.get(
                    self._normalizar_forma_pagamento(forma),
                    "Informe o valor recebido e pressione Enter.",
                )
            )
        self.lineEditValor.setFocus()
        self.lineEditValor.selectAll()

    def _inserir_valor(self, trecho: str) -> None:
        if trecho == ",":
            return
        if not trecho.isdigit():
            return
        if self._cents >= 10000000:
            return
        self._cents = self._cents * 10 + int(trecho)
        self._atualizar_display_valor()

    def _atualizar_display_valor(self) -> None:
        valor = self._cents / 100
        self.lineEditValor.setText(f"{valor:.2f}".replace(".", ","))

    def _limpar_valor(self) -> None:
        self._cents = self._cents // 10
        self._atualizar_display_valor()

    def _usar_pagamento_exato(self) -> None:
        restante = self._valor_restante()
        self._cents = int(round(restante * 100))
        self._atualizar_display_valor()

    def _lancar_pagamento(self) -> None:
        if not self._forma_selecionada:
            mostrar_info(self, "Forma de pagamento", "Nenhuma forma de pagamento ativa está disponível para lançamento.")
            return

        valor = self._cents / 100
        if valor <= 0:
            self._atualizar_status_pagamento("Informe um valor maior que zero.", "warning")
            mostrar_info(self, "Valor inválido", "Informe um valor maior que zero para lançar o pagamento.")
            return

        pagamento: dict[str, Any] = {"forma": self._forma_selecionada, "valor": valor}

        dados = self._formas_pagamento_dados.get(self._forma_selecionada, {})
        permite = str(dados.get("permite_parcelamento") or FLAG_NAO).upper() == FLAG_SIM

        if permite and self._spin_parcelas and self._spin_parcelas.value() > 1:
            parcelas = self._spin_parcelas.value()
            taxa = float(dados.get("taxa_administrativa") or 0.0)
            valor_total_com_taxa = valor * (1 + taxa / 100) if taxa > 0 else valor
            valor_parcela = valor_total_com_taxa / parcelas

            pagamento["parcelas"] = parcelas
            pagamento["taxa_administrativa"] = taxa
            pagamento["valor_parcela"] = valor_parcela

        self._pagamentos.append(pagamento)
        self._ultima_linha_pagamento = len(self._pagamentos) - 1
        self._cents = 0
        self._atualizar_display_valor()
        if self._spin_parcelas:
            self._spin_parcelas.setValue(1)
        self._renderizar_pagamentos()
        self._atualizar_resumo()
        restante_atual = self._valor_restante()
        self._atualizar_status_pagamento(
            (
                f"{self._forma_selecionada} lançado: {formatar_moeda(valor)} | "
                f"Falta pagar: {formatar_moeda(restante_atual)}"
            )
            if restante_atual > 0
            else f"Pagamento concluído: {self._forma_selecionada} — {formatar_moeda(valor)}",
            "warning" if restante_atual > 0 else "success",
        )

        if self._normalizar_forma_pagamento(self._forma_selecionada) == "pag. parcial":
            restante = self._valor_restante()
            if restante > 0:
                self._finalizar_com_pendencia()

    def _renderizar_pagamentos(self) -> None:
        self.tableFormasPagamento.setRowCount(len(self._pagamentos))
        if self._lbl_pagamentos_vazio:
            self._lbl_pagamentos_vazio.setVisible(not self._pagamentos)
        for row, pagamento in enumerate(self._pagamentos):
            parcelas = pagamento.get("parcelas")
            if parcelas and parcelas > 1:
                texto_forma = f"{pagamento['forma']} ({parcelas}x)"
            else:
                texto_forma = str(pagamento["forma"])

            set_table_item(self.tableFormasPagamento, row, 0, texto_forma)
            set_table_item(self.tableFormasPagamento, row, 1, formatar_moeda(pagamento["valor"]))
            item_acao = set_table_item(self.tableFormasPagamento, row, 2, "Excluir")
            item_acao.setTextAlignment(Qt.AlignCenter)
            item_acao.setForeground(QBrush(QColor("#b42318")))
            item_acao.setToolTip("Clique para excluir este pagamento.")
            if row == self._ultima_linha_pagamento:
                for coluna in range(3):
                    item = self.tableFormasPagamento.item(row, coluna)
                    if item is not None:
                        item.setBackground(QBrush(QColor("#e8f4ff")))
                        fonte = item.font()
                        fonte.setBold(True)
                        item.setFont(fonte)

    def _atualizar_resumo(self) -> None:
        total = numero_decimal((self._venda_data or {}).get("total"))
        pagamentos = sum(numero_decimal(item["valor"]) for item in self._pagamentos)
        restante = max(0.0, total - pagamentos)
        troco = max(0.0, pagamentos - total)
        self.lblSomaTotalValor.setText(formatar_moeda(pagamentos))
        self.lblRestanteValor.setText(formatar_moeda(restante))
        self.lblTrocoValor.setText(formatar_moeda(troco))
        self._atualizar_status_resumo(total, pagamentos, restante, troco)
        self.btnFecharPedido.setEnabled(total > 0 and pagamentos >= total)
        cliente_id = int((self._venda_data or {}).get("cliente_id") or 0)
        cliente_eh_consumidor_final = bool((self._venda_data or {}).get("cliente_eh_consumidor_final"))
        self.btnFinalizarPendencia.setEnabled(
            total > 0 and pagamentos < total and cliente_id > 0 and not cliente_eh_consumidor_final
        )

    def _valor_restante(self) -> float:
        total = numero_decimal((self._venda_data or {}).get("total"))
        pagamentos = sum(numero_decimal(item["valor"]) for item in self._pagamentos)
        return max(0.0, total - pagamentos)

    def _ao_clicar_pagamento(self, row: int, column: int) -> None:
        if column != 2:
            return
        self._remover_pagamento(row)

    def _remover_pagamento_selecionado(self) -> None:
        self._remover_pagamento(self.tableFormasPagamento.currentRow())

    def _remover_pagamento(self, row: int) -> None:
        if row < 0 or row >= len(self._pagamentos):
            return
        pagamento = self._pagamentos[row]
        if not confirmar_acao(
            self,
            "Excluir pagamento",
            f"Deseja remover o pagamento de {formatar_moeda(pagamento['valor'])} ({pagamento['forma']})?",
        ):
            return
        self._pagamentos.pop(row)
        self._ultima_linha_pagamento = len(self._pagamentos) - 1 if self._pagamentos else None
        self._renderizar_pagamentos()
        self._atualizar_resumo()
        self._atualizar_status_pagamento("Pagamento removido. Confira o valor restante.", "warning")

    def _atualizar_status_pagamento(self, texto: str, nivel: str = "info") -> None:
        if not self._lbl_status_pagamento:
            return
        cores = {
            "info": ("#eef6ff", "#1a5fa0"),
            "success": ("#ecfdf3", "#027a48"),
            "warning": ("#fff7e6", "#b54708"),
            "error": ("#fef3f2", "#b42318"),
        }
        fundo, texto_cor = cores.get(nivel, cores["info"])
        self._lbl_status_pagamento.setText(texto)
        self._lbl_status_pagamento.setStyleSheet(
            f"QLabel#lblStatusPagamento {{ background-color: {fundo}; color: {texto_cor}; "
            f"border: 1px solid {texto_cor}; border-radius: 4px; padding: 6px; "
            "font-size: 11px; font-weight: bold; }"
        )

    def _atualizar_status_resumo(self, total: float, pagamentos: float, restante: float, troco: float) -> None:
        if troco > 0:
            self.frameTroco.setStyleSheet(
                "QFrame#frameTroco{background:#ecfdf3;border-bottom-left-radius:5px;border-bottom-right-radius:5px;}"
            )
            self.lblTrocoLabel.setStyleSheet("font-size:15px;font-weight:bold;color:#027a48;letter-spacing:1px;")
            self.lblTrocoValor.setStyleSheet("font-size:28px;font-weight:bold;color:#027a48;")
            self._atualizar_status_pagamento(f"Pagamento excedente | Troco: {formatar_moeda(troco)}", "success")
            return

        self.frameTroco.setStyleSheet(
            "QFrame#frameTroco{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #1a5fa0,stop:1 #0e3878);border-bottom-left-radius:5px;border-bottom-right-radius:5px;}"
        )
        self.lblTrocoLabel.setStyleSheet("font-size:15px;font-weight:bold;color:#80b8e0;letter-spacing:1px;")
        self.lblTrocoValor.setStyleSheet("font-size:28px;font-weight:bold;color:white;")
        if restante > 0:
            self.frameRestante.setStyleSheet("QFrame{background-color:#fff1e6;border-bottom:1px solid #f0c080;}")
            self.lblRestanteValor.setStyleSheet("font-size:24px;font-weight:bold;color:#b54708;")
            self._atualizar_status_pagamento(
                f"Recebido: {formatar_moeda(pagamentos)} | Falta pagar: {formatar_moeda(restante)}",
                "warning" if pagamentos > 0 else "info",
            )
        else:
            self.frameRestante.setStyleSheet("QFrame{background-color:#ecfdf3;border-bottom:1px solid #b7e4c7;}")
            self.lblRestanteValor.setStyleSheet("font-size:24px;font-weight:bold;color:#027a48;")
            self._atualizar_status_pagamento(
                f"Pagamento exato | Recebido: {formatar_moeda(pagamentos)}",
                "success",
            )

    def _finalizar_pagamento(self) -> None:
        if not self._venda_data:
            return
        total = numero_decimal(self._venda_data.get("total"))
        pagamentos = sum(numero_decimal(item["valor"]) for item in self._pagamentos)
        troco = max(0.0, pagamentos - total)
        if not confirmar_acao(
            self,
            "Confirmar pagamento",
            f"Recebido: {formatar_moeda(pagamentos)}\n"
            f"Falta pagar: R$ 0,00\n"
            f"Troco: {formatar_moeda(troco)}\n\n"
            "Deseja finalizar esta venda?",
        ):
            return
        self.venda_finalizada.emit(
            {
                "numero_venda": self._venda_data.get("numero_venda"),
                "cliente_id": self._venda_data.get("cliente_id"),
                "cliente_nome": self._venda_data.get("cliente_nome"),
                "cliente_eh_consumidor_final": self._venda_data.get("cliente_eh_consumidor_final"),
                "data_hora_venda": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"),
                "itens": list(self._venda_data.get("itens") or []),
                "subtotal": self._venda_data.get("subtotal"),
                "desconto_global": self._venda_data.get("desconto_global"),
                "desconto_itens": self._venda_data.get("desconto_itens"),
                "desconto_total": self._venda_data.get("desconto_total"),
                "total": self._venda_data.get("total"),
                "pagamentos": list(self._pagamentos),
                "troco": troco,
            }
        )

    def _finalizar_com_pendencia(self) -> None:
        if not self._venda_data:
            return

        total = numero_decimal(self._venda_data.get("total"))
        pagamentos = sum(numero_decimal(item["valor"]) for item in self._pagamentos)
        restante = max(0.0, total - pagamentos)
        cliente_id = int(self._venda_data.get("cliente_id") or 0)
        cliente_eh_consumidor_final = bool(self._venda_data.get("cliente_eh_consumidor_final"))

        if cliente_id <= 0 or cliente_eh_consumidor_final:
            mostrar_info(
                self,
                "Cliente obrigatório",
                "Selecione um cliente diferente de Consumidor Final antes de finalizar a venda com pendencia.",
            )
            return

        if restante <= 0:
            mostrar_info(
                self,
                "Pendência inválida",
                "Não há saldo em aberto para gerar uma pendência.",
            )
            return

        if not confirmar_acao(
            self,
            "Registrar pendência",
            f"Registrar {formatar_moeda(restante)} como conta a receber de {self._venda_data.get('cliente_nome') or 'cliente'}?",
        ):
            return

        dialog = FinalizarPendenciaDialog(
            venda_data=self._venda_data,
            valor_pago=pagamentos,
            parent=self,
        )
        if dialog.exec_() != dialog.Accepted or not dialog.resultado:
            return

        self.venda_finalizada.emit(
            {
                "numero_venda": self._venda_data.get("numero_venda"),
                "cliente_id": self._venda_data.get("cliente_id"),
                "cliente_nome": self._venda_data.get("cliente_nome"),
                "cliente_eh_consumidor_final": self._venda_data.get("cliente_eh_consumidor_final"),
                "data_hora_venda": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"),
                "itens": list(self._venda_data.get("itens") or []),
                "subtotal": self._venda_data.get("subtotal"),
                "desconto_global": self._venda_data.get("desconto_global"),
                "desconto_itens": self._venda_data.get("desconto_itens"),
                "desconto_total": self._venda_data.get("desconto_total"),
                "total": self._venda_data.get("total"),
                "pagamentos": list(self._pagamentos),
                "troco": 0.0,
                "finalizar_com_pendencia": True,
                "valor_em_aberto": restante,
                "data_vencimento": dialog.resultado.get("data_vencimento"),
                "observacao_pendencia": dialog.resultado.get("observacao"),
            }
        )

    def _atualizar_data_hora(self) -> None:
        self.lblStatusDataHora.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm:ss"))
