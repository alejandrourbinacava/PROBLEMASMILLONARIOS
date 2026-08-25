"""Logging con marcas de tiempo y secciones, legible en los logs de GitHub Actions."""
from __future__ import annotations

import sys
import time

_T0 = time.time()
_GROUP_OPEN = False

# La consola de Windows viene en cp1252 y revienta con los emojis y las flechas.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # ya reconfigurada o redirigida
        pass


def _stamp() -> str:
    elapsed = time.time() - _T0
    return f"[{int(elapsed // 60):02d}:{elapsed % 60:04.1f}]"


def info(msg: str) -> None:
    print(f"{_stamp()} {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"{_stamp()} ⚠️  {msg}", flush=True)


def error(msg: str) -> None:
    print(f"{_stamp()} ❌ {msg}", file=sys.stderr, flush=True)


def step(msg: str) -> None:
    """Cabecera de paso. En Actions crea un grupo plegable."""
    global _GROUP_OPEN
    if _GROUP_OPEN:
        print("::endgroup::", flush=True)
    print(f"::group::{_stamp()} ▶ {msg}", flush=True)
    _GROUP_OPEN = True


def endstep() -> None:
    global _GROUP_OPEN
    if _GROUP_OPEN:
        print("::endgroup::", flush=True)
        _GROUP_OPEN = False
