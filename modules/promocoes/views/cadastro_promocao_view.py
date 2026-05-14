from __future__ import annotations

from datetime import date, datetime

from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtWidgets import QComboBox, QDateTimeEdit, QDialog, QLabel, QLineEdit, QPushButton, QTextEdit

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

    def _configurar_campos(self) -> None:
        agora = QDateTime.currentDateTime()
        self.dateTimeInicio.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.dateTimeFim.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.comboTipoDesconto.currentTextChanged.connect(self._ajustar_campos_por_tipo)
        if self.promocao_id > 0:
            self._carregar_promocao()
        else:
            self.lineEditCodigo.setText(PromocaoService.gerar_proximo_codigo())
            self.dateTimeInicio.setDateTime(agora)
            self.dateTimeFim.setDateTime(agora.addDays(7))
            self._ajustar_campos_por_tipo()

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
        self._ajustar_campos_por_tipo()

    def _ajustar_campos_por_tipo(self) -> None:
        tipo = self.comboTipoDesconto.currentText().strip().upper()
        self.lineEditDescontoPercentual.setEnabled(tipo == "PERCENTUAL")
        self.lineEditDescontoValor.setEnabled(tipo == "VALOR")
        self.lineEditPrecoFixo.setEnabled(tipo == "PRECO_FIXO")

        if tipo != "PERCENTUAL":
            self.lineEditDescontoPercentual.setText("0")
        if tipo != "VALOR":
            self.lineEditDescontoValor.setText("0")
        if tipo != "PRECO_FIXO":
            self.lineEditPrecoFixo.setText("0")

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

        dados = {
            "codigo": self.lineEditCodigo.text().strip(),
            "nome": nome,
            "classificacao": self.comboClassificacao.currentText().strip(),
            "tipo_desconto": self.comboTipoDesconto.currentText().strip(),
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
            self.textEditDescricao.clear()
            self.textEditObservacao.clear()
            agora = QDateTime.currentDateTime()
            self.dateTimeInicio.setDateTime(agora)
            self.dateTimeFim.setDateTime(agora.addDays(7))
            self._ajustar_campos_por_tipo()
        self.lineEditNomePromocao.setFocus()
