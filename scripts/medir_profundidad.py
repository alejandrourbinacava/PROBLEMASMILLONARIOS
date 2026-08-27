"""Descarta material que NO sirve para 2.5D. No juzga si una imagen es buena.

Esa distincion importa, porque probe a medir lo segundo y no se puede. La
pregunta que de verdad decide es la de siempre: si me moviera dos pasos a la
izquierda, ¿veria algo que antes no veia? Medida sobre el mapa de profundidad,
una foto frontal y una calle en fuga dan casi lo mismo:

    metrica          poster frontal    calle en fuga
    gradiente             4,54             4,80
    oclusion              6,02 %           6,10 %
    recorrido del suelo   198              185

Ninguna las separa, porque el poster tambien tiene acera y cielo. Lo unico que
las distinguio fue el reparto -0,55 contra 0,64- y por un pelo, justo en el
umbral: eso no es una medida robusta, es casualidad.

Lo que si hace bien esto es cazar material claramente inservible. Frente a una
foto de un interior con barandillas, cristal y gente a veinte distancias, la
diferencia es de un factor diez:

    oclusion (saltos grandes)   imagen generada 3,3 %   foto de interior 0,30 %

Asi que sirve de reja de entrada automatica, no de juez. Que una imagen tenga
espacio de verdad hay que verlo, y de momento no hay forma de delegarlo.

  recorrido    rango de profundidad que ocupa la escena
  reparto      si la profundidad esta repartida o amontonada en dos valores
  oclusion     cuanto borde de profundidad hay, o sea cuantas cosas tapan a
               otras: es lo unico que el movimiento lateral puede descubrir
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

    # Oclusion: que fraccion del encuadre son BORDES de profundidad, o sea
    # sitios donde una cosa tapa a otra. Es lo unico que el movimiento lateral
    # puede descubrir, y lo que separa material aprovechable de material que no
    # lo es. Se mide sobre una version reducida: entre pixeles contiguos de una
    # imagen de 4096 de ancho un degradado suave da menos de una unidad, y lo
    # que se estaria midiendo es el ruido del modelo, no la estructura.
    pequeno = np.asarray(
        Image.fromarray(profundidad).resize((320, 180), Image.BILINEAR),
        dtype=np.float32,
    )
    salto = 30.0
    gh = np.abs(np.diff(pequeno, axis=1)) > salto
    gv = np.abs(np.diff(pequeno, axis=0)) > salto
    oclusion = float(gh.mean() + gv.mean()) * 100

    quemado = float((rgb.min(axis=2) > 250).mean())
    banda_cielo = profundidad[: profundidad.shape[0] // 3]
    cielo = float(banda_cielo.std())

    return {
        "recorrido": recorrido, "reparto": reparto, "oclusion": oclusion,
        "quemado": quemado, "cielo": cielo,
    }


UMBRALES = {
    # (minimo aceptable, texto de que significa)
    "recorrido": (110.0, "rango de profundidad de la escena"),
    "reparto": (0.55, "profundidad repartida, no amontonada"),
    # 1,5% es holgado a proposito: las imagenes generadas dan 3,3 y la foto de
    # interior 0,30, asi que el umbral separa con margen sin descartar de mas.
    "oclusion": (1.5, "hay cosas que tapan a otras (%)"),
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
        print(f"  DESCARTADA. Falla en: {', '.join(fallos)}")
        raise SystemExit(1)
    print("  Pasa la reja. OJO: esto solo descarta material inservible.")
    print("  Que la escena tenga espacio de verdad -que moverse dos pasos")
    print("  descubra algo- hay que verlo; ninguna de estas medidas lo detecta.")


if __name__ == "__main__":
    main()
