"""Puntos repartidos dentro de la silueta de un pais, para los mapas animados.

    python puntos_mapa.py ESP=1603 PRT=1000 ...   -> remotion/src/vox/video/puntos.ts

Lee las siluetas de `europa.ts` (Natural Earth) y reparte N puntos al azar
dentro de cada pais, con una separacion minima para que no se monten. Las
coordenadas son las del propio mapa (1000 x 967).
"""
import io
import json
import os
import random
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
VIDEO = os.path.join(AQUI, "..", "remotion", "src", "vox", "video")


def poligonos(d):
    out = []
    for trozo in d.split("M")[1:]:
        pts = [tuple(float(v) for v in p.split(",")) for p in re.findall(r"-?[\d.]+,-?[\d.]+", trozo)]
        if len(pts) >= 3:
            out.append(pts)
    return out


def area(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2.0


def dentro(p, x, y):
    c = False
    j = len(p) - 1
    for i in range(len(p)):
        (xi, yi), (xj, yj) = p[i], p[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def reparte(polis, n, rng):
    polis = [p for p in polis if area(p) > 0.4]
    total = sum(area(p) for p in polis)
    sep = 0.62 * (total / n) ** 0.5
    pts = []
    for p in sorted(polis, key=area, reverse=True):
        quiero = max(1, int(round(n * area(p) / total)))
        xs, ys = [q[0] for q in p], [q[1] for q in p]
        mios, intentos, s = [], 0, sep
        while len(mios) < quiero and intentos < 400000:
            intentos += 1
            if intentos % 20000 == 0:
                s *= 0.9
            x, y = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
            if not dentro(p, x, y):
                continue
            if any((x - a) ** 2 + (y - b) ** 2 < s * s for a, b in mios):
                continue
            mios.append((x, y))
        pts += mios
    rng.shuffle(pts)
    return pts[:n]


def main():
    src = io.open(os.path.join(VIDEO, "europa.ts"), encoding="utf-8").read()
    datos = json.loads(src[src.index("= {", src.index("EUROPA:")) + 2:].rstrip().rstrip(";"))
    rng = random.Random(7)
    out = {}
    for a in sys.argv[1:]:
        cod, n = a.split("=")
        pts = reparte(poligonos(datos[cod]["d"]), int(n), rng)
        out[cod] = [[round(x, 1), round(y, 1)] for x, y in pts]
        print(cod, len(pts))
    with io.open(os.path.join(VIDEO, "puntos.ts"), "w", encoding="utf-8", newline="\n") as f:
        f.write("// Puntos dentro de cada pais (coordenadas de europa.ts). Generado por vox/puntos_mapa.py: no editar a mano.\n")
        f.write("export const PUNTOS: Record<string, [number, number][]> = %s;\n" % json.dumps(out, separators=(",", ":")))


if __name__ == "__main__":
    main()
