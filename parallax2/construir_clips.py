#!/usr/bin/env python3
"""
Construye el episodio entero con METRAJE REAL. Cero imagenes generadas.

    python3 construir_clips.py

Por que existe, al lado de `construir_guion.py`:

  El de capas cuesta unos catorce dolares de imagen por episodio y hace falta
  revisar trescientos PNG. Este cuesta CERO y el material ya esta descargado.
  Lo que hace que no parezca un pase de diapositivas no es de donde sale la
  imagen: es la gradacion por capitulo, las particulas, el Ken Burns con
  desplazamiento, los latigazos, los contadores y los rotulos. Todo eso el
  motor ya lo hace igual sobre un clip que sobre una composicion.

La lista de clips es una LISTA BLANCA revisada a ojo, no la etiqueta del
banco. De cuarenta candidatos que el catalogo daba por buenos, diecisiete no
eran lo que decian ser: un campo de tulipanes etiquetado "money in bank
vault", un castillo escoces como "luxury resort tower". Ninguna metrica
detecta eso. Por eso el pool es corto y esta verificado, y por eso un plano
abstracto cae en un generico del tema en vez de en cualquier cosa.
"""
import collections
import json
import math
import os
import re
import unicodedata

POOL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "pool_clips.json"), encoding="utf-8"))

# Que tema pide cada frase. Se mira en ESTE orden: gana el primero que
# aparezca, de lo mas concreto a lo mas general, porque una frase que habla de
# la licencia Y del dinero es una frase sobre la licencia.
TEMAS = [
    ("ruleta",     ("ruleta", "formula", "matematica", "matematico", "azar", "ventaja")),
    ("papeles",    ("licencia", "licencias", "documento", "expediente", "investigacion",
                    "investigan", "solicitud", "papel", "contrato", "firma", "auditor")),
    ("vigilancia", ("camara", "camaras", "vigilancia", "seguridad", "control", "vigilan")),
    ("oficina",    ("estado", "gobierno", "junta", "comision", "socio", "impuesto",
                    "impuestos", "abogado", "regulador", "inspector", "board")),
    ("fichas",     ("ficha", "fichas", "apostar", "apostaron", "apuesta")),
    ("mesa",       ("crupier", "mesa", "mesas", "cartas", "reparte", "blackjack")),
    ("maquinas",   ("tragaperras", "maquina", "maquinas", "slot")),
    ("dinero",     ("dinero", "millones", "dolares", "euros", "billetes", "coste",
                    "cuesta", "precio", "tasa", "beneficio", "beneficios", "ingresos",
                    "caja", "recaudacion", "margen", "paga", "pagar")),
    ("vegas",      ("vegas", "strip", "nevada")),
    ("lujo",       ("hotel", "resort", "lujo", "espectaculo", "restaurante", "spa",
                    "habitaciones", "suite")),
    ("exterior",   ("edificio", "construir", "construccion", "obra", "terreno",
                    "fachada", "puerta", "puertas", "entrada")),
    ("gente",      ("gente", "cliente", "clientes", "multitud", "publico", "jugador",
                    "jugadores", "empleado", "empleados", "plantilla")),
]
POR_DEFECTO = "sala"

# Grades SUAVES: los normales estan calibrados para arte generado oscuro y
# sobre metraje con manos y caras dejan la piel verde.
CLIMA = {
 "GANCHO":           ("dorado_suave", ["destellos", "bokeh", "niebla", "brasas"]),
 "CAP1_DOS_CASINOS": ("dorado_suave", ["bokeh", "humo", "destellos", "polvo"]),
 "CAP2_EDIFICIO":    ("acero_suave",  ["ceniza", "polvo", "chispas", "niebla"]),
 "CAP3_LICENCIA":    ("frio_suave",   ["polvo", "lluvia", "fuga_luz", "humo"]),
 "CAP4_SOCIO":       ("sepia_archivo",["humo", "polvo", "destellos", "fuga_luz"]),
 "CAP5_INGRESOS":    ("verde_suave",  ["billetes", "bokeh", "destellos", "niebla"]),
 "CAP6_GIRO":        ("rojo_suave",   ["brasas", "ceniza", "lluvia", "chispas"]),
 "CIERRE":           ("dorado_suave", ["niebla", "destellos", "brasas", "bokeh"]),
}

MOVS = ["push_in", "drift_der", "pull_out", "contra_izq", "estatico",
        "drift_izq", "contra_der", "subir", "push_in", "bajar"]

TOPE = 4.5          # un plano de metraje aguanta algo mas que uno compuesto
# Aire entre frase y frase. No basta con el respiro: la transicion solapa
# 0,45 s, asi que la escena siguiente empieza ANTES de que acabe la actual y
# ese solape se come el hueco de la voz. Con 0,55 se salian cuarenta y tres
# frases por decimas. 0,45 de solape mas 0,40 de respiro.
PAUSA = 1.0

# La duracion de cada idea sale de lo que TARDA EN DECIRSE, medida sobre la
# locucion ya sintetizada, no de un numero puesto a mano en el guion. Los que
# habia -siete, ocho, nueve segundos por frase- casi doblaban la voz real:
# ochenta y cinco frases que suman 7:54 repartidas en catorce minutos de
# imagen son seis minutos de silencio. Con la voz mandando, la imagen dura lo
# que dura la narracion.
DURACIONES = {}
_d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "duraciones_voz.json")
if os.path.exists(_d):
    DURACIONES = json.load(open(_d, encoding="utf-8"))


def dura(texto, por_defecto):
    import hashlib
    h = hashlib.sha1(texto.encode("utf-8")).hexdigest()[:16]
    v = DURACIONES.get(h)
    return round(v + PAUSA, 2) if v else por_defecto
