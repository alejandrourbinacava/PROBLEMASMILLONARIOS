"""Guion tecnico de «Por que Chupa Chups vende MAS fuera de Espana que dentro» — piel ANIM.

    python chupachups.py            -> vox/chupachups.spec.json

Los numeros de fragmento son los de la locucion (`locucion.txt`, 84 fragmentos).
Las escenas estan en remotion/src/vox/video/c_chupa1.tsx, c_chupa2.tsx y c_chupa3.tsx
(registro CHUPA, que Animado elige porque el spec lleva `tema: chupachups`).

Cada plano: foto real o metraje desenfocado al fondo (`clips`), elementos de foto de
estudio (vox/media/chupachups/g_*.webp) y texto que entra con la voz. Los pasos atan
cada movimiento a la palabra que lo dice: (fragmento, frase), (fragmento, fraccion)
o (fragmento, "trozo literal").
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from tecnico import Media, Tiempos, construye  # noqa: E402

MARCA = {"nombre": "CHUPA CHUPS", "color": "#E0352B", "claro": "#FF6A5C", "oscuro": "#5A1014", "acento": "#FFD95A"}
MEDIA = Media(["parallax2/proyecto/stock_mercadona", "vox/media/chupachups"], os.path.join(AQUI, "chupachups.media.json"))
IDCH = "International Directory of Company Histories, vol. 38 (2001)"
ARA = "Ara, 20-9-2023"
CE = "Comisión Europea, decisión de 10-5-2007 sobre Chupa Chups"
WH = "Knowledge at Wharton, 12-7-2006"
TEMPS = "El Temps, julio de 2006"
EXPO = "foto de fondo: J Aaron Farr, CC BY 2.0"

S = []


def C(a, paso=None, **k):
    d = {"a": a, "paso": paso}
    d.update(k)
    return d


def E(tipo, de, d, pasos=None, fuente=None, cap=None, clips=None):
    e = {"tipo": tipo, "de": de, "d": d}
    if pasos:
        e["pasos"] = pasos
    if fuente:
        e["fuente"] = fuente
    if cap is not None:
        e["cap"] = cap
    if clips:
        e["fondo_clip"] = [C(c) if isinstance(c, str) else c for c in clips]
    S.append(e)


def an(comp, de, pasos=None, fuente=None, clips=None, cap=None, **d):
    E("anim", de, dict(comp=comp, **d), pasos=pasos, fuente=fuente, clips=clips, cap=cap)


# =============================================================== GANCHO
an("caramelo", 0, [(0, 0), (0, 1)], clips=["f_expositor"], fuente=EXPO)
an("tres", 1, [(1, 0), (1, "Lo dibujó"), (1, "lo llevó"), (1, "y ha viajado")], clips=["f_expositor"],
   fuente=IDCH + " · " + ARA + " · " + EXPO)
an("vuelta", 2, [(2, 0), (2, 1), (2, "solo uno"), (2, 2), (2, "eran nueve")], clips=["f_confiteria"], fuente=IDCH)
an("noventa", 3, [(3, 0), (3, "más del noventa")], clips=["container_port_reach"], fuente=IDCH + " (93 % en 1999)")
an("ya_no", 4, [(4, 0), (4, "hoy ya no")], clips=["f_expositor"], fuente="vendida a Perfetti Van Melle en 2006 · " + EXPO)
an("locura", 5, [(5, 0), (5, "dejar de fabricar"), (5, "para quedarse")], clips=["f_confiteria"], fuente=IDCH)

# =============================================================== 1
E("capitulo", 6, {"num": "1", "titulo": "Un solo *caramelo*", "sub": "Enric Bernat, de una familia de confiteros de Barcelona"},
  pasos=[(6, 0), (6, 0.05)], cap="1")
an("bernat", (6, 1), [(6, 1), (6, "desde los nueve")], clips=["f_confiteria"], fuente="entrevista en El País (1990), recogida por Merca2, 2-6-2024")
an("granja", 7, [(7, 0), (7, "Granja Asturias"), (7, "en Villamayor"), (7, "y que había estado")], fuente=IDCH)
an("uno_solo", 8, [(8, 0), (8, 1), (8, "dejó de fabricar"), (8, "para concentrarse")], clips=["f_confiteria"], fuente=IDCH)
an("ninos", 9, [(9, 0), (9, 1), (9, 2), (9, "y acababan")], clips=["f_confiteria"], fuente=IDCH)
an("palo", 10, [(10, 0), (10, 1), (10, 2), (10, "de plástico")], clips=["f_fabrica"], fuente=IDCH + " · El Temps (2006)")
an("nombre", 11, [(11, 0), (11, 1), (11, 2), (11, "y la empresa")], clips=["f_expositor"], fuente=ARA + " · " + EXPO)
an("peseta", 12, [(12, 0), (12, "menos de"), (12, 1)], clips=["f_confiteria"], fuente=IDCH + " · 1 € = 166,386 pesetas")
an("flota", 13, [(13, 0), (13, 1), (13, 2), (13, "los repartía")], clips=["aerial_town_avenue"], fuente=IDCH + " · " + ARA)
an("bocas", 14, [(14, 0), (14, 1), (14, "encontrando")], clips=["f_fabrica"])
an("techo", 15, [(15, 0), (15, 1), (15, "tiene techo")], fuente="INE, censo de 1960: 30,4 millones de habitantes")

# =============================================================== 2
E("capitulo", 16, {"num": "2", "titulo": "Nada que *traducir*", "sub": "1967 · empieza a salir"},
  pasos=[(16, 0), (16, 0.05)], cap="2")
an("salida", (16, 1), [(16, 1), (16, "y su primera filial"), (17, 0)], fuente=IDCH)
an("socios", 18, [(18, 0), (18, 1), (18, "en Italia"), (18, "y en Estados Unidos")], clips=["f_confiteria"], fuente=IDCH)
an("van_melle", 19, [(19, 0), (19, 1), (19, 2)], fuente=IDCH + " · Confectionery News, 5-7-2006")
an("duro", 20, [(20, 0), (20, "aguanta"), (20, "y cabe")], clips=["f_expositor"], fuente="razonamiento propio · " + EXPO)
an("imagen", 21, [(21, 0), (21, "una imagen")], clips=["aerial_town_street"])
an("dali", 22, [(22, 0), (22, 1), (23, 0), (23, 1)], clips=["f_dali"],
   fuente=IDCH + " · " + ARA + " · foto: Carl Van Vechten (1939), dominio público · flor: ilustración propia, no es el logotipo")
an("arriba", 24, [(24, 0), (24, "poner el logotipo"), (24, "y no en un lado"), (24, "para que se viera")], clips=["f_fabrica"],
   fuente="Artnet News · ilustración propia, no es el logotipo")
an("traducir", 25, [(25, 0), (25, 1)], clips=["f_expositor"], fuente=EXPO)

# =============================================================== 3
E("capitulo", 26, {"num": "3", "titulo": "Nueve de cada *diez*", "sub": "1970 · solo uno de cada diez se vende fuera de España"},
  pasos=[(26, 0), (26, 0.03)], cap="3")
an("paises", (26, 1), [(26, 1), (26, 1), (26, 2), (27, 0), (28, 0), (28, "nueve de cada")], clips=["container_port_reach"], fuente=IDCH)
an("fabricas", 29, [(29, 0), (29, "y en mil"), (29, 1), (29, "otra en"), (29, "y una filial")], clips=["trucks_highway_aerial"], fuente=IDCH)
an("veinte_mil", 30, [(30, 0), (30, 1)], clips=["f_fabrica"], fuente=ARA)
an("jackson", 31, [(31, 0), (31, 1), (31, "patrocinó")], clips=["f_campnou"], fuente=ARA + " · foto de fondo: Daniel (Glasgow), CC BY 2.0")
an("cruyff", 32, [(32, 0), (32, "tuvo que"), (33, 0), (33, "empezó a tener")], clips=["f_campnou"],
   fuente=ARA + " · foto de fondo: Daniel (Glasgow), CC BY 2.0")
an("anuncio", 34, [(34, 0), (34, "«El fútbol")], clips=["f_campnou"],
   fuente="campaña de la Generalitat de Catalunya, 1991 · foto de fondo: Daniel (Glasgow), CC BY 2.0")
an("mir", 35, [(35, 0), (35, "viajaron"), (35, 1)], clips=["f_mir"], fuente=IDCH + " · foto: NASA (misión STS-89), dominio público")
an("cumbre", 36, [(36, 0), (37, 0), (37, "tenía dos mil"), (37, "y vendía")], clips=["f_fabrica"],
   fuente=IDCH + " · 73.000 millones de pesetas, a euros")
an("espacio", 38, [(38, 0)], clips=["f_mir"], fuente="foto: NASA (misión STS-89), dominio público")

# =============================================================== 4
E("capitulo", 39, {"num": "4", "titulo": "Ahí empezó *el problema*", "sub": "Demasiado grande"},
  pasos=[(39, 0), (39, 0.05)], cap="4")
an("fabricas5", (40, "Chupa Chups había"), [(40, "Chupa Chups había"), (40, "España"), (40, "Francia"), (40, "Rusia"), (40, "México"), (40, "y China"), (40, 1)],
   clips=["trucks_highway_aerial"], fuente=IDCH)
an("casi_todo", 41, [(41, 0), (42, 0), (42, 1), (42, "un reloj"), (42, "y una piruleta"), (43, 0), (43, "de ropa")], clips=["f_fabrica"],
   fuente=IDCH + " · " + WH)
an("caida", 44, [(44, 0), (44, 1), (44, 2), (45, 0)], clips=["calculator_papers"],
   fuente="Confectionery News, 10-2-2003 (2001) · " + CE + " (2002 y 2004)")
an("encoge", 46, [(46, 0), (46, 1), (46, "a la mitad")], clips=["warehouse_racks"], fuente="Confectionery News, 10-2-2003")
an("perdidas", 47, [(47, 0), (47, 1), (47, "unos ciento"), (48, 0)], clips=["calculator_papers"],
   fuente=CE + " · deuda: Cinco Días, vía Confectionery News, 10-2-2003")
an("recortes", 49, [(49, 0), (49, 1), (49, 2), (50, 0), (50, 1)], clips=["hands_laptop"],
   fuente="Confectionery News, 10-2-2003 · El Temps (2006)")
an("familia", 51, [(51, 0), (51, "y cedió")], clips=["calculator_papers"], fuente=CE + " · Confectionery News, 10-2-2003")
an("hipoteca", 52, [(52, 0), (52, "para conseguir"), (52, "hipotecó")], clips=["hands_laptop"], fuente=CE)
an("batllo", 53, [(53, 0), (53, 1), (53, "que los Bernat"), (53, 2)], clips=["f_paseo"],
   fuente=CE + " · The Art Newspaper, 25-4-2025 · edificio recreado con IA · fondo: DimiTalen, CC0")
an("muere", 54, [(54, 0), (54, "murió")], clips=["f_confiteria"], fuente="27 de diciembre de 2003")
an("hacienda", 55, [(55, 0), (55, "por otros"), (55, "para que Hacienda")], clips=["f_paseo"],
   fuente=CE + " (15,24 M€, febrero de 2004) · edificio recreado con IA")
an("bruselas", 56, [(56, 0), (56, 1), (56, 2)], clips=["government_building"], fuente=CE)

# =============================================================== 5
E("capitulo", 57, {"num": "5", "titulo": "Se *vende*", "sub": "3 de julio de 2006 · la familia vende la empresa entera"},
  pasos=[(57, 0), (57, 0.03)], cap="5")
an("venta", (57, 1), [(57, 1), (57, 1), (57, "un grupo"), (57, "el dueño"), (58, 0), (58, 1)],
   clips=["calculator_papers"], fuente=WH + " (1.434 M€ frente a 264 M€)")
an("precio", 59, [(59, 0), (59, 1)], clips=["euro_50_banknotes"], fuente=WH + " · " + TEMPS)
an("comite", 60, [(60, 0), (60, "y casi"), (60, 1), (61, 0)], clips=["hands_laptop"], fuente=TEMPS + " · traducido del catalán")
an("promesas", 62, [(62, 0), (62, "una oportunidad"), (63, 0), (63, "y levantar")], clips=["f_fabrica"],
   fuente=TEMPS + " · " + WH + " · traducción propia")
an("profesores", 64, [(64, 0), (64, 1), (65, 0), (65, "«El futuro")], clips=["elderly_people_meeting"], fuente=WH + " · traducción propia")
an("medias", 66, [(66, 0), (66, 1)], fuente=ARA)
an("villamayor", 67, [(67, 0), (67, "anunció el cierre"), (67, 1), (68, 0), (68, "y la producción")], clips=["f_pilona"],
   fuente="Just Food y Confectionery News, junio de 2010 · fondo: jacilluch, CC BY-SA 2.0")
an("ere", 69, [(69, 0), (69, "para cincuenta")], clips=["hands_laptop"], fuente="Alimarket, 2013")
an("kiwis", 70, [(70, 0), (70, 1)], clips=["f_pilona"], fuente="elDiario.es, 1-8-2025 · fondo: jacilluch, CC BY-SA 2.0")
an("quesos", 71, [(71, 0), (71, "que va a invertir"), (71, "y a crear"), (72, 0), (72, "se harán quesos")], clips=["f_pilona"],
   fuente="elDiario.es, 1-8-2025 · fondo: jacilluch, CC BY-SA 2.0")
an("hoy", 73, [(73, 0), (73, "que factura"), (73, "con dieciocho"), (73, "y treinta"), (74, 0)], clips=["container_port_reach"],
   fuente="Perfetti Van Melle, «At a glance» (2025)")

# =============================================================== CIERRE
an("pregunta", 75, [(75, 0)], clips=["f_expositor"], cap="", fuente=EXPO)
an("porque", 76, [(76, 0), (76, 1), (77, 0)], clips=["f_fabrica"], fuente="flor: ilustración propia, no es el logotipo")
an("comprado", 78, [(78, 0), (78, 1), (78, 2), (78, "acabó comprado")], clips=["container_port_reach"], fuente="conclusión propia")
an("casa", 79, [(79, 0), (80, 0), (80, "sigue siendo"), (80, 1), (80, "y tres años")], clips=["f_paseo"],
   fuente="Ara, 18-4-2026 · The Art Newspaper, 25-4-2025 · edificio recreado con IA · fondo: DimiTalen, CC0")
an("visitantes", 81, [(81, 0), (81, "el doble"), (81, "e ingresó")], clips=["f_batllo2"],
   fuente="The Art Newspaper, 25-4-2025 · foto: jqmj (Queralt), CC BY-SA 2.0")
an("comparacion", 82, [(82, 0), (82, "factura unos"), (82, 1)], clips=["f_paseo"],
   fuente=ARA + " (2022) · The Art Newspaper, 25-4-2025 (2023) · son años distintos")
an("final", 83, [(83, 0), (83, 1)], clips=["f_paseo"], fuente="edificio recreado con IA · fondo: DimiTalen, CC0")

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(AQUI, "..", "..", "CHUPA_CHUPS"))
    loc = os.path.join(AQUI, "chupachups.locucion.txt")
    if not os.path.exists(loc):
        loc = os.path.join(base, "locucion.txt")
    voz = os.path.join(AQUI, "chupachups.voz.json")
    if not os.path.exists(voz):
        voz = os.path.join(base, "voz.json")
    construye(Tiempos(loc, voz), S, MARCA, os.path.join(AQUI, "chupachups.spec.json"), MEDIA, piel="anim")
