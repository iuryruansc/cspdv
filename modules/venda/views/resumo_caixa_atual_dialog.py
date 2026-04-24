from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils.format_utils import formatar_moeda


class ResumoCaixaAtualDialog(QDialog):
    def __init__(self, resumo: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._resumo = resumo
        self.setWindowTitle("Resumo do Caixa Atual")
        self.setModal(True)
        self.resize(860, 600)
        self.setMinimumSize(820, 580)
        self._montar_ui()

    def _montar_ui(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background-color: #eef4fb;
            }
            QFrame#headerCard, QFrame#resumoCard, QFrame#pagamentoCard {
                background-color: #ffffff;
                border: 1px solid #c9dced;
                border-radius: 16px;
            }
            QLabel#tituloDialog {
                color: #173a5f;
                font-size: 24px;
                font-weight: 700;
            }
            QLabel#subtituloDialog {
                color: #5f7d9a;
                font-size: 12px;
            }
            QLabel[class="campoLabel"] {
                color: #5b7590;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }
            QLabel[class="campoValor"] {
                color: #173a5f;
                font-size: 18px;
                font-weight: 700;
            }
            QLabel[class="campoValorPequeno"] {
                color: #214b73;
                font-size: 15px;
                font-weight: 600;
            }
            QLabel#statusBadge {
                background-color: #e8f7ec;
                color: #22834c;
                border: 1px solid #bbe1c4;
                border-radius: 12px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#pagamentoTitulo {
                color: #173a5f;
                font-size: 14px;
                font-weight: 700;
            }
            QFrame[class="pagamentoLinha"] {
                background-color: #f7fbff;
                border: 1px solid #d8e7f4;
                border-radius: 10px;
            }
            QLabel[class="pagamentoForma"] {
                color: #2b5a84;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel[class="pagamentoValor"] {
                color: #173a5f;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton {
                background-color: #2f79c8;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 22px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #2467ae;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_card = QFrame(self)
        header_card.setObjectName("headerCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(22, 20, 22, 20)

        header_texto = QVBoxLayout()
        titulo = QLabel("Resumo do Caixa Atual", header_card)
        titulo.setObjectName("tituloDialog")
        subtitulo = QLabel("Acompanhe rapidamente a sessao de caixa aberta e os totais operacionais.", header_card)
        subtitulo.setObjectName("subtituloDialog")
        header_texto.addWidget(titulo)
        header_texto.addWidget(subtitulo)
        header_texto.addStretch()
        header_layout.addLayout(header_texto, 1)

        status = QLabel(self._resumo.get("status", "Aberto"), header_card)
        status.setObjectName("statusBadge")
        status.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(status, 0, Qt.AlignTop)

        layout.addWidget(header_card)

        resumo_card = QFrame(self)
        resumo_card.setObjectName("resumoCard")
        resumo_layout = QGridLayout(resumo_card)
        resumo_layout.setContentsMargins(24, 24, 24, 24)
        resumo_layout.setHorizontalSpacing(24)
        resumo_layout.setVerticalSpacing(18)

        campos = [
            ("PDV", self._resumo.get("pdv_label", "-"), "campoValorPequeno"),
            ("Operador", self._resumo.get("operador", "-"), "campoValorPequeno"),
            ("Abertura", self._resumo.get("data_abertura", "-"), "campoValorPequeno"),
            ("Fundo inicial", formatar_moeda(float(self._resumo.get("fundo_inicial") or 0.0)), "campoValor"),
            ("Vendas do dia", str(int(self._resumo.get("vendas_dia") or 0)), "campoValor"),
            ("Faturamento total", formatar_moeda(float(self._resumo.get("faturamento_total") or 0.0)), "campoValor"),
            ("Faturamento em dinheiro", formatar_moeda(float(self._resumo.get("faturamento_dinheiro") or 0.0)), "campoValor"),
            ("Sangrias", formatar_moeda(float(self._resumo.get("total_sangrias") or 0.0)), "campoValor"),
            ("Suprimentos", formatar_moeda(float(self._resumo.get("total_suprimentos") or 0.0)), "campoValor"),
            ("Reforco de troco", formatar_moeda(float(self._resumo.get("total_troco") or 0.0)), "campoValor"),
            ("Dinheiro esperado", formatar_moeda(float(self._resumo.get("total_esperado") or 0.0)), "campoValor"),
            ("Saldo atual", formatar_moeda(float(self._resumo.get("saldo_atual") or 0.0)), "campoValor"),
        ]

        for indice, (rotulo, valor, classe_valor) in enumerate(campos):
            linha = (indice // 3) * 2
            coluna = indice % 3
            label = QLabel(rotulo, resumo_card)
            label.setProperty("class", "campoLabel")
            valor_label = QLabel(str(valor), resumo_card)
            valor_label.setProperty("class", classe_valor)
            valor_label.setWordWrap(True)
            resumo_layout.addWidget(label, linha, coluna)
            resumo_layout.addWidget(valor_label, linha + 1, coluna)

        layout.addWidget(resumo_card)

        pagamento_card = QFrame(self)
        pagamento_card.setObjectName("pagamentoCard")
        pagamento_layout = QVBoxLayout(pagamento_card)
        pagamento_layout.setContentsMargins(24, 22, 24, 22)
        pagamento_layout.setSpacing(12)

        pagamento_titulo = QLabel("Totais por forma de pagamento", pagamento_card)
        pagamento_titulo.setObjectName("pagamentoTitulo")
        pagamento_layout.addWidget(pagamento_titulo)

        totais = list(self._resumo.get("totais_forma_pagamento") or [])
        if totais:
            for forma in totais:
                linha = QFrame(pagamento_card)
                linha.setProperty("class", "pagamentoLinha")
                linha_layout = QHBoxLayout(linha)
                linha_layout.setContentsMargins(12, 10, 12, 10)
                linha_layout.setSpacing(12)

                nome = QLabel(str(forma.get("forma_pagamento") or "Forma"), linha)
                nome.setProperty("class", "pagamentoForma")
                qtd = QLabel(f"{int(forma.get('qtd_vendas') or 0)} venda(s)", linha)
                qtd.setProperty("class", "pagamentoForma")
                valor = QLabel(formatar_moeda(float(forma.get("total") or 0.0)), linha)
                valor.setProperty("class", "pagamentoValor")

                linha_layout.addWidget(nome, 1)
                linha_layout.addWidget(qtd, 0)
                linha_layout.addWidget(valor, 0, Qt.AlignRight)
                pagamento_layout.addWidget(linha)
        else:
            vazio = QLabel("Nenhuma movimentacao de pagamento registrada ainda para este caixa.", pagamento_card)
            vazio.setProperty("class", "campoValorPequeno")
            pagamento_layout.addWidget(vazio)

        layout.addWidget(pagamento_card, 1)

        acoes = QWidget(self)
        acoes_layout = QHBoxLayout(acoes)
        acoes_layout.setContentsMargins(0, 0, 0, 0)
        acoes_layout.addStretch()
        btn_fechar = QPushButton("Fechar", acoes)
        btn_fechar.clicked.connect(self.accept)
        acoes_layout.addWidget(btn_fechar)
        layout.addWidget(acoes)
