from __future__ import annotations

import csv
from datetime import date
from typing import Any

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.relatorios.painel_relatorios import Ui_PainelRelatorios
from modules.relatorios.services.relatorio_service import RelatorioService
from utils.format_utils import formatar_moeda
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.table_widget_utils import set_table_item

_MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
_VERDE_FUNDO = QColor("#d4edda")
_VERDE_TEXTO = QColor("#155724")
_AZUL_TOTAL = QColor("#153552")
_BRANCO = QColor("#ffffff")

COR = {"azul": "#3585c8", "verde": "#5cb85c", "roxo": "#9b59b6", "laranja": "#e67e22"}

class GraficoCanvas(FigureCanvas):
    def __init__(self, parent=None, dpi=100):
        self.fig = Figure(dpi=dpi, facecolor="white")
        self.fig.subplots_adjust(left=0.18, right=0.96, top=0.94, bottom=0.12)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def limpar(self):
        self.ax.clear()
        self.fig.subplots_adjust(left=0.18, right=0.96, top=0.94, bottom=0.12)
        self.draw()

class PainelRelatoriosView(QMainWindow, Ui_PainelRelatorios, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._configurar_tamanho_responsivo()
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._configurar_periodo_padrao()
        self._configurar_tabelas()
        self._instalar_graficos()
        self._conectar_eventos()
        self.chipsFrame.setVisible(False)
        self.framePeriodoFiltro.setVisible(False)
        self._gerar_relatorio()

    def _conectar_eventos(self) -> None:
        self.btnGerarRelatorio.clicked.connect(self._gerar_relatorio)
        self.btnExportarCsv.clicked.connect(self._exportar_csv)
        self.tabTipoRelatorio.currentChanged.connect(self._ao_mudar_aba)
        self.cmbAno.currentIndexChanged.connect(self._gerar_matriz_anual)

    def _configurar_periodo_padrao(self) -> None:
        from PyQt5.QtCore import QDate
        hoje = QDate.currentDate()
        inicio_mes = hoje.addDays(1 - hoje.day())
        fim_mes = QDate(hoje.year(), hoje.month(), hoje.daysInMonth())
        self.dateInicial.setDisplayFormat("dd/MM/yyyy")
        self.dateFinal.setDisplayFormat("dd/MM/yyyy")
        self.dateInicial.setDate(inicio_mes)
        self.dateFinal.setDate(fim_mes)

    def _ao_mudar_aba(self, index: int) -> None:
        self.chipsFrame.setVisible(index != 0)
        self.framePeriodoFiltro.setVisible(index != 0)
        self.stackedContent.setCurrentIndex(index)
        if index != 0:
            self.chipsFrame.updateGeometry()
        self._gerar_relatorio()

    def _configurar_tabelas(self) -> None:
        for t in (self.tableProdutos, self.tableCaixa, self.tableMatriz):
            t.setRowCount(0)

    def _instalar_graficos(self) -> None:
        self.graficoProdutos = GraficoCanvas(self.chartProdutosWidget)
        lay_p = QVBoxLayout(self.chartProdutosWidget)
        lay_p.setContentsMargins(0, 0, 0, 0)
        lay_p.addWidget(self.graficoProdutos)

        self.graficoCaixa = GraficoCanvas(self.chartCaixaWidget)
        lay_c = QVBoxLayout(self.chartCaixaWidget)
        lay_c.setContentsMargins(0, 0, 0, 0)
        lay_c.addWidget(self.graficoCaixa)

    def _gerar_relatorio(self) -> None:
        tipo = self.tabTipoRelatorio.currentIndex()
        if tipo == 0:
            self._popular_anos()
            self._gerar_matriz_anual()
        elif tipo == 1:
            self._render_produtos()
        elif tipo == 2:
            self._render_clientes()
        elif tipo == 3:
            self._render_caixa()

    # ── Tab 0: Matriz Anual ───────────────────────────────────────────
    def _popular_anos(self) -> None:
        if self.cmbAno.count() > 0:
            return
        dados = RelatorioService.matriz_vendas_anual(ano=date.today().year)
        for a in dados.get("anos_disponiveis", []):
            self.cmbAno.addItem(str(a), a)

    def _gerar_matriz_anual(self) -> None:
        ano = self.cmbAno.currentData()
        if ano is None:
            if self.cmbAno.count() > 0:
                self.cmbAno.setCurrentIndex(0)
                ano = self.cmbAno.currentData()
            else:
                ano = date.today().year
        if not ano:
            return
        dados = RelatorioService.matriz_vendas_anual(ano=int(ano))

        self._set_chip(self.cardEstoqueBruto, "Estoque Bruto", formatar_moeda(dados.get("estoque_bruto")))
        self._set_chip(self.cardEstoqueLiquido, "Estoque Liquido", formatar_moeda(dados.get("estoque_liquido")))
        self._set_chip(self.cardTotalBruto, "Total Vendas Bruto", formatar_moeda(dados.get("total_ano_bruto")))
        self._set_chip(self.cardTotalLiquido, "Total Vendas Liquido", formatar_moeda(dados.get("total_ano_liquido")))

        self._montar_matriz(dados)

    def _montar_matriz(self, dados: dict[str, Any]) -> None:
        matriz = dados.get("matriz_vendas") or {}
        totais_mensais = dados.get("totais_mensais") or {}

        # 24 columns: 12 months * 2 (Data, Valor)
        self.tableMatriz.setColumnCount(24)
        cabecalhos = []
        for mes in range(12):
            cabecalhos.append(f"{_MESES[mes]} - Data")
            cabecalhos.append(f"{_MESES[mes]} - Valor")
        self.tableMatriz.setHorizontalHeaderLabels(cabecalhos)
        self.tableMatriz.setRowCount(33)  # 31 days + 2 total rows

        for col in range(24):
            item = self.tableMatriz.horizontalHeaderItem(col)
            if col % 2 == 0:
                item.setTextAlignment(Qt.AlignCenter)

        for dia in range(1, 32):
            row = dia - 1
            for mes_idx in range(12):
                mes = mes_idx + 1
                col_data = mes_idx * 2
                col_valor = mes_idx * 2 + 1

                val = matriz.get((mes, dia), 0.0)
                tem_venda = val > 0

                texto_data = f"{dia}-{_MESES[mes_idx]}" if tem_venda else ""
                texto_valor = formatar_moeda(val) if tem_venda else ""

                item_data = QtWidgets.QTableWidgetItem(texto_data)
                item_valor = QtWidgets.QTableWidgetItem(texto_valor)
                item_data.setTextAlignment(Qt.AlignCenter)
                item_valor.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                if tem_venda:
                    item_data.setBackground(_VERDE_FUNDO)
                    item_data.setForeground(_VERDE_TEXTO)
                    item_valor.setBackground(_VERDE_FUNDO)
                    item_valor.setForeground(_VERDE_TEXTO)
                    font = QFont()
                    font.setBold(True)
                    item_data.setFont(font)
                    item_valor.setFont(font)

                self.tableMatriz.setItem(row, col_data, item_data)
                self.tableMatriz.setItem(row, col_valor, item_valor)

        # Total rows
        fonte_total = QFont()
        fonte_total.setBold(True)
        for mes_idx in range(12):
            mes = mes_idx + 1
            total_mes = totais_mensais.get(mes, 0.0)
            col_valor = mes_idx * 2 + 1
            col_data = mes_idx * 2

            item_data_total = QtWidgets.QTableWidgetItem("Total Mes")
            item_valor_total = QtWidgets.QTableWidgetItem(formatar_moeda(total_mes))
            item_data_total.setTextAlignment(Qt.AlignCenter)
            item_valor_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_data_total.setBackground(_AZUL_TOTAL)
            item_data_total.setForeground(_BRANCO)
            item_valor_total.setBackground(_AZUL_TOTAL)
            item_valor_total.setForeground(_BRANCO)
            item_data_total.setFont(fonte_total)
            item_valor_total.setFont(fonte_total)
            self.tableMatriz.setItem(31, col_data, item_data_total)
            self.tableMatriz.setItem(31, col_valor, item_valor_total)

            item_data_liq = QtWidgets.QTableWidgetItem("Total Liq")
            item_valor_liq = QtWidgets.QTableWidgetItem(formatar_moeda(total_mes))
            item_data_liq.setTextAlignment(Qt.AlignCenter)
            item_valor_liq.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_data_liq.setBackground(QColor("#2c3e50"))
            item_data_liq.setForeground(QColor("#ffe59d"))
            item_valor_liq.setBackground(QColor("#2c3e50"))
            item_valor_liq.setForeground(QColor("#ffe59d"))
            item_data_liq.setFont(fonte_total)
            item_valor_liq.setFont(fonte_total)
            self.tableMatriz.setItem(32, col_data, item_data_liq)
            self.tableMatriz.setItem(32, col_valor, item_valor_liq)

        self.tableMatriz.resizeColumnsToContents()

    # ── Tab 1: Produtos ──────────────────────────────────────────────
    def _render_produtos(self) -> None:
        data_ini = self.dateInicial.date().toPyDate()
        data_fim = self.dateFinal.date().toPyDate()
        dados = RelatorioService.produtos_mais_vendidos(data_inicial=data_ini, data_final=data_fim)
        resumo = dados.get("resumo") or {}
        self._set_chip(self.chipVendas, "Vendas", str(int(resumo.get("total_vendas") or 0)))
        self._set_chip(self.chipFaturamento, "Faturamento", formatar_moeda(resumo.get("faturamento")))
        self._set_chip(self.chipTicketMedio, "Itens Vendidos", str(int(resumo.get("total_produtos") or 0)))
        self._set_chip(self.chipClientes, "Produtos", str(len(dados.get("produtos") or [])))

        produtos = dados.get("produtos") or []
        self._desenhar_grafico_barras(produtos)

        self.tableProdutos.setColumnCount(3)
        self.tableProdutos.setHorizontalHeaderLabels(["Produto", "Qtd.", "Receita"])
        self.tableProdutos.setRowCount(len(produtos))
        headers = self.tableProdutos.horizontalHeader()
        headers.setSectionResizeMode(0, headers.Stretch)
        headers.setSectionResizeMode(1, headers.ResizeToContents)
        headers.setSectionResizeMode(2, headers.ResizeToContents)
        for row, item in enumerate(produtos):
            set_table_item(self.tableProdutos, row, 0, str(item.get("produto") or "-"))
            set_table_item(self.tableProdutos, row, 1, str(int(item.get("quantidade") or 0)), alignment=Qt.AlignCenter)
            set_table_item(self.tableProdutos, row, 2, formatar_moeda(item.get("receita")), alignment=Qt.AlignRight | Qt.AlignVCenter)

    def _desenhar_grafico_barras(self, produtos: list[dict]) -> None:
        canvas = self.graficoProdutos
        canvas.limpar()
        ax = canvas.ax
        if not produtos:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", fontsize=14, color="#999")
            canvas.draw()
            return
        nomes = [p.get("produto", "-")[:20] for p in reversed(produtos)]
        quantidades = [int(p.get("quantidade") or 0) for p in reversed(produtos)]
        receitas = [float(p.get("receita") or 0) for p in reversed(produtos)]
        y_pos = range(len(nomes))
        bars = ax.barh(y_pos, quantidades, height=0.6, color=COR["azul"], edgecolor="white", linewidth=0.5)
        for bar, receita in zip(bars, receitas):
            ax.text(bar.get_width() + max(quantidades) * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    formatar_moeda(receita), va="center", ha="left", fontsize=8, color="#555")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(nomes, fontsize=9)
        ax.set_xlabel("Quantidade", fontsize=9, color="#555")
        ax.tick_params(axis="x", labelsize=8, colors="#555")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#ddd")
        ax.spines["bottom"].set_color("#ddd")
        ax.set_axisbelow(True)
        ax.grid(axis="x", linestyle="--", alpha=0.3)
        canvas.draw()

    # ── Tab 2: Clientes ──────────────────────────────────────────────
    def _render_clientes(self) -> None:
        data_ini = self.dateInicial.date().toPyDate()
        data_fim = self.dateFinal.date().toPyDate()
        dados = RelatorioService.clientes_ticket_medio(data_inicial=data_ini, data_final=data_fim)
        resumo = dados.get("resumo") or {}
        self._set_chip(self.chipVendas, "Vendas", str(int(resumo.get("total_vendas") or 0)))
        self._set_chip(self.chipFaturamento, "Faturamento", formatar_moeda(resumo.get("faturamento")))
        self._set_chip(self.chipTicketMedio, "Ticket Medio", formatar_moeda(resumo.get("ticket_medio")))
        self._set_chip(self.chipClientes, "Clientes", str(int(resumo.get("total_clientes") or 0)))

        clientes = dados.get("clientes") or []
        grid = self.gridClientes
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        if not clientes:
            lbl = QLabel("Nenhum cliente encontrado no periodo.")
            lbl.setStyleSheet("color: #999; font-size: 13px; padding: 40px;")
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, 0, 1, 3)
            return
        cores = [COR["azul"], COR["verde"], COR["roxo"], COR["laranja"], "#6c7ea0"]
        cols = min(3, len(clientes)) if len(clientes) >= 3 else 1
        for idx, cli in enumerate(clientes):
            cor = cores[idx % len(cores)]
            row, col = divmod(idx, cols)
            card = self._criar_card_cliente(cli, cor, idx + 1)
            grid.addWidget(card, row, col)

    def _criar_card_cliente(self, cli: dict, cor: str, rank: int) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background-color: white; border: 1px solid #d7e4ef; "
            f"border-radius: 8px; border-left: 4px solid {cor}; }}"
        )
        card.setMinimumHeight(100)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(4)
        header = QHBoxLayout()
        lbl_rank = QLabel(f"#{rank}")
        lbl_rank.setStyleSheet(f"color: {cor}; font-size: 16px; font-weight: bold; background: transparent;")
        header.addWidget(lbl_rank)
        lbl_nome = QLabel(str(cli.get("cliente") or "-"))
        lbl_nome.setStyleSheet("color: #1a3a5c; font-size: 13px; font-weight: bold; background: transparent;")
        header.addWidget(lbl_nome)
        header.addStretch()
        lay.addLayout(header)
        metrics = QHBoxLayout()
        metrics.setSpacing(16)
        for titulo, valor in [
            ("Compras", str(int(cli.get("compras") or 0))),
            ("Total Gasto", formatar_moeda(cli.get("total_gasto"))),
            ("Ticket Medio", formatar_moeda(cli.get("ticket_medio"))),
        ]:
            col = QVBoxLayout()
            col.setSpacing(1)
            lbl_v = QLabel(valor)
            lbl_v.setStyleSheet("color: #1a3a5c; font-size: 14px; font-weight: bold; background: transparent;")
            lbl_t = QLabel(titulo)
            lbl_t.setStyleSheet("color: #7a8ea0; font-size: 10px; background: transparent;")
            col.addWidget(lbl_v)
            col.addWidget(lbl_t)
            metrics.addLayout(col)
        lay.addLayout(metrics)
        return card

    # ── Tab 3: Caixa ─────────────────────────────────────────────────
    def _render_caixa(self) -> None:
        data_ini = self.dateInicial.date().toPyDate()
        data_fim = self.dateFinal.date().toPyDate()
        dados = RelatorioService.caixa_por_periodo(data_inicial=data_ini, data_final=data_fim)
        resumo = dados.get("resumo") or {}
        self._set_chip(self.chipVendas, "Vendas", str(int(resumo.get("total_vendas") or 0)))
        self._set_chip(self.chipFaturamento, "Entradas", formatar_moeda(resumo.get("entradas")))
        self._set_chip(self.chipTicketMedio, "Ticket Medio", formatar_moeda(resumo.get("ticket_medio")))
        self._set_chip(self.chipClientes, "Dias", str(len(dados.get("resumo_periodo") or [])))

        periodo = dados.get("resumo_periodo") or []
        self._desenhar_grafico_linha(periodo)

        self.tableCaixa.setColumnCount(4)
        self.tableCaixa.setHorizontalHeaderLabels(["Periodo", "Vendas", "Faturamento", "Ticket Medio"])
        self.tableCaixa.setRowCount(len(periodo))
        for row, item in enumerate(periodo):
            set_table_item(self.tableCaixa, row, 0, str(item.get("periodo") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableCaixa, row, 1, str(int(item.get("vendas") or 0)), alignment=Qt.AlignCenter)
            set_table_item(self.tableCaixa, row, 2, formatar_moeda(item.get("faturamento")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableCaixa, row, 3, formatar_moeda(item.get("ticket_medio")), alignment=Qt.AlignRight | Qt.AlignVCenter)

    def _desenhar_grafico_linha(self, periodo: list[dict]) -> None:
        canvas = self.graficoCaixa
        canvas.limpar()
        ax = canvas.ax
        if not periodo:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center", fontsize=14, color="#999")
            canvas.draw()
            return
        datas = [str(p.get("periodo") or "") for p in periodo]
        faturamentos = [float(p.get("faturamento") or 0) for p in periodo]
        ax.fill_between(range(len(datas)), faturamentos, alpha=0.15, color=COR["verde"])
        ax.plot(range(len(datas)), faturamentos, color=COR["verde"], linewidth=2.5, marker="o", markersize=5)
        for i, f in enumerate(faturamentos):
            ax.annotate(formatar_moeda(f), (i, f), textcoords="offset points",
                        xytext=(0, 10), ha="center", fontsize=8, color="#333")
        ax.set_xticks(range(len(datas)))
        ax.set_xticklabels(datas, fontsize=8, rotation=30, ha="right")
        ax.set_ylabel("Faturamento", fontsize=9, color="#555")
        ax.tick_params(axis="y", labelsize=8, colors="#555")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#ddd")
        ax.spines["bottom"].set_color("#ddd")
        ax.set_axisbelow(True)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        canvas.fig.subplots_adjust(bottom=0.2)
        canvas.draw()

    # ── Helpers ───────────────────────────────────────────────────────
    @staticmethod
    def _set_chip(chip, titulo: str, valor: str) -> None:
        chip._lbl_titulo.setText(titulo)
        chip._lbl_valor.setText(valor)

    def _exportar_csv(self) -> None:
        tipo = self.tabTipoRelatorio.currentIndex()
        if tipo == 0:
            return
        tabelas = {1: self.tableProdutos, 3: self.tableCaixa}
        tabela = tabelas.get(tipo)
        if tabela is None:
            return
        caminho, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "relatorio.csv", "CSV (*.csv)")
        if not caminho:
            return
        cabecalhos = [tabela.horizontalHeaderItem(c).text() for c in range(tabela.columnCount())]
        linhas = []
        for row in range(tabela.rowCount()):
            linha = []
            for col in range(tabela.columnCount()):
                item = tabela.item(row, col)
                linha.append(item.text() if item else "")
            linhas.append(linha)
        with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(cabecalhos)
            writer.writerows(linhas)
