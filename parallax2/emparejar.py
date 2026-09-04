#!/usr/bin/env python3
"""
Empareja cada frase con el clip que NOMBRA su palabra, y marca las que no
tienen ninguno posible.

    python3 emparejar.py proyecto/episodio_banco.json

La regla de oro del canal es que la imagen tiene que ver con lo que se dice.
El episodio del banco la rompe de forma estructural: 130 ficheros distintos
pero seis ideas, y el 68% son gente en una reunion, gente contando billetes o
gente firmando. Eso no se arregla cambiando un clip; se arregla decidiendo,
frase por frase, si hay algo que filmar.

Este script hace esa decision y no la esconde:

  - Si la frase nombra algo que existe en el pool -una fachada, una firma,
    una maquina de contar-, le asigna ese clip.
  - Si no, lo dice: `SIN IMAGEN POSIBLE`. Esa frase no quiere un clip de
    relleno, quiere un grafico. Poner metraje generico ahi es lo que hace
    que el video parezca barato.

Y descarta el metraje en euros. El guion habla de dolares y de Estados
Unidos, y nueve planos del montaje actual ensenan billetes de euro.
"""
import argparse
import io
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))

# Palabra de la locucion -> palabras que aparecen en el nombre del clip.
# Solo terminos que EXISTEN en el pool: un sinonimo bonito que no tiene
# metraje detras no empareja nada y ademas disimula el agujero.
LEXICO = {
    "banco": ["bank", "facade"], "bancos": ["bank", "facade"],
    "bancaria": ["bank"], "bancario": ["bank"],
    "oficina": ["office", "desk"], "oficinas": ["office", "desk"],
    "mostrador": ["desk", "register"], "sucursal": ["bank", "facade"],
    "fachada": ["facade", "building"],
    "edificio": ["building", "corporate"], "edificios": ["building"],
    "sede": ["corporate", "building", "glass"],
    "ciudad": ["city", "aerial"], "calle": ["street", "city", "traffic"],
    "puertas": ["door", "revolving"], "puerta": ["door", "revolving"],
    "abres": ["door", "open"], "abrir": ["door", "open"],
    "cola": ["revolving", "people", "busy"],
    "gente": ["people", "busy"], "clientes": ["people", "busy"],
    "cliente": ["people", "register"],

    "dinero": ["money", "cash"], "dolares": ["money", "cash", "bills"],
    "dolar": ["money", "cash"], "millones": ["cash", "stack", "briefcase"],
    "moneda": ["coins"], "monedas": ["coins"],
    "billetes": ["bills", "banknotes", "cash"],
    "contando": ["counting", "machine"], "contar": ["counting"],
    "maquinaria": ["machine"], "maquina": ["machine"],
    "efectivo": ["cash"], "caja": ["register", "briefcase"],

    "firma": ["signing", "pen", "hands"], "firmar": ["signing", "pen"],
    "firmado": ["signing"], "contrato": ["contract"],
    "solicitud": ["documents", "paperwork", "contract"],
    "licencia": ["contract", "documents"], "ficha": ["contract", "documents"],
    "permiso": ["contract", "documents"],
    "autorizacion": ["documents", "contract"],
    "papeles": ["paperwork", "documents"], "papeleo": ["paperwork"],
    "expediente": ["documents", "paperwork"],
    "abogados": ["legal", "documents"], "abogado": ["legal"],
    "seguro": ["insurance", "documents"], "garantia": ["insurance"],
    "facturas": ["invoices"], "factura": ["invoices"],
    "leer": ["reading"], "lee": ["reading"], "leelo": ["reading"],

    "reunion": ["meeting", "boardroom"], "socios": ["meeting", "handshake"],
    "socio": ["handshake", "meeting"], "negociar": ["negotiation"],
    "consejo": ["boardroom", "decision"], "junta": ["boardroom"],
    "decide": ["decision"], "deciden": ["decision"], "decides": ["decision"],
    "entrevista": ["interview", "job"],
    "evaluan": ["interview", "reviewing"],
    "regulador": ["reviewing", "manager", "documents"],
    "reguladores": ["reviewing", "manager"],
    "supervision": ["reviewing", "manager"],
    "cumplimiento": ["documents", "reviewing"],
    "vigilado": ["reviewing", "manager"],

    "grafica": ["graph", "chart"], "crece": ["graph", "growth"],
    "sube": ["graph", "rising"], "cae": ["declining"],
    "porcentaje": ["percentage", "graph"], "margen": ["chart", "graph"],
    "rendimiento": ["graph", "profit", "chart"],
    "inversion": ["investment", "growth"],
    "capital": ["chart", "calculator"],
    "calculadora": ["calculator"], "calculo": ["calculator"],
    "cuentas": ["calculator", "invoices"], "cuenta": ["calculator"],
    "coste": ["invoices", "calculator"], "costes": ["invoices", "calculator"],
    "gastos": ["invoices", "calculator"], "cuesta": ["invoices", "calculator"],
    "nominas": ["payroll", "documents"], "nomina": ["payroll"],
    "personal": ["job", "interview", "payroll"],

    "alquiler": ["real", "estate"], "inmueble": ["real", "estate"],
    "obra": ["blueprint", "construction"], "plano": ["blueprint"],
    "reloj": ["clock", "time"], "tiempo": ["clock", "time", "lapse"],
    "anos": ["clock", "time", "lapse"],
    "perdidas": ["declining", "worried"], "susto": ["worried"],
    "riesgo": ["worried", "declining"],
    "preocupa": ["worried"], "incomoda": ["worried", "serious"],
    "publicidad": ["billboard", "advertisement"],
    "anuncio": ["billboard", "advertisement"],
    "luz": ["electricity", "meter"], "consumo": ["electricity", "meter"],
    "llaves": ["keys", "landlord"],

    # --- vocabulario del guion v2: segunda persona e historias. El v1 era
    # expositivo y su lexico no cubre "compras", "hipoteca", "panico" ni
    # "carteles", asi que casi la mitad de los planos se quedaban huerfanos.
    "compras": ["handshake", "business", "contract"],
    "comprar": ["handshake", "business"], "compra": ["handshake", "business"],
    "vender": ["handshake", "sale"], "venden": ["handshake", "sale"],
    "vendes": ["handshake", "sale"], "vende": ["handshake", "sale"],
    "hipoteca": ["mortgage", "calculator"],
    "hipotecas": ["mortgage", "calculator"],
    "tarjeta": ["register", "cash"], "tarjetas": ["register", "cash"],
    "deuda": ["declining", "invoices"], "deudas": ["invoices"],
    "cajero": ["register", "counting"],
    "interes": ["percentage", "graph"], "intereses": ["percentage", "graph"],
    "ahorro": ["coins", "money"],
    "pagas": ["invoices", "cash"], "paga": ["invoices", "cash"],
    "pago": ["invoices", "calculator"], "pagar": ["invoices", "cash"],
    "cobras": ["counting", "cash"], "cobra": ["counting", "cash"],
    "beneficio": ["profit", "graph"], "beneficios": ["profit", "graph"],
    "creces": ["growth", "graph"], "crecen": ["growth", "graph"],
    "comisiones": ["invoices", "calculator"],
    "activos": ["chart", "graph"],
    "bonos": ["stock_market", "chart"], "tipos": ["stock_market", "graph"],
    "mercado": ["stock_market", "screen"],
    "liquidez": ["counting", "cash"],
    "depositantes": ["people", "revolving"],
    "panico": ["worried", "declining"], "quiebra": ["declining", "worried"],
    "derrumbe": ["declining"], "cae": ["declining"], "cayo": ["declining"],
    "pantalla": ["screen"], "movil": ["screen"],
    "sistemas": ["screen", "machine"], "informatico": ["screen"],
    "transferencias": ["screen", "machine"],
    "tribunal": ["legal", "documents"], "multa": ["legal", "invoices"],
    "empleados": ["job", "interview", "people"],
    "director": ["manager", "reviewing"],
    "consejero": ["boardroom", "manager"],
    "acciones": ["stock_market", "chart"],
    "paginas": ["paperwork", "documents"],
    "escribe": ["signing", "screen"], "teclea": ["screen"],
    "cuentas": ["calculator", "invoices"],
    "millones": ["cash", "stack", "briefcase"],
    "clientes": ["people", "busy", "register"],
    "puertas": ["door", "revolving"],
    "guardar": ["briefcase", "insurance"],
    "custodias": ["insurance", "documents"],
    "retirar": ["counting", "register"],
    "colchon": ["insurance", "briefcase"],
}

