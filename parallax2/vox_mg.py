#!/usr/bin/env python3
"""
Motion graphics del estilo VOX: lo que se dibuja ENCIMA de los recortes.

`vox.py` trae el tratamiento de las imagenes -semitono, trazo, papel- y los
dos graficos de datos: cifra y barras. Aqui van los gestos que hacen que la
pantalla no se quede quieta despues del primer segundo, que era el problema:
las capas entraban, y luego cuatro segundos sin que se moviera nada.

Todo se dibuja con la misma paleta y todo recibe `u`, el avance de 0 a 1,
porque en este estilo nada aparece de golpe: se traza.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import vox


def _suave(u):
    return 1 - (1 - u) ** 3


def anillo(im, pct, pal, centro=(0.50, 0.42), radio=0.15, u=1.0,
           sufijo="%", pie="", grosor=26, decimales=0):
    """
    Un porcentaje que se dibuja barriendo el arco. Para cuando la cifra ES
    la frase y no hay nada mas que contar.
    """
    W, H = im.size
    cx, cy, r = centro[0] * W, centro[1] * H, radio * min(W, H)
    caja = [cx - r, cy - r, cx + r, cy + r]
    d = ImageDraw.Draw(im)
    d.arc(caja, 0, 360, fill=pal["suave"], width=grosor)
    barrido = 360 * (pct / 100.0) * _suave(u)
    if barrido > 0.6:
        d.arc(caja, -90, -90 + barrido, fill=pal["apoyo"], width=grosor)
    fo = vox.f(int(r * 0.62))
    # sin decimales, un 3,22 se dibujaba como "3" y se perdia la cifra
    t = f"{pct*_suave(u):.{decimales}f}".replace(".", ",") + sufijo
    an = d.textlength(t, font=fo)
    d.text((cx - an / 2, cy - r * 0.42), t, font=fo, fill=pal["tinta"])
    if pie:
        fp = vox.f(42, regular=True)
        d.text(((W - d.textlength(pie, font=fp)) / 2, cy + r * 1.22), pie,
               font=fp, fill=pal["tinta"])
    return im


def marca(im, caja, pal, u=1.0, grosor=11, vueltas=1.15):
    """
    El circulo de rotulador alrededor de algo. Se traza, no aparece: el
    barrido es lo que dirige la mirada.
    """
    x0, y0, x1, y1 = [c * s for c, s in zip(caja, [im.size[0], im.size[1]] * 2)]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    pasos = max(2, int(150 * _suave(u)))
    total = 2 * math.pi * vueltas
    pts = []
    for i in range(pasos):
        a = -math.pi / 2 + total * i / 150.0
        # el radio ondula un poco: un circulo perfecto no parece hecho a mano
        w = 1 + 0.035 * math.sin(a * 3.1) + 0.02 * math.sin(a * 7.3)
        pts.append((cx + rx * w * math.cos(a), cy + ry * w * math.sin(a)))
    if len(pts) > 1:
        d.line(pts, fill=tuple(pal["apoyo"]) + (255,), width=grosor,
               joint="curve")
    im.paste(capa, (0, 0), capa)
    return im


def flecha(im, desde, hasta, pal, u=1.0, grosor=12, punta=34):
    """Una flecha que se dibuja sola de `desde` a `hasta`."""
    W, H = im.size
    x0, y0 = desde[0] * W, desde[1] * H
    x1, y1 = hasta[0] * W, hasta[1] * H
    s = _suave(u)
    xa, ya = x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
    d = ImageDraw.Draw(im)
    d.line([(x0, y0), (xa, ya)], fill=pal["tinta"], width=grosor)
    if s > 0.82:                       # la punta solo al final del trazo
        a = math.atan2(y1 - y0, x1 - x0)
        d.polygon([(x1, y1),
                   (x1 - punta * math.cos(a - 0.45), y1 - punta * math.sin(a - 0.45)),
                   (x1 - punta * math.cos(a + 0.45), y1 - punta * math.sin(a + 0.45))],
                  fill=pal["tinta"])
    return im


def ticker(im, texto, pal, u=1.0, y=0.885, px=40):
    """Banda inferior con un dato de apoyo. Entra deslizando desde abajo."""
    W, H = im.size
    fo = vox.f(px)
    d = ImageDraw.Draw(im)
    an = d.textlength(texto, font=fo)
    alto = int(px * 1.9)
    yy = int(H * y + (1 - _suave(u)) * alto)
    d.rectangle([0, yy, an + px * 2.4, yy + alto], fill=pal["tinta"])
    d.rectangle([0, yy, px * 0.34, yy + alto], fill=pal["apoyo"])
    d.text((px * 1.0, yy + px * 0.42), texto, font=fo, fill=pal["fondo"])
    return im


def barrido(im, u, pal, desde="izq"):
    """
    Bloque de color que cruza la pantalla. Es el corte: tapa el cambio de
    escena en vez de encadenar, que es lo que hace este estilo.
    """
    W, H = im.size
    if u <= 0 or u >= 1:
        return im
    # va y viene: entra tapando y sale destapando
    p = 1 - abs(2 * u - 1)
    ancho = int(W * 1.25 * p)
    d = ImageDraw.Draw(im)
    x = -int(W * 0.12) if desde == "izq" else W + int(W * 0.12) - ancho
    d.rectangle([x, 0, x + ancho, H], fill=pal["apoyo"] if u < 0.5 else pal["acento"])
    return im


def deriva(t, dur, indice=0):
    """
    El movimiento continuo de la escena: un empuje lento que no para.

    Es lo que faltaba. Las capas entraban en medio segundo y luego la
    pantalla se quedaba muerta hasta el corte. Aqui todo crece un 4% a lo
    largo de la escena y se desplaza un poco, y el frente lo hace MENOS que
    los sujetos, que es lo que da la sensacion de profundidad sin necesidad
    de desenfocar nada.

    Devuelve (escala_sujeto, dx, dy, escala_frente).
    """
    p = min(1.0, max(0.0, t / max(0.1, dur)))
    lado = 1 if indice % 2 == 0 else -1
    return (1.0 + 0.045 * p,
            lado * 0.018 * p,
            -0.012 * p,
            1.0 + 0.018 * p)


def reparto(im, pal, valor=100, etiqueta_a="", etiqueta_b="", u=1.0,
            y=0.30, alto=96, parte=None):
    """
    Una barra partida: cuanto se lleva cada uno. La parte de la izquierda
    crece y la de la derecha es lo que queda.

    Es el grafico del episodio: casi todo el dinero es de los clientes y una
    astilla es del banco. Con dos barras sueltas no se ve; partiendo UNA
    barra, si.
    """
    W, H = im.size
    x0, ancho = int(W * 0.12), int(W * 0.76)
    yy = int(H * y)
    d = ImageDraw.Draw(im)
    frac = (parte if parte is not None else 0.5) * _suave(u)
    d.rectangle([x0, yy, x0 + ancho, yy + alto], fill=pal["suave"])
    d.rectangle([x0, yy, x0 + int(ancho * frac), yy + alto], fill=pal["apoyo"])
    fo = vox.f(40, regular=True)
    if etiqueta_a:
        d.text((x0, yy + alto + 16), etiqueta_a, font=fo, fill=pal["tinta"])
    if etiqueta_b:
        an = d.textlength(etiqueta_b, font=fo)
        d.text((x0 + ancho - an, yy + alto + 16), etiqueta_b, font=fo,
               fill=pal["tinta"])
    return im


def banda(im, pal, u=1.0, y=0.70, alto=14):
    """Franja de color que se descubre de izquierda a derecha. Separa el
    bloque de tipografia de la imagen sin dibujar una caja."""
    W, H = im.size
    d = ImageDraw.Draw(im)
    yy = int(H * y)
    d.rectangle([0, yy, int(W * _suave(u)), yy + alto], fill=pal["acento"])
    return im


def tachado(im, caja, pal, u=1.0, grosor=12):
    """Raya que tacha algo. Se traza de un lado al otro."""
    W, H = im.size
    x0, y0, x1, y1 = caja[0]*W, caja[1]*H, caja[2]*W, caja[3]*H
    d = ImageDraw.Draw(im)
    s = _suave(u)
    d.line([(x0, y0), (x0 + (x1-x0)*s, y0 + (y1-y0)*s)],
           fill=pal["apoyo"], width=grosor)
    return im


# ---------------------------------------------------------------------------
# MOBILIARIO DE PANTALLA
# Lo que hace que una escena tenga cinco o seis elementos y no dos. No son
# adorno: son lo que llena el encuadre en este estilo, y sin ellos el plano
# se lee como una foto con un titulo encima. Todos cuestan codigo, cero
# imagenes generadas.
# ---------------------------------------------------------------------------

def banda_lateral(im, pal, u=1.0, lado="izq", ancho=18):
    """Franja vertical pegada a un borde. Crece de abajo arriba."""
    W, H = im.size
    d = ImageDraw.Draw(im)
    alto = int(H * _suave(u))
    x = 0 if lado == "izq" else W - ancho
    d.rectangle([x, H - alto, x + ancho, H], fill=pal["apoyo"])
    return im


def bloque_esquina(im, pal, u=1.0, esquina="sd", lado=0.10):
    """Bloque macizo en una esquina. Ancla la composicion y tapa el vacio
    que dejan los recortes cuando no llegan al borde."""
    W, H = im.size
    s = int(min(W, H) * lado * _suave(u))
    if s < 2:
        return im
    d = ImageDraw.Draw(im)
    x = W - s if esquina[1] == "d" else 0
    y = 0 if esquina[0] == "s" else H - s
    d.rectangle([x, y, x + s, y + s], fill=pal["acento"])
    return im


def numero_escena(im, n, pal, u=1.0, px=34):
    """El numero del plano, arriba a la derecha. Es de las cosas que mas
    dicen 'esto es un reportaje' y cuesta tres lineas."""
    W, H = im.size
    d = ImageDraw.Draw(im)
    fo = vox.f(px)
    t = f"{n:02d}"
    an = d.textlength(t, font=fo)
    a = int(255 * _suave(u))
    d.text((W - an - px * 1.2, px * 0.9), t, font=fo, fill=pal["tinta"] + (a,)
           if len(pal["tinta"]) == 4 else pal["tinta"])
    return im


def pie_fuente(im, texto, pal, u=1.0, px=28):
    """Credito de la fuente, abajo a la derecha, pequeno. Es lo que separa
    un dato de una opinion."""
    W, H = im.size
    d = ImageDraw.Draw(im)
    fo = vox.f(px, regular=True)
    an = d.textlength(texto, font=fo)
    x = W - an - px * 1.6
    y = H - px * 2.6 + (1 - _suave(u)) * px
    d.text((x, y), texto, font=fo, fill=pal["tinta"])
    d.rectangle([x - px * 0.5, y + px * 0.1, x - px * 0.28, y + px * 1.1],
                fill=pal["apoyo"])
    return im


def asterisco(im, xy, pal, u=1.0, r=30, grosor=8):
    """Asterisco dibujado a mano: tres trazos que salen del centro."""
    W, H = im.size
    cx, cy = xy[0] * W, xy[1] * H
    d = ImageDraw.Draw(im)
    s = _suave(u)
    for k in range(3):
        a = math.radians(30 + k * 60)
        dx, dy = math.cos(a) * r * s, math.sin(a) * r * s
        d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)],
               fill=pal["apoyo"], width=grosor)
    return im


def corchete(im, caja, pal, u=1.0, grosor=9, brazo=0.22):
    """Dos corchetes que encierran una zona. Acota sin tapar, que es lo que
    hace falta cuando el circulo taparia la cara del sujeto."""
    x0, y0, x1, y1 = [c * s for c, s in zip(caja, [im.size[0], im.size[1]] * 2)]
    d = ImageDraw.Draw(im)
    s = _suave(u)
    b = (y1 - y0) * brazo * s
    h = (y1 - y0) * s / 2
    for x, sig in ((x0, 1), (x1, -1)):
        d.line([(x, y0 + (y1-y0)/2 - h), (x, y0 + (y1-y0)/2 + h)],
               fill=pal["tinta"], width=grosor)
        d.line([(x, y0 + (y1-y0)/2 - h), (x + sig*b, y0 + (y1-y0)/2 - h)],
               fill=pal["tinta"], width=grosor)
        d.line([(x, y0 + (y1-y0)/2 + h), (x + sig*b, y0 + (y1-y0)/2 + h)],
               fill=pal["tinta"], width=grosor)
    return im


def bocadillo(im, xy, texto, pal, u=1.0, px=44):
    """Bocadillo de comic con rabo. Sale del sujeto y dice una frase corta."""
    W, H = im.size
    d = ImageDraw.Draw(im)
    fo = vox.f(px)
    an = d.textlength(texto, font=fo)
    an_c, al = an + px * 1.1, px * 2.0
    x, y = xy[0] * W, xy[1] * H
    s = _suave(u)
    if s < 0.05:
        return im
    caja = [x, y, x + an_c * s, y + al * s]
    d.rounded_rectangle(caja, px * 0.42, fill=pal["fondo"],
                        outline=pal["tinta"], width=6)
    if s > 0.6:
        d.polygon([(x + an_c * 0.22, y + al), (x + an_c * 0.36, y + al),
                   (x + an_c * 0.20, y + al + px * 0.6)],
                  fill=pal["fondo"], outline=pal["tinta"])
        d.text((x + px * 0.55, y + px * 0.42), texto, font=fo, fill=pal["tinta"])
    return im


def rejilla(im, pal, u=1.0, paso=96, grosor=2):
    """Rejilla tecnica de fondo. Solo en escenas de datos: dice 'esto se
    mide' sin escribirlo."""
    W, H = im.size
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    col = tuple(pal["tinta"]) + (int(38 * _suave(u)),)
    for x in range(0, W, paso):
        d.line([(x, 0), (x, H)], fill=col, width=grosor)
    for y in range(0, H, paso):
        d.line([(0, y), (W, y)], fill=col, width=grosor)
    im.paste(capa, (0, 0), capa)
    return im


