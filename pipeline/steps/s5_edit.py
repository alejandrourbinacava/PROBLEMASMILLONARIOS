"""Paso 5: montaje.

El montaje se hace en cuatro fases para que un video de 13 minutos quepa en el
tiempo de un runner de GitHub Actions:

  1. Cada plano se normaliza por separado a 1920x1080/30fps con su zoom, su
     grado de color y su rotulo. Se paraleliza por nucleos.
  2. Los planos se pegan con el demuxer concat SIN recodificar. Por eso todos
     los cortes son secos: un fundido encadenado obligaria a recodificar los
     13 minutos enteros. Las transiciones las marca el sonido, que es lo que
     realmente percibe el espectador.
  3. La mezcla de audio (voz + musica con ducking + golpes) va aparte.
  4. Una unica pasada final quema subtitulos, pega el audio y cierra el archivo.
"""
from __future__ import annotations

import os
import random
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ..config import ASSETS_DIR, Config
from ..util import captions as captions_util
from ..util import ffmpeg, fonts, log, sfx
from ..util.sfxbed import SfxEvent, build_bed
from ..util.timing import Cue, caption_cues


def run(
    cfg: Config,
    script: dict[str, Any],
    timeline: dict[str, Any],
    broll: dict[str, Any],
    workdir: Path,
) -> Path:
    slots = broll["slots"]
    total = float(timeline["duration"])
    font_file, font_family = fonts.resolve_from_config(cfg)
    font_file = _localize_font(font_file, workdir)

    log.step("Montaje 1/4: normalizando planos")
    segments = _render_segments(cfg, slots, workdir, font_file)
    log.endstep()

    log.step("Montaje 2/4: pegando planos")
    silent = workdir / "silent.ts"
    ffmpeg.concat_copy(segments, silent, workdir / "segments")
    log.info(f"Video mudo: {ffmpeg.duration(silent):.1f}s (narracion: {total:.1f}s)")
    log.endstep()

    log.step("Montaje 3/4: mezcla de audio")
    mixed = _mix_audio(cfg, broll, timeline, workdir)
    log.endstep()

    log.step("Montaje 4/4: subtitulos y masterizado")
    ass_path = _write_captions(cfg, timeline, workdir, font_family)
    output = _master(cfg, silent, mixed, ass_path, workdir, font_file)
    log.endstep()
    return output


# ==========================================================================
# 1. Normalizacion de planos
# ==========================================================================

def _render_segments(
    cfg: Config, slots: list[dict], workdir: Path, font_file: Path | None
) -> list[Path]:
    segdir = workdir / "segments"
    if segdir.exists():
        shutil.rmtree(segdir)
    segdir.mkdir(parents=True)

    workers = max(1, min(8, (os.cpu_count() or 2)))
    fps = int(cfg.get("edit.fps", 30))
    frame_counts = _frame_plan(slots, fps)
    log.info(f"{len(slots)} planos con {workers} procesos de ffmpeg en paralelo")

    jobs = [
        (index, slot, frame_counts[index])
        for index, slot in enumerate(slots) if slot.get("clip")
    ]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        paths = list(pool.map(
            lambda job: _render_one(cfg, job[0], job[1], job[2], segdir, font_file), jobs
        ))
    done = [path for path in paths if path is not None and path.exists()]
    if len(done) != len(jobs):
        raise RuntimeError(
            f"Solo se generaron {len(done)} de {len(jobs)} planos. Cortar aqui "
            "desincronizaria la voz del resto del video."
        )
    return done


def _frame_plan(slots: list[dict], fps: int) -> list[int]:
    """Reparte los planos en fotogramas ENTEROS y acumulativos.

    Si cada plano se cortara por separado con -t, ffmpeg redondearia cada uno al
    fotograma siguiente. Son unos 15 ms por plano que no se ven... hasta que
    sumas 200 planos y la imagen va cuatro segundos por detras de la voz al
    final del video. Calculando las fronteras sobre la linea temporal absoluta,
    los errores no se acumulan: como mucho hay medio fotograma de diferencia.
    """
    counts: list[int] = []
    for slot in slots:
        start_frame = int(round(float(slot["start"]) * fps))
        end_frame = int(round(float(slot["end"]) * fps))
        counts.append(max(1, end_frame - start_frame))
    return counts


