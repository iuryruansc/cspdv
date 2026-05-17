from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from modules.pdvs.models.pdv_model import PdvModel
from modules.pdvs.services.pdv_service import PdvService
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import texto_limpo, texto_maiusculo
from utils.ui_messages import mostrar_aviso, mostrar_campos_invalidos, mostrar_info


class CadastroPdvView(QDialog, ValidacaoFormMixin):
    def __init__(self, parent=None, pdv_id=None):
        super().__init__(parent)
        self._pdv_id = int(pdv_id) if pdv_id is not None else None
        self._montar_ui()
        self.registrar_estilos([self.lineEditIdentificacao, self.lineEditDescricao])
        self.conectar_limpeza_em_tempo_real()
        self._configurar_modo()

    def _montar_ui(self) -> None:
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.resize(480, 250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.lblBadge = QLabel("CADASTRO DE PDV")
        self.lblBadge.setStyleSheet("font-size: 11px; font-weight: bold; color: #1a5fa0;")
        layout.addWidget(self.lblBadge)

        self.lblFormTitle = QLabel("Dados do PDV")
        self.lblFormTitle.setStyleSheet("font-size: 20px; font-weight: bold; color: #16324f;")
        layout.addWidget(self.lblFormTitle)

        form = QFormLayout()
        form.setSpacing(10)

        self.lineEditCodigo = QLineEdit()
        self.lineEditCodigo.setReadOnly(True)
        form.addRow("Código", self.lineEditCodigo)

        self.lineEditIdentificacao = QLineEdit()
        self.lineEditIdentificacao.setPlaceholderText("Ex: PDV-01")
        form.addRow("Identificação *", self.lineEditIdentificacao)

        self.lineEditDescricao = QLineEdit()
        self.lineEditDescricao.setPlaceholderText("Ex: Caixa Principal")
        form.addRow("Descrição *", self.lineEditDescricao)

        self.checkBoxAtivo = QCheckBox("PDV ativo")
        self.checkBoxAtivo.setChecked(True)
        form.addRow("Status", self.checkBoxAtivo)

        layout.addLayout(form)

        botoes = QHBoxLayout()
        botoes.addStretch(1)
        self.btnLimpar = QPushButton("Limpar")
        self.btnVoltar = QPushButton("Cancelar")
        self.btnSalvar = QPushButton("Salvar")
        botoes.addWidget(self.btnLimpar)
        botoes.addWidget(self.btnVoltar)
        botoes.addWidget(self.btnSalvar)
        layout.addLayout(botoes)

        self.btnSalvar.clicked.connect(self._salvar_pdv)
        self.btnVoltar.clicked.connect(self.reject)
        self.btnLimpar.clicked.connect(self._limpar_campos)

    def _configurar_modo(self) -> None:
        if self._pdv_id is None:
            self.lineEditCodigo.setText("Auto-gerado")
            return

        pdv = PdvModel.buscar_por_id(self._pdv_id)
        if not pdv:
            mostrar_aviso(self, "PDV não encontrado", "Não foi possível carregar o PDV para edição.")
            self.reject()
            return

        self.lblBadge.setText("EDIÇÃO DE PDV")
        self.lineEditCodigo.setText(str(pdv.get("id") or ""))
        self.lineEditIdentificacao.setText(str(pdv.get("identificacao") or ""))
        self.lineEditDescricao.setText(str(pdv.get("descricao") or ""))
        self.checkBoxAtivo.setChecked(str(pdv.get("ativo") or "N").upper() == "S")
        self.btnSalvar.setText("Atualizar")

    def _salvar_pdv(self) -> None:
        self.limpar_erros()

        identificacao = texto_maiusculo(texto_limpo(self.lineEditIdentificacao.text()))
        descricao = texto_limpo(self.lineEditDescricao.text())
        dados = {
            "identificacao": identificacao,
            "descricao": descricao,
            "ativo": "S" if self.checkBoxAtivo.isChecked() else "N",
        }

        erros = []
        if not identificacao:
            self.marcar_invalido(self.lineEditIdentificacao)
            erros.append("Identificação: informe o código do PDV.")
        if not descricao:
            self.marcar_invalido(self.lineEditDescricao)
            erros.append("Descrição: informe a descrição do PDV.")
        if erros:
            mostrar_campos_invalidos(self, erros)
            return

        if self._pdv_id is None:
            sucesso, mensagem = PdvService.cadastrar_pdv(dados)
        else:
            sucesso, mensagem = PdvService.atualizar_pdv(self._pdv_id, dados)

        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
            return

        if "identificação" in mensagem.lower():
            self.marcar_invalido(self.lineEditIdentificacao)
        if "descrição" in mensagem.lower():
            self.marcar_invalido(self.lineEditDescricao)
        mostrar_aviso(self, "Atenção", mensagem)

    def _limpar_campos(self) -> None:
        self.limpar_erros()
        self.lineEditIdentificacao.clear()
        self.lineEditDescricao.clear()
        self.checkBoxAtivo.setChecked(True)
        self.lineEditIdentificacao.setFocus()
