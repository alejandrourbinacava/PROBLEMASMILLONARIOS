"""Diseno de sonido: efectos de transicion sintetizados con ffmpeg.

Un whoosh que suene moderno no es ruido con una envolvente encima: lo que el
oido reconoce como "algo ha pasado por delante" es un BARRIDO, el centro
espectral subiendo o bajando durante el efecto.

Aqui se consigue apilando bandas de ruido con las entradas escalonadas (primero
los graves, luego los medios, luego los agudos), un chirp de apoyo por debajo y
una cola corta de reverb. Es lo mismo que hace un banco de sonidos, solo que
generado en el momento y sin depender de ninguna descarga.

Si prefieres tus propios efectos, deja whoosh.wav / shutter.wav / impact.wav en
assets/sfx/ y se usaran esos en lugar de los sinteticos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import log


@dataclass
class Recipe:
    """Una receta = varias fuentes lavfi + un grafo que termina en [out]."""
    inputs: list[str]
    graph: str
    description: str = field(default="")


# --------------------------------------------------------------------------
# Transiciones. La elegida en config/channel.yml -> audio.whoosh_style
# se copia a assets/sfx/whoosh.wav
# --------------------------------------------------------------------------

WHOOSH_STYLES: dict[str, Recipe] = {

    "sweep": Recipe(
        description="Barrido ascendente con cuerpo. El estandar de transicion.",
        inputs=[
            "anoisesrc=d=0.62:c=pink:a=1:r=48000",
            "anoisesrc=d=0.62:c=white:a=1:r=48000",
            "aevalsrc='sin(2*PI*(170*t+2100*t*t))':d=0.62:s=48000",
        ],
        graph=(
            # Graves: entran ya y se van pronto
            "[0:a]bandpass=f=650:width_type=o:w=2.2,"
            "afade=t=in:st=0:d=0.30:curve=qua,"
            "afade=t=out:st=0.32:d=0.26:curve=exp,volume=1.7[low];"
            # Agudos: entran tarde. El desfase entre bandas ES el barrido.
            "[1:a]bandpass=f=4800:width_type=o:w=2.6,"
            "afade=t=in:st=0.12:d=0.30:curve=qua,"
            "afade=t=out:st=0.44:d=0.17:curve=exp,volume=1.3[high];"
            # Chirp de apoyo, muy por debajo: da direccion al barrido
            "[2:a]afade=t=in:st=0:d=0.34:curve=qua,"
            "afade=t=out:st=0.38:d=0.22:curve=exp,volume=0.22[chirp];"
            "[low][high][chirp]amix=inputs=3:normalize=0[mix];"
            "[mix]aecho=0.9:0.75:38|64:0.22|0.15,"
            "highpass=f=170,aformat=channel_layouts=stereo,"
            "stereowiden=delay=14:feedback=0.35:crossfeed=0.3:drymix=0.8,"
            "alimiter=limit=0.92,volume=1.9[out]"
        ),
    ),

    "riser": Recipe(
        description="Sube y corta en seco. Muy agresivo, tipo trailer.",
        inputs=[
            "anoisesrc=d=0.8:c=white:a=1:r=48000",
            "aevalsrc='sin(2*PI*(240*t+2600*t*t))':d=0.8:s=48000",
        ],
        graph=(
            "[0:a]highpass=f=380,lowpass=f=13000,"
            "afade=t=in:st=0:d=0.74:curve=exp,"
            "afade=t=out:st=0.76:d=0.04,volume=2.0[air];"
            "[1:a]afade=t=in:st=0:d=0.74:curve=exp,"
            "afade=t=out:st=0.76:d=0.04,volume=0.30[chirp];"
            "[air][chirp]amix=inputs=2:normalize=0,"
            "aformat=channel_layouts=stereo,"
            "stereowiden=delay=18:feedback=0.4:crossfeed=0.3:drymix=0.75,"
            "alimiter=limit=0.92,volume=1.8[out]"
        ),
    ),

    "swish": Recipe(
        description="Corto y seco, pasa de largo. El menos invasivo.",
        inputs=[
            "anoisesrc=d=0.34:c=brown:a=1:r=48000",
            "anoisesrc=d=0.34:c=white:a=1:r=48000",
        ],
        graph=(
            "[0:a]bandpass=f=900:width_type=o:w=1.8,"
            "afade=t=in:st=0:d=0.06:curve=qua,"
            "afade=t=out:st=0.08:d=0.24:curve=exp,volume=2.0[body];"
            "[1:a]bandpass=f=6200:width_type=o:w=2.2,"
            "afade=t=in:st=0.02:d=0.07:curve=qua,"
            "afade=t=out:st=0.10:d=0.20:curve=exp,volume=1.1[air];"
            "[body][air]amix=inputs=2:normalize=0,"
            "aecho=0.9:0.6:26:0.16,"
            "aformat=channel_layouts=stereo,"
            "stereowiden=delay=10:feedback=0.3:crossfeed=0.35:drymix=0.85,"
            "alimiter=limit=0.92,volume=1.9[out]"
        ),
    ),

    "sub": Recipe(
        description="Aire arriba y golpe de sub grave. El mas 'de canal grande'.",
        inputs=[
            "anoisesrc=d=0.7:c=white:a=1:r=48000",
            "aevalsrc='sin(2*PI*(95*t-52*t*t))':d=0.7:s=48000",
        ],
        graph=(
            "[0:a]highpass=f=2200,lowpass=f=14000,"
            "afade=t=in:st=0:d=0.26:curve=qua,"
            "afade=t=out:st=0.28:d=0.40:curve=exp,volume=1.5[air];"
            # Sub que cae de 95 Hz hacia abajo: el 'peso' de la transicion
            "[1:a]lowpass=f=200,"
            "afade=t=in:st=0:d=0.02,"
            "afade=t=out:st=0.14:d=0.54:curve=exp,volume=1.6[drop];"
            "[air][drop]amix=inputs=2:normalize=0,"
            "aformat=channel_layouts=stereo,"
            "stereowiden=delay=12:feedback=0.3:crossfeed=0.3:drymix=0.85,"
            "alimiter=limit=0.9,volume=1.8[out]"
        ),
    ),
}


# --------------------------------------------------------------------------
# Obturador del hook e impacto de apertura
# --------------------------------------------------------------------------

SHUTTER = Recipe(
    description="Obturador reflex: espejo y cortinilla, dos golpes separados.",
    inputs=[
        "anoisesrc=d=0.13:c=white:a=1:r=48000",
        "anoisesrc=d=0.13:c=white:a=1:r=48000",
    ],
    graph=(
        # Primer golpe: el espejo. Mas grave y con algo de cuerpo.
        "[0:a]bandpass=f=1500:width_type=o:w=2.4,"
        "afade=t=in:st=0:d=0.002,"
        "afade=t=out:st=0.006:d=0.05:curve=exp,volume=2.4[mirror];"
        # Segundo golpe 38 ms despues: la cortinilla. Mas agudo y mas corto.
        "[1:a]highpass=f=3200,lowpass=f=11000,"
        "afade=t=in:st=0:d=0.001,"
        "afade=t=out:st=0.004:d=0.035:curve=exp,volume=1.9,"
        "adelay=38|38[curtain];"
        "[mirror][curtain]amix=inputs=2:normalize=0,"
        "aformat=channel_layouts=stereo,alimiter=limit=0.94,volume=1.6[out]"
    ),
)

IMPACT = Recipe(
    description="Impacto de apertura: sub con cola corta.",
    inputs=[
        "aevalsrc='sin(2*PI*(58*t-16*t*t))':d=1.2:s=48000",
        "anoisesrc=d=1.2:c=brown:a=1:r=48000",
    ],
    graph=(
        "[0:a]lowpass=f=170,"
        "afade=t=in:st=0:d=0.004,"
        "afade=t=out:st=0.05:d=1.1:curve=exp,volume=1.9[sub];"
        "[1:a]bandpass=f=380:width_type=o:w=2,"
        "afade=t=in:st=0:d=0.003,"
        "afade=t=out:st=0.02:d=0.5:curve=exp,volume=1.0[body];"
        "[sub][body]amix=inputs=2:normalize=0,"
        "aformat=channel_layouts=stereo,"
        "acompressor=threshold=0.12:ratio=5,alimiter=limit=0.92,volume=1.7[out]"
    ),
)


def build(recipe: Recipe, out_path: Path, runner) -> Path:
    """Sintetiza una receta. `runner` es pipeline.util.ffmpeg.run."""
    args: list[str] = []
    for source in recipe.inputs:
        args += ["-f", "lavfi", "-i", source]
    args += [
        "-filter_complex", recipe.graph, "-map", "[out]",
        "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(out_path),
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    runner(args)
    return out_path


WHOOSH_POOL_DIR = "whoosh"
_AUDIO_EXTENSIONS = (".wav", ".mp3", ".m4a", ".ogg", ".flac")


def ensure(sfx_dir: Path, whoosh_style: str, runner) -> dict[str, Path]:
    """Devuelve {clave: ruta} para la mezcla.

    Las transiciones se devuelven como whoosh:0, whoosh:1... El montaje las va
    rotando entre cortes: repetir el mismo golpe doscientas veces se nota
    enseguida y delata que el vídeo está hecho con plantilla.

    Prioridad para las transiciones:
      1. assets/sfx/whoosh/  -> banco propio, se rotan todas
      2. assets/sfx/whoosh.* -> un único archivo propio
      3. síntesis según audio.whoosh_style
    """
    sfx_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    for index, path in enumerate(_whoosh_sources(sfx_dir, whoosh_style, runner)):
        paths[f"whoosh:{index}"] = path

    # "pop" es el golpe que acompaña a cada cifra en pantalla. Si no hay uno
    # propio se reaprovecha la receta del obturador, que es igual de seca.
    for name, recipe in (("shutter", SHUTTER), ("impact", IMPACT), ("pop", SHUTTER)):
        override = _user_file(sfx_dir, name)
        if override is not None:
            log.info(f"Efecto propio: {override.name}")
            paths[name] = override
            continue
        target = sfx_dir / f"{name}.wav"
        if not target.exists() or target.stat().st_size < 2048:
            log.info(f"Sintetizando {target.name}: {recipe.description}")
            build(recipe, target, runner)
        paths[name] = target
    return paths


def _whoosh_sources(sfx_dir: Path, whoosh_style: str, runner) -> list[Path]:
    pool_dir = sfx_dir / WHOOSH_POOL_DIR
    if pool_dir.is_dir():
        pool = sorted(
            path for path in pool_dir.iterdir()
            if path.suffix.lower() in _AUDIO_EXTENSIONS and path.stat().st_size > 2048
        )
        if pool:
            log.info(
                f"Banco de transiciones propio: {len(pool)} sonidos "
                f"({', '.join(p.stem for p in pool[:5])}{'...' if len(pool) > 5 else ''})"
            )
            return pool

    single = _user_file(sfx_dir, "whoosh")
    if single is not None:
        log.info(f"Transición propia: {single.name}")
        return [single]

    style = whoosh_style if whoosh_style in WHOOSH_STYLES else "sweep"
    if style != whoosh_style:
        log.warn(
            f"audio.whoosh_style '{whoosh_style}' no existe. "
            f"Opciones: {', '.join(WHOOSH_STYLES)}. Se usa 'sweep'."
        )
    # El estilo va en el nombre: cambiarlo en la config regenera el archivo
    target = sfx_dir / f"whoosh_{style}.wav"
    if not target.exists() or target.stat().st_size < 2048:
        log.info(f"Sintetizando {target.name}: {WHOOSH_STYLES[style].description}")
        build(WHOOSH_STYLES[style], target, runner)
    return [target]


def _user_file(sfx_dir: Path, name: str) -> Path | None:
    for extension in (".wav", ".mp3", ".m4a", ".ogg", ".flac"):
        candidate = sfx_dir / f"{name}{extension}"
        if candidate.exists() and candidate.stat().st_size > 2048:
            return candidate
    return None