def _render_one(
    cfg: Config, index: int, slot: dict, frames: int, segdir: Path, font_file: Path | None
) -> Path:
    fps = int(cfg.get("edit.fps", 30))
    duration = frames / fps
    clip = Path(slot["clip"])
    clip_duration = float(slot.get("clip_duration") or 0.0)
    out_path = segdir / f"seg_{index:04d}.ts"

    args: list[str] = []
    # Si el clip es mas corto que el plano, se repite en bucle en lugar de congelarlo
    if clip_duration and clip_duration < duration + 0.15:
        args += ["-stream_loop", "-1"]
    else:
        start_at = _pick_in_point(index, clip_duration, duration)
        if start_at > 0:
            args += ["-ss", f"{start_at:.3f}"]
    args += ["-i", str(clip)]

    # Tres intentos de menos a mas conservador. Un plano que falla NO puede
    # acortar el video: eso desplazaria todo lo que viene detras y la voz
    # dejaria de cuadrar con la imagen durante el resto del video.
    attempts = (
        ("completo", _filter_chain(cfg, slot, frames, fps, index, font_file, segdir)),
        ("simple", _simple_chain(cfg, fps)),
    )
    for level, chain in attempts:
        try:
            # cwd=segdir para que las rutas dentro del grafo de filtros sean relativas
            ffmpeg.run(
                args + ["-an", "-sn", "-vf", chain]
                + _encode_args(cfg, fps, frames, out_path),
                cwd=segdir,
            )
            return out_path
        except ffmpeg.FFmpegError as exc:
            log.warn(
                f"Plano {index} ('{slot.get('query', '')}') fallo en modo "
                f"{level}: {str(exc)[:160]}"
            )
    return _filler(cfg, index, frames, fps, segdir, out_path)


def _encode_args(cfg: Config, fps: int, frames: int, out_path: Path) -> list[str]:
    """Parametros de codificacion identicos en todos los planos: es lo que
    permite pegarlos despues sin recodificar. -frames:v fija la duracion en
    fotogramas exactos, que es lo que impide que la sincronia derive."""
    return [
        "-frames:v", str(frames),
        "-r", str(fps), "-fps_mode", "cfr",
        "-c:v", "libx264", "-preset", cfg.get("edit.preset", "veryfast"),
        "-crf", str(cfg.get("edit.segment_crf", 20)),
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
        "-x264-params", f"keyint={fps * 2}:min-keyint={fps * 2}:scenecut=0",
        "-threads", "1", "-f", "mpegts", out_path.name,
    ]


def _simple_chain(cfg: Config, fps: int) -> str:
    width = int(cfg.get("edit.width", 1920))
    height = int(cfg.get("edit.height", 1080))
    return (
        f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1,format=yuv420p"
    )


def _filler(
    cfg: Config, index: int, frames: int, fps: int, segdir: Path, out_path: Path
) -> Path:
    """Ultimo recurso: un plano sintetico de la duracion exacta. Feo, pero el
    video sigue cuadrando y solo se ven unos segundos de fondo liso."""
    width = int(cfg.get("edit.width", 1920))
    height = int(cfg.get("edit.height", 1080))
    duration = frames / fps
    log.warn(f"Plano {index}: relleno sintetico de {duration:.2f}s para no perder la sincronia")
    ffmpeg.run([
        "-f", "lavfi",
        "-i", f"color=c=0x111318:size={width}x{height}:rate={fps}:duration={duration + 0.5:.3f}",
        "-vf", "vignette=PI/5,setsar=1,format=yuv420p",
    ] + _encode_args(cfg, fps, frames, out_path), cwd=segdir)
    return out_path


def _pick_in_point(index: int, clip_duration: float, needed: float) -> float:
    """Entra en un punto distinto del clip cada vez que se reutiliza."""
    margin = clip_duration - needed - 0.2
    if margin <= 0.3:
        return 0.0
    rng = random.Random(index * 7919)
    # Evita el primer medio segundo, que suele traer el fundido de entrada del stock
    return round(rng.uniform(0.4, max(0.4, margin)), 3)