# ---------------------------------------------------------------------------
# ENTRADAS
# El storyboard le pone a CADA capa su tipo de entrada y yo aplicaba el mismo
# muelle a todas. Ahi se perdia la mitad del movimiento: si las seis capas de
# una escena entran igual, se leen como una sola imagen apareciendo.
# ---------------------------------------------------------------------------

def entrada(tipo, u):
    """
    Devuelve (escala, dx, dy, alfa) para el avance `u` de 0 a 1.

    dx y dy van en fracciones de la propia pieza, no de la pantalla: una
    capa pequena tiene que recorrer poco y una grande mucho, o la pequena
    parece que no se mueve.
    """
    u = 0.0 if u < 0 else (1.0 if u > 1 else u)
    if u >= 1:
        return 1.0, 0.0, 0.0, 1.0
    s = _suave(u)
    if tipo == "sube":                       # entra desde debajo del borde
        return 1.0, 0.0, (1 - s) * 0.85, min(1.0, u * 2.2)
    if tipo == "cae":                        # cae desde arriba y asienta
        reb = 1 - math.exp(-6.0 * u) * math.cos(2.6 * math.pi * u)
        return 1.0, 0.0, -(1 - reb) * 0.70, min(1.0, u * 2.6)
    if tipo in ("lateral", "lateral_izq"):
        return 1.0, -(1 - s) * 1.10, 0.0, min(1.0, u * 2.4)
    if tipo == "lateral_der":
        return 1.0, (1 - s) * 1.10, 0.0, min(1.0, u * 2.4)
    if tipo == "barrido":                    # crece en horizontal
        return 1.0, 0.0, 0.0, min(1.0, u * 3.0)
    # `pop` es la de por defecto: escala desde 0,72 y rebasa el reposo
    reb = 1 - math.exp(-6.5 * u) * math.cos(1.7 * math.pi * u)
    return 0.72 + 0.28 * reb + (reb - 1) * 0.06, 0.0, 0.0, min(1.0, u * 2.0)


