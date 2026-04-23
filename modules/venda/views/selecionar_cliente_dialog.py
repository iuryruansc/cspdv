from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from modules.clientes.services.cliente_service import ClienteService


class SelecionarClienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar cliente")
        self.setModal(True)
        self.resize(460, 420)
        self._cliente_selecionado: Optional[Dict[str, Any]] = None

        self.setStyleSheet(
            """
            QDialog { background-color: #eef4fa; }
            QLabel { color: #17324d; font-size: 12px; background: transparent; }
            QLineEdit {
                background: white;
                color: #17324d;
                border: 1px solid #b8cee0;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #3585c8; }
            QListWidget {
                background: white;
                color: #17324d;
                border: 1px solid #d5e2ee;
                border-radius: 10px;
                padding: 4px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #e6f1fb;
                color: #17324d;
            }
            QPushButton {
                min-width: 110px;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("Localize o cliente por nome ou CPF", self)
        titulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #163a59;")
        layout.addWidget(titulo)

        self.lineBusca = QLineEdit(self)
        self.lineBusca.setPlaceholderText("Digite ao menos 2 caracteres...")
        layout.addWidget(self.lineBusca)

        self.listaClientes = QListWidget(self)
        layout.addWidget(self.listaClientes, 1)

        self.lblStatus = QLabel("Consumidor Final sera usado se nenhum cliente for selecionado.", self)
        self.lblStatus.setStyleSheet("color: #5f7891;")
        layout.addWidget(self.lblStatus)

        botoes = QHBoxLayout()
        botoes.addStretch(1)
        self.btnConsumidorFinal = QPushButton("Consumidor Final", self)
        self.btnCancelar = QPushButton("Cancelar", self)
        self.btnSelecionar = QPushButton("Selecionar", self)
        self.btnConsumidorFinal.setStyleSheet(
            "QPushButton { background-color: #e8eef5; color: #274764; border: 1px solid #c5d6e4; }"
        )
        self.btnCancelar.setStyleSheet(
            "QPushButton { background-color: #e8eef5; color: #274764; border: 1px solid #c5d6e4; }"
        )
        self.btnSelecionar.setStyleSheet(
            "QPushButton { background-color: #2f78bd; color: white; border: 1px solid #2869a5; }"
        )
        botoes.addWidget(self.btnConsumidorFinal)
        botoes.addWidget(self.btnCancelar)
        botoes.addWidget(self.btnSelecionar)
        layout.addLayout(botoes)

        self.lineBusca.textChanged.connect(self._buscar_clientes)
        self.lineBusca.returnPressed.connect(self._selecionar_cliente)
        self.listaClientes.itemDoubleClicked.connect(lambda _: self._selecionar_cliente())
        self.btnConsumidorFinal.clicked.connect(self._usar_consumidor_final)
        self.btnCancelar.clicked.connect(self.reject)
        self.btnSelecionar.clicked.connect(self._selecionar_cliente)

        self.lineBusca.setFocus()

    @property
    def cliente_selecionado(self) -> Optional[Dict[str, Any]]:
        return self._cliente_selecionado

    def _buscar_clientes(self) -> None:
        termo = self.lineBusca.text().strip()
        self.listaClientes.clear()
        self._cliente_selecionado = None

        if len(termo) < 2:
            self.lblStatus.setText("Digite ao menos 2 caracteres para buscar.")
            return

        clientes = ClienteService.buscar_para_venda(termo)
        if not clientes:
            self.lblStatus.setText("Nenhum cliente encontrado.")
            return

        self.lblStatus.setText(f"{len(clientes)} cliente(s) encontrado(s).")
        for cliente in clientes:
            cpf = str(cliente.get("cpf") or "").strip()
            telefone = str(cliente.get("telefone") or "").strip()
            subtitulo = " | ".join(parte for parte in (cpf, telefone) if parte)
            texto = str(cliente.get("nome") or "")
            if subtitulo:
                texto = f"{texto}\n{subtitulo}"
            item = QListWidgetItem(texto)
            item.setData(256, cliente)
            self.listaClientes.addItem(item)

        self.listaClientes.setCurrentRow(0)

    def _usar_consumidor_final(self) -> None:
        self._cliente_selecionado = None
        self.accept()

    def _selecionar_cliente(self) -> None:
        item = self.listaClientes.currentItem()
        if item is None:
            self._usar_consumidor_final()
            return

        self._cliente_selecionado = item.data(256)
        self.accept()
