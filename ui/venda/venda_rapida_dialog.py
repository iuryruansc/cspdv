# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_VendaRapidaDialog(object):
    def setupUi(self, VendaRapidaDialog):
        VendaRapidaDialog.setObjectName("VendaRapidaDialog")
        VendaRapidaDialog.resize(1460, 900)
        VendaRapidaDialog.setMinimumSize(QtCore.QSize(1320, 820))
        VendaRapidaDialog.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #edf4f9, stop:1 #dce8f1);
            }
            QWidget#frameHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #163552, stop:0.6 #224e76, stop:1 #2f6b9d);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 16px;
            }
            QLabel#lblTitulo {
                color: white;
                font-size: 22px;
                font-weight: 800;
            }
            QLabel#lblSubtitulo {
                color: #dbeaf7;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#lblOperador, QLabel#lblCaixa {
                color: #eef6fc;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 12px;
                background-color: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 10px;
            }
            QWidget#contentWrap {
                background-color: rgba(255,255,255,0.42);
                border: 1px solid #c9d9e6;
                border-radius: 18px;
            }
            """
        )

        self.verticalLayout = QtWidgets.QVBoxLayout(VendaRapidaDialog)
        self.verticalLayout.setContentsMargins(14, 14, 14, 14)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frameHeader = QtWidgets.QWidget(VendaRapidaDialog)
        self.frameHeader.setObjectName("frameHeader")
        self.headerLayout = QtWidgets.QHBoxLayout(self.frameHeader)
        self.headerLayout.setContentsMargins(18, 14, 18, 14)
        self.headerLayout.setSpacing(14)
        self.headerLayout.setObjectName("headerLayout")

        self.titleCol = QtWidgets.QVBoxLayout()
        self.titleCol.setSpacing(4)
        self.lblTitulo = QtWidgets.QLabel(self.frameHeader)
        self.lblTitulo.setObjectName("lblTitulo")
        self.titleCol.addWidget(self.lblTitulo)
        self.lblSubtitulo = QtWidgets.QLabel(self.frameHeader)
        self.lblSubtitulo.setObjectName("lblSubtitulo")
        self.titleCol.addWidget(self.lblSubtitulo)
        self.headerLayout.addLayout(self.titleCol)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.headerLayout.addItem(spacerItem)

        self.statusCol = QtWidgets.QVBoxLayout()
        self.statusCol.setSpacing(4)
        self.lblOperador = QtWidgets.QLabel(self.frameHeader)
        self.lblOperador.setObjectName("lblOperador")
        self.statusCol.addWidget(self.lblOperador)
        self.lblCaixa = QtWidgets.QLabel(self.frameHeader)
        self.lblCaixa.setObjectName("lblCaixa")
        self.statusCol.addWidget(self.lblCaixa)
        self.headerLayout.addLayout(self.statusCol)
        self.verticalLayout.addWidget(self.frameHeader)

        self.contentWrap = QtWidgets.QWidget(VendaRapidaDialog)
        self.contentWrap.setObjectName("contentWrap")
        self.contentLayout = QtWidgets.QStackedLayout(self.contentWrap)
        self.contentLayout.setContentsMargins(12, 12, 12, 12)
        self.contentLayout.setObjectName("contentLayout")
        self.verticalLayout.addWidget(self.contentWrap)

        self.retranslateUi(VendaRapidaDialog)
        QtCore.QMetaObject.connectSlotsByName(VendaRapidaDialog)

    def retranslateUi(self, VendaRapidaDialog):
        _translate = QtCore.QCoreApplication.translate
        VendaRapidaDialog.setWindowTitle(_translate("VendaRapidaDialog", "CSPdv - Venda Rapida"))
        self.lblTitulo.setText(_translate("VendaRapidaDialog", "Venda Rapida"))
        self.lblSubtitulo.setText(_translate("VendaRapidaDialog", "Fluxo compacto de venda sem sair do painel administrativo."))
        self.lblOperador.setText(_translate("VendaRapidaDialog", "Operador: ---"))
        self.lblCaixa.setText(_translate("VendaRapidaDialog", "Caixa: ---"))
