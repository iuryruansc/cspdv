# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_CadastroPromocao(object):
    def setupUi(self, CadastroPromocao):
        CadastroPromocao.setObjectName("CadastroPromocao")
        CadastroPromocao.resize(860, 720)
        CadastroPromocao.setMinimumSize(QtCore.QSize(820, 680))
        CadastroPromocao.setStyleSheet(
            """
            QDialog {
                background-color: #eef4f8;
                color: #18324a;
                font-family: "Segoe UI";
            }
            QFrame#frameHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #153552, stop:0.55 #1d4c74, stop:1 #2f75b0);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            QLabel#lblBadge {
                color: #ffe59d;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 14px;
                border-radius: 8px;
                background-color: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.18);
            }
            QLabel#lblFormTitle, QLabel#lblFormHint {
                color: white;
            }
            QLabel#lblFormTitle {
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#lblFormHint {
                font-size: 12px;
            }
            QFrame#frameCard {
                background-color: white;
                border: 1px solid #d6e2ec;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
            QLabel[sectionLabel="true"] {
                color: #244866;
                font-size: 12px;
                font-weight: 700;
            }
            QLabel[sectionTitle="true"] {
                color: #153552;
                font-size: 13px;
                font-weight: 800;
            }
            QLineEdit, QComboBox, QDateTimeEdit, QTextEdit {
                background-color: #f7fafc;
                border: 1px solid #c8d7e6;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
                color: #18324a;
            }
            QLineEdit, QComboBox, QDateTimeEdit {
                min-height: 42px;
            }
            QTextEdit {
                min-height: 96px;
            }
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QTextEdit:focus {
                border: 2px solid #3a8ad3;
                background-color: white;
            }
            QCheckBox {
                font-size: 12px;
                font-weight: 600;
                color: #244866;
            }
            QPushButton {
                min-height: 40px;
                border: none;
                border-radius: 10px;
                padding: 0 18px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btnSalvar {
                background-color: #2f80c9;
                color: white;
            }
            QPushButton#btnSalvar:hover {
                background-color: #276faa;
            }
            QPushButton#btnLimpar {
                background-color: #eef3f8;
                color: #315676;
                border: 1px solid #c6d6e5;
            }
            QPushButton#btnVoltar {
                background-color: #d92b2b;
                color: white;
            }
            """
        )
        self.verticalLayout = QtWidgets.QVBoxLayout(CadastroPromocao)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frameHeader = QtWidgets.QFrame(CadastroPromocao)
        self.frameHeader.setObjectName("frameHeader")
        self.headerLayout = QtWidgets.QVBoxLayout(self.frameHeader)
        self.headerLayout.setContentsMargins(24, 20, 24, 20)
        self.headerLayout.setSpacing(8)
        self.headerLayout.setObjectName("headerLayout")
        self.lblBadge = QtWidgets.QLabel(self.frameHeader)
        self.lblBadge.setObjectName("lblBadge")
        self.headerLayout.addWidget(self.lblBadge, 0, QtCore.Qt.AlignLeft)
        self.lblFormTitle = QtWidgets.QLabel(self.frameHeader)
        self.lblFormTitle.setObjectName("lblFormTitle")
        self.headerLayout.addWidget(self.lblFormTitle)
        self.lblFormHint = QtWidgets.QLabel(self.frameHeader)
        self.lblFormHint.setObjectName("lblFormHint")
        self.headerLayout.addWidget(self.lblFormHint)
        self.verticalLayout.addWidget(self.frameHeader)

        self.frameCard = QtWidgets.QFrame(CadastroPromocao)
        self.frameCard.setObjectName("frameCard")
        self.cardLayout = QtWidgets.QVBoxLayout(self.frameCard)
        self.cardLayout.setContentsMargins(26, 24, 26, 24)
        self.cardLayout.setSpacing(20)
        self.cardLayout.setObjectName("cardLayout")

        self.gridCabecalho = QtWidgets.QGridLayout()
        self.gridCabecalho.setHorizontalSpacing(14)
        self.gridCabecalho.setVerticalSpacing(12)
        self.gridCabecalho.setObjectName("gridCabecalho")
        self.lblCodigo = QtWidgets.QLabel(self.frameCard)
        self.lblCodigo.setProperty("sectionLabel", "true")
        self.lblCodigo.setObjectName("lblCodigo")
        self.gridCabecalho.addWidget(self.lblCodigo, 0, 0, 1, 1)
        self.lineEditCodigo = QtWidgets.QLineEdit(self.frameCard)
        self.lineEditCodigo.setMinimumHeight(42)
        self.lineEditCodigo.setMaximumHeight(42)
        self.lineEditCodigo.setReadOnly(True)
        self.lineEditCodigo.setObjectName("lineEditCodigo")
        self.gridCabecalho.addWidget(self.lineEditCodigo, 1, 0, 1, 1)
        self.lblNomePromocao = QtWidgets.QLabel(self.frameCard)
        self.lblNomePromocao.setProperty("sectionLabel", "true")
        self.lblNomePromocao.setObjectName("lblNomePromocao")
        self.gridCabecalho.addWidget(self.lblNomePromocao, 0, 1, 1, 3)
        self.lineEditNomePromocao = QtWidgets.QLineEdit(self.frameCard)
        self.lineEditNomePromocao.setMinimumHeight(42)
        self.lineEditNomePromocao.setMaximumHeight(42)
        self.lineEditNomePromocao.setObjectName("lineEditNomePromocao")
        self.gridCabecalho.addWidget(self.lineEditNomePromocao, 1, 1, 1, 3)
        self.lblClassificacao = QtWidgets.QLabel(self.frameCard)
        self.lblClassificacao.setProperty("sectionLabel", "true")
        self.lblClassificacao.setObjectName("lblClassificacao")
        self.gridCabecalho.addWidget(self.lblClassificacao, 2, 0, 1, 1)
        self.comboClassificacao = QtWidgets.QComboBox(self.frameCard)
        self.comboClassificacao.setMinimumHeight(42)
        self.comboClassificacao.setMaximumHeight(42)
        self.comboClassificacao.setObjectName("comboClassificacao")
        self.comboClassificacao.addItem("")
        self.comboClassificacao.addItem("")
        self.gridCabecalho.addWidget(self.comboClassificacao, 3, 0, 1, 1)
        self.lblTipoDesconto = QtWidgets.QLabel(self.frameCard)
        self.lblTipoDesconto.setProperty("sectionLabel", "true")
        self.lblTipoDesconto.setObjectName("lblTipoDesconto")
        self.gridCabecalho.addWidget(self.lblTipoDesconto, 2, 1, 1, 1)
        self.comboTipoDesconto = QtWidgets.QComboBox(self.frameCard)
        self.comboTipoDesconto.setMinimumHeight(42)
        self.comboTipoDesconto.setMaximumHeight(42)
        self.comboTipoDesconto.setObjectName("comboTipoDesconto")
        self.comboTipoDesconto.addItem("")
        self.comboTipoDesconto.addItem("")
        self.comboTipoDesconto.addItem("")
        self.gridCabecalho.addWidget(self.comboTipoDesconto, 3, 1, 1, 1)
        self.lblStatus = QtWidgets.QLabel(self.frameCard)
        self.lblStatus.setProperty("sectionLabel", "true")
        self.lblStatus.setObjectName("lblStatus")
        self.gridCabecalho.addWidget(self.lblStatus, 2, 2, 1, 1)
        self.comboStatus = QtWidgets.QComboBox(self.frameCard)
        self.comboStatus.setMinimumHeight(42)
        self.comboStatus.setMaximumHeight(42)
        self.comboStatus.setObjectName("comboStatus")
        self.comboStatus.addItem("")
        self.comboStatus.addItem("")
        self.comboStatus.addItem("")
        self.comboStatus.addItem("")
        self.comboStatus.addItem("")
        self.gridCabecalho.addWidget(self.comboStatus, 3, 2, 1, 1)
        self.gridCabecalho.setColumnStretch(0, 2)
        self.gridCabecalho.setColumnStretch(1, 2)
        self.gridCabecalho.setColumnStretch(2, 1)
        self.gridCabecalho.setColumnStretch(3, 1)
        self.gridCabecalho.setRowMinimumHeight(1, 48)
        self.gridCabecalho.setRowMinimumHeight(3, 48)
        self.cardLayout.addLayout(self.gridCabecalho)

        self.lblSecaoVigencia = QtWidgets.QLabel(self.frameCard)
        self.lblSecaoVigencia.setProperty("sectionTitle", "true")
        self.lblSecaoVigencia.setObjectName("lblSecaoVigencia")
        self.cardLayout.addWidget(self.lblSecaoVigencia)
        self.gridVigencia = QtWidgets.QGridLayout()
        self.gridVigencia.setHorizontalSpacing(14)
        self.gridVigencia.setVerticalSpacing(12)
        self.gridVigencia.setObjectName("gridVigencia")
        self.lblDataInicio = QtWidgets.QLabel(self.frameCard)
        self.lblDataInicio.setProperty("sectionLabel", "true")
        self.lblDataInicio.setObjectName("lblDataInicio")
        self.gridVigencia.addWidget(self.lblDataInicio, 0, 0, 1, 1)
        self.dateTimeInicio = QtWidgets.QDateTimeEdit(self.frameCard)
        self.dateTimeInicio.setMinimumHeight(42)
        self.dateTimeInicio.setMaximumHeight(42)
        self.dateTimeInicio.setCalendarPopup(True)
        self.dateTimeInicio.setObjectName("dateTimeInicio")
        self.gridVigencia.addWidget(self.dateTimeInicio, 1, 0, 1, 1)
        self.lblDataFim = QtWidgets.QLabel(self.frameCard)
        self.lblDataFim.setProperty("sectionLabel", "true")
        self.lblDataFim.setObjectName("lblDataFim")
        self.gridVigencia.addWidget(self.lblDataFim, 0, 1, 1, 1)
        self.dateTimeFim = QtWidgets.QDateTimeEdit(self.frameCard)
        self.dateTimeFim.setMinimumHeight(42)
        self.dateTimeFim.setMaximumHeight(42)
        self.dateTimeFim.setCalendarPopup(True)
        self.dateTimeFim.setObjectName("dateTimeFim")
        self.gridVigencia.addWidget(self.dateTimeFim, 1, 1, 1, 1)
        self.checkBoxCumulativa = QtWidgets.QCheckBox(self.frameCard)
        self.checkBoxCumulativa.setObjectName("checkBoxCumulativa")
        self.gridVigencia.addWidget(self.checkBoxCumulativa, 1, 2, 1, 1)
        self.checkBoxAtiva = QtWidgets.QCheckBox(self.frameCard)
        self.checkBoxAtiva.setObjectName("checkBoxAtiva")
        self.gridVigencia.addWidget(self.checkBoxAtiva, 1, 3, 1, 1)
        self.gridVigencia.setColumnStretch(0, 2)
        self.gridVigencia.setColumnStretch(1, 2)
        self.gridVigencia.setColumnStretch(2, 1)
        self.gridVigencia.setColumnStretch(3, 1)
        self.gridVigencia.setRowMinimumHeight(1, 48)
        self.cardLayout.addLayout(self.gridVigencia)

        self.lblSecaoValores = QtWidgets.QLabel(self.frameCard)
        self.lblSecaoValores.setProperty("sectionTitle", "true")
        self.lblSecaoValores.setObjectName("lblSecaoValores")
        self.cardLayout.addWidget(self.lblSecaoValores)
        self.gridValores = QtWidgets.QGridLayout()
        self.gridValores.setHorizontalSpacing(14)
        self.gridValores.setVerticalSpacing(12)
        self.gridValores.setObjectName("gridValores")
        self.lblDescontoPercentual = QtWidgets.QLabel(self.frameCard)
        self.lblDescontoPercentual.setProperty("sectionLabel", "true")
        self.lblDescontoPercentual.setObjectName("lblDescontoPercentual")
        self.gridValores.addWidget(self.lblDescontoPercentual, 0, 0, 1, 1)
        self.lineEditDescontoPercentual = QtWidgets.QLineEdit(self.frameCard)
        self.lineEditDescontoPercentual.setMinimumHeight(42)
        self.lineEditDescontoPercentual.setMaximumHeight(42)
        self.lineEditDescontoPercentual.setObjectName("lineEditDescontoPercentual")
        self.gridValores.addWidget(self.lineEditDescontoPercentual, 1, 0, 1, 1)
        self.lblDescontoValor = QtWidgets.QLabel(self.frameCard)
        self.lblDescontoValor.setProperty("sectionLabel", "true")
        self.lblDescontoValor.setObjectName("lblDescontoValor")
        self.gridValores.addWidget(self.lblDescontoValor, 0, 1, 1, 1)
        self.lineEditDescontoValor = QtWidgets.QLineEdit(self.frameCard)
        self.lineEditDescontoValor.setMinimumHeight(42)
        self.lineEditDescontoValor.setMaximumHeight(42)
        self.lineEditDescontoValor.setObjectName("lineEditDescontoValor")
        self.gridValores.addWidget(self.lineEditDescontoValor, 1, 1, 1, 1)
        self.lblPrecoFixo = QtWidgets.QLabel(self.frameCard)
        self.lblPrecoFixo.setProperty("sectionLabel", "true")
        self.lblPrecoFixo.setObjectName("lblPrecoFixo")
        self.gridValores.addWidget(self.lblPrecoFixo, 0, 2, 1, 1)
        self.lineEditPrecoFixo = QtWidgets.QLineEdit(self.frameCard)
        self.lineEditPrecoFixo.setMinimumHeight(42)
        self.lineEditPrecoFixo.setMaximumHeight(42)
        self.lineEditPrecoFixo.setObjectName("lineEditPrecoFixo")
        self.gridValores.addWidget(self.lineEditPrecoFixo, 1, 2, 1, 1)
        self.gridValores.setColumnStretch(0, 1)
        self.gridValores.setColumnStretch(1, 1)
        self.gridValores.setColumnStretch(2, 1)
        self.gridValores.setRowMinimumHeight(1, 48)
        self.cardLayout.addLayout(self.gridValores)

        self.lblDescricao = QtWidgets.QLabel(self.frameCard)
        self.lblDescricao.setProperty("sectionLabel", "true")
        self.lblDescricao.setObjectName("lblDescricao")
        self.cardLayout.addWidget(self.lblDescricao)
        self.textEditDescricao = QtWidgets.QTextEdit(self.frameCard)
        self.textEditDescricao.setMinimumHeight(90)
        self.textEditDescricao.setMaximumHeight(110)
        self.textEditDescricao.setObjectName("textEditDescricao")
        self.cardLayout.addWidget(self.textEditDescricao)
        self.lblObservacao = QtWidgets.QLabel(self.frameCard)
        self.lblObservacao.setProperty("sectionLabel", "true")
        self.lblObservacao.setObjectName("lblObservacao")
        self.cardLayout.addWidget(self.lblObservacao)
        self.textEditObservacao = QtWidgets.QTextEdit(self.frameCard)
        self.textEditObservacao.setMinimumHeight(90)
        self.textEditObservacao.setMaximumHeight(110)
        self.textEditObservacao.setObjectName("textEditObservacao")
        self.cardLayout.addWidget(self.textEditObservacao)

        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setSpacing(10)
        self.buttonsLayout.setObjectName("buttonsLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonsLayout.addItem(spacerItem)
        self.btnLimpar = QtWidgets.QPushButton(self.frameCard)
        self.btnLimpar.setObjectName("btnLimpar")
        self.buttonsLayout.addWidget(self.btnLimpar)
        self.btnVoltar = QtWidgets.QPushButton(self.frameCard)
        self.btnVoltar.setObjectName("btnVoltar")
        self.buttonsLayout.addWidget(self.btnVoltar)
        self.btnSalvar = QtWidgets.QPushButton(self.frameCard)
        self.btnSalvar.setObjectName("btnSalvar")
        self.buttonsLayout.addWidget(self.btnSalvar)
        self.cardLayout.addLayout(self.buttonsLayout)

        self.verticalLayout.addWidget(self.frameCard)

        self.retranslateUi(CadastroPromocao)
        QtCore.QMetaObject.connectSlotsByName(CadastroPromocao)

    def retranslateUi(self, CadastroPromocao):
        _translate = QtCore.QCoreApplication.translate
        CadastroPromocao.setWindowTitle(_translate("CadastroPromocao", "CSPdv - Cadastro de Promocao"))
        self.lblBadge.setText(_translate("CadastroPromocao", "CADASTRO DE PROMOCAO"))
        self.lblFormTitle.setText(_translate("CadastroPromocao", "Nova Promocao"))
        self.lblFormHint.setText(_translate("CadastroPromocao", "Cadastre a base da promocao ou campanha antes de vincular produtos e regras avancadas."))
        self.lblCodigo.setText(_translate("CadastroPromocao", "Codigo"))
        self.lineEditCodigo.setText(_translate("CadastroPromocao", "Auto-gerado"))
        self.lblNomePromocao.setText(_translate("CadastroPromocao", "Nome da Promocao *"))
        self.lblClassificacao.setText(_translate("CadastroPromocao", "Classificacao *"))
        self.comboClassificacao.setItemText(0, _translate("CadastroPromocao", "PROMOCAO"))
        self.comboClassificacao.setItemText(1, _translate("CadastroPromocao", "CAMPANHA"))
        self.lblTipoDesconto.setText(_translate("CadastroPromocao", "Tipo de Desconto *"))
        self.comboTipoDesconto.setItemText(0, _translate("CadastroPromocao", "PERCENTUAL"))
        self.comboTipoDesconto.setItemText(1, _translate("CadastroPromocao", "VALOR"))
        self.comboTipoDesconto.setItemText(2, _translate("CadastroPromocao", "PRECO_FIXO"))
        self.lblStatus.setText(_translate("CadastroPromocao", "Status *"))
        self.comboStatus.setItemText(0, _translate("CadastroPromocao", "RASCUNHO"))
        self.comboStatus.setItemText(1, _translate("CadastroPromocao", "AGENDADA"))
        self.comboStatus.setItemText(2, _translate("CadastroPromocao", "ATIVA"))
        self.comboStatus.setItemText(3, _translate("CadastroPromocao", "ENCERRADA"))
        self.comboStatus.setItemText(4, _translate("CadastroPromocao", "CANCELADA"))
        self.lblSecaoVigencia.setText(_translate("CadastroPromocao", "Vigencia"))
        self.lblDataInicio.setText(_translate("CadastroPromocao", "Inicio *"))
        self.lblDataFim.setText(_translate("CadastroPromocao", "Fim *"))
        self.checkBoxCumulativa.setText(_translate("CadastroPromocao", "Promocao cumulativa"))
        self.checkBoxAtiva.setText(_translate("CadastroPromocao", "Registro ativo"))
        self.lblSecaoValores.setText(_translate("CadastroPromocao", "Regra Financeira"))
        self.lblDescontoPercentual.setText(_translate("CadastroPromocao", "Desconto Percentual (%)"))
        self.lblDescontoValor.setText(_translate("CadastroPromocao", "Desconto em Valor (R$)"))
        self.lblPrecoFixo.setText(_translate("CadastroPromocao", "Preco Fixo Promocional (R$)"))
        self.lblDescricao.setText(_translate("CadastroPromocao", "Descricao"))
        self.lblObservacao.setText(_translate("CadastroPromocao", "Observacao"))
        self.btnLimpar.setText(_translate("CadastroPromocao", "Limpar"))
        self.btnVoltar.setText(_translate("CadastroPromocao", "Voltar"))
        self.btnSalvar.setText(_translate("CadastroPromocao", "Salvar"))
