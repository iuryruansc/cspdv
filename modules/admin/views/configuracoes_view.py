from PyQt5.QtWidgets import QWidget

from ui.admin.configuracoes import Ui_ConfiguracoesWidget
from utils.ui_messages import mostrar_info


class ConfiguracoesView(QWidget, Ui_ConfiguracoesWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._configurar_defaults()
        self._conectar_eventos()

    def _configurar_defaults(self) -> None:
        self.lineEditRazaoSocial.setText("Empresa em configuração")
        self.lineEditFundoSugerido.setText("0,00")
        self.lineEditHorasSessao.setText("12")
        self.lineEditIntervaloBackup.setText("24")
        self.checkVendaRapidaAdmin.setChecked(True)
        self.checkBloquearPromocoesSimultaneas.setChecked(True)
        self.checkAtivarPorVigencia.setChecked(True)
        self.checkRestaurarLogin.setChecked(True)
        self.checkBloquearFecharAppCaixa.setChecked(True)
        self.checkExigirAdminSangria.setChecked(True)
        self.checkExigirAdminReembolso.setChecked(True)
        self.checkExigirAdminDiferenca.setChecked(True)

    def _conectar_eventos(self) -> None:
        self.btnSalvarParametros.clicked.connect(self._salvar_estrutura_inicial)
        self.btnRestaurarPadroes.clicked.connect(self._restaurar_defaults)

    def _salvar_estrutura_inicial(self) -> None:
        mostrar_info(
            self,
            "Configurações",
            "A estrutura inicial da área de configurações já está pronta. O próximo passo é ligar persistência real por grupo de parâmetros.",
        )

    def _restaurar_defaults(self) -> None:
        self._configurar_defaults()
        mostrar_info(
            self,
            "Configurações",
            "Os valores visuais padrão desta estrutura inicial foram restaurados.",
        )
