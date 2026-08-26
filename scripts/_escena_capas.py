"""Una escena montada con un elemento por sustantivo de la frase.

    "antes de que entre el primer cliente"

        fondo       el interior del casino, desenfocado
        gente       lo que se ve a traves de las puertas
        puertas     la entrada
        TEXTO       aqui, entre la puerta y quien la cruza
        seguridad   a un lado
        cliente     de espaldas, lo mas cerca de camara

Cada capa entra con un efecto distinto y se mueve a distinta velocidad.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, ".")

from PIL import Image, ImageFilter

from pipeline.util import ffmpeg
from pipeline.util import layers as L

W, H, FPS = 1920, 1080, 25
OUT = Path("build/_escena").resolve()
CLIPS = Path(".cache/clips").resolve()
FONT = Path("assets/fonts/Poppins-Black.ttf").resolve()

_SESSION = None


def recorte(clip: str, at: float, nombre: str) -> Image.Image:
    """Recorta el sujeto y AVISA de su resolucion real."""
    global _SESSION
    dst = OUT / f"{nombre}.png"
    if not dst.exists():
        still = OUT / f"{nombre}.src.png"
        ffmpeg.run(["-ss", f"{at:.2f}", "-i", str(CLIPS / clip), "-frames:v", "1",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                    str(still)])
        from rembg import new_session, remove
        if _SESSION is None:
            _SESSION = new_session("u2net")
        remove(Image.open(still).convert("RGBA"), session=_SESSION).save(dst)
    image = Image.open(dst).convert("RGBA")
    box = image.getchannel("A").getbbox()
    alto = (box[3] - box[1]) if box else 0
    tope = L.max_scale(image, H)
    marca = "ok" if L.is_cutout(image) else "RECORTE MALO"
    print(f"  {nombre:10} sujeto {alto:4}px de alto  ->  tope de escala {tope:.2f}  [{marca}]")
    return image


def fondo_plano(clip: str, at: float, nombre: str, blur: int = 18) -> Image.Image:
    dst = OUT / f"{nombre}.png"
    if not dst.exists():
        ffmpeg.run(["-ss", f"{at:.2f}", "-i", str(CLIPS / clip), "-frames:v", "1",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                    str(dst)])
    return Image.open(dst).convert("RGBA").filter(ImageFilter.GaussianBlur(blur))


def texto(cadena: str, size: int, y: float, hueco: tuple[float, float],
          colour=(255, 255, 255)) -> Image.Image:
    """Escribe dentro del hueco medido, encogiendo la letra si no cabe."""
    from PIL import ImageDraw, ImageFont
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Se permite que asome un poco por detras de las figuras (ese es el efecto),
    # pero no que se coma una palabra: el hueco se ensancha solo un 18%.
    ancho = (hueco[1] - hueco[0]) * W * 1.18
    while size > 44:
        font = ImageFont.truetype(str(FONT), size)
        if draw.textlength(cadena, font=font) <= ancho:
            break
        size -= 6
    font = ImageFont.truetype(str(FONT), size)
    span = draw.textlength(cadena, font=font)
    centro = (hueco[0] + hueco[1]) / 2
    draw.text((L.safe_x(span, W, centro), H * y), cadena, font=font, fill=(*colour, 255))
    print(f"    texto a {size}px en el hueco {hueco[0]:.2f}-{hueco[1]:.2f}")
    return image


def colocar(cutout: Image.Image, escala: float, anclaje: tuple[float, float]) -> Image.Image:
    """Coloca respetando el tope de aumento del recorte."""
    tope = L.max_scale(cutout, H)
    if escala > tope:
        print(f"    (escala {escala:.2f} recortada a {tope:.2f}: no da mas de si)")
        escala = tope
    return L.fit_canvas(cutout, W, H, escala, anclaje)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(">> recortes")
    cliente = recorte("pexels_3374591_63cab7748b.mp4", 1.5, "cliente")
    puertas = recorte("pexels_5266998_587353952f.mp4", 1.5, "puertas")
    gente = recorte("pexels_852107_e70c4cb090.mp4", 2.0, "gente")
    seguridad = recorte("pixabay_199623_cfd4ba6740.mp4", 1.5, "seguridad")
    interior = fondo_plano("pixabay_176993_16ce96aae2.mp4", 2.0, "interior")

    print(">> composicion")
    # El recorte de la multitud sale rechazado: rembg no encuentra sujeto en un
    # borron. El interior desenfocado del fondo YA hace ese papel, y ademas
    # mejor: la gente del casino se intuye, no se recorta.
    if not L.is_cutout(gente):
        print("  gente: descartada, no es un recorte (es una mancha)")

    # Tamanos modestos: si un elemento llena el encuadre, tapa a los demas y se
    # pierde la composicion por capas, que es justo lo que se busca.
    capa_letrero = colocar(puertas, 0.30, (0.80, 0.16))
    capa_seg = colocar(seguridad, 0.50, (0.10, 1.0))
    capa_cliente = colocar(cliente, 0.62, (0.86, 1.0))

    # El hueco se MIDE sobre las figuras ya colocadas, no se adivina
    hueco = L.free_span([capa_seg, capa_cliente, capa_letrero], W, H)
    print(f"  hueco libre: {hueco[0]:.2f} a {hueco[1]:.2f} del ancho")

    comp = L.Composition(width=W, height=H, push=0.11, layers=[
        L.Layer(L.graded(interior, (20, 40, 90), 0.55, 1.1, 0.9),
                entrance="fade", delay=0.00, duration=0.20, parallax=0.0),
        L.Layer(L.graded(capa_letrero, (255, 190, 210), 0.12, 1.25, 1.4),
                entrance="fall", delay=0.10, duration=0.30, parallax=0.35),
        L.Layer(texto("EL PRIMER CLIENTE", 120, 0.38, hueco),
                entrance="rise", delay=0.34, duration=0.26, parallax=0.70),
        L.Layer(L.graded(capa_seg, (40, 70, 140), 0.30, 1.2, 0.95),
                entrance="slide_right", delay=0.44, duration=0.26, parallax=1.05),
        L.Layer(L.graded(capa_cliente, (30, 45, 110), 0.24, 1.25, 1.05),
                entrance="slide_left", delay=0.24, duration=0.32, parallax=1.55),
    ])

    frames = int(4.4 * FPS)
    out = OUT / "escena.mp4"
    L.render(comp, out, frames=frames, fps=FPS, encode_args=[
        "-frames:v", str(frames), "-r", str(FPS), "-fps_mode", "cfr",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", out.name,
    ])
    print(f">> {out}  {ffmpeg.duration(out):.2f}s")


if __name__ == "__main__":
    main()
