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

Y de paso, una pasada final: toda ILUSTRACION que se quede sin titular
recibe uno, sacado de su propia frase. `vestir` ya intenta esto, pero con una
regla estricta -clausula entera de doce caracteres o mas-, y al reconstruir el
episodio cambian los planos y reaparecen iconos sueltos sin una palabra: en
Mercadona salio asi la frase que da el giro de la serie, «El capital. Es
decir, el dueño. En quinto lugar.», que se vio como dos iconos de persona en
blanco. Un icono sin nada escrito no dice de que va.

Va DESPUES de `motion_manual`.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(AQUI))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    # Sin ids solo hace la pasada de titulares.
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
    # --- ilustraciones sin titular -------------------------------------
    import efectos as FX
    import motion_banco as MB
    claro = not FX.PALETA.get("oscura", True)
    previo, puestos = "", []
    for e in g["escenas"]:
        tp = (e.get("texto_pantalla") or {}).get("texto")
        if (e.get("grafico") or {}).get("tipo") == "ilustracion" and not tp:
            limite = min(34, MB.tope_legible(e.get("duracion", 3), 0.26))
            txt = MB.rotulo_de(e.get("texto") or "", limite)
            sin_marca = txt.replace("*", "").strip()
            if len(sin_marca) >= 8 and sin_marca != previo:
                e["texto_pantalla"] = {
                    "texto": FX._may(MB.resalta(txt)), "px": 96, "y": 0.64,
                    "acento": list(FX.PALETA["acento"]),
                    "color": list(FX.PALETA["hueso"]),
                    "halo": "claro" if claro else "oscuro",
                    "estilo": "sube", "retardo": 0.26,
                }
                puestos.append(e["id"])
                tp = txt
        previo = (tp or "").replace("*", "").strip()
    json.dump(g, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"graficos quitados: {len(quitados)} ({', '.join(quitados)})")
    if puestos:
        print(f"  ilustraciones mudas que reciben titular: {', '.join(puestos)}")
    if ilustrados:
        print(f"  platos que pasan a ilustracion: {', '.join(ilustrados)}")
    if ausentes:
        print(f"  AVISO: no existen estos planos: {', '.join(sorted(ausentes))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
