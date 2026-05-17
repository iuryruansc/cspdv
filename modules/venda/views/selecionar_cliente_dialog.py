from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt5.QtWidgets import QDialog, QListWidgetItem

from modules.clientes.services.cliente_service import ClienteService
from ui.venda.selecionar_cliente_dialog import Ui_SelecionarClienteDialog

class SelecionarClienteDialog(QDialog, Ui_SelecionarClienteDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self._cliente_selecionado: Optional[Dict[str, Any]] = None
        self._cliente_consumidor_final = ClienteService.obter_consumidor_final()

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
        self._cliente_selecionado = dict(self._cliente_consumidor_final) if self._cliente_consumidor_final else None
        self.accept()

    def _selecionar_cliente(self) -> None:
        item = self.listaClientes.currentItem()
        if item is None:
            self._usar_consumidor_final()
            return

        self._cliente_selecionado = item.data(256)
        self.accept()
