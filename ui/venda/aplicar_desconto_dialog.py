# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_AplicarDescontoDialog(object):
    def setupUi(self, AplicarDescontoDialog):
        AplicarDescontoDialog.setObjectName("AplicarDescontoDialog")
        AplicarDescontoDialog.resize(420, 220)
        AplicarDescontoDialog.setMinimumSize(QtCore.QSize(420, 220))
        AplicarDescontoDialog.setStyleSheet(
            """
            QDialog { background-color: #eef4fa; }
            QLabel { color: #17324d; font-size: 12px; background: transparent; }
            QComboBox, QDoubleSpinBox {
                background: white;
                color: #17324d;
                border: 1px solid #b8cee0;
                border-radius: 8px;
                padding: 7px 10px;
                font-size: 12px;
            }
            QPushButton {
                min-width: 110px;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#btnCancelar {
                background-color: #e8eef5;
                color: #274764;
                border: 1px solid #c5d6e4;
            }
            QPushButton#btnAplicar {
                background-color: #2f78bd;
                color: white;
                border: 1px solid #2869a5;
            }
            """
        )

        self.verticalLayout = QtWidgets.QVBoxLayout(AplicarDescontoDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")

        self.lblTitulo = QtWidgets.QLabel(AplicarDescontoDialog)
        self.lblTitulo.setObjectName("lblTitulo")
        self.lblTitulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #163a59;")
        self.verticalLayout.addWidget(self.lblTitulo)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName("formLayout")

        self.lblModo = QtWidgets.QLabel(AplicarDescontoDialog)
        self.lblModo.setMinimumWidth(90)
        self.lblModo.setObjectName("lblModo")
        self.comboModo = QtWidgets.QComboBox(AplicarDescontoDialog)
        self.comboModo.setObjectName("comboModo")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lblModo)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboModo)

        self.lblAcao = QtWidgets.QLabel(AplicarDescontoDialog)
        self.lblAcao.setMinimumWidth(90)
        self.lblAcao.setObjectName("lblAcao")
        self.comboAcao = QtWidgets.QComboBox(AplicarDescontoDialog)
        self.comboAcao.setObjectName("comboAcao")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lblAcao)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboAcao)

        self.lblTipo = QtWidgets.QLabel(AplicarDescontoDialog)
        self.lblTipo.setMinimumWidth(90)
        self.lblTipo.setObjectName("lblTipo")
        self.comboTipo = QtWidgets.QComboBox(AplicarDescontoDialog)
        self.comboTipo.setObjectName("comboTipo")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lblTipo)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboTipo)

        self.lblValor = QtWidgets.QLabel(AplicarDescontoDialog)
        self.lblValor.setMinimumWidth(90)
        self.lblValor.setObjectName("lblValor")
        self.spinValor = QtWidgets.QDoubleSpinBox(AplicarDescontoDialog)
        self.spinValor.setObjectName("spinValor")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.lblValor)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.spinValor)

        self.verticalLayout.addLayout(self.formLayout)

        self.lblAjuda = QtWidgets.QLabel(AplicarDescontoDialog)
        self.lblAjuda.setWordWrap(True)
        self.lblAjuda.setStyleSheet("color: #5f7891;")
        self.lblAjuda.setObjectName("lblAjuda")
        self.verticalLayout.addWidget(self.lblAjuda)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)
        self.btnCancelar = QtWidgets.QPushButton(AplicarDescontoDialog)
        self.btnCancelar.setObjectName("btnCancelar")
        self.buttonLayout.addWidget(self.btnCancelar)
        self.btnAplicar = QtWidgets.QPushButton(AplicarDescontoDialog)
        self.btnAplicar.setObjectName("btnAplicar")
        self.buttonLayout.addWidget(self.btnAplicar)
        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(AplicarDescontoDialog)
        QtCore.QMetaObject.connectSlotsByName(AplicarDescontoDialog)

    def retranslateUi(self, AplicarDescontoDialog):
        _translate = QtCore.QCoreApplication.translate
        AplicarDescontoDialog.setWindowTitle(_translate("AplicarDescontoDialog", "Aplicar desconto"))
        self.lblTitulo.setText(_translate("AplicarDescontoDialog", "Escolha onde e como o desconto sera aplicado"))
        self.lblModo.setText(_translate("AplicarDescontoDialog", "Aplicar em"))
        self.lblAcao.setText(_translate("AplicarDescontoDialog", "Acao"))
        self.lblTipo.setText(_translate("AplicarDescontoDialog", "Tipo"))
        self.lblValor.setText(_translate("AplicarDescontoDialog", "Desconto"))
        self.lblAjuda.setText(_translate("AplicarDescontoDialog", "No modo global, o desconto reduz apenas o total da venda nesta etapa inicial."))
        self.btnCancelar.setText(_translate("AplicarDescontoDialog", "Cancelar"))
        self.btnAplicar.setText(_translate("AplicarDescontoDialog", "Aplicar desconto"))
