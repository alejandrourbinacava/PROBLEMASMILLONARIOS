"""Prueba de 30 segundos con los tres estilos, uno detrás de otro.

    0:00 - 0:10   VOX          papel cuadriculado, círculo rojo, flecha, subrayado
    0:10 - 0:22   MagnatesMedia  escenas por capas, texto DETRÁS del sujeto
    0:22 - 0:27   parallax       lo mismo pero enseñando solo la profundidad
    0:27 - 0:30   remate         cortes rápidos con whoosh

Sin narración a propósito: esto prueba imagen, y la voz de ai33 cuesta créditos.
Lleva música y efectos para que se juzgue con el ritmo real.
"""
from __future__ import annotations

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, ".")

from PIL import Image

from pipeline.util import annotate, ffmpeg, graphics
from pipeline.util import layers as L

W, H, FPS = 1920, 1080, 25
OUT = Path("build/_demo30").resolve()
CLIPS = Path(".cache/clips").resolve()
FONT = Path("assets/fonts/Poppins-Black.ttf").resolve()

ENCODE = [
    "-r", str(FPS), "-fps_mode", "cfr",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
    "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
    "-x264-params", f"keyint={FPS * 2}:min-keyint={FPS * 2}:scenecut=0",
    "-threads", "1", "-f", "mpegts",
]


def encode(frames: int, name: str) -> list[str]:
    return ["-frames:v", str(frames)] + ENCODE + [name]


# --------------------------------------------------------------------------
# Recortes
# --------------------------------------------------------------------------

_SESSION = None


def cutout(clip: Path, at: float, dst: Path) -> Image.Image:
    """Saca un fotograma del clip y le quita el fondo con rembg."""
    global _SESSION
    if dst.exists():
        return Image.open(dst).convert("RGBA")
    still = dst.with_suffix(".src.png")
    ffmpeg.run(["-ss", f"{at:.2f}", "-i", str(clip), "-frames:v", "1", str(still)])
    from rembg import new_session, remove

    if _SESSION is None:
        _SESSION = new_session("u2net")
    image = remove(Image.open(still).convert("RGBA"), session=_SESSION)
    image.save(dst)
    return image


def still(clip: Path, at: float, dst: Path) -> Image.Image:
    if not dst.exists():
        ffmpeg.run([
            "-ss", f"{at:.2f}", "-i", str(clip), "-frames:v", "1",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
            str(dst),
        ])
    return Image.open(dst).convert("RGBA")


def text_layer(text: str, size: int, y: float, colour=(255, 255, 255)) -> Image.Image:
    from PIL import ImageDraw, ImageFont

    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(FONT), size)
    span = draw.textlength(text, font=font)
    draw.text(((W - span) / 2, H * y), text, font=font, fill=(*colour, 255))
    return image


# --------------------------------------------------------------------------
# Planos
# --------------------------------------------------------------------------

def vox_graphic(spec: graphics.GraphicSpec, seconds: float, name: str) -> Path:
    frames = int(seconds * FPS)
    out = OUT / name
    graphics.render(
        spec, out, frames=frames, fps=FPS,
        theme=graphics.Theme(width=W, height=H, font_file=FONT),
        encode_args=encode(frames, out.name),
    )
    return out


def vox_annotated(clip: Path, seconds: float, ann: annotate.Annotation, name: str) -> Path:
    """Clip de archivo con la capa de anotación encima, como hace VOX."""
    frames = int(seconds * FPS)
    pattern = annotate.render_frames(ann, OUT / f"ann_{name}", frames=frames)
    out = OUT / name
    ffmpeg.run([
        "-ss", "1.0", "-i", str(clip),
        "-framerate", str(FPS), "-i", str(pattern),
        "-filter_complex",
        f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},setsar=1,eq=saturation=1.12:contrast=1.08[base];"
        f"[base][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]",
    ] + encode(frames, out.name), cwd=OUT)
    return out


def composed(comp: L.Composition, seconds: float, name: str) -> Path:
    frames = int(seconds * FPS)
    out = OUT / name
    L.render(comp, out, frames=frames, fps=FPS, encode_args=encode(frames, out.name))
    return out


