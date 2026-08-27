"""Busca en los bancos el metraje de cada plano y lo deja listo para renderizar.

Cada escena de tipo clip trae en `busqueda` una o varias consultas separadas por
un punto medio. Aqui se prueban en orden y se guarda la primera que da un clip
util. El resultado va a `clips`, que es lo que lee la composicion.

Dos cosas que no son obvias:

  La reserva. `acquire` tiene una consulta de ultimo recurso -"money cash"- que
  siempre encuentra algo. Aqui se DESACTIVA: un plano con metraje generico de
  billetes cuando se esta hablando de una licencia no representa lo que se dice,
  que es justo lo que EDICION.md prohibe. Es mejor que el plano quede marcado
  como fallido y se vea en el informe.

  El clip mas corto que el plano. Se admite: la composicion lo congela o lo
  ralentiza. Lo que no se admite es uno mucho mas corto, porque el congelado se
  nota, asi que se pide al menos la mitad de la duracion del plano.

    python scripts/conseguir_metraje.py
    python scripts/conseguir_metraje.py --solo C3     # un capitulo
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.providers.stock import StockLibrary, relevance  # noqa: E402

# Minimo de la consulta que tiene que aparecer de verdad en el clip.
# Cuando NADA casa, el banco devuelve igualmente su primer resultado por
# posicion: pidiendo 'roulette wheel spinning' llego una abeja sobre una
# flor. Un plano asi no representa lo que se dice, que es justo lo que
# EDICION.md prohibe, asi que se rechaza y se prueba la consulta siguiente.
MINIMO_PARECIDO = 0.5

# Palabras que describen COMO esta rodado el plano, no QUE se ve en el. Puntuan
# igual que las demas y por eso un clip de pintura amarilla pasaba el filtro
# pedido "roulette wheel spinning slow motion macro": casaba el estilo y no el
# sujeto. Se quitan antes de comparar, asi la nota mide lo unico que importa,
# que es si sale lo que se esta contando.
ESTILO = {
    "slow", "motion", "macro", "close", "closeup", "shot", "wide", "aerial",
    "view", "footage", "clip", "time", "lapse", "background", "detail",
    "cinematic", "handheld", "static", "moving", "camera", "angle", "top",
}


# Palabras de contenido que casi cualquier clip contiene: no distinguen nada.
# "official handing certificate over counter" tiene como sujeto el CERTIFICADO,
# no el "official", y exigir la primera palabra dejaba fuera setenta planos que
# tenian buen metraje esperando.
GENERICO = {
    "official", "people", "person", "man", "woman", "men", "women", "hands",
    "hand", "business", "worker", "guy", "someone", "group", "over", "into",
    "with", "and", "the", "from", "under", "against", "being", "one", "two",
    # Sustantivos que aparecen en medio banco y no dicen de que va el plano.
    # Con 0,4 y sin esta lista entraron unos dardos por "board", el skyline de
    # Manhattan por "buildings" y una boda por "table".
    "table", "board", "buildings", "building", "room", "screen", "screens",
    "sign", "door", "office", "desk", "paper", "papers", "walking", "standing",
    "looking", "empty", "modern", "new", "old",
    # Palabras de textura: casan con cualquier macro abstracto. Pidiendo
    # "carpet pattern" llego "colours, pattern, texture, abstract".
    "pattern", "texture", "abstract", "detail", "colours", "colors", "surface",
}


def _sujeto(consulta: str) -> list[str]:
    return [w for w in consulta.split() if w.lower() not in ESTILO]


def _distintivas(consulta: str) -> list[str]:
    return [w for w in _sujeto(consulta) if w.lower() not in GENERICO]


# Cuantas etiquetas se miran de la descripcion del clip.
#
# Pexels describe cada clip con una frase; Pixabay suelta una lista de treinta
# etiquetas. Puntuando la lista entera, un clip de Pixabay gana POR VOLUMEN:
# cuantas mas etiquetas, mas probable es acertar una por azar. Asi entro un
# timelapse de Dubrovnik pedido "fluorescent corridor interior" con un 0,67, y
# una mezquita pedido "casino carpet". Pixabay ordena sus etiquetas por
# relevancia, asi que quedandose con las primeras se mira lo que el clip es de
# verdad y no todo lo que alguien penso al subirlo.
ETIQUETAS = 8


def _recortar(pista: str) -> str:
    partes = [t.strip() for t in pista.split(",")]
    return ", ".join(partes[:ETIQUETAS]) if len(partes) > 1 else pista


def parecido(consulta: str, pista: str) -> float:
    """Que parte del SUJETO de la consulta aparece de verdad en el clip.

    No basta con la proporcion. La primera palabra es DE QUE va el plano, y
    tiene que salir si o si: pidiendo "roulette ball bouncing" llegaron pelotas
    de tenis con un 0,67, porque casaban "ball" y "bouncing" y fallaba la unica
    palabra que importaba. Si falta el sujeto, la nota es cero.
    """
    pista = _recortar(pista)
    palabras = _sujeto(consulta)
    if not palabras:
        return 0.0
    # Tiene que salir algo que identifique el plano, no una palabra cualquiera:
    # pidiendo "roulette ball bouncing" llegaron pelotas de tenis con un 0,67,
    # porque casaban "ball" y "bouncing" y fallaba la unica que importaba.
    distintivas = _distintivas(consulta) or palabras
    if not any(relevance(w, pista) for w in distintivas):
        return 0.0
    return relevance(" ".join(palabras), pista)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escenas", type=Path,
                   default=Path("remotion/public/episodio/escenas.json"))
    p.add_argument("--destino", type=Path,
                   default=Path("remotion/public/episodio/clips"))
    p.add_argument("--solo", default="", help="prefijo de id, para ir por capitulos")
    args = p.parse_args()

    spec = json.loads(args.escenas.read_text(encoding="utf-8"))
    fps = spec["fps"]
    args.destino.mkdir(parents=True, exist_ok=True)
    banco = StockLibrary()

    pendientes = [e for e in spec["escenas"]
                  if e["tipo"] == "clip" and e.get("busqueda")
                  and e["id"].startswith(args.solo)]
    print(f"{len(pendientes)} planos de metraje\n")

    fallidos: list[tuple[str, str]] = []
    for e in pendientes:
        if e.get("clips"):
            continue
        minimo = (e["duracion"] / fps) * 0.5
        elegido = None
        consultas = [q.strip() for q in e["busqueda"].split("·") if q.strip()]
        # Ultimo intento con la consulta recortada a su sujeto. Una consulta de
        # seis palabras casi nunca llega al minimo aunque el clip sea el bueno:
        # "close up on casino machines" se caia con 0,33 pedido "slot machines
        # row switched on casino floor", cuando es exactamente el plano. Con
        # tres palabras la nota vuelve a medir lo que se ve.
        for q in list(consultas):
            corta = " ".join(w for w in q.split() if w.lower() not in ESTILO)[:60]
            corta = " ".join(corta.split()[:3])
            if corta and corta != q:
                consultas.append(corta)
        for consulta in consultas:
            candidato = banco.acquire(consulta, minimo, fallback_query="")
            if not candidato:
                continue
            nota = parecido(consulta, candidato.hint)
            if nota < MINIMO_PARECIDO:
                print(f"  {e['id']:8} descartado ({nota:.2f}) "
                      f"'{consulta[:32]}' -> {candidato.hint[:40]}")
                continue
            elegido = candidato
            break
        if not elegido:
            fallidos.append((e["id"], e["busqueda"]))
            print(f"  {e['id']:8} SIN CLIP  {e['busqueda'][:60]}")
            continue
        nombre = f"{e['id']}{elegido.path.suffix}"
        shutil.copy2(elegido.path, args.destino / nombre)
        e["clips"] = [f"clips/{nombre}"]
        e["credito"] = f"{elegido.provider}:{elegido.clip_id}"
        # Se anota para poder repasar despues cuales entraron justos.
        e["parecido"] = round(parecido(elegido.query, elegido.hint), 2)
        print(f"  {e['id']:8} {elegido.provider:8} {elegido.duration:5.1f}s  "
              f"{parecido(elegido.query, elegido.hint):.2f}  {elegido.hint[:40]}")

    args.escenas.write_text(json.dumps(spec, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    hechos = sum(1 for e in spec["escenas"] if e.get("clips"))
    print(f"\n{hechos} planos con metraje, {len(fallidos)} sin resolver")
    if fallidos:
        print("Reescribe la busqueda de estos en config/contenido_casino.json:")
        for cid, q in fallidos:
            print(f"  {cid:8} {q}")


if __name__ == "__main__":
    main()
