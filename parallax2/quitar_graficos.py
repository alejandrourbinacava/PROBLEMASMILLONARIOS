#!/usr/bin/env python3
"""
Quita el grafico a unos planos concretos de un guion ya montado.

    python3 quitar_graficos.py proyecto/mercadona.json cap1_02b cap2_04d ...

POR QUE EXISTE. `motion_banco` pone un contador en cada plano donde la frase
dice una cifra, y lo hace leyendo el numero suelto: «mil seiscientas tiendas»
salio como «1.000 · seiscientas tiendas», «mil setecientos treinta y cuatro
euros brutos» como «4 · brutos al mes», «dos mil euros» como «2 M», un año
-«desde dos mil nueve»- como una cantidad que se contaba hasta 2.009 y
«cuatrocientos mil» sin ninguna unidad. Es la clase de error que ve quien ve
el video y no ve ninguna comprobacion.

`motion_manual` pone la ficha BUENA en el primer trozo de la frase, pero el
contador malo se queda en el trozo siguiente: una frase partida en tres planos
-`cap4_04`, `cap4_04b`, `cap4_04c`- tiene la cifra bien en el primero y mal en
el segundo. Esto quita el malo.

Si el plano llevaba clip, se queda con el clip: una cifra de menos no lo vacia.
Si era un plato -tarjeta sin metraje- se convierte en una ilustracion con el
icono de lo que dice la frase, que es la regla del canal: nunca un plato
vacio.

Va DESPUES de `motion_manual`.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(AQUI))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    ruta, ids = sys.argv[1], set(sys.argv[2:])
    sys.stdout.reconfigure(encoding="utf-8")
    import iconos
    import vestir

    g = json.load(open(ruta, encoding="utf-8"))
    episodio = os.path.basename(ruta).replace(".json", "")
    quitados, ilustrados, ausentes = [], [], set(ids)
    for i, e in enumerate(g["escenas"]):
        if e["id"] not in ids:
            continue
        ausentes.discard(e["id"])
        if not e.get("grafico"):
            continue
        e.pop("grafico")
        quitados.append(e["id"])
        if e.get("fondo") == "plato":
            vestir.a_plato(e, i, episodio, iconos)
            ilustrados.append(e["id"])
    json.dump(g, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"graficos quitados: {len(quitados)} ({', '.join(quitados)})")
    if ilustrados:
        print(f"  platos que pasan a ilustracion: {', '.join(ilustrados)}")
    if ausentes:
        print(f"  AVISO: no existen estos planos: {', '.join(sorted(ausentes))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
