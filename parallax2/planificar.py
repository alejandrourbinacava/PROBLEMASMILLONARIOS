#!/usr/bin/env python3
"""
Reparte composiciones, movimientos, entradas y efectos con gramatica de
montaje, en vez de por rotacion.

    python3 planificar.py proyecto/guion.json

La rotacion modulo N garantiza que dos escenas seguidas no sean iguales,
pero no produce un montaje: produce un ciclo. Un montaje real alterna
ESCALA (ancho / medio / cerca) y LADO (izquierda / centro / derecha), y
cuando una idea se parte en varios planos, los planos se acercan.
"""
import json, argparse, collections

# ---------------------------------------------------------------------------
# TIPOS DE ESCENA. Que las 225 sean fondo + sujeto + primer plano es lo que
# hace que el video se lea igual de principio a fin, por mucho que cambie
# el encuadre. Hay que alternar la ESTRUCTURA, no solo la composicion.
#
#   pleno    las tres capas. El plano de referencia.
#   detalle  sin fondo: sujeto y primer plano muy cerca, poca profundidad.
#   silueta  sin sujeto: solo el fondo y el primer plano recortado. Respira.
#   grafico  el dato ocupa la pantalla, el fondo desenfocado detras.
#   rotulo   una frase sola sobre el fondo. Para los remates.
#   clip     metraje de stock.
# ---------------------------------------------------------------------------
TIPOS = ["pleno", "detalle", "silueta", "grafico", "rotulo"]

# Ritmo de estructura. El pleno es el suelo; los demas entran a intervalos
# y nunca dos seguidos, o dejan de ser un cambio de registro.
RITMO_TIPO = ["pleno", "detalle", "pleno", "silueta", "pleno", "rotulo",
              "pleno", "detalle", "pleno", "silueta", "detalle", "pleno"]


def frase_corta(texto, tope=34):
    """La clausula mas corta de la locucion, para los rotulos."""
    trozos = [t.strip(" .,") for t in texto.replace(";", ".").split(".") if t.strip()]
    trozos += [t.strip(" ,") for t in texto.split(",") if t.strip()]
    cand = [t for t in trozos if 8 <= len(t) <= tope]
    return min(cand, key=len).upper() if cand else None


def aplicar_tipo(e, tipo):
    """Reestructura las capas de la escena segun su tipo."""
    capas = e.get("capas", [])
    por_rol = {c["rol"]: c for c in capas}
    e["tipo"] = tipo

    if tipo == "detalle" and len(capas) >= 2:
        e["capas"] = [c for c in capas if c["rol"] != "fondo"] or capas
    elif tipo == "silueta" and "fondo" in por_rol and len(capas) >= 3:
        e["capas"] = [c for c in capas if c["rol"] in ("fondo", "frente",
                                                       "frente_bajo")]
    elif tipo == "grafico":
        e["capas"] = [c for c in capas if c["rol"] == "fondo"] or capas[:1]
    elif tipo == "rotulo":
        e["capas"] = [c for c in capas if c["rol"] == "fondo"] or capas[:1]
        f = frase_corta(e.get("texto", ""))
        if f:
            e["texto_pantalla"] = {"texto": f, "px": 108, "y": 0.5,
                                   "acento": [255, 196, 90], "estilo": "golpe"}
    else:
        e["capas"] = capas
    return e


# ---------------------------------------------------------------------------
# Cada composicion se clasifica por escala y por el lado donde cae el sujeto.
# ---------------------------------------------------------------------------
COMPOS = {
    "lejos":     ("ancho", "C"), "lejos_izq": ("ancho", "I"),
    "lejos_der": ("ancho", "D"), "alto":      ("ancho", "C"),
    "alto_der":  ("ancho", "D"),
    "centrado":  ("medio", "C"), "izquierda": ("medio", "I"),
    "derecha":   ("medio", "D"), "diagonal":  ("medio", "I"),
    "esquina":   ("medio", "D"),
    "cerca":     ("cerca", "C"), "cerca_izq": ("cerca", "I"),
    "cerca_der": ("cerca", "D"), "bajo":      ("cerca", "C"),
    "bajo_izq":  ("cerca", "I"),
}

# Se alterna I -> D -> C -> D -> I ... El centro es un descanso, no el
# valor por defecto: si mas de un tercio de las escenas cae centrada, el
# video vuelve a leerse como una sola composicion repetida.
CICLO_LADO = ["I", "D", "C", "D", "I", "C"]

# Respiracion del capitulo: se abre, se acerca, se vuelve a abrir.
RITMO = ["ancho", "medio", "cerca", "medio", "cerca", "ancho", "medio", "cerca"]

# Si el sujeto cae a un lado, la camara deriva hacia el otro: deja aire
# delante del sujeto en vez de comerselo.
MOV_POR_LADO = {
    "I": ["drift_der", "contra_der", "push_in"],
    "D": ["drift_izq", "contra_izq", "push_in"],
    "C": ["push_in", "pull_out", "subir", "estatico", "bajar"],
}

ENTRADAS = ["golpe", "latigo_izq", "desplome", "rebote", "latigo_der"]
EFECTOS = ["polvo", "brasas", "bokeh", "ceniza", "fuga_luz", "chispas"]

# Grade por capitulo: el color marca el tema, no la escena.
GRADE_CAP = {
    "gancho": "dorado_noche",
    "cap1": "dorado_noche",
    "cap2": "sepia_archivo",
    "cap3": "frio_institucional",
    "cap4": "acero",
    "cap5": "verde_dinero",
    "cap6": "rojo_alerta",
    "cierre": "dorado_noche",
}


def clave_cap(ident):
    return ident.split("_")[0]


