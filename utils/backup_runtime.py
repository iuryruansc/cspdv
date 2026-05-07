from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Sequence, cast

from PyQt5.QtCore import QObject, QTimer

from database.connection import get_connection
from utils.app_logger import log_error, log_info, log_warning
from utils.system_runtime import intervalo_backup_horas


UTC = timezone.utc
APP_ROOT = Path(__file__).resolve().parents[1]
BACKUP_ROOT = Path(os.getenv("CSPDV_BACKUP_DIR", APP_ROOT / "backups" / "database"))
STATE_FILE = BACKUP_ROOT / "backup_state.json"


@dataclass
class BackupResultado:
    sucesso: bool
    arquivo: str | None = None
    mensagem: str = ""


def _agora_utc() -> datetime:
    return datetime.now(UTC)


def _carregar_estado() -> dict[str, Any]:
    try:
        if not STATE_FILE.exists():
            return {}
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        log_warning(f"Não foi possível ler o estado do backup: {exc}")
        return {}


def _salvar_estado(payload: dict[str, Any]) -> None:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _ultima_execucao() -> datetime | None:
    estado = _carregar_estado()
    bruto = str(estado.get("ultimo_backup_utc") or "").strip()
    if not bruto:
        return None
    try:
        return datetime.fromisoformat(bruto)
    except ValueError:
        return None


def _registrar_resultado(resultado: BackupResultado) -> None:
    agora = _agora_utc().isoformat()
    estado = _carregar_estado()
    estado.update(
        {
            "ultimo_backup_utc": agora,
            "ultimo_status": "SUCESSO" if resultado.sucesso else "ERRO",
            "ultimo_arquivo": resultado.arquivo,
            "ultima_mensagem": resultado.mensagem,
        }
    )
    _salvar_estado(estado)


def _escape_texto(valor: str) -> str:
    texto = valor
    texto = texto.replace("\\", "\\\\")
    texto = texto.replace("'", "\\'")
    texto = texto.replace("\0", "\\0")
    texto = texto.replace("\n", "\\n")
    texto = texto.replace("\r", "\\r")
    texto = texto.replace("\t", "\\t")
    texto = texto.replace("\x1a", "\\Z")
    return f"'{texto}'"


def _formatar_valor_sql(valor: Any) -> str:
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, Decimal):
        return str(valor)
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, datetime):
        return _escape_texto(valor.strftime("%Y-%m-%d %H:%M:%S"))
    if isinstance(valor, date):
        return _escape_texto(valor.strftime("%Y-%m-%d"))
    if isinstance(valor, time):
        return _escape_texto(valor.strftime("%H:%M:%S"))
    if isinstance(valor, bytes):
        return f"X'{valor.hex().upper()}'"
    return _escape_texto(str(valor))


def _formatar_insert_em_lotes(
    tabela: str,
    colunas: Sequence[str],
    linhas: Iterable[Sequence[Any]],
) -> list[str]:
    prefixo = (
        f"INSERT INTO `{tabela}` ("
        + ", ".join(f"`{coluna}`" for coluna in colunas)
        + ") VALUES\n"
    )
    blocos: list[str] = []
    acumulado: list[str] = []

    for linha in linhas:
        valores = ", ".join(_formatar_valor_sql(valor) for valor in linha)
        acumulado.append(f"({valores})")
        if len(acumulado) >= 250:
            blocos.append(prefixo + ",\n".join(acumulado) + ";\n")
            acumulado = []

    if acumulado:
        blocos.append(prefixo + ",\n".join(acumulado) + ";\n")

    return blocos