def maquina(im, lineas, pal, px=96, y0=None, u=1.0, cursor=True):
    """
    Texto a maquina de escribir: aparece letra a letra, con cursor.

    No es un capricho: en el video de referencia los remates entran asi y el
    efecto es que la frase se esta escribiendo AHORA, no que estaba puesta.
    Cambia como se lee la misma frase.
    """
    d = ImageDraw.Draw(im)
    W, H = im.size
    fo = vox.f(px)
    total = sum(len(l) for l in lineas)
    n = int(total * u)
    y = y0 if y0 is not None else H * 0.34
    puesto = 0
    for ln in lineas:
        if puesto >= n:
            break
        trozo = ln[:max(0, n - puesto)]
        limpio = trozo.replace("*", "")
        d.text((W * 0.08, y), limpio, font=fo, fill=pal["tinta"])
        if cursor and puesto + len(ln) > n:
            an = d.textlength(limpio, font=fo)
            d.rectangle([W * 0.08 + an + px * 0.06, y + px * 0.12,
                         W * 0.08 + an + px * 0.16, y + px * 0.92],
                        fill=pal["apoyo"])
        puesto += len(ln)
        y += px * 1.16
    return im


def ondula(t, amplitud=0.012, periodo=3.4):
    """
    Vaiven lento en vertical. Para el frente que tiene que parecer vivo -el
    agua, una llama, una multitud- sin ser un video: la capa entera sube y
    baja unos pocos pixeles y el ojo lo lee como movimiento propio.
    """
    return math.sin(2 * math.pi * t / periodo) * amplitud


