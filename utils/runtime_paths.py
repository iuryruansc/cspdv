from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

SOURCE_ROOT = Path(__file__).resolve().parents[1]
IS_FROZEN = bool(getattr(sys, "frozen", False))
BUNDLED_ROOT = Path(getattr(sys, "_MEIPASS", SOURCE_ROOT))


def app_root() -> Path:
    custom_root = str(os.getenv("CSPDV_APP_ROOT") or "").strip()
    if custom_root:
        return Path(custom_root).expanduser().resolve()

    if IS_FROZEN:
        return Path(sys.executable).resolve().parent

    return SOURCE_ROOT


def resource_root() -> Path:
    return BUNDLED_ROOT


def writable_path(*parts: str) -> Path:
    return app_root().joinpath(*parts)


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)


def resolve_existing_path(relative_path: str | Path) -> Path | None:
    caminho = Path(relative_path)
    if caminho.is_absolute():
        return caminho if caminho.exists() else None

    externo = writable_path(*caminho.parts)
    if externo.exists():
        return externo

    empacotado = resource_path(*caminho.parts)
    if empacotado.exists():
        return empacotado

    return None


def dotenv_file_path() -> Path | None:
    custom_env = str(os.getenv("CSPDV_ENV_FILE") or "").strip()
    if custom_env:
        caminho = Path(custom_env).expanduser()
        return caminho.resolve() if caminho.exists() else None

    candidatos = [
        writable_path(".env"),
        SOURCE_ROOT / ".env",
    ]

    for candidato in candidatos:
        if candidato.exists():
            return candidato

    return None


def expected_dotenv_path() -> Path:
    return writable_path(".env")


def load_project_dotenv() -> Path | None:
    caminho = dotenv_file_path()
    if caminho is not None:
        load_dotenv(dotenv_path=str(caminho), override=False)
    return caminho
