"""Busqueda y descarga de b-roll en Pexels y Pixabay, con cache en disco.

Ambos bancos permiten uso comercial sin atribucion. Los clips descargados se
guardan en .cache/clips/ y se reutilizan entre ejecuciones (la cache de GitHub
Actions la persiste), asi que el coste de red baja mucho tras los primeros videos.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import CACHE_DIR, env
from ..util import ffmpeg, log

_TIMEOUT = 45
_MIN_WIDTH = 1280

# Material que NUNCA debe salir en un video de negocios, por muy bien que
# encaje con la busqueda. Un canal automatico publica sin que nadie mire los
# clips uno a uno: sin esta lista, una manifestacion o un accidente pueden
# acabar debajo de una cifra y hundir el video.
DEFAULT_BLOCKLIST = [
    "protest", "protester", "demonstration", "riot", "boycott", "picket",
    "genocide", "refugee", "war", "soldier", "military", "weapon", "gun",
    "rifle", "bomb", "terror", "police arrest", "arrest",
    "funeral", "coffin", "grave", "accident", "crash", "injured", "blood",
    "ambulance", "hospital", "wounded", "corpse", "death",
    # Elementos para montar, no metraje: en los bancos abundan y son basura
    # si se usan tal cual, porque estan hechos para recortar sobre croma.
    "green screen", "greenscreen", "chroma", "chromakey", "alpha channel",
    "subscribe button", "lower third", "overlay", "vfx element", "transition pack",
]


@dataclass
class Clip:
    provider: str
    clip_id: str
    url: str
    width: int
    height: int
    duration: float
    query: str
    # Puesto que ocupaba en la respuesta del banco. Los dos bancos devuelven
    # por relevancia, asi que esta posicion es informacion valiosa.
    rank: int = 0
    # Texto descriptivo del clip: Pexels lo mete en la URL y Pixabay en tags.
    # Es la unica forma de saber QUE se ve en el clip sin descargarlo.
    hint: str = ""
    # 0 = se ve la marca literalmente. 1 = solo contexto del tema.
    tier: int = 1
    path: Path | None = field(default=None)

    @property
    def key(self) -> str:
        return f"{self.provider}:{self.clip_id}"


class StockLibrary:
    """Agrega los bancos disponibles y evita repetir clips dentro de un video."""

    def __init__(
        self, *, recent_keys: set[str] | None = None,
        blocklist: list[str] | None = None,
    ) -> None:
        self.blocklist = [
            term.lower().replace("-", " ")
            for term in (DEFAULT_BLOCKLIST if blocklist is None else blocklist)
        ]
        self.cache_dir = CACHE_DIR / "clips"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.cache_dir / "index.json"
        self._index: dict[str, dict] = _read_json(self._index_path, {})
        self._used: set[str] = set()
        self._recent: set[str] = recent_keys or set()
        self._search_cache: dict[str, list[Clip]] = {}
        # Pixabay corta a las 100 peticiones por minuto y devuelve 429. Un
        # video pide unas 150 busquedas, asi que hay que espaciarlas o se
        # pierde la mitad del banco a mitad de camino.
        self._pixabay_lock = threading.Lock()
        self._pixabay_last = 0.0

        self.pexels_key = env("PEXELS_API_KEY")
        self.pixabay_key = env("PIXABAY_API_KEY")
        if not self.pexels_key and not self.pixabay_key:
            raise RuntimeError(
                "No hay ninguna clave de banco de video. Define PEXELS_API_KEY "
                "y/o PIXABAY_API_KEY (ambas son gratuitas)."
            )

    # ---------------- API publica ----------------

    def acquire(self, query: str, min_duration: float, *, fallback_query: str = "money cash") -> Clip | None:
        """Devuelve un clip descargado y aun no usado en este video."""
        for attempt_query in (query, _broaden(query), fallback_query):
            if not attempt_query:
                continue
            candidates = self._search(attempt_query)
            picked = self._pick(candidates, min_duration, query=attempt_query)
            if picked is None:
                continue
            path = self._download(picked)
            if path is None:
                continue
            self._used.add(picked.key)
            picked.path = path
            return picked
        log.warn(f"Sin clip para '{query}' (ni con reserva '{fallback_query}')")
        return None

    def release_all(self) -> list[str]:
        """Claves usadas en este video, para el registro anti-repeticion."""
        return sorted(self._used)

    def harvest(
        self, queries: list[str], per_query: int = 6,
        keywords: list[str] | None = None,
        primary: list[str] | None = None,
    ) -> list[Clip]:
        """Descarga un fondo de clips del TEMA, no de cada frase suelta.

        Los bancos de stock tienen poquísimo material de marca: buscando
        "mcdonalds" los primeros resultados son McDonald's de verdad y a partir
        del quinto ya son calles genéricas. Y añadir la marca a una consulta
        concreta no sirve de nada: "mcdonalds deep fryer" devuelve exactamente
        lo mismo que "deep fryer".

        Así que se cosecha aparte lo poco que hay, cogiendo solo la cabeza de
        cada búsqueda, y el montaje lo reparte por el vídeo.
        """
        needles = [k.lower().replace("-", " ") for k in (keywords or []) if k.strip()]
        core = [k.lower().replace("-", " ") for k in (primary or []) if k.strip()]
        pool: list[Clip] = []
        rejected = vetoed = 0
        for query in queries:
            candidates = sorted(self._search(query), key=lambda c: (c.rank, -c.width))
            taken = 0
            for clip in candidates:
                if taken >= per_query:
                    break
                if clip.key in self._used or clip.width < _MIN_WIDTH:
                    continue
                if self._blocked(clip):
                    vetoed += 1
                    continue
                # Filtro por lo que SE VE, no por lo que se buscó. Buscando
                # "fast food restaurant" el banco devuelve tambien restaurantes
                # de manteles y autopistas; el texto del clip los delata.
                if needles and not _matches(clip.hint, needles):
                    rejected += 1
                    continue
                path = self._download(clip)
                if path is None:
                    continue
                clip.path = path
                clip.tier = 0 if core and _matches(clip.hint, core) else 1
                # Se reserva para que acquire() no lo vuelva a repartir por su
                # cuenta: del fondo de marca decide el montaje, no la busqueda.
                self._used.add(clip.key)
                pool.append(clip)
                taken += 1
        if vetoed:
            log.warn(f"{vetoed} clips vetados por contenido no publicable")
        exact = sum(1 for clip in pool if clip.tier == 0)
        log.info(
            f"Fondo de marca: {len(pool)} clips de {len(queries)} búsquedas"
            + (f", {rejected} descartados por no verse del tema" if rejected else "")
        )
        if core:
            log.info(
                f"  de esos, {exact} enseñan la marca literalmente; el resto es "
                "contexto del tema"
            )
        return pool

    def local_clips(self, directories: list[Path]) -> list[Clip]:
        """Clips que has dejado tú. Se usan antes que cualquier cosa del stock."""
        found: list[Clip] = []
        for directory in directories:
            if not directory.is_dir():
                continue
            for path in sorted(directory.iterdir()):
                if path.suffix.lower() not in {".mp4", ".mov", ".m4v", ".webm"}:
                    continue
                if path.stat().st_size < 65536:
                    continue
                try:
                    width, height = ffmpeg.video_size(path)
                    duration = ffmpeg.duration(path)
                except ffmpeg.FFmpegError as exc:
                    log.warn(f"{path.name} no es un vídeo legible: {exc}")
                    continue
                found.append(Clip(
                    provider="local", clip_id=path.stem, url=str(path),
                    width=width, height=height, duration=duration,
                    query="propio", rank=0, path=path,
                ))
        if found:
            log.info(f"Clips propios: {len(found)} en assets/broll/")
        return found

    # ---------------- Seleccion ----------------

    def _pick(self, candidates: list[Clip], min_duration: float, query: str = "") -> Clip | None:
        candidates = [c for c in candidates if not self._blocked(c)]
        usable = [c for c in candidates if c.duration >= min_duration and c.width >= _MIN_WIDTH]
        if not usable:
            # Un clip corto sirve: al montarlo se ralentiza o se congela el final
            usable = [c for c in candidates if c.width >= _MIN_WIDTH]
        if not usable:
            return None
        fresh = [c for c in usable if c.key not in self._used and c.key not in self._recent]
        pool = fresh or [c for c in usable if c.key not in self._used] or usable

        # Primero lo que SE VE en el clip contra lo que dice la frase; el puesto
        # que le dio el banco solo desempata. Ordenando solo por puesto entraban
        # clips que casaban una palabra suelta de la consulta y nada mas.
        scored = sorted(
            pool, key=lambda c: (-relevance(query, c.hint), c.rank, -c.width)
        )
        best = relevance(query, scored[0].hint) if query else 0.0
        if query and best > 0:
            # Solo se sortea entre los que empatan arriba, para no bajar de nivel
            top = [c for c in scored if relevance(query, c.hint) >= best - 0.001]
            return random.choice(top[: min(4, len(top))])
        return random.choice(scored[: min(4, len(scored))])

    def _blocked(self, clip: Clip) -> bool:
        return bool(self.blocklist) and _matches_word(clip.hint, self.blocklist)

    # ---------------- Busqueda ----------------

    def _search(self, query: str) -> list[Clip]:
        if query in self._search_cache:
            return self._search_cache[query]
        results: list[Clip] = []
        if self.pexels_key:
            results += self._search_pexels(query)
        if self.pixabay_key:
            results += self._search_pixabay(query)
        self._search_cache[query] = results
        log.info(f"  b-roll '{query}': {len(results)} candidatos")
        return results

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=20))
    def _search_pexels(self, query: str) -> list[Clip]:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": self.pexels_key},
            # 30 en vez de 15: con el filtro por descripcion se descarta mucho,
            # asi que hace falta mas material del que mirar.
            params={"query": query, "orientation": "landscape", "per_page": 30, "size": "medium"},
            timeout=_TIMEOUT,
        )
        if response.status_code == 429:
            log.warn("Pexels: limite de peticiones alcanzado, se sigue con Pixabay")
            return []
        response.raise_for_status()
        clips: list[Clip] = []
        for position, video in enumerate(response.json().get("videos", [])):
            best = _best_pexels_file(video.get("video_files", []))
            if best is None:
                continue
            clips.append(Clip(
                rank=position,
                hint=_slug_of(video.get("url", "")),
                provider="pexels",
                clip_id=str(video.get("id")),
                url=best["link"],
                width=int(best.get("width") or 0),
                height=int(best.get("height") or 0),
                duration=float(video.get("duration") or 0),
                query=query,
            ))
        return clips

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=20))
    def _search_pixabay(self, query: str) -> list[Clip]:
        with self._pixabay_lock:
            wait = 0.65 - (time.monotonic() - self._pixabay_last)
            if wait > 0:
                time.sleep(wait)
            self._pixabay_last = time.monotonic()
        response = requests.get(
            "https://pixabay.com/api/videos/",
            params={"key": self.pixabay_key, "q": query, "video_type": "film", "per_page": 20},
            timeout=_TIMEOUT,
        )
        if response.status_code == 429:
            log.warn("Pixabay: limite de peticiones alcanzado")
            return []
        response.raise_for_status()
        clips: list[Clip] = []
        for position, hit in enumerate(response.json().get("hits", [])):
            variants = hit.get("videos") or {}
            best = None
            for name in ("large", "medium", "small"):
                variant = variants.get(name) or {}
                if variant.get("url") and int(variant.get("width") or 0) >= _MIN_WIDTH:
                    best = variant
                    break
            if best is None:
                continue
            clips.append(Clip(
                rank=position,
                hint=str(hit.get("tags") or "").lower(),
                provider="pixabay",
                clip_id=str(hit.get("id")),
                url=best["url"],
                width=int(best.get("width") or 0),
                height=int(best.get("height") or 0),
                duration=float(hit.get("duration") or 0),
                query=query,
            ))
        return clips

    # ---------------- Descarga ----------------

    def _download(self, clip: Clip) -> Path | None:
        digest = hashlib.sha1(clip.url.encode("utf-8")).hexdigest()[:10]
        target = self.cache_dir / f"{clip.provider}_{clip.clip_id}_{digest}.mp4"
        if target.exists() and target.stat().st_size > 65536:
            # También se comprueba lo ya cacheado: si no, un croma descargado
            # antes de existir esta comprobación seguiría colándose para siempre.
            return None if self._is_greenscreen(target, clip.key) else target
        try:
            with requests.get(clip.url, stream=True, timeout=_TIMEOUT) as response:
                response.raise_for_status()
                tmp = target.with_suffix(".part")
                with open(tmp, "wb") as fh:
                    for chunk in response.iter_content(chunk_size=262144):
                        fh.write(chunk)
                tmp.replace(target)
        except Exception as exc:  # red inestable: se prueba el siguiente candidato
            log.warn(f"Fallo al descargar {clip.key}: {exc}")
            return None
        if target.stat().st_size < 65536:
            target.unlink(missing_ok=True)
            return None
        if self._is_greenscreen(target, clip.key):
            log.warn(f"{clip.key}: es una pantalla de croma, descartado")
            return None
        self._index[clip.key] = {"query": clip.query, "file": target.name}
        _write_json(self._index_path, self._index)
        return target

    def _is_greenscreen(self, path: Path, key: str) -> bool:
        """Mira un fotograma y descarta el clip si es croma verde.

        Por el texto no basta: muchos elementos de croma se anuncian como
        "subscribe animation" sin decir que van sobre verde, y colarlos deja
        tres segundos de pantalla verde en el video.
        """
        cached = self._index.get(key, {}).get("chroma")
        if cached is not None:
            return bool(cached)
        verdict = False
        try:
            frame = path.with_suffix(".probe.png")
            ffmpeg.run([
                "-ss", "0.5", "-i", str(path), "-frames:v", "1",
                "-vf", "scale=64:-1", str(frame),
            ])
            from PIL import Image, ImageStat

            red, green, blue = ImageStat.Stat(Image.open(frame).convert("RGB")).mean
            verdict = green > red * 1.6 and green > blue * 1.6 and green > 90
            frame.unlink(missing_ok=True)
        except Exception as exc:  # noqa: BLE001 - ante la duda, se acepta el clip
            log.warn(f"No se pudo comprobar el croma de {key}: {exc}")
        entry = self._index.setdefault(key, {})
        entry["chroma"] = verdict
        _write_json(self._index_path, self._index)
        return verdict


def _best_pexels_file(files: list[dict[str, Any]]) -> dict | None:
    """Prefiere el mp3/mp4 mas grande que no pase de 1080p (4K infla el render)."""
    usable = [
        f for f in files
        if f.get("file_type") == "video/mp4" and int(f.get("width") or 0) >= _MIN_WIDTH
    ]
    if not usable:
        return None
    within = [f for f in usable if int(f.get("width") or 0) <= 1920]
    pool = within or usable
    return max(pool, key=lambda f: int(f.get("width") or 0))


# Palabras de las consultas que no dicen nada sobre lo que se ve
_FILLER = {
    "a", "an", "the", "of", "in", "on", "at", "and", "with", "up", "close",
    "shot", "view", "video", "footage", "scene", "background",
}


def relevance(query: str, hint: str) -> float:
    """Qué parte de lo que pide la frase aparece de verdad en el clip.

    Los bancos ordenan por su propia relevancia, que con consultas de varias
    palabras es floja: buscando "worker mopping restaurant floor" Pixabay
    devolvía una fábrica textil porque casaba "worker". Comparando las palabras
    de la consulta contra la descripción del clip eso se cae solo.
    """
    words = {
        word for word in re.findall(r"[a-z]+", query.lower())
        if len(word) > 2 and word not in _FILLER
    }
    if not words:
        return 0.0
    text = " " + hint.replace("-", " ").replace(",", " ").lower() + " "
    hits = sum(1 for word in words if re.search(r"(?<![a-z])" + word[:6], text))
    return hits / len(words)


def _matches(hint: str, needles: list[str]) -> bool:
    """Coincidencia por subcadena: es lo que se quiere para las palabras clave,
    donde "mcdonald" tiene que casar con "mcdonalds"."""
    text = hint.replace("-", " ").replace(",", " ")
    return any(needle in text for needle in needles)


def _matches_word(hint: str, needles: list[str]) -> bool:
    """Coincidencia por palabra entera, para el veto.

    Por subcadena, "war" casaba dentro de "warning" y tiraba clips inofensivos
    de carteles de aviso. En un veto un falso positivo cuesta material bueno.
    """
    text = " " + hint.replace("-", " ").replace(",", " ") + " "
    # Se admiten los plurales y derivados habituales: "protest" tiene que cazar
    # "protesters", pero "war" no puede cazar "warning".
    return any(
        re.search(
            r"(?<![a-z])" + re.escape(needle) + r"(?:s|es|er|ers|ing|ed)?(?![a-z])",
            text,
        )
        for needle in needles
    )


def _slug_of(url: str) -> str:
    """De https://www.pexels.com/video/burger-being-made-12345/ saca las palabras."""
    tail = url.rstrip("/").split("/")[-1]
    words = [w for w in tail.split("-") if not w.isdigit()]
    return " ".join(words).lower()


def _broaden(query: str) -> str:
    """Recorta la consulta a sus dos primeras palabras para ampliar resultados."""
    words = query.split()
    return " ".join(words[:2]) if len(words) > 2 else ""


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
