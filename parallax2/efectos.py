#!/usr/bin/env python3
"""
Capa de acabado: gradacion de color, efectos de pantalla, texto y
animaciones de entrada/salida de capa.

Todo procedural. No hace falta descargar ni un solo asset de particulas:
las brasas, el polvo y los destellos se calculan, asi que son deterministas
(misma semilla, mismo resultado) y se reanudan igual tras un corte.
"""
import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

import iconos as ICO

import os as _os

# Donde viven las fuentes. El repo trae las suyas en assets/fonts y esa es
# la unica ruta que existe en las tres maquinas: Windows, el runner de
# GitHub y cualquier portatil. Las otras dos quedan de respaldo.
_AQUI = _os.path.dirname(_os.path.abspath(__file__))
_RUTAS = [
    _os.path.join(_AQUI, "..", "assets", "fonts", "{}"),
    "/usr/share/fonts/truetype/google-fonts/{}",
    "/usr/share/fonts/truetype/liberation/{}",
    "C:/Windows/Fonts/{}",
]


def _busca(*nombres):
    for nom in nombres:
        for patron in _RUTAS:
            ruta = _os.path.normpath(patron.format(nom))
            if _os.path.exists(ruta):
                return ruta
    return None


# Cuatro pesos de la misma familia. La jerarquia de un grafico no se hace
# con colores ni con cajas: se hace con el peso y el tamano de la letra.
#
#   NEGRA    las cifras. Es el contenido.
#   FUERTE   los importes de una lista y los nombres de las cajas.
#   MEDIA    las etiquetas, los pies y los conceptos.
#
# Poppins Medium sobre Poppins Black es un salto de cuatro pesos: se lee
# como dos niveles distintos de informacion incluso a 480 px de alto.
NEGRA  = _busca("Poppins-Black.ttf", "Poppins-Bold.ttf", "ArchivoBlack-Regular.ttf",
                "LiberationSans-Bold.ttf", "arialbd.ttf")
FUERTE = _busca("Poppins-SemiBold.ttf", "Poppins-Bold.ttf", "Nunito-Black.ttf",
                "LiberationSans-Bold.ttf", "arialbd.ttf")
MEDIA  = _busca("Poppins-Medium.ttf", "Poppins-Regular.ttf", "Quicksand-Bold.ttf",
                "LiberationSans-Regular.ttf", "arial.ttf")
FUENTES = [f for f in (NEGRA, FUERTE, MEDIA) if f]

# ---------------------------------------------------------------------------
# GRADACION DE COLOR
# Cada entrada es (sombras RGB, altas RGB, contraste, saturacion, elevacion).
# El "toque premium" es casi todo esto: sombras tenidas de un color y luces
# del complementario. Se elige por capitulo, no por escena.
# ---------------------------------------------------------------------------
GRADES = {
    "neutro":         ((0, 0, 0),      (0, 0, 0),       1.00, 1.00, 0.000),
    "dorado_noche":   ((-8, -2, 26),   (24, 12, -14),   1.14, 1.06, 0.010),
    "frio_institucional": ((-4, 2, 20), (6, 8, 14),     1.10, 0.82, 0.014),
    "verde_dinero":   ((-10, 4, -6),   (18, 20, -6),    1.12, 0.94, 0.008),
    # Los de arriba estan calibrados para arte generado oscuro. Sobre
    # metraje con manos y caras dejan la piel verde: la tinta de sombras
    # mas la de luces empujan el canal verde justo donde vive el tono de
    # piel. Estos son la version para METRAJE: la tinta va solo a las
    # luces y flojo, asi que la piel no se mueve.
    "verde_suave":    ((-4, 0, -2),    (6, 14, -4),     1.08, 0.98, 0.006),
    "dorado_suave":   ((-4, -1, 12),   (14, 8, -8),     1.08, 1.02, 0.008),
    "frio_suave":     ((-2, 1, 10),    (4, 6, 10),      1.06, 0.90, 0.010),
    "rojo_suave":     ((6, -3, -2),    (16, 2, -6),     1.10, 1.00, 0.005),
    "acero_suave":    ((-3, -1, 8),    (3, 6, 10),      1.08, 0.86, 0.005),
    "rojo_alerta":    ((10, -6, -4),   (26, 4, -10),    1.18, 1.02, 0.006),
    "sepia_archivo":  ((6, 0, -10),    (22, 14, -18),   1.06, 0.62, 0.020),
    "acero":          ((-6, -2, 14),   (4, 10, 18),     1.16, 0.74, 0.006),
}


def gradar(arr, nombre):
    """arr float32 HxWx3 en 0..255."""
    if nombre == "neutro" or nombre not in GRADES:
        return arr
    som, alt, contraste, sat, lift = GRADES[nombre]
    x = arr / 255.0
    peso_s = (1.0 - x) ** 2
    peso_a = x ** 2
    x = x + peso_s * (np.array(som, np.float32) / 255.0) \
          + peso_a * (np.array(alt, np.float32) / 255.0)
    x = (x - 0.5) * contraste + 0.5
    if sat != 1.0:
        gris = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        x = gris[..., None] + (x - gris[..., None]) * sat
    x = x * (1.0 - lift) + lift
    return np.clip(x, 0, 1) * 255.0


# Duotonos del canal. Un clip de stock se reconoce como stock por su color:
# viene de una libreria y trae la luz que trajo. El duotono lo lleva entero a
# dos tintas -las del canal- y a partir de ahi todo el metraje del episodio
# parece de la misma pieza, aunque venga de doce sitios distintos. Es la
# diferencia entre "clip de banco de imagenes" y "plano del canal".
#
# La fuerza importa: al 100% deja de leerse como metraje y parece un filtro.
# Entre 0,45 y 0,7 se nota el color y se sigue viendo lo que pasa.
DUOTONOS = {
    "duo_ambar": ((10, 16, 30),   (255, 205, 140)),
    "duo_frio":  ((8, 14, 28),    (196, 216, 240)),
    "duo_rojo":  ((16, 10, 18),   (255, 176, 150)),
    "duo_papel": ((12, 14, 22),   (237, 231, 218)),
    "duo_verde": ((8, 16, 18),    (176, 226, 196)),
}


def duotono(arr, nombre, fuerza=0.6):
    """Lleva la imagen a dos tintas: la sombra y la alta del canal.

    Se mezcla con el original en vez de sustituirlo, porque un duotono puro
    borra las caras y los objetos dejan de reconocerse. `fuerza` es cuanto
    manda el duotono sobre el color real.
    """
    if not nombre or nombre not in DUOTONOS:
        return arr
    som, alt = (np.array(c, np.float32) for c in DUOTONOS[nombre])
    x = arr / 255.0
    # luminancia perceptual, no la media: con la media el rojo y el azul
    # acaban en el mismo gris y el duotono aplana la imagen
    lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    # un poco de curva: sube las medias para que no quede todo en la sombra
    lum = np.clip(lum, 0, 1) ** 0.85
    duo = som + (alt - som) * lum
    return np.clip(arr * (1.0 - fuerza) + duo * fuerza, 0, 255)


# ---------------------------------------------------------------------------
# EFECTOS DE PANTALLA (particulas y overlays)
# ---------------------------------------------------------------------------
# `vy` negativo sube, positivo baja. `dx` es el vaiven lateral (una sinusoide)
# y `deriva` el arrastre lateral constante, que es lo que hace que algo cruce
# el plano en vez de temblar en el sitio.
#
# Cuidado con el reparto de direcciones: cuatro de los seis efectos originales
# subian, y un capitulo entero podia salir con TODO flotando hacia arriba. Un
# episodio necesita cosas que caigan, cosas que crucen y cosas que ni se
# muevan, o el aire del video siempre es el mismo.
PARTICULAS = {
    #                  n     vel_y    vaiven  deriva  radio  color              brillo
    "brasas":   dict(n=90,  vy=-0.055, dx=0.012, r=2.6,  col=(255, 150, 45),  a=0.85),
    "polvo":    dict(n=150, vy=-0.010, dx=0.006, r=1.7,  col=(230, 220, 200), a=0.40),
    "ceniza":   dict(n=110, vy= 0.030, dx=0.010, r=2.1,  col=(190, 190, 195), a=0.35),
    "bokeh":    dict(n=26,  vy=-0.018, dx=0.008, r=16.0, col=(255, 214, 150), a=0.22),
    "chispas":  dict(n=60,  vy=-0.090, dx=0.020, r=1.9,  col=(255, 230, 170), a=0.90),
    "billetes": dict(n=40,  vy= 0.050, dx=0.016, r=4.5,  col=(180, 220, 170), a=0.30),

    # --- los que NO son puntitos subiendo ---
    # niebla: masas grandes y blandas que CRUZAN el plano de lado.
    "niebla":   dict(n=13,  vy=-0.004, dx=0.004, deriva=0.055, r=110.0,
                     col=(140, 160, 195), a=0.13),
    # humo: mas denso y mas lento, casi quieto, para interiores cargados.
    "humo":     dict(n=9,   vy=-0.012, dx=0.003, deriva=0.018, r=150.0,
                     col=(150, 135, 120), a=0.10),
    # lluvia: rayas rapidas hacia ABAJO y en diagonal.
    "lluvia":   dict(n=150, vy= 0.62,  dx=0.004, deriva=0.09, r=1.2,
                     col=(175, 200, 235), a=0.30, forma="raya", largo=30),
    # destellos: no se desplazan, PARPADEAN. Rompen el patron de deriva.
    "destellos":dict(n=22,  vy= 0.0,   dx=0.002, r=4.5,
                     col=(255, 238, 200), a=0.75, parpadeo=True),
}


