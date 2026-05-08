# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets

class Ui_ResumoCaixaAtualDialog(object):
    def setupUi(self, ResumoCaixaAtualDialog):
        ResumoCaixaAtualDialog.setObjectName("ResumoCaixaAtualDialog")
        ResumoCaixaAtualDialog.resize(880, 700)
        ResumoCaixaAtualDialog.setMinimumSize(QtCore.QSize(840, 660))
        ResumoCaixaAtualDialog.setStyleSheet(
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
            QLabel[role="campoLabel"] {
                color: #5b7590;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }
            QLabel[role="campoValor"] {
                color: #173a5f;
                font-size: 18px;
                font-weight: 700;
            }
            QLabel[role="campoValorPequeno"] {
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
            QFrame[role="pagamentoLinha"] {
                background-color: #f7fbff;
                border: 1px solid #d8e7f4;
                border-radius: 10px;
            }
            QLabel[role="pagamentoForma"] {
                color: #2b5a84;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel[role="pagamentoValor"] {
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

        self.verticalLayout = QtWidgets.QVBoxLayout(ResumoCaixaAtualDialog)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(16)
        self.verticalLayout.setObjectName("verticalLayout")

        self.headerCard = QtWidgets.QFrame(ResumoCaixaAtualDialog)
        self.headerCard.setObjectName("headerCard")
        self.headerLayout = QtWidgets.QHBoxLayout(self.headerCard)
        self.headerLayout.setContentsMargins(22, 20, 22, 20)
        self.headerLayout.setObjectName("headerLayout")
        self.headerTextLayout = QtWidgets.QVBoxLayout()
        self.headerTextLayout.setObjectName("headerTextLayout")
        self.tituloDialog = QtWidgets.QLabel(self.headerCard)
        self.tituloDialog.setObjectName("tituloDialog")
        self.headerTextLayout.addWidget(self.tituloDialog)
        self.subtituloDialog = QtWidgets.QLabel(self.headerCard)
        self.subtituloDialog.setObjectName("subtituloDialog")
        self.headerTextLayout.addWidget(self.subtituloDialog)
        spacerHeader = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.headerTextLayout.addItem(spacerHeader)
        self.headerLayout.addLayout(self.headerTextLayout, 1)
        self.lblStatusBadge = QtWidgets.QLabel(self.headerCard)
        self.lblStatusBadge.setObjectName("statusBadge")
        self.lblStatusBadge.setAlignment(QtCore.Qt.AlignCenter)
        self.headerLayout.addWidget(self.lblStatusBadge, 0, QtCore.Qt.AlignTop)
        self.verticalLayout.addWidget(self.headerCard)

        self.resumoCard = QtWidgets.QFrame(ResumoCaixaAtualDialog)
        self.resumoCard.setObjectName("resumoCard")
        self.gridResumo = QtWidgets.QGridLayout(self.resumoCard)
        self.gridResumo.setContentsMargins(24, 24, 24, 24)
        self.gridResumo.setHorizontalSpacing(24)
        self.gridResumo.setVerticalSpacing(18)
        self.gridResumo.setObjectName("gridResumo")

        self.lblPdvLabel = QtWidgets.QLabel(self.resumoCard)
        self.lblPdvLabel.setProperty("role", "campoLabel")
        self.gridResumo.addWidget(self.lblPdvLabel, 0, 0, 1, 1)
        self.lblOperadorLabel = QtWidgets.QLabel(self.resumoCard)
        self.lblOperadorLabel.setProperty("role", "campoLabel")
        self.gridResumo.addWidget(self.lblOperadorLabel, 0, 1, 1, 1)
        self.lblAberturaLabel = QtWidgets.QLabel(self.resumoCard)
        self.lblAberturaLabel.setProperty("role", "campoLabel")
        self.gridResumo.addWidget(self.lblAberturaLabel, 0, 2, 1, 1)

        self.lblPdvValor = QtWidgets.QLabel(self.resumoCard)
        self.lblPdvValor.setProperty("role", "campoValorPequeno")
        self.gridResumo.addWidget(self.lblPdvValor, 1, 0, 1, 1)
        self.lblOperadorValor = QtWidgets.QLabel(self.resumoCard)
        self.lblOperadorValor.setProperty("role", "campoValorPequeno")
        self.gridResumo.addWidget(self.lblOperadorValor, 1, 1, 1, 1)
        self.lblAberturaValor = QtWidgets.QLabel(self.resumoCard)
        self.lblAberturaValor.setProperty("role", "campoValorPequeno")
        self.gridResumo.addWidget(self.lblAberturaValor, 1, 2, 1, 1)

        self._adicionar_metricas()
        self.verticalLayout.addWidget(self.resumoCard)

        self.pagamentoCard = QtWidgets.QFrame(ResumoCaixaAtualDialog)
        self.pagamentoCard.setObjectName("pagamentoCard")
        self.pagamentoLayout = QtWidgets.QVBoxLayout(self.pagamentoCard)
        self.pagamentoLayout.setContentsMargins(24, 22, 24, 22)
        self.pagamentoLayout.setSpacing(12)
        self.pagamentoLayout.setObjectName("pagamentoLayout")
        self.pagamentoTitulo = QtWidgets.QLabel(self.pagamentoCard)
        self.pagamentoTitulo.setObjectName("pagamentoTitulo")
        self.pagamentoLayout.addWidget(self.pagamentoTitulo)
        self.tablePagamentos = QtWidgets.QTableWidget(self.pagamentoCard)
        self.tablePagamentos.setObjectName("tablePagamentos")
        self.tablePagamentos.setColumnCount(3)
        self.tablePagamentos.setRowCount(0)
        self.tablePagamentos.setHorizontalHeaderLabels(["Forma", "Qtd.", "Total"])
        self.tablePagamentos.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tablePagamentos.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tablePagamentos.setAlternatingRowColors(True)
        self.tablePagamentos.verticalHeader().setVisible(False)
        self.tablePagamentos.horizontalHeader().setStretchLastSection(False)
        self.tablePagamentos.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tablePagamentos.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tablePagamentos.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tablePagamentos.setStyleSheet(
            """
            QTableWidget {
                background-color: #f7fbff;
                border: 1px solid #d8e7f4;
                border-radius: 10px;
                gridline-color: #e4eef6;
                color: #173a5f;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #eef5fb;
                color: #2b5a84;
                font-size: 11px;
                font-weight: 700;
                border: none;
                border-bottom: 1px solid #d8e7f4;
                padding: 8px;
            }
            """
        )
        self.pagamentoLayout.addWidget(self.tablePagamentos)
        self.lblPagamentosVazio = QtWidgets.QLabel(self.pagamentoCard)
        self.lblPagamentosVazio.setProperty("role", "campoValorPequeno")
        self.lblPagamentosVazio.setWordWrap(True)
        self.pagamentoLayout.addWidget(self.lblPagamentosVazio)
        self.verticalLayout.addWidget(self.pagamentoCard, 1)

        self.frameAcoes = QtWidgets.QWidget(ResumoCaixaAtualDialog)
        self.acoesLayout = QtWidgets.QHBoxLayout(self.frameAcoes)
        self.acoesLayout.setContentsMargins(0, 0, 0, 0)
        spacerAcoes = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.acoesLayout.addItem(spacerAcoes)
        self.btnFechar = QtWidgets.QPushButton(self.frameAcoes)
        self.btnFechar.setObjectName("btnFechar")
        self.acoesLayout.addWidget(self.btnFechar)
        self.verticalLayout.addWidget(self.frameAcoes)

        self.retranslateUi(ResumoCaixaAtualDialog)
        QtCore.QMetaObject.connectSlotsByName(ResumoCaixaAtualDialog)

    def _adicionar_metricas(self):
        campos = [
            ("lblFundoInicialLabel", "lblFundoInicialValor"),
            ("lblVendasDiaLabel", "lblVendasDiaValor"),
            ("lblFaturamentoTotalLabel", "lblFaturamentoTotalValor"),
            ("lblFaturamentoDinheiroLabel", "lblFaturamentoDinheiroValor"),
            ("lblSangriasLabel", "lblSangriasValor"),
            ("lblSuprimentosLabel", "lblSuprimentosValor"),
            ("lblTrocoLabel", "lblTrocoValor"),
            ("lblEsperadoLabel", "lblEsperadoValor"),
            ("lblSaldoAtualLabel", "lblSaldoAtualValor"),
        ]
        for indice, (nome_label, nome_valor) in enumerate(campos):
            base_row = 2 + (indice // 3) * 2
            col = indice % 3
            label = QtWidgets.QLabel(self.resumoCard)
            label.setProperty("role", "campoLabel")
            setattr(self, nome_label, label)
            self.gridResumo.addWidget(label, base_row, col, 1, 1)
            valor = QtWidgets.QLabel(self.resumoCard)
            valor.setProperty("role", "campoValor")
            valor.setWordWrap(True)
            setattr(self, nome_valor, valor)
            self.gridResumo.addWidget(valor, base_row + 1, col, 1, 1)

    def retranslateUi(self, ResumoCaixaAtualDialog):
        _translate = QtCore.QCoreApplication.translate
        ResumoCaixaAtualDialog.setWindowTitle(_translate("ResumoCaixaAtualDialog", "Resumo do Caixa Atual"))
        self.tituloDialog.setText(_translate("ResumoCaixaAtualDialog", "Resumo do Caixa Atual"))
        self.subtituloDialog.setText(_translate("ResumoCaixaAtualDialog", "Acompanhe rapidamente a sessao de caixa aberta e os totais operacionais."))
        self.lblStatusBadge.setText(_translate("ResumoCaixaAtualDialog", "Aberto"))
        self.lblPdvLabel.setText(_translate("ResumoCaixaAtualDialog", "PDV"))
        self.lblOperadorLabel.setText(_translate("ResumoCaixaAtualDialog", "OPERADOR"))
        self.lblAberturaLabel.setText(_translate("ResumoCaixaAtualDialog", "ABERTURA"))
        self.lblFundoInicialLabel.setText(_translate("ResumoCaixaAtualDialog", "FUNDO INICIAL"))
        self.lblVendasDiaLabel.setText(_translate("ResumoCaixaAtualDialog", "VENDAS DO DIA"))
        self.lblFaturamentoTotalLabel.setText(_translate("ResumoCaixaAtualDialog", "FATURAMENTO TOTAL"))
        self.lblFaturamentoDinheiroLabel.setText(_translate("ResumoCaixaAtualDialog", "FATURAMENTO EM DINHEIRO"))
        self.lblSangriasLabel.setText(_translate("ResumoCaixaAtualDialog", "SANGRIAS"))
        self.lblSuprimentosLabel.setText(_translate("ResumoCaixaAtualDialog", "SUPRIMENTOS"))
        self.lblTrocoLabel.setText(_translate("ResumoCaixaAtualDialog", "REFORCO DE TROCO"))
        self.lblEsperadoLabel.setText(_translate("ResumoCaixaAtualDialog", "DINHEIRO ESPERADO"))
        self.lblSaldoAtualLabel.setText(_translate("ResumoCaixaAtualDialog", "SALDO ATUAL"))
        self.pagamentoTitulo.setText(_translate("ResumoCaixaAtualDialog", "Totais por forma de pagamento"))
        self.btnFechar.setText(_translate("ResumoCaixaAtualDialog", "Fechar"))
