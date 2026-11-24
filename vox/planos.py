"""Guiones tecnicos con planos libres (remotion/src/vox/video/libre.tsx).

Un guion (`vox/<tema>.py`) crea un `Guion`, le va anadiendo planos y cartelas, y lo escribe:

    from planos import *
    G = Guion("zara", MARCA, medios=["parallax2/proyecto/stock_mercadona"])
    G.plano(0, [(0, 0), (0, "su talla")], [im("g_percha", 500, 1080, 520), tit("...", 1300, 200, p=1)],
            fuente="...", clips=["f_tienda"])
    G.cap(6, 1, "Titulo con *acento*", "subtitulo", el="g_percha", ew=420, clips=["f_tienda"])
    if __name__ == "__main__": G.escribe()

Cada pieza es un diccionario de atras a delante. `p` es el paso en el que entra (0 = al empezar),
`dt` fotogramas de retraso, `sale` el paso en el que se va. Las posiciones son del lienzo 1920x1080:
en los textos (x, y) es el centro vertical y la izquierda, el centro o la derecha segun `a`
("i", "c", "d"); en las imagenes, el centro de la base.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from tecnico import Media, Tiempos, construye  # noqa: E402


def _i(k, p, dt, sale, **d):
    d = {a: b for a, b in d.items() if b is not None}
    d["k"] = k
    if p:
        d["p"] = p
    if dt:
        d["dt"] = dt
    if sale is not None:
        d["sale"] = sale
    return d


def im(src, x, y, w, p=0, dt=0, sale=None, de="aba", **k):
    return _i("im", p, dt, sale, src=src, x=x, y=y, w=w, de=de, **k)


def tit(t, x=960, y=120, p=0, dt=0, sale=None, a="c", tam=78, **k):
    return _i("tit", p, dt, sale, t=t, x=x, y=y, ancla=a, tam=tam, **k)


def par(t, x, y, w, p=0, dt=0, sale=None, tam=52, **k):
    return _i("par", p, dt, sale, t=t, x=x, y=y, w=w, tam=tam, **k)


def dato(cifra, x, y, pie=None, p=0, dt=0, sale=None, a="c", tam=170, color="ambar", **k):
    return _i("dato", p, dt, sale, cifra=cifra, pie=pie, x=x, y=y, ancla=a, tam=tam, color=color, **k)


def chip(t, x, y, p=0, dt=0, sale=None, a="c", tam=46, color="humo", **k):
    return _i("chip", p, dt, sale, t=t, x=x, y=y, ancla=a, tam=tam, color=color, **k)


def sello(t, x, y, p=0, dt=0, sale=None, tam=68, **k):
    return _i("sello", p, dt, sale, t=t, x=x, y=y, tam=tam, **k)


def eti(t, x, y, p=0, dt=0, sale=None, a="c", tam=28, **k):
    return _i("eti", p, dt, sale, t=t, x=x, y=y, ancla=a, tam=tam, **k)


def detras(t, x, y, p=0, dt=0, sale=None, tam=260, **k):
    return _i("detras", p, dt, sale, t=t, x=x, y=y, tam=tam, **k)


def hoja(anio, x=190, y=160, p=0, dt=0, sale=None, **k):
    return _i("hoja", p, dt, sale, t=str(anio), x=x, y=y, **k)


def marca(tipo, x, y, p=0, dt=0, sale=None, s=4, **k):
    return _i(tipo, p, dt, sale, x=x, y=y, s=s, **k)


def flecha(x0, y0, x1, y1, p=0, dt=0, sale=None, **k):
    return _i("flecha", p, dt, sale, x0=x0, y0=y0, x1=x1, y1=y1, **k)


def barra(x, y, w, p=0, dt=0, sale=None, t=None, color="ambar", **k):
    return _i("barra", p, dt, sale, x=x, y=y, w=w, t=t, color=color, **k)


def col(t, x, y, alto, pie=None, p=0, dt=0, sale=None, color="cian", **k):
    return _i("col", p, dt, sale, t=t, x=x, y=y, alto=alto, pie=pie, color=color, **k)


def linea(t, x, y, p=0, dt=0, sale=None, tam=50, **k):
    return _i("linea", p, dt, sale, t=t, x=x, y=y, tam=tam, **k)


def cita(t, x, y, w, p=0, dt=0, sale=None, tam=66, **k):
    return _i("cita", p, dt, sale, t=t, x=x, y=y, w=w, tam=tam, **k)


def div(x, y, w=2, h=720, p=0, dt=0, sale=None):
    return _i("div", p, dt, sale, x=x, y=y, w=w, h=h)


def reparto(x, y, w, partes, p=0, dt=0, sale=None, **k):
    return _i("reparto", p, dt, sale, x=x, y=y, w=w, partes=partes, **k)


def serie(x, y, w, h, series, ejes=None, p=0, dt=0, sale=None, **k):
    return _i("serie", p, dt, sale, x=x, y=y, w=w, h=h, series=series, ejes=ejes, **k)


def rejilla(n, cols, x, y, p=0, dt=0, sale=None, **k):
    return _i("rejilla", p, dt, sale, n=n, cols=cols, x=x, y=y, **k)


def mapa(p=0, dt=0, sale=None, **k):
    return _i("mapa", p, dt, sale, **k)


def velo(p=0, dt=0, sale=None, **k):
    return _i("velo", p, dt, sale, **k)


def quien(nombre, cargo, x=110, y=150, p=0, tam=100):
    """Nombre grande y su cargo debajo (para las citas)."""
    return [tit(nombre, x, y, p=p, a="i", tam=tam), eti(cargo, x + 4, y + tam * 0.78, p=p, dt=5, a="i", tam=27)]


class Guion:
    def __init__(self, tema, marca, medios=None, color_cap=None):
        self.tema, self.marca = tema, marca
        self.S = []
        self.media = Media((medios or ["parallax2/proyecto/stock_mercadona"]) + ["vox/media/" + tema],
                           os.path.join(AQUI, tema + ".media.json"))

    def plano(self, de, pasos, items, fuente=None, clips=None, cap=None, **d):
        plana = []
        for it in items:
            plana.extend(it if isinstance(it, list) else [it])
        e = {"tipo": "anim", "de": de, "d": dict(comp="libre", items=plana, **d), "pasos": pasos}
        if fuente:
            e["fuente"] = fuente
        if clips:
            e["fondo_clip"] = [{"a": c, "paso": None} if isinstance(c, str) else {"a": c[0], "paso": c[1]} for c in clips]
        if cap is not None:
            e["cap"] = cap
        self.S.append(e)

    def cap(self, de, num, titulo, sub=None, clips=None, **d):
        self.S.append({"tipo": "capitulo", "de": de, "d": dict(num=str(num), titulo=titulo, sub=sub, **d),
                       "pasos": [de if isinstance(de, tuple) else (de, 0), (de[0] if isinstance(de, tuple) else de, 0.03)], "cap": str(num),
                       "fondo_clip": [{"a": c, "paso": None} for c in (clips or [])]})

    def escribe(self, carpeta):
        base = os.path.abspath(os.path.join(AQUI, "..", "..", carpeta))
        loc = os.path.join(AQUI, self.tema + ".locucion.txt")
        if not os.path.exists(loc):
            loc = os.path.join(base, "locucion.txt")
        voz = os.path.join(AQUI, self.tema + ".voz.json")
        if not os.path.exists(voz):
            voz = os.path.join(base, "voz.json")
        return construye(Tiempos(loc, voz), self.S, self.marca, os.path.join(AQUI, self.tema + ".spec.json"), self.media, piel="anim")