def base_beat(ident):
    """gancho_03b -> gancho_03: los trozos de una misma idea."""
    return ident.rstrip("abcdefghij") if ident[-1].isalpha() else ident


def elegir(candidatos, evitar, historial, n=2):
    """El primero que no este en los ultimos n usados."""
    recientes = historial[-n:]
    for c in candidatos:
        if c not in recientes and c not in evitar:
            return c
    for c in candidatos:
        if c not in evitar:
            return c
    return candidatos[0]


def planificar(escenas):
    por_escala = collections.defaultdict(list)
    for nom, (esc, lado) in COMPOS.items():
        por_escala[esc].append(nom)

    h_comp, h_lado, h_mov, h_ent, h_fx = [], [], [], [], []
    beat_ant, paso_beat = None, 0
    cambios = collections.Counter()
    tipo_ant = "pleno"

    for i, e in enumerate(escenas):
        beat = base_beat(e["id"])
        if beat == beat_ant:
            paso_beat += 1
        else:
            paso_beat, beat_ant = 0, beat

        # --- tipo de escena ---
        if e.get("clip"):
            tipo = "clip"
        elif e.get("grafico"):
            tipo = "grafico"                      # el dato manda
        else:
            tipo = RITMO_TIPO[i % len(RITMO_TIPO)]
            if tipo != "pleno" and tipo_ant != "pleno":
                tipo = "pleno"                    # nunca dos seguidos
            if tipo == "detalle" and len(e.get("capas", [])) < 2:
                tipo = "pleno"
            if tipo == "silueta" and len(e.get("capas", [])) < 3:
                tipo = "pleno"
            if tipo == "rotulo" and not frase_corta(e.get("texto", "")):
                tipo = "pleno"
            # remate de capitulo: siempre rotulo si hay frase que sirva
            if i + 1 < len(escenas) and \
               clave_cap(escenas[i + 1]["id"]) != clave_cap(e["id"]) and \
               frase_corta(e.get("texto", "")):
                tipo = "rotulo"
        aplicar_tipo(e, tipo)
        tipo_ant = tipo

        # --- escala ---
        if tipo == "detalle":
            escala = "cerca"
        elif tipo in ("grafico", "rotulo", "silueta"):
            escala = "ancho"
        elif paso_beat == 0:
            escala = RITMO[i % len(RITMO)]
        else:
            # los trozos de una misma idea se ACERCAN: es un corte con
            # intencion, no un salto suelto
            escala = ["ancho", "medio", "cerca"][min(2, paso_beat)]

        # --- lado: viene del ciclo, no de lo que sobre ---
        objetivo = CICLO_LADO[i % len(CICLO_LADO)]
        if h_lado and objetivo == h_lado[-1]:
            objetivo = CICLO_LADO[(i + 1) % len(CICLO_LADO)]

        cands = [c for c in por_escala[escala] if COMPOS[c][1] == objetivo] \
                or [c for c in por_escala[escala] if COMPOS[c][1] != (h_lado[-1] if h_lado else "")] \
                or por_escala[escala]
        cands.sort(key=lambda c: c in h_comp[-4:])
        comp = elegir(cands, [], h_comp, 2)
        lado = COMPOS[comp][1]

        # --- movimiento acorde al lado ---
        mov = elegir(MOV_POR_LADO[lado], [], h_mov, 2)

        # --- entradas: escalonadas y sin repetir la de la escena anterior ---
        ent = elegir(ENTRADAS, [], h_ent, 2)
        for j, c in enumerate(e.get("capas", [])):
            c["entrada"] = ent if j else ("escala" if c["rol"] == "fondo" else ent)
            c["retardo"] = round(j * 0.09, 2)

        # --- efectos: uno de cada tres escenas, y nunca el mismo seguido ---
        if i % 3 == 0:
            fx = elegir(EFECTOS, [], h_fx, 3)
            e["efectos"] = [fx]
            h_fx.append(fx)
        else:
            e.pop("efectos", None)

        cambios["comp"] += e.get("composicion") != comp
        cambios["mov"] += e.get("movimiento") != mov
        e["composicion"], e["movimiento"] = comp, mov
        e["grade"] = GRADE_CAP.get(clave_cap(e["id"]), "neutro")

        h_comp.append(comp); h_lado.append(lado)
        h_mov.append(mov); h_ent.append(ent)
    return cambios


def informe(escenas):
    seguidas = sum(1 for a, b in zip(escenas, escenas[1:])
                   if a["composicion"] == b["composicion"])
    mismo_lado = sum(1 for a, b in zip(escenas, escenas[1:])
                     if COMPOS[a["composicion"]][1] == COMPOS[b["composicion"]][1])
    tipos = collections.Counter(e.get("tipo", "pleno") for e in escenas)
    print(f"  tipos    {dict(tipos)}")
    esc = collections.Counter(COMPOS[e["composicion"]][0] for e in escenas)
    lados = collections.Counter(COMPOS[e["composicion"]][1] for e in escenas)
    n = len(escenas)
    print(f"  composiciones repetidas seguidas: {seguidas}")
    print(f"  mismo lado dos veces seguidas:    {mismo_lado} de {n-1}")
    print(f"  escalas  {dict(esc)}")
    print(f"  lados    {dict(lados)}")
    print(f"  centrado en el {100*lados['C']//n}% de las escenas")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    a = ap.parse_args()
    g = json.load(open(a.guion, encoding="utf-8"))
    print("ANTES"); informe(g["escenas"])
    planificar(g["escenas"])
    print("\nDESPUES"); informe(g["escenas"])
    json.dump(g, open(a.guion, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f'\n{len(g["escenas"])} escenas replanificadas -> {a.guion}')


if __name__ == "__main__":
    main()