class Particulas:
    """
    Sistema de particulas con posiciones precalculadas. Se dibuja sumando
    (modo pantalla), asi que nunca oscurece la imagen: solo anade luz.
    """

    def __init__(self, tipo, W, H, semilla=0):
        p = PARTICULAS[tipo]
        rng = np.random.default_rng(abs(hash((tipo, semilla))) % (2 ** 32))
        self.p = p
        self.W, self.H = W, H
        n = p["n"]
        self.x0 = rng.random(n)
        self.y0 = rng.random(n)
        self.fase = rng.random(n) * 6.283
        self.vel = 0.6 + rng.random(n) * 0.9
        self.tam = 0.5 + rng.random(n) * 1.2
        self.brillo = 0.4 + rng.random(n) * 0.6

    def dibujar(self, t):
        p, W, H = self.p, self.W, self.H
        x = (self.x0
             + p["dx"] * self.vel * np.sin(self.fase + t * 2.1)
             + p.get("deriva", 0.0) * self.vel * t) % 1.0
        y = (self.y0 + p["vy"] * self.vel * t * 10.0) % 1.0
        r = p["r"] * self.tam
        brillo = self.brillo
        if p.get("parpadeo"):
            # no se mueven: aparecen y se apagan. Es la unica forma de
            # atmosfera que no arrastra la mirada en una direccion.
            brillo = brillo * (0.15 + 0.85 * np.clip(
                np.sin(self.fase + t * 3.4), 0, 1) ** 3)
        capa = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(capa)
        largo = p.get("largo", 0)
        for xi, yi, ri, bi in zip(x * W, y * H, r, brillo):
            v = int(255 * bi * p["a"])
            if v <= 0:
                continue
            if largo:
                # raya en la direccion del movimiento: es lo que convierte
                # un punto que cae en una gota de lluvia
                dxr = p.get("deriva", 0.0) * largo * 8
                d.line([xi - dxr, yi - largo, xi, yi],
                       fill=v, width=max(1, int(ri)))
            else:
                d.ellipse([xi - ri, yi - ri, xi + ri, yi + ri], fill=v)
        capa = capa.filter(ImageFilter.GaussianBlur(max(1.0, p["r"] * 0.45)))
        m = np.asarray(capa, np.float32)[..., None] / 255.0
        return m * np.array(p["col"], np.float32)


def fuga_luz(W, H, t, fuerza=0.18, color=(255, 170, 90)):
    """Light leak: una franja calida que barre el encuadre. Muy usado."""
    xx = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    centro = -0.25 + 1.5 * ((t * 0.35) % 1.0)
    banda = np.exp(-((xx - centro) ** 2) / 0.012)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    banda = banda * (0.4 + 0.6 * yy)
    return (banda[..., None] * np.array(color, np.float32) * fuerza)


def aberracion(img, px=1.6):
    """Desplaza R y B en sentidos opuestos. En dosis minima, sabe a cine."""
    a = np.asarray(img, np.float32)
    d = int(round(px))
    if d < 1:
        return a
    out = a.copy()
    out[:, d:, 0] = a[:, :-d, 0]
    out[:, :-d, 2] = a[:, d:, 2]
    return out


