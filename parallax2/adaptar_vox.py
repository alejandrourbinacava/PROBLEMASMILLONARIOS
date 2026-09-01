#!/usr/bin/env python3
"""
Adapta el guion del storyboard al motor VOX y recorta un tramo de prueba.

    python3 adaptar_vox.py ../../_f22/guion.json --segundos 60 \
        --salida proyecto/vox_min.json

Hace tres cosas que el storyboard no puede hacer solo:

  DEVUELVE LAS TILDES. El guion viene sin ellas -"al ano", "nominas",
  "veintidos"- y eso cuesta dos veces. La voz de pago va cacheada por hash
  del texto, asi que un texto distinto es una locucion distinta aunque
  suene igual: de las 199 frases, solo 21 encajan con lo ya pagado y otras
  39 son la MISMA frase sin tildes. Y ademas ai33 lee lo que hay escrito:
  "ano" no es "ano" con enye, y eso ya se noto en el episodio anterior.

  SUSTITUYE LAS IMAGENES QUE NO EXISTEN. El storyboard pide 37 piezas
  nuevas (m_banquero, f_oficina...) que hay que generar. Para la prueba se
  mapean a las que ya hay, y se dice cuales se han sustituido en vez de
  fallar en silencio.

  NO REPITE LA VOZ. El storyboard parte una misma frase en dos planos
  (gancho_03 y gancho_03a). La locucion suena una vez: el segundo plano va
  mudo y hereda el tiempo.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import leer_guion

# Lo que hay en disco frente a lo que pide el storyboard. Sustituciones para
# la prueba; en el episodio de verdad estas piezas se generan con Meta AI.
SUJETOS = {
    "m_plantilla.png": "s_cola.png",      "m_cola.png":      "s_cola.png",
    "m_familia.png":   "s_manos.png",     "m_fundador.png":  "s_cajero.png",
    "m_banquero.png":  "s_cajero.png",    "m_cajero.png":    "s_cajero.png",
    "m_abogados.png":  "s_cajero.png",    "m_inspector.png": "s_cajero.png",
    "m_consultor.png": "s_calculadora.png", "m_guardia.png": "s_atm.png",
}
FRENTES = {
    "f_oficina.png": "h_vecinos.png",     "f_hucha.png":     "p_papeles.png",
    "f_llaves.png":  "p_papeles_b.png",   "f_mostrador.png": "p_canto_mesa.png",
    "f_boveda.png":  "p_cordon.png",      "f_atm.png":       "p_valla.png",
    "f_regulador.png": "h_vecinos.png",   "f_torre.png":     "h_vecinos2.png",
    "f_maletin.png": "p_manos_b.png",     "f_libro.png":     "p_papeles.png",
    "f_expediente.png": "p_papeles_b.png", "f_billetes.png": "p_manos.png",
}


# Frentes que tienen que parecer vivos: el vaiven lento los saca de "foto
# pegada" sin ser un video. En el estilo de referencia el agua se mueve y el
# barco cabecea, y eso es lo que separa un collage de una escena.
VIVOS = ("agua", "mar", "ola", "fuego", "llama", "humo", "multitud", "cola",
         "cordon", "manos")

TOPE = 4.0          # ningun plano pasa de cuatro segundos
MIN_ELEM = 5        # ni baja de cinco elementos en pantalla


def norm(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]", "", t).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--md", default="../config/guion_banco.md")
    ap.add_argument("--segundos", type=float, default=60.0)
    ap.add_argument("--salida", default="proyecto/vox_min.json")
    a = ap.parse_args()

    src = json.load(open(a.guion, encoding="utf-8"))
    tildes = {norm(f): f for _k, _t, fr in leer_guion.leer(
        os.path.join(AQUI, a.md)) for f in fr}

    escenas, t, visto, faltan, recuperadas = [], 0.0, set(), set(), 0
    troceadas = 0
    for e in src["escenas"]:
        if t >= a.segundos:
            break
        texto = tildes.get(norm(e["texto"]), e["texto"])
        if texto != e["texto"]:
            recuperadas += 1

        capas, frente, n_frente = [], None, {}
        for c in e["capas"]:
            if c.get("tipo_capa") != "imagen" or c.get("rol") == "fondo":
                continue
            arch = c["archivo"]
            # La entrada y el retardo de cada capa vienen del storyboard y
            # hay que respetarlos. Aplicando el mismo muelle a todas, las
            # seis capas de la escena entran a la vez y se leen como una
            # sola imagen apareciendo: ahi se iba la mitad del movimiento.
            if c["rol"] == "frente":
                frente = FRENTES.get(arch, arch)
                n_frente = {"entrada_frente": c.get("entrada", "sube"),
                            "frente_vivo": any(k in arch for k in VIVOS)}
                if arch not in FRENTES:
                    faltan.add(arch)
            else:
                capas.append({"archivo": SUJETOS.get(arch, arch),
                              "entrada": c.get("entrada", "pop"),
                              "retardo": c.get("retardo", 0.12)})
                if arch not in SUJETOS:
                    faltan.add(arch)

        n = {"id": e["id"], "texto": texto, "duracion": e["duracion"],
             "capas": capas, "transicion": e.get("transicion", "corte")}
        if frente:
            n["frente"] = frente
            n.update(n_frente)
        # la voz suena una vez aunque la frase se parta en dos planos
        n["muda"] = norm(texto) in visto
        visto.add(norm(texto))

        g = e.get("grafico")
        if g:
            tipo = g["tipo"]
            if tipo == "titular":
                n["texto_pantalla"] = {"lineas": [tildes.get(norm(l), l)
                                                  for l in g["lineas"]],
                                       "px": 92, "y": 0.09,
                                       "entrada": g.get("entrada", "pop")}
            elif tipo == "contador":
                n["grafico"] = {"tipo": "cifra", "valor": g["valor"],
                                "decimales": g.get("dec", 0),
                                "sufijo": g.get("sufijo", ""),
                                "pie": g.get("pie", ""), "y": 0.28}
            elif tipo == "reparto":
                n["grafico"] = {"tipo": "reparto", "valor": g["valor"],
                                "etiqueta_a": g.get("etiqueta_a", ""),
                                "etiqueta_b": g.get("etiqueta_b", ""),
                                "parte": 0.9, "y": 0.30}
            else:
                n["grafico"] = dict(g, y=g.get("y", 0.16))
        # TODAS las capas de codigo, no solo dos. Antes me quedaba con las
        # imagenes y tiraba el resto, y las escenas pasaban de las 5-7 capas
        # que pide el storyboard a 2. Ahi se iba el dinamismo entero: el
        # mobiliario de pantalla es lo que llena el encuadre en este estilo.
        formas = []
        for k, c in enumerate(e["capas"]):
            if c.get("tipo_capa") != "codigo":
                continue
            f = c.get("forma")
            if f == "etiqueta_capitulo":
                n["etiqueta"] = c.get("texto", "")
                continue
            if f in ("titular", "contador", "barras", "anillo", "reparto",
                     "subrayado"):
                continue          # esos ya salen por `grafico`
            d = {"forma": f, "retardo_def": round(0.06 + 0.06 * k, 2)}
            if c.get("texto"):
                d["texto"] = tildes.get(norm(c["texto"]), c["texto"])
            if f == "banda_lateral":
                d["lado"] = "izq" if k % 2 == 0 else "der"
            if f == "bloque_esquina":
                d["esquina"] = ("sd", "si", "id", "ii")[k % 4]
            if f == "numero_escena":
                d["n"] = len(escenas) + 1
            if f == "pie_fuente" and not d.get("texto"):
                d["texto"] = "Reserva Federal de San Luis"
            formas.append(d)
        if formas:
            n["formas"] = formas

        # Ningun plano pasa de 4 segundos. Los de 4,5 y 5 se parten en dos y
        # el segundo va mudo: la voz sigue sonando entera por encima.
        if e["duracion"] > TOPE:
            mitad = round(e["duracion"] / 2, 2)
            a1 = dict(n, duracion=mitad)
            a2 = dict(n, id=n["id"] + "b", duracion=round(e["duracion"] - mitad, 2),
                      muda=True)
            a2.pop("grafico", None); a2.pop("texto_pantalla", None)
            # al partir, la segunda mitad pierde el grafico y se queda corta
            # de elementos. Se le devuelve uno de otro tipo para que no baje
            # del minimo, y ademas cambia el encuadre entre las dos mitades.
            extra = ({"forma": "corchete", "retardo_def": 0.12},
                     {"forma": "asterisco", "retardo_def": 0.12},
                     {"forma": "rejilla", "retardo_def": 0.10})[troceadas % 3]
            a2["formas"] = list(a2.get("formas", [])) + [extra]
            escenas += [a1, a2]
            troceadas += 1
        else:
            escenas.append(n)
        t += e["duracion"]

    out = {"titulo": "prueba VOX 1 min", "paleta": "vox",
           "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
           "escenas": escenas}
    with open(os.path.join(AQUI, a.salida), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    def cuenta(e):
        return (1 + len(e["capas"]) + bool(e.get("frente")) + bool(e.get("grafico"))
                + bool(e.get("texto_pantalla")) + bool(e.get("etiqueta"))
                + len(e.get("formas", [])))

    flojas = [(e["id"], cuenta(e)) for e in escenas if cuenta(e) < MIN_ELEM]
    largas = [(e["id"], e["duracion"]) for e in escenas if e["duracion"] > TOPE]
    mudas = sum(1 for e in escenas if e["muda"])
    print(f'{len(escenas)} planos - {t:.1f}s')
    print(f'{recuperadas} frases con las tildes devueltas')
    print(f'{mudas} planos mudos (la frase ya suena en el plano anterior)')
    if faltan:
        print(f'{len(faltan)} imagenes del storyboard sin equivalente:',
              ", ".join(sorted(faltan)))
    n = [cuenta(e) for e in escenas]
    print(f'elementos por plano: min {min(n)}, medio {sum(n)/len(n):.1f}, max {max(n)}')
    print(f'{troceadas} planos partidos por pasar de {TOPE}s')
    if flojas:
        print(f'POR DEBAJO DE {MIN_ELEM} ELEMENTOS:',
              ", ".join(f"{i}({c})" for i, c in flojas[:8]))
    if largas:
        print(f'MAS DE {TOPE}s:', largas[:8])
    print("->", a.salida)
    return 1 if (flojas or largas) else 0


if __name__ == "__main__":
    sys.exit(main())
