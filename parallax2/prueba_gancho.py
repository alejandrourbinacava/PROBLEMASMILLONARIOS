#!/usr/bin/env python3
"""
Reconstruye el gancho del episodio del banco con lo que dice la
investigacion de retencion, y sin tocar la locucion.

    python3 prueba_gancho.py

Tres cambios, y solo tres, para que la prueba diga algo:

1. EL CLIP SE ELIGE POR LA PALABRA. Lo asigna emparejar.py: el clip de la
   fachada cae en la frase que habla de la fachada. Antes caia donde tocase.

2. LO QUE NO TIENE IMAGEN NO LLEVA IMAGEN. Cuatro frases del gancho -"la
   pregunta se hace sola", "aqui este video se separa de los dos
   anteriores"- no las ilustra ningun clip del mundo. Hoy llevan una reunion
   de stock. Aqui llevan una tarjeta: fondo del canal y la frase en
   movimiento. Un plano que no dice nada es peor que ningun plano.

3. REFUERZO VISUAL CADA 3-5 SEGUNDOS. Es la regla del estilo explainer, y
   con planos de 3,6 s significa uno por plano. Hoy solo 4 de 14 llevan
   texto en pantalla.

Lo que NO se toca: la locucion. Cambiar una frase obliga a sintetizar voz de
pago otra vez, y la del canal ya esta pagada. Asi que esta prueba mide lo que
cambia la IMAGEN, no lo que cambiaria un guion nuevo.
"""
import io
import json
import math
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.join(AQUI, "proyecto")

FONDO = (11, 18, 32)
REJILLA = (27, 36, 54)
AMBAR = [255, 176, 60]
PAPEL = [237, 231, 218]

# Las cuatro frases del gancho que ningun clip puede decir, con el rotulo
# que llevan en su lugar. El rotulo NO es la frase entera: es la parte que
# el ojo puede leer en tres segundos.
TARJETAS = {
    "gancho_05":  "Coge el *tuyo*",
    "gancho_05b": "Y se queda la *diferencia*",
    "gancho_06":  "¿Cuánto cuesta *montar uno*?",
    "gancho_07":  "Aquí cambia *todo*",
}

# Refuerzo visual donde hoy no hay nada.
#
# NINGUNO LLEVA `retardo`. El render cronometra el rotulo contra la PALABRA
# que lo dispara: busca la primera palabra del rotulo dentro de la locucion
# y la convierte a segundos al ritmo del guion. Poner el retardo a mano
# -que es lo que hice en la primera prueba- hace entrar todos los rotulos a
# la vez, a los 0,55 s, y ninguno cae donde se dice.
#
# Para que funcione, la primera palabra del rotulo TIENE que aparecer
# literal en la locucion de esa escena.
ROTULOS = {
    "gancho_01b": "*cien* prestados",
    "gancho_02b": "oficinas y *nóminas*",
    "gancho_04":  "gana con el *tuyo*",
    "gancho_08":  "*licencia*",
    "gancho_09":  "nunca ha sido *tuyo*",
}


def tarjeta(ruta, semilla):
    """El fondo de una tarjeta: la rejilla isometrica del canal, desplazada
    para que no haya dos iguales."""
    from PIL import Image, ImageDraw
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(im)
    cos30, sen30 = math.cos(math.radians(30)), 0.5
    cx, cy = W / 2, H / 2 + 60 + semilla * 26

    def iso(x, y):
        return (cx + (x - y) * cos30, cy + (x + y) * sen30)

    for i in range(-16, 17):
        p = i * 44 + semilla * 9
        d.line([iso(p, -700), iso(p, 700)], fill=REJILLA, width=2)
        d.line([iso(-700, p), iso(700, p)], fill=REJILLA, width=2)
    im.save(ruta)


