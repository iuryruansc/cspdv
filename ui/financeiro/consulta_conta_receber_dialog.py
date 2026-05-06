from PyQt5 import QtCore, QtWidgets


class Ui_ConsultaContaReceberDialog(object):
    def setupUi(self, ConsultaContaReceberDialog):
        ConsultaContaReceberDialog.setObjectName("ConsultaContaReceberDialog")
        ConsultaContaReceberDialog.resize(860, 620)
        ConsultaContaReceberDialog.setMinimumSize(QtCore.QSize(820, 580))
        ConsultaContaReceberDialog.setStyleSheet(
            "QDialog{background-color:#edf4fb;}"
            "QFrame#frameHeader,QFrame#frameCard,QFrame#frameTable{background-color:#ffffff;border:1px solid #c8d9ea;border-radius:12px;}"
            "QLabel{color:#153d68;font-size:12px;}"
            "QLabel#lblTitulo{font-size:24px;font-weight:bold;color:#123f6f;}"
            "QLabel#lblSubtitulo{font-size:12px;color:#5c7c9c;}"
            "QLabel.infoLabel{font-size:11px;font-weight:bold;color:#557596;letter-spacing:0.6px;}"
            "QLabel.infoValue{font-size:16px;font-weight:bold;color:#123f6f;}"
            "QTableWidget{border:none;background-color:white;gridline-color:#dce8f0;font-size:12px;}"
            "QHeaderView::section{background-color:#f0f6fc;color:#1a3a5c;font-size:11px;font-weight:bold;border:none;border-right:1px solid #dce8f0;border-bottom:2px solid #3585c8;padding:5px 6px;}"
            "QPushButton{min-height:42px;border-radius:8px;font-size:13px;font-weight:bold;padding:0 18px;background-color:#2f7ed1;border:1px solid #2568af;color:#ffffff;}"
            "QPushButton:hover{background-color:#3a8ae0;}"
        )
        self.verticalLayout = QtWidgets.QVBoxLayout(ConsultaContaReceberDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(12)
        self.frameHeader = QtWidgets.QFrame(ConsultaContaReceberDialog)
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
        self.frameCard = QtWidgets.QFrame(ConsultaContaReceberDialog)
        self.frameCard.setObjectName("frameCard")
        self.cardLayout = QtWidgets.QGridLayout(self.frameCard)
        self.cardLayout.setContentsMargins(22, 18, 22, 18)
        self.cardLayout.setHorizontalSpacing(20)
        self.cardLayout.setVerticalSpacing(10)
        labels = [
            ("lblContaLabel", "lblContaValor"),
            ("lblClienteLabel", "lblClienteValor"),
            ("lblVendaLabel", "lblVendaValor"),
            ("lblStatusLabel", "lblStatusValor"),
            ("lblVencimentoLabel", "lblVencimentoValor"),
            ("lblTotalLabel", "lblTotalValor"),
            ("lblRecebidoLabel", "lblRecebidoValor"),
            ("lblAbertoLabel", "lblAbertoValor"),
        ]
        positions = [(0, 0), (0, 1), (0, 2), (0, 3), (2, 0), (2, 1), (2, 2), (2, 3)]
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
        self.frameTable = QtWidgets.QFrame(ConsultaContaReceberDialog)
        self.frameTable.setObjectName("frameTable")
        self.tableLayout = QtWidgets.QVBoxLayout(self.frameTable)
        self.tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableLayout.setSpacing(0)
        self.lblRecebimentos = QtWidgets.QLabel(self.frameTable)
        self.lblRecebimentos.setStyleSheet("background-color:#f0f6fc;color:#1a3a5c;font-size:13px;font-weight:bold;padding:8px 12px;border-bottom:1px solid #d8e3ee;")
        self.lblRecebimentos.setObjectName("lblRecebimentos")
        self.tableLayout.addWidget(self.lblRecebimentos)
        self.tableRecebimentos = QtWidgets.QTableWidget(self.frameTable)
        self.tableRecebimentos.setRowCount(0)
        self.tableRecebimentos.setColumnCount(4)
        self.tableRecebimentos.setObjectName("tableRecebimentos")
        item = QtWidgets.QTableWidgetItem()
        self.tableRecebimentos.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRecebimentos.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRecebimentos.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRecebimentos.setHorizontalHeaderItem(3, item)
        self.tableRecebimentos.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tableRecebimentos.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableRecebimentos.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tableRecebimentos.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.tableRecebimentos.verticalHeader().setVisible(False)
        self.tableLayout.addWidget(self.tableRecebimentos)
        self.verticalLayout.addWidget(self.frameTable)
        self.bottomLayout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.bottomLayout.addItem(spacer)
        self.btnFechar = QtWidgets.QPushButton(ConsultaContaReceberDialog)
        self.btnFechar.setObjectName("btnFechar")
        self.bottomLayout.addWidget(self.btnFechar)
        self.verticalLayout.addLayout(self.bottomLayout)

        self.retranslateUi(ConsultaContaReceberDialog)
        QtCore.QMetaObject.connectSlotsByName(ConsultaContaReceberDialog)

    def retranslateUi(self, ConsultaContaReceberDialog):
        _translate = QtCore.QCoreApplication.translate
        ConsultaContaReceberDialog.setWindowTitle(_translate("ConsultaContaReceberDialog", "CSPdv - Conta a Receber"))
        self.lblTitulo.setText(_translate("ConsultaContaReceberDialog", "Detalhes da Conta a Receber"))
        self.lblSubtitulo.setText(_translate("ConsultaContaReceberDialog", "Acompanhe status, vencimento e historico de recebimentos da pendencia."))
        self.lblContaLabel.setText(_translate("ConsultaContaReceberDialog", "CONTA"))
        self.lblContaValor.setText(_translate("ConsultaContaReceberDialog", "#0"))
        self.lblClienteLabel.setText(_translate("ConsultaContaReceberDialog", "CLIENTE"))
        self.lblClienteValor.setText(_translate("ConsultaContaReceberDialog", "Consumidor Final"))
        self.lblVendaLabel.setText(_translate("ConsultaContaReceberDialog", "VENDA"))
        self.lblVendaValor.setText(_translate("ConsultaContaReceberDialog", "#0"))
        self.lblStatusLabel.setText(_translate("ConsultaContaReceberDialog", "STATUS"))
        self.lblStatusValor.setText(_translate("ConsultaContaReceberDialog", "-"))
        self.lblVencimentoLabel.setText(_translate("ConsultaContaReceberDialog", "VENCIMENTO"))
        self.lblVencimentoValor.setText(_translate("ConsultaContaReceberDialog", "--/--/----"))
        self.lblTotalLabel.setText(_translate("ConsultaContaReceberDialog", "VALOR TOTAL"))
        self.lblTotalValor.setText(_translate("ConsultaContaReceberDialog", "R$ 0,00"))
        self.lblRecebidoLabel.setText(_translate("ConsultaContaReceberDialog", "JA RECEBIDO"))
        self.lblRecebidoValor.setText(_translate("ConsultaContaReceberDialog", "R$ 0,00"))
        self.lblAbertoLabel.setText(_translate("ConsultaContaReceberDialog", "EM ABERTO"))
        self.lblAbertoValor.setText(_translate("ConsultaContaReceberDialog", "R$ 0,00"))
        self.lblRecebimentos.setText(_translate("ConsultaContaReceberDialog", "Historico de Recebimentos"))
        item = self.tableRecebimentos.horizontalHeaderItem(0)
        item.setText(_translate("ConsultaContaReceberDialog", "Data/Hora"))
        item = self.tableRecebimentos.horizontalHeaderItem(1)
        item.setText(_translate("ConsultaContaReceberDialog", "Forma"))
        item = self.tableRecebimentos.horizontalHeaderItem(2)
        item.setText(_translate("ConsultaContaReceberDialog", "Valor"))
        item = self.tableRecebimentos.horizontalHeaderItem(3)
        item.setText(_translate("ConsultaContaReceberDialog", "Observacao"))
        self.btnFechar.setText(_translate("ConsultaContaReceberDialog", "Fechar"))
