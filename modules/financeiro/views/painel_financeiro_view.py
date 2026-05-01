from __future__ import annotations

from typing import Any, Optional

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QComboBox, QMainWindow, QTableWidget, QTableWidgetItem

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.financeiro.services.reembolso_service import ReembolsoService
from modules.financeiro.services.financeiro_service import FinanceiroService
from ui.financeiro.painel_financeiro import Ui_PainelFinanceiro
from utils.format_utils import formatar_inteiro, formatar_moeda
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.ui_messages import confirmar_acao, mostrar_aviso, mostrar_info


class PainelFinanceiroView(QMainWindow, Ui_PainelFinanceiro, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.cmbPdvFiltro: QComboBox
        self.cmbFormaPagamentoFiltro: QComboBox
        self.tableCaixaMovimentacoes: QTableWidget
        self.tablePagamentos: QTableWidget
        self.tableReembolsos: QTableWidget

        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._configurar_tabelas()
        self._configurar_filtros_iniciais()
        self._conectar_eventos()
        self._carregar_painel()

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self._carregar_painel()

    def _configurar_tabelas(self) -> None:
        return None

    def _configurar_filtros_iniciais(self) -> None:
        self._configurar_periodo_padrao()
        self._carregar_pdvs()
        self._carregar_formas_pagamento()

    def _conectar_eventos(self) -> None:
        self.btnAtualizar.clicked.connect(self._carregar_painel)
        self.btnConsultarVenda.clicked.connect(self._consultar_venda)
        self.btnRegistrarReembolso.clicked.connect(self._novo_reembolso)
        self.btnAbrirCaixa.clicked.connect(self._abrir_caixa_financeiro)
        self.btnFecharCaixa.clicked.connect(self._fechar_caixa_financeiro)
        self.btnRegistrarMovimento.clicked.connect(self._registrar_movimentacao_financeiro)

    def _configurar_periodo_padrao(self) -> None:
        hoje = QDate.currentDate()
        inicio_mes = hoje.addDays(1 - hoje.day())
        self.dateInicial.setDisplayFormat("dd/MM/yyyy")
        self.dateFinal.setDisplayFormat("dd/MM/yyyy")
        self.dateInicial.setDate(inicio_mes)
        self.dateFinal.setDate(hoje)

    def _carregar_pdvs(self) -> None:
        self.cmbPdvFiltro.clear()
        self.cmbPdvFiltro.addItem("Todos os PDVs", None)
        for pdv in FinanceiroService.listar_pdvs():
            descricao = str(pdv.get("descricao") or "").strip()
            identificacao = str(pdv.get("identificacao") or "").strip()
            rotulo = identificacao if not descricao else f"{identificacao} - {descricao}"
            self.cmbPdvFiltro.addItem(rotulo, int(pdv["id"]))

    def _carregar_formas_pagamento(self) -> None:
        self.cmbFormaPagamentoFiltro.clear()
        self.cmbFormaPagamentoFiltro.addItem("Todas as formas de pagamento", None)
        for forma in FinanceiroService.listar_formas_pagamento():
            self.cmbFormaPagamentoFiltro.addItem(str(forma.get("nome") or "Forma"), int(forma["id"]))

    def _carregar_painel(self) -> None:
        self._carregar_cards()
        self._carregar_movimentacoes_caixa()
        self._carregar_recebimentos()
        self._carregar_reembolsos()
        self.lblStatusBar.setText(
            "CSPdv - Módulo Financeiro | "
            f"{self.tableCaixaMovimentacoes.rowCount()} movimentação(ões), "
            f"{self.tablePagamentos.rowCount()} recebimento(s), "
            f"{self.tableReembolsos.rowCount()} reembolso(s)"
        )

    def _abrir_caixa_financeiro(self) -> None:
        if not SessionManager.has_permission("vendas.pdv"):
            mostrar_aviso(
                self,
                "Acesso negado",
                "O usuário atual não possui permissão para abrir caixa por este módulo.",
            )
            return

        usuario = SessionManager.current_user() or {}
        from modules.venda.services.caixa_service import CaixaService

        if not CaixaSession.has_open_caixa():
            CaixaService.restaurar_caixa_aberto(usuario.get("id"))

        if CaixaSession.has_open_caixa():
            mostrar_info(
                self,
                "Caixa já aberto",
                "Já existe um caixa aberto nesta sessão. Você pode acompanhar os dados e fechar o caixa por aqui quando necessário.",
            )
            self._carregar_painel()
            return

        confirmar = confirmar_acao(
            self,
            "Abrir caixa",
            "Deseja abrir o caixa agora sem sair do módulo financeiro?",
        )
        if not confirmar:
            return

        from modules.venda.views.abrir_frente_caixa_dialog import AbrirFrenteCaixaDialog

        dialog = AbrirFrenteCaixaDialog(self)
        if dialog.exec_() != dialog.Accepted:
            return

        self._carregar_painel()
        mostrar_info(
            self,
            "Caixa aberto",
            "Caixa aberto com sucesso. O módulo financeiro foi atualizado com a sessão atual.",
        )

    def _fechar_caixa_financeiro(self) -> None:
        if not CaixaSession.has_open_caixa():
            mostrar_aviso(
                self,
                "Caixa não encontrado",
                "Não há um caixa aberto no momento para encerrar por este módulo.",
            )
            self._carregar_painel()
            return

        from modules.venda.views.fechar_caixa_dialog import FecharCaixaDialog

        dialog = FecharCaixaDialog(self)
        if dialog.exec_() != dialog.Accepted:
            return

        self._carregar_painel()
        mostrar_info(
            self,
            "Caixa fechado",
            "Caixa encerrado com sucesso. O módulo financeiro foi recarregado.",
        )

    def _registrar_movimentacao_financeiro(self) -> None:
        if not CaixaSession.has_open_caixa():
            mostrar_aviso(
                self,
                "Caixa não encontrado",
                "Abra um caixa antes de registrar sangria, suprimento ou reforço de troco.",
            )
            return

        from modules.venda.views.movimentacao_caixa_dialog import MovimentacaoCaixaDialog

        dialog = MovimentacaoCaixaDialog(self)
        if dialog.exec_() == dialog.Accepted:
            self._carregar_painel()

    def _consultar_venda(self) -> None:
        venda_id = self._obter_venda_id_selecionada()
        if not venda_id:
            mostrar_aviso(
                self,
                "Selecione uma venda",
                "Escolha uma linha em Recebimentos da Operação ou Reembolsos Registrados para consultar os detalhes da venda.",
            )
            return

        detalhes = FinanceiroService.obter_venda_detalhada(venda_id)
        if not detalhes:
            mostrar_aviso(
                self,
                "Venda não encontrada",
                "Não foi possível localizar os detalhes da venda selecionada.",
            )
            return

        from modules.financeiro.views.consulta_venda_dialog import ConsultaVendaDialog

        dialog = ConsultaVendaDialog(detalhes, self)
        dialog.exec_()

    def _novo_reembolso(self) -> None:
        venda_id = self._obter_venda_id_selecionada()
        if not venda_id:
            mostrar_aviso(
                self,
                "Selecione uma venda",
                "Escolha uma linha em Recebimentos da Operação para iniciar um novo reembolso.",
            )
            return

        detalhes = FinanceiroService.obter_venda_detalhada(venda_id)
        if not detalhes:
            mostrar_aviso(
                self,
                "Venda não encontrada",
                "Não foi possível localizar os detalhes da venda selecionada.",
            )
            return

        from modules.financeiro.views.novo_reembolso_dialog import NovoReembolsoDialog

        dialog = NovoReembolsoDialog(detalhes, self)
        if dialog.exec_() != dialog.Accepted or not dialog.resultado:
            return

        sucesso, mensagem, resultado = ReembolsoService.registrar_reembolso(dialog.resultado)
        if not sucesso or resultado is None:
            mostrar_aviso(self, "Reembolso não registrado", mensagem)
            return

        self._carregar_painel()
        mostrar_info(
            self,
            "Reembolso registrado",
            f"{mensagem}\n\nReembolso #{resultado['reembolso_id']} | Venda #{resultado['venda_id']} | Valor {formatar_moeda(resultado['valor_total'])}",
        )

    def _obter_venda_id_selecionada(self) -> Optional[int]:
        for table in (self.tablePagamentos, self.tableReembolsos):
            row = table.currentRow()
            if row < 0:
                continue
            item = table.item(row, 0)
            if not item:
                continue
            value = item.data(Qt.UserRole)
            try:
                venda_id = int(value)
            except (TypeError, ValueError):
                continue
            if venda_id > 0:
                return venda_id
        return None

    def _carregar_cards(self) -> None:
        resumo = FinanceiroService.obter_resumo_financeiro(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
            forma_pagamento=self._forma_pagamento_filtro(),
        )
        self.lblSaldoCaixaValor.setText(formatar_moeda(resumo.get("saldo_atual_caixa")))
        self.lblEntradasDiaValor.setText(formatar_moeda(resumo.get("entradas_periodo")))
        self.lblSaidasDiaValor.setText(formatar_moeda(resumo.get("saidas_periodo")))
        self.lblPagamentosPendentesValor.setText(formatar_inteiro(resumo.get("reembolsos_periodo")))

    def _carregar_movimentacoes_caixa(self) -> None:
        registros = FinanceiroService.listar_movimentacoes_caixa(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
        )

        registros.sort(key=lambda r: r.get("data_hora") or 0, reverse=True)

        self.tableCaixaMovimentacoes.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            self._set_table_item(self.tableCaixaMovimentacoes, row, 0, self._formatar_data_hora(registro.get("data_hora")))
            self._set_table_item(self.tableCaixaMovimentacoes, row, 1, str(registro.get("pdv") or "-"))
            self._set_table_item(self.tableCaixaMovimentacoes, row, 2, str(registro.get("operador") or "-"))
            self._set_table_item(self.tableCaixaMovimentacoes, row, 3, str(registro.get("motivo") or "-"))
            self._set_table_item(self.tableCaixaMovimentacoes, row, 4, str(registro.get("forma_pagamento") or "-"))
            self._set_table_item(
                self.tableCaixaMovimentacoes,
                row,
                5,
                formatar_moeda(registro.get("valor")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )

    @staticmethod
    def _agrupar_por_venda(registros: list) -> list:
        agrupado: dict = {}
        for reg in registros:
            vid = int(reg.get("venda_id") or 0)
            if vid == 0:
                continue

            if vid not in agrupado:
                agrupado[vid] = {
                    "venda_id":       vid,
                    "cliente":        reg.get("cliente") or "-",
                    "status":         reg.get("status") or "-",
                    "valor_pago":     float(reg.get("valor_pago") or 0),
                    "_formas":        set(),
                }

            # Acumular valor
            agrupado[vid]["valor_pago"] += float(reg.get("valor_pago") or 0)

            # Coletar formas distintas (ignora None / vazio)
            forma = str(reg.get("forma_pagamento") or "").strip()
            if forma:
                agrupado[vid]["_formas"].add(forma)

        # Montar forma_pagamento final e limpar campo auxiliar
        resultado = []
        for entrada in agrupado.values():
            formas_ordenadas = sorted(entrada.pop("_formas"))
            entrada["forma_pagamento"] = " + ".join(formas_ordenadas) if formas_ordenadas else "-"
            resultado.append(entrada)

        # Manter ordenação por venda_id
        resultado.sort(key=lambda r: r["venda_id"], reverse=True)
        return resultado

    def _carregar_recebimentos(self) -> None:
        registros = FinanceiroService.listar_recebimentos(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
            forma_pagamento=self._forma_pagamento_filtro(),
        )

        agrupados = self._agrupar_por_venda(registros)

        self.tablePagamentos.setRowCount(len(agrupados))
        for row, registro in enumerate(agrupados):
            item_venda = self._set_table_item(
                self.tablePagamentos,
                row,
                0,
                str(registro["venda_id"]),
                alignment=Qt.AlignCenter,
            )
            item_venda.setData(Qt.UserRole, registro["venda_id"])
            self._set_table_item(self.tablePagamentos, row, 1, str(registro["cliente"]))
            self._set_table_item(self.tablePagamentos, row, 2, str(registro["forma_pagamento"]))
            self._set_table_item(self.tablePagamentos, row, 3, str(registro["status"]), alignment=Qt.AlignCenter)
            self._set_table_item(
                self.tablePagamentos,
                row,
                4,
                formatar_moeda(registro["valor_pago"]),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )

    def _carregar_reembolsos(self) -> None:
        registros = FinanceiroService.listar_reembolsos(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
            forma_pagamento=self._forma_pagamento_filtro(),
        )
        registros.sort(
            key=lambda r: (
                r.get("data_hora") or 0,
                int(r.get("reembolso_id") or 0),
            ),
            reverse=True,
        )
        self.tableReembolsos.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            item_venda = self._set_table_item(
                self.tableReembolsos,
                row,
                0,
                str(registro.get("venda_id") or "-"),
                alignment=Qt.AlignCenter,
            )
            item_venda.setData(Qt.UserRole, int(registro.get("venda_id") or 0))
            self._set_table_item(self.tableReembolsos, row, 1, str(registro.get("tipo") or "-"), alignment=Qt.AlignCenter)
            self._set_table_item(self.tableReembolsos, row, 2, str(registro.get("motivo") or "-"))
            self._set_table_item(self.tableReembolsos, row, 3, str(registro.get("status") or "-"), alignment=Qt.AlignCenter)
            self._set_table_item(
                self.tableReembolsos,
                row,
                4,
                formatar_moeda(registro.get("valor_total")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )

    def _forma_pagamento_filtro(self) -> Optional[str]:
        if self.cmbFormaPagamentoFiltro.currentData() is None:
            return None
        return self.cmbFormaPagamentoFiltro.currentText().strip() or None

    @staticmethod
    def _combo_data_int(combo: QComboBox) -> Optional[int]:
        value = combo.currentData()
        if value in (None, "", 0, "0"):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _set_table_item(
        table: QTableWidget,
        row: int,
        column: int,
        value: str,
        *,
        alignment: Any = Qt.AlignLeft | Qt.AlignVCenter,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(value)
        item.setTextAlignment(int(alignment))
        table.setItem(row, column, item)
        return item

    @staticmethod
    def _formatar_data_hora(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y %H:%M")
        return "-"
