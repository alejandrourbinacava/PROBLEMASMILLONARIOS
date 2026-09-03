#!/usr/bin/env python3
"""
Convierte una imagen -de Meta AI, de stock, de donde sea- en vector plano
con la paleta del canal.

    python3 trazar.py ../parallax2/proyecto/meta/f_balanza.png

Dos pasos. vtracer saca los contornos, que ya no es un PNG: es un SVG de
verdad, nitido a cualquier tamano. Y despues cada relleno se lleva al color
mas cercano de la paleta. Ese segundo paso es el que importa: es lo que
convierte una imagen generada en una pieza DEL CANAL en vez de una imagen
suelta. Sin el, sigue siendo lo que escupio el generador.
"""
import argparse
import io
import os
import re
import sys

# La paleta del canal. Todo relleno acaba en uno de estos.
FONDO = (11, 18, 32)
# La linea NO puede ser del color del fondo. El dibujo venia hecho con trazo
# negro sobre blanco; sobre azul noche el negro desaparece y las cuerdas de
# la balanza se van con el. Se invierte: trazo claro sobre fondo oscuro.
LINEA = (74, 94, 128)
PAPEL = (237, 231, 218)
FRIO = (122, 146, 178)
ROJO = (232, 86, 64)
AMBAR = (255, 176, 60)
PALETA = [LINEA, PAPEL, FRIO, ROJO, AMBAR]

# Por encima de esta luminancia el relleno es el fondo blanco del generador
# y se tira. Si no, el recorte queda dentro de un ladrillo blanco.
BLANCO = 232


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def cerca(c):
    """El color de paleta mas parecido. Se pesa mas el tono que el brillo:
    comparar en RGB a secas manda los grises al rojo."""
    def d(p):
        dl = (lum(c) - lum(p)) ** 2
        dc = sum((a - b) ** 2 for a, b in zip(c, p))
        return dl * 2.2 + dc
    return min(PALETA, key=d)


def hexa(c):
    return "#%02X%02X%02X" % c


def de_hexa(s):
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def repintar(svg):
    """Sustituye cada fill por su equivalente de paleta. Devuelve tambien el
    recuento, que es lo unico que dice si el trazado ha salido bien: un
    trazado con cuatrocientos colores es un degradado mal cortado."""
    vistos = {}

    def cambia(m):
        crudo = m.group(1)
        if not crudo.startswith("#"):
            return m.group(0)
        c = de_hexa(crudo)
        vistos[crudo] = vistos.get(crudo, 0) + 1
        if lum(c) >= BLANCO:
            return 'fill="none"'
        return 'fill="%s"' % hexa(cerca(c))

    return re.sub(r'fill="([^"]+)"', cambia, svg), vistos


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("imagen")
    ap.add_argument("--salida", default=None)
    ap.add_argument("--mota", type=int, default=6,
                    help="tamano en px por debajo del cual la mancha se tira")
    ap.add_argument("--colores", type=int, default=6)
    a = ap.parse_args()

    import vtracer

    aqui = os.path.dirname(os.path.abspath(__file__))
    destino = a.salida or os.path.join(aqui, "salida", "b_trazado.svg")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    bruto = destino.replace(".svg", "_bruto.svg")

    vtracer.convert_image_to_svg_py(
        a.imagen, bruto,
        colormode="color", hierarchical="stacked", mode="spline",
        filter_speckle=a.mota, color_precision=a.colores,
        layer_difference=18, corner_threshold=62,
        length_threshold=4.0, splice_threshold=45, path_precision=6)

    svg = io.open(bruto, encoding="utf-8").read()
    svg, vistos = repintar(svg)

    # un fondo de canal detras, que el trazado sale transparente
    m = re.search(r'viewBox="([^"]+)"', svg)
    if not m:
        m2 = re.search(r'width="(\d+)"\s+height="(\d+)"', svg)
        vb = f"0 0 {m2.group(1)} {m2.group(2)}" if m2 else "0 0 2048 1152"
        svg = svg.replace("<svg", f'<svg viewBox="{vb}"', 1)
    else:
        vb = m.group(1)
    x, y, w, h = (float(v) for v in vb.split())
    svg = re.sub(r"(<svg[^>]*>)",
                 r'\1<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>'
                 % (x, y, w, h, hexa(FONDO)), svg, count=1)

    io.open(destino, "w", encoding="utf-8").write(svg)
    os.remove(bruto)
    print(f"{len(vistos)} colores en el trazado -> {len(PALETA)} de paleta")
    print(f"escrito {destino}  ({len(svg) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
