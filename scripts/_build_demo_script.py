"""Genera el guion de demostración del McDonald's en formato del pipeline.

    python scripts/_build_demo_script.py

Escribe config/manual/cuanto-cuesta-comprar-y-mantener-un-mcdonald-s.json
Sirve como ejemplo de guion manual y como prueba end-to-end sin gastar LLM.

Cifras: estimaciones para España a partir de datos públicos de franquicia
(canon, royalty, alquiler, ventas medias por restaurante). El guion las presenta
como estimaciones donde lo son.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import CONFIG_DIR  # noqa: E402
from pipeline.util import log  # noqa: E402  (fuerza stdout en utf-8)

SLUG = "cuanto-cuesta-comprar-y-mantener-un-mcdonald-s"
TITLE = "¿Cuánto cuesta comprar y mantener un McDonald's?"

# (narración, búsqueda de clip en inglés, rótulo en pantalla)
HOOK_LINES = [
    ("Un McDonald's cuesta 1,2 millones.", "1.200.000 €"),
    ("Y ese es el gasto pequeño.", ""),
    ("Le pagas alquiler a McDonald's.", ""),
    ("Sube cuanto más vendes.", ""),
    ("Firmas veinte años.", "20 AÑOS"),
    ("Y de cada menú, te quedan 70 céntimos.", "0,70 €"),
]

HOOK_VISUALS = [
    "mcdonalds restaurant exterior night", "cash counting machine close up",
    "fast food kitchen busy", "hands signing contract pen",
    "burger being assembled close up", "city street traffic timelapse",
    "coins falling slow motion", "drive thru window car",
    "restaurant crew working uniform", "french fries fryer basket",
    "empty restaurant chairs morning", "calculator and invoices desk",
    "delivery truck unloading boxes", "soda cup filling machine",
    "commercial kitchen stainless steel", "shopping mall food court crowd",
    "keys handed over close up", "bank building facade",
    "worker mopping restaurant floor", "digital menu board screens",
    "burger wrapped paper tray", "night city aerial neon",
    "person counting euro bills", "restaurant opening door sign",
]

BLOCKS = [
    {
        "chapter_title": "El billete de entrada",
        "scenes": [
            ("Antes de vender una sola hamburguesa, ya has firmado un cheque enorme.", "hands signing contract pen", ""),
            ("El canon de entrada son unos cuarenta y cinco mil euros.", "cash stack euro bills", "45.000 €"),
            ("Eso solo te da derecho a usar el nombre y el manual.", "mcdonalds logo sign", ""),
            ("Ni local, ni cocina, ni una triste patata.", "empty commercial space renovation", ""),
            ("La inversión completa ronda el millón doscientos mil euros.", "construction workers building interior", "1,2 M€"),
            ("Ahí entra la cocina industrial, el mobiliario y la obra.", "commercial kitchen stainless steel", ""),
            ("Solo las freidoras y la plancha se van a ochenta mil.", "deep fryer commercial kitchen", "80.000 €"),
            ("El sistema de cajas y pantallas, otros sesenta mil.", "digital menu board screens", "60.000 €"),
            ("Y el McAuto, si lo hay, suma doscientos mil más.", "drive thru window car", "200.000 €"),
            ("Pero aquí viene la parte que frena a casi todo el mundo.", "person thinking worried desk", ""),
            ("McDonald's no acepta que financies el cien por cien.", "bank building facade", ""),
            ("Exige que al menos el cuarenta por ciento sea dinero tuyo.", "counting money hands table", "40%"),
            ("Dinero limpio, no prestado, no hipotecado.", "empty wallet close up", ""),
            ("Son casi quinientos mil euros en efectivo sobre la mesa.", "cash briefcase open", "500.000 €"),
            ("Ese filtro no es casual: quieren socios que no puedan rendirse.", "handshake business meeting", ""),
            ("Y cuando por fin firmas, descubres lo que has firmado de verdad.", "contract paperwork stack desk", ""),
        ],
    },
    {
        "chapter_title": "El local nunca es tuyo",
        "scenes": [
            ("Aquí está el secreto peor entendido de toda la empresa.", "mcdonalds restaurant exterior day", ""),
            ("McDonald's no gana dinero vendiendo hamburguesas.", "burger being assembled close up", ""),
            ("Gana dinero siendo el casero de quien las vende.", "keys handed over close up", ""),
            ("La compañía compra o alquila el suelo y el edificio.", "aerial view commercial real estate", ""),
            ("Después te lo subarrienda a ti.", "for lease sign building", ""),
            ("Y no te cobra un alquiler fijo como un casero normal.", "rental agreement signing", ""),
            ("Te cobra un porcentaje de todo lo que factures.", "cash register receipt printing", ""),
            ("Entre el diez y el doce por ciento de las ventas.", "percentage graph screen", "10-12%"),
            ("Traducido: cuanto mejor te va, más caro te sale el local.", "busy restaurant customers queue", ""),
            ("Con dos millones cuatrocientos mil euros de ventas al año...", "crowded fast food restaurant", "2,4 M€"),
            ("...el alquiler se lleva unos doscientos setenta mil euros.", "euro bills falling slow motion", "270.000 €"),
            ("Veintidós mil euros cada mes, solo por estar ahí.", "calendar pages flipping", "22.000 €/mes"),
            ("Y si reformas el local y vendes más, pagas más.", "restaurant renovation workers", ""),
            ("Es un alquiler que te castiga por trabajar bien.", "tired worker restaurant counter", ""),
            ("Por eso hay quien dice que McDonald's es una inmobiliaria...", "real estate buildings aerial", ""),
            ("...que además, casualmente, vende hamburguesas.", "burger and fries tray", ""),
            ("Y todavía no hemos hablado de la marca.", "mcdonalds golden arches sign", ""),
        ],
    },
    {
        "chapter_title": "Alquilar la marca",
        "scenes": [
            ("Usar los arcos dorados también se paga aparte.", "mcdonalds golden arches sign", ""),
            ("El canon de servicio es un cinco por ciento de las ventas.", "percentage symbol graphic", "5%"),
            ("Sobre dos millones cuatrocientos mil, son ciento veinte mil euros.", "money counting machine", "120.000 €"),
            ("Ese dinero no compra nada físico.", "empty box open", ""),
            ("Compra el derecho a seguir llamándote McDonald's un año más.", "restaurant sign at night", ""),
            ("Y encima está la publicidad, que también sale de tu bolsillo.", "television commercial screen", ""),
            ("Otro cuatro por ciento largo va al fondo de marketing.", "advertising billboard city", "4%"),
            ("Casi cien mil euros al año en anuncios que no eliges tú.", "billboard advertisement street", "100.000 €"),
            ("Los decide la central, en Madrid o en Chicago.", "corporate office building glass", ""),
            ("Suma royalty y publicidad: doscientos veinte mil euros.", "calculator numbers close up", "220.000 €"),
            ("Ahora júntalo con el alquiler del capítulo anterior.", "invoices paperwork desk", ""),
            ("Casi medio millón de euros al año...", "stack of euro banknotes", "490.000 €"),
            ("...antes de comprar un solo gramo de carne.", "raw beef patties kitchen", ""),
            ("Y esa carne, claro, tampoco la eliges tú.", "food delivery truck unloading", ""),
            ("Pero el gasto más grande todavía no ha aparecido.", "restaurant crew working uniform", ""),
        ],
    },
    {
        "chapter_title": "Sesenta nóminas",
        "scenes": [
            ("Un McDonald's medio necesita entre sesenta y setenta personas.", "restaurant staff team working", "60-70"),
            ("No trabajan todos a la vez, pero cobran todos.", "employees schedule board", ""),
            ("Turnos partidos, fines de semana, madrugadas y festivos.", "night shift worker restaurant", ""),
            ("La nómina se lleva cerca del veintisiete por ciento de las ventas.", "payroll documents calculator", "27%"),
            ("Son unos seiscientos cincuenta mil euros al año.", "euro bills fanned out", "650.000 €"),
            ("Cincuenta y cuatro mil euros cada mes en sueldos.", "person working cash register", "54.000 €/mes"),
            ("Y ese número no lo controlas casi nada.", "worried manager office desk", ""),
            ("El convenio marca los salarios y la seguridad social.", "legal documents signing", ""),
            ("Si sube el salario mínimo, tú lo absorbes.", "graph rising arrow screen", ""),
            ("El precio del menú, en cambio, lo decide la central.", "menu board prices restaurant", ""),
            ("Ahí está la trampa del modelo entero.", "chess pieces board strategy", ""),
            ("Los costes son tuyos. Los precios son suyos.", "hands tied rope symbolic", ""),
            ("Y la rotación de personal ronda el setenta por ciento anual.", "revolving door people", "70%"),
            ("Formas gente todo el año para que se vaya en seis meses.", "training new employee kitchen", ""),
            ("Cada persona que entra y sale cuesta dinero.", "empty uniform hanging locker", ""),
            ("Pero aún queda la factura que nadie enseña.", "electricity meter close up", ""),
        ],
    },
    {
        "chapter_title": "La factura invisible",
        "scenes": [
            ("Un McDonald's abre dieciocho horas al día, todos los días.", "restaurant open 24 hours sign", "18 h/día"),
            ("Las freidoras no se apagan. Las cámaras frigoríficas tampoco.", "industrial refrigerator kitchen", ""),
            ("La factura de luz ronda los sesenta mil euros al año.", "electricity meter spinning", "60.000 €"),
            ("Cinco mil euros al mes solo en electricidad.", "power lines sunset", "5.000 €/mes"),
            ("El agua, la limpieza y los residuos suman veinte mil más.", "cleaning restaurant floor mop", "20.000 €"),
            ("Y luego está la comida, que es el gasto mayor de todos.", "food ingredients kitchen prep", ""),
            ("Alrededor del treinta por ciento de cada venta.", "burger ingredients close up", "30%"),
            ("Setecientos veinte mil euros al año en producto.", "delivery boxes warehouse", "720.000 €"),
            ("Con los proveedores impuestos por la central.", "supply truck logistics", ""),
            ("No puedes buscar carne más barata aunque la encuentres.", "butcher meat counter", ""),
            ("Y lo que no se vende, se tira.", "food waste bin restaurant", ""),
            ("Las mermas se comen otro dos por ciento largo.", "trash bags restaurant kitchen", "2%"),
            ("Cincuenta mil euros al año a la basura, literalmente.", "garbage truck collecting", "50.000 €"),
            ("Todo esto es constante, mes tras mes, sin descanso.", "clock time lapse wall", ""),
            ("Pero cada siete años llega un golpe distinto.", "construction site scaffolding", ""),
        ],
    },
    {
        "chapter_title": "La reforma obligatoria",
        "scenes": [
            ("El contrato incluye una cláusula que casi nadie lee bien.", "reading contract magnifying glass", ""),
            ("Estás obligado a reformar el restaurante cada cierto tiempo.", "restaurant interior renovation", ""),
            ("Cuando la marca cambia de imagen, tú pagas el cambio.", "interior design blueprint", ""),
            ("No es pintar una pared. Es rehacer el local entero.", "demolition interior construction", ""),
            ("Mobiliario nuevo, cocina nueva, pantallas nuevas.", "modern restaurant interior new", ""),
            ("Entre trescientos mil y quinientos mil euros cada vez.", "money and construction plans", "300-500 mil €"),
            ("Y mientras dura la obra, el restaurante cierra.", "closed sign shop window", ""),
            ("Semanas sin facturar, pero pagando nóminas y alquiler.", "empty restaurant chairs", ""),
            ("Si te niegas, incumples el contrato.", "contract being torn", ""),
            ("Y si incumples, puedes perder la licencia entera.", "closed restaurant boarded up", ""),
            ("Veinte años dan para dos o tres reformas de estas.", "calendar years passing", "x2 o x3"),
            ("Casi un millón de euros extra a lo largo del contrato.", "euro banknotes stack tall", "1 M€"),
            ("Nadie te lo cuenta el día que firmas.", "signing contract close up hands", ""),
            ("Entonces, con todo esto encima, ¿se gana dinero o no?", "person calculating finances", ""),
        ],
    },
    {
        "chapter_title": "Lo que de verdad te llevas",
        "scenes": [
            ("Vamos a montar la cuenta de un año completo.", "spreadsheet numbers screen", ""),
            ("Ventas: dos millones cuatrocientos mil euros.", "cash register busy restaurant", "2,4 M€"),
            ("Producto y mermas: setecientos setenta mil.", "food supplies boxes kitchen", "-770.000 €"),
            ("Personal: seiscientos cincuenta mil.", "restaurant employees working", "-650.000 €"),
            ("Alquiler a McDonald's: doscientos setenta mil.", "building keys and contract", "-270.000 €"),
            ("Royalty y publicidad: doscientos veinte mil.", "advertising campaign screens", "-220.000 €"),
            ("Suministros, limpieza y mantenimiento: ciento veinte mil.", "maintenance worker repairing", "-120.000 €"),
            ("Seguros, gestoría, licencias e imprevistos: sesenta mil.", "insurance documents desk", "-60.000 €"),
            ("Total de gastos: dos millones noventa mil euros.", "calculator total display", "-2,09 M€"),
            ("Te quedan trescientos diez mil euros de beneficio operativo.", "profit graph rising", "310.000 €"),
            ("Suena bien, hasta que restas la financiación.", "bank loan documents", ""),
            ("El préstamo de la inversión se lleva ciento veinte mil al año.", "mortgage payment calculator", "-120.000 €"),
            ("Y luego llega Hacienda a por su parte.", "tax forms and pen", ""),
            ("Al final del año, limpio, te quedan unos ciento cincuenta mil.", "person counting money desk", "150.000 €"),
            ("Sobre dos millones cuatrocientos mil facturados.", "busy restaurant wide shot", ""),
            ("Un seis por ciento. Seis céntimos de cada euro.", "single euro coin close up", "6%"),
            ("De cada menú de diez euros, setenta céntimos son tuyos.", "burger meal tray table", "0,70 €"),
        ],
    },
    {
        "chapter_title": "La cuenta final",
        "scenes": [
            ("Recapitulemos lo que significa comprar un McDonald's.", "mcdonalds restaurant exterior night", ""),
            ("Pones un millón doscientos mil euros para empezar.", "cash briefcase money", "1,2 M€"),
            ("De los cuales medio millón tiene que ser tuyo de verdad.", "person counting euro bills", "500.000 €"),
            ("Mueves dos millones cuatrocientos mil euros al año.", "busy restaurant customers", "2,4 M€"),
            ("Gestionas a sesenta y cinco personas.", "restaurant team meeting", "65"),
            ("Trabajas dentro de un manual que no has escrito tú.", "instruction manual pages", ""),
            ("No eliges proveedores, ni precios, ni publicidad.", "corporate meeting boardroom", ""),
            ("Y te llevas ciento cincuenta mil euros al año.", "money envelope cash", "150.000 €"),
            ("Recuperar la inversión te lleva unos ocho años.", "calendar planning long term", "8 AÑOS"),
            ("De un contrato que dura veinte.", "hourglass sand time", "20 AÑOS"),
            ("Los otros doce sí son rentables de verdad.", "successful business owner smiling", ""),
            ("Por eso casi nadie vende su McDonald's una vez lo tiene.", "restaurant open sign glowing", ""),
            ("Es un negocio lento, seguro y agotador.", "night shift restaurant closing", ""),
            ("Es una nómina muy buena, con un millón de euros de aval.", "bank vault door", ""),
            ("Ganas lo que gana un directivo, pero el riesgo es tuyo.", "executive office window city", ""),
            ("Ese es el problema millonario de los arcos dorados.", "golden arches sign sunset", ""),
            ("Si te ha servido, suscríbete. Cada semana desmontamos otro.", "mcdonalds restaurant exterior night", ""),
        ],
    },
]


# Escenas adicionales que se insertan ANTES del cierre de cada capítulo.
# Se mantienen aparte para que se vea de un vistazo dónde se ha profundizado.
EXTRA_SCENES: dict[str, list[tuple[str, str, str]]] = {
    "El billete de entrada": [
        ("Y el dinero ni siquiera es el filtro más duro del proceso.", "job interview office serious", ""),
        ("Antes de aceptarte, te hacen trabajar en un restaurante.", "restaurant crew training kitchen", ""),
        ("Nueve meses de formación, a jornada completa, sin cobrar nada.", "employee training clipboard", "9 MESES"),
        ("Fregando suelos, montando pedidos, cerrando caja de madrugada.", "worker mopping restaurant floor", ""),
        ("Si no pasas esos nueve meses, te quedas fuera.", "closed door office rejection", ""),
        ("Además exigen dedicación exclusiva al restaurante.", "busy manager restaurant floor", ""),
        ("Nada de tener el negocio y dirigirlo desde casa.", "empty home office chair", ""),
        ("Muchos venden sus otras empresas para poder entrar.", "for sale sign business", ""),
        ("Buscan operadores dentro del local, no inversores de despacho.", "manager talking to staff", ""),
    ],
    "El local nunca es tuyo": [
        ("Y ese contrato te ata al edificio, no a la marca.", "building blueprint architecture", ""),
        ("No puedes mudarte aunque la calle se muera.", "empty street closed shops", ""),
        ("No puedes subarrendar ni ceder el local a otro.", "for lease sign window", ""),
        ("Si el barrio cambia y pierdes clientes, sigues pagando igual.", "abandoned commercial street", ""),
        ("La compañía es uno de los mayores propietarios de suelo del mundo.", "aerial city real estate", ""),
        ("Miles de millones en terrenos comprados hace décadas.", "land plot aerial view", ""),
        ("Terrenos que se revalorizan solos, año tras año.", "property value graph rising", ""),
        ("Esa revalorización es de ellos. Tú solo la pagas.", "landlord keys building", ""),
    ],
    "Alquilar la marca": [
        ("¿Y qué compras exactamente con ese cinco por ciento?", "question mark neon sign", ""),
        ("Compras una cadena de suministro que funciona sola.", "warehouse logistics conveyor", ""),
        ("Compras un manual con cada gesto de la cocina cronometrado.", "kitchen timer stopwatch", ""),
        ("Compras que la gente entre sin preguntarse si se comerá bien.", "customers entering restaurant", ""),
        ("Eso vale dinero. La discusión es cuánto.", "balance scale money", ""),
        ("Y desde hace unos años hay un gasto nuevo encima.", "smartphone food delivery app", ""),
        ("Las plataformas de reparto se llevan del veinticinco al treinta por ciento.", "delivery rider scooter city", "25-30%"),
        ("De cada pedido a domicilio, casi un tercio se va fuera.", "delivery bag food handover", ""),
        ("Vendes más volumen y ganas menos por pedido.", "delivery packages stacked", ""),
    ],
    "Sesenta nóminas": [
        ("Por encima de todos ellos hay tres o cuatro encargados.", "restaurant manager uniform", ""),
        ("Esos sí son fijos, y cobran el doble que el resto.", "manager reviewing documents", ""),
        ("La seguridad social añade un treinta por ciento sobre cada sueldo.", "payroll spreadsheet screen", "+30%"),
        ("Eso ya está dentro de los seiscientos cincuenta mil.", "calculator and payslips", ""),
        ("Pero no está el absentismo, ni las bajas, ni las sustituciones.", "empty workstation restaurant", ""),
        ("Un sábado con dos bajas te arruina el mejor día de la semana.", "busy queue restaurant counter", ""),
        ("Y formar a alguien cuesta unas cuarenta horas pagadas.", "training session employees", "40 h"),
        ("Con setenta por ciento de rotación, formas casi una plantilla entera al año.", "revolving door people blur", ""),
        ("Es un coste que no aparece en ninguna línea del balance.", "financial report pages", ""),
    ],
    "La factura invisible": [
        ("Y hay gastos que ni te imaginas hasta que los pagas.", "surprised person looking bill", ""),
        ("El aceite de las freidoras se cambia cada pocos días.", "cooking oil pouring fryer", ""),
        ("Solo eso son más de veinte mil euros al año.", "oil containers kitchen", "20.000 €"),
        ("Los envases, las bolsas y los vasos: otros ochenta mil.", "paper cups packaging stack", "80.000 €"),
        ("El hielo, los uniformes, los productos de limpieza.", "ice machine commercial", ""),
        ("Los contratos de mantenimiento de la maquinaria.", "technician repairing equipment", ""),
        ("Cuando se rompe una freidora un viernes, pagas la urgencia.", "repair technician tools kitchen", ""),
        ("Ninguna de estas partidas es enorme por separado.", "small coins pile", ""),
        ("Juntas se comen el beneficio de un mes entero.", "monthly calendar red mark", ""),
    ],
    "La reforma obligatoria": [
        ("Y al llegar al año veinte, llega la última sorpresa.", "hourglass running out", ""),
        ("El contrato no se renueva solo.", "expired document stamp", ""),
        ("Hay que negociarlo otra vez, y volver a pagar por entrar.", "negotiation meeting table", ""),
        ("Con el local puesto a punto, según sus condiciones.", "renovated restaurant interior", ""),
        ("La maquinaria industrial dura entre ocho y diez años.", "commercial kitchen equipment", "8-10 AÑOS"),
        ("Así que en veinte años cambias la cocina dos veces enteras.", "kitchen equipment installation", ""),
        ("Nada de esto es letra pequeña oculta: está escrito.", "reading contract closeup", ""),
        ("Simplemente, nadie lo suma antes de firmar.", "person signing pen paper", ""),
    ],
    "Lo que de verdad te llevas": [
        ("Y ojo, porque esa cuenta es la de un restaurante que va bien.", "busy restaurant success", ""),
        ("Uno con dos millones cuatrocientos mil de ventas.", "cash register busy day", ""),
        ("Hay locales que facturan un millón y medio.", "quiet restaurant few customers", "1,5 M€"),
        ("Con esa facturación, los costes fijos se te comen vivo.", "declining graph red", ""),
        ("El alquiler baja, sí, pero la nómina mínima no.", "employee schedule board", ""),
        ("Necesitas la misma gente para abrir dieciocho horas.", "restaurant opening morning", ""),
        ("Por debajo de dos millones, el margen se acerca a cero.", "zero on calculator", "0%"),
        ("Por eso la ubicación no es importante: es todo.", "busy city corner location", ""),
        ("Y la ubicación, recordemos, la elige la central.", "corporate decision meeting", ""),
    ],
    "La cuenta final": [
        ("Compáralo con la alternativa más aburrida del mundo.", "stock market chart screen", ""),
        ("Coges esos quinientos mil euros y no haces nada.", "money in bank vault", "500.000 €"),
        ("Los metes en un fondo indexado y te vas a dormir.", "person sleeping peacefully", ""),
        ("Sacarías unos treinta y cinco mil euros al año.", "investment growth chart", "35.000 €"),
        ("Sin empleados, sin madrugones, sin freidoras rotas.", "relaxed person beach laptop", ""),
        ("El McDonald's te da cuatro veces más...", "restaurant busy successful", "x4"),
        ("...a cambio de sesenta horas semanales durante veinte años.", "tired worker late night", ""),
        ("Y de algo que no aparece en ninguna cuenta anual.", "empty family dinner table", ""),
        ("Al final del contrato, además, el negocio vale dinero.", "handshake business sale", ""),
        ("Un McDonald's consolidado se traspasa por más de un millón.", "restaurant sold sign", "1 M€"),
        ("Ese es el premio real: no el sueldo, el patrimonio.", "house and keys investment", ""),
    ],
}


def main() -> int:
    hook = {
        "lines": [{"narration": text, "on_screen": label} for text, label in HOOK_LINES],
        "visuals": HOOK_VISUALS,
    }
    blocks = []
    for index, spec in enumerate(BLOCKS, start=1):
        scenes = list(spec["scenes"])
        extra = EXTRA_SCENES.get(spec["chapter_title"], [])
        if extra:
            # Van justo antes del cierre: la última escena es el bucle abierto
            # que engancha con el capítulo siguiente y tiene que seguir siendo
            # la última.
            scenes = scenes[:-1] + extra + scenes[-1:]
        blocks.append({
            "id": index,
            "chapter_title": spec["chapter_title"],
            "scenes": [
                {"narration": narration, "broll_query": query, "on_screen": label}
                for narration, query, label in scenes
            ],
        })

    script = {
        "outline": {
            "working_title": TITLE,
            "total_figure": "1,2 millones para entrar y 2,2 millones al año para mantenerlo",
            "comparison": "de cada menú de 10 euros, solo 70 céntimos son tuyos",
            # Búsquedas del SUJETO. Con estas se cosecha el fondo de clips de
            # marca que se reparte por todo el vídeo.
            "broll_anchors": [
                "mcdonalds", "mcdonalds restaurant", "mcdonalds drive thru",
                "mcdonalds sign", "fast food restaurant interior",
                "burger fast food meal", "fast food crew working",
                "drive thru window",
            ],
            # Lo que tiene que VERSE en el clip para entrar en el fondo. El
            # anclaje acierta con las palabras, esto acierta con la imagen.
            "broll_keywords": [
                "mcdonald", "burger", "hamburger", "cheeseburger", "fries",
                "french fries", "fast food", "fastfood", "drive thru",
                "drive through", "food court", "takeaway", "take away",
                "milkshake", "soda cup", "fried chicken", "nuggets",
            ],
            # Términos que solo salen si SE VE la marca. Estos clips se reservan
            # para el hook, las cifras y las aperturas de capítulo.
            "broll_keywords_primary": [
                "mcdonald", "golden arches", "big mac", "mcauto",
            ],
            "blocks": [
                {"id": b["id"], "chapter_title": b["chapter_title"],
                 "thesis": "", "key_figures": [], "open_loop": "",
                 "target_words": sum(len(s["narration"].split()) for s in b["scenes"])}
                for b in blocks
            ],
        },
        "hook": hook,
        "blocks": blocks,
    }

    target = CONFIG_DIR / "manual" / f"{SLUG}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")

    words = sum(len(line["narration"].split()) for line in hook["lines"])
    words += sum(len(s["narration"].split()) for b in blocks for s in b["scenes"])
    scenes = len(hook["lines"]) + sum(len(b["scenes"]) for b in blocks)
    log.info(str(target))
    log.info(f"{len(blocks)} capítulos · {scenes} escenas · {words} palabras")
    log.info(f"~ {words / 165:.1f} minutos de narración a 165 palabras por minuto")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