def _filter_chain(
    cfg: Config, slot: dict, frames: int, fps: int,
    index: int, font_file: Path | None, segdir: Path,
) -> str:
    width = int(cfg.get("edit.width", 1920))
    height = int(cfg.get("edit.height", 1080))
    is_hook = slot["kind"] == "hook"
    duration = frames / fps

    parts = [f"fps={fps}"]

    if cfg.get("edit.body.ken_burns", True):
        # Se sobredimensiona antes del zoompan para que el zoom no pixele
        over_w, over_h = int(width * 1.10), int(height * 1.10)
        parts += [
            f"scale={over_w}:{over_h}:force_original_aspect_ratio=increase",
            f"crop={over_w}:{over_h}",
            f"zoompan=z='{_zoom_expr(cfg, slot, index, frames)}':d=1"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}",
        ]
    else:
        parts += [
            f"scale={width}:{height}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}",
        ]

    if cfg.get("edit.grade.enabled", True):
        parts.append(
            f"eq=contrast={cfg.get('edit.grade.contrast', 1.06)}"
            f":saturation={cfg.get('edit.grade.saturation', 1.12)}"
        )
        if cfg.get("edit.grade.vignette", True):
            parts.append("vignette=PI/5")

    # Flash blanco de entrada: solo en el hook, y solo unos fotogramas
    if is_hook and int(cfg.get("edit.hook.flash_frames", 1)) > 0:
        flash = int(cfg.get("edit.hook.flash_frames", 1)) / fps
        parts.append(f"fade=t=in:st=0:d={flash:.3f}:color=white")

    parts.extend(_label_filters(cfg, slot, font_file, segdir, index))
    parts += ["setsar=1", "format=yuv420p"]
    return ",".join(parts)


def _zoom_expr(cfg: Config, slot: dict, index: int, frames: int) -> str:
    """Zoom continuo. Alterna acercar/alejar para que no todo respire igual."""
    if slot["kind"] == "hook":
        punch = float(cfg.get("edit.hook.zoom_punch", 0.10))
        if punch <= 0:
            return "1"
        # Golpe: entra ampliado y se asienta. Muy rapido, encaja con cortes de 0,3 s
        return f"max(1,{1 + punch:.3f}-{punch:.3f}*on/{frames})"

    amount = float(cfg.get("edit.body.ken_burns_amount", 0.07))
    if amount <= 0:
        return "1"
    if index % 2 == 0:
        return f"min({1 + amount:.3f},1+{amount:.3f}*on/{frames})"
    return f"max(1,{1 + amount:.3f}-{amount:.3f}*on/{frames})"


def _label_filters(
    cfg: Config, slot: dict, font_file: Path | None, segdir: Path, index: int
) -> list[str]:
    """Rotulos de cifra: centrados, enormes y con entrada rapida.

    Van en el centro de la imagen a proposito. Los subtitulos ocupan la banda
    baja, asi que el centro es el unico sitio donde una cifra puede ser lo mas
    grande de la pantalla sin pelearse con nada.

    El texto se pasa en un archivo aparte porque dentro del grafo de filtros hay
    que escapar comillas, dos puntos y comas, y una cifra como "1.200.000 €" los
    lleva casi todos.
    """
    if not cfg.get("figures.enabled", True):
        return []
    labels = slot.get("labels") or []
    if not labels:
        return []

    accent = (cfg.get("figures.color") or cfg.get("brand.accent", "#FFD400")).lstrip("#")
    base_size = int(cfg.get("figures.font_size", 156))
    filters: list[str] = []

    for position, label in enumerate(labels):
        text = str(label.get("text", "")).strip().upper()
        if not text:
            continue
        start = max(0.0, float(label.get("from", 0.0)))
        end = float(label.get("to", 0.0))
        if end - start < 0.08:
            continue

        textfile = segdir / f"label_{index:04d}_{position}.txt"
        textfile.write_text(text, encoding="utf-8")

        options = [
            f"textfile={textfile.name}",
            "reload=0",
            # SIN esto, drawtext trata el texto como plantilla y al toparse con
            # un "%" lo descarta ENTERO con un aviso que no rompe el render:
            # todos los porcentajes salian invisibles y el log no decia nada.
            "expansion=none",
            f"fontsize={_fit_size(text, base_size, int(cfg.get('edit.width', 1920)))}",
            f"fontcolor=0x{accent}",
            f"borderw={int(cfg.get('figures.outline', 12))}",
            "bordercolor=black@0.92",
            "shadowx=0",
            f"shadowy={int(cfg.get('figures.shadow', 7))}",
            "shadowcolor=black@0.45",
            "x=(w-text_w)/2",
            "y=(h-text_h)/2",
            f"enable='between(t,{start:.3f},{end:.3f})'",
            f"alpha='{_pop_alpha(start, end, bool(label.get('head', True)), bool(label.get('tail', True)))}'",
        ]
        if font_file is not None:
            # Ruta relativa a segdir (el cwd de ffmpeg). Una ruta absoluta de
            # Windows mete dos puntos dentro del grafo de filtros y no hay
            # escapado que valga: ffmpeg los toma como separador de opciones.
            options.insert(0, f"fontfile=../fonts/{font_file.name}")
        filters.append("drawtext=" + ":".join(options))
    return filters


