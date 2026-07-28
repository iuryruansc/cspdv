from __future__ import annotations

import os
import traceback
from datetime import datetime
from types import TracebackType
from typing import Optional, Type

from utils.runtime_paths import writable_path
from utils.system_runtime import perfil_log


def _log_dir() -> str:
    return str(writable_path("logs"))


def _log_file() -> str:
    return os.path.join(_log_dir(), "cspdv.log")


def _ensure_log_dir() -> None:
    os.makedirs(_log_dir(), exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def _escrever_arquivo(linha: str) -> None:
    try:
        _ensure_log_dir()
        with open(_log_file(), "a", encoding="utf-8") as f:
            f.write(linha + "\n")
    except Exception:
        pass


def _deve_emitir_logs() -> bool:
    return perfil_log() != "SILENCIOSO"


def _emitir(prefixo: str, mensagem: str) -> None:
    linha = f"[{_timestamp()}] [{prefixo}] {mensagem}"
    print(linha)
    _escrever_arquivo(linha)


def log_info(message: str) -> None:
    if not _deve_emitir_logs():
        return
    _emitir("INFO", message)


def log_warning(message: str) -> None:
    if not _deve_emitir_logs():
        return
    _emitir("AVISO", message)


def log_error(message: str, exc: Exception | None = None) -> None:
    current_profile = perfil_log()
    if current_profile == "SILENCIOSO":
        return

    _emitir("ERRO", message)
    if exc is None:
        return

    if current_profile == "DETALHADO":
        tb_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        _escrever_arquivo(tb_text)
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        return

    _emitir("ERRO", f"{type(exc).__name__}: {exc}")


def log_exception(
    title: str,
    exc_type: Type[BaseException],
    exc_value: BaseException,
    tb: Optional[TracebackType],
) -> None:
    current_profile = perfil_log()
    if current_profile == "SILENCIOSO":
        return

    _emitir("ERRO", title)

    if current_profile == "DETALHADO":
        tb_text = "".join(traceback.format_exception(exc_type, exc_value, tb))
        _escrever_arquivo(tb_text)
        traceback.print_exception(exc_type, exc_value, tb)
    else:
        msg = f"{exc_type.__name__}: {exc_value}"
        _emitir("ERRO", msg)
