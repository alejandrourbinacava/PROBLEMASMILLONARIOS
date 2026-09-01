#!/usr/bin/env python3
"""
Estilo VOX: diseno plano, tipografia grande, recortes de papel y datos.

Por que esto resuelve lo que el parallax fotorrealista no resolvia:

  - No hace falta que las imagenes compartan luz. El recorte va sobre color
    plano con marco blanco y sombra: es collage, y el collage ADMITE que
    las piezas vengan de sitios distintos. Ese era el fallo insalvable de
    la biblioteca acumulada.
  - El marco blanco tapa el borde del recorte. Un alfa regular deja de
    importar porque nadie ve el borde real.
  - Casi todo el metraje es tipografia, formas y datos: eso es codigo, no
    imagen generada. No hay problema de resolucion porque no hay pixeles.
  - Nada de profundidad de campo, croma ni coherencia de lugar.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Las fuentes se buscan donde estan, no en una ruta fija de Linux: el
# repo trae las suyas en assets/fonts y la maquina de casa es Windows.
# Sin esto, `ImageFont.truetype` falla y cae a la fuente por defecto de
# Pillow, que es un mapa de bits de 11 px: el titular se ve como un
# vídeo de 1998.
import os as _os

_AQUI = _os.path.dirname(_os.path.abspath(__file__))
_CANDIDATAS = [
    _os.path.join(_AQUI, "..", "assets", "fonts", "{}"),
    "/usr/share/fonts/truetype/google-fonts/{}",
    "C:/Windows/Fonts/{}",
]


def _buscar(*nombres):
    for nom in nombres:
        for patron in _CANDIDATAS:
            ruta = _os.path.normpath(patron.format(nom))
            if _os.path.exists(ruta):
                return ruta
    return nombres[0]


FUENTE = _buscar("Poppins-Black.ttf", "Poppins-Bold.ttf", "Anton-Regular.ttf",
                 "ArchivoBlack-Regular.ttf", "arialbd.ttf")
FUENTE_TXT = _buscar("Poppins-Regular.ttf", "Nunito-Black.ttf",
                     "Quicksand-Bold.ttf", "arial.ttf")

# Paleta corta y aplicada igual en todo el video. La contencion es la mitad
# del estilo: tres colores, no doce.
PALETAS = {
    "vox":     dict(fondo=(247, 244, 236), tinta=(26, 26, 28),
                    acento=(255, 199, 44), apoyo=(216, 66, 48), suave=(228, 223, 210)),
    "nocturno":dict(fondo=(22, 26, 34), tinta=(240, 238, 232),
                    acento=(255, 199, 44), apoyo=(240, 108, 84), suave=(38, 44, 56)),
    "dinero":  dict(fondo=(238, 240, 233), tinta=(24, 32, 26),
                    acento=(52, 168, 110), apoyo=(216, 66, 48), suave=(214, 222, 210)),
}


def f(px, regular=False):
    try:
        return ImageFont.truetype(FUENTE_TXT if regular else FUENTE, px)
    except OSError:
        return ImageFont.load_default()


def _suave(u):
    return 1 - (1 - u) ** 3


def lienzo(W, H, pal, textura=True):
    im = Image.new("RGB", (W, H), pal["fondo"])
    if textura:
        # grano de papel: separa el plano de un PNG exportado sin mas
        r = np.random.default_rng(7).normal(0, 3.4, (H, W, 1))
        im = Image.fromarray(np.clip(np.asarray(im, np.float32) + r, 0, 255)
                             .astype(np.uint8))
    return im


def recorte(im, capa, caja, rot=0, marco=16, sombra=26):
    """
    Foto como recorte de papel: marco blanco, sombra y giro leve.
    El marco es lo que hace que un recorte mediocre pase por intencional.
    """
    x, y, w, h = caja
    foto = capa.convert("RGBA")
    foto.thumbnail((w, h), Image.LANCZOS)
    fw, fh = foto.size
    tarjeta = Image.new("RGBA", (fw + marco * 2, fh + marco * 2), (255, 255, 255, 255))
    tarjeta.paste(foto, (marco, marco), foto)
    if rot:
        tarjeta = tarjeta.rotate(rot, expand=True, resample=Image.BICUBIC)
    sw, sh = tarjeta.size

    if sombra:
        s = Image.new("RGBA", (sw + sombra * 3, sh + sombra * 3), (0, 0, 0, 0))
        s.paste(Image.new("RGBA", tarjeta.size, (0, 0, 0, 90)),
                (sombra, sombra + 6), tarjeta)
        s = s.filter(ImageFilter.GaussianBlur(sombra * 0.6))
        im.paste(s, (int(x - sombra), int(y - sombra)), s)
    im.paste(tarjeta, (int(x), int(y)), tarjeta)
    return im


def subrayado(d, texto, xy, px, pal, u=1.0, alto=0.42):
    """
    Barra de color que barre por detras de la palabra al pronunciarla.
    Es el gesto mas reconocible del estilo y cuesta cuatro lineas.
    """
    fo = f(px)
    an = d.textlength(texto, font=fo)
    x, y = xy
    d.rectangle([x - px * .12, y + px * (1 - alto), x - px * .12 + an * _suave(u) + px * .24,
                 y + px * 1.02], fill=pal["acento"])
    d.text((x, y), texto, font=fo, fill=pal["tinta"])
    return an


def titular(im, lineas, pal, px=118, y0=None, u=1.0, resaltar=None):
    d = ImageDraw.Draw(im)
    W, H = im.size
    y = y0 if y0 is not None else H * 0.30
    for i, ln in enumerate(lineas):
        ui = np.clip((u - i * 0.16) / 0.6, 0, 1)
        dy = (1 - _suave(ui)) * 34
        x = W * 0.08
        for pal_txt in ln.split(" "):
            marcado = pal_txt.startswith("*")
            limpio = pal_txt.replace("*", "")
            cola = ""
            while limpio and limpio[-1] in ".,:;?!":
                cola = limpio[-1] + cola
                limpio = limpio[:-1]
            if marcado:
                an = subrayado(d, limpio, (x, y + dy), px, pal, ui)
                if cola:      # la puntuacion queda FUERA del subrayado
                    fo = f(px)
                    d.text((x + an, y + dy), cola, font=fo, fill=pal["tinta"])
                    an += d.textlength(cola, font=fo)
            else:
                fo = f(px)
                d.text((x, y + dy), limpio + cola, font=fo, fill=pal["tinta"])
                an = d.textlength(limpio + cola, font=fo)
            x += an + px * 0.26
        y += px * 1.16
    return im


def barras(im, items, pal, u=1.0, y0=0.34, destacado=None, sufijo="%"):
    d = ImageDraw.Draw(im)
    W, H = im.size
    x0, ancho = int(W * 0.30), int(W * 0.52)
    alto, hueco = 74, 40
    mx = max(v for _, v in items) or 1
    y = int(H * y0)
    for i, (nom, v) in enumerate(items):
        ui = _suave(np.clip((u - i * 0.16) / 0.62, 0, 1))
        col = pal["apoyo"] if nom == destacado else pal["acento"]
        d.rectangle([x0, y, x0 + ancho, y + alto], fill=pal["suave"])
        d.rectangle([x0, y, x0 + int(ancho * v / mx * ui), y + alto], fill=col)
        fo = f(42, regular=True)
        d.text((x0 - 26 - d.textlength(nom, font=fo), y + 14), nom,
               font=fo, fill=pal["tinta"])
        fv = f(48)
        d.text((x0 + ancho + 26, y + 10),
               f"{v*ui:.1f}".replace(".", ",").rstrip("0").rstrip(",") + sufijo,
               font=fv, fill=col)
        y += alto + hueco
    return im


def cifra(im, valor, pal, sufijo="", pie="", u=1.0, px=260, y=0.34,
          decimales=0):
    d = ImageDraw.Draw(im)
    W, H = im.size
    # con formato entero, un 3,22 se dibujaba como "3" y se perdia
    # justo la cifra que sostiene el episodio
    t = f"{valor*_suave(u):,.{decimales}f}".replace(",", "@").replace(".", ",").replace("@", ".")
    fo = f(px)
    an = d.textlength(t, font=fo)
    x = (W - an) / 2
    d.text((x, H * y), t, font=fo, fill=pal["tinta"])
    if sufijo:
        fs = f(int(px * 0.30))
        d.text((x + an + 16, H * y + px * 0.62), sufijo, font=fs, fill=pal["acento"])
    if pie:
        fp = f(46, regular=True)
        d.text(((W - d.textlength(pie, font=fp)) / 2, H * y + px * 1.16),
               pie, font=fp, fill=pal["tinta"])
    return im


def etiqueta(im, texto, pal, xy, px=38):
    """Pildora de color: capitulo, fecha, fuente."""
    d = ImageDraw.Draw(im)
    fo = f(px)
    an = d.textlength(texto, font=fo)
    x, y = xy
    d.rounded_rectangle([x, y, x + an + px * 1.0, y + px * 1.7], px * 0.85,
                        fill=pal["acento"])
    d.text((x + px * 0.5, y + px * 0.32), texto, font=fo, fill=pal["tinta"])
    return im


def stutter(f_idx, fps_objetivo=12, fps=25):
    """
    Congelado a 12 fps sobre 25. Es el 'stutter' de Vox: la animacion no va
    fluida, va a saltos, y eso es lo que la hace parecer dibujada a mano.
    Devuelve el indice de fotograma que hay que calcular.
    """
    paso = max(1, round(fps / fps_objetivo))
    return (f_idx // paso) * paso


# ---------------------------------------------------------------------------
# TRATAMIENTO DE RECORTES
# Esto es lo que resuelve de verdad "las capas no pegan entre si". No es
# generarlas juntas: es pasarlas todas por el mismo filtro grafico. Dos
# fotos con luces distintas, convertidas a semitono en blanco y negro,
# dejan de tener luz propia y pasan a ser el mismo material.
# ---------------------------------------------------------------------------

def semitono(im, celda=5.0, angulo=15.0, contraste=1.15, gamma=0.95):
    """
    Convierte a blanco y negro con trama de puntos de imprenta.
    Conserva el alfa. Es el aspecto de recorte de periodico de Vox.
    """
    im = im.convert("RGBA")
    a = np.asarray(im, np.float32)
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    lum = np.clip(((lum / 255.0) ** gamma - 0.5) * contraste + 0.5, 0, 1)

    H, W = lum.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = math.radians(angulo)
    u = (xx * math.cos(t) + yy * math.sin(t)) * (math.pi / celda)
    v = (-xx * math.sin(t) + yy * math.cos(t)) * (math.pi / celda)
    trama = (np.sin(u) * np.sin(v) + 1.0) * 0.5

    punto = np.clip((lum - trama) * 6.0 + 0.5, 0, 1)
    # se mezcla algo de luminancia real para no perder los medios tonos
    gris = np.clip(punto * 0.78 + lum * 0.22, 0, 1) * 255
    return Image.fromarray(
        np.dstack([gris, gris, gris, a[..., 3]]).astype(np.uint8), "RGBA")


def trazo(im, color=(224, 67, 41), dx=-16, dy=10, grosor=9):
    """
    Silueta desplazada detras del recorte, como un rotulador mal alineado.
    Hace dos cosas a la vez: da el relieve caracteristico y TAPA el borde
    del recorte. Un alfa mediocre deja de verse porque nadie mira el borde.
    """
    im = im.convert("RGBA")
    al = im.getchannel("A")
    silueta = al.point(lambda v: 255 if v > 110 else 0)
    if grosor:
        silueta = silueta.filter(ImageFilter.MaxFilter(2 * (grosor // 2) + 1))
    W, H = im.size
    m = abs(dx) + abs(dy) + grosor * 2
    fuera = Image.new("RGBA", (W + m * 2, H + m * 2), (0, 0, 0, 0))
    tinta = Image.new("RGBA", im.size, tuple(color) + (255,))
    fuera.paste(tinta, (m + dx, m + dy), silueta)
    fuera.paste(im, (m, m), im)
    return fuera.crop(fuera.getbbox() or (0, 0, W, H))


def papel(W, H, pal, celda=132, lineas=True):
    """
    Fondo BLOQUEADO: el mismo en todas las escenas del episodio.
    Es la decision que mas hace por la coherencia. Como no cambia nunca,
    el video se lee como una sola toma continua sobre la que van entrando
    cosas, en vez de como 200 planos distintos.
    """
    rng = np.random.default_rng(11)
    base = np.full((H, W, 3), pal["fondo"], np.float32)
    base += rng.normal(0, 5.2, (H, W, 1))
    manchas = rng.normal(0, 1, (H // 24 + 1, W // 24 + 1, 1)).astype(np.float32)
    manchas = np.asarray(Image.fromarray(
        np.clip(manchas * 40 + 128, 0, 255).astype(np.uint8)[..., 0]
    ).resize((W, H), Image.BICUBIC), np.float32)[..., None]
    base += (manchas - 128) * 0.10
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    if lineas:
        d = ImageDraw.Draw(im, "RGBA")
        c = tuple(int(v * 0.93) for v in pal["fondo"]) + (150,)
        for x in range(0, W, celda):
            d.line([(x, 0), (x, H)], fill=c, width=2)
        for y in range(0, H, celda):
            d.line([(0, y), (W, y)], fill=c, width=2)
    return im
