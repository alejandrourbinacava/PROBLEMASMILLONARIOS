"""Miniaturas 1280x720 de bar, taxi, burger y peluqueria con la formula de la B del estanco.
    python miniaturas_4.py   ->  salidas/<tema>/miniatura.jpg
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
FUENTE = AQUI.parent / "assets" / "fonts" / "Poppins-Black.ttf"
W, H = 1280, 720
AMARILLO, ROJO = (255, 212, 0), (255, 45, 85)


def f(px):
    return ImageFont.truetype(str(FUENTE), px)


def cubrir(im, cx, cy, zoom=1.0):
    iw, ih = im.size
    bw = min(iw, ih * 16 / 9) / zoom
    bh = bw * 9 / 16
    x0 = min(max(cx * iw - bw / 2, 0), iw - bw)
    y0 = min(max(cy * ih - bh / 2, 0), ih - bh)
    return im.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)


def oscurecer(im, fuerza=0.80):
    deg = Image.new("L", (W, 1))
    for x in range(W):
        deg.putpixel((x, 0), int(255 * fuerza * max(0.0, 1 - x / (W * 0.88)) ** 0.9))
    return Image.composite(Image.new("RGB", (W, H), (8, 8, 12)), im, deg.resize((W, H)))


def texto(d, xy, s, px, fill, borde=10):
    d.text(xy, s, font=f(px), fill=fill, stroke_width=borde, stroke_fill=(0, 0, 0))


def hacer(tema, foto, cx, cy, zoom, lineas, cifra, sub):
    im = oscurecer(cubrir(Image.open(AQUI / "_fotos" / tema / "orig" / foto).convert("RGB"), cx, cy, zoom))
    d = ImageDraw.Draw(im)
    y = 56
    for s in lineas:
        texto(d, (60, y), s, 106, (255, 255, 255))
        y += 114
    y += 12
    px = 178 if len(cifra) <= 6 else 138
    texto(d, (60, y), cifra, px, AMARILLO, borde=13)
    bb = d.textbbox((60, y), cifra, font=f(px), stroke_width=13)
    d.rectangle([bb[0], bb[3] + 12, bb[2], bb[3] + 26], fill=ROJO)
    texto(d, (62, bb[3] + 44), sub, 48, (255, 255, 255), borde=7)
    out = AQUI.parent / "salidas" / tema
    out.mkdir(parents=True, exist_ok=True)
    im.save(out / "miniatura.jpg", "JPEG", quality=90, optimize=True)
    print(tema, (out / "miniatura.jpg").stat().st_size // 1024, "KB")


hacer("bar", "o0049.jpg", 0.5, 0.55, 1.0, ["ASÍ GANA", "UN BAR"], "0,15 €", "DE CADA CAFÉ CON LECHE")
hacer("taxi", "o0081.jpg", 0.5, 0.6, 1.0, ["UNA LICENCIA", "DE TAXI"], "−40 %", "DE VALOR EN UN SOLO AÑO")
hacer("burger", "o0026.jpg", 0.3, 0.5, 1.0, ["ASÍ GANA UN", "BURGER KING"], "2,6 %", "DE LO QUE ENTRA POR LA CAJA")
hacer("peluqueria", "o0013.jpg", 0.5, 0.5, 1.0, ["ASÍ GANA UNA", "PELUQUERÍA"], "9 €", "DE UN CORTE DE 30 €")
