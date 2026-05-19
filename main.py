import sys

from PyQt5.QtCore import QEvent, QObject, QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from database.bootstrap import bootstrap_database
from database.connection import close_connection, get_connection_diagnostics
from database.migrations.runner import run_pending_migrations
from database.seeds.runner import run_pending_seeds
from modules.auth.models.usuario_model import UsuarioModel
from modules.auth.views.login_view import LoginView
from modules.auth.views.selecao_modo_view import SelecaoModoView
from modules.setup.models.setup_model import SetupModel
from modules.setup.views.setup_wizard_view import SetupWizardView
from utils.app_logger import log_exception, log_info
from utils.backup_runtime import BackupScheduler
from utils.runtime_paths import expected_dotenv_path, load_project_dotenv
from utils.system_runtime import carregar_parametros_sistema, descricao_ambiente
from utils.ui_messages import mostrar_aviso

load_project_dotenv()

def _excepthook(tipo, valor, tb):
    log_exception("Erro não tratado", tipo, valor, tb)

sys.excepthook = _excepthook

def _mostrar_dialog(dialog):
    frame = dialog.frameGeometry()
    screen = QApplication.primaryScreen()

    if screen is not None:
        frame.moveCenter(screen.availableGeometry().center())
        dialog.move(frame.topLeft())

    if dialog.__class__.__name__ in {
        "SelecaoModoView",
        "PainelAdminView",
        "PainelEstoqueView",
        "PainelFinanceiroView",
        "PainelPromocoesView",
        "FrenteLojaView",
    }:
        dialog.showMaximized()
    else:
        dialog.show()
    dialog.raise_()
    dialog.activateWindow()

def _mostrar_erro_conexao(mensagem):
    diagnostics = get_connection_diagnostics()
    env_path = expected_dotenv_path()
    detalhes = [
        f"Modo: {diagnostics['mode']}",
        f"Host: {diagnostics['host']}:{diagnostics['port']}",
        f"Banco: {diagnostics['database']}",
        f"Pool habilitado: {'sim' if diagnostics['pool_enabled'] else 'não'}",
        f"Pool inicializado: {'sim' if diagnostics['pool_initialized'] else 'não'}",
        f"Timeout: {diagnostics['connection_timeout']}s",
    ]

    if diagnostics["pool_enabled"]:
        detalhes.append(f"Pool name: {diagnostics.get('pool_name', '-')}")
        detalhes.append(f"Pool size: {diagnostics.get('pool_size', '-')}")

    orientacao = ""
    if not str(diagnostics["database"] or "").strip():
        orientacao = (
            "Verifique o arquivo de configuração `.env` ao lado do executável.\n"
            f"Caminho esperado: {env_path}\n\n"
            "Se necessário, copie `.env.example` para `.env` e preencha os dados do MySQL.\n\n"
        )
    elif "localization support" in mensagem.lower():
        orientacao = (
            "O driver MySQL do ambiente nao conseguiu carregar os recursos de idioma da instalacao.\n"
            "Gere novamente o executavel para incluir os modulos auxiliares do conector, ou revise o empacotamento.\n\n"
        )
    elif "access denied" in mensagem.lower():
        orientacao = (
            "Verifique usuario e senha do MySQL no arquivo `.env`.\n"
            f"Caminho esperado: {env_path}\n\n"
        )
    elif "can't connect" in mensagem.lower() or "nao foi possivel conectar" in mensagem.lower():
        orientacao = (
            "Confirme se o servidor MySQL esta ligado, acessivel na rede e liberado na porta configurada.\n\n"
        )

    QMessageBox.critical(
        None,
        "Falha na conexão com o banco",
        (
            "Não foi possível iniciar o sistema porque a conexão com o banco falhou.\n\n"
            + orientacao
            + f"{mensagem}\n\n"
            + "\n".join(detalhes)
        ),
    )

class _AppCloseGuard(QObject):
    _WINDOW_CLASSES = {
        "SelecaoModoView",
        "PainelAdminView",
        "PainelEstoqueView",
        "PainelFinanceiroView",
        "PainelPromocoesView",
        "PainelRelatoriosView",
        "FrenteLojaView",
    }

    def eventFilter(self, a0, a1):
        if (
            a1.type() == QEvent.Close
            and a0 is not None
            and a0.__class__.__name__ in self._WINDOW_CLASSES
            and SessionManager.should_block_close_with_open_caixa()
            and CaixaSession.has_open_caixa()
        ):
            a1.ignore()
            if isinstance(a0, QWidget):
                mostrar_aviso(
                    a0,
                    "Caixa aberto",
                    "Não é possível fechar o programa enquanto houver um caixa aberto.\n\n"
                    "Feche o caixa primeiro para encerrar a operação com segurança.",
                )
            return True

        return super().eventFilter(a0, a1)

def main():
    app = QApplication(sys.argv)
    parametros_sistema = carregar_parametros_sistema()
    app.setApplicationVersion(str(parametros_sistema["versao_referencia"]))
    app.setProperty("cspdv_backup_intervalo_horas", int(parametros_sistema["intervalo_backup_horas"]))
    app.setProperty("cspdv_perfil_log", str(parametros_sistema["perfil_log"]))
    log_info(f"Sistema iniciado: {descricao_ambiente()}")

    close_guard = _AppCloseGuard(app)
    app.installEventFilter(close_guard)

    backup_scheduler = BackupScheduler(app)
    app.setProperty("cspdv_backup_scheduler", backup_scheduler)
    backup_scheduler.iniciar()

    try:
        database_created = bootstrap_database()
        if database_created:
            log_info("Banco de dados criado automaticamente na inicializacao.")
        applied_migrations = run_pending_migrations()
        if applied_migrations:
            log_info(f"Migrations aplicadas na inicializacao: {', '.join(applied_migrations)}")
        applied_seeds = run_pending_seeds()
        if applied_seeds:
            log_info(f"Seeds aplicados na inicializacao: {', '.join(applied_seeds)}")
        if SetupModel.is_first_run():
            wizard = SetupWizardView()
            QTimer.singleShot(0, lambda: _mostrar_dialog(wizard))
            if wizard.exec_() != SetupWizardView.Accepted or not wizard.foi_concluido():
                return 0
    except ConnectionError as exc:
        _mostrar_erro_conexao(str(exc))
        return 1
    except Exception as exc:
        log_exception("Falha ao iniciar servicos de banco", type(exc), exc, exc.__traceback__)
        _mostrar_erro_conexao(str(exc))
        return 1

    autenticado = SessionManager.restore_persisted_session(UsuarioModel.buscar_sessao_por_id)
    if not autenticado:
        login = LoginView()
        QTimer.singleShot(0, lambda: _mostrar_dialog(login))
        if login.exec_() != LoginView.Accepted:
            return 0

    selecao = SelecaoModoView()
    _mostrar_dialog(selecao)
    return app.exec_()

if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        close_connection()
