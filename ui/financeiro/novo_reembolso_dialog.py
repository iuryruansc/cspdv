# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_NovoReembolsoDialog(object):
    def setupUi(self, NovoReembolsoDialog):
        NovoReembolsoDialog.setObjectName("NovoReembolsoDialog")
        NovoReembolsoDialog.resize(980, 760)
        NovoReembolsoDialog.setMinimumSize(QtCore.QSize(940, 720))
        NovoReembolsoDialog.setWindowTitle("Novo Reembolso")
        NovoReembolsoDialog.setStyleSheet(
            """
            QDialog { background: #eef5fb; }
            QFrame[card="true"] { background: white; border: 1px solid #c8d8ea; border-radius: 14px; }
            QLabel[title="true"] { color: #173a5f; font-size: 16px; font-weight: bold; }
            QLabel[caption="true"] { color: #4c6b8b; font-size: 11px; font-weight: bold; }
            QLabel[value="true"] { color: #173a5f; font-size: 18px; font-weight: bold; }
            QTableWidget { background: white; border: 1px solid #c8d8ea; border-radius: 10px; gridline-color: #d9e6f2; color: #173a5f; }
            QHeaderView::section { background: #e7f0f8; color: #1e4e79; padding: 8px; border: none; border-right: 1px solid #d1e0ee; border-bottom: 1px solid #d1e0ee; font-weight: bold; }
            QLineEdit, QTextEdit { background: white; border: 1px solid #bcd0e4; border-radius: 10px; padding: 8px 10px; color: #173a5f; }
            QRadioButton { color: #173a5f; font-weight: bold; }
            QSpinBox { background: white; border: 1px solid #bcd0e4; border-radius: 8px; padding: 4px; color: #173a5f; }
            QPushButton#btnConfirmar { background: #d9534f; color: white; border: none; border-radius: 10px; padding: 10px 20px; font-weight: bold; }
            QPushButton#btnConfirmar:hover { background: #c64542; }
            QPushButton#btnCancelar { background: #dfe9f3; color: #173a5f; border: 1px solid #c2d5e8; border-radius: 10px; padding: 10px 20px; font-weight: bold; }
            QPushButton#btnCancelar:hover { background: #d1dfec; }
            """
        )
        self.verticalLayout = QtWidgets.QVBoxLayout(NovoReembolsoDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(14)

        self.headerCard = QtWidgets.QFrame(NovoReembolsoDialog)
        self.headerCard.setProperty("card", "true")
        self.headerLayout = QtWidgets.QVBoxLayout(self.headerCard)
        self.headerLayout.setContentsMargins(18, 18, 18, 18)
        self.headerLayout.setSpacing(12)
        self.lblHeaderTitulo = QtWidgets.QLabel(self.headerCard)
        self.lblHeaderTitulo.setProperty("title", "true")
        self.headerLayout.addWidget(self.lblHeaderTitulo)
        self.headerInfoRow = QtWidgets.QHBoxLayout()
        self.headerInfoRow.setSpacing(24)
        self.headerLayout.addLayout(self.headerInfoRow)
        self.lblCliente = self._add_info_block(self.headerInfoRow, "CLIENTE")
        self.lblDataHora = self._add_info_block(self.headerInfoRow, "DATA / HORA")
        self.lblTotalVenda = self._add_info_block(self.headerInfoRow, "TOTAL DA VENDA")
        self.lblStatus = self._add_info_block(self.headerInfoRow, "STATUS")
        self.verticalLayout.addWidget(self.headerCard)

        self.modeCard = QtWidgets.QFrame(NovoReembolsoDialog)
        self.modeCard.setProperty("card", "true")
        self.modeLayout = QtWidgets.QVBoxLayout(self.modeCard)
        self.modeLayout.setContentsMargins(18, 18, 18, 18)
        self.modeLayout.setSpacing(12)
        self.lblTipoSection = QtWidgets.QLabel(self.modeCard)
        self.lblTipoSection.setProperty("title", "true")
        self.modeLayout.addWidget(self.lblTipoSection)
        self.modeRow = QtWidgets.QHBoxLayout()
        self.radioTotal = QtWidgets.QRadioButton(self.modeCard)
        self.radioParcial = QtWidgets.QRadioButton(self.modeCard)
        self.radioTotal.setChecked(True)
        self.modeRow.addWidget(self.radioTotal)
        self.modeRow.addWidget(self.radioParcial)
        self.modeRow.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.modeLayout.addLayout(self.modeRow)
        self.tableItens = QtWidgets.QTableWidget(self.modeCard)
        self.tableItens.setColumnCount(6)
        self.tableItens.setHorizontalHeaderLabels(["Código", "Descrição", "Disponível", "Selecionada", "Vl. Unit.", "Total"])
        self.tableItens.verticalHeader().setVisible(False)
        self.tableItens.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableItens.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableItens.horizontalHeader().setStretchLastSection(True)
        self.modeLayout.addWidget(self.tableItens)
        self.verticalLayout.addWidget(self.modeCard, 1)

        self.formCard = QtWidgets.QFrame(NovoReembolsoDialog)
        self.formCard.setProperty("card", "true")
        self.formLayout = QtWidgets.QVBoxLayout(self.formCard)
        self.formLayout.setContentsMargins(18, 18, 18, 18)
        self.formLayout.setSpacing(10)
        self.lblJustificativaSection = QtWidgets.QLabel(self.formCard)
        self.lblJustificativaSection.setProperty("title", "true")
        self.formLayout.addWidget(self.lblJustificativaSection)
        self.inputMotivo = QtWidgets.QLineEdit(self.formCard)
        self.formLayout.addWidget(self.inputMotivo)
        self.inputObservacao = QtWidgets.QTextEdit(self.formCard)
        self.inputObservacao.setMinimumHeight(88)
        self.inputObservacao.setMaximumHeight(88)
        self.formLayout.addWidget(self.inputObservacao)
        self.summaryRow = QtWidgets.QHBoxLayout()
        self.lblTotalReembolsoCaption = QtWidgets.QLabel(self.formCard)
        self.lblTotalReembolsoCaption.setProperty("caption", "true")
        self.summaryRow.addWidget(self.lblTotalReembolsoCaption)
        self.summaryRow.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.lblTotalReembolso = QtWidgets.QLabel(self.formCard)
        self.lblTotalReembolso.setProperty("value", "true")
        self.summaryRow.addWidget(self.lblTotalReembolso)
        self.formLayout.addLayout(self.summaryRow)
        self.verticalLayout.addWidget(self.formCard)

        self.footerLayout = QtWidgets.QHBoxLayout()
        self.footerLayout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.btnCancelar = QtWidgets.QPushButton(NovoReembolsoDialog)
        self.btnCancelar.setObjectName("btnCancelar")
        self.footerLayout.addWidget(self.btnCancelar)
        self.btnConfirmar = QtWidgets.QPushButton(NovoReembolsoDialog)
        self.btnConfirmar.setObjectName("btnConfirmar")
        self.footerLayout.addWidget(self.btnConfirmar)
        self.verticalLayout.addLayout(self.footerLayout)

        self.retranslateUi(NovoReembolsoDialog)
        QtCore.QMetaObject.connectSlotsByName(NovoReembolsoDialog)

    def _add_info_block(self, parent_layout, caption):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(4)
        lbl_caption = QtWidgets.QLabel(caption)
        lbl_caption.setProperty("caption", "true")
        layout.addWidget(lbl_caption)
        lbl_value = QtWidgets.QLabel("-")
        lbl_value.setProperty("value", "true")
        layout.addWidget(lbl_value)
        parent_layout.addLayout(layout, 1)
        return lbl_value

    def retranslateUi(self, NovoReembolsoDialog):
        _translate = QtCore.QCoreApplication.translate
        self.lblHeaderTitulo.setText(_translate("NovoReembolsoDialog", "Reembolso da Venda #-"))
        self.lblTipoSection.setText(_translate("NovoReembolsoDialog", "Tipo de Reembolso"))
        self.radioTotal.setText(_translate("NovoReembolsoDialog", "Reembolso total"))
        self.radioParcial.setText(_translate("NovoReembolsoDialog", "Reembolso parcial por item"))
        self.lblJustificativaSection.setText(_translate("NovoReembolsoDialog", "Justificativa"))
        self.inputMotivo.setPlaceholderText(_translate("NovoReembolsoDialog", "Informe o motivo do reembolso"))
        self.inputObservacao.setPlaceholderText(_translate("NovoReembolsoDialog", "Observações adicionais sobre o reembolso..."))
        self.lblTotalReembolsoCaption.setText(_translate("NovoReembolsoDialog", "Valor a reembolsar"))
        self.lblTotalReembolso.setText(_translate("NovoReembolsoDialog", "R$ 0,00"))
        self.btnCancelar.setText(_translate("NovoReembolsoDialog", "Cancelar"))
        self.btnConfirmar.setText(_translate("NovoReembolsoDialog", "Confirmar Reembolso"))
