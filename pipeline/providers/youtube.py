"""Subida a YouTube mediante la Data API v3.

Nota importante sobre "borradores": la API de YouTube NO permite crear borradores
de Studio. Lo mas cercano es subir el video como PRIVADO con todo relleno
(titulo, descripcion, capitulos, etiquetas y miniatura). Aparece en tu Studio
listo para revisar y solo tienes que cambiar la visibilidad a publico.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from ..config import env
from ..util import log

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


class YouTubeError(RuntimeError):
    pass


def client():
    credentials = Credentials(
        token=None,
        refresh_token=env("YT_REFRESH_TOKEN", required=True),
        client_id=env("YT_CLIENT_ID", required=True),
        client_secret=env("YT_CLIENT_SECRET", required=True),
        token_uri=TOKEN_URI,
        scopes=SCOPES,
    )
    credentials.refresh(Request())
    return build("youtube", "v3", credentials=credentials, cache_discovery=False)


def upload_video(
    service, video_path: Path, metadata: dict[str, Any], *,
    privacy: str = "private", category_id: str = "24", made_for_kids: bool = False,
) -> str:
    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": str(category_id),
            "defaultLanguage": "es",
            "defaultAudioLanguage": "es",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": bool(made_for_kids),
            "embeddable": True,
        },
    }
    media = MediaFileUpload(str(video_path), chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    last_logged = -10
    while response is None:
        try:
            status, response = request.next_chunk()
        except HttpError as exc:
            if exc.resp.status in (500, 502, 503, 504):
                log.warn(f"Error temporal de YouTube ({exc.resp.status}), reintentando")
                continue
            raise YouTubeError(f"Fallo al subir: {exc}") from exc
        if status:
            percent = int(status.progress() * 100)
            if percent >= last_logged + 10:
                log.info(f"  subiendo... {percent}%")
                last_logged = percent

    video_id = response.get("id")
    if not video_id:
        raise YouTubeError(f"La subida no devolvio id: {response}")
    return video_id


def set_thumbnail(service, video_id: str, thumbnail: Path) -> None:
    try:
        service.thumbnails().set(
            videoId=video_id, media_body=MediaFileUpload(str(thumbnail), mimetype="image/jpeg")
        ).execute()
        log.info("Miniatura subida")
    except HttpError as exc:
        # Requiere canal verificado por telefono; no es motivo para tumbar el proceso
        log.warn(
            f"No se pudo poner la miniatura ({exc.resp.status}). "
            "Verifica el canal por telefono en youtube.com/verify y subela a mano."
        )


def add_to_playlist(service, video_id: str, playlist_id: str) -> None:
    if not playlist_id:
        return
    try:
        service.playlistItems().insert(
            part="snippet",
            body={"snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }},
        ).execute()
        log.info(f"Anadido a la playlist {playlist_id}")
    except HttpError as exc:
        log.warn(f"No se pudo anadir a la playlist: {exc}")
