"""Orquestador del pipeline.

    python -m pipeline.cli                      # video del dia, completo
    python -m pipeline.cli --no-upload          # todo menos publicar
    python -m pipeline.cli --topic "Cuanto cuesta un submarino"
    python -m pipeline.cli --resume             # reaprovecha guion y voz ya generados

Cada paso deja su resultado en JSON dentro de build/<fecha>_<tema>/. Con --resume
esos JSON se releen en vez de repetir el paso, que es lo que evita volver a pagar
la sintesis de voz cuando lo que ha fallado es el montaje.
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import date
from pathlib import Path
from typing import Any

from .config import BUILD_DIR, Config
from .steps import (
    s1_topic, s2_script, s3_voice, s4_broll,
    s5_edit, s6_thumbnail, s7_metadata, s8_upload,
)
from .util import log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pipeline", description="Genera y sube el video diario de Problemas Millonarios"
    )
    parser.add_argument("--topic", help="Forzar un tema concreto en vez de coger el de la cola")
    parser.add_argument("--no-upload", action="store_true", help="No publicar en YouTube")
    parser.add_argument("--no-thumbnail", action="store_true", help="No generar miniatura")
    parser.add_argument("--resume", action="store_true",
                        help="Reutilizar los pasos ya completados de este mismo video")
    parser.add_argument("--workdir", help="Directorio de trabajo concreto (implica --resume)")
    parser.add_argument("--config", help="Ruta a un channel.yml alternativo")
    parser.add_argument("--remix", action="store_true",
                        help="Rehacer solo el audio y el masterizado, sin recodificar "
                             "los planos. Para cambiar música o efectos de sonido; "
                             "los rótulos van quemados y necesitan render completo.")
    args = parser.parse_args(argv)

    cfg = Config(Path(args.config)) if args.config else Config()

    try:
        return _run(cfg, args)
    except KeyboardInterrupt:
        log.endstep()
        log.error("Interrumpido")
        return 130
    except Exception as exc:  # noqa: BLE001 - queremos el traceback en el log de Actions
        log.endstep()
        log.error(f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1


def _run(cfg: Config, args: argparse.Namespace) -> int:
    ledger = s1_topic.load_ledger()

    log.step("Paso 1/8 · Tema")
    topic = s1_topic.run(cfg, forced_title=args.topic)
    log.endstep()

    if args.workdir:
        workdir = Path(args.workdir)
        resume = True
    else:
        workdir = BUILD_DIR / f"{date.today():%Y-%m-%d}_{topic['slug']}"
        resume = args.resume
    workdir.mkdir(parents=True, exist_ok=True)
    log.info(f"Directorio de trabajo: {workdir}")
    _write(workdir / "topic.json", topic)

    log.step("Paso 2/8 · Guion")
    script = _cached(workdir / "script.json", resume, lambda: s2_script.run(cfg, topic, workdir))
    log.endstep()

    log.step("Paso 3/8 · Narracion")
    timeline = _cached(
        workdir / "timeline.json", resume, lambda: s3_voice.run(cfg, script, workdir)
    )
    log.endstep()

    log.step("Paso 4/8 · B-roll")
    broll = _cached(
        workdir / "broll.json", resume,
        lambda: s4_broll.run(
            cfg, script, timeline, workdir,
            topic=topic,
            recent_clip_keys=s1_topic.recent_clip_keys(ledger),
        ),
    )
    log.endstep()

    log.step("Paso 5/8 · Montaje")
    video = workdir / "video.mp4"
    if resume and video.exists() and not args.remix:
        log.info("Video ya montado, se reutiliza (--resume)")
    else:
        # Solo --remix reutiliza el master mudo. Con --resume a secas no, porque
        # los rótulos van quemados en cada plano: cambiar la fuente, el color o
        # el zoom obliga a recodificarlos, y reutilizarlos daría un vídeo con la
        # configuración vieja sin avisar.
        video = s5_edit.run(
            cfg, script, timeline, broll, workdir, reuse_silent=args.remix,
        )
    log.endstep()

    log.step("Paso 6/8 · Metadatos")
    metadata = _cached(
        workdir / "metadata.json", resume,
        lambda: s7_metadata.run(cfg, topic, script, timeline, workdir),
    )
    log.endstep()

    thumbnail: Path | None = None
    if not args.no_thumbnail:
        log.step("Paso 7/8 · Miniatura")
        thumbnail = s6_thumbnail.run(cfg, video, metadata, workdir)
        log.endstep()

    if args.no_upload:
        log.step("Paso 8/8 · Subida (omitida)")
        log.info(f"Listo en local: {video}")
        log.endstep()
        _summary(workdir, metadata, video, None)
        return 0

    log.step("Paso 8/8 · Subida a YouTube")
    upload = s8_upload.run(cfg, video, thumbnail, metadata, workdir)
    log.endstep()

    _record(ledger, topic, metadata, broll, upload)
    _summary(workdir, metadata, video, upload)
    return 0


# ---------------- utilidades ----------------

def _cached(path: Path, resume: bool, produce) -> Any:
    if resume and path.exists():
        log.info(f"Reutilizando {path.name} (--resume)")
        return json.loads(path.read_text(encoding="utf-8"))
    return produce()


def _write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _record(
    ledger: dict, topic: dict, metadata: dict, broll: dict, upload: dict
) -> None:
    """Anota el video publicado y los clips usados para no repetirlos manana."""
    ledger["published"].append({
        "slug": topic["slug"],
        "title": metadata["title"],
        "date": f"{date.today():%Y-%m-%d}",
        "video_id": upload["video_id"],
        "url": upload["url"],
    })
    ledger["used_clips"].append({
        "slug": topic["slug"], "keys": broll.get("clip_keys", []),
    })
    ledger["used_clips"] = ledger["used_clips"][-10:]
    s1_topic.save_ledger(ledger)
    log.info("Registro actualizado (data/ledger.json)")


def _summary(workdir: Path, metadata: dict, video: Path, upload: dict | None) -> None:
    """Resumen final. En GitHub Actions se escribe ademas en la pagina del job."""
    lines = [
        "## 🎬 Problemas Millonarios",
        "",
        f"**{metadata['title']}**",
        "",
        f"- Duracion del archivo: `{video.name}`",
        f"- Capitulos: {len(metadata.get('chapters', []))}",
        f"- Etiquetas: {len(metadata.get('tags', []))} ({metadata.get('tags_chars', 0)}/500 caracteres)",
    ]
    if upload:
        lines += [
            f"- Estado: **{upload['privacy']}**",
            f"- Revisar y publicar: {upload['studio_url']}",
        ]
    else:
        lines.append(f"- Sin subir. Archivo en `{workdir}`")
    lines += ["", "<details><summary>Descripcion</summary>", "",
              "```", metadata["description"], "```", "", "</details>"]

    text = "\n".join(lines)
    print("\n" + text, flush=True)
    import os

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    sys.exit(main())
