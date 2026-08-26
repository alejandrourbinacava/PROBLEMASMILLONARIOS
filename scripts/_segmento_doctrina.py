"""Un segmento montado según config/EDICION.md, sobre la narración ya sintetizada.

La diferencia con lo anterior no es estética, es de método: los planos NO salen
de un reparto por turnos, salen de decidir QUÉ EXPLICA cada frase y cuánto tiene
que durar esa explicación. Las marcas de tiempo vienen del SRT de la propia
narración, así que la cifra cae cuando se pronuncia.

El argumento del segmento es uno solo y se construye en cadena:

    la ruleta tiene 37 casillas  ->  paga como si tuviera 36
    esa diferencia  ->  2,7%
    parece poco  ->  es 28 millones antes de abrir

Cada plano prepara al siguiente. Eso es lo que pide la doctrina cuando dice que
la transición sale de la información.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, ".")

from pipeline.util import annotate, ffmpeg, graphics

W, H, FPS = 1920, 1080, 25
OUT = Path("build/_doctrina").resolve()
CLIPS = Path(".cache/clips").resolve()
FONT = Path("assets/fonts/Poppins-Black.ttf").resolve()
VOZ = Path("build/_demo30/voz.mp3").resolve()

TEMA = graphics.Theme(width=W, height=H, font_file=FONT)

# ---------------------------------------------------------------------------
# El plan. Un recurso por idea, con la duración que pide la explicación.
# Los cortes caen en los silencios del SRT, no cada N segundos.
# ---------------------------------------------------------------------------
PLAN = [
    # (fin_en_segundos, recurso, argumento)
    (2.20, "card", dict(display="NO APUESTA CONTRA TI")),
    (4.35, "card", dict(display="TE VENDE TIEMPO")),
    (6.86, "ruleta", dict(etiqueta="37 CASILLAS")),
    (8.30, "compare", dict(
        context="La ruleta europea", label="esta casilla es el negocio",
        items=[("casillas", "37"), ("te paga", "36")])),
    (11.30, "bar", dict(
        label="LA VENTAJA DE LA CASA", display="2,7%", value=2.7, unit="percent",
        context="En cada giro, para siempre")),
    (12.45, "card", dict(display="PARECE POCO")),
    (16.55, "counter", dict(
        label="ABRIR UNO", display="28.000.000 €", value=28_000_000, unit="eur",
        context="Antes del primer cliente")),
    (21.10, "stack", dict(
        context="Y todos los meses", items=[
            ("Personal", "300"), ("Vigilancia", "24 h"),
            ("Sin relojes", "0"), ("Sin ventanas", "0")])),
]

ENCODE_BASE = [
    "-r", str(FPS), "-fps_mode", "cfr",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
    "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
    "-x264-params", f"keyint={FPS * 2}:min-keyint={FPS * 2}:scenecut=0",
    "-threads", "1", "-f", "mpegts",
]


def encode(frames: int, name: str) -> list[str]:
    return ["-frames:v", str(frames)] + ENCODE_BASE + [name]


def plano_grafico(kind: str, frames: int, nombre: str, **campos) -> Path:
    out = OUT / nombre
    graphics.render(
        graphics.GraphicSpec(kind=kind, **campos), out,
        frames=frames, fps=FPS, theme=TEMA, encode_args=encode(frames, out.name),
    )
    return out


def plano_ruleta(frames: int, nombre: str, etiqueta: str) -> Path:
    """Metraje real con la anotación encima: se señala LA casilla, no la ruleta."""
    ann = annotate.Annotation(
        width=W, height=H, font_file=FONT,
        circles=[annotate.Circle(centre=(0.52, 0.47), radius=0.15, delay=0.16)],
        arrows=[annotate.Arrow(start=(0.16, 0.78), end=(0.40, 0.56),
                               bend=0.24, delay=0.44)],
        labels=[annotate.Label(etiqueta, at=(0.07, 0.78), size=64, delay=0.36)],
    )
    patron = annotate.render_frames(ann, OUT / f"ann_{nombre}", frames=frames)
    out = OUT / nombre
    ffmpeg.run([
        "-ss", "1.2", "-i", str(CLIPS / "pexels_35728855_0962957f02.mp4"),
        "-framerate", str(FPS), "-i", str(patron),
        "-filter_complex",
        f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},setsar=1,eq=saturation=0.9:contrast=1.06[base];"
        f"[base][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]",
    ] + encode(frames, out.name), cwd=OUT)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Reparto en fotogramas ENTEROS y acumulativos: si cada plano se redondea
    # por su cuenta, a los ocho planos la imagen ya va por detrás de la voz.
    piezas: list[Path] = []
    frame_previo = 0
    for indice, (fin, recurso, campos) in enumerate(PLAN):
        frame_fin = int(round(fin * FPS))
        frames = max(1, frame_fin - frame_previo)
        nombre = f"{indice:02d}_{recurso}.ts"
        print(f"  {indice:02d} {recurso:8} {frames / FPS:5.2f}s  hasta {fin:5.2f}s")
        if recurso == "ruleta":
            piezas.append(plano_ruleta(frames, nombre, **campos))
        else:
            piezas.append(plano_grafico(recurso, frames, nombre, **campos))
        frame_previo = frame_fin

    mudo = OUT / "mudo.mp4"
    ffmpeg.concat_copy(piezas, mudo, OUT)
    total = ffmpeg.duration(mudo)
    print(f">> imagen: {total:.2f}s / voz: {ffmpeg.duration(VOZ):.2f}s")

    final = OUT / "segmento.mp4"
    ffmpeg.run([
        "-i", str(mudo), "-i", str(VOZ),
        "-filter_complex",
        "[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
        f"loudnorm=I=-15:TP=-1.5:LRA=11,apad,atrim=0:{total:.3f}[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", str(final),
    ])
    print(f">> {final}  {ffmpeg.duration(final):.2f}s")


if __name__ == "__main__":
    main()
