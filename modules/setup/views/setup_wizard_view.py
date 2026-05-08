import re

import requests
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit

from modules.setup.models.setup_model import SetupModel
from ui.setup import (
    PageAdminUi,
    PageBoasVindasUi,
    PageConclusaoUi,
    PageEmpresaUi,
    PageEnderecoUi,
    PagePDVUi,
    SetupWizardUi,
)

class PageBoasVindas(PageBoasVindasUi):
    def validate(self) -> bool:
        return True

    def get_data(self) -> dict:
        return {}

class PageEmpresa(PageEmpresaUi):
    def validate(self):
        razao = self.f_razao.value()
        cnpj = re.sub(r"\D", "", self.f_cnpj.value())
        email = self.f_email.value()
        tel_limpo = re.sub(r"\D", "", self.f_telefone.value())

        if tel_limpo and len(tel_limpo) < 10:
            self.show_error("Telefone incompleto.")
            return False
        if not razao or len(razao) < 3:
            self.show_error("Razão Social é obrigatória.")
            return False
        if not self.validar_cnpj(cnpj):
            self.show_error("CNPJ inválido ou mal formatado.")
            return False
        if email and not self.validar_email(email):
            self.show_error("O formato do e-mail informado é inválido.")
            return False

        self.hide_error()
        return True

    def validar_email(self, email):
        regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        return re.search(regex, email.lower())

    def validar_cnpj(self, cnpj):
        cnpj = re.sub(r"\D", "", cnpj)
        if len(cnpj) != 14 or len(set(cnpj)) == 1:
            return False

        def calcular_digito(cnpj_base, pesos):
            soma = sum(int(a) * b for a, b in zip(cnpj_base, pesos))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        digito1 = calcular_digito(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        digito2 = calcular_digito(cnpj[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        return cnpj[-2:] == f"{digito1}{digito2}"

    def get_data(self):
        return {
            "razao_social": self.f_razao.value(),
            "nome_fantasia": self.f_fantasia.value(),
            "cnpj": re.sub(r"\D", "", self.f_cnpj.value()),
            "inscricao_estadual": self.f_ie.value(),
            "regime_tributario": self.f_regime.value(),
            "email": self.f_email.value(),
            "telefone": self.f_telefone.value(),
        }

class PageEndereco(PageEnderecoUi):
    def __init__(self):
        super().__init__()
        if isinstance(self.f_cep.field_widget, QLineEdit):
            self.f_cep.field_widget.editingFinished.connect(self.consultar_cep)

    def consultar_cep(self):
        cep = re.sub(r"\D", "", self.f_cep.value())
        if len(cep) == 8:
            try:
                response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=3)
                data = response.json()
                if "erro" not in data:
                    self.f_logr.set_value(data.get("logradouro", ""))
                    self.f_bairro.set_value(data.get("bairro", ""))
                    self.f_cidade.set_value(data.get("localidade", ""))
                    self.f_estado.set_value(data.get("uf", ""))
                    self.f_numero.field_widget.setFocus()
            except (requests.RequestException, ValueError):
                pass

    def validate(self) -> bool:
        self.hide_error()
        return True

    def get_data(self):
        return {
            "cep": re.sub(r"\D", "", self.f_cep.value()),
            "logradouro": self.f_logr.value(),
            "numero": self.f_numero.value(),
            "bairro": self.f_bairro.value(),
            "cidade": self.f_cidade.value(),
            "estado": self.f_estado.value(),
        }

class PagePDV(PagePDVUi):
    def validate(self):
        if not self.f_id.value():
            self.show_error("Identificação do PDV é obrigatória.")
            return False
        self.hide_error()
        return True

    def get_data(self):
        return {
            "identificacao": self.f_id.value(),
            "descricao": self.f_desc.value() or self.f_id.value(),
        }

class PageAdmin(PageAdminUi):
    def validate(self):
        if not self.f_nome.value():
            self.show_error("Nome completo é obrigatório.")
            return False
        if not self.f_login.value():
            self.show_error("Login é obrigatório.")
            return False
        if len(self.f_senha.value()) < 6:
            self.show_error("Senha deve ter pelo menos 6 caracteres.")
            return False
        if self.f_senha.value() != self.f_confirma.value():
            self.show_error("As senhas não coincidem.")
            return False
        if self.f_email.value() and not self.validar_email(self.f_email.value()):
            self.show_error("O formato do e-mail informado é inválido.")
            return False
        self.hide_error()
        return True

    def validar_email(self, email):
        regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        return re.search(regex, email.lower())

    def get_data(self):
        return {
            "nome_completo": self.f_nome.value(),
            "login": self.f_login.value(),
            "email": self.f_email.value(),
            "senha": self.f_senha.value(),
        }

class PageConclusao(PageConclusaoUi):
    def validate(self) -> bool:
        return True

    def get_data(self) -> dict:
        return {}

    def preencher_resumo(self, empresa, pdv, admin):
        regime = empresa.get("regime_tributario", "")
        cidade = empresa.get("cidade", "")
        estado = empresa.get("estado", "")
        local = f"{cidade}/{estado}" if cidade else "—"
        self.lbl_resumo.setText(
            f"<b>Empresa:</b>  {empresa.get('razao_social', '—')}<br>"
            f"<b>CNPJ:</b>  {empresa.get('cnpj', '—')}<br>"
            f"<b>Regime:</b>  {regime}<br>"
            f"<b>Localização:</b>  {local}<br><br>"
            f"<b>PDV:</b>  {pdv.get('identificacao', '—')}  —  {pdv.get('descricao', '')}<br><br>"
            f"<b>Administrador:</b>  {admin.get('nome_completo', '—')}<br>"
            f"<b>Login:</b>  {admin.get('login', '—')}"
        )

class SetupWizardView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dados_empresa = {}
        self._dados_pdv = {}
        self._dados_admin = {}
        self._finalizado = False

        self.pages = [
            PageBoasVindas(),
            PageEmpresa(),
            PageEndereco(),
            PagePDV(),
            PageAdmin(),
            PageConclusao(),
        ]

        self.ui = SetupWizardUi()
        self.ui.setupUi(self, self.pages)

        self.stack = self.ui.stack
        self.progress = self.ui.progress
        self.step_labels = self.ui.step_labels
        self.lbl_status = self.ui.lbl_status
        self.btn_voltar = self.ui.btn_voltar
        self.btn_avancar = self.ui.btn_avancar

        self.btn_avancar.clicked.connect(self._avancar)
        self.btn_voltar.clicked.connect(self._voltar)

        self._current = 0

    def _avancar(self):
        page = self.pages[self._current]
        if not page.validate():
            return

        if self._current == len(self.pages) - 1:
            self._salvar()
            return

        self._current += 1
        self.stack.setCurrentIndex(self._current)
        self._atualizar_ui()

        if self._current == len(self.pages) - 1:
            self._dados_empresa = {**self.pages[1].get_data(), **self.pages[2].get_data()}
            self._dados_pdv = self.pages[3].get_data()
            self._dados_admin = self.pages[4].get_data()
            self.pages[5].preencher_resumo(
                self._dados_empresa,
                self._dados_pdv,
                self._dados_admin,
            )

    def _voltar(self):
        if self._current > 0:
            self._current -= 1
            self.stack.setCurrentIndex(self._current)
            self._atualizar_ui()

    def _atualizar_ui(self):
        current = self._current
        total = len(self.pages)

        self.progress.setValue(current)
        self.btn_voltar.setVisible(current > 0)

        if current == total - 1:
            self.btn_avancar.setText("✓  Concluir")
        elif current == 0:
            self.btn_avancar.setText("Começar  ▶")
        else:
            self.btn_avancar.setText("Avançar  ▶")

        for index, label in enumerate(self.step_labels):
            name = label.text().split("  ", 1)[1] if "  " in label.text() else label.text()
            if index == current:
                label.setText(f"●  {name}")
                label.setStyleSheet("font-size:11px;color:white;font-weight:bold;")
            elif index < current:
                label.setText(f"✓  {name}")
                label.setStyleSheet("font-size:11px;color:#3585c8;")
            else:
                label.setText(f"○  {name}")
                label.setStyleSheet("font-size:11px;color:#3a6a8a;")

    def _salvar(self):
        self._dados_empresa = {**self.pages[1].get_data(), **self.pages[2].get_data()}
        self._dados_pdv = self.pages[3].get_data()
        self._dados_admin = self.pages[4].get_data()

        self.btn_avancar.setEnabled(False)
        self.btn_voltar.setEnabled(False)
        self.lbl_status.setText("Salvando...")

        QApplication.processEvents()

        try:
            SetupModel.salvar_tudo(self._dados_empresa, self._dados_pdv, self._dados_admin)
            self._finalizado = True
            self.pages[5].lbl_salvo.setVisible(True)
            self.lbl_status.setText("Configuração concluída!")
            self.btn_avancar.setText("Ir para o Login  →")
            self.btn_avancar.setEnabled(True)
            self.btn_avancar.clicked.disconnect()
            self.btn_avancar.clicked.connect(self.accept)
        except Exception as exc:
            self.lbl_status.setText("Erro ao salvar.")
            self.pages[5].show_error(f"Erro ao salvar: {exc}")
            self.btn_avancar.setEnabled(True)
            self.btn_voltar.setEnabled(True)

    def foi_concluido(self) -> bool:
        return self._finalizado
