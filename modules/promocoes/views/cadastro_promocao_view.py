from __future__ import annotations

import json
from datetime import date, datetime

from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtWidgets import (
    QComboBox, QDateTimeEdit, QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from modules.promocoes.services.promocao_service import PromocaoService
from ui.promocoes.cadastro_promocao import Ui_CadastroPromocao
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.ui_messages import mostrar_aviso, mostrar_campos_invalidos, mostrar_info

class CadastroPromocaoView(QDialog, Ui_CadastroPromocao, ValidacaoFormMixin):
    def __init__(self, parent=None, promocao_id: int | None = None):
        super().__init__(parent)
        self.setupUi(self)
        self.lineEditCodigo: QLineEdit
        self.lineEditNomePromocao: QLineEdit
        self.comboClassificacao: QComboBox
        self.comboTipoDesconto: QComboBox
        self.comboStatus: QComboBox
        self.lineEditDescontoPercentual: QLineEdit
        self.lineEditDescontoValor: QLineEdit
        self.lineEditPrecoFixo: QLineEdit
        self.dateTimeInicio: QDateTimeEdit
        self.dateTimeFim: QDateTimeEdit
        self.textEditDescricao: QTextEdit
        self.textEditObservacao: QTextEdit
        self.btnSalvar: QPushButton
        self.btnVoltar: QPushButton
        self.btnLimpar: QPushButton
        self.lblFormTitle: QLabel
        self.lblFormHint: QLabel
        self.frameLeveXPagueY: QFrame
        self.frameDescontoProgressivo: QFrame
        self.frameCombo: QFrame
        self.frameRegraVinculacao: QFrame
        self.frameFaixaPreco: QFrame
        self.lineEditLeveX: QLineEdit
        self.lineEditPagueY: QLineEdit
        self.comboAplicacaoDesconto: QComboBox
        self.tableFaixas: QTableWidget
        self.btnAdicionarFaixa: QPushButton
        self.btnRemoverFaixa: QPushButton
        self.lineEditComboQtd: QLineEdit
        self.lineEditComboPreco: QLineEdit
        self.comboTipoRegra: QComboBox
        self.lineEditValorRegra: QLineEdit
        self.lineEditFaixaPrecoMin: QLineEdit
        self.lineEditFaixaPrecoMax: QLineEdit
        self.btnAplicarRegra: QPushButton
        self.lblResultadoRegra: QLabel
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.promocao_id = int(promocao_id or 0)
        self._dados_carregados: dict[str, object] | None = None

        self._configurar_campos()
        self.registrar_estilos(
            [
                self.lineEditNomePromocao,
                self.comboClassificacao,
                self.comboTipoDesconto,
                self.comboStatus,
                self.lineEditDescontoPercentual,
                self.lineEditDescontoValor,
                self.lineEditPrecoFixo,
            ]
        )
        self.conectar_limpeza_em_tempo_real()

        self.btnSalvar.clicked.connect(self._salvar_promocao)
        self.btnVoltar.clicked.connect(self.reject)
        self.btnLimpar.clicked.connect(self._limpar_campos)
        self.comboTipoRegra.currentTextChanged.connect(self._ajustar_campos_regra)
        self.btnAplicarRegra.clicked.connect(self._aplicar_regra)
        self.btnAdicionarFaixa.clicked.connect(self._adicionar_faixa)
        self.btnRemoverFaixa.clicked.connect(self._remover_faixa)

    def _configurar_campos(self) -> None:
        agora = QDateTime.currentDateTime()
        self.dateTimeInicio.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dateTimeFim.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.comboTipoDesconto.currentTextChanged.connect(self._ajustar_campos_por_tipo)
        self.tableFaixas.setColumnWidth(0, 200)
        self.tableFaixas.setColumnWidth(1, 200)
        if self.promocao_id > 0:
            self._carregar_promocao()
        else:
            self.lineEditCodigo.setText(PromocaoService.gerar_proximo_codigo())
            self.dateTimeInicio.setDateTime(agora)
            self.dateTimeFim.setDateTime(agora.addDays(7))
            self._ajustar_campos_por_tipo()
            self._ajustar_campos_regra()

    @staticmethod
    def _para_qdatetime(valor: object) -> QDateTime:
        if isinstance(valor, QDateTime):
            return valor
        if isinstance(valor, datetime):
            return QDateTime(valor)
        if isinstance(valor, date):
            return QDateTime(datetime.combine(valor, datetime.min.time()))
        return QDateTime.currentDateTime()

    def _carregar_promocao(self) -> None:
        promocao = PromocaoService.buscar_promocao(self.promocao_id)
        if not promocao:
            mostrar_aviso(self, "Promoções", "Não foi possível carregar a promoção selecionada para edição.")
            self.reject()
            return

        self._dados_carregados = dict(promocao)
        self.setWindowTitle("CSPdv - Editar Promoção")
        self.lblFormTitle.setText("Editar Promoção")
        self.lblFormHint.setText("Atualize os dados da promoção antes de revisar vínculos e regras aplicadas.")
        self.btnSalvar.setText("Atualizar")

        self.lineEditCodigo.setText(str(promocao.get("codigo") or ""))
        self.lineEditNomePromocao.setText(str(promocao.get("nome") or ""))
        self.comboClassificacao.setCurrentText(str(promocao.get("classificacao") or "PROMOCAO"))
        self.comboTipoDesconto.setCurrentText(str(promocao.get("tipo_desconto") or "PERCENTUAL"))
        self.comboStatus.setCurrentText(str(promocao.get("status") or "RASCUNHO"))
        self.dateTimeInicio.setDateTime(self._para_qdatetime(promocao.get("data_inicio")))
        self.dateTimeFim.setDateTime(self._para_qdatetime(promocao.get("data_fim")))
        self.lineEditDescontoPercentual.setText(str(promocao.get("desconto_percentual") or 0))
        self.lineEditDescontoValor.setText(str(promocao.get("desconto_valor") or 0))
        self.lineEditPrecoFixo.setText(str(promocao.get("preco_fixo") or 0))
        self.textEditDescricao.setPlainText(str(promocao.get("descricao") or ""))
        self.textEditObservacao.setPlainText(str(promocao.get("observacao") or ""))

        self.lineEditLeveX.setText(str(promocao.get("leve_x") or ""))
        self.lineEditPagueY.setText(str(promocao.get("pague_y") or ""))
        self.comboAplicacaoDesconto.setCurrentText(str(promocao.get("aplicacao_desconto_xpy") or "MAIS_BARATO"))
        self.lineEditComboQtd.setText(str(promocao.get("combo_qtd") or ""))
        self.lineEditComboPreco.setText(str(promocao.get("combo_preco") or 0))

        regras_raw = promocao.get("regras_progressivas")
        if regras_raw:
            try:
                regras = json.loads(str(regras_raw)) if isinstance(regras_raw, str) else regras_raw
                if isinstance(regras, list):
                    self.tableFaixas.setRowCount(0)
                    for r in regras:
                        self._adicionar_faixa_dados(str(r.get("qtd_min", "")), str(r.get("desconto", "")))
            except (json.JSONDecodeError, TypeError):
                pass

        regra = PromocaoService.buscar_regra_da_promocao(self.promocao_id)
        if regra:
            self.comboTipoRegra.setCurrentText(str(regra.get("tipo_regra") or "ITEM"))
            alvo_ids = regra.get("alvo_ids") or ""
            if isinstance(alvo_ids, list):
                alvo_ids = ",".join(str(i) for i in alvo_ids)
            self.lineEditValorRegra.setText(str(alvo_ids))
            faixa_min = regra.get("faixa_preco_min")
            faixa_max = regra.get("faixa_preco_max")
            if faixa_min is not None:
                self.lineEditFaixaPrecoMin.setText(str(faixa_min))
            if faixa_max is not None:
                self.lineEditFaixaPrecoMax.setText(str(faixa_max))
            self._ajustar_campos_regra()

        self._ajustar_campos_por_tipo()

    def _ajustar_campos_por_tipo(self) -> None:
        tipo = self.comboTipoDesconto.currentText().strip().upper()
        self.lineEditDescontoPercentual.setEnabled(tipo == "PERCENTUAL")
        self.lineEditDescontoValor.setEnabled(tipo == "VALOR")
        self.lineEditPrecoFixo.setEnabled(tipo == "PRECO_FIXO")

        self.frameRegra.setVisible(tipo in ("PERCENTUAL", "VALOR", "PRECO_FIXO"))
        self.frameLeveXPagueY.setVisible(tipo == "LEVE_X_PAGUE_Y")
        self.frameDescontoProgressivo.setVisible(tipo == "DESCONTO_PROGRESSIVO")
        self.frameCombo.setVisible(tipo == "COMBO")
        self.frameRegraVinculacao.setVisible(True)

        if tipo != "PERCENTUAL":
            self.lineEditDescontoPercentual.setText("0")
        if tipo != "VALOR":
            self.lineEditDescontoValor.setText("0")
        if tipo != "PRECO_FIXO":
            self.lineEditPrecoFixo.setText("0")

    def _ajustar_campos_regra(self) -> None:
        tipo = self.comboTipoRegra.currentText().strip().upper()
        self.lineEditValorRegra.setVisible(tipo != "FAIXA_PRECO")
        self.lblValorRegra.setVisible(tipo != "FAIXA_PRECO")
        self.frameFaixaPreco.setVisible(tipo == "FAIXA_PRECO")

        if tipo == "ITEM":
            self.lblValorRegra.setText("ID do Produto *")
            self.lineEditValorRegra.setPlaceholderText("Ex: 123")
        elif tipo == "MARCA":
            self.lblValorRegra.setText("Nome da Marca *")
            self.lineEditValorRegra.setPlaceholderText("Ex: Nike")
        elif tipo == "CATEGORIA":
            self.lblValorRegra.setText("Nome da Categoria *")
            self.lineEditValorRegra.setPlaceholderText("Ex: Tenis")
        elif tipo == "FORNECEDOR":
            self.lblValorRegra.setText("Nome do Fornecedor *")
            self.lineEditValorRegra.setPlaceholderText("Ex: Distribuidora ABC")
        elif tipo == "LISTA_ITENS":
            self.lblValorRegra.setText("IDs dos Produtos (separados por virgula) *")
            self.lineEditValorRegra.setPlaceholderText("Ex: 1,2,3")

    def _adicionar_faixa(self) -> None:
        self._adicionar_faixa_dados("", "")

    def _adicionar_faixa_dados(self, qtd: str, desconto: str) -> None:
        row = self.tableFaixas.rowCount()
        self.tableFaixas.insertRow(row)
        item_qtd = QTableWidgetItem(qtd)
        item_desc = QTableWidgetItem(desconto)
        self.tableFaixas.setItem(row, 0, item_qtd)
        self.tableFaixas.setItem(row, 1, item_desc)

    def _remover_faixa(self) -> None:
        row = self.tableFaixas.currentRow()
        if row >= 0:
            self.tableFaixas.removeRow(row)

    def _aplicar_regra(self) -> None:
        if self.promocao_id <= 0:
            mostrar_aviso(self, "Regra", "Salve a promoção antes de aplicar regras de vinculação.")
            return

        regra_dados = self._montar_dados_regra()
        if not regra_dados:
            return

        sucesso, mensagem, vinculados = PromocaoService.salvar_regra_e_vincular(
            self.promocao_id, regra_dados
        )
        if sucesso:
            self.lblResultadoRegra.setText(mensagem)
            self.lblResultadoRegra.setStyleSheet("color: #2e7d32; font-size: 12px; font-weight: 600;")
            mostrar_info(self, "Regra", mensagem)
        else:
            self.lblResultadoRegra.setText(mensagem)
            self.lblResultadoRegra.setStyleSheet("color: #c62828; font-size: 12px; font-weight: 600;")
            mostrar_aviso(self, "Regra", mensagem)

    def _montar_dados_regra(self) -> dict | None:
        tipo = self.comboTipoRegra.currentText().strip().upper()
        valor = self.lineEditValorRegra.text().strip()

        if tipo == "FAIXA_PRECO":
            try:
                min_val = float(self.lineEditFaixaPrecoMin.text().strip().replace(",", "."))
                max_val = float(self.lineEditFaixaPrecoMax.text().strip().replace(",", "."))
            except ValueError:
                mostrar_aviso(self, "Regra", "Informe valores numericos validos para a faixa de preco.")
                return None
            return {"tipo": tipo, "alvo_ids": "", "faixa_min": min_val, "faixa_max": max_val}

        if not valor:
            mostrar_aviso(self, "Regra", f"Informe o valor para a regra do tipo {tipo}.")
            return None

        if tipo == "ITEM":
            try:
                int(valor)
            except ValueError:
                mostrar_aviso(self, "Regra", "O ID do produto deve ser um numero inteiro.")
                return None

        return {"tipo": tipo, "alvo_ids": valor, "faixa_min": None, "faixa_max": None}

    def _salvar_promocao(self) -> None:
        self.limpar_erros()
        nome = self.lineEditNomePromocao.text().strip()
        if not nome:
            self.marcar_invalido(self.lineEditNomePromocao)
            mostrar_campos_invalidos(
                self,
                ["Nome da Promoção: preencha o nome principal da campanha ou promoção."],
                cabecalho="Corrija os seguintes pontos:",
            )
            return

        tipo = self.comboTipoDesconto.currentText().strip().upper()
        dados = {
            "codigo": self.lineEditCodigo.text().strip(),
            "nome": nome,
            "classificacao": self.comboClassificacao.currentText().strip(),
            "tipo_desconto": tipo,
            "status": self.comboStatus.currentText().strip(),
            "descricao": self.textEditDescricao.toPlainText().strip(),
            "observacao": self.textEditObservacao.toPlainText().strip(),
            "desconto_percentual": self.lineEditDescontoPercentual.text().strip(),
            "desconto_valor": self.lineEditDescontoValor.text().strip(),
            "preco_fixo": self.lineEditPrecoFixo.text().strip(),
            "data_inicio": self.dateTimeInicio.dateTime().toPyDateTime(),
            "data_fim": self.dateTimeFim.dateTime().toPyDateTime(),
            "cumulativa": False,
            "ativo": True,
        }

        if tipo == "LEVE_X_PAGUE_Y":
            dados["leve_x"] = self.lineEditLeveX.text().strip()
            dados["pague_y"] = self.lineEditPagueY.text().strip()
            dados["aplicacao_desconto_xpy"] = self.comboAplicacaoDesconto.currentText().strip()
        elif tipo == "DESCONTO_PROGRESSIVO":
            regras = []
            for row in range(self.tableFaixas.rowCount()):
                qtd_item = self.tableFaixas.item(row, 0)
                desc_item = self.tableFaixas.item(row, 1)
                qtd = qtd_item.text().strip() if qtd_item else ""
                desc = desc_item.text().strip() if desc_item else ""
                if qtd and desc:
                    regras.append({"qtd_min": int(qtd), "desconto": float(desc)})
            dados["regras_progressivas"] = regras
        elif tipo == "COMBO":
            dados["combo_qtd"] = self.lineEditComboQtd.text().strip()
            dados["combo_preco"] = self.lineEditComboPreco.text().strip()

        if self.promocao_id > 0:
            sucesso, mensagem = PromocaoService.atualizar_promocao(self.promocao_id, dados)
        else:
            sucesso, mensagem = PromocaoService.cadastrar_promocao(dados)
        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
            return

        self._marcar_campos_por_mensagem(mensagem)
        mostrar_aviso(self, "Atenção", mensagem)

    def _marcar_campos_por_mensagem(self, mensagem: str) -> None:
        texto = mensagem.lower()
        if "nome da promoção" in texto or "nome da promocao" in texto:
            self.marcar_invalido(self.lineEditNomePromocao)
        elif "percentual" in texto:
            self.marcar_invalido(self.lineEditDescontoPercentual)
        elif "valor" in texto and "desconto" in texto:
            self.marcar_invalido(self.lineEditDescontoValor)
        elif "preço" in texto or "preco" in texto:
            self.marcar_invalido(self.lineEditPrecoFixo)
        elif "leve" in texto or "pague" in texto:
            if "leve" in texto:
                self.marcar_invalido(self.lineEditLeveX)
            if "pague" in texto:
                self.marcar_invalido(self.lineEditPagueY)
        elif "progressivo" in texto or "faixa" in texto:
            self.marcar_invalido(self.tableFaixas)
        elif "combo" in texto:
            if "quantidade" in texto:
                self.marcar_invalido(self.lineEditComboQtd)
            elif "preco" in texto:
                self.marcar_invalido(self.lineEditComboPreco)

    def _limpar_campos(self) -> None:
        self.limpar_erros()
        if self.promocao_id > 0:
            self._carregar_promocao()
        else:
            self.lineEditCodigo.setText(PromocaoService.gerar_proximo_codigo())
            self.lineEditNomePromocao.clear()
            self.comboClassificacao.setCurrentIndex(0)
            self.comboTipoDesconto.setCurrentIndex(0)
            self.comboStatus.setCurrentIndex(0)
            self.lineEditDescontoPercentual.setText("0")
            self.lineEditDescontoValor.setText("0")
            self.lineEditPrecoFixo.setText("0")
            self.lineEditLeveX.clear()
            self.lineEditPagueY.clear()
            self.comboAplicacaoDesconto.setCurrentIndex(0)
            self.tableFaixas.setRowCount(0)
            self.lineEditComboQtd.clear()
            self.lineEditComboPreco.setText("0")
            self.comboTipoRegra.setCurrentIndex(0)
            self.lineEditValorRegra.clear()
            self.lineEditFaixaPrecoMin.clear()
            self.lineEditFaixaPrecoMax.clear()
            self.textEditDescricao.clear()
            self.textEditObservacao.clear()
            self.lblResultadoRegra.clear()
            agora = QDateTime.currentDateTime()
            self.dateTimeInicio.setDateTime(agora)
            self.dateTimeFim.setDateTime(agora.addDays(7))
            self._ajustar_campos_por_tipo()
            self._ajustar_campos_regra()
        self.lineEditNomePromocao.setFocus()