def halo(arr, fuerza=0.25, umbral=185, radio=30):
    """Bloom sobre las altas luces."""
    if fuerza <= 0:
        return arr
    h, w = arr.shape[:2]
    peq = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize(
        (w // 4, h // 4), Image.BILINEAR)
    s = np.asarray(peq, np.float32)
    s = np.clip(s - umbral, 0, None) * (255.0 / max(1, 255 - umbral))
    g = Image.fromarray(s.astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radio / 4)).resize((w, h), Image.BILINEAR)
    return 255 - (255 - arr) * (255 - np.asarray(g, np.float32) * fuerza) / 255.0


# ---------------------------------------------------------------------------
# ANIMACION DE ENTRADA / SALIDA DE CAPA
# ---------------------------------------------------------------------------
ENTRADAS = ("fundido", "sube", "baja", "izquierda", "derecha", "escala",
            "escala_atras", "desenfoque", "golpe", "latigo_izq", "latigo_der",
            "rebote", "desplome", "ninguna")


def _suave(u):
    return 1 - (1 - u) ** 3           # ease-out cubico


def _atras(u, k=2.2):
    """Ease-out con rebasamiento: pasa de largo y vuelve. Es lo que da la
    sensacion de golpe; sin esto una entrada se lee como estatica."""
    u = u - 1.0
    return u * u * ((k + 1) * u + k) + 1.0


def _rebote(u):
    if u < 4 / 11:
        return (121 * u * u) / 16
    if u < 8 / 11:
        u -= 6 / 11;  return 4.0 / 3 * u * u + 0.75
    if u < 9 / 10:
        u -= 0.85;    return 3.0 * u * u + 0.9375
    u -= 0.96;        return 12.0 * u * u + 0.9843


def anim_capa(tipo, u, W, H, saliendo=False):
    """
    Devuelve (dx, dy, escala, opacidad, desenfoque) para u en 0..1, donde
    u=0 es el instante mas lejano del reposo y u=1 el reposo.
    Las entradas "duras" (golpe, latigo, rebote, desplome) rebasan el
    reposo y vuelven: es lo que separa una entrada viva de un fundido.
    """
    if tipo in (None, "ninguna"):
        return 0.0, 0.0, 1.0, 1.0, 0.0
    u = float(np.clip(u, 0, 1))
    e = _suave(u)
    s = -1.0 if saliendo else 1.0
    op_rapida = min(1.0, u * 2.6)          # el alfa sube antes que el movimiento

    if tipo == "fundido":
        return 0, 0, 1.0, e, 0.0
    if tipo == "sube":
        return 0, (1 - e) * H * 0.10 * s, 1.0, e, 0.0
    if tipo == "baja":
        return 0, -(1 - e) * H * 0.10 * s, 1.0, e, 0.0
    if tipo == "izquierda":
        return (1 - e) * W * 0.13 * s, 0, 1.0, e, 0.0
    if tipo == "derecha":
        return -(1 - e) * W * 0.13 * s, 0, 1.0, e, 0.0
    if tipo == "escala":
        return 0, 0, 1.0 + (1 - e) * 0.14, e, 0.0
    if tipo == "escala_atras":
        return 0, 0, 1.0 - (1 - e) * 0.12, e, 0.0
    if tipo == "desenfoque":
        return 0, 0, 1.0 + (1 - e) * 0.03, e, (1 - e) * 14.0

    # --- entradas duras ---
    if tipo == "golpe":
        a = _atras(u)
        return 0, 0, 1.0 + (1 - a) * 0.30, op_rapida, (1 - min(1, u * 3)) * 9
    if tipo in ("latigo_izq", "latigo_der"):
        d = -1.0 if tipo == "latigo_izq" else 1.0
        a = _atras(u, 1.6)
        return d * (1 - a) * W * 0.42 * s, 0, 1.0, op_rapida, \
               (1 - min(1, u * 2.2)) * 26
    if tipo == "rebote":
        return 0, -(1 - _rebote(u)) * H * 0.22 * s, 1.0, op_rapida, 0.0
    if tipo == "desplome":
        a = _atras(u, 1.4)
        return 0, -(1 - a) * H * 0.30 * s, 1.0 + (1 - a) * 0.06, op_rapida, \
               (1 - min(1, u * 2.6)) * 12
    return 0.0, 0.0, 1.0, 1.0, 0.0


def factor_anim(f, n, fps, dur_ent, dur_sal, retardo=0.0):
    """
    Devuelve (u_entrada, u_salida) del fotograma f.
    `retardo` escalona las capas: el fondo entra primero, el sujeto despues
    y el primer plano el ultimo. Que no entren a la vez es la mitad del
    efecto; entrando juntas se lee como una sola imagen apareciendo.
    """
    ne = max(1, int(dur_ent * fps))
    ns = max(1, int(dur_sal * fps))
    f0 = int(retardo * fps)
    ue = min(1.0, max(0.0, (f - f0) / ne)) if dur_ent > 0 else 1.0
    us = min(1.0, (n - 1 - f) / ns) if dur_sal > 0 else 1.0
    return ue, us


# ---------------------------------------------------------------------------
# TEXTO EN PANTALLA
# ---------------------------------------------------------------------------
import functools as _ft


@_ft.lru_cache(maxsize=256)
def _fuente(px, peso="negra"):
    """La fuente del canal al peso que se pida, cacheada.

    Cacheada porque los graficos se dibujan fotograma a fotograma y abrir
    el mismo TTF veinticinco veces por segundo durante catorce minutos es
    trabajo tirado.
    """
    for ruta in ({"negra": NEGRA, "fuerte": FUERTE, "media": MEDIA}.get(peso),
                 NEGRA, FUERTE, MEDIA):
        if not ruta:
            continue
        try:
            return ImageFont.truetype(ruta, px)
        except OSError:
            continue
    try:
        return ImageFont.load_default(px)      # Pillow >= 10.1: escalable
    except TypeError:
        return ImageFont.load_default()


def render_texto(txt, W, H, px=132, color=(255, 255, 255),
                 acento=None, pos=("center", 0.5)):
    """
    Dibuja el texto una sola vez en una RGBA del tamano del lienzo. Luego se
    anima moviendo esa imagen, que es mucho mas barato que redibujar.
    Las palabras entre *asteriscos* van en color de acento.
    """
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    f = _fuente(px)
    partes, act, en_acento = [], "", False
    for ch in txt:
        if ch == "*":
            if act:
                partes.append((act, en_acento)); act = ""
            en_acento = not en_acento
        else:
            act += ch
    if act:
        partes.append((act, en_acento))

    # EL ROTULO ENCOGE HASTA CABER.
    #
    # Antes el tamano era fijo y el que escribia el rotulo tenia que
    # adivinar cuantos caracteres caben: por eso `rotulo_de` cortaba a
    # treinta y "Ese es el precio de ser el dueno" -la ultima frase del
    # episodio del hotel- salia como "Ese es el precio de ser". Es el mismo
    # fallo que la etiqueta de la barra que salia como "oteles con su
    # nombre": medir despues en vez de suponer antes.
    ancho = sum(d.textlength(p, font=f) for p, _ in partes)
    while ancho > W * 0.86 and px > 56:
        px = int(px * 0.94)
        f = _fuente(px)
        ancho = sum(d.textlength(p, font=f) for p, _ in partes)
    alto = px * 1.25
    ax, ay = pos
    x = (W - ancho) / 2 if ax == "center" else (
        W * 0.09 if ax == "left" else W * 0.91 - ancho)
    y = ay * H - alto / 2

    # Un rotulo sobre metraje real no se lee con una sombra dura: el fondo se
    # mueve y tiene detalle en todas las frecuencias. Lo que lo separa es un
    # HALO oscuro y difuso alrededor -el "scrim" de television- y encima la
    # sombra de siempre. Sobre arte generado sobraba; sobre video no.
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dh = ImageDraw.Draw(halo)
    xh = x
    for parte, _ in partes:
        dh.text((xh, y), parte, font=f, fill=(0, 0, 0, 210))
        xh += dh.textlength(parte, font=f)
    halo = halo.filter(ImageFilter.GaussianBlur(px * 0.22))
    capa = Image.alpha_composite(capa, halo)
    capa = Image.alpha_composite(capa, halo)      # dos pasadas: mas denso
    d = ImageDraw.Draw(capa)

    for parte, es_ac in partes:
        col = acento if (es_ac and acento) else color
        d.text((x + 3, y + 4), parte, font=f, fill=(0, 0, 0, 170))
        d.text((x, y), parte, font=f, fill=tuple(col) + (255,))
        x += d.textlength(parte, font=f)
    return capa


def compon_texto(arr, capa_txt, u_ent, u_sal, estilo, W, H):
    """Anima la capa de texto ya dibujada sobre el fotograma."""
    dx, dy, esc, op, _ = anim_capa(estilo, u_ent, W, H)
    dx2, dy2, esc2, op2, _ = anim_capa(estilo, u_sal, W, H, saliendo=True)
    dx += dx2; dy += dy2; esc *= esc2; op *= op2
    if op <= 0.01:
        return arr
    if abs(esc - 1.0) > 1e-3 or abs(dx) > 0.5 or abs(dy) > 0.5:
        nw, nh = int(W * esc), int(H * esc)
        capa_txt = capa_txt.resize((nw, nh), Image.BICUBIC)
        lienzo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lienzo.paste(capa_txt, (int(dx - (nw - W) / 2), int(dy - (nh - H) / 2)))
        capa_txt = lienzo
    t = np.asarray(capa_txt, np.float32)
    a = (t[..., 3:4] / 255.0) * op
    return arr * (1 - a) + t[..., :3] * a


# ---------------------------------------------------------------------------
# MOTION GRAPHICS
# Para las escenas de cifras. Se dibujan por fotograma (a diferencia del
# texto, que se precalcula) porque el numero cuenta y las barras crecen.
# Rompen la monotonia: sin esto las 200 escenas son todas el mismo recurso.
# ---------------------------------------------------------------------------
# La paleta del canal, y solo esta. Tres colores de tinta y dos de papel.
# Un grafico premium no tiene mas colores que uno cutre: tiene MENOS, y los
# usa siempre para lo mismo. El ambar es la cifra de la que habla la frase,
# el rojo es lo que te quitan y el hueso es todo lo demas.
PALETA = {
    "acento":  (255, 196, 90),
    "aviso":   (255, 110, 86),
    "ok":      (120, 220, 170),
    "hueso":   (242, 238, 230),
    # El gris de las etiquetas. Antes las etiquetas iban en hueso al 90%,
    # o sea casi en blanco: competian con la cifra. Un gris azulado a media
    # luz las pone un escalon por debajo, que es donde tienen que estar.
    "tenue":   (154, 162, 182),
    "carta":   (22, 29, 45),
    "base":    (11, 15, 25),
    "surco":   (255, 255, 255, 30),
}

# Contorno muy simplificado de la Espana peninsular, en (longitud, latitud).
# No pretende ser cartografia: pretende que se reconozca de un vistazo a
# 1920 de ancho y durante cuatro segundos. Portugal queda fuera a proposito,
# que es lo que hace la silueta reconocible.
ESPANA = [
    # cornisa cantabrica, de Finisterre a Irun
    (-9.30, 43.05), (-8.90, 43.38), (-8.20, 43.66), (-7.30, 43.78),
    (-6.50, 43.66), (-5.80, 43.63), (-4.80, 43.50), (-4.00, 43.48),
    (-3.20, 43.47), (-2.50, 43.45), (-1.95, 43.38), (-1.75, 43.32),
    # Pirineos
    (-1.30, 43.05), (-0.70, 42.87), (0.20, 42.72), (0.70, 42.72),
    (1.45, 42.60), (1.95, 42.45), (2.65, 42.35), (3.20, 42.32),
    # Mediterraneo, de Cap de Creus a Tarifa
    (3.10, 41.90), (2.20, 41.40), (1.20, 41.10), (0.85, 40.72),
    (0.20, 40.10), (0.00, 39.85), (-0.25, 39.45), (-0.20, 38.90),
    (-0.50, 38.35), (-0.75, 37.85), (-0.95, 37.58), (-1.65, 37.35),
    (-1.95, 36.83), (-2.60, 36.72), (-3.60, 36.72), (-4.42, 36.72),
    (-5.15, 36.42), (-5.36, 36.15),
    # golfo de Cadiz
    (-5.60, 36.20), (-6.05, 36.35), (-6.35, 36.65), (-6.90, 37.20),
    (-7.40, 37.18),
    # raya de Portugal, subiendo
    (-7.45, 37.55), (-7.30, 38.00), (-7.05, 38.20), (-7.10, 38.80),
    (-6.95, 39.10), (-7.35, 39.48), (-7.55, 39.68), (-7.00, 40.25),
    (-6.85, 41.03), (-6.20, 41.58), (-6.55, 41.88), (-7.15, 41.95),
    (-8.20, 41.90), (-8.65, 42.05),
    # rias baixas
    (-8.85, 42.30), (-8.75, 42.60), (-9.05, 42.75), (-8.85, 42.95),
]


def _fmt(v, dec=0, mil="."):
    e = f"{v:,.{dec}f}".replace(",", "\x00").replace(".", ",").replace("\x00", mil)
    return e if dec else e.split(",")[0]


# ---------------------------------------------------------------------------
# PRIMITIVAS DE DISENO
#
# Todos los graficos del canal se dibujan con estas cuatro cosas, y por eso
# parecen de la misma familia aunque uno sea un mapa y otro una factura:
# la misma tarjeta, el mismo galon de acento, la misma barra y el mismo
# entreletrado en las etiquetas.
# ---------------------------------------------------------------------------
_MARGEN = 56          # aire alrededor de la tarjeta para que quepa la sombra


@_ft.lru_cache(maxsize=64)
def _carta(w, h, radio=30, acento=None, alpha=236):
    """Una tarjeta de datos: sombra, degradado, filo de luz y galon.

    Lo que separa un grafico de television de un rotulo de programador es
    que el rotulo es un rectangulo plano de color y la tarjeta tiene CUERPO:
    una sombra que la despega del metraje, un degradado vertical que le da
    volumen y un filo claro arriba que simula el canto iluminado.

    Va cacheada porque no depende de la animacion -solo del tamano- y se
    pediria veinticinco veces por segundo. Sin la cache, el desenfoque
    gaussiano de la sombra se comeria el render.
    """
    m = _MARGEN
    W_, H_ = w + m * 2, h + m * 2
    img = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))

    # 1. la sombra, que es lo que la despega del fondo
    mascara = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [m, m + 18, m + w, m + h + 18], radio, fill=170)
    mascara = mascara.filter(ImageFilter.GaussianBlur(26))
    sombra = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    sombra.putalpha(mascara)
    img = Image.alpha_composite(img, sombra)

    # 2. el cuerpo, con degradado vertical
    rampa = np.linspace(1.16, 0.74, h, dtype=np.float32)[:, None, None]
    cuerpo = np.clip(np.array(PALETA["carta"], np.float32)[None, None, :] * rampa,
                     0, 255)
    cuerpo = np.repeat(cuerpo, w, axis=1).astype(np.uint8)
    tarjeta = Image.fromarray(cuerpo, "RGB").convert("RGBA")
    mc = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mc).rounded_rectangle([0, 0, w - 1, h - 1], radio, fill=alpha)
    tarjeta.putalpha(mc)
    img.alpha_composite(tarjeta, (m, m))

    d = ImageDraw.Draw(img)
    # 3. el filo de luz del canto superior y el contorno de un pixel
    d.rounded_rectangle([m, m, m + w - 1, m + h - 1], radio,
                        outline=(255, 255, 255, 26), width=2)
    d.line([m + radio, m + 1, m + w - radio, m + 1], fill=(255, 255, 255, 54),
           width=2)
    # 4. el galon de acento en el canto izquierdo: la firma del canal
    if acento:
        d.rounded_rectangle([m + 1, m + radio - 4, m + 7, m + h - radio + 4],
                            3, fill=tuple(acento) + (235,))
    return img


