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

FUENTES = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

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
def _fuente(px):
    for f in FUENTES:
        try:
            return ImageFont.truetype(f, px)
        except OSError:
            continue
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

    ancho = sum(d.textlength(p, font=f) for p, _ in partes)
    alto = px * 1.25
    ax, ay = pos
    x = (W - ancho) / 2 if ax == "center" else (
        W * 0.09 if ax == "left" else W * 0.91 - ancho)
    y = ay * H - alto / 2

    for parte, es_ac in partes:
        col = acento if (es_ac and acento) else color
        d.text((x + 3, y + 4), parte, font=f, fill=(0, 0, 0, 150))   # sombra
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
PALETA = {
    "acento":  (255, 196, 90),
    "aviso":   (255, 110, 86),
    "ok":      (120, 220, 170),
    "hueso":   (240, 236, 228),
    "surco":   (255, 255, 255, 38),
}


def _fmt(v, dec=0, mil="."):
    e = f"{v:,.{dec}f}".replace(",", "\x00").replace(".", ",").replace("\x00", mil)
    return e if dec else e.split(",")[0]


def _panel(d, caja, radio=18, alpha=104):
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
        f = _fuente(px)
        fp = _fuente(int(px * 0.42))
        txt = spec.get("prefijo", "") + _fmt(val, spec.get("dec", 0))
        sub = spec.get("sufijo", "")
        an = d.textlength(txt, font=f)
        ans = d.textlength(sub, font=fp) if sub else 0
        x = (W - (an + ans + (18 if sub else 0))) / 2
        d.text((x + 4, cy - px * 0.6 + 5), txt, font=f, fill=(0, 0, 0, 150))
        d.text((x, cy - px * 0.6), txt, font=f, fill=ac + (255,))
        if sub:
            d.text((x + an + 18, cy - px * 0.16), sub, font=fp,
                   fill=PALETA["hueso"] + (235,))
        if spec.get("pie"):
            fpie = _fuente(46)
            t = spec["pie"]
            d.text(((W - d.textlength(t, font=fpie)) / 2, cy + px * 0.48),
                   t, font=fpie, fill=PALETA["hueso"] + (200,))

    elif tipo == "barras":
        items = spec["items"]
        mx = max(v for _, v in items) or 1
        n = len(items)
        alto, hueco = 62, 34
        ancho = int(W * 0.56)
        x0 = int(W * 0.22)
        y0 = cy - (n * alto + (n - 1) * hueco) // 2
        f = _fuente(40)
        fv = _fuente(46)
        _panel(d, [x0 - 46, y0 - 40, x0 + ancho + 250, y0 + n * (alto + hueco) + 10])
        for i, (nom, v) in enumerate(items):
            y = y0 + i * (alto + hueco)
            # cada barra arranca un poco despues que la anterior
            ui = np.clip((u - i * 0.14) / 0.6, 0, 1)
            largo = int(ancho * (v / mx) * _suave(ui))
            col = tuple(spec.get("destacar", {}).get(nom, ac))
            d.rounded_rectangle([x0, y, x0 + ancho, y + alto], 8,
                                fill=PALETA["surco"])
            if largo > 10:
                d.rounded_rectangle([x0, y, x0 + largo, y + alto], 8,
                                    fill=col + (232,))
            d.text((x0 - 26 - d.textlength(nom, font=f), y + 10), nom, font=f,
                   fill=PALETA["hueso"] + (230,))
            d.text((x0 + ancho + 26, y + 6),
                   _fmt(v * _suave(ui), spec.get("dec", 1)) + spec.get("sufijo", ""),
                   font=fv, fill=col + (255,))

    elif tipo == "anillo":
        val = spec["valor"]
        top = spec.get("max", 100)
        r = int(spec.get("r", 190))
        cx = int(spec.get("x", 0.5) * W)
        gr = 26
        caja = [cx - r, cy - r, cx + r, cy + r]
        d.ellipse(caja, outline=(255, 255, 255, 46), width=gr)
        d.arc(caja, -90, -90 + 360 * (val / top) * e, fill=ac + (255,), width=gr)
        f = _fuente(int(r * 0.44))
        t = _fmt(val * e, spec.get("dec", 1)) + spec.get("sufijo", "")
        caja_t = d.textbbox((0, 0), t, font=f)
        d.text((cx - (caja_t[2] - caja_t[0]) / 2,
                cy - (caja_t[3] + caja_t[1]) / 2), t, font=f, fill=ac + (255,))
        if spec.get("pie"):
            fp = _fuente(44)
            d.text((cx - d.textlength(spec["pie"], font=fp) / 2, cy + r + 26),
                   spec["pie"], font=fp, fill=PALETA["hueso"] + (215,))

    elif tipo == "reparto":
        # una barra partida: cuanto se lleva cada uno. Para el capitulo 4.
        val = spec["valor"] / 100.0
        ancho, alto = int(W * 0.66), 96
        x0 = (W - ancho) // 2
        f = _fuente(44)
        d.rounded_rectangle([x0, cy - alto // 2, x0 + ancho, cy + alto // 2], 12,
                            fill=(255, 255, 255, 40))
        corte = int(ancho * val * e)
        d.rounded_rectangle([x0, cy - alto // 2, x0 + max(14, corte), cy + alto // 2],
                            12, fill=tuple(spec.get("color_a", PALETA["aviso"])) + (240,))
        izq = spec.get("etiqueta_a", "")
        der = spec.get("etiqueta_b", "")
        d.text((x0, cy - alto), izq, font=f, fill=PALETA["hueso"] + (230,))
        d.text((x0 + ancho - d.textlength(der, font=f), cy - alto), der,
               font=f, fill=PALETA["hueso"] + (230,))
        fv = _fuente(60)
        t = _fmt(spec["valor"] * e, spec.get("dec", 1)) + "%"
        d.text((x0 + 20, cy - 30), t, font=fv, fill=(12, 14, 20, 255))

    return capa


def compon_grafico(arr, capa, entrada, u_ent, u_sal, W, H):
    return compon_texto(arr, capa, u_ent, u_sal, entrada, W, H)


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
