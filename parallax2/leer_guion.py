#!/usr/bin/env python3
"""
Lee un guion en Markdown y saca la estructura de capitulos y frases.

    python3 leer_guion.py ../config/guion_banco.md

Existe porque hasta ahora la estructura vivia escrita a mano dentro de
`construir_guion.py`: una tabla de ochenta y cinco frases con sus segundos
puestos a ojo. Eso trajo dos problemas.

  Las duraciones eran inventadas. Se repartian siete, ocho, nueve segundos
  por frase cuando la locucion real dura cinco: seis minutos de silencio en
  un episodio de catorce.

  Y cada episodio nuevo obligaba a reescribir la tabla. El guion ya existe
  en Markdown, con sus capitulos y sus frases; no hace falta copiarlo.

Aqui se lee el Markdown y ya. Las duraciones NO salen de aqui: salen de
medir la locucion, que es lo unico que sabe cuanto dura una frase.
"""
import argparse
import json
import re
import unicodedata


def clave(titulo):
    """'CAPÍTULO 3 — La licencia no es una tasa' -> 'cap3'."""
    t = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    t = t.lower()
    if t.startswith("gancho"):
        return "gancho"
    if t.startswith("cierre"):
        return "cierre"
    m = re.match(r"capitulo\s+(\d+)", t)
    return f"cap{m.group(1)}" if m else re.sub(r"[^a-z0-9]+", "_", t)[:18].strip("_")


def leer(ruta):
    """Devuelve [(clave_capitulo, titulo, [frases])]."""
    texto = open(ruta, encoding="utf-8").read()
    # lo que va despues de Fuentes son notas, no locucion
    texto = re.split(r"^##\s+Fuentes", texto, flags=re.M)[0]

    capitulos, actual = [], None
    for linea in texto.splitlines():
        l = linea.strip()
        if l.startswith("## "):
            titulo = l[3:].split("·")[0].strip()
            actual = (clave(titulo), titulo, [])
            capitulos.append(actual)
            continue
        if actual is None or not l:
            continue
        # cabeceras, citas, listas, negritas sueltas y separadores no se dicen
        if l.startswith(("#", ">", "-", "*", "|", "`", "**Duración",
                         "**Episodio", "**Locución", "---")):
            continue
        actual[2].append(re.sub(r"\*\*(.+?)\*\*", r"\1", l))
    return [c for c in capitulos if c[2]]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("guion")
    ap.add_argument("--json", help="vuelca la estructura a un JSON")
    a = ap.parse_args()

    caps = leer(a.guion)
    total_frases = sum(len(f) for _, _, f in caps)
    total_pal = sum(len(x.split()) for _, _, f in caps for x in f)
    total_car = sum(len(x) for _, _, f in caps for x in f)

    print(f'{"capitulo":10s} {"frases":>7s} {"palabras":>9s}  titulo')
    for k, t, frases in caps:
        pal = sum(len(x.split()) for x in frases)
        print(f"{k:10s} {len(frases):7d} {pal:9d}  {t[:52]}")
    print(f'\n{total_frases} frases · {total_pal} palabras · {total_car} caracteres')
    print(f"a 140 ppm: {total_pal/140:.1f} min")
    # la voz de ai33 sale a 1,36 creditos por caracter, medido en dos episodios
    print(f"voz ai33: ~{total_car*1.36:,.0f} creditos")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump([{"cap": k, "titulo": t, "frases": fr}
                       for k, t, fr in caps], f, ensure_ascii=False, indent=1)
        print(f"-> {a.json}")


if __name__ == "__main__":
    main()
