"""Lista las voces de GenAIPro y genera muestras para que elijas.

    python scripts/list_voices.py                  # lista voces en espanol
    python scripts/list_voices.py --all            # todas
    python scripts/list_voices.py --demo 4         # sintetiza 4 muestras

Copia el voice_id que te guste a config/channel.yml -> voice.voice_id
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import BUILD_DIR, Config  # noqa: E402
from pipeline.providers.genaipro import GenAIPro  # noqa: E402
from pipeline.util import log  # noqa: E402

DEMO_TEXT = (
    "Comprar un equipo de futbol cuesta cuarenta y siete millones de euros. "
    "Pero mantenerlo un solo ano cuesta el triple. Y nadie te cuenta por que."
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="No filtrar por idioma")
    parser.add_argument("--demo", type=int, default=0,
                        help="Numero de muestras de audio a generar")
    parser.add_argument("--filter", default="", help="Filtrar por texto en el nombre")
    args = parser.parse_args()

    cfg = Config()
    client = GenAIPro(cfg)
    voices = client.list_voices(None if args.all else "es")
    if not voices:
        log.warn("Sin filtro de idioma no llego nada; se piden todas.")
        voices = client.list_voices()

    if not voices:
        log.error("La API no devolvio voces. Revisa GENAIPRO_API_KEY.")
        return 1

    rows = []
    for voice in voices:
        name = str(_first(voice, "name", "voice_name", "title") or "?")
        if args.filter and args.filter.lower() not in name.lower():
            continue
        rows.append({
            "id": str(_first(voice, "voice_id", "id", "uuid") or "?"),
            "name": name,
            "language": str(_first(voice, "language", "lang", "locale") or "-"),
            "gender": str(_first(voice, "gender", "sex") or "-"),
        })

    print(f"\n{len(rows)} voces disponibles\n")
    print(f"{'VOICE_ID':<40} {'NOMBRE':<26} {'IDIOMA':<10} GENERO")
    print("-" * 90)
    for row in rows:
        print(f"{row['id']:<40} {row['name'][:25]:<26} {row['language'][:9]:<10} {row['gender']}")

    if args.demo > 0:
        out_dir = BUILD_DIR / "_voice_demos"
        out_dir.mkdir(parents=True, exist_ok=True)
        print()
        for row in rows[: args.demo]:
            target = out_dir / f"{_safe(row['name'])}_{row['id'][:8]}.mp3"
            log.info(f"Generando muestra de {row['name']}...")
            try:
                task_id = _demo_task(client, row["id"])
                client.download(client.wait_for_task(task_id), target)
                log.info(f"  -> {target}")
            except Exception as exc:  # noqa: BLE001
                log.warn(f"  fallo con {row['name']}: {exc}")
        print(f"\nEscuchalas en {out_dir} y copia el voice_id elegido a config/channel.yml")

    print("\nPega el que elijas en config/channel.yml -> voice.voice_id\n")
    return 0


def _demo_task(client: GenAIPro, voice_id: str) -> str:
    original = client.cfg.data["voice"]["voice_id"]
    client.cfg.data["voice"]["voice_id"] = voice_id
    try:
        return client.create_task(DEMO_TEXT)
    finally:
        client.cfg.data["voice"]["voice_id"] = original


def _first(payload: dict, *keys: str):
    for key in keys:
        if payload.get(key):
            return payload[key]
    return None


def _safe(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name)[:24]


if __name__ == "__main__":
    raise SystemExit(main())