def main():
    # 1. el emparejamiento por palabra
    v2 = os.path.join(PROY, "episodio_banco_v2.json")
    subprocess.run([sys.executable, os.path.join(AQUI, "emparejar.py"),
                    "proyecto/episodio_banco.json",
                    "--salida", "proyecto/episodio_banco_v2.json"],
                   cwd=AQUI, check=True, stdout=subprocess.DEVNULL)

    g = json.load(io.open(v2, encoding="utf-8"))
    escenas = [e for e in g["escenas"] if e["id"].startswith("gancho")]

    # El ciclo de la casa: I - D - C - D - I - C. Nunca el mismo lado dos
    # veces seguidas, y el centro como descanso, no como valor por defecto.
    CICLO = ["izquierda", "derecha", "centrado", "derecha", "izquierda",
             "centrado"]
    MOV = ["push_in", "drift_der", "pull_out", "drift_izq", "subir",
           "contra_der"]

    n_tarjeta = n_rotulo = n_clip = 0
    for i, e in enumerate(escenas):
        e["composicion"] = CICLO[i % len(CICLO)]
        e["movimiento"] = MOV[i % len(MOV)]
        # 2. tarjeta donde no hay imagen posible
        if e["id"] in TARJETAS:
            arch = f"tarjeta_{e['id']}.png"
            tarjeta(os.path.join(PROY, arch), i)
            e.pop("clip", None)
            e.pop("clip_desde", None)
            e.pop("clip_sin_imagen", None)
            # `tipo: rotulo` no es decoracion: exime a la escena de la regla
            # de las dos capas y del techo de 4s, que son para planos
            # compuestos. Aqui manda la frase y una capa detras solo estorba.
            e["tipo"] = "rotulo"
            e["capas"] = [{"rol": "fondo", "archivo": arch,
                           "clase": "abstracto", "entrada": "escala",
                           "prompt": "tarjeta del canal"}]
            e["texto_pantalla"] = {
                "texto": TARJETAS[e["id"]], "px": 118, "y": 0.46,
                "acento": AMBAR, "color": PAPEL,
                # La tarjeta SI lleva retardo fijo, y es la excepcion: aqui
                # el texto no acompana a una imagen, el texto ES el plano.
                # Espera lo justo a que asiente el fondo y entra.
                "estilo": "sube", "retardo": 0.30,
            }
            e["efectos"] = []
            n_tarjeta += 1
            continue

        e.pop("clip_sin_imagen", None)
        n_clip += 1

        # 3. refuerzo visual donde no habia
        if e["id"] in ROTULOS and not e.get("texto_pantalla"):
            e["texto_pantalla"] = {
                "texto": ROTULOS[e["id"]], "px": 96, "y": 0.30,
                "acento": AMBAR, "color": PAPEL,
                "estilo": "sube",
            }
            n_rotulo += 1

    g["escenas"] = escenas

    # Un rotulo cuya palabra no se dice en SU plano se muda al plano hermano
    # donde si se dice. Antes se quedaba sin cronometrar y entraba al
    # retardo por defecto, o sea a destiempo y sin que nada lo delatara.
    import render as R
    R.preparar(g)
    for e in escenas:
        if not e.get("texto_pantalla") or R.retardo_rotulo(e) is not None:
            continue
        hermanos = [o for o in escenas
                    if o.get("texto") == e.get("texto") and o is not e]
        movido = False
        for h in hermanos:
            if h.get("texto_pantalla"):
                continue
            h["texto_pantalla"] = e["texto_pantalla"]
            if R.retardo_rotulo(h) is not None:
                del e["texto_pantalla"]
                movido = True
                break
            del h["texto_pantalla"]
        if not movido:
            # mejor sin rotulo que con uno a destiempo
            del e["texto_pantalla"]
    for e in escenas:
        e.pop("_tramo", None)
        e.pop("_trozo_frase", None)
        e.pop("_sangrado", None)
        e.pop("hilo_t", None)

    destino = os.path.join(PROY, "prueba_gancho.json")
    json.dump(g, io.open(destino, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    dur = sum(e.get("duracion", 0) for e in escenas)
    con_texto = sum(1 for e in escenas if e.get("texto_pantalla"))
    print(f"{len(escenas)} escenas | {dur:.1f} s")
    print(f"  clips reasignados por palabra : {n_clip}")
    print(f"  tarjetas (sin imagen posible) : {n_tarjeta}")
    print(f"  rotulos nuevos                : {n_rotulo}")
    print(f"  planos con texto en pantalla  : {con_texto} de {len(escenas)}"
          f"  (antes 4)")
    print(f"escrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
