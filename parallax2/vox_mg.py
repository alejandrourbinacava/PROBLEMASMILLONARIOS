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
