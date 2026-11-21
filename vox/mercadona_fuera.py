"""Guion tecnico de «Por que Mercadona NO quiere crecer fuera de Espana» — piel ANIM.

    python mercadona_fuera.py            -> vox/mercadona_fuera.spec.json

Los numeros de fragmento son los de la locucion (`locucion.txt`, 97 fragmentos).

Dos clases de plano, que se alternan (como en Moatseek):

  animado     la idea se representa con actores -tiendas, camiones, fajos,
              monedas, personas, paises- que se mueven y se cuentan con la voz
  por capas   imagen real: metraje desenfocado al fondo (`clips`), un texto
              enorme detras y un recorte limpio delante (`fotos`: c_*.webp)

Los pasos atan cada movimiento a la palabra que lo dice: (fragmento, frase),
(fragmento, fraccion) o (fragmento, "trozo literal").

  an(comp, de, pasos)     escena del registro ESCENAS (remotion/src/vox/video/m_*.tsx)
  cita / capitulo
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from tecnico import Media, Tiempos, construye  # noqa: E402

MARCA = {"nombre": "MERCADONA", "color": "#12B25E", "claro": "#27D07A", "oscuro": "#053D22", "acento": "#FF7A1A"}
RES = "resultados anuales de Mercadona · 10 de marzo de 2026"
ROIG = {"autor": "Juan Roig", "cargo": "Presidente de Mercadona"}
MEDIA = Media(["parallax2/proyecto/stock_mercadona", "vox/media/mercadona_fuera"], os.path.join(AQUI, "mercadona_fuera.media.json"))

S = []


def C(a, paso=None, **k):
    """Un clip (o foto) de fondo. `paso`: cuando corta a el."""
    d = {"a": a, "paso": paso}
    d.update(k)
    return d


def E(tipo, de, d, pasos=None, fuente=None, cap=None, clips=None, fotos=None):
    e = {"tipo": tipo, "de": de, "d": d}
    if pasos:
        e["pasos"] = pasos
    if fuente:
        e["fuente"] = fuente
    if cap is not None:
        e["cap"] = cap
    if clips:
        e["fondo_clip"] = clips
    if fotos:
        # imagenes reales que la escena ensena: le llegan en ctx.medios y las busca por nombre
        e["medios"] = [dict(a=f + ".webp" if f.startswith("c_") else f, paso={"s": 0}, queda=True) for f in fotos]
    S.append(e)


def an(comp, de, pasos=None, fuente=None, fotos=None, clips=None, **d):
    E("anim", de, dict(comp=comp, **d), pasos=pasos, fuente=fuente, fotos=fotos, clips=clips)


def cita(de, pasos, partes, cuando, previo=None, fuente=None, nota=None, pregunta=None, fondo="headquarters_office"):
    """Cita de Juan Roig, por capas: la sede desenfocada, su nombre detras y su retrato delante."""
    d = dict(ROIG, cuando=cuando, partes=partes)
    for k, v in (("previo", previo), ("nota", nota), ("pregunta", pregunta)):
        if v:
            d[k] = v
    E("cita", de, d, pasos=pasos, fuente=(fuente + " · " if fuente else "") + "foto: Junta de Andalucía, CC BY-SA 2.0", fotos=["c_roig"], clips=[C(fondo)])


FOTOS = " · fotos: Wikimedia Commons"

# =============================================================== GANCHO
an("ventas", 0, [(0, 0), (1, 0), (1, 1), (1, 2), (1, "pasan por")], fuente=RES,
   clips=[C("supermarket_checkout_lanes"), C("aerial_town_avenue", 2), C("hands_checkout", 3)])
an("mapa_dos", 2, [(2, 0), (3, 0), (3, 1), (3, 2), (4, 0), (4, "tiene tiendas")],
   fuente="Mercadona (tiendas) · Worldpanel by Numerator (cuotas) · Schwarz Gruppe (países)")
cita(5, [(5, 0), (5, "«No hay")], ["*No hay un tercer país.* No vamos a ir a un tercer país."], "10 de marzo de 2026",
     previo="Marzo de 2026 · presentación de resultados", pregunta="¿Cuál será el siguiente país?",
     fuente="OKDiario, 11-3-2026", fondo="headquarters_night")
an("niega", 6, [(6, 0), (6, "se niega"), (7, 0), (7, 1), (8, 0), (8, 1)])

# =============================================================== 1
E("capitulo", 9, {"num": "1", "titulo": "El plan que empezaba por *«I»*", "sub": "Más de diez años pensando en salir de España"},
  pasos=[(9, 0), (9, 0.3)], cap="1")
an("italia", 10, [(10, 0), (10, "aterrizaje"), (10, 1), (10, "cerca"), (10, "con un mercado"), (10, 2)], fuente="Valencia Plaza, 12-3-2019")
an("frescos", 11, [(11, 0), (11, "los productos frescos")],
   clips=[C("fish_counter"), C("fresh_fish", (11, 0.55))], fuente="Valencia Plaza, 12-3-2019")
an("portugal_elige", 12, [(12, 0), (12, "eligió"), (12, 2), (13, 0), (13, "un mercado cercano"), (13, "que encajaba")],
   fuente="nota de Mercadona, 23-6-2016 · traducción propia de la versión en inglés")
an("camion", 14, [(14, 0), (14, "se puede llegar"), (14, "desde los almacenes")],
   clips=[C("truck_highway_bridge")])
an("plan_inicial", 15, [(15, 0), (15, 1), (15, 2), (15, 3), (15, 4)], fuente="nota de Mercadona, 23-6-2016")
an("tres_anios", 16, [(16, 0), (16, 1), (16, "abrir la primera")])
an("pruebas", 17, [(17, 0), (17, 1), (18, 0), (18, "seis de cada"), (18, "había que")], fuente="Valencia Plaza y Alicante Plaza, marzo de 2019")
an("mancha", 19, [(19, 0), (19, 1), (19, "tres o cuatro"), (19, "mancha"), (20, 0), (20, "Y añadió")], fuente="Valencia Plaza, 12-3-2019")
an("siete_anios", 21, [(21, 0), (21, 1), (22, 0), (22, 1), (23, 0)])

# =============================================================== 2
E("capitulo", 24, {"num": "2", "titulo": "Lo que cuesta *un país*", "sub": "Julio de 2019 · abre la primera tienda"},
  pasos=[(24, 0), (24, 0.12)], cap="2")
an("canidelo", (24, "en Canidelo"), [(24, "en Canidelo"), (24, "al lado"), (25, 0)], clips=[C("f_porto2")],
   fuente="El Independiente, 2-7-2019")
an("cuenta", 26, [(26, 0), (26, 1), (27, 0), (27, "supera"), (28, 0)], fuente="Mercadona (2016) · Valencia Plaza (2019) · ECO (2026)")
an("ganado", 29, [(29, 0), (30, 0), (30, 1), (30, 2), (30, 3), (31, 0)], fuente="ECO (eco.sapo.pt), 12-3-2024 y 10-3-2026")
an("despega", 32, [(32, 0), (32, "Sesenta y nueve"), (32, "dos mil noventa"), (32, "veintiséis")], fuente=RES)
an("margen", 33, [(33, 0), (33, 1), (34, 0), (34, "algo más de cuatro"), (34, 1), (34, "poco más de uno"), (35, 0)], fuente=RES)
an("por_tienda", 36, [(36, 0), (36, 1), (36, 2), (36, "más que la media")], fuente=RES + " · cálculo propio: ventas entre tiendas")
an("hogares", 37, fuente="Worldpanel by Numerator, primer semestre de 2026 (vía Xataka)")
an("cuota", 38, [(38, 0), (38, "siete coma"), (38, "más de lo que"), (38, "tres décadas")], fuente="Worldpanel by Numerator, 2026 (vía Xataka)")
an("detras", 39, [(39, 0), (39, 1)])
an("lista", 40, [(40, 0), (40, "«Cuesta"), (40, "corregir"), (40, "adaptar"), (40, "y encontrar"), (41, 0), (41, "«Cuando"), (42, 0), (42, 1)],
   fuente="ECO (eco.sapo.pt), 10-3-2026 · traducido del portugués · foto: Junta de Andalucía, CC BY-SA 2.0", fotos=["c_roig"], clips=[C("headquarters_office")])

# =============================================================== 3
E("capitulo", 43, {"num": "3", "titulo": "Por qué su máquina *no viaja*", "sub": "Qué es Mercadona de verdad"}, pasos=[(43, 0), (43, 0.5)], cap="3")
an("cadena", 44, [(44, 0), (44, 1)])
an("marcas", 45, [(45, 0), (45, "Hacendado"), (45, "Deliplus"), (45, "Bosque")], fuente="Worldpanel, 2025 (77,8 %), vía elEconomista")
an("encargo", 46, [(46, 0), (46, "los encarga"), (46, "con los que"), (46, "y a los que")])
an("red_es", 47, [(47, 0), (48, 0), (48, 1)], fuente="prensa económica, julio de 2026")
an("otros_abren", 49, [(49, 0), (49, "llenan"), (49, "con marcas"), (49, "y con su marca")])
an("merc_abre", 50, [(50, 0), (50, 1), (50, "quién le trae"), (50, "quién le fabrica"), (50, "y a su precio")], fotos=["g_pan2", "g_pescado", "g_yogur"])
an("red_pt", 51, [(51, 0), (51, "y les compra"), (51, 1), (51, "uno en"), (51, "y otro"), (52, 0)], fuente="ECO (eco.sapo.pt), 10-3-2026")
cita(53, [(53, 0), (53, "«Estamos")], ["Estamos en Portugal, pero *no conocemos a fondo el país*. No somos portugueses."], "10 de marzo de 2026",
     previo="Después de siete años", pregunta="Y aun así, dice esto:", fuente="OKDiario, 11-3-2026")
an("segunda", 54, [(54, 0), (54, "y es una"), (55, 0), (55, "«No vamos"), (55, "Abriremos")], fuente="Valencia Plaza, 12-3-2019")
an("letrero", 56, [(56, 0), (56, 1), (56, "cambiarle"), (56, 2), (56, "su plantilla"), (56, "sus contratos"), (56, "sus vicios"), (57, 0)])
an("objetivo", 58, [(58, 0), (58, "entre ciento"), (58, "va con retraso"), (58, 1), (59, 0), (60, 0)], fuente="Valencia Plaza (2019) · ECO y Xataka (2026)")

# =============================================================== 4
E("capitulo", 61, {"num": "4", "titulo": "Los que salieron *y volvieron*", "sub": "Roig no es el primero que mira un mapa y hace cuentas"},
  pasos=[(61, 0), (61, 0.1)], cap="4")
an("vuelven", (61, 1), [(61, 1), (61, 2)])
W = "Supermarket News, Irish Times y NBC, julio de 2006"
an("walmart_entra", 62, [(62, 0), (62, "convencida"), (62, "ya era"), (62, "y de")], fuente=W)
an("walmart_sale", 63, [(63, 0), (63, 1), (63, "y asumió"), (63, "cerca de")], fuente=W)
an("tesco", 64, [(64, 0), (64, 1), (64, "sin haber"), (64, "la vendió"), (65, 0)], fuente="Fortune · Merca2.0")
an("dia", 66, [(66, 0), (66, 1), (66, 2), (66, 3), (67, 0)], fuente="Alimarket · ESM Magazine")
an("centimos", 68, [(68, 0), (68, 1)], fuente=RES + " · cálculo propio")
an("grande", 69, [(69, 0), (69, "compras"), (69, "llenas"), (69, "repartes")])
an("balanza", 70, [(70, 0), (70, "no vale")])
an("walmart85", 71, [(71, 0), (71, 1), (71, "con ochenta"), (71, "frente a")], fuente="IGD, citado por The Grocer (2006)")
cita(72, [(72, 0), (72, "lo que tienes"), (72, 1)],
     ["*Lo que tienes, hay que gestionarlo muy bien.*", "Y cuando abarcas más de lo que puedes, después los resultados no son buenos."],
     "10 de marzo de 2026", previo="Roig lo resume a su manera", fuente="OKDiario, 11-3-2026")

# =============================================================== 5
E("capitulo", 73, {"num": "5", "titulo": "*No lo necesita*", "sub": "Si salir es tan caro, ¿por qué lo hacen las demás?"},
  pasos=[(73, 0), (73, 1)], cap="5")
an("bolsa", 74, [(74, 0), (74, 1), (74, "cada trimestre"), (74, 2), (74, "el único")], clips=[C("f_bolsa_dentro")],
   fuente="fotos: Wikimedia Commons")
an("dos_motivos", 75, [(75, 0), (75, 1)], clips=[C("modern_store_glass")])
an("familiar", 76, [(76, 0), (76, 1), (76, "Juan Roch"), (76, "la mayoría"), (77, 0), (77, 1), (77, "puede")], fotos=["c_roig"],
   clips=[C("headquarters_office")], fuente="nota de Mercadona, 23-6-2016 (el 80 % del capital) · foto: Junta de Andalucía, CC BY-SA 2.0")
an("sin_abrir", 78, [(78, 0), (78, 1), (78, 2)])
N = "nota de Mercadona (2016) · resultados anuales (2026)"
an("diez_anios", 79, [(79, 0), (79, "y vendía"), (80, 0), (80, 1), (81, 0), (82, 0)], fuente=N)
an("por_tienda_es", (82, 1), [(82, 1), (82, "a mover"), (83, 0)], fuente=N)
an("como", 84, [(84, 0), (84, 1), (84, "abriendo"), (84, 2), (84, "y cerró"), (84, 3), (84, "comida"), (84, "aparcamiento")],
   fuente="Merca2, 11-3-2026")
an("tienda9", 85, [(85, 0), (85, 1), (85, 2), (85, "tres mil"), (85, "de aquí")], clips=[C("modern_store_glass")],
   fuente="Merca2 y Forbes, 11-3-2026")
an("eleccion", 86, [(86, 0), (87, 0), (87, "o gastárselos"), (87, "Roch elige")], fotos=["c_roig"], clips=[C("headquarters_office")],
   fuente="foto: Junta de Andalucía, CC BY-SA 2.0")

# =============================================================== CIERRE
an("no_miedo", 88, [(88, 0), (88, 1)], cap="")
an("recap1", 89, [(89, 0), (89, 1), (89, "ocho años"), (89, "y un margen")], fuente=RES)
an("recap2", 90, [(90, 0), (90, 1), (91, 0), (91, "y que en cada")], clips=[C("truck_highway_bridge")])
an("recap3", 92, [(92, 0), (92, "Sin bolsa"), (92, "sin prisa"), (92, "y con un mercado")], fotos=["c_roig"], clips=[C("modern_store_glass")],
   fuente="foto: Junta de Andalucía, CC BY-SA 2.0")
cita(93, [(93, 0), (93, "llegará"), (93, 2)], ["*Llegará.*"], "marzo de 2023", previo="Hace tres años", pregunta="¿Habrá tercer país?",
     nota="Pero antes, Portugal tiene que ganar lo mismo que España.", fuente="The Objective, 15-3-2023")
an("no_pasado", 94, [(94, 0), (94, "no ha pasado")], fuente=RES + " · cálculo propio")
an("final", 95, [(95, 0), (96, 0)], clips=[C("facade_hill")])

# Metraje real desenfocado detras de las escenas que no llevan mapa ni fondo propio:
# el fondo se mueve y es del tema, en vez de un oscuro plano.
FONDOS = {
    "plan_inicial": "construction_site_cranes", "tres_anios": "concrete_frame", "pruebas": "supermarket_produce",
    "ganado": "calculator_papers", "margen": "woman_paying_checkout", "por_tienda": "supermarket_parking_lot",
    "hogares": "aerial_town_street", "cuota": "supermarket_aisle_shelves", "cadena": "food_factory",
    "marcas": "supermarket_aisle_shelves", "encargo": "bottling_line", "otros_abren": "empty_shopping_arcade",
    "merc_abre": "fresh_fish_hake", "segunda": "store_building_street_corner", "letrero": "greengrocer_shop",
    "objetivo": "aerial_town_avenue", "vuelven": "container_port_reach", "walmart_sale": "traffic_sunset",
    "tesco": "aerial_roundabout", "centimos": "card_terminal", "grande": "warehouse_racks", "balanza": "aerial_highway",
    "walmart85": "trucks_highway_aerial", "diez_anios": "supermarket_checkout_lanes", "por_tienda_es": "store_facade_hill",
    "como": "store_facade_empty_parking", "recap1": "hands_laptop", "no_pasado": "woman_card_payment",
}
for _e in S:
    _c = _e["d"].get("comp")
    if _e["tipo"] == "anim" and _c in FONDOS and "fondo_clip" not in _e:
        _e["fondo_clip"] = [C(FONDOS[_c])]

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(AQUI, "..", "..", "MERCADONA_FUERA"))
    loc = os.path.join(AQUI, "mercadona_fuera.locucion.txt")
    if not os.path.exists(loc):
        loc = os.path.join(base, "locucion.txt")
    voz = os.path.join(AQUI, "mercadona_fuera.voz.json")
    if not os.path.exists(voz):
        voz = os.path.join(base, "voz.json")
    construye(Tiempos(loc, voz), S, MARCA, os.path.join(AQUI, "mercadona_fuera.spec.json"), MEDIA, piel="anim")
