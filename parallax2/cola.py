#!/usr/bin/env python3
"""
Saca la cola de prompts para generarlos a mano en el navegador.

    python3 cola.py proyecto/guion.json --lote 20

Whisk y Meta AI no dan PNG con transparencia, asi que los prompts salen
pidiendo fondo verde croma plano y `recortar.py` lo quita despues. Es
exactamente lo mismo que se le pide a kie.ai: los prompts los arma
`generar.py`, no este script, para que la ruta de pago y la de navegador
produzcan la misma imagen.

Deja en `proyecto/cola/`:

    prompts_NN.txt   un prompt por linea, para pegar en la extension
    prompts_NN.csv   con nombre de archivo, si la extension lee columnas
    cola.json        el manifiesto con el ORDEN, que es lo que importa

Las tandas son de veinte y no de ciento dieciseis a proposito. `recoger.py`
empareja por fecha de descarga contra este manifiesto, asi que un fallo a
mitad descuadra todo lo que venga detras. Con tandas cortas se pierden
veinte, no la biblioteca entera.
"""
import argparse
import csv
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import generar


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--lote", type=int, default=20, help="prompts por tanda")
    ap.add_argument("--salida", default="cola")
    ap.add_argument("--crudas", default="crudas")
    ap.add_argument("--rehacer", action="store_true",
                    help="incluye tambien las capas que ya estan generadas")
    a = ap.parse_args()

    base = os.path.dirname(os.path.abspath(a.guion))
    guion = json.load(open(a.guion, encoding="utf-8"))
    estilo = guion.get("estilo", "")
    capas = generar.capas_unicas(guion)

    crudas = os.path.join(base, a.crudas)
    pendientes = [(arch, capa) for arch, capa in capas.items()
                  if a.rehacer or not os.path.exists(os.path.join(crudas, arch))]
    if not pendientes:
        print("no queda ninguna capa por generar")
        return 0

    dest = os.path.join(base, a.salida)
    os.makedirs(dest, exist_ok=True)

    manifiesto = []
    for i, (arch, capa) in enumerate(pendientes):
        # un prompt por linea: cualquier salto de linea rompe el pegado
        p = " ".join(generar.prompt_de(capa, estilo).split())
        manifiesto.append({"orden": i, "archivo": arch, "rol": capa["rol"],
                           "tanda": i // a.lote, "prompt": p})

    for t in range(0, len(manifiesto), a.lote):
        trozo = manifiesto[t:t + a.lote]
        n = t // a.lote + 1
        with open(os.path.join(dest, f"prompts_{n:02d}.txt"), "w",
                  encoding="utf-8") as f:
            f.write("\n".join(x["prompt"] for x in trozo) + "\n")
        with open(os.path.join(dest, f"prompts_{n:02d}.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["archivo", "rol", "prompt"])
            for x in trozo:
                w.writerow([x["archivo"], x["rol"], x["prompt"]])
        print(f'prompts_{n:02d}  {len(trozo):3d} prompts  '
              f'{trozo[0]["archivo"]} .. {trozo[-1]["archivo"]}')

    with open(os.path.join(dest, "cola.json"), "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, ensure_ascii=False, indent=1)

    ya = len(capas) - len(pendientes)
    print(f'\n{len(manifiesto)} por generar de {len(capas)} capas '
          f'({ya} ya estaban) - {len(manifiesto)//a.lote + 1} tandas')
    print(f"-> {os.path.join(a.salida, 'cola.json')}")
    print("\nEl ORDEN es lo unico que no se puede tocar: recoger.py empareja")
    print("por fecha de descarga contra este manifiesto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
