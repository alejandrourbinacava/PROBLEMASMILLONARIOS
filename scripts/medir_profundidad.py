"""Comprueba defectos TECNICOS de una imagen antes de separarla en capas.

NO decide si la imagen sirve. Lo intente y no se puede, y conviene dejarlo
escrito para que nadie lo vuelva a intentar creyendo que es facil.

La pregunta que de verdad decide es: si me muevo dos pasos a la izquierda,
¿veo algo que antes no veia? Probe tres formas de medirla sobre el mapa de
profundidad y ninguna funciona:

    metrica              poster plano   calle en fuga
    gradiente                4,54           4,80      no separa
    recorrido del suelo    198            185          sale peor la buena
    oclusion                 3,71 %         0,21 %     INVERTIDA

La ultima es la que mas ensena. Contar pixeles con un salto brusco de
profundidad premia las siluetas duras recortadas contra un fondo lejano, que es
justo lo que tiene un poster. En una calle que se aleja las transiciones son
graduales y casi ningun pixel supera el umbral. O sea que medía cuanto contraste
de silueta hay, no cuanto tapa una cosa a otra, y con esa reja se habrian
descartado las dos mejores imagenes de cuatro.

Se podrian mover los umbrales hasta que el orden coincidiera con mi opinion,
pero ajustar una medida a cuatro ejemplos no es medir. Asi que el fichero se
queda con lo que si puede comprobar objetivamente:

  quemado    superficie sin textura. El modelo de profundidad se apoya en el
             gradiente, y ante una zona plana da profundidad ruidosa. Es un
             defecto tecnico real y medible.
  cielo      cuanta materia hay arriba. Un degradado limpio no se ve moverse,
             asi que la capa de cielo no tendria nada que animar.
  recorrido  que la escena ocupe un rango de profundidad, no dos valores.

Si la escena tiene espacio de verdad hay que mirarlo. No hay atajo.

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

    quemado = float((rgb.min(axis=2) > 250).mean())
    banda_cielo = profundidad[: profundidad.shape[0] // 3]
    cielo = float(banda_cielo.std())

    return {"recorrido": recorrido, "reparto": reparto,
            "quemado": quemado, "cielo": cielo}


UMBRALES = {
    # (minimo aceptable, texto de que significa)
    "recorrido": (110.0, "rango de profundidad de la escena"),
    # 0,45 es un suelo bajo a proposito: solo caza escenas de dos valores, no
    # pretende distinguir una composicion buena de una mediocre.
    "reparto": (0.45, "profundidad repartida, no amontonada"),
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
        print(f"  DEFECTOS TECNICOS: {', '.join(fallos)}")
        raise SystemExit(1)
    print("  Sin defectos tecnicos.")
    print("  Esto NO dice que la imagen sirva: si la escena tiene espacio de")
    print("  verdad, si moverse dos pasos descubre algo, hay que mirarlo.")


if __name__ == "__main__":
    main()