def _fit_size(text: str, base: int, frame_width: int) -> int:
    """Cuerpo de letra maximo que cabe a lo ancho.

    Se estima el ancho en lugar de aplicar una escala por tramos: con una tabla
    de tramos, "300.000-500.000 €" bajaba a 75 px cuando en realidad cabe de
    sobra a tamaño completo. Anton avanza unos 0,48 em por caracter.
    """
    usable = frame_width * 0.82
    estimated = max(1, len(text)) * 0.48
    return max(64, min(base, int(usable / estimated)))


def _pop_alpha(start: float, end: float, head: bool, tail: bool) -> str:
    """Opacidad del rotulo dentro de ESTE plano.

    La entrada solo se aplica donde el rotulo empieza de verdad y la salida solo
    donde acaba. Una cifra que se mantiene tres cortes seguidos es una unica
    aparicion continua: si cada plano hiciera su propio fundido, la cifra
    parpadearia en cada corte.
    """
    if not head and not tail:
        return "1"
    rise = 0.07 if head else 0.0
    fall = min(0.14, max(0.05, (end - start) * 0.25)) if tail else 0.0

    expression = "1"
    if fall > 0:
        expression = f"if(lt(t,{end - fall:.3f}),1,max(0,({end:.3f}-t)/{fall:.3f}))"
    if rise > 0:
        expression = (
            f"if(lt(t,{start:.3f}),0,"
            f"if(lt(t,{start + rise:.3f}),(t-{start:.3f})/{rise:.3f},{expression}))"
        )
    return expression


def _localize_font(font_file: Path | None, workdir: Path) -> Path | None:
    """Copia la fuente a workdir/fonts para poder referenciarla en relativo."""
    if font_file is None:
        return None
    local_dir = workdir / "fonts"
    local_dir.mkdir(parents=True, exist_ok=True)
    local = local_dir / font_file.name
    if not local.exists():
        shutil.copy2(font_file, local)
    return local


# ==========================================================================
# 3. Audio
# ==========================================================================

def _mix_audio(cfg: Config, broll: dict[str, Any], timeline: dict[str, Any], workdir: Path) -> Path:
    narration = Path(timeline["narration_path"])
    total = float(timeline["duration"])

    sfx_paths = sfx.ensure(
        ASSETS_DIR / "sfx", cfg.get("audio.whoosh_style", "sweep"), ffmpeg.run
    )
    events = _sfx_events(cfg, broll["slots"], sfx_paths, broll.get("figures", []))
    sfx_track = build_bed(events, sfx_paths, total, workdir / "sfx.wav", workdir / "audio")

    music = _pick_music()
    out_path = workdir / "mixed.wav"

    inputs = ["-i", str(narration), "-i", str(sfx_track)]
    sfx_db = float(cfg.get("audio.sfx_volume_db", -9.0))

    if music is None:
        log.warn(
            "Sin musica en assets/music/. El video sale solo con voz y efectos. "
            "Descarga pistas libres de la Biblioteca de audio de YouTube y dejalas ahi."
        )
        graph = (
            f"[1:a]volume={sfx_db}dB[sfx];"
            f"[0:a][sfx]amix=inputs=2:duration=first:normalize=0,"
            f"alimiter=limit=0.97[out]"
        )
    else:
        log.info(f"Musica de fondo: {music.name}")
        inputs = ["-i", str(narration), "-stream_loop", "-1", "-i", str(music), "-i", str(sfx_track)]
        music_db = float(cfg.get("audio.music_volume_db", -22.0))
        duck_ratio = max(2.0, abs(float(cfg.get("audio.duck_db", -12.0))))
        graph = (
            f"[0:a]asplit=2[nar][key];"
            f"[1:a]volume={music_db}dB[mus];"
            # La musica baja sola cuando entra la voz y vuelve a subir al callar
            f"[mus][key]sidechaincompress=threshold=0.03:ratio={duck_ratio:.0f}"
            f":attack=15:release=350:makeup=1[ducked];"
            f"[2:a]volume={sfx_db}dB[sfx];"
            f"[nar][ducked][sfx]amix=inputs=3:duration=first:normalize=0,"
            f"alimiter=limit=0.97[out]"
        )

    ffmpeg.run(inputs + [
        "-filter_complex", graph, "-map", "[out]",
        "-t", f"{total:.3f}",
        "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(out_path),
    ])
    return out_path


