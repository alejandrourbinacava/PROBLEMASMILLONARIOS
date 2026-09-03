#!/usr/bin/env python3
"""
La hoja de calculo del banco, en vectorial plano. Escribe un SVG.

    python3 plano_vector.py

No hay dependencias: es texto. Y no hay coordenadas escritas a mano -eso
seria imposible de mantener-: se declara la escena en unidades de mundo y
`iso()` la proyecta. Cambiar el angulo de camara es cambiar una constante,
no volver a dibujarlo todo.

Es la version barata de las tres: un SVG pesa kilobytes, sale nitido a 4K
y se recolorea entero cambiando la paleta de aqui abajo.
"""
import math
import os

W, H = 1920, 1080
CX, CY = W / 2, H / 2 + 60
COS30, SEN30 = math.cos(math.radians(30)), math.sin(math.radians(30))

# LA PALETA DEL CANAL. Todo lo que se pinta sale de aqui.
FONDO = "#0B1220"
PAPEL = "#EDE7DA"
TINTA = "#0B1220"
FRIO = "#7A92B2"
ROJO = "#E85640"
AMBAR = "#FFB03C"
HUMO = "#1B2436"


def sombra(hex_col, f):
    """Oscurece un color. Las tres caras de un bloque no pueden ser iguales."""
    r, g, b = (int(hex_col[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))


def iso(x, y, z=0.0):
    return (CX + (x - y) * COS30, CY + (x + y) * SEN30 - z)


def poli(pts, relleno, borde=TINTA, grosor=3.0, opacidad=1.0):
    d = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return (f'<polygon points="{d}" fill="{relleno}" stroke="{borde}" '
            f'stroke-width="{grosor}" stroke-linejoin="round" '
            f'opacity="{opacidad}"/>')


def bloque(x, y, hw, hd, z0, alto, color, grosor=3.0):
    """Un prisma en isometrico. Solo se dibujan las tres caras que se ven."""
    ci = sombra(color, 0.74)   # cara +x
    cd = sombra(color, 0.55)   # cara +y, la mas oscura
    a, b = x - hw, x + hw
    c, d = y - hd, y + hd
    z1 = z0 + alto
    tapa = [iso(a, c, z1), iso(b, c, z1), iso(b, d, z1), iso(a, d, z1)]
    lat_x = [iso(b, c, z1), iso(b, d, z1), iso(b, d, z0), iso(b, c, z0)]
    lat_y = [iso(a, d, z1), iso(b, d, z1), iso(b, d, z0), iso(a, d, z0)]
    return "".join([poli(lat_x, ci, grosor=grosor),
                    poli(lat_y, cd, grosor=grosor),
                    poli(tapa, color, grosor=grosor)])


def pila(x, y, hw, hd, n, alto, hueco, color, z0=0.0):
    """Una columna de losas. Se pinta de abajo arriba o se tapan mal."""
    fuera = []
    for i in range(n):
        fuera.append(bloque(x, y, hw, hd, z0 + i * (alto + hueco), alto, color))
    return "".join(fuera)


def texto(x, y, txt, px=34, color=PAPEL, peso=700, anclaje="middle",
          espaciado=2.0, opacidad=1.0):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{px}" '
            f'font-family="Inter, Segoe UI, Helvetica Neue, Arial, sans-serif" '
            f'font-weight="{peso}" fill="{color}" text-anchor="{anclaje}" '
            f'letter-spacing="{espaciado}" opacity="{opacidad}">{txt}</text>')


def escena():
    p = []

    # --- fondo y una rejilla muy tenue: sigue siendo una hoja de calculo
    p.append(f'<rect width="{W}" height="{H}" fill="{FONDO}"/>')
    rej = []
    for i in range(-11, 12):
        x0, y0 = iso(i * 40, -440)
        x1, y1 = iso(i * 40, 440)
        rej.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" '
                   f'y2="{y1:.1f}"/>')
        x0, y0 = iso(-440, i * 40)
        x1, y1 = iso(440, i * 40)
        rej.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" '
                   f'y2="{y1:.1f}"/>')
    p.append(f'<g stroke="{HUMO}" stroke-width="1.6">{"".join(rej)}</g>')

    # --- LA HOJA
    p.append(bloque(0, 0, 330, 330, -26, 26, PAPEL, grosor=3.5))

    # Las dos columnas van en la diagonal CONTRARIA a la de la camara. Si las
    # pones en la misma -las dos con y=0- se tapan la una a la otra, porque en
    # isometrico esa diagonal es la de profundidad, no la de anchura.
    D = 170
    for s in (-1, 1):
        a, b = iso(-s * D - 100, s * D - 100), iso(-s * D + 100, s * D + 100)
        p.append(poli([iso(-s*D-100, s*D-100, -26), iso(-s*D+100, s*D-100, -26),
                       iso(-s*D+100, s*D+100, -26), iso(-s*D-100, s*D+100, -26)],
                      sombra(PAPEL, 0.86), borde="none", grosor=0))

    # depositos a la izquierda y mas altos: siempre hay mas depositado que
    # prestado, y esa es la regla del capitulo.
    p.append(pila(-D, D, 100, 100, 9, 20, 7, FRIO))
    p.append(pila(D, -D, 100, 100, 6, 20, 7, ROJO))

    # --- EL MARGEN: una lamina de nueve unidades de grosor entre las dos
    #     columnas, y lo unico de la escena que emite luz.
    p.append(f'<g filter="url(#brillo)">{bloque(0, 0, 62, 5, 0, 58, AMBAR, grosor=2.0)}</g>')

    # --- rotulos
    ix, dx = CX - (2 * D) * COS30, CX + (2 * D) * COS30
    p.append(texto(ix, 906, "DEPÓSITOS", 30, FRIO, espaciado=5))
    p.append(texto(ix, 944, "lo que la gente dejó", 24, sombra(PAPEL, 0.60),
                   peso=400, espaciado=0))
    p.append(texto(dx, 906, "PRÉSTAMOS", 30, ROJO, espaciado=5))
    p.append(texto(dx, 944, "lo que el banco prestó", 24,
                   sombra(PAPEL, 0.60), peso=400, espaciado=0))

    # el margen se rotula arriba, con una guia hasta la lamina
    px, py = iso(0, 0, 58)
    p.append(f'<line x1="{px:.1f}" y1="{py - 16:.1f}" x2="{px:.1f}" '
             f'y2="188" stroke="{AMBAR}" stroke-width="2" opacity="0.5"/>')
    p.append(texto(W / 2, 168, "EL MARGEN", 28, AMBAR, espaciado=6))
    p.append(texto(W / 2, 118, "3,22 %", 74, PAPEL, espaciado=1))

    p.append(texto(W / 2, 1028, "El banco de verdad es una hoja de cálculo.",
                   33, sombra(PAPEL, 0.76), peso=500, espaciado=0))
    return "".join(p)


def main():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <filter id="brillo" x="-160%" y="-160%" width="420%" height="420%">
    <feGaussianBlur stdDeviation="26" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/>
             <feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
{escena()}
</svg>'''
    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "salida", "a_vector.svg")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"escrito {destino}  ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
