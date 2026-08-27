"""Lleva la mezcla de tipos a la que pide el documento de escenas.

`mezcla_objetivo` pide 45% clip, 30% grafico y 25% capas. Salia 79/14/6.

Las capas suben SIN generar imagenes nuevas. Cada decorado montado -cielo,
fondo, suelo y sujeto- da varios planos si se cambia la camara: un empuje, un
paneo lateral, un plano corto del sujeto. Es lo que hace MagnatesMedia, que
construye un set y lo rueda desde tres sitios, y es tambien lo que pide la
regla del documento -las capas se reservan al gancho, a la apertura de cada
capitulo y a las revelaciones- porque reservarlas a esos momentos significa que
esos momentos DUREN, no que tengan un plano suelto.

Se comprueba en el propio documento: los 57 segundos escritos a mano llevan
360 frames de capas de 1.415, que es exactamente el 25%.

Los graficos suben pasando a cifra los planos cuya frase trae un dato y estaba
cayendo en metraje por no llevar la unidad pegada al numero.

    python scripts/rebalancear.py
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

FPS = 25
# Cuanto dura la apertura por capas de un capitulo.
APERTURA = 20 * FPS
OBJETIVO_GRAFICO = 0.30

# Como se rueda cada decorado. Un plano por entrada, en este orden.
MIRADAS = [
    # empuje frontal, el que ya venia
    {"zoom": [1.0, 1.14], "x": [0, -18]},
    # paneo lateral: es lo que hace VISIBLE la separacion en capas, porque
    # descubre lo que estaba tapado. Un empuje solo se parece a un zoom.
    {"zoom": [1.08, 1.16], "x": [-70, 90]},
    # plano mas cerrado y contrario, para que el corte se note
    {"zoom": [1.22, 1.30], "x": [60, -40], "y": [0, -10]},
    # retroceso lento, deja respirar antes de entrar en el capitulo
    {"zoom": [1.26, 1.06], "x": [30, 0]},
]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escenas", type=Path,
                   default=Path("remotion/public/episodio/escenas.json"))
    p.add_argument("--objetivo", type=float, default=0.25)
    args = p.parse_args()

    spec = json.loads(args.escenas.read_text(encoding="utf-8"))
    escenas = spec["escenas"]
    total = sum(e["duracion"] for e in escenas)
    quiere = total * args.objetivo

    salida: list[dict] = []
    for escena in escenas:
        salida.append(escena)
        if escena["tipo"] != "capas":
            continue

        # Los planos que siguen a un decorado se le ceden: en vez de cortar a
        # metraje, se sigue rodando el mismo set. Se toman de los clips que
        # vienen justo detras, que es el momento reservado del que habla la
        # regla.
        escena["_set"] = True

    # Cuantos segundos hay que convertir
    hay = sum(e["duracion"] for e in salida if e["tipo"] == "capas")
    falta = quiere - hay

    resultado: list[dict] = []
    i = 0
    while i < len(salida):
        e = salida[i]
        resultado.append(e)
        i += 1
        if not e.pop("_set", False) or falta <= 0:
            continue
        # Se convierten los siguientes planos de metraje del mismo bloque,
        # hasta tres, rodando el mismo decorado con otra camara.
        # El decorado cubre la apertura de su capitulo, no tres planos
        # sueltos: se sigue rodando mientras la apertura dure menos de lo que
        # le toca. Ese es el sentido de "reservarlas a esos momentos".
        # El decorado cubre la apertura de su capitulo, no tres planos
        # sueltos: ese es el sentido de "reservarlas a esos momentos". Un
        # grafico por medio no corta la apertura, se queda donde esta y se
        # sigue rodando el set despues de el, que es como se monta: se ensena
        # la cifra y se vuelve al decorado.
        hechos = 0
        cubierto = e["duracion"]
        while i < len(salida) and cubierto < APERTURA and falta > 0:
            sig = salida[i]
            if sig.get("bloque") != e.get("bloque"):
                break
            if sig["tipo"] != "clip":
                resultado.append(sig)
                i += 1
                continue
            nuevo = copy.deepcopy(e)
            nuevo["id"] = f"{e['id']}_v{hechos + 2}"
            nuevo["duracion"] = sig["duracion"]
            nuevo["locucion"] = sig.get("locucion", "")
            nuevo["camara"] = MIRADAS[(hechos + 1) % len(MIRADAS)]
            # El rotulo va una sola vez, en el primer plano del decorado.
            for campo in ("texto", "clips", "busqueda", "credito", "parecido"):
                nuevo.pop(campo, None)
            resultado.append(nuevo)
            falta -= sig["duracion"]
            cubierto += sig["duracion"]
            hechos += 1
            i += 1

    # ---- Graficos: del 14% al 30% ----
    #
    # Una frase corta y cerrada no necesita metraje que la ilustre, necesita
    # leerse. Es el patron `frase_destacada` del documento y es lo que pide
    # EDICION.md: la idea importante se ve, no se acompana. Se convierten por
    # orden de contundencia -las mas cortas primero, que son las que funcionan
    # como rotulo- y solo hasta llegar al objetivo: pasarse llenaria el
    # episodio de carteles.
    t = sum(e["duracion"] for e in resultado)
    hay_g = sum(e["duracion"] for e in resultado
                if e["tipo"] in ("grafico", "documento"))
    falta_g = t * OBJETIVO_GRAFICO - hay_g

    frases = []
    for e in resultado:
        if e["tipo"] != "clip":
            continue
        texto = (e.get("locucion") or "").strip()
        if texto.endswith((".", "!", "?")) and 1 <= len(texto.split()) <= 14:
            frases.append((len(texto.split()), e))
    for _, e in sorted(frases, key=lambda f: f[0]):
        if falta_g <= 0:
            break
        limpio = re.sub(r"\s+", " ", e["locucion"]).strip().rstrip(".")
        e["tipo"] = "grafico"
        e["patron"] = "cifra_impacto"
        e["variante"] = "frase_destacada"
        e["contenido"] = {"linea": limpio}
        for campo in ("clips", "busqueda", "credito", "parecido"):
            e.pop(campo, None)
        falta_g -= e["duracion"]

    spec["escenas"] = resultado
    args.escenas.write_text(json.dumps(spec, ensure_ascii=False, indent=2),
                            encoding="utf-8")

    t = sum(e["duracion"] for e in resultado)
    por: dict[str, int] = {}
    for e in resultado:
        por[e["tipo"]] = por.get(e["tipo"], 0) + e["duracion"]
    print(f"{len(resultado)} escenas, {t/FPS/60:.2f} min")
    for k, v in sorted(por.items(), key=lambda kv: -kv[1]):
        print(f"  {k:10} {v/FPS:5.0f}s {v/t*100:4.0f}%")


if __name__ == "__main__":
    main()