def _sfx_events(
    cfg: Config, slots: list[dict], sfx_paths: dict[str, Path],
    figures: list[dict] | None = None,
) -> list[SfxEvent]:
    events: list[SfxEvent] = []
    if cfg.get("audio.opening_impact", False):
        events.append(SfxEvent(at=0.0, name="impact", gain_db=-3.0))
    every = max(1, int(cfg.get("edit.body.whoosh_every_n_cuts", 2)))
    hook_mode = str(cfg.get("edit.hook.sfx", "whoosh")).lower()
    body_sfx = bool(cfg.get("edit.body.whoosh_sfx", True))
    picker = _WhooshPicker(sfx_paths)

    # Marcas donde suena una transicion, para saber cuanto hueco hay hasta la
    # siguiente y no meter un sonido de dos segundos en un hueco de uno.
    marks: list[float] = []
    counter = 0
    for slot in slots:
        if slot["kind"] == "hook":
            if hook_mode != "none" and slot["start"] > 0.01:
                marks.append(slot["start"])
        else:
            counter += 1
            if counter % every == 0:
                marks.append(slot["start"])

    body_index = 0
    for slot in slots:
        if slot["kind"] == "hook":
            # En el troceo rapido suena una transicion en CADA corte: es lo que
            # da la sensacion de metralleta. Como el hueco es de 0,3 s, el
            # selector se queda solo con las transiciones cortas.
            if hook_mode == "none" or slot["start"] <= 0.01:
                continue
            if hook_mode == "shutter":
                events.append(SfxEvent(at=slot["start"], name="shutter"))
            else:
                events.append(_whoosh_event(picker, slot["start"], marks))
        else:
            body_index += 1
            if body_sfx and body_index % every == 0:
                events.append(_whoosh_event(picker, slot["start"], marks))

    # Un golpe seco cada vez que una cifra entra en pantalla. Es el sonido que
    # el espectador asocia al dato, y funciona tanto en el hook como en el cuerpo.
    if cfg.get("figures.sound", True):
        gain = float(cfg.get("figures.sound_db", -6.0))
        for figure in figures or []:
            events.append(SfxEvent(at=float(figure["start"]), name="pop", gain_db=gain))

    events.sort(key=lambda event: event.at)
    return events


def _whoosh_event(picker: "_WhooshPicker", cut_at: float, marks: list[float]) -> SfxEvent:
    """Coloca la transicion justo ANTES del corte: asi se percibe como una
    transicion y no como un ruido que llega tarde."""
    gap = next((mark - cut_at for mark in marks if mark > cut_at + 0.05), 4.0)
    return SfxEvent(at=max(0.0, cut_at - 0.06), name=picker.pick(gap))


