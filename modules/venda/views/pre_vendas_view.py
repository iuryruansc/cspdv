from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from modules.venda.services.pre_venda_service import PreVendaService
from ui.venda.tela_pre_vendas import Ui_TelaPreVendas
from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from utils.format_utils import formatar_moeda
from utils.ui_messages import mostrar_aviso, mostrar_info, confirmar_acao


class PreVendasView(QWidget, Ui_TelaPreVendas):
    pre_venda_importada = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._pre_vendas: List[Dict[str, Any]] = []
        self._conectar_sinais()
        self._configurar_tabela()

    def _conectar_sinais(self) -> None:
        self.btnAtualizar.clicked.connect(self._carregar_pre_vendas)
        self.tablePreVendas.cellClicked.connect(self._ao_clicar_celula)

    def _configurar_tabela(self) -> None:
        self.tablePreVendas.setColumnWidth(0, 60)
        self.tablePreVendas.setColumnWidth(1, 140)
        self.tablePreVendas.setColumnWidth(2, 200)
        self.tablePreVendas.setColumnWidth(3, 100)
        self.tablePreVendas.setColumnWidth(4, 60)
        self.tablePreVendas.setColumnWidth(5, 240)

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self._carregar_pre_vendas()

    def _carregar_pre_vendas(self) -> None:
        caixa = CaixaSession.current() or {}
        caixa_id = int(caixa.get("id") or 0) or None

        self._pre_vendas = PreVendaService.listar_pre_vendas_pendentes(
            caixa_id=caixa_id,
        )

        self.lblPendentesValor.setText(str(len(self._pre_vendas)))
        self._renderizar_tabela()

    def _renderizar_tabela(self) -> None:
        if not self._pre_vendas:
            self.tablePreVendas.hide()
            self.frameVazio.show()
            return

        self.frameVazio.hide()
        self.tablePreVendas.show()

        self.tablePreVendas.setRowCount(len(self._pre_vendas))

        for row, pv in enumerate(self._pre_vendas):
            numero = pv.get("numero_venda") or pv.get("id") or "---"
            self._criar_item_tabela(row, 0, str(numero), Qt.AlignCenter)

            data_hora = pv.get("data_hora")
            if data_hora is not None and hasattr(data_hora, "strftime"):
                texto_data = data_hora.strftime("%d/%m/%Y %H:%M")
            else:
                texto_data = str(data_hora or "---")
            self._criar_item_tabela(row, 1, texto_data, Qt.AlignCenter)

            cliente = pv.get("cliente_nome") or "Consumidor Final"
            self._criar_item_tabela(row, 2, cliente, Qt.AlignLeft)

            valor_total = float(pv.get("valor_total") or 0.0)
            self._criar_item_tabela(row, 3, formatar_moeda(valor_total), Qt.AlignRight)

            self._criar_item_tabela(row, 4, "0", Qt.AlignCenter)

            frame_acoes = QWidget()
            frame_acoes.setStyleSheet("background:transparent;")
            layout_acoes = QHBoxLayout(frame_acoes)
            layout_acoes.setContentsMargins(8, 6, 8, 6)
            layout_acoes.setSpacing(8)
            layout_acoes.setAlignment(Qt.AlignCenter)

            btn_importar = QPushButton("  Importar")
            btn_importar.setMinimumSize(QtCore.QSize(110, 32))
            btn_importar.setStyleSheet(
                "QPushButton{background-color:#2a6fa8;color:white;border:none;"
                "border-radius:6px;padding:6px 14px;font-size:12px;font-weight:bold;}"
                "QPushButton:hover{background-color:#3585c8;}"
                "QPushButton:pressed{background-color:#1e5a8a;}"
            )
            btn_importar.setCursor(Qt.PointingHandCursor)
            btn_importar.clicked.connect(
                lambda _=False, idx=pv.get("id"): self._importar_pre_venda(idx)
            )
            layout_acoes.addWidget(btn_importar)

            btn_cancelar = QPushButton("  Cancelar")
            btn_cancelar.setMinimumSize(QtCore.QSize(100, 32))
            btn_cancelar.setStyleSheet(
                "QPushButton{background-color:#8a2020;color:white;border:none;"
                "border-radius:6px;padding:6px 14px;font-size:12px;font-weight:bold;}"
                "QPushButton:hover{background-color:#a83030;}"
                "QPushButton:pressed{background-color:#6a1010;}"
            )
            btn_cancelar.setCursor(Qt.PointingHandCursor)
            btn_cancelar.clicked.connect(
                lambda _=False, idx=pv.get("id"): self._cancelar_pre_venda(idx)
            )
            layout_acoes.addWidget(btn_cancelar)

            self.tablePreVendas.setCellWidget(row, 5, frame_acoes)
            self.tablePreVendas.setRowHeight(row, 48)

    def _criar_item_tabela(self, row: int, col: int, texto: str, alinhamento: int) -> None:
        item = QTableWidgetItem(texto)
        item.setTextAlignment(alinhamento | Qt.AlignVCenter)
        self.tablePreVendas.setItem(row, col, item)

    def _ao_clicar_celula(self, row: int, column: int) -> None:
        pass

    def _importar_pre_venda(self, pre_venda_id: Optional[int]) -> None:
        if pre_venda_id is None:
            return

        sucesso, mensagem, pre_venda = PreVendaService.carregar_pre_venda(pre_venda_id)
        if not sucesso or pre_venda is None:
            mostrar_aviso(self, "Importar Pré-Venda", mensagem)
            return

        itens = pre_venda.get("itens") or []
        if not itens:
            mostrar_aviso(
                self,
                "Importar Pré-Venda",
                "Esta pré-venda não contém itens válidos.",
            )
            return

        dados_venda = {
            "itens": itens,
            "cliente_id": pre_venda.get("cliente_id"),
            "cliente_nome": pre_venda.get("cliente_nome") or "Consumidor Final",
            "desconto_global": float(pre_venda.get("desconto_global") or 0.0),
            "pre_venda_id": pre_venda_id,
        }

        self.pre_venda_importada.emit(dados_venda)
        mostrar_info(
            self,
            "Importar Pré-Venda",
            f"Pré-venda #{pre_venda_id} importada com sucesso.",
        )

    def _cancelar_pre_venda(self, pre_venda_id: Optional[int]) -> None:
        if pre_venda_id is None:
            return

        resposta = confirmar_acao(
            self,
            "Cancelar Pré-Venda",
            f"Deseja cancelar a pré-venda #{pre_venda_id}?",
        )
        if not resposta:
            return

        sucesso, mensagem = PreVendaService.cancelar_pre_venda(pre_venda_id)
        if sucesso:
            mostrar_info(self, "Cancelar Pré-Venda", mensagem)
            self._carregar_pre_vendas()
        else:
            mostrar_aviso(self, "Cancelar Pré-Venda", mensagem)
