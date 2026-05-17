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

from modules.unidades.models.unidade_model import UnidadeModel
from modules.unidades.services.unidade_service import UnidadeService
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import texto_limpo, texto_maiusculo
from utils.ui_messages import mostrar_aviso, mostrar_campos_invalidos, mostrar_info


class CadastroUnidadeView(QDialog, ValidacaoFormMixin):
    def __init__(self, parent=None, unidade_id=None):
        super().__init__(parent)
        self._unidade_id = int(unidade_id) if unidade_id is not None else None
        self._montar_ui()
        self.registrar_estilos([self.lineEditSigla, self.lineEditDescricao, self.lineEditCodigoSefaz])
        self.conectar_limpeza_em_tempo_real()
        self._configurar_modo()

    def _montar_ui(self) -> None:
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.resize(500, 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.lblBadge = QLabel("CADASTRO DE UNIDADE")
        self.lblBadge.setStyleSheet("font-size: 11px; font-weight: bold; color: #1a5fa0;")
        layout.addWidget(self.lblBadge)

        self.lblFormTitle = QLabel("Dados da Unidade")
        self.lblFormTitle.setStyleSheet("font-size: 20px; font-weight: bold; color: #16324f;")
        layout.addWidget(self.lblFormTitle)

        form = QFormLayout()
        form.setSpacing(10)

        self.lineEditCodigo = QLineEdit()
        self.lineEditCodigo.setReadOnly(True)
        form.addRow("Código", self.lineEditCodigo)

        self.lineEditSigla = QLineEdit()
        self.lineEditSigla.setMaxLength(6)
        self.lineEditSigla.setPlaceholderText("Ex: UN")
        form.addRow("Sigla *", self.lineEditSigla)

        self.lineEditDescricao = QLineEdit()
        self.lineEditDescricao.setPlaceholderText("Ex: Unidade")
        form.addRow("Descrição *", self.lineEditDescricao)

        self.lineEditCodigoSefaz = QLineEdit()
        self.lineEditCodigoSefaz.setMaxLength(6)
        self.lineEditCodigoSefaz.setPlaceholderText("Opcional")
        form.addRow("Código SEFAZ", self.lineEditCodigoSefaz)

        self.checkBoxFracionavel = QCheckBox("Permite fracionamento")
        form.addRow("Fracionável", self.checkBoxFracionavel)

        self.checkBoxAtivo = QCheckBox("Unidade ativa")
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

        self.btnSalvar.clicked.connect(self._salvar_unidade)
        self.btnVoltar.clicked.connect(self.reject)
        self.btnLimpar.clicked.connect(self._limpar_campos)

    def _configurar_modo(self) -> None:
        if self._unidade_id is None:
            self.lineEditCodigo.setText("Auto-gerado")
            return

        unidade = UnidadeModel.buscar_por_id(self._unidade_id)
        if not unidade:
            mostrar_aviso(self, "Unidade não encontrada", "Não foi possível carregar a unidade para edição.")
            self.reject()
            return

        self.lblBadge.setText("EDIÇÃO DE UNIDADE")
        self.lineEditCodigo.setText(str(unidade.get("id") or ""))
        self.lineEditSigla.setText(str(unidade.get("sigla") or ""))
        self.lineEditDescricao.setText(str(unidade.get("descricao") or ""))
        self.lineEditCodigoSefaz.setText(str(unidade.get("codigo_sefaz") or ""))
        self.checkBoxFracionavel.setChecked(bool(unidade.get("fracionavel")))
        self.checkBoxAtivo.setChecked(str(unidade.get("ativo") or "N").upper() == "S")
        self.btnSalvar.setText("Atualizar")

    def _salvar_unidade(self) -> None:
        self.limpar_erros()

        sigla = texto_maiusculo(texto_limpo(self.lineEditSigla.text()))
        descricao = texto_limpo(self.lineEditDescricao.text())
        codigo_sefaz = texto_maiusculo(texto_limpo(self.lineEditCodigoSefaz.text()))
        dados = {
            "sigla": sigla,
            "descricao": descricao,
            "codigo_sefaz": codigo_sefaz,
            "fracionavel": self.checkBoxFracionavel.isChecked(),
            "ativo": "S" if self.checkBoxAtivo.isChecked() else "N",
        }

        erros = []
        if not sigla:
            self.marcar_invalido(self.lineEditSigla)
            erros.append("Sigla: informe a sigla da unidade.")
        if not descricao:
            self.marcar_invalido(self.lineEditDescricao)
            erros.append("Descrição: informe a descrição da unidade.")
        if erros:
            mostrar_campos_invalidos(self, erros)
            return

        if self._unidade_id is None:
            sucesso, mensagem = UnidadeService.cadastrar_unidade(dados)
        else:
            sucesso, mensagem = UnidadeService.atualizar_unidade(self._unidade_id, dados)

        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
            return

        if "sigla" in mensagem.lower():
            self.marcar_invalido(self.lineEditSigla)
        if "descrição" in mensagem.lower():
            self.marcar_invalido(self.lineEditDescricao)
        if "sefaz" in mensagem.lower():
            self.marcar_invalido(self.lineEditCodigoSefaz)
        mostrar_aviso(self, "Atenção", mensagem)

    def _limpar_campos(self) -> None:
        self.limpar_erros()
        self.lineEditSigla.clear()
        self.lineEditDescricao.clear()
        self.lineEditCodigoSefaz.clear()
        self.checkBoxFracionavel.setChecked(False)
        self.checkBoxAtivo.setChecked(True)
        self.lineEditSigla.setFocus()