def bloque_cifra(im, valor, pal, sufijo="", pie="", u=1.0, xy=(0.62, 0.16),
                 px=190, decimales=0):
    """
    El dato como un BLOQUE, no como un numero flotando en medio.

    En el material de referencia la cifra nunca esta suelta ni centrada: es
    una unidad compuesta -marca de color, numero grande, pie en versalitas-
    puesta en la parte vacia del encuadre. Centrado, el numero se cruza con
    los recortes y no se lee ni el uno ni el otro.
    """
    W, H = im.size
    x, y = xy[0] * W, xy[1] * H
    d = ImageDraw.Draw(im)
    s = _suave(u)
    t = f"{valor*s:,.{decimales}f}".replace(",", "@").replace(".", ",").replace("@", ".")
    t += sufijo
    fo = vox.f(px)
    an = d.textlength(t, font=fo)
    # marca de color a la izquierda, del alto del numero
    d.rectangle([x - px * 0.42, y + px * 0.10, x - px * 0.16, y + px * 0.92],
                fill=pal["apoyo"])
    d.text((x, y), t, font=fo, fill=pal["tinta"])
    if pie:
        fp = vox.f(int(px * 0.22))
        d.text((x, y + px * 1.02), pie.upper(), font=fp, fill=pal["tinta"])
    return im


