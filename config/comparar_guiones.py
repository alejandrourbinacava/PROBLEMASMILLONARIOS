#!/usr/bin/env python3
"""
Busca el molde: frases que el guion nuevo comparte con los ya publicados.

    python3 comparar_guiones.py guion_nuevo.md

Existe porque los tres primeros episodios salieron con el mismo esqueleto y
nadie lo vio hasta que el usuario dijo "no hagas los guiones tan iguales".
Comparados palabra por palabra compartian los capitulos, la anafora del
giro -"Has puesto... Has conseguido..."-, la frase de pago -"lo que de
verdad tienes no es un X"- y la apertura del cierre -"Entonces, cuanto".
Quien ve dos episodios nota el molde en el tercero y ya sabe lo que viene.

No mide calidad. Mide repeticion, que es lo unico que se puede contar.
"""
import argparse
import glob
import io
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
N = 4

# La tesis de la serie SI se repite a proposito: es la identidad del canal.
# Lo que no puede repetirse es como se cuenta.
DELIBERADO = (
    "dueño", "duracion objetivo", "locucion", "ritmo", "ppm", "hilo conductor",
    "el precio de ser el dueño", "mcdonald", "casino", "episodio de la serie",
)


def cuerpo(ruta):
    """El guion sin la cabecera ni las tablas de fuentes: solo la locucion."""
    t = io.open(ruta, encoding="utf-8").read()
    t = t.split("## Fuentes")[0]
    # Fuera la cabecera entera: la ficha del episodio -titulo, duracion,
    # ritmo, tesis de la serie- es igual a proposito y llenaba el informe
    # de falsos positivos que tapaban los de verdad.
    corte = t.find("\n## ")
    if corte > 0:
        t = t[corte:]
    t = re.sub(r"^>.*$", " ", t, flags=re.M)        # citas de cabecera
    t = re.sub(r"^\|.*$", " ", t, flags=re.M)       # tablas
    t = re.sub(r"^\*\(.*?\)\*$", " ", t, flags=re.M)  # notas de montaje
    return t


def grupos(texto):
    p = re.findall(r"[a-záéíóúñü]+", texto.lower())
    return {" ".join(p[i:i + N]): i for i in range(len(p) - N + 1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--contra", default=None,
                    help="carpeta con los guiones publicados (por defecto, la de config)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    nuevo = os.path.abspath(a.guion)
    carpeta = a.contra or AQUI
    otros = [f for f in sorted(glob.glob(os.path.join(carpeta, "guion_*.md")))
             if os.path.abspath(f) != nuevo]
    if not otros:
        print("no hay guiones anteriores contra los que comparar")
        return 0

    mio = grupos(cuerpo(nuevo))
    fuera = []
    for f in otros:
        suyo = grupos(cuerpo(f))
        for frase in mio:
            if frase not in suyo:
                continue
            if any(d in frase for d in DELIBERADO):
                continue
            fuera.append((frase, os.path.basename(f)))

    # Una frase compartida con UN episodio puede ser casualidad; con dos ya
    # es plantilla.
    cuenta = {}
    for frase, arch in fuera:
        cuenta.setdefault(frase, set()).add(arch)

    molde = sorted((f for f, s in cuenta.items() if len(s) >= 2),
                   key=lambda f: mio[f])
    sueltas = sorted((f for f, s in cuenta.items() if len(s) == 1),
                     key=lambda f: mio[f])

    print(f"{os.path.basename(nuevo)} contra {len(otros)} guiones anteriores")
    print(f"  frases de {N} palabras repetidas en DOS o mas: {len(molde)}")
    for f in molde[:30]:
        print("    MOLDE   ", f, " ->", ", ".join(sorted(cuenta[f])))
    print(f"  repetidas en uno solo: {len(sueltas)}")
    for f in sueltas[:15]:
        print("    ojo     ", f, " ->", ", ".join(cuenta[f]))

    if molde:
        print("\nEso es plantilla, no estilo. Reescribe esas frases: el "
              "espectador que ha visto dos episodios ya sabe lo que viene.")
        return 1
    print("\n  sin molde compartido")
    return 0


if __name__ == "__main__":
    sys.exit(main())
