from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from modules.formas_pagamento.models.forma_pagamento_model import FormaPagamentoModel
from modules.formas_pagamento.services.forma_pagamento_service import FormaPagamentoService
from utils.form_validation_mixin import ValidacaoFormMixin
from utils.string_utils import texto_limpo, texto_maiusculo
from utils.ui_messages import mostrar_aviso, mostrar_campos_invalidos, mostrar_info


class CadastroFormaPagamentoView(QDialog, ValidacaoFormMixin):
    def __init__(self, parent=None, forma_pagamento_id=None):
        super().__init__(parent)
        self._forma_pagamento_id = int(forma_pagamento_id) if forma_pagamento_id is not None else None
        self._montar_ui()
        self.registrar_estilos([self.lineEditNome, self.lineEditTipoSefaz, self.lineEditTaxa])
        self.conectar_limpeza_em_tempo_real()
        self._configurar_modo()

    def _montar_ui(self) -> None:
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.resize(460, 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.lblBadge = QLabel("CADASTRO DE FORMA DE PAGAMENTO")
        self.lblBadge.setStyleSheet("font-size: 11px; font-weight: bold; color: #1a5fa0;")
        layout.addWidget(self.lblBadge)

        self.lblFormTitle = QLabel("Dados da Forma de Pagamento")
        self.lblFormTitle.setStyleSheet("font-size: 20px; font-weight: bold; color: #16324f;")
        layout.addWidget(self.lblFormTitle)

        form = QFormLayout()
        form.setSpacing(10)

        self.lineEditCodigo = QLineEdit()
        self.lineEditCodigo.setReadOnly(True)
        form.addRow("Código", self.lineEditCodigo)

        self.lineEditNome = QLineEdit()
        self.lineEditNome.setPlaceholderText("Nome da forma de pagamento")
        form.addRow("Nome *", self.lineEditNome)

        self.lineEditTipoSefaz = QLineEdit()
        self.lineEditTipoSefaz.setMaxLength(2)
        self.lineEditTipoSefaz.setPlaceholderText("01")
        form.addRow("Tipo SEFAZ *", self.lineEditTipoSefaz)

        self.comboParcelamento = QComboBox()
        self.comboParcelamento.addItem("Não permite", "N")
        self.comboParcelamento.addItem("Permite", "S")
        form.addRow("Parcelamento", self.comboParcelamento)

        self.lineEditTaxa = QLineEdit()
        self.lineEditTaxa.setPlaceholderText("0,00")
        form.addRow("Taxa administrativa (%)", self.lineEditTaxa)

        self.checkBoxAtivo = QCheckBox("Forma de pagamento ativa")
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

        self.btnSalvar.clicked.connect(self._salvar_forma_pagamento)
        self.btnVoltar.clicked.connect(self.reject)
        self.btnLimpar.clicked.connect(self._limpar_campos)

    def _configurar_modo(self) -> None:
        if self._forma_pagamento_id is None:
            self.lineEditCodigo.setText("Auto-gerado")
            return

        forma = FormaPagamentoModel.buscar_por_id(self._forma_pagamento_id)
        if not forma:
            mostrar_aviso(
                self,
                "Forma de pagamento não encontrada",
                "Não foi possível carregar a forma de pagamento para edição.",
            )
            self.reject()
            return

        self.lblBadge.setText("EDIÇÃO DE FORMA DE PAGAMENTO")
        self.lineEditCodigo.setText(str(forma.get("id") or ""))
        self.lineEditNome.setText(str(forma.get("nome") or ""))
        self.lineEditTipoSefaz.setText(str(forma.get("tipo_sefaz") or ""))
        self.comboParcelamento.setCurrentIndex(1 if str(forma.get("permite_parcelamento") or "N").upper() == "S" else 0)
        taxa = str(forma.get("taxa_administrativa") or "0").replace(".", ",")
        self.lineEditTaxa.setText(taxa)
        self.checkBoxAtivo.setChecked(str(forma.get("ativo") or "N").upper() == "S")
        self.btnSalvar.setText("Atualizar")

    def _salvar_forma_pagamento(self) -> None:
        self.limpar_erros()

        nome = texto_maiusculo(texto_limpo(self.lineEditNome.text()))
        tipo_sefaz = texto_limpo(self.lineEditTipoSefaz.text())
        taxa_texto = texto_limpo(self.lineEditTaxa.text()).replace(".", "").replace(",", ".")
        try:
            taxa = float(taxa_texto or "0")
        except ValueError:
            taxa = -1.0

        dados = {
            "nome": nome,
            "tipo_sefaz": tipo_sefaz,
            "permite_parcelamento": str(self.comboParcelamento.currentData() or "N"),
            "taxa_administrativa": taxa,
            "ativo": "S" if self.checkBoxAtivo.isChecked() else "N",
        }

        if not nome:
            self.marcar_invalido(self.lineEditNome)
            mostrar_campos_invalidos(self, ["Nome: informe a forma de pagamento."])
            return

        if not tipo_sefaz:
            self.marcar_invalido(self.lineEditTipoSefaz)
            mostrar_campos_invalidos(self, ["Tipo SEFAZ: informe o código correspondente."])
            return

        if taxa < 0:
            self.marcar_invalido(self.lineEditTaxa)
            mostrar_campos_invalidos(self, ["Taxa administrativa: informe um valor válido maior ou igual a zero."])
            return

        if self._forma_pagamento_id is None:
            sucesso, mensagem = FormaPagamentoService.cadastrar_forma_pagamento(dados)
        else:
            sucesso, mensagem = FormaPagamentoService.atualizar_forma_pagamento(self._forma_pagamento_id, dados)

        if sucesso:
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
            return

        if "nome" in mensagem.lower():
            self.marcar_invalido(self.lineEditNome)
        if "sefaz" in mensagem.lower():
            self.marcar_invalido(self.lineEditTipoSefaz)
        if "taxa" in mensagem.lower():
            self.marcar_invalido(self.lineEditTaxa)
        mostrar_aviso(self, "Atenção", mensagem)

    def _limpar_campos(self) -> None:
        self.limpar_erros()
        self.lineEditNome.clear()
        self.lineEditTipoSefaz.clear()
        self.lineEditTaxa.clear()
        self.comboParcelamento.setCurrentIndex(0)
        self.checkBoxAtivo.setChecked(True)
        self.lineEditNome.setFocus()