class BackupService:
    @staticmethod
    def diretorio_backup() -> Path:
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        return BACKUP_ROOT

    @staticmethod
    def executar_backup() -> BackupResultado:
        conn = get_connection()
        cursor = conn.cursor()
        arquivo_path: Path | None = None

        try:
            conn.start_transaction()
            cursor.execute("SHOW TABLES")
            rows_tabelas = cast(list[Sequence[Any]], cursor.fetchall())
            tabelas = [str(row[0]) for row in rows_tabelas]
            if not tabelas:
                resultado = BackupResultado(False, mensagem="Nenhuma tabela encontrada para backup.")
                _registrar_resultado(resultado)
                return resultado

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo_path = BackupService.diretorio_backup() / f"cspdv_backup_{timestamp}.sql"

            linhas_saida: list[str] = [
                "-- CSPdv backup\n",
                f"-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                "SET NAMES utf8mb4;\n",
                "SET FOREIGN_KEY_CHECKS = 0;\n\n",
            ]

            for tabela in tabelas:
                cursor.execute(f"SHOW CREATE TABLE `{tabela}`")
                create_row = cast(Sequence[Any] | None, cursor.fetchone())
                create_sql = str(create_row[1]) if create_row and len(create_row) > 1 else ""

                linhas_saida.append(f"-- Estrutura da tabela `{tabela}`\n")
                linhas_saida.append(f"DROP TABLE IF EXISTS `{tabela}`;\n")
                linhas_saida.append(create_sql + ";\n\n")

                cursor.execute(f"SELECT * FROM `{tabela}`")
                rows = cast(list[Sequence[Any]], cursor.fetchall())
                if not rows:
                    continue

                colunas = [descricao[0] for descricao in cursor.description or []]
                linhas_saida.append(f"-- Dados da tabela `{tabela}`\n")
                linhas_saida.extend(_formatar_insert_em_lotes(tabela, colunas, rows))
                linhas_saida.append("\n")

            linhas_saida.append("SET FOREIGN_KEY_CHECKS = 1;\n")
            arquivo_path.write_text("".join(linhas_saida), encoding="utf-8")

            conn.rollback()
            resultado = BackupResultado(
                True,
                arquivo=str(arquivo_path),
                mensagem=f"Backup gerado com sucesso em {arquivo_path.name}.",
            )
            _registrar_resultado(resultado)
            BackupService._aplicar_retencao()
            log_info(resultado.mensagem)
            return resultado
        except Exception as exc:
            conn.rollback()
            if arquivo_path is not None and arquivo_path.exists():
                try:
                    arquivo_path.unlink()
                except OSError:
                    pass
            resultado = BackupResultado(False, mensagem=f"Falha ao gerar backup: {exc}")
            _registrar_resultado(resultado)
            log_error("Falha ao gerar backup do banco de dados.", exc)
            return resultado
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _aplicar_retencao(max_arquivos: int = 30) -> None:
        arquivos = sorted(
            BackupService.diretorio_backup().glob("cspdv_backup_*.sql"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for arquivo in arquivos[max_arquivos:]:
            try:
                arquivo.unlink()
            except OSError as exc:
                log_warning(f"Não foi possível remover backup antigo {arquivo.name}: {exc}")

    @staticmethod
    def backup_esta_vencido() -> bool:
        ultima_execucao = _ultima_execucao()
        if ultima_execucao is None:
            return True
        proxima_execucao = ultima_execucao + timedelta(hours=intervalo_backup_horas())
        return _agora_utc() >= proxima_execucao


class BackupScheduler(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(10 * 60 * 1000)
        self._timer.timeout.connect(self._agendar_se_necessario)
        self._lock = threading.Lock()
        self._thread_ativa: threading.Thread | None = None

    def iniciar(self) -> None:
        self._timer.start()
        QTimer.singleShot(15_000, self._agendar_se_necessario)

    def _agendar_se_necessario(self) -> None:
        if not BackupService.backup_esta_vencido():
            return

        with self._lock:
            if self._thread_ativa is not None and self._thread_ativa.is_alive():
                return

            self._thread_ativa = threading.Thread(
                target=self._executar_em_background,
                name="cspdv-backup",
                daemon=True,
            )
            self._thread_ativa.start()

    def _executar_em_background(self) -> None:
        BackupService.executar_backup()