def plain(clip: Path, seconds: float, name: str, start: float = 1.0) -> Path:
    frames = int(seconds * FPS)
    out = OUT / name
    ffmpeg.run([
        "-ss", f"{start}", "-i", str(clip),
        "-vf",
        f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},setsar=1,eq=saturation=1.15:contrast=1.1,format=yuv420p",
        "-an",
    ] + encode(frames, out.name), cwd=OUT)
    return out


# --------------------------------------------------------------------------

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    C = lambda name: CLIPS / name  # noqa: E731

    ruleta = C("pexels_35728855_0962957f02.mp4")
    ruleta2 = C("pexels_36600728_38ae073548.mp4")
    fichas = C("pexels_7607942_e0c26d60bb.mp4")
    fichas2 = C("pexels_7608213_35b9798554.mp4")
    cartas = C("pexels_35728857_19020f1c2a.mp4")
    tragaperras = C("pexels_9807879_49e3623999.mp4")
    neon = C("pexels_36147796_c8b4e20f0c.mp4")
    vegas = C("pexels_31869126_ba8a2aa5c0.mp4")
    manos = C("pexels_35728852_cb23b26767.mp4")
    traje = C("pexels_4512205_2cb059a052.mp4")
    ciudad = C("pixabay_42487_fc2141cc56.mp4")
    lampara = C("pexels_34555902_2c9bd49f6d.mp4")

    print(">> recortes")
    sujeto_manos = cutout(manos, 2.0, OUT / "cut_manos.png")
    sujeto_traje = cutout(traje, 1.5, OUT / "cut_traje.png")
    sujeto_fichas = cutout(fichas2, 1.5, OUT / "cut_fichas.png")
    fondo_neon = still(neon, 1.0, OUT / "bg_neon.png")
    fondo_ciudad = still(ciudad, 1.0, OUT / "bg_ciudad.png")
    fondo_vegas = still(vegas, 2.0, OUT / "bg_vegas.png")

    # ---------------- VOX ----------------
    print(">> VOX")
    v1 = vox_graphic(
        graphics.GraphicSpec(
            kind="bar", label="LA VENTAJA DE LA CASA", display="2,7%",
            value=2.7, unit="percent", context="La ruleta europea",
        ), 3.4, "01_vox_barra.ts",
    )
    v2 = vox_annotated(
        ruleta, 3.6,
        annotate.Annotation(
            width=W, height=H, font_file=FONT,
            circles=[annotate.Circle(centre=(0.52, 0.48), radius=0.17, delay=0.10)],
            arrows=[annotate.Arrow(start=(0.17, 0.80), end=(0.40, 0.56), bend=0.24, delay=0.42)],
            labels=[annotate.Label("EL CERO", at=(0.08, 0.80), size=62, delay=0.34)],
        ), "02_vox_ruleta.ts",
    )
    v3 = vox_graphic(
        graphics.GraphicSpec(
            kind="stack", context="Lo que cuesta abrir",
            items=[("Licencia", "8,4 M€"), ("Obra", "12 M€"),
                   ("Maquinas", "4,1 M€"), ("Caja fuerte", "3,5 M€")],
        ), 3.2, "03_vox_cuenta.ts",
    )

    # ---------------- MagnatesMedia ----------------
    print(">> MagnatesMedia")
    m1 = composed(L.Composition(width=W, height=H, push=0.09, layers=[
        L.Layer(L.backdrop_glow(W, H, (255, 176, 60), centre=(0.5, 0.55), radius=0.72),
                entrance="scale", delay=0.00, duration=0.45, parallax=0.0),
        L.Layer(L.fit_canvas(L.skyline(fondo_ciudad, (26, 22, 40), cut=0.52),
                             W, H, 0.62, (0.5, 0.98)),
                entrance="rise", delay=0.10, duration=0.35, parallax=0.25),
        L.Layer(text_layer("28 M€", 300, 0.30),
                entrance="scale", delay=0.24, duration=0.30, parallax=0.5),
        L.Layer(L.graded(L.fit_canvas(sujeto_manos, W, H, 0.95, (0.5, 1.0)),
                         (255, 150, 60), 0.28, 1.3, 1.2),
                entrance="slide_left", delay=0.16, duration=0.35, parallax=1.0),
    ]), 4.0, "04_mm_ciudad.ts")

    m2 = composed(L.Composition(width=W, height=H, push=0.08, layers=[
        L.Layer(L.graded(fondo_neon, (40, 90, 190), 0.42, 1.2, 1.35),
                entrance="fade", delay=0.00, duration=0.30, parallax=0.0),
        L.Layer(text_layer("300 PERSONAS", 170, 0.34),
                entrance="rise", delay=0.22, duration=0.28, parallax=0.45),
        L.Layer(L.silhouette(L.fit_canvas(sujeto_traje, W, H, 1.45, (0.38, 1.0)),
                             (10, 14, 30), 0.90),
                entrance="slide_right", delay=0.12, duration=0.34, parallax=1.0),
    ]), 3.6, "05_mm_traje.ts")

    m3 = composed(L.Composition(width=W, height=H, push=0.10, layers=[
        L.Layer(L.backdrop_glow(W, H, (60, 200, 170), centre=(0.62, 0.44), radius=0.66),
                entrance="fade", delay=0.00, duration=0.25, parallax=0.0),
        L.Layer(L.fit_canvas(L.skyline(fondo_vegas, (12, 28, 38), cut=0.46),
                             W, H, 0.70, (0.5, 0.98)),
                entrance="wipe_up", delay=0.14, duration=0.30, parallax=0.3),
        L.Layer(text_layer("EL 2,7%", 260, 0.26),
                entrance="fall", delay=0.26, duration=0.28, parallax=0.55),
        L.Layer(L.graded(L.fit_canvas(sujeto_fichas, W, H, 0.80, (0.55, 1.0)),
                         (255, 210, 120), 0.22, 1.35, 1.25),
                entrance="rise", delay=0.18, duration=0.32, parallax=1.0),
    ]), 3.6, "06_mm_fichas.ts")

    # ---------------- parallax puro ----------------
    # Sin animaciones de entrada: todas las capas ya están puestas y lo único
    # que pasa es que la cámara empuja. Así se ve el efecto aislado.
    print(">> parallax")
    p1 = composed(L.Composition(width=W, height=H, push=0.26, layers=[
        L.Layer(L.graded(fondo_vegas, (30, 60, 150), 0.40, 1.15, 1.3),
                entrance="fade", delay=0.0, duration=0.01, parallax=0.0),
        L.Layer(L.fit_canvas(L.skyline(fondo_ciudad, (14, 18, 34), cut=0.52),
                             W, H, 0.58, (0.5, 0.98)),
                entrance="fade", delay=0.0, duration=0.01, parallax=0.45),
        L.Layer(text_layer("PARALLAX", 190, 0.22, (255, 212, 0)),
                entrance="fade", delay=0.0, duration=0.01, parallax=0.75),
        L.Layer(L.silhouette(L.fit_canvas(sujeto_traje, W, H, 1.35, (0.30, 1.0)),
                             (6, 8, 18), 0.95),
                entrance="fade", delay=0.0, duration=0.01, parallax=1.6),
    ]), 4.6, "07_parallax.ts")

    # ---------------- remate ----------------
    print(">> remate")
    rapid = [
        plain(clip, 0.48, f"08_r{index}.ts", start=1.2)
        for index, clip in enumerate(
            [ruleta2, tragaperras, cartas, fichas, lampara, neon]
        )
    ]

    order = [v1, v2, v3, m1, m2, m3, p1] + rapid
    silent = OUT / "silent.mp4"
    ffmpeg.concat_copy(order, silent, OUT)
    total = ffmpeg.duration(silent)
    print(f">> vídeo mudo: {total:.2f}s")
    return silent, total


if __name__ == "__main__":
    main()