def _pon(capa, carta, x, y):
    """Pega una tarjeta ya dibujada con su esquina util en (x, y)."""
    capa.alpha_composite(carta, (int(x) - _MARGEN, int(y) - _MARGEN))


def _ancho_esp(d, txt, font, esp=0):
    return sum(d.textlength(c, font=font) for c in txt) + esp * max(0, len(txt) - 1)


def _esp(d, xy, txt, font, fill, esp=4, anchor="ls"):
    """Texto con entreletrado. PIL no tiene tracking y hay que abrirlo a mano.

    Las mayusculas pegadas se leen como un bloque; abiertas cuatro pixeles
    se leen como un epigrafe. Es el detalle que mas dice "esto lo ha hecho
    alguien" y cuesta seis lineas.
    """
    x, y = xy
    for c in txt:
        d.text((x, y), c, font=font, fill=fill, anchor=anchor)
        x += d.textlength(c, font=font) + esp


def _barra(capa, caja, col, radio=None, brillo=0.20):
    """Una barra con volumen: clara arriba, oscura abajo, cantos redondos."""
    x0, y0, x1, y1 = (int(v) for v in caja)
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    if radio is None:
        radio = min(h // 2, 18)
    rampa = np.linspace(1.0 + brillo, 1.0 - brillo * 0.7, h,
                        dtype=np.float32)[:, None, None]
    cuerpo = np.clip(np.array(col, np.float32)[None, None, :] * rampa, 0, 255)
    img = Image.fromarray(np.repeat(cuerpo, w, axis=1).astype(np.uint8),
                          "RGB").convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radio, fill=248)
    img.putalpha(mask)
    capa.alpha_composite(img, (x0, y0))


