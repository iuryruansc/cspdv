from __future__ import annotations

from typing import Any

from PyQt5.QtWidgets import QComboBox, QLineEdit, QMainWindow, QTableWidget, QTableWidgetItem

from modules.promocoes.services.promocao_service import PromocaoService
from modules.promocoes.views.cadastro_promocao_view import CadastroPromocaoView
from modules.promocoes.views.vincular_produtos_promocao_dialog import VincularProdutosPromocaoDialog
from ui.promocoes.painel_promocoes import Ui_PainelPromocoes
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.ui_messages import mostrar_aviso, mostrar_info


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
        self._vincular_produtos_dialog = None

        self._configurar_tamanho_responsivo()
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._conectar_eventos()
        self._carregar_dados()

    def _conectar_eventos(self) -> None:
        self.btnAtualizar.clicked.connect(self._abrir_editar_promocao)
        self.btnNovaPromocao.clicked.connect(self._abrir_nova_promocao)
        self.btnDuplicarPromocao.clicked.connect(self._acao_indisponivel)
        self.btnVincularProdutos.clicked.connect(self._abrir_vincular_produtos)
        self.txtBuscaPromocao.returnPressed.connect(self._aplicar_filtros)
        self.txtBuscaPromocao.textChanged.connect(self._aplicar_filtros)
        self.cmbStatusFiltro.currentIndexChanged.connect(self._aplicar_filtros)
        self.cmbTipoFiltro.currentIndexChanged.connect(self._aplicar_filtros)
        self.tablePromocoes.itemSelectionChanged.connect(self._popular_itens_da_promocao)

    def _carregar_dados(self) -> None:
        self._promocoes_base = PromocaoService.listar_promocoes()
        self._aplicar_filtros()

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
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            self.tableItensPromocao.setRowCount(0)
            return

        itens_db = PromocaoService.listar_itens_promocao(int(promocao.get("id") or 0))
        self.tableItensPromocao.setRowCount(len(itens_db))
        for row, item in enumerate(itens_db):
            valores = [
                str(item.get("produto") or "-"),
                self._formatar_moeda(item.get("preco_original")),
                self._formatar_moeda(item.get("preco_promocional")),
                self._formatar_desconto(item),
                str(item.get("observacao") or "-"),
            ]
            for column, valor in enumerate(valores):
                self.tableItensPromocao.setItem(row, column, QTableWidgetItem(valor))

    def _abrir_nova_promocao(self) -> None:
        self._cadastro_promocao_dialog = CadastroPromocaoView(self)
        if self._cadastro_promocao_dialog.exec_():
            self._carregar_dados()

    def _abrir_editar_promocao(self) -> None:
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            mostrar_aviso(self, "Promoções", "Selecione uma promoção antes de editar.")
            return

        promocao_id = int(promocao.get("id") or 0)
        self._cadastro_promocao_dialog = CadastroPromocaoView(self, promocao_id=promocao_id)
        if self._cadastro_promocao_dialog.exec_():
            self._carregar_dados()
            self._restaurar_promocao_por_id(promocao_id)

    def _abrir_vincular_produtos(self) -> None:
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            mostrar_aviso(self, "Promoções", "Selecione uma promoção antes de vincular produtos.")
            return

        promocao_id = int(promocao.get("id") or 0)
        self._vincular_produtos_dialog = VincularProdutosPromocaoDialog(promocao_id, self)
        self._vincular_produtos_dialog.exec_()
        self._carregar_dados()
        self._restaurar_promocao_por_id(promocao_id)

    def _acao_indisponivel(self) -> None:
        mostrar_info(
            self,
            "Promoções",
            "A estrutura inicial da área de promoções foi criada. O próximo passo será ligar duplicação, campanhas por grupo e regras promocionais avançadas nesta mesma tela.",
        )

    def _obter_promocao_selecionada(self) -> dict[str, Any] | None:
        row = self.tablePromocoes.currentRow()
        if row < 0 or row >= len(self._promocoes_filtradas):
            return None
        return self._promocoes_filtradas[row]

    def _restaurar_promocao_por_id(self, promocao_id: int) -> None:
        if promocao_id <= 0:
            return
        for row, promocao in enumerate(self._promocoes_filtradas):
            if int(promocao.get("id") or 0) == promocao_id:
                self.tablePromocoes.selectRow(row)
                self._popular_itens_da_promocao()
                break

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
