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
    for e in src["escenas"]:
        if t >= a.segundos:
            break
        texto = tildes.get(norm(e["texto"]), e["texto"])
        if texto != e["texto"]:
            recuperadas += 1

        capas, frente = [], None
        for c in e["capas"]:
            if c.get("tipo_capa") != "imagen" or c.get("rol") == "fondo":
                continue
            arch = c["archivo"]
            if c["rol"] == "frente":
                frente = FRENTES.get(arch, arch)
                if arch not in FRENTES:
                    faltan.add(arch)
            else:
                capas.append({"archivo": SUJETOS.get(arch, arch)})
                if arch not in SUJETOS:
                    faltan.add(arch)

        n = {"id": e["id"], "texto": texto, "duracion": e["duracion"],
             "capas": capas, "transicion": e.get("transicion", "corte")}
        if frente:
            n["frente"] = frente
        # la voz suena una vez aunque la frase se parta en dos planos
        n["muda"] = norm(texto) in visto
        visto.add(norm(texto))

        g = e.get("grafico")
        if g:
            tipo = g["tipo"]
            if tipo == "titular":
                n["texto_pantalla"] = {"lineas": [tildes.get(norm(l), l)
                                                  for l in g["lineas"]],
                                       "px": 92, "y": 0.09}
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
        for c in e["capas"]:
            if c.get("forma") == "etiqueta_capitulo":
                n["etiqueta"] = c.get("texto", "")
            if c.get("forma") == "banda_inferior":
                n["banda"] = True
        escenas.append(n)
        t += e["duracion"]

    out = {"titulo": "prueba VOX 1 min", "paleta": "vox",
           "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
           "escenas": escenas}
    with open(os.path.join(AQUI, a.salida), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    mudas = sum(1 for e in escenas if e["muda"])
    print(f'{len(escenas)} planos - {t:.1f}s')
    print(f'{recuperadas} frases con las tildes devueltas')
    print(f'{mudas} planos mudos (la frase ya suena en el plano anterior)')
    if faltan:
        print(f'{len(faltan)} imagenes del storyboard sin equivalente:',
              ", ".join(sorted(faltan)))
    print("->", a.salida)


if __name__ == "__main__":
    main()