def fondo_rejilla(W, H, celda=108, base=(228, 227, 224), linea=(243, 243, 240),
                  grosor=2, grano=3.0, veladura=1.5, semilla=11):
    """
    El fondo del video de referencia: papel gris claro con rejilla tenue.

    Se calcula, no se genera con IA. Un fondo asi es tres cosas -un tono
    plano, una rejilla y grano- y las tres salen mejor de una formula: sale
    a cualquier resolucion, no cuesta una generacion, y sobre todo NO TIENE
    CONTENIDO. Pedido a un modelo acaba con manchas, una esquina mas oscura
    o una textura que se reconoce al repetirse doscientas veces.

    Tres detalles que lo separan de un cuadriculado de hoja de calculo:

      La linea es MAS CLARA que el fondo, no mas oscura. Es una marca de
      agua en el papel, no una cuadricula impresa encima.

      Va desenfocada medio pixel. Una linea de un pixel exacto se lee como
      interfaz; difuminada se lee como impresa.

      Y el tono no es plano: lleva una veladura muy suave de baja
      frecuencia, que es lo que hace que parezca papel y no un relleno.
    """
    r = np.random.default_rng(semilla)
    a = np.zeros((H, W, 3), np.float32) + np.array(base, np.float32)

    # veladura de baja frecuencia: manchas anchas y suavisimas
    # MUY suave: con desviacion 5,5 salian manchas que se ven, y el fondo
    # de referencia es casi uniforme. Lo que tiene que notarse es el grano
    # fino, no el nublado.
    ch, cw = max(2, H // 160), max(2, W // 160)
    manchas = r.normal(0, veladura, (ch, cw)).astype(np.float32)
    manchas = np.asarray(Image.fromarray(manchas, "F").resize((W, H), Image.BICUBIC))
    a += manchas[..., None]

    # rejilla, en su propia capa para poder desenfocarla
    rej = np.zeros((H, W), np.float32)
    for x in range(0, W + celda, celda):
        rej[:, max(0, x - grosor // 2):x + grosor - grosor // 2] = 1.0
    for y in range(0, H + celda, celda):
        rej[max(0, y - grosor // 2):y + grosor - grosor // 2, :] = 1.0
    rej = np.asarray(Image.fromarray((rej * 255).astype(np.uint8))
                     .filter(ImageFilter.GaussianBlur(0.9)), np.float32) / 255.0
    a += rej[..., None] * (np.array(linea, np.float32) - np.array(base, np.float32))

    a += r.normal(0, grano, (H, W, 1))          # grano de papel
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")
