from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.venda.services.pre_venda_service import PreVendaService
from core.caixa_session import CaixaSession
from utils.format_utils import formatar_moeda


class ImportarPreVendaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importar Pré-Venda")
        self.setMinimumSize(700, 450)
        self.setMaximumSize(700, 450)
        self.setStyleSheet(
            "QDialog{background-color:#102233;}"
            "QLabel{background-color:transparent;color:#e0e8f0;}"
        )
        self._pre_vendas: List[Dict[str, Any]] = []
        self._pre_venda_selecionada: Optional[Dict[str, Any]] = None
        self._configurar_interface()
        self._carregar_pre_vendas()

    @property
    def resultado(self) -> Optional[Dict[str, Any]]:
        return self._pre_venda_selecionada

    def _configurar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        lbl_titulo = QLabel("Selecione uma pré-venda para importar:")
        lbl_titulo.setStyleSheet("font-size:14px;font-weight:bold;color:#8bb7d8;")
        layout.addWidget(lbl_titulo)

        self._frame_lista = QWidget()
        self._frame_lista.setStyleSheet(
            "QFrame#frameLista{background-color:#12283a;border:1px solid #214b6a;border-radius:8px;}"
        )
        self._frame_lista.setObjectName("frameLista")
        self._lista_layout = QVBoxLayout(self._frame_lista)
        self._lista_layout.setContentsMargins(12, 12, 12, 12)
        self._lista_layout.setSpacing(8)
        layout.addWidget(self._frame_lista)

        self._lbl_vazio = QLabel("Nenhuma pré-venda pendente encontrada.")
        self._lbl_vazio.setStyleSheet("font-size:12px;color:#5a7a9a;font-style:italic;")
        self._lbl_vazio.setAlignment(Qt.AlignCenter)
        self._lista_layout.addWidget(self._lbl_vazio)

        layout.addStretch()

        frame_botoes = QWidget()
        frame_botoes.setStyleSheet("background:transparent;")
        botoes_layout = QHBoxLayout(frame_botoes)
        botoes_layout.setContentsMargins(0, 0, 0, 0)
        botoes_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setMinimumSize(120, 36)
        btn_cancelar.setStyleSheet(
            "QPushButton{background-color:#4a5a6a;color:white;border:none;"
            "border-radius:6px;font-size:12px;font-weight:bold;}"
            "QPushButton:hover{background-color:#5a6a7a;}"
        )
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.clicked.connect(self.reject)
        botoes_layout.addWidget(btn_cancelar)

        layout.addWidget(frame_botoes)

    def _carregar_pre_vendas(self) -> None:
        caixa = CaixaSession.current() or {}
        caixa_id = int(caixa.get("id") or 0) or None

        self._pre_vendas = PreVendaService.listar_pre_vendas_pendentes(
            caixa_id=caixa_id,
        )

        for item in reversed(range(self._lista_layout.count())):
            widget = self._lista_layout.itemAt(item).widget()
            if widget and widget != self._lbl_vazio:
                self._lista_layout.removeWidget(widget)
                widget.deleteLater()

        if not self._pre_vendas:
            self._lbl_vazio.show()
            return

        self._lbl_vazio.hide()

        for pv in self._pre_vendas:
            self._criar_item_lista(pv)

    def _criar_item_lista(self, pv: Dict[str, Any]) -> None:
        item_widget = QWidget()
        item_widget.setStyleSheet(
            "QWidget{background-color:#0d1f2d;border:1px solid #1a3a5a;border-radius:6px;}"
            "QWidget:hover{border-color:#3585c8;}"
        )
        item_widget.setMinimumHeight(60)

        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(16)

        col_info = QVBoxLayout()
        col_info.setSpacing(4)

        numero = pv.get("numero_venda") or pv.get("id") or "---"
        lbl_numero = QLabel(f"Pré-Venda #{numero}")
        lbl_numero.setStyleSheet("font-size:13px;font-weight:bold;color:#e0e8f0;")
        col_info.addWidget(lbl_numero)

        data_hora = pv.get("data_hora")
        if data_hora is not None and hasattr(data_hora, "strftime"):
            texto_data = data_hora.strftime("%d/%m/%Y %H:%M")
        else:
            texto_data = str(data_hora or "---")

        cliente = pv.get("cliente_nome") or "Consumidor Final"
        lbl_detalhes = QLabel(f"{texto_data}  •  {cliente}")
        lbl_detalhes.setStyleSheet("font-size:11px;color:#8bb7d8;")
        col_info.addWidget(lbl_detalhes)

        layout.addLayout(col_info, stretch=1)

        valor_total = float(pv.get("valor_total") or 0.0)
        lbl_valor = QLabel(formatar_moeda(valor_total))
        lbl_valor.setStyleSheet("font-size:16px;font-weight:bold;color:#4caf50;")
        lbl_valor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lbl_valor)

        btn_importar = QPushButton("Importar")
        btn_importar.setMinimumSize(100, 36)
        btn_importar.setStyleSheet(
            "QPushButton{background-color:#2a6fa8;color:white;border:none;"
            "border-radius:6px;font-size:12px;font-weight:bold;}"
            "QPushButton:hover{background-color:#3585c8;}"
            "QPushButton:pressed{background-color:#1e5a8a;}"
        )
        btn_importar.setCursor(Qt.PointingHandCursor)
        btn_importar.clicked.connect(
            lambda _=False, p=pv: self._selecionar_e_fechar(p)
        )
        layout.addWidget(btn_importar)

        self._lista_layout.addWidget(item_widget)

    def _selecionar_e_fechar(self, pv: Dict[str, Any]) -> None:
        pre_venda_id = pv.get("id")
        if pre_venda_id:
            sucesso, _, pre_venda_completa = PreVendaService.carregar_pre_venda(pre_venda_id)
            if sucesso and pre_venda_completa:
                self._pre_venda_selecionada = pre_venda_completa
                self.accept()
                return
        self._pre_venda_selecionada = pv
        self.accept()