SEPARACION = 10     # planos minimos antes de repetir un clip
# Puntos de entrada distintos dentro del mismo clip. Con treinta y nueve
# clips para doscientos planos, alguno sale veinte veces; lo que hace que no
# se note es que cada vez se vea OTRO momento, no el mismo fotograma con otro
# color. Los clips duran nueve segundos y el plano cuatro y medio.
ENTRADAS_CLIP = [0.3, 2.6, 4.6, 1.5, 3.6]


def sin_tildes(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return set(re.findall(r"[a-z]+", t))


def tema_de(texto):
    pal = sin_tildes(texto)
    for tema, claves in TEMAS:
        if pal & set(claves):
            return tema
    return POR_DEFECTO


class Reparto:
    """Elige clip del tema que toca, sin repetir de cerca.

    Si el tema se ha agotado -son treinta y nueve clips para casi doscientos
    planos- se cae a "sala", que es el generico que vale para cualquier frase
    de un episodio de casino. Vale mas un plano de sala de juego sobre una
    frase abstracta que un castillo escoces sobre una concreta.
    """

    def __init__(self, pool):
        self.por_tema = collections.defaultdict(list)
        for tema, q, f in pool:
            self.por_tema[tema].append(f)
        self.ultimo = {}
        self.usados = set()
        self.veces = collections.Counter()

    def desde(self, f):
        """Cada clip se usa una vez, asi que siempre se entra por el principio."""
        return 0.3

    def toca(self, tema, i):
        """Un clip se usa UNA vez en todo el episodio. Nunca dos.

        Antes se permitia repetir con diez planos de separacion, y con
        treinta y nueve clips para doscientos planos alguno salia doce veces.
        Ahora el pool tiene mas clips que planos, asi que cada uno aparece una
        sola vez: se gasta primero el tema que pide la frase y, cuando ese
        tema se agota, se tira del generico. Si se agotara todo -no deberia-
        se avisa en voz alta en vez de repetir a escondidas.
        """
        for t in (tema, POR_DEFECTO):
            libres = [f for f in self.por_tema.get(t, []) if f not in self.usados]
            if libres:
                f = libres[0]
                self.usados.add(f)
                return f
        libres = [f for v in self.por_tema.values() for f in v
                  if f not in self.usados]
        if libres:
            f = libres[0]
            self.usados.add(f)
            return f
        print(f"  AVISO: sin clips sin usar en el plano {i}; se repite uno")
        todos = [f for v in self.por_tema.values() for f in v]
        return todos[i % len(todos)]


def main():
    import importlib.util
    aqui = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("cg", os.path.join(aqui, "construir_guion.py"))
    src = open(os.path.join(aqui, "construir_guion.py"), encoding="utf-8").read()
    ns = {}
    exec(src.split("def apoyo_para")[0], ns)
    GUION, GRAFICOS, ROTULOS = ns["GUION"], ns["GRAFICOS"], ns["ROTULOS"]

    reparto = Reparto(POOL)
    escenas = []
    for cap, objetivo, beats in GUION:
        grade, paleta = CLIMA.get(cap, ("dorado_suave", ["polvo"]))
        primera = len(escenas)
        for i, (texto, dur, mov, _capas) in enumerate(beats, 1):
            tema = tema_de(texto)
            dur = dura(texto, dur)
            # una idea larga se cuenta en varios planos, no en uno largo
            k = max(1, int(math.ceil(dur / TOPE)))
            paso = round(dur / k, 2)
            graf = next((dict(s) for c, s in GRAFICOS if c.lower() in texto.lower()), None)
            rot = next((dict(s) for c, s in ROTULOS if c.lower() in texto.lower()), None)
            for j in range(k):
                n = len(escenas)
                elegido = reparto.toca(tema, n)
                esc = {
                    "id": f"{cap.lower()}_{i:02d}" + ("abcd"[j] if j else ""),
                    "texto": texto,
                    "duracion": paso,
                    "movimiento": MOVS[n % len(MOVS)],
                    "grade": grade,
                    "efectos": [paleta[n % len(paleta)]],
                    "clip": "stock/" + elegido,
                    "clip_desde": reparto.desde(elegido),
                    "capas": [],
                }
                if j == 0 and graf:
                    esc["grafico"] = dict(graf, retardo=0.6, entrada="golpe")
                if j == 0 and rot:
                    esc["texto_pantalla"] = rot
                escenas.append(esc)
        escenas[-1]["cierra_bloque"] = True
        # un latigazo cada cinco planos: acento, no tic
        for k in range(primera, len(escenas) - 1):
            if not escenas[k].get("cierra_bloque") and (k - primera) % 5 == 3:
                escenas[k]["latigo"] = "izq" if k % 2 else "der"

    guion = {"titulo": "Cuanto cuesta tener un casino",
             "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
             "estilo": "metraje real", "escenas": escenas}
    with open(os.path.join(aqui, "proyecto", "episodio.json"), "w", encoding="utf-8") as f:
        json.dump(guion, f, ensure_ascii=False, indent=2)

    total = sum(e["duracion"] for e in escenas)
    print(f'{len(escenas)} planos · {total/60:.0f}:{total%60:04.1f}')
    print(f'{len({e["clip"] for e in escenas})} clips distintos · '
          f'{sum(1 for e in escenas if e.get("grafico"))} graficos · '
          f'{sum(1 for e in escenas if e.get("texto_pantalla"))} rotulos · '
          f'{sum(1 for e in escenas if e.get("latigo"))} latigazos')
    top = collections.Counter(e["clip"] for e in escenas).most_common(3)
    print("mas usados: " + ", ".join(f"{os.path.basename(k)} x{v}" for k, v in top))


if __name__ == "__main__":
    main()
