"""Mantiene la cache de clips por debajo de un tamano.

La cache de GitHub Actions admite 10 GB por repositorio. Sin podar, la carpeta
de clips crece sin freno y acaba echando fuera al resto de caches.

    python scripts/prune_cache.py --max-gb 4

Borra primero los clips que hace mas tiempo que no se usan.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import CACHE_DIR  # noqa: E402
from pipeline.util import log  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-gb", type=float, default=4.0)
    args = parser.parse_args()

    clips_dir = CACHE_DIR / "clips"
    if not clips_dir.exists():
        log.info("No hay cache de clips todavia")
        return 0

    files = [path for path in clips_dir.glob("*.mp4") if path.is_file()]
    total = sum(path.stat().st_size for path in files)
    limit = int(args.max_gb * 1024**3)
    log.info(f"Cache: {len(files)} clips, {total / 1024**3:.2f} GB (limite {args.max_gb} GB)")

    if total <= limit:
        return 0

    # Los menos usados recientemente salen primero
    files.sort(key=lambda path: path.stat().st_atime)
    freed = 0
    removed = 0
    for path in files:
        if total - freed <= limit:
            break
        size = path.stat().st_size
        path.unlink(missing_ok=True)
        freed += size
        removed += 1

    log.info(f"Podados {removed} clips, {freed / 1024**3:.2f} GB liberados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
