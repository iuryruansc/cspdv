from PyQt5 import QtCore, QtWidgets


class Ui_ConsultaReembolsoDialog(object):
    def setupUi(self, ConsultaReembolsoDialog):
        ConsultaReembolsoDialog.setObjectName("ConsultaReembolsoDialog")
        ConsultaReembolsoDialog.resize(940, 760)
        ConsultaReembolsoDialog.setMinimumSize(QtCore.QSize(900, 700))
        ConsultaReembolsoDialog.setStyleSheet(
            "QDialog{background-color:#edf4fb;}"
            "QFrame#frameHeader,QFrame#frameCard,QFrame#frameObservacao,QFrame#frameItens,QFrame#framePagamentos{background-color:#ffffff;border:1px solid #c8d9ea;border-radius:12px;}"
            "QLabel{color:#153d68;font-size:12px;}"
            "QLabel#lblTitulo{font-size:24px;font-weight:bold;color:#123f6f;}"
            "QLabel#lblSubtitulo{font-size:12px;color:#5c7c9c;}"
            "QLabel.infoLabel{font-size:11px;font-weight:bold;color:#557596;letter-spacing:0.6px;}"
            "QLabel.infoValue{font-size:16px;font-weight:bold;color:#123f6f;}"
            "QLabel#lblStatusValor[status='concluido']{color:#027a48;}"
            "QLabel#lblStatusValor[status='cancelado']{color:#b42318;}"
            "QPlainTextEdit{border:none;background-color:#f8fbfe;color:#24415e;font-size:12px;padding:8px;}"
            "QTableWidget{border:none;background-color:white;gridline-color:#dce8f0;font-size:12px;}"
            "QHeaderView::section{background-color:#f0f6fc;color:#1a3a5c;font-size:11px;font-weight:bold;border:none;border-right:1px solid #dce8f0;border-bottom:2px solid #3585c8;padding:5px 6px;}"
            "QPushButton{min-height:42px;border-radius:8px;font-size:13px;font-weight:bold;padding:0 18px;background-color:#2f7ed1;border:1px solid #2568af;color:#ffffff;}"
            "QPushButton:hover{background-color:#3a8ae0;}"
        )
        self.verticalLayout = QtWidgets.QVBoxLayout(ConsultaReembolsoDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(12)

        self.frameHeader = QtWidgets.QFrame(ConsultaReembolsoDialog)
        self.frameHeader.setObjectName("frameHeader")
        self.headerLayout = QtWidgets.QVBoxLayout(self.frameHeader)
        self.headerLayout.setContentsMargins(22, 20, 22, 18)
        self.headerLayout.setSpacing(8)
        self.lblTitulo = QtWidgets.QLabel(self.frameHeader)
        self.lblTitulo.setObjectName("lblTitulo")
        self.headerLayout.addWidget(self.lblTitulo)
        self.lblSubtitulo = QtWidgets.QLabel(self.frameHeader)
        self.lblSubtitulo.setWordWrap(True)
        self.lblSubtitulo.setObjectName("lblSubtitulo")
        self.headerLayout.addWidget(self.lblSubtitulo)
        self.verticalLayout.addWidget(self.frameHeader)

        self.frameCard = QtWidgets.QFrame(ConsultaReembolsoDialog)
        self.frameCard.setObjectName("frameCard")
        self.cardLayout = QtWidgets.QGridLayout(self.frameCard)
        self.cardLayout.setContentsMargins(22, 18, 22, 18)
        self.cardLayout.setHorizontalSpacing(20)
        self.cardLayout.setVerticalSpacing(10)

        labels = [
            ("lblReembolsoLabel", "lblReembolsoValor"),
            ("lblVendaLabel", "lblVendaValor"),
            ("lblTipoLabel", "lblTipoValor"),
            ("lblStatusLabel", "lblStatusValor"),
            ("lblDataHoraLabel", "lblDataHoraValor"),
            ("lblOperadorLabel", "lblOperadorValor"),
            ("lblTotalLabel", "lblTotalValor"),
            ("lblMotivoLabel", "lblMotivoValor"),
        ]
        positions = [
            (0, 0), (0, 1), (0, 2), (0, 3),
            (2, 0), (2, 1), (2, 2), (2, 3),
        ]
        for (label_name, value_name), (row, col) in zip(labels, positions):
            label = QtWidgets.QLabel(self.frameCard)
            label.setObjectName(label_name)
            label.setProperty("class", "infoLabel")
            value = QtWidgets.QLabel(self.frameCard)
            value.setObjectName(value_name)
            value.setProperty("class", "infoValue")
            self.cardLayout.addWidget(label, row, col, 1, 1)
            self.cardLayout.addWidget(value, row + 1, col, 1, 1)
            setattr(self, label_name, label)
            setattr(self, value_name, value)
        self.verticalLayout.addWidget(self.frameCard)

        self.frameObservacao = QtWidgets.QFrame(ConsultaReembolsoDialog)
        self.frameObservacao.setObjectName("frameObservacao")
        self.observacaoLayout = QtWidgets.QVBoxLayout(self.frameObservacao)
        self.observacaoLayout.setContentsMargins(22, 16, 22, 16)
        self.observacaoLayout.setSpacing(8)
        self.lblObservacao = QtWidgets.QLabel(self.frameObservacao)
        self.lblObservacao.setProperty("class", "infoLabel")
        self.lblObservacao.setObjectName("lblObservacao")
        self.observacaoLayout.addWidget(self.lblObservacao)
        self.plainObservacao = QtWidgets.QPlainTextEdit(self.frameObservacao)
        self.plainObservacao.setReadOnly(True)
        self.plainObservacao.setMaximumHeight(88)
        self.plainObservacao.setObjectName("plainObservacao")
        self.observacaoLayout.addWidget(self.plainObservacao)
        self.verticalLayout.addWidget(self.frameObservacao)

        self.frameItens = QtWidgets.QFrame(ConsultaReembolsoDialog)
        self.frameItens.setObjectName("frameItens")
        self.itensLayout = QtWidgets.QVBoxLayout(self.frameItens)
        self.itensLayout.setContentsMargins(0, 0, 0, 0)
        self.itensLayout.setSpacing(0)
        self.lblItens = QtWidgets.QLabel(self.frameItens)
        self.lblItens.setStyleSheet(
            "background-color:#f0f6fc;color:#1a3a5c;font-size:13px;font-weight:bold;"
            "padding:8px 12px;border-bottom:1px solid #d8e3ee;"
        )
        self.lblItens.setObjectName("lblItens")
        self.itensLayout.addWidget(self.lblItens)
        self.tableItens = QtWidgets.QTableWidget(self.frameItens)
        self.tableItens.setRowCount(0)
        self.tableItens.setColumnCount(5)
        self.tableItens.setObjectName("tableItens")
        for i in range(5):
            item = QtWidgets.QTableWidgetItem()
            self.tableItens.setHorizontalHeaderItem(i, item)
        self.tableItens.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableItens.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.tableItens.verticalHeader().setVisible(False)
        self.itensLayout.addWidget(self.tableItens)
        self.verticalLayout.addWidget(self.frameItens)

        self.framePagamentos = QtWidgets.QFrame(ConsultaReembolsoDialog)
        self.framePagamentos.setObjectName("framePagamentos")
        self.pagamentosLayout = QtWidgets.QVBoxLayout(self.framePagamentos)
        self.pagamentosLayout.setContentsMargins(0, 0, 0, 0)
        self.pagamentosLayout.setSpacing(0)
        self.lblPagamentos = QtWidgets.QLabel(self.framePagamentos)
        self.lblPagamentos.setStyleSheet(
            "background-color:#f0f6fc;color:#1a3a5c;font-size:13px;font-weight:bold;"
            "padding:8px 12px;border-bottom:1px solid #d8e3ee;"
        )
        self.lblPagamentos.setObjectName("lblPagamentos")
        self.pagamentosLayout.addWidget(self.lblPagamentos)
        self.tablePagamentos = QtWidgets.QTableWidget(self.framePagamentos)
        self.tablePagamentos.setRowCount(0)
        self.tablePagamentos.setColumnCount(3)
        self.tablePagamentos.setObjectName("tablePagamentos")
        for i in range(3):
            item = QtWidgets.QTableWidgetItem()
            self.tablePagamentos.setHorizontalHeaderItem(i, item)
        self.tablePagamentos.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tablePagamentos.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tablePagamentos.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tablePagamentos.verticalHeader().setVisible(False)
        self.pagamentosLayout.addWidget(self.tablePagamentos)
        self.verticalLayout.addWidget(self.framePagamentos)

        self.bottomLayout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.bottomLayout.addItem(spacer)
        self.btnAbrirVenda = QtWidgets.QPushButton(ConsultaReembolsoDialog)
        self.btnAbrirVenda.setObjectName("btnAbrirVenda")
        self.bottomLayout.addWidget(self.btnAbrirVenda)
        self.btnFechar = QtWidgets.QPushButton(ConsultaReembolsoDialog)
        self.btnFechar.setObjectName("btnFechar")
        self.bottomLayout.addWidget(self.btnFechar)
        self.verticalLayout.addLayout(self.bottomLayout)

        self.retranslateUi(ConsultaReembolsoDialog)
        QtCore.QMetaObject.connectSlotsByName(ConsultaReembolsoDialog)

    def retranslateUi(self, ConsultaReembolsoDialog):
        _translate = QtCore.QCoreApplication.translate
        ConsultaReembolsoDialog.setWindowTitle(_translate("ConsultaReembolsoDialog", "CSPdv - Detalhes do Reembolso"))
        self.lblTitulo.setText(_translate("ConsultaReembolsoDialog", "Detalhes do Reembolso"))
        self.lblSubtitulo.setText(_translate("ConsultaReembolsoDialog", "Visualize itens, pagamentos e informacoes do reembolso registrado."))
        self.lblReembolsoLabel.setText(_translate("ConsultaReembolsoDialog", "REEMBOLSO"))
        self.lblReembolsoValor.setText(_translate("ConsultaReembolsoDialog", "#0"))
        self.lblVendaLabel.setText(_translate("ConsultaReembolsoDialog", "VENDA"))
        self.lblVendaValor.setText(_translate("ConsultaReembolsoDialog", "#0"))
        self.lblTipoLabel.setText(_translate("ConsultaReembolsoDialog", "TIPO"))
        self.lblTipoValor.setText(_translate("ConsultaReembolsoDialog", "-"))
        self.lblStatusLabel.setText(_translate("ConsultaReembolsoDialog", "STATUS"))
        self.lblStatusValor.setText(_translate("ConsultaReembolsoDialog", "-"))
        self.lblDataHoraLabel.setText(_translate("ConsultaReembolsoDialog", "DATA / HORA"))
        self.lblDataHoraValor.setText(_translate("ConsultaReembolsoDialog", "--/--/---- --:--"))
        self.lblOperadorLabel.setText(_translate("ConsultaReembolsoDialog", "OPERADOR"))
        self.lblOperadorValor.setText(_translate("ConsultaReembolsoDialog", "-"))
        self.lblTotalLabel.setText(_translate("ConsultaReembolsoDialog", "VALOR TOTAL"))
        self.lblTotalValor.setText(_translate("ConsultaReembolsoDialog", "R$ 0,00"))
        self.lblMotivoLabel.setText(_translate("ConsultaReembolsoDialog", "MOTIVO"))
        self.lblMotivoValor.setText(_translate("ConsultaReembolsoDialog", "-"))
        self.lblObservacao.setText(_translate("ConsultaReembolsoDialog", "OBSERVACAO"))
        self.lblItens.setText(_translate("ConsultaReembolsoDialog", "Itens Reembolsados"))
        item = self.tableItens.horizontalHeaderItem(0)
        item.setText(_translate("ConsultaReembolsoDialog", "Codigo"))
        item = self.tableItens.horizontalHeaderItem(1)
        item.setText(_translate("ConsultaReembolsoDialog", "Produto"))
        item = self.tableItens.horizontalHeaderItem(2)
        item.setText(_translate("ConsultaReembolsoDialog", "Qtd"))
        item = self.tableItens.horizontalHeaderItem(3)
        item.setText(_translate("ConsultaReembolsoDialog", "Vl. Unitario"))
        item = self.tableItens.horizontalHeaderItem(4)
        item.setText(_translate("ConsultaReembolsoDialog", "Subtotal"))
        self.lblPagamentos.setText(_translate("ConsultaReembolsoDialog", "Pagamentos do Reembolso"))
        item = self.tablePagamentos.horizontalHeaderItem(0)
        item.setText(_translate("ConsultaReembolsoDialog", "Forma de Pagamento"))
        item = self.tablePagamentos.horizontalHeaderItem(1)
        item.setText(_translate("ConsultaReembolsoDialog", "Observacao"))
        item = self.tablePagamentos.horizontalHeaderItem(2)
        item.setText(_translate("ConsultaReembolsoDialog", "Valor"))
        self.btnAbrirVenda.setText(_translate("ConsultaReembolsoDialog", "Abrir Venda"))
        self.btnFechar.setText(_translate("ConsultaReembolsoDialog", "Fechar"))
