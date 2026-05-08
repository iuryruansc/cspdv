from __future__ import annotations

import traceback
from types import TracebackType
from typing import Optional, Type

from utils.system_runtime import perfil_log

def _deve_emitir_logs() -> bool:
    return perfil_log() != "SILENCIOSO"

def log_info(message: str) -> None:
    if not _deve_emitir_logs():
        return
    print(f"[INFO] {message}")

def log_warning(message: str) -> None:
    if not _deve_emitir_logs():
        return
    print(f"[AVISO] {message}")

def log_error(message: str, exc: Exception | None = None) -> None:
    current_profile = perfil_log()
    if current_profile == "SILENCIOSO":
        return

    print(f"[ERRO] {message}")
    if exc is None:
        return

    if current_profile == "DETALHADO":
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        return

    print(f"[ERRO] {type(exc).__name__}: {exc}")

def log_exception(
    title: str,
    exc_type: Type[BaseException],
    exc_value: BaseException,
    tb: Optional[TracebackType],
) -> None:
    current_profile = perfil_log()
    if current_profile == "SILENCIOSO":
        return

    print("\n" + "=" * 60)
    print(f"[ERRO] {title}")
    if current_profile == "DETALHADO":
        traceback.print_exception(exc_type, exc_value, tb)
    else:
        print(f"{exc_type.__name__}: {exc_value}")
    print("=" * 60 + "\n")