VACIAS = {"que", "los", "las", "del", "por", "con", "para", "una", "uno",
          "eso", "esa", "ese", "esto", "hay", "son", "mas", "pero", "como",
          "todo", "todos", "cada", "sus", "sin", "muy", "ese", "les", "nos"}


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def claves(texto):
    """Las palabras de la frase que tienen metraje detras."""
    fuera = []
    for w in re.findall(r"[a-z]+", norm(texto)):
        if len(w) < 3 or w in VACIAS:
            continue
        if w in LEXICO:
            fuera.append(w)
    return fuera


def puntua(texto, ruta, desc):
    """Cuantas palabras de la frase nombra este clip. Cero es cero: no se
    inventa un empate para rellenar."""
    bolsa = set(re.findall(r"[a-z]+", (desc + " " + ruta).lower()))
    p, casadas = 0, []
    for w in claves(texto):
        golpes = [t for t in LEXICO[w] if t in bolsa]
        if golpes:
            # la primera palabra de la lista es la literal; vale mas que un
            # sinonimo de ambiente
            p += 2 if golpes[0] == LEXICO[w][0] else 1
            casadas.append(w)
    return p, casadas


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--pool", default="pool_banco_revisado.json")
    ap.add_argument("--salida", default=None,
                    help="escribe un guion nuevo con los clips reasignados")
    ap.add_argument("--con-euros", action="store_true",
                    help="no descartar el metraje en euros")
    a = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    g = json.load(io.open(os.path.join(AQUI, a.guion), encoding="utf-8"))
    pool = json.load(io.open(os.path.join(AQUI, a.pool), encoding="utf-8"))

    euros = [r for r in pool if "euro" in r[2].lower()]
    if not a.con_euros:
        pool = [r for r in pool if "euro" not in r[2].lower()]

    escenas = g["escenas"]

    # Todas las combinaciones, y se reparte de mejor a peor. Asi el clip de
    # la fachada cae en la frase que habla de la fachada, y no en la primera
    # que pasaba por ahi.
    combis = []
    for i, e in enumerate(escenas):
        t = e.get("texto") or ""
        for _, desc, ruta in pool:
            p, cas = puntua(t, ruta, desc)
            if p:
                combis.append((p, i, ruta, cas))
    combis.sort(key=lambda x: -x[0])

    asignado, usados = {}, set()
    for p, i, ruta, cas in combis:
        if i in asignado or ruta in usados:
            continue
        asignado[i] = (ruta, p, cas)
        usados.add(ruta)

    huerfanas = [i for i in range(len(escenas)) if i not in asignado]

    print(f"{len(escenas)} escenas | {len(pool)} clips en el pool")
    print(f"  emparejadas por palabra : {len(asignado)}")
    print(f"  SIN IMAGEN POSIBLE      : {len(huerfanas)}"
          f"  <- estas quieren grafico, no clip")
    if euros and not a.con_euros:
        print(f"  descartados por estar en euros: {len(euros)}")

    print("\n--- lo que ninguna imagen del pool puede decir:")
    for i in huerfanas:
        e = escenas[i]
        marca = "G" if e.get("grafico") else " "
        print(f"  {marca} {e['id']:<12} {(e.get('texto') or '')[:78]}")

    print("\n--- emparejadas (palabra de la frase -> clip):")
    for i in sorted(asignado)[:14]:
        ruta, p, cas = asignado[i]
        print(f"  {escenas[i]['id']:<12} {p:2d}  {','.join(cas)[:26]:<26} "
              f"{os.path.basename(ruta)[:38]}")

    if a.salida:
        for i, (ruta, _, _) in asignado.items():
            escenas[i]["clip"] = ruta
        for i in huerfanas:
            # No se deja un clip de relleno: se marca para que lo coja el
            # generador de graficos. Un clip que no dice nada es peor que
            # ningun clip.
            escenas[i]["clip_sin_imagen"] = True
        destino = os.path.join(AQUI, a.salida)
        json.dump(g, io.open(destino, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"\nescrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
