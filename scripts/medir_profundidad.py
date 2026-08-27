"""¿Esta imagen tiene ESPACIO o solo tiene capas?

La pregunta que hay que hacerle a una imagen antes de meterla en el pipeline es:
si me moviera dos pasos a la izquierda, ¿veria algo que antes no veia? En un
plano frontal la respuesta es no, y entonces el parallax se ve como un zoom por
mucho que las capas esten bien separadas.

Eso se puede medir sobre el mapa de profundidad, sin mirar la imagen:

  recorrido    cuanto rango de profundidad ocupa de verdad la escena
  reparto      si la profundidad esta repartida o amontonada en dos valores
  gradiente    cuanta profundidad cambia al recorrer la imagen: una calle que
               se aleja da un gradiente alto y sostenido, una fachada frontal
               da casi cero
  quemado      superficie sin textura, donde el modelo de profundidad no tiene
               en que apoyarse
  cielo        cuanta materia hay arriba para poder animarla

Uso:
    python scripts/medir_profundidad.py imagen.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def medir(ruta: Path, modelo: str, hilos: int) -> dict:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "bl", Path(__file__).with_name("build_layers.py"))
    bl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bl)

    imagen = Image.open(ruta).convert("RGB")
    profundidad = bl.mapa_profundidad(imagen, modelo, hilos)
    rgb = np.asarray(imagen, dtype=np.float32)

    # Recorrido util: entre los percentiles 2 y 98, para no contar cuatro
    # pixeles sueltos como si fueran el rango de la escena.
    p2, p98 = np.percentile(profundidad, [2, 98])
    recorrido = float(p98 - p2)

    # Reparto: si la profundidad se amontona en dos valores -pared y cielo- la
    # escena es plana por mucho rango que tenga. Se mide con la entropia del
    # histograma, normalizada.
    hist, _ = np.histogram(profundidad, bins=32, range=(0, 255))
    p = hist / max(1, hist.sum())
    p = p[p > 0]
    reparto = float(-(p * np.log2(p)).sum() / np.log2(32))

    # Gradiente horizontal medio: una calle que se aleja lo tiene alto y
    # sostenido; una fachada paralela a camara lo tiene casi a cero.
    gx = np.abs(np.diff(profundidad, axis=1))
    gradiente = float(np.percentile(gx, 90))

    quemado = float((rgb.min(axis=2) > 250).mean())
    banda_cielo = profundidad[: profundidad.shape[0] // 3]
    cielo = float(banda_cielo.std())

    return {
        "recorrido": recorrido, "reparto": reparto, "gradiente": gradiente,
        "quemado": quemado, "cielo": cielo,
    }


UMBRALES = {
    # (minimo aceptable, texto de que significa)
    "recorrido": (110.0, "rango de profundidad de la escena"),
    "reparto": (0.55, "profundidad repartida, no amontonada"),
    "gradiente": (1.2, "la escena retrocede al recorrerla"),
    "cielo": (4.0, "el cielo tiene materia que animar"),
}
MAXIMO_QUEMADO = 0.06


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("imagen", type=Path)
    parser.add_argument("--model", default="small")
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()

    m = medir(args.imagen, args.model, args.threads)
    print(f"\n{args.imagen.name}\n")
    fallos = []
    for clave, (minimo, texto) in UMBRALES.items():
        valor = m[clave]
        bien = valor >= minimo
        print(f"  {clave:11} {valor:7.2f}  (min {minimo:5.2f})  "
              f"{'ok ' if bien else 'NO '} {texto}")
        if not bien:
            fallos.append(clave)
    bien = m["quemado"] <= MAXIMO_QUEMADO
    print(f"  {'quemado':11} {m['quemado'] * 100:6.2f}%  (max {MAXIMO_QUEMADO * 100:4.1f}%)  "
          f"{'ok ' if bien else 'NO '} superficie sin textura")
    if not bien:
        fallos.append("quemado")

    print()
    if fallos:
        print(f"  NO SIRVE. Falla en: {', '.join(fallos)}")
        print("  Es una imagen con capas, no con espacio: al mover la camara no")
        print("  se descubre nada y el parallax se vera como un zoom.")
        raise SystemExit(1)
    print("  Sirve: la escena tiene espacio de verdad.")


if __name__ == "__main__":
    main()
