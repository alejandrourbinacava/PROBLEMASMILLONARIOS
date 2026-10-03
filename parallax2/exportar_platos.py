#!/usr/bin/env python3
"""
Saca de un guion los planos de PLATO, con todo lo que Remotion necesita para
dibujarlos, y dice como se tiene que llamar cada fichero.

    python3 exportar_platos.py proyecto/mercadona.json platos.json

Un plano de plato es el que no lleva metraje: el fondo de papel del canal, un
grafico o un icono, y a veces un titular. Es donde el motor de Pillow se nota
mas -tarjetas con animacion de fotograma a fotograma, sin curvas de verdad- y
donde Remotion rinde mejor, asi que son los que se le pasan. El resto del
episodio (metraje con grade, Ken Burns, grano) sigue en `render.py`.

Hay un detalle que no se puede equivocar: el NOMBRE y el NUMERO DE FOTOGRAMAS.
`render_par.py` salta cualquier plano cuyo fichero `_escenas/NNN_id.mp4` ya
exista, y `montar.py` cuenta con que dure `duracion + sangrado`. Si Remotion
deja ahi un fichero con el nombre bien y los fotogramas bien, el resto del
motor no se entera y la voz sigue cuadrando.
"""
import copy
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(AQUI))

import efectos as FX
import render as R


def _rgb(v, papel="acento"):
    return [int(c) for c in FX._col(v, papel)]


def resuelve_colores(g):
    """Pasa a RGB los 'papeles' de una ficha: Remotion no conoce el tema."""
    tipo = g.get("tipo", "contador")
    g["_ac"] = _rgb(g.get("color"), FX._POR_TIPO.get(tipo, "acento"))
    if g.get("destacar"):
        g["_destacar"] = {k: _rgb(v, "serie") for k, v in g["destacar"].items()}
    if g.get("colores"):
        g["_colores"] = {k: _rgb(v) for k, v in g["colores"].items()}
    if tipo == "reparto":
        g["_color_a"] = _rgb(g.get("color_a"), "acento")
    if tipo == "rejilla":
        g["_color_base"] = _rgb(g.get("color_base"), "tenue")
        g["_color_marca"] = _rgb(g.get("color_marca"), "acento")
    return g


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    ruta, destino = sys.argv[1], sys.argv[2]
    sys.stdout.reconfigure(encoding="utf-8")

    guion = json.load(open(ruta, encoding="utf-8"))
    FX.tema(guion.get("tema", "papel"))
    guion = R.preparar(guion)
    cfg = {**dict(w=1920, h=1080, fps=25, ppm=140), **guion.get("lienzo", {})}
    FPS = cfg["fps"]

    platos, latigos = [], 0
    for i, e in enumerate(guion["escenas"]):
        if e.get("clip") or not e.get("fondo"):
            continue
        n = int(FPS * (e.get("duracion", 8) + e.get("_sangrado", 0.0)))
        txt = copy.deepcopy(e.get("texto_pantalla"))
        if txt and txt.get("retardo") is None:
            r = R.retardo_rotulo(e, cfg.get("ppm", 140))
            # None = la palabra que lo dispara no se dice en este plano: el
            # motor de Pillow no lo dibuja, y aqui tampoco.
            txt = None if r is None else {**txt, "retardo": r}
        graf = resuelve_colores(copy.deepcopy(e["grafico"])) if e.get("grafico") else None
        if e.get("_lat_ent") is not None or e.get("_lat_sal") is not None:
            latigos += 1
        platos.append({
            "archivo": "%03d_%s.mp4" % (i, e["id"]),
            "frames": n,
            "id": e["id"],
            "duracion": e.get("duracion", 8),
            "fondo_titulo": e.get("fondo_titulo") or "",
            "acento": _rgb(e.get("fondo_color")),
            "fase": float(e.get("fondo_fase", 0.0)),
            "grafico": graf,
            "texto_pantalla": txt,
            "lat_ent": e.get("_lat_ent"),
            "lat_sal": e.get("_lat_sal"),
        })

    paleta = {k: (list(v) if isinstance(v, tuple) else v)
              for k, v in FX.PALETA.items()}
    salida = {"fps": FPS, "w": cfg["w"], "h": cfg["h"], "paleta": paleta,
              "total": len(guion["escenas"]), "platos": platos}
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
    seg = sum(p["frames"] for p in platos) / float(FPS)
    print("%d planos de plato de %d (%.1f min) -> %s"
          % (len(platos), len(guion["escenas"]), seg / 60.0, destino))
    if latigos:
        print("AVISO: %d planos con latigo de escena; Remotion todavia no lo "
              "hace y esos planos saldrian sin el" % latigos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
