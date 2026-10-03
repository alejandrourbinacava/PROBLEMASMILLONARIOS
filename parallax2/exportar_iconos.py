#!/usr/bin/env python3
"""
Exporta los pictogramas de `iconos.py` como DATOS para Remotion.

    python3 exportar_iconos.py ../remotion/public/p2/iconos.json

Los treinta y cinco iconos del canal estan escritos como funciones de Python
que dibujan con PIL. Remotion no puede llamarlas, y reescribirlos a mano en
SVG seria perder la fuente de verdad: el dia que se toque un icono habria que
tocarlo en dos sitios. Aqui se ejecuta CADA funcion contra un lienzo falso que
anota lo que se le pide -lineas, circulos, rectangulos, arcos- y se guarda
como JSON. Cambias `iconos.py`, vuelves a exportar, y los dos motores dibujan
lo mismo.

Cada trazo lleva el `paso` en el que entra (0, 1, 2...): es lo que permite a
Remotion DIBUJARLOS uno detras de otro, en vez de aparecer de golpe. Todo va
en una caja de 1000 x 1000, con el grosor que le daria `dibuja` a un icono de
esa caja (45).
"""
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import iconos as I

CAJA = (0, 0, 1000, 1000)
GROSOR = max(4, int(1000 * 0.045))


class Lienzo:
    """Hace de `ImageDraw`: no dibuja, anota."""

    def __init__(self):
        self.prims = []
        self.paso = 0

    def _add(self, **kw):
        kw["s"] = self.paso
        self.prims.append(kw)

    def line(self, pts, fill=None, width=1, joint=None):
        self._add(t="l", p=[[round(x, 2), round(y, 2)] for x, y in pts],
                  w=width)

    def ellipse(self, box, outline=None, width=1, fill=None):
        x0, y0, x1, y1 = box
        self._add(t="c", cx=round((x0 + x1) / 2, 2), cy=round((y0 + y1) / 2, 2),
                  r=round((x1 - x0) / 2, 2), f=bool(fill) and not outline,
                  w=width)

    def rectangle(self, box, outline=None, width=1, fill=None):
        x0, y0, x1, y1 = box
        self._add(t="r", x=round(x0, 2), y=round(y0, 2), w_=round(x1 - x0, 2),
                  h=round(y1 - y0, 2), rx=0, w=width, f=bool(fill) and not outline)

    def rounded_rectangle(self, box, radius=0, outline=None, width=1, fill=None):
        x0, y0, x1, y1 = box
        self._add(t="r", x=round(x0, 2), y=round(y0, 2), w_=round(x1 - x0, 2),
                  h=round(y1 - y0, 2), rx=round(radius, 2), w=width,
                  f=bool(fill) and not outline)

    def polygon(self, pts, fill=None, outline=None, width=1):
        self._add(t="p", p=[[round(x, 2), round(y, 2)] for x, y in pts],
                  f=bool(fill))

    def arc(self, box, start, end, fill=None, width=1):
        x0, y0, x1, y1 = box
        self._add(t="a", cx=round((x0 + x1) / 2, 2), cy=round((y0 + y1) / 2, 2),
                  r=round((x1 - x0) / 2, 2), a0=start, a1=end, w=width)

    def text(self, *a, **k):          # ningun icono escribe texto
        raise RuntimeError("un icono no deberia escribir texto")


def exporta(nombre, fn):
    d = Lienzo()

    def paso(i):
        d.paso = i
        return True

    # Los helpers dibujan en el lienzo falso; los linea/circulos de remate que
    # PIL necesita a mano (no tiene remate redondo) no hacen falta: en SVG es
    # `stroke-linecap: round`.
    def lin(d_, caja, pts, col, gr, cerrado=False):
        p = [I._pt(caja, a, b) for a, b in pts]
        if cerrado:
            p = p + [p[0]]
        if len(p) >= 2:
            d_.line(p, fill=col, width=gr)

    viejo = I._lin
    I._lin = lin
    # `_circ` y `_caja` ya hablan en terminos del lienzo; `_punta` llama a
    # `_lin` con la caja unidad y a `polygon`, que tambien anotamos.
    try:
        fn(d, CAJA, (0, 0, 0, 255), GROSOR, paso)
    finally:
        I._lin = viejo
    return d.prims


def main():
    destino = sys.argv[1] if len(sys.argv) > 1 else "iconos.json"
    salida = {"grosor": GROSOR, "iconos": {}}
    for nombre, fn in I.ICONOS.items():
        prims = exporta(nombre, fn)
        pasos = sorted({p["s"] for p in prims})
        salida["iconos"][nombre] = {"prims": prims, "pasos": pasos}
        print("  %-11s %2d trazos en %d pasos" % (nombre, len(prims), len(pasos)))
    os.makedirs(os.path.dirname(os.path.abspath(destino)), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, separators=(",", ":"))
    print("%d iconos -> %s" % (len(salida["iconos"]), destino))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