def _surco(d, caja, radio=None):
    x0, y0, x1, y1 = (int(v) for v in caja)
    if radio is None:
        radio = min((y1 - y0) // 2, 18)
    d.rounded_rectangle([x0, y0, x1, y1], radio, fill=(255, 255, 255, 24))
    d.rounded_rectangle([x0, y0, x1, y1], radio, outline=(255, 255, 255, 30),
                        width=1)


def _epigrafe(capa, d, x, y, ancho, txt, color=None):
    """Epigrafe en versalitas mas la regla que llega hasta el borde.

    El texto no llena la tarjeta, asi que sin la regla queda un hueco raro a
    la derecha. La regla lo cierra y ademas marca la cabecera: es la misma
    solucion de una portada de informe.
    """
    color = color or PALETA["acento"]
    f = _fuente(29, "media")
    txt = txt.upper()
    an = _ancho_esp(d, txt, f, 5)
    _esp(d, (x, y), txt, f, tuple(color) + (215,), 5)
    if an + 28 < ancho:
        d.line([x + an + 20, y - 10, x + ancho, y - 10],
               fill=(255, 255, 255, 30), width=2)


def _panel(d, caja, radio=18, alpha=104):
    """Compatibilidad: queda para no romper llamadas viejas."""
    d.rounded_rectangle(caja, radio, fill=(8, 12, 22, alpha))


def grafico(spec, W, H, u, ancla=0.5):
    """
    u va de 0 a 1 a lo largo de la animacion del grafico.
    Devuelve una RGBA del tamano del lienzo lista para componer.
    """
    tipo = spec.get("tipo", "contador")
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    e = _suave(float(np.clip(u, 0, 1)))
    ac = tuple(spec.get("color", PALETA["acento"]))
    cy = int(spec.get("y", ancla) * H)

    if tipo == "contador":
        val = spec["valor"] * e
        px = spec.get("px", 190)
        f = _fuente(px, "negra")
        fs = _fuente(int(px * 0.32), "media")
        txt = spec.get("prefijo", "") + _fmt(val, spec.get("dec", 0))
        sub = spec.get("sufijo", "")
        an = d.textlength(txt, font=f)
        hueco = int(px * 0.11) if sub else 0
        ans = d.textlength(sub, font=fs) if sub else 0
        pie = spec.get("pie", "")
        fp = _fuente(40, "media")
        ap = _ancho_esp(d, pie.upper(), fp, 4) if pie else 0

        ancho = int(max(an + hueco + ans, ap) + 170)
        alto = int(px * 0.92) + 96 + (76 if pie else 0)
        x0, y0 = (W - ancho) // 2, cy - alto // 2
        _pon(capa, _carta(ancho, alto, 32, ac), x0, y0)

        # La cifra y su unidad comparten LINEA DE BASE. Antes el sufijo se
        # colocaba por su borde superior y "€ por litro" flotaba a media
        # altura del cero: se leia como dos rotulos distintos pegados.
        base = y0 + 62 + int(px * 0.70)
        x = (W - (an + hueco + ans)) / 2
        d.text((x + 3, base + 4), txt, font=f, fill=(0, 0, 0, 120), anchor="ls")
        d.text((x, base), txt, font=f, fill=ac + (255,), anchor="ls")
        if sub:
            d.text((x + an + hueco, base), sub, font=fs,
                   fill=PALETA["hueso"] + (235,), anchor="ls")
        # subrayado que crece con la cifra: la cifra no aparece, LLEGA
        d.rounded_rectangle([x, base + 20, x + max(4, int((an + hueco + ans) * e)),
                             base + 26], 3, fill=ac + (190,))
        if pie:
            _esp(d, ((W - ap) / 2, base + 82), pie.upper(), fp,
                 PALETA["tenue"] + (225,), 4)

    elif tipo == "barras":
        items = spec["items"]
        mx = max(v for _, v in items) or 1
        n = len(items)
        ancho = int(W * 0.58)
        x0 = (W - ancho) // 2
        alto_b, hueco = 30, 92
        fl = _fuente(36, "media")
        fv = _fuente(52, "negra")
        titulo = spec.get("titulo", "")

        alto = (56 if titulo else 0) + n * (alto_b + hueco) - hueco + 146
        y0 = cy - alto // 2
        _pon(capa, _carta(ancho + 120, alto, 32, ac), x0 - 60, y0)

        yy = y0 + 76
        if titulo:
            _epigrafe(capa, d, x0, yy, ancho, titulo)
            yy += 56

        for i, (nom, v) in enumerate(items):
            ui = _suave(float(np.clip((u - i * 0.16) / 0.62, 0, 1)))
            col = tuple(spec.get("destacar", {}).get(nom, ac))
            # LA ETIQUETA VA ENCIMA DE LA BARRA, no a su izquierda.
            #
            # A la izquierda el ancho disponible depende de lo larga que sea
            # la etiqueta, y "hoteles con su nombre" se salia del encuadre:
            # en el episodio del hotel se vio "oteles con su nombre". Encima
            # de la barra cabe siempre, la cifra queda alineada a la derecha
            # con las de las demas filas, y ademas se lee en el orden en que
            # se dice: primero de que hablamos, luego cuanto es.
            d.text((x0, yy), nom, font=fl, fill=PALETA["tenue"] + (235,),
                   anchor="ls")
            et = _fmt(v * ui, spec.get("dec", 0)) + spec.get("sufijo", "")
            d.text((x0 + ancho, yy + 4), et, font=fv, fill=col + (255,),
                   anchor="rs")
            _surco(d, [x0, yy + 24, x0 + ancho, yy + 24 + alto_b])
            largo = int(ancho * (v / mx) * ui)
            # Una barra minuscula tiene que VERSE minuscula, no faltar: los
            # 50 hoteles propios sobre 9.000 son ocho pixeles, y esa astilla
            # ES el argumento del episodio.
            if largo > 2:
                # el minimo es una pastilla corta, no un circulo: un circulo
                # suelto al principio de la barra se lee como un punto de
                # carga, no como una cantidad ridicula
                _barra(capa, [x0, yy + 24, x0 + max(int(alto_b * 1.9), largo),
                              yy + 24 + alto_b], col)
            yy += alto_b + hueco

    elif tipo == "anillo":
        val = spec["valor"]
        top = spec.get("max", 100)
        r = int(spec.get("r", 180))
        cx = int(spec.get("x", 0.5) * W)
        gr = 30
        pie = spec.get("pie", "")
        fp = _fuente(40, "media")
        ap = _ancho_esp(d, pie.upper(), fp, 4) if pie else 0
        ancho = int(max(r * 2 + 150, ap + 150))
        alto = r * 2 + 130 + (70 if pie else 0)
        _pon(capa, _carta(ancho, alto, 32, ac), cx - ancho // 2, cy - r - 64)

        caja = [cx - r, cy - r, cx + r, cy + r]
        d.ellipse(caja, outline=(255, 255, 255, 34), width=gr)
        ang = 360 * (val / top) * e
        d.arc(caja, -90, -90 + ang, fill=ac + (255,), width=gr)
        # Remate redondo en las dos puntas del arco. PIL dibuja el arco a
        # tope cuadrado y se nota: un arco con canto recto parece un trozo
        # de tarta, uno con canto redondo parece un indicador.
        for a_ in (-90, -90 + ang):
            rad = math.radians(a_)
            px_, py_ = cx + r * math.cos(rad), cy + r * math.sin(rad)
            d.ellipse([px_ - gr / 2, py_ - gr / 2, px_ + gr / 2, py_ + gr / 2],
                      fill=ac + (255,))
        f = _fuente(int(r * 0.46), "negra")
        t = _fmt(val * e, spec.get("dec", 1)) + spec.get("sufijo", "")
        d.text((cx, cy + int(r * 0.16)), t, font=f, fill=ac + (255,), anchor="ms")
        if pie:
            _esp(d, (cx - ap / 2, cy + r + 66), pie.upper(), fp,
                 PALETA["tenue"] + (225,), 4)

    elif tipo == "reparto":
        # una barra partida: cuanto se lleva cada uno. Para el capitulo 4.
        val = spec["valor"] / 100.0
        ancho, alto = int(W * 0.60), 76
        x0 = (W - ancho) // 2
        f = _fuente(36, "media")
        fv = _fuente(54, "negra")
        _pon(capa, _carta(ancho + 120, alto + 136, 32, ac), x0 - 60, cy - 114)
        izq = spec.get("etiqueta_a", "")
        der = spec.get("etiqueta_b", "")
        d.text((x0, cy - 46), izq, font=f, fill=PALETA["tenue"] + (235,),
               anchor="ls")
        d.text((x0 + ancho, cy - 46), der, font=f, fill=PALETA["tenue"] + (235,),
               anchor="rs")
        _surco(d, [x0, cy - 22, x0 + ancho, cy - 22 + alto])
        corte = int(ancho * val * e)
        col_a = tuple(spec.get("color_a", PALETA["aviso"]))
        if corte > 2:
            _barra(capa, [x0, cy - 22, x0 + max(alto, corte), cy - 22 + alto],
                   col_a)
        t = _fmt(spec["valor"] * e, spec.get("dec", 1)) + "%"
        an_t = d.textlength(t, font=fv)
        # La cifra va DENTRO del tramo si cabe, y fuera si no: metida a la
        # fuerza en un tramo estrecho se sale por el otro lado.
        if an_t + 44 < corte:
            d.text((x0 + 26, cy + 34), t, font=fv, fill=(12, 14, 20, 255),
                   anchor="ls")
        else:
            d.text((x0 + corte + 22, cy + 34), t, font=fv, fill=col_a + (255,),
                   anchor="ls")

    elif tipo == "factura":
        # Las lineas de gasto que ya llevas, y el total debajo.
        #
        # Este es EL grafico del canal. El formato es "cuanto cuesta comprar
        # y mantener X", y lo que engancha no es cada cifra suelta: es ver
        # la cuenta crecer. Un contador dice 55 millones y se va; la factura
        # dice 55 millones Y ademas te recuerda que ya llevabas catorce, y
        # por eso te quedas a ver el capitulo siguiente.
        #
        # Las lineas anteriores entran ya puestas y en gris. La ultima se
        # escribe delante del espectador y en color: es la de este capitulo.
        lineas = spec.get("lineas", [])
        ancho = int(W * 0.58)
        x0 = (W - ancho) // 2
        fc = _fuente(36, "media")
        fi = _fuente(38, "fuerte")
        ft = _fuente(31, "media")
        ftot = _fuente(78, "negra")
        alto_l = 62
        titulo = spec.get("titulo", "")

        alto = (62 if titulo else 22) + len(lineas) * alto_l + 240
        y0 = cy - alto // 2
        _pon(capa, _carta(ancho + 128, alto, 32, ac), x0 - 64, y0)

        yy = y0 + 56
        if titulo:
            _epigrafe(capa, d, x0, yy, ancho, titulo)
            yy += 40

        for i, par in enumerate(lineas):
            nom, imp = par[0], par[1]
            nueva = (i == len(lineas) - 1)
            ui = 1.0 if not nueva else float(np.clip((u - 0.16) / 0.40, 0, 1))
            if ui <= 0.02:
                continue
            col = PALETA["hueso"] if nueva else PALETA["tenue"]
            col_i = ac if nueva else (178, 184, 200)
            op = int((255 if nueva else 205) * ui)
            base = yy + 42
            # marca de la linea nueva: un galon corto en el margen
            if nueva:
                d.rounded_rectangle([x0 - 28, base - 28, x0 - 22, base + 6], 3,
                                    fill=ac + (op,))
            imp_t = imp if isinstance(imp, str) else _fmt(imp, 1)
            an_i = d.textlength(imp_t, font=fi)
            txt = nom
            while d.textlength(txt, font=fc) > ancho - an_i - 80 and len(txt) > 4:
                txt = txt[:-2]
            an_c = d.textlength(txt, font=fc)
            d.text((x0, base), txt, font=fc, fill=col + (op,), anchor="ls")
            d.text((x0 + ancho, base), imp_t, font=fi, fill=col_i + (op,),
                   anchor="rs")
            # Puntos guia entre el concepto y el importe. Es lo que hace que
            # se lea como una FACTURA y no como una lista: el ojo sigue los
            # puntos de un lado al otro y no se pierde de linea.
            px_, fin = x0 + an_c + 18, x0 + ancho - an_i - 18
            while px_ < fin:
                d.ellipse([px_, base - 11, px_ + 3, base - 8],
                          fill=PALETA["tenue"] + (int(op * 0.5),))
                px_ += 13
            yy += alto_l

        yt = yy + 24
        d.line([x0, yt, x0 + ancho, yt], fill=(255, 255, 255, 46), width=2)
        ut = float(np.clip((u - 0.55) / 0.40, 0, 1))
        if ut > 0.02:
            et = spec.get("etiqueta_total", "llevas gastado").upper()
            _esp(d, (x0, yt + 44), et, ft, PALETA["tenue"] + (int(210 * ut),), 4)
            tot = spec.get("total", "")
            d.text((x0 + ancho, yt + 104), tot, font=ftot,
                   fill=ac + (int(255 * ut),), anchor="rs")

    elif tipo == "apilada":
        # Una sola barra partida en tramos. Es el grafico que faltaba: el
        # contador dice UNA cifra, y hay frases que son un DESGLOSE -"de
        # 7,66 millones que entran, 383 mil se los lleva el letrero"-. Con
        # un contador esa frase se cuenta a medias.
        items = spec["items"]
        suma = sum(v for _, v in items) or 1
        ancho, alto_b = int(W * 0.60), 54
        x0 = (W - ancho) // 2
        fl = _fuente(34, "media")
        fv = _fuente(42, "negra")
        alto = 92 + alto_b + 46 + len(items) * 54
        y0 = cy - alto // 2
        _pon(capa, _carta(ancho + 128, alto, 32, ac), x0 - 64, y0)

        yy = y0 + 58
        if spec.get("total"):
            _epigrafe(capa, d, x0, yy, ancho, spec["total"], PALETA["tenue"])
        yb = yy + 34
        _surco(d, [x0, yb, x0 + ancho, yb + alto_b])
        # LA BARRA SE DIBUJA DE UNA PIEZA Y SE RECORTA DESPUES.
        #
        # Tramo a tramo, cada uno con su propio redondeo, el ultimo -que
        # mide el cinco por ciento- salia redondeado por los cuatro lados:
        # una pastilla suelta pegada al final, no el remate de la barra.
        # Dibujando los tramos a canto vivo sobre una tira y aplicando la
        # mascara redondeada al conjunto, las esquinas exteriores salen
        # redondas, las juntas interiores rectas y el ultimo tramo termina
        # exactamente donde termina la barra.
        tira = Image.new("RGBA", (ancho, alto_b), (0, 0, 0, 0))
        dt = ImageDraw.Draw(tira)
        rampa = np.linspace(1.20, 0.86, alto_b, dtype=np.float32)
        cursor = 0.0
        for i, (nom, v) in enumerate(items):
            ui = _suave(float(np.clip((u - i * 0.24) / 0.52, 0, 1)))
            largo = ancho * (v / suma) * ui
            xa, xb = int(cursor), int(cursor + largo)
            col = tuple(spec.get("colores", {}).get(
                nom, ac if i == 0 else PALETA["aviso"]))
            if xb - xa > 0:
                for fila in range(alto_b):
                    dt.line([xa, fila, xb, fila],
                            fill=tuple(int(min(255, c * rampa[fila]))
                                       for c in col) + (248,))
            cursor += ancho * (v / suma)
        mascara = Image.new("L", (ancho, alto_b), 0)
        ImageDraw.Draw(mascara).rounded_rectangle(
            [0, 0, ancho - 1, alto_b - 1], alto_b // 2, fill=255)
        tira.putalpha(Image.fromarray(
            np.minimum(np.asarray(tira.getchannel("A")),
                       np.asarray(mascara))))
        capa.alpha_composite(tira, (x0, yb))

        # LEYENDA DEBAJO, no cifras metidas dentro de los tramos.
        #
        # El tramo del letrero es el 5% de la barra: ahi no cabe "383 mil €"
        # de ninguna manera, y sacarlo con una guia dejaba dos numeros casi
        # encima del otro. En una fila por concepto siempre cabe, siempre
        # esta alineado y se puede leer sin pausar.
        yl = yb + alto_b + 42
        for i, (nom, v) in enumerate(items):
            ui = float(np.clip((u - 0.26 - i * 0.20) / 0.38, 0, 1))
            if ui <= 0.02:
                continue
            op = int(255 * ui)
            col = tuple(spec.get("colores", {}).get(
                nom, ac if i == 0 else PALETA["aviso"]))
            d.rounded_rectangle([x0, yl + 8, x0 + 16, yl + 24], 4,
                                fill=col + (op,))
            d.text((x0 + 34, yl + 26), nom, font=fl,
                   fill=PALETA["hueso"] + (int(op * 0.92),), anchor="ls")
            et = _fmt(v, spec.get("dec", 2)) + spec.get("sufijo", "")
            d.text((x0 + ancho, yl + 28), et, font=fv, fill=col + (op,),
                   anchor="rs")
            yl += 54

    elif tipo == "rejilla":
        # Cuenta de unidades: 200 personas, 100 marcadas. Un porcentaje
        # dibujado como anillo es abstracto; 200 cuadraditos son 200
        # personas y se entienden sin leer la cifra.
        total = int(spec.get("total", 100))
        marcados = int(spec.get("marcados", 0))
        cols = int(spec.get("cols", 21))
        filas = (total + cols - 1) // cols
        lado = int(min(W * 0.56 / cols, H * 0.38 / filas))
        hueco = max(3, lado // 6)
        paso = lado + hueco
        an_g = cols * paso - hueco
        al_g = filas * paso - hueco
        gx = (W - an_g) // 2
        pie = spec.get("pie", "")
        fp = _fuente(40, "media")
        ap = _ancho_esp(d, pie.upper(), fp, 4) if pie else 0
        alto = al_g + 116 + (74 if pie else 0)
        gy = cy - alto // 2 + 58
        _pon(capa, _carta(int(max(an_g, ap) + 148), alto, 32, ac),
             (W - int(max(an_g, ap) + 148)) // 2, cy - alto // 2)

        base = tuple(spec.get("color_base", (255, 255, 255)))
        marca = tuple(spec.get("color_marca", PALETA["aviso"]))
        for k in range(total):
            fi_, co = divmod(k, cols)
            x = gx + co * paso
            y = gy + fi_ * paso
            if k >= total - marcados:
                uk = float(np.clip((u - 0.62) / 0.30, 0, 1))
                col, op = marca, int(255 * uk)
            else:
                uk = float(np.clip((u - 0.55 * (k / float(max(1, total)))) / 0.30,
                                   0, 1))
                col, op = base, int(84 * uk)
            if op <= 2:
                continue
            d.rounded_rectangle([x, y, x + lado, y + lado],
                                max(2, lado // 4), fill=col + (op,))
        if pie:
            _esp(d, ((W - ap) / 2, gy + al_g + 62), pie.upper(), fp,
                 PALETA["hueso"] + (230,), 4)

    elif tipo == "flecha":
        # Quien le paga a quien. Dos cajas y una flecha que viaja. El
        # capitulo de Charleroi es exactamente esto y no hay clip de stock
        # que lo cuente: lo unico que hay que ver es que la flecha va al
        # reves de como todo el mundo cree.
        f = _fuente(44, "fuerte")
        fe = _fuente(34, "media")
        cajas = [spec.get("a", ""), spec.get("b", "")]
        anchos = [max(300, int(d.textlength(c, font=f)) + 88) for c in cajas]
        alto = 132
        sep = int(W * 0.22)
        xa = (W - (anchos[0] + sep + anchos[1])) // 2
        xb = xa + anchos[0] + sep
        for cx0, an, nom, acc in ((xa, anchos[0], cajas[0], None),
                                  (xb, anchos[1], cajas[1], ac)):
            _pon(capa, _carta(an, alto, 20, acc), cx0, cy - alto // 2)
            d.text((cx0 + an / 2, cy + 15), nom, font=f,
                   fill=PALETA["hueso"] + (252,), anchor="ms")
        # La punta se para ANTES del canto de la caja: metida dentro se
        # solapaba con el galon de acento y los dos rojos se fundian en un
        # borron.
        ix, fx = xa + anchos[0] + 22, xb - 46
        if spec.get("invertida"):
            ix, fx = fx, ix
        pos = ix + (fx - ix) * e
        s = 1 if fx > ix else -1
        d.line([ix, cy, pos, cy], fill=ac + (255,), width=8)
        d.polygon([(pos + s * 28, cy), (pos - s * 12, cy - 22),
                   (pos - s * 12, cy + 22)], fill=ac + (255,))
        # un pulso que recorre la linea ya trazada: dice "esto va pasando
        # ahora", que es justo lo que la frase esta contando
        pul = ix + (fx - ix) * float((u * 1.6) % 1.0)
        if abs(pul - ix) < abs(pos - ix):
            d.ellipse([pul - 7, cy - 7, pul + 7, cy + 7],
                      fill=PALETA["hueso"] + (210,))
        if spec.get("etiqueta") and u > 0.5:
            op = int(255 * min(1.0, (u - 0.5) / 0.35))
            et = spec["etiqueta"]
            an_e = d.textlength(et, font=fe)
            yp = cy - alto // 2 - 60
            d.rounded_rectangle([(W - an_e) / 2 - 30, yp - 16,
                                 (W + an_e) / 2 + 30, yp + 50], 33,
                                fill=(10, 14, 24, int(op * 0.88)),
                                outline=ac + (int(op * 0.6),), width=2)
            d.text((W / 2, yp + 36), et, font=fe, fill=ac + (op,), anchor="ms")

    elif tipo == "ilustracion":
        # EL MEDALLON. Para las frases que no tienen metraje de calidad.
        #
        # Un icono suelto en mitad del cuadro flota. Metido en un medallon
        # -la misma tarjeta de los demas graficos, pero cuadrada y con las
        # esquinas muy redondas- tiene sitio, sombra y peso, y se corta con
        # el resto del episodio sin que cante.
        #
        # El anillo que lo rodea se cierra mientras el icono se construye:
        # es lo que convierte un dibujo en motion graphics. Dice "esto se
        # esta montando ahora", que es exactamente el tono del canal.
        lado = int(spec.get("lado", 300))
        x0 = (W - lado) // 2
        y0 = cy - lado // 2
        # Redondo, no cuadrado con las esquinas comidas: el anillo que lo
        # rodea es un circulo y el canto del cuadrado asomaba por detras en
        # los planos con el fondo claro.
        _pon(capa, _carta(lado, lado, lado // 2, None), x0, y0)

        cx, cy_m = x0 + lado // 2, y0 + lado // 2
        r_an = int(lado * 0.60)
        caja_an = [cx - r_an, cy_m - r_an, cx + r_an, cy_m + r_an]
        d.ellipse(caja_an, outline=(255, 255, 255, 26), width=5)
        if e > 0.01:
            d.arc(caja_an, -90, -90 + 360 * e, fill=ac + (200,), width=5)
            rad = math.radians(-90 + 360 * e)
            d.ellipse([cx + r_an * math.cos(rad) - 7,
                       cy_m + r_an * math.sin(rad) - 7,
                       cx + r_an * math.cos(rad) + 7,
                       cy_m + r_an * math.sin(rad) + 7], fill=ac + (235,))

        m = int(lado * 0.22)
        ICO.dibuja(spec.get("icono", "dato"), d,
                   (x0 + m, y0 + m, x0 + lado - m, y0 + lado - m),
                   ac + (255,), float(np.clip(u / 0.92, 0, 1)))

        # La chapa de direccion, arriba a la derecha del medallon. La frase
        # dice "sube" o "cae" y eso es la mitad de lo que hay que entender;
        # una flecha lo dice sin gastar una linea de rotulo.
        dirn = spec.get("flecha")
        if dirn and u > 0.45:
            op = int(255 * min(1.0, (u - 0.45) / 0.3))
            col_f = PALETA["ok"] if dirn == "sube" else PALETA["aviso"]
            # En la diagonal del anillo, fuera de el. En la esquina de la
            # caja caia justo encima del trazo del anillo.
            bx = int(cx + r_an * 0.74)
            by = int(cy_m - r_an * 0.74)
            d.ellipse([bx - 38, by - 38, bx + 38, by + 38],
                      fill=(10, 14, 24, int(op * 0.94)),
                      outline=col_f + (op,), width=3)
            # Hacia donde dice la frase. Estaba invertido: "cuando
            # pierdes" salia con la flecha subiendo.
            s = 1 if dirn == "sube" else -1
            d.line([bx - 15, by + 15 * s, bx + 15, by - 15 * s],
                   fill=col_f + (op,), width=6)
            d.polygon([(bx + 21, by - 21 * s), (bx + 2, by - 17 * s),
                       (bx + 17, by - 2 * s)], fill=col_f + (op,))

        if spec.get("nota"):
            f = _fuente(30, "media")
            nota = spec["nota"].upper()
            an = _ancho_esp(d, nota, f, 5)
            _esp(d, ((W - an) / 2, y0 + lado + 78), nota, f,
                 PALETA["tenue"] + (215,), 5)

    elif tipo == "mapa":
        # Silueta de la Espana peninsular con los aeropuertos encendiendose
        # y apagandose. Un capitulo que es una lista de ciudades, contado
        # con rotulos, es una lista; contado sobre un mapa, es una imagen.
        pts = spec.get("contorno") or ESPANA
        lons = [q[0] for q in pts]
        lats = [q[1] for q in pts]
        # equirectangular con correccion por latitud, o Espana sale gorda
        kx = math.cos(math.radians(sum(lats) / len(lats)))
        w_g = (max(lons) - min(lons)) * kx
        h_g = max(lats) - min(lats)
        escala = min(W * 0.62 / w_g, H * 0.70 / h_g)
        cx = int(spec.get("x", 0.5) * W)
        lon_c = (min(lons) + max(lons)) / 2.0
        lat_c = (min(lats) + max(lats)) / 2.0

        def proyecta(lon, lat):
            return (cx + (lon - lon_c) * kx * escala,
                    cy - (lat - lat_c) * escala)

        contorno = [proyecta(*q) for q in pts]
        d.polygon(contorno, fill=(255, 255, 255, 22))
        d.line(contorno + [contorno[0]], fill=PALETA["hueso"] + (130,), width=3)
        fp = _fuente(32, "media")
        # Asturias y Santander estan a 180 km, y en pantalla el nombre de
        # una acababa justo encima del circulo de la otra. Se reservan
        # PRIMERO todos los circulos y luego cada nombre baja hasta hueco.
        ocupadas = []
        for m in spec.get("puntos", []):
            px_, py_ = proyecta(m[1], m[2])
            ocupadas.append((px_ - 22, py_ - 22, px_ + 22, py_ + 22))

        def hueco_libre(x, y, ancho, alto=40):
            for _ in range(6):
                caja = (x, y, x + ancho, y + alto)
                if not any(caja[0] < o[2] and o[0] < caja[2]
                           and caja[1] < o[3] and o[1] < caja[3]
                           for o in ocupadas):
                    ocupadas.append(caja)
                    return y
                y += alto + 4
            ocupadas.append((x, y, x + ancho, y + alto))
            return y

        for i, m in enumerate(spec.get("puntos", [])):
            nom, lon, lat = m[0], m[1], m[2]
            off = bool(m[3]) if len(m) > 3 else False
            x, y = proyecta(lon, lat)
            ui = float(np.clip((u - 0.12 * i) / 0.45, 0, 1))
            if ui <= 0.01:
                continue
            if off:
                col = tuple(int(a + (b - a) * _suave(ui))
                            for a, b in zip(ac, (120, 120, 128)))
                r = int(15 - 6 * _suave(ui))
                brillo = int(38 * (1 - _suave(ui)))
                op = int(240 * (1 - 0.55 * _suave(ui)))
            else:
                col, r, brillo, op = ac, 13, 30, int(240 * ui)
            if brillo > 2:
                d.ellipse([x - r - brillo, y - r - brillo,
                           x + r + brillo, y + r + brillo], fill=col + (46,))
            d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
            ex = x + r + 14
            an_n = d.textlength(nom, font=fp)
            ey = hueco_libre(ex, y - 20, an_n)
            if ey != y - 20:
                d.line([x + r + 4, y, ex - 4, ey + 18],
                       fill=PALETA["hueso"] + (int(op * 0.5),), width=2)
            # chapita oscura detras del nombre: sobre el relleno del mapa un
            # texto claro se pierde
            d.rounded_rectangle([ex - 8, ey - 2, ex + an_n + 10, ey + 38], 8,
                                fill=(10, 14, 24, int(op * 0.72)))
            d.text((ex, ey + 30), nom, font=fp, fill=PALETA["hueso"] + (op,),
                   anchor="ls")

    return capa


def compon_grafico(arr, capa, entrada, u_ent, u_sal, W, H):
    return compon_texto(arr, capa, u_ent, u_sal, entrada, W, H)


# ---------------------------------------------------------------------------
# EL PLATO: EL FONDO DE MARCA
#
# Un grafico encima de un clip de stock siempre pierde. El clip se mueve, tiene
# detalle en todas las frecuencias y trae su propia luz, asi que la tarjeta
# necesita opacidad y sombra solo para poder leerse, y aun asi el ojo se va al
# metraje. Y encima obliga a buscar un plano que "pegue" con una cifra, que es
# de donde salian los planos que no venian a cuento.
#
# Cuando lo que importa es el dato, el fondo no tiene que competir: tiene que
# ser del canal. Esto es un plato virtual -degradado, reticula, marca de agua,
# el rotulo del canal abajo y una luz que cruza- dibujado entero por codigo,
# sin un solo asset. El espectador nota que el video CAMBIA DE MODO cuando
# llega una cifra, que es exactamente lo que se quiere decir.
#
# Si algun dia hay un logotipo de verdad en assets/brand/logo.png, se usa ese
# en vez del monograma dibujado. Hasta entonces, el monograma.
# ---------------------------------------------------------------------------
CANAL = "PROBLEMAS MILLONARIOS"
SERIE = "EL PRECIO DE SER EL DUEÑO"

_LOGO = _os.path.normpath(_os.path.join(_AQUI, "..", "assets", "brand", "logo.png"))


@_ft.lru_cache(maxsize=4)
def _plato_fondo(W, H, acento):
    """La parte quieta del plato. Se calcula una vez por episodio."""
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    # Degradado radial descentrado hacia arriba: el centro optico de un plano
    # no esta en el centro geometrico, esta un poco por encima.
    r = np.sqrt(((x - 0.5) * 1.02) ** 2 + ((y - 0.44) * 1.32) ** 2)
    v = np.clip(1.0 - r * 0.92, 0.0, 1.0) ** 1.35
    base = np.stack([9 + v * 30, 13 + v * 38, 24 + v * 54], -1).astype(np.float32)

    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)

    # Marca de agua: el simbolo del euro, enorme y a punto de no verse. Es lo
    # que hace que un fondo liso deje de parecer una diapositiva en blanco.
    # A 0,80 de ancho el simbolo se salia por la derecha y lo que quedaba
    # en cuadro no se reconocia: se leia como una mancha clara. Entero y algo
    # mas pequeno se lee como lo que es sin pedir atencion.
    d.text((int(W * 0.74), int(H * 0.54)), "\u20ac", font=_fuente(int(H * 1.18), "negra"),
           fill=(255, 255, 255, 10), anchor="mm")

    # La banda de abajo: el rotulo del canal. Es el "banner".
    yb = int(H * 0.915)
    d.line([int(W * 0.055), yb - 36, int(W * 0.945), yb - 36],
           fill=(255, 255, 255, 26), width=2)

    logo, marca_an = None, 0
    if _os.path.exists(_LOGO):
        try:
            logo = Image.open(_LOGO).convert("RGBA")
            k = 62.0 / max(1, logo.height)
            logo = logo.resize((max(1, int(logo.width * k)), 62), Image.LANCZOS)
            marca_an = logo.width + 22
        except OSError:
            logo = None
    if logo is None:
        # Monograma: el euro dentro de un anillo. Que sea un circulo y no un
        # cuadrado no es un capricho: al lado de un rotulo en caja alta, un
        # cuadrado se lee como una vineta y un circulo se lee como un sello.
        cxm, cym, rm = int(W * 0.055) + 30, yb + 4, 30
        d.ellipse([cxm - rm, cym - rm, cxm + rm, cym + rm],
                  outline=tuple(acento) + (225,), width=4)
        d.text((cxm, cym + 1), "\u20ac", font=_fuente(38, "negra"),
               fill=tuple(acento) + (245,), anchor="mm")
        marca_an = 82

    xm = int(W * 0.055) + marca_an
    _esp(d, (xm, yb - 2), CANAL, _fuente(29, "negra"), PALETA["hueso"] + (215,), 6)
    _esp(d, (xm, yb + 30), SERIE, _fuente(21, "media"), PALETA["tenue"] + (170,), 5)
    if logo is not None:
        capa.alpha_composite(logo, (int(W * 0.055), yb - 40))

    a = np.asarray(capa, np.float32)
    al = a[..., 3:4] / 255.0
    return (base * (1 - al) + a[..., :3] * al).astype(np.float32)


@_ft.lru_cache(maxsize=4)
def _plato_reticula(W, H, paso=92):
    """Trama de lineas finas, con un cuadro de margen para poder moverla."""
    m = paso
    g = Image.new("L", (W + m, H + m), 0)
    d = ImageDraw.Draw(g)
    for i in range(0, W + m, paso):
        d.line([i, 0, i, H + m], fill=13, width=1)
    for j in range(0, H + m, paso):
        # cada cuarta linea, mas marcada: la jerarquia tambien va en el fondo
        d.line([0, j, W + m, j], fill=26 if (j // paso) % 4 == 0 else 13, width=1)
    return np.asarray(g, np.float32)


def plato(W, H, t, acento=None, titulo="", fase=0.0):
    """Un fotograma del plato del canal. `t` va de 0 a 1 a lo largo del plano.

    Lo que se mueve: la reticula deriva despacio en diagonal y una luz calida
    cruza el plano de izquierda a derecha una sola vez. Nada mas. Un fondo de
    datos que se mueve mucho compite con el dato; lo que tiene que hacer es no
    estar quieto del todo, que es distinto.
    """
    acento = tuple(acento or PALETA["acento"])
    arr = _plato_fondo(W, H, acento).copy()

    # `fase` da variedad entre planos sin cambiar nada del diseno: la
    # reticula deriva hacia un lado o hacia el otro y la luz entra por la
    # izquierda o por la derecha. Veintitres tarjetas identicas se leen como
    # una plantilla; las mismas con la luz cambiada, como planos distintos.
    s = -1.0 if fase >= 0.5 else 1.0
    paso = 92
    g = _plato_reticula(W, H, paso)
    dx = int(((t * 0.55 * s) % 1.0) * paso)
    dy = int(((1.0 - t * 0.38 * s) % 1.0) * paso)
    arr += g[dy:dy + H, dx:dx + W][..., None]

    # La luz que cruza, separable -un perfil en x por otro en y- para no
    # calcular una gaussiana de dos millones de puntos por fotograma.
    cx = (-0.25 + 1.5 * t) if s > 0 else (1.25 - 1.5 * t)
    px = np.exp(-(((np.linspace(0, 1, W, dtype=np.float32) - cx) / 0.30) ** 2))
    py = np.exp(-(((np.linspace(0, 1, H, dtype=np.float32) - 0.40) / 0.75) ** 2))
    arr += np.outer(py, px)[..., None] * (np.array(acento, np.float32) / 255.0) * 26.0

    if titulo:
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        x0, y0 = int(W * 0.09), int(H * 0.135)
        d.rounded_rectangle([x0 - 4, y0 - 26, x0 + 4, y0 + 6], 3,
                            fill=acento + (235,))
        _esp(d, (x0 + 22, y0), titulo.upper(), _fuente(30, "media"),
             PALETA["hueso"] + (205,), 5)
        a = np.asarray(capa, np.float32)
        al = a[..., 3:4] / 255.0
        arr = arr * (1 - al) + a[..., :3] * al

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------------------
# LATIGAZO DE CAMARA (whip pan)
# ---------------------------------------------------------------------------
def latigo(arr, direccion, u, fuerza=0.95):
    """Barrido lateral rapido con desenfoque de movimiento.

    Es la transicion invisible que usan los editores en After Effects con
    Motion Tile mas Directional Blur: la camara sale de plano a toda
    velocidad, el desenfoque se come el detalle, y el plano siguiente entra
    con el mismo barrido en el mismo sentido. El ojo no ve un corte, ve una
    panoramica.

    Lo que lo vende es el desenfoque, no el desplazamiento: un barrido nitido
    se lee como un salto. Por eso el radio crece con la VELOCIDAD -la
    derivada, 2u- y no con la distancia recorrida.

    u va de 0 (en reposo) a 1 (fuera de cuadro). `direccion` es -1 o +1.
    """
    H, W = arr.shape[:2]
    u = float(np.clip(u, 0, 1))
    if u <= 0.001:
        return arr
    dx = int(round(direccion * W * fuerza * u * u))
    radio = int(round(W * 0.055 * min(1.0, 2.0 * u)))

    if radio > 1:
        # Desenfoque horizontal por suma acumulada: O(1) por radio, que a
        # 1920 de ancho y radio 100 es la diferencia entre medio segundo por
        # fotograma y ninguno.
        r = min(radio, W // 2 - 1)
        pad = np.pad(arr, ((0, 0), (r + 1, r), (0, 0)), mode="edge")
        acum = np.cumsum(pad, axis=1)
        arr = (acum[:, 2 * r + 1:] - acum[:, :-(2 * r + 1)]) / (2 * r + 1)

    if dx:
        movido = np.empty_like(arr)
        if dx > 0:
            dx = min(dx, W - 1)
            movido[:, dx:] = arr[:, :W - dx]
            movido[:, :dx] = arr[:, :1]
        else:
            dx = max(dx, -(W - 1))
            movido[:, :W + dx] = arr[:, -dx:]
            movido[:, W + dx:] = arr[:, -1:]
        arr = movido
    # Oscurece un poco para que el corte caiga en el punto mas apagado, pero
    # POCO: el barrido de salida y el de entrada se suman a ambos lados del
    # corte, y con 0,45 en cada uno quedaba casi medio segundo de imagen
    # negra. Un whip pan es un borron, no un parpadeo.
    return arr * (1.0 - 0.22 * u * u)
