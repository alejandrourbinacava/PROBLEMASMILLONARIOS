"""Paso 8: subir el video al canal como privado, listo para revisar."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import Config
from ..providers import youtube
from ..util import log


def run(
    cfg: Config, video: Path, thumbnail: Path | None,
    metadata: dict[str, Any], workdir: Path,
) -> dict[str, Any]:
    service = youtube.client()
    log.info(f"Subiendo {video.name} ({video.stat().st_size / (1024 * 1024):.0f} MB)")

    video_id = youtube.upload_video(
        service, video, metadata,
        privacy=cfg.get("youtube.privacy", "private"),
        category_id=cfg.get("youtube.category_id", "24"),
        made_for_kids=bool(cfg.get("youtube.made_for_kids", False)),
    )
    url = f"https://youtu.be/{video_id}"
    studio = f"https://studio.youtube.com/video/{video_id}/edit"
    log.info(f"Subido: {url}")

    if thumbnail is not None and thumbnail.exists():
        youtube.set_thumbnail(service, video_id, thumbnail)
    youtube.add_to_playlist(service, video_id, cfg.get("youtube.default_playlist", ""))

    result = {"video_id": video_id, "url": url, "studio_url": studio,
              "privacy": cfg.get("youtube.privacy", "private")}
    (workdir / "upload.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info(f"Revisalo y publicalo aqui: {studio}")
    return result
