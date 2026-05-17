from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QDateTime, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QWidget,
)

from modules.financeiro.services.financeiro_service import FinanceiroService
from modules.venda.views.finalizar_pendencia_dialog import FinalizarPendenciaDialog
from ui.venda.tela_pagamento import Ui_TelaPagamento
from utils.format_utils import formatar_moeda, numero_decimal
from utils.table_widget_utils import set_table_item
from utils.ui_messages import mostrar_info

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

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._venda_data: Optional[Dict[str, Any]] = None
        self._pagamentos: List[Dict[str, Any]] = []
        self._forma_selecionada = ""
        self._botoes_forma_ordenados = [
            self.btnDinheiro,
            self.btnPix,
            self.btnCartaoDebito,
            self.btnCartaoCredito,
            self.btnValeRefeicao,
            self.btnCheque,
        ]
        self._atalhos_forma = ["F1", "F2", "F3", "F4", "F5", "F6"]
        self._botoes_forma: Dict[str, QPushButton] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._atualizar_data_hora)
        self._timer.start()
        self._configurar_interface()
        self._carregar_formas_pagamento()
        self._conectar_sinais()
        self._atualizar_data_hora()
        self._atualizar_resumo()

    def carregar_venda(self, venda_data: Dict[str, Any]) -> None:
        self._venda_data = dict(venda_data)
        self._pagamentos = []
        self.lblNumVendaValor.setText(str(venda_data.get("numero_venda") or "---"))
        self.lblClienteValor.setText(str(venda_data.get("cliente_nome") or "Consumidor Final"))
        total = numero_decimal(venda_data.get("total"))
        descontos = numero_decimal(venda_data.get("desconto_total"))
        self.lblTotalHeaderValor.setText(formatar_moeda(total))
        self.lblValorTotalValor.setText(formatar_moeda(total))
        self.lblDescontosValor.setText(formatar_moeda(descontos))
        self.tableFormasPagamento.setRowCount(0)
        self.lineEditValor.setText("")
        self._atualizar_resumo()

    def _configurar_interface(self) -> None:
        self.btnFecharPedido.setToolTip("Finalizar pagamento")
        self.btnFinalizarPendencia.setToolTip("Concluir a venda com saldo em aberto para recebimento posterior")

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
            "cheque": 5,
        }
        icones = {
            "dinheiro": "💸",
            "pix": "⚡",
            "cartao debito": "💳",
            "cartao credito": "💳",
            "vale refeicao": "🍴",
            "cheque": "📄",
        }
        formas_ativas = sorted(
            list(formas or []),
            key=lambda forma: (
                ordem_preferida.get(self._normalizar_forma_pagamento(str(forma.get("nome") or "")), 99),
                str(forma.get("nome") or "").upper(),
            ),
        )

        self._botoes_forma.clear()
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

            botao.show()
            botao.setEnabled(True)
            botao.setCheckable(True)
            botao.setShortcut(atalho)
            botao.setText(f"{icone}  {nome}   ({atalho})")
            self._botoes_forma[nome] = botao

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

    def _inserir_valor(self, trecho: str) -> None:
        texto = self.lineEditValor.text().strip()
        if trecho == ",":
            if "," in texto:
                return
            self.lineEditValor.setText((texto or "0") + ",")
            return
        self.lineEditValor.setText(texto + trecho)

    def _limpar_valor(self) -> None:
        self.lineEditValor.clear()

    def _usar_pagamento_exato(self) -> None:
        restante = self._valor_restante()
        self.lineEditValor.setText(f"{restante:.2f}".replace(".", ","))

    def _lancar_pagamento(self) -> None:
        if not self._forma_selecionada:
            mostrar_info(self, "Forma de pagamento", "Nenhuma forma de pagamento ativa está disponível para lançamento.")
            return

        valor = numero_decimal(self.lineEditValor.text())
        if valor <= 0:
            mostrar_info(self, "Valor inválido", "Informe um valor maior que zero para lançar o pagamento.")
            return

        self._pagamentos.append({"forma": self._forma_selecionada, "valor": valor})
        self.lineEditValor.clear()
        self._renderizar_pagamentos()
        self._atualizar_resumo()

    def _renderizar_pagamentos(self) -> None:
        self.tableFormasPagamento.setRowCount(len(self._pagamentos))
        for row, pagamento in enumerate(self._pagamentos):
            set_table_item(self.tableFormasPagamento, row, 0, str(pagamento["forma"]))
            set_table_item(self.tableFormasPagamento, row, 1, formatar_moeda(pagamento["valor"]))
            set_table_item(self.tableFormasPagamento, row, 2, "Remover")

    def _atualizar_resumo(self) -> None:
        total = numero_decimal((self._venda_data or {}).get("total"))
        pagamentos = sum(numero_decimal(item["valor"]) for item in self._pagamentos)
        restante = max(0.0, total - pagamentos)
        troco = max(0.0, pagamentos - total)
        self.lblSomaTotalValor.setText(formatar_moeda(pagamentos))
        self.lblRestanteValor.setText(formatar_moeda(restante))
        self.lblTrocoValor.setText(formatar_moeda(troco))
        self.btnFecharPedido.setEnabled(total > 0 and pagamentos >= total)
        cliente_id = int((self._venda_data or {}).get("cliente_id") or 0)
        self.btnFinalizarPendencia.setEnabled(total > 0 and 0 < pagamentos < total and cliente_id > 0)

    def _valor_restante(self) -> float:
        total = numero_decimal((self._venda_data or {}).get("total"))
        pagamentos = sum(numero_decimal(item["valor"]) for item in self._pagamentos)
        return max(0.0, total - pagamentos)

    def _ao_clicar_pagamento(self, row: int, column: int) -> None:
        if column != 2:
            return
        if row < 0 or row >= len(self._pagamentos):
            return
        self._pagamentos.pop(row)
        self._renderizar_pagamentos()
        self._atualizar_resumo()

    def _finalizar_pagamento(self) -> None:
        if not self._venda_data:
            return
        self.venda_finalizada.emit(
            {
                "numero_venda": self._venda_data.get("numero_venda"),
                "cliente_id": self._venda_data.get("cliente_id"),
                "cliente_nome": self._venda_data.get("cliente_nome"),
                "data_hora_venda": QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"),
                "itens": list(self._venda_data.get("itens") or []),
                "subtotal": self._venda_data.get("subtotal"),
                "desconto_global": self._venda_data.get("desconto_global"),
                "desconto_itens": self._venda_data.get("desconto_itens"),
                "desconto_total": self._venda_data.get("desconto_total"),
                "total": self._venda_data.get("total"),
                "pagamentos": list(self._pagamentos),
                "troco": max(
                    0.0,
                    sum(numero_decimal(item["valor"]) for item in self._pagamentos)
                    - numero_decimal(self._venda_data.get("total")),
                ),
            }
        )

    def _finalizar_com_pendencia(self) -> None:
        if not self._venda_data:
            return

        total = numero_decimal(self._venda_data.get("total"))
        pagamentos = sum(numero_decimal(item["valor"]) for item in self._pagamentos)
        restante = max(0.0, total - pagamentos)
        cliente_id = int(self._venda_data.get("cliente_id") or 0)

        if cliente_id <= 0:
            mostrar_info(
                self,
                "Cliente obrigatório",
                "Selecione um cliente antes de finalizar a venda com pendência.",
            )
            return

        if pagamentos <= 0 or restante <= 0:
            mostrar_info(
                self,
                "Pendência inválida",
                "Lance um pagamento parcial antes de concluir a venda com pendência.",
            )
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