class _WhooshPicker:
    """Rota entre las transiciones disponibles evitando repetir seguido y
    descartando las que no caben en el hueco hasta el siguiente corte."""

    def __init__(self, sfx_paths: dict[str, Path]) -> None:
        keys = [key for key in sfx_paths if key.startswith("whoosh:")]
        self.keys = sorted(keys, key=lambda key: int(key.split(":")[1]))
        self.durations: dict[str, float] = {}
        for key in self.keys:
            try:
                self.durations[key] = ffmpeg.duration(sfx_paths[key])
            except ffmpeg.FFmpegError:
                self.durations[key] = 0.6
        self._cursor = 0
        self._last: str | None = None

    def pick(self, gap: float) -> str:
        """Round-robin de verdad: avanza el cursor MAS ALLA del elegido.

        Con un modulo sobre un pool que cambia de tamano segun el hueco, unos
        sonidos salian treinta veces y otros dos. Recorriendo el anillo desde
        el cursor y dejandolo detras del elegido, el reparto queda parejo.
        """
        if not self.keys:
            return "whoosh:0"
        budget = max(0.25, gap * 1.1)
        total = len(self.keys)
        for step in range(total):
            key = self.keys[(self._cursor + step) % total]
            if self.durations[key] <= budget and key != self._last:
                self._cursor = (self._cursor + step + 1) % total
                self._last = key
                return key
        # Nada encaja en el hueco: el mas corto, aunque repita
        key = min(self.keys, key=lambda item: self.durations[item])
        self._last = key
        return key


def _pick_music() -> Path | None:
    music_dir = ASSETS_DIR / "music"
    tracks = sorted(
        path for path in music_dir.glob("*")
        if path.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
    )
    return random.choice(tracks) if tracks else None


# ==========================================================================
# 4. Subtitulos y masterizado
# ==========================================================================

def _write_captions(
    cfg: Config, timeline: dict[str, Any], workdir: Path, font_family: str
) -> Path | None:
    if not cfg.get("captions.enabled", True):
        return None
    cues: list[Cue] = []
    max_chars = int(cfg.get("captions.max_chars_per_cue", 22))
    for segment in timeline["segments"]:
        cues += caption_cues(
            segment["narration"], float(segment["start"]), float(segment["end"]), max_chars
        )
    log.info(f"Subtitulos: {len(cues)} cues")
    return captions_util.build_ass(
        cues,
        workdir / "captions.ass",
        width=int(cfg.get("edit.width", 1920)),
        height=int(cfg.get("edit.height", 1080)),
        font_name=font_family,
        font_size=int(cfg.get("captions.font_size", 82)),
        outline=int(cfg.get("captions.outline", 6)),
        shadow=int(cfg.get("captions.shadow", 3)),
        margin_bottom=int(cfg.get("captions.margin_bottom", 170)),
        accent=cfg.get("brand.accent", "#FFD400"),
        uppercase=bool(cfg.get("captions.uppercase", True)),
        highlight_numbers=bool(cfg.get("captions.highlight_numbers", True)),
    )


def _master(
    cfg: Config, silent: Path, mixed: Path, ass_path: Path | None,
    workdir: Path, font_file: Path | None,
) -> Path:
    output = workdir / "video.mp4"
    args = ["-i", silent.name, "-i", mixed.name]

    filters: list[str] = []
    if ass_path is not None:
        subtitle_filter = f"subtitles={ass_path.name}"
        if font_file is not None:
            # libass busca por nombre de familia dentro de fontsdir. Va en
            # relativo respecto a workdir, por el mismo motivo que drawtext.
            subtitle_filter += ":fontsdir=fonts"
        filters.append(subtitle_filter)

    watermark = ASSETS_DIR / "brand" / "logo.png"
    if watermark.exists():
        args += ["-i", str(watermark)]
        video_chain = ",".join(filters) if filters else "null"
        args += [
            "-filter_complex",
            f"[0:v]{video_chain}[base];"
            f"[2:v]scale=-1:70,format=rgba,colorchannelmixer=aa=0.55[wm];"
            f"[base][wm]overlay=W-w-46:46[v]",
            "-map", "[v]", "-map", "1:a",
        ]
    else:
        if filters:
            args += ["-vf", ",".join(filters)]
        args += ["-map", "0:v", "-map", "1:a"]

    args += [
        "-c:v", "libx264", "-preset", cfg.get("edit.master_preset", "medium"),
        "-crf", str(cfg.get("edit.master_crf", 19)),
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", output.name,
    ]
    ffmpeg.run(args, cwd=workdir)
    size_mb = output.stat().st_size / (1024 * 1024)
    log.info(f"Video final: {output.name}, {ffmpeg.duration(output) / 60:.1f} min, {size_mb:.0f} MB")
    return output
