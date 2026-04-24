from __future__ import annotations

from typing import Any

from PyQt5.QtWidgets import QComboBox, QLineEdit, QMainWindow, QTableWidget, QTableWidgetItem

from modules.promocoes.services.promocao_service import PromocaoService
from modules.promocoes.views.cadastro_promocao_view import CadastroPromocaoView
from ui.promocoes.painel_promocoes import Ui_PainelPromocoes
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.ui_messages import mostrar_info


class PainelPromocoesView(QMainWindow, Ui_PainelPromocoes, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.txtBuscaPromocao: QLineEdit
        self.cmbStatusFiltro: QComboBox
        self.cmbTipoFiltro: QComboBox
        self.tablePromocoes: QTableWidget
        self.tableItensPromocao: QTableWidget
        self._promocoes_base: list[dict[str, Any]] = []
        self._promocoes_filtradas: list[dict[str, Any]] = []
        self._cadastro_promocao_dialog = None

        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._configurar_tabelas()
        self._conectar_eventos()
        self._popular_mock_inicial()

    def _configurar_tabelas(self) -> None:
        self.tablePromocoes.setColumnWidth(0, 90)
        self.tablePromocoes.setColumnWidth(1, 240)
        self.tablePromocoes.setColumnWidth(2, 160)
        self.tablePromocoes.setColumnWidth(3, 170)
        self.tablePromocoes.setColumnWidth(4, 110)
        self.tablePromocoes.horizontalHeader().setStretchLastSection(True)

        self.tableItensPromocao.setColumnWidth(0, 200)
        self.tableItensPromocao.setColumnWidth(1, 90)
        self.tableItensPromocao.setColumnWidth(2, 90)
        self.tableItensPromocao.setColumnWidth(3, 80)
        self.tableItensPromocao.horizontalHeader().setStretchLastSection(True)

    def _conectar_eventos(self) -> None:
        self.btnAtualizar.clicked.connect(self._atualizar_dados)
        self.btnNovaPromocao.clicked.connect(self._abrir_nova_promocao)
        self.btnDuplicarPromocao.clicked.connect(self._acao_indisponivel)
        self.btnVincularProdutos.clicked.connect(self._acao_indisponivel)
        self.txtBuscaPromocao.returnPressed.connect(self._aplicar_filtros)
        self.txtBuscaPromocao.textChanged.connect(self._aplicar_filtros)
        self.cmbStatusFiltro.currentIndexChanged.connect(self._aplicar_filtros)
        self.cmbTipoFiltro.currentIndexChanged.connect(self._aplicar_filtros)
        self.tablePromocoes.itemSelectionChanged.connect(self._popular_itens_da_promocao)

    def _popular_mock_inicial(self) -> None:
        self._promocoes_base = PromocaoService.listar_promocoes()
        self._aplicar_filtros()

    def _atualizar_dados(self) -> None:
        self._popular_mock_inicial()

    def _aplicar_filtros(self) -> None:
        busca = self.txtBuscaPromocao.text().strip().lower()
        status = self._mapear_status_filtro(self.cmbStatusFiltro.currentText())
        tipo = self._mapear_tipo_filtro(self.cmbTipoFiltro.currentText())

        self._promocoes_filtradas = []
        for promocao in self._promocoes_base:
            if status and str(promocao.get("status", "")).strip().upper() != status:
                continue
            if tipo and str(promocao.get("tipo_desconto", "")).strip().upper() != tipo:
                continue

            texto_base = " ".join(
                [
                    str(promocao.get("codigo", "")),
                    str(promocao.get("nome", "")),
                    str(promocao.get("tipo_desconto", "")),
                    str(promocao.get("status", "")),
                    str(promocao.get("alcance", "")),
                ]
            ).lower()
            if busca and busca not in texto_base:
                continue
            self._promocoes_filtradas.append(promocao)

        self._renderizar_promocoes()
        self._atualizar_metricas()

    def _renderizar_promocoes(self) -> None:
        self.tablePromocoes.setRowCount(len(self._promocoes_filtradas))
        for row, promocao in enumerate(self._promocoes_filtradas):
            valores = [
                str(promocao.get("codigo") or "-"),
                str(promocao.get("nome") or "-"),
                self._label_tipo(str(promocao.get("tipo_desconto") or "-")),
                str(promocao.get("vigencia") or "-"),
                self._label_status(str(promocao.get("status") or "-")),
                str(promocao.get("alcance") or "-"),
            ]
            for column, value in enumerate(valores):
                self.tablePromocoes.setItem(row, column, QTableWidgetItem(value))

        if self.tablePromocoes.rowCount() > 0:
            self.tablePromocoes.selectRow(0)
        else:
            self.tableItensPromocao.setRowCount(0)
            self.lblStatusBar.setText("CSPdv - Modulo de Promocoes | Nenhuma promocao encontrada para os filtros atuais")

    def _atualizar_metricas(self) -> None:
        total_ativas = sum(1 for promocao in self._promocoes_base if str(promocao.get("status") or "").upper() == "ATIVA")
        total_agendadas = sum(1 for promocao in self._promocoes_base if str(promocao.get("status") or "").upper() == "AGENDADA")
        total_encerradas = sum(1 for promocao in self._promocoes_base if str(promocao.get("status") or "").upper() == "ENCERRADA")
        total_itens = sum(int(promocao.get("qtd_produtos") or 0) for promocao in self._promocoes_base)

        self.lblPromocoesAtivasValor.setText(str(total_ativas))
        self.lblAgendadasValor.setText(str(total_agendadas))
        self.lblProdutosPromocaoValor.setText(str(total_itens))
        self.lblEncerradasValor.setText(str(total_encerradas))

        self.lblStatusBar.setText(
            "CSPdv - Modulo de Promocoes | "
            f"{len(self._promocoes_filtradas)} promocao(oes) listada(s) com os filtros atuais"
        )

    def _popular_itens_da_promocao(self) -> None:
        row = self.tablePromocoes.currentRow()
        if row < 0 or row >= len(self._promocoes_filtradas):
            self.tableItensPromocao.setRowCount(0)
            return
        promocao_id = int(self._promocoes_filtradas[row].get("id") or 0)
        itens_db = PromocaoService.listar_itens_promocao(promocao_id) if promocao_id > 0 else []
        itens = [
            (
                str(item.get("produto") or "-"),
                self._formatar_moeda(item.get("preco_original")),
                self._formatar_moeda(item.get("preco_promocional")),
                self._formatar_desconto(item),
                str(item.get("observacao") or "-"),
            )
            for item in itens_db
        ]
        self.tableItensPromocao.setRowCount(len(itens))
        for item_row, item_data in enumerate(itens):
            for column, value in enumerate(item_data):
                self.tableItensPromocao.setItem(item_row, column, QTableWidgetItem(value))

    @staticmethod
    def _formatar_moeda(valor: Any) -> str:
        try:
            return f"R$ {float(valor or 0):.2f}".replace(".", ",")
        except (TypeError, ValueError):
            return "R$ 0,00"

    @staticmethod
    def _formatar_desconto(item: dict[str, Any]) -> str:
        try:
            desconto = float(item.get("desconto_aplicado") or 0)
        except (TypeError, ValueError):
            desconto = 0.0
        return f"R$ {desconto:.2f}".replace(".", ",") if desconto > 0 else "-"

    def _abrir_nova_promocao(self) -> None:
        self._cadastro_promocao_dialog = CadastroPromocaoView(self)
        if self._cadastro_promocao_dialog.exec_():
            self._carregar_apos_salvar()

    def _carregar_apos_salvar(self) -> None:
        self._popular_mock_inicial()

    def _acao_indisponivel(self) -> None:
        mostrar_info(
            self,
            "Promoções",
            "A estrutura inicial da área de promoções foi criada. O próximo passo será ligar o cadastro e as regras promocionais nesta mesma tela.",
        )

    @staticmethod
    def _mapear_status_filtro(texto: str) -> str:
        mapa = {
            "ATIVAS": "ATIVA",
            "AGENDADAS": "AGENDADA",
            "ENCERRADAS": "ENCERRADA",
        }
        return mapa.get(texto.strip().upper(), "")

    @staticmethod
    def _mapear_tipo_filtro(texto: str) -> str:
        mapa = {
            "DESCONTO POR PERCENTUAL": "PERCENTUAL",
            "DESCONTO POR VALOR": "VALOR",
            "PRECO PROMOCIONAL": "PRECO_FIXO",
        }
        return mapa.get(texto.strip().upper(), "")

    @staticmethod
    def _label_tipo(tipo: str) -> str:
        mapa = {
            "PERCENTUAL": "Desconto por percentual",
            "VALOR": "Desconto por valor",
            "PRECO_FIXO": "Preco promocional",
        }
        return mapa.get(tipo.strip().upper(), tipo)

    @staticmethod
    def _label_status(status: str) -> str:
        mapa = {
            "RASCUNHO": "Rascunho",
            "AGENDADA": "Agendada",
            "ATIVA": "Ativa",
            "ENCERRADA": "Encerrada",
            "CANCELADA": "Cancelada",
        }
        return mapa.get(status.strip().upper(), status)
