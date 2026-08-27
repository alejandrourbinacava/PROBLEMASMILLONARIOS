"""Vuelca en las escenas lo que se ve en cada plano y avisa de lo que falta.

El expansor decide CUANTO dura cada plano y de que TIPO es, que se puede sacar
de las marcas del SRT. Lo que no se puede sacar de ahi es QUE se ve: eso esta
escrito a mano en config/contenido_casino.json contra la locucion, porque la
regla de EDICION.md -cada plano representa lo que se esta diciendo- no la
resuelve una expresion regular.

Este script junta las dos cosas y, sobre todo, LISTA lo que se queda sin
contenido. Un clip sin busqueda no falla al renderizar: sale un hueco, o peor,
sale el clip de reserva, que es metraje generico y es exactamente lo que la
doctrina prohibe. Asi que tiene que verse aqui y no al revisar el video.

    python scripts/aplicar_contenido.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escenas", type=Path,
                   default=Path("config/escenas_casino_completo.json"))
    p.add_argument("--contenido", type=Path,
                   default=Path("config/contenido_casino.json"))
    p.add_argument("--out", type=Path,
                   default=Path("remotion/public/episodio/escenas.json"))
    args = p.parse_args()

    spec = json.loads(args.escenas.read_text(encoding="utf-8"))
    conten = json.loads(args.contenido.read_text(encoding="utf-8"))
    conten.pop("_nota", None)

    # Lo que ya se resolvio contra los bancos se conserva. Si no, cada pasada
    # por aqui borra los clips descargados y hay que volver a bajarlos todos.
    previo: dict[str, dict] = {}
    if args.out.exists():
        anterior = json.loads(args.out.read_text(encoding="utf-8"))
        previo = {e["id"]: e for e in anterior.get("escenas", [])}

    ids = {e["id"] for e in spec["escenas"]}
    huerfanos = sorted(set(conten) - ids)

    puestos = 0
    for e in spec["escenas"]:
        extra = conten.get(e["id"])
        if not extra:
            continue
        e.update(extra)
        puestos += 1

    for e in spec["escenas"]:
        antes = previo.get(e["id"], {})
        for campo in ("clips", "credito"):
            if antes.get(campo) and not e.get(campo):
                e[campo] = antes[campo]

    sin_busqueda = [e["id"] for e in spec["escenas"]
                    if e["tipo"] == "clip" and not e.get("busqueda")]
    sin_contenido = [e["id"] for e in spec["escenas"]
                     if e["tipo"] in ("grafico", "documento") and not e.get("contenido")]
    sin_capas = [e["id"] for e in spec["escenas"]
                 if e["tipo"] == "capas" and not e.get("capas")]

    print(f"{puestos} escenas con contenido de {len(spec['escenas'])}")
    if huerfanos:
        # Una entrada que no casa con ninguna escena es casi siempre un id que
        # cambio al reexpandir: el contenido escrito a mano se pierde en
        # silencio y el plano se queda vacio.
        print(f"\nAVISO  {len(huerfanos)} entradas sin escena: {', '.join(huerfanos)}")
    for etiqueta, faltan in (("clips sin busqueda", sin_busqueda),
                             ("graficos sin contenido", sin_contenido),
                             ("escenas de capas sin imagenes", sin_capas)):
        if faltan:
            print(f"\nFALTA  {etiqueta} ({len(faltan)}): {', '.join(faltan)}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(spec, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\n-> {args.out}")


if __name__ == "__main__":
    main()
