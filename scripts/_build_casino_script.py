"""Genera el guion del casino en formato del pipeline.

    python scripts/_build_casino_script.py

Escribe config/manual/esto-es-lo-que-cuesta-comprar-un-casino.json

Cifras: estimaciones para España a partir de datos públicos del sector del
juego (precio de máquinas, plantillas, fiscalidad autonómica sobre el margen
bruto) y de operaciones conocidas en Las Vegas. El guion las presenta como
estimaciones donde lo son.

El ángulo del vídeo: un casino no apuesta. Vende tiempo. La ventaja de la casa
es ridícula por jugada y demoledora por hora, y todo el negocio consiste en
alargar esa hora.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import CONFIG_DIR  # noqa: E402
from pipeline.util import log  # noqa: E402

SLUG = "esto-es-lo-que-cuesta-comprar-un-casino"
TITLE = "Esto es lo que cuesta comprar un casino"

HOOK_LINES = [
    ("Comprar un casino cuesta 28 millones.", "28 M€"),
    ("Y cuatro millones más que no puedes tocar.", ""),
    ("La ventaja de la casa es del 2,7%.", "2,7%"),
    ("Parece nada. Es todo.", ""),
    ("Porque el casino no apuesta contra ti.", ""),
    ("Te vende tiempo, y el tiempo siempre gana.", ""),
]

HOOK_VISUALS = [
    "casino roulette wheel spinning", "casino chips stack close up",
    "slot machine reels spinning", "casino floor wide shot",
    "playing cards dealt table", "las vegas strip night aerial",
    "security camera ceiling dome", "cash counting machine close up",
    "croupier hands chips table", "casino neon sign night",
    "dice rolling green felt", "people playing slot machines",
    "poker table players night", "casino entrance doors",
    "money counting hands euro", "surveillance monitors room",
    "blackjack table dealer", "casino carpet lights",
    "empty casino morning", "cocktail served casino bar",
]

BLOCKS = [
    {
        "chapter_title": "El billete de entrada",
        "scenes": [
            ("Un casino no se compra como se compra un bar.", "casino entrance doors night", ""),
            ("No compras un local: compras una empresa entera.", "office building glass facade", ""),
            ("Con su licencia, su plantilla y sus deudas dentro.", "contract paperwork stack desk", ""),
            ("Un casino mediano en España ronda los veintiocho millones.", "casino floor wide shot", "28 M€"),
            ("Ahí entra el edificio, la maquinaria y el permiso.", "casino building exterior", ""),
            ("En Las Vegas la escala es otra por completo.", "las vegas strip night aerial", ""),
            ("El Mirage se vendió por mil millones de dólares.", "las vegas hotel casino night", "1.000 M$"),
            ("Y el Cosmopolitan por cinco mil seiscientos millones.", "luxury hotel tower night", "5.600 M$"),
            ("Pero el precio de compra es lo de menos.", "person thinking worried desk", ""),
            ("Porque un casino es un negocio que arranca en negativo.", "declining graph red screen", ""),
            ("Antes de abrir ya has inmovilizado millones que no producen.", "bank vault door closed", ""),
            ("Y hay algo que el dinero por sí solo no compra.", "closed door office", ""),
        ],
    },
    {
        "chapter_title": "La licencia que no se vende",
        "scenes": [
            ("En España las licencias de casino no están a la venta.", "government building facade", ""),
            ("Las concede cada comunidad autónoma y son contadas.", "official documents stamp desk", ""),
            ("En algunas regiones no llegan a cinco en total.", "map spain graphic", ""),
            ("No puedes pedir una y esperar tu turno.", "waiting room empty chairs", ""),
            ("Tienes que comprar la empresa que ya la tiene.", "handshake business meeting", ""),
            ("Y eso dispara el precio muy por encima de los activos.", "rising graph arrow screen", ""),
            ("Estás pagando por un permiso que nadie más puede conseguir.", "key in lock close up", ""),
            ("Además el regulador tiene que aprobarte a ti.", "audit documents magnifying glass", ""),
            ("Revisan tu patrimonio, tu origen del dinero y tus socios.", "financial audit paperwork", ""),
            ("Un solo socio con antecedentes tumba la operación entera.", "rejected stamp document", ""),
            ("El proceso puede llevar más de un año.", "calendar pages flipping", "1 AÑO"),
            ("Y durante ese año pagas abogados sin ingresar nada.", "lawyer office desk documents", ""),
            ("Cuando por fin abres, empieza el gasto de verdad.", "casino doors opening", ""),
        ],
    },
    {
        "chapter_title": "Llenar la sala",
        "scenes": [
            ("Una sala vacía no gana dinero. Hay que llenarla.", "empty casino floor", ""),
            ("Un casino mediano monta unas trescientas máquinas.", "row of slot machines", "300"),
            ("Cada máquina nueva cuesta unos dieciocho mil euros.", "slot machine close up", "18.000 €"),
            ("Solo en máquinas se van cinco millones cuatrocientos mil.", "slot machines row lights", "5,4 M€"),
            ("Las mesas son más baratas de lo que parece.", "roulette table green felt", ""),
            ("Veinticinco mesas a doce mil euros: trescientos mil.", "blackjack table empty", "300.000 €"),
            ("Pero las mesas no se pagan con la mesa.", "croupier hands chips", ""),
            ("Se pagan con los cuatro crupieres que necesita cada una.", "croupier dealing cards", ""),
            ("Y luego están las fichas, que casi nadie cuenta.", "casino chips stack close up", ""),
            ("Un casino guarda más de cien mil fichas.", "chips tray casino", "100.000"),
            ("Cada una lleva un chip de radiofrecuencia dentro.", "rfid chip electronics", ""),
            ("Cuestan entre dos y tres euros la unidad.", "casino chips close up macro", "2-3 €"),
            ("Trescientos mil euros en fichas paradas en un cajón.", "chips organized tray", "300.000 €"),
            ("Y las cambias enteras si alguien las falsifica.", "counterfeit detection uv light", ""),
            ("Con la sala montada llega la partida más rara del balance.", "casino floor busy people", ""),
        ],
    },
    {
        "chapter_title": "El dinero que no es tuyo",
        "scenes": [
            ("Un casino tiene que poder pagar si ganas.", "cash counting hands euro", ""),
            ("Y tiene que poder pagarlo en el momento.", "cashier window casino", ""),
            ("Eso obliga a tener millones en efectivo parados.", "bank vault money stacks", ""),
            ("Se llama fondo de caja y ronda los cuatro millones.", "cash stacks counted", "4 M€"),
            ("Ese dinero no invierte, no renta y no se toca.", "safe deposit box closed", ""),
            ("Está ahí solo por si esta noche alguien revienta la banca.", "roulette wheel spinning", ""),
            ("Y el regulador comprueba que lo tienes de verdad.", "auditor checking documents", ""),
            ("Si no llegas al mínimo, te cierran la sala.", "closed sign door", ""),
            ("Súmale la garantía que exige la comunidad autónoma.", "official seal document", ""),
            ("Otro millón inmovilizado antes de abrir la puerta.", "bank building facade", "1 M€"),
            ("Cinco millones de euros que existen solo para estar quietos.", "money stack still", "5 M€"),
            ("Un banco te diría que eso es capital muerto.", "banker desk meeting", ""),
            ("En un casino es el precio de poder abrir.", "casino entrance lights", ""),
            ("Y todavía no ha entrado nadie a trabajar.", "empty casino morning light", ""),
        ],
    },
    {
        "chapter_title": "Trescientas personas",
        "scenes": [
            ("Un casino mediano emplea a unas trescientas personas.", "casino staff working floor", "300"),
            ("Y a diferencia de un restaurante, no puede cerrar.", "24 hours neon sign", ""),
            ("Muchas salas abren dieciocho horas al día, todo el año.", "casino floor night busy", "18 h/día"),
            ("Cada mesa activa necesita cuatro crupieres al día.", "croupier changing shift", ""),
            ("Turnos rotatorios, porque nadie aguanta ocho horas seguidas.", "dealer concentration table", ""),
            ("Un crupier no puede despistarse ni un segundo.", "hands dealing cards fast", ""),
            ("Un error de pago se lo come la casa.", "chips being paid out", ""),
            ("Por eso rotan cada veinte minutos y se les vigila.", "casino floor supervisor", ""),
            ("A eso súmale seguridad, caja, sala técnica y limpieza.", "security guard casino", ""),
            ("La nómina se lleva unos nueve millones al año.", "payroll documents calculator", "9 M€"),
            ("Es la partida más grande del casino, con diferencia.", "team of employees working", ""),
            ("Y la que no puedes recortar sin cerrar mesas.", "closed table casino", ""),
            ("Menos mesas es menos ingreso: la pescadilla de siempre.", "empty tables casino", ""),
            ("Pero hay un departamento que no verás en ninguna visita.", "security camera dome ceiling", ""),
        ],
    },
    {
        "chapter_title": "El ojo en el techo",
        "scenes": [
            ("Sobre tu cabeza hay más de mil cámaras.", "security cameras ceiling row", "1.000"),
            ("Cubren cada mesa, cada máquina y cada puerta.", "surveillance monitors wall", ""),
            ("No hay un solo metro cuadrado sin grabar.", "casino floor from above", ""),
            ("La sala de control funciona las veinticuatro horas.", "control room operators", "24 h"),
            ("Con gente entrenada para leer manos, no caras.", "hands on casino table", ""),
            ("Montar todo eso cuesta cerca de dos millones.", "server room technology", "2 M€"),
            ("Y mantenerlo, medio millón más cada año.", "technician repairing equipment", "500.000 €"),
            ("Pero la vigilancia no está ahí solo por los tramposos.", "surveillance screen watching", ""),
            ("Está ahí porque un casino mueve efectivo a lo bestia.", "cash bundles counting", ""),
            ("Y eso lo convierte en objetivo de blanqueo de capitales.", "financial documents audit", ""),
            ("La ley obliga a identificar a quien mueva ciertas cantidades.", "id document scanner", ""),
            ("Y a reportar cada operación sospechosa al supervisor.", "compliance report desk", ""),
            ("Eso significa un departamento entero de cumplimiento.", "office team meeting documents", ""),
            ("Otro millón largo al año en gente que no genera ingresos.", "office workers desks", "1 M€"),
            ("Con todo esto encima, ¿de dónde sale el dinero?", "casino floor busy night", ""),
        ],
    },
    {
        "chapter_title": "La ventaja de la casa",
        "scenes": [
            ("Aquí está el corazón del negocio, y es pura aritmética.", "roulette wheel close up", ""),
            ("La ruleta europea tiene treinta y siete números.", "roulette numbers wheel", "37"),
            ("Pero si aciertas, te pagan treinta y seis veces.", "chips placed roulette", "x36"),
            ("Esa diferencia es toda la ventaja de la casa.", "roulette ball spinning", ""),
            ("Dos coma siete por ciento. Nada más.", "percentage graphic screen", "2,7%"),
            ("En el blackjack bien jugado baja al medio por ciento.", "blackjack cards dealt", "0,5%"),
            ("En las máquinas sube hasta el ocho o el diez.", "slot machine spinning reels", "8-10%"),
            ("Y por eso las máquinas dan el setenta por ciento del ingreso.", "row of slot machines busy", "70%"),
            ("No las mesas, que son el escaparate.", "elegant casino table", ""),
            ("Ahora fíjate en lo que significa ese dos coma siete.", "casino chips being pushed", ""),
            ("En una sola jugada casi no existe: puedes ganar tú.", "single roulette spin", ""),
            ("En mil jugadas es una certeza matemática.", "many chips on table", ""),
            ("Por eso el casino no apuesta contra ti.", "croupier watching table", ""),
            ("Apuesta a que te quedes el tiempo suficiente.", "clock casino wall", ""),
            ("Todo lo demás está diseñado para eso.", "casino interior lights maze", ""),
            ("Sin relojes, sin ventanas, sin salidas evidentes.", "casino interior no windows", ""),
            ("La bebida gratis, el aparcamiento gratis, el hotel barato.", "cocktail served casino", ""),
            ("Nada de eso es generosidad: es alargar tu sesión.", "person playing slots night", ""),
            ("Un casino no vende juego. Vende horas.", "casino floor time lapse", ""),
            ("Y ahora ya podemos montar la cuenta.", "calculator spreadsheet desk", ""),
        ],
    },
    {
        "chapter_title": "La cuenta final",
        "scenes": [
            ("Vamos a cerrar el año de ese casino mediano.", "spreadsheet numbers screen", ""),
            ("Ingreso bruto de juego: veintiocho millones.", "cash register casino", "28 M€"),
            ("Personal: nueve millones.", "employees working casino", "-9 M€"),
            ("Impuesto del juego: seis millones y medio.", "tax documents official", "-6,5 M€"),
            ("Es el mordisco autonómico sobre el margen bruto.", "government building official", ""),
            ("Y va del veinte al cincuenta y cinco por ciento según la región.", "map percentage graphic", "20-55%"),
            ("Edificio, luz y climatización: dos millones.", "electricity meter building", "-2 M€"),
            ("Vigilancia y cumplimiento: tres millones.", "surveillance control room", "-3 M€"),
            ("Máquinas, renovación y averías: dos millones.", "technician slot machine repair", "-2 M€"),
            ("Bebidas, hotel y promociones: dos millones y medio.", "casino bar drinks", "-2,5 M€"),
            ("Total de gastos: veinticinco millones.", "calculator total display", "-25 M€"),
            ("Te quedan tres millones de beneficio operativo.", "profit graph rising", "3 M€"),
            ("Sobre veintiocho facturados es un once por ciento.", "percentage chart screen", "11%"),
            ("Recuperar los veintiocho de compra lleva unos diez años.", "calendar long term planning", "10 AÑOS"),
            ("Y todo eso suponiendo que la sala se llene.", "busy casino floor crowd", ""),
            ("Porque el casino gana siempre, pero solo si hay gente.", "empty casino chairs", ""),
            ("Una sala vacía pierde dinero igual que cualquier negocio.", "empty casino night", ""),
            ("Esa es la trampa del que compra pensando que es magia.", "person counting money worried", ""),
            ("La ventaja de la casa no crea clientes. Los exprime.", "casino floor people playing", ""),
            ("Ese es el problema millonario de comprar un casino.", "casino neon sign night", ""),
            ("Si te ha servido, suscríbete. Cada semana desmontamos otro.", "casino entrance night lights", ""),
        ],
    },
]

# Escenas que se insertan ANTES del cierre de cada capítulo. Van aparte para
# que se vea de un vistazo dónde se ha profundizado.
EXTRA_SCENES: dict[str, list[tuple[str, str, str]]] = {
    "El billete de entrada": [
        ("Antes de firmar, un equipo revisa la empresa entera.", "auditor reviewing documents", ""),
        ("Cuentas, contratos, expedientes y multas de los últimos años.", "stacked folders archive", ""),
        ("Esa revisión sola cuesta doscientos mil euros.", "lawyer office meeting", "200.000 €"),
        ("Y sirve para descubrir lo que el vendedor no cuenta.", "person reading contract closely", ""),
        ("Porque nadie vende un casino que va bien.", "for sale sign building", ""),
        ("Se vende cuando la sala envejece o cambia la ley.", "old casino interior worn", ""),
        ("O cuando el dueño no puede pagar la próxima reforma.", "renovation construction interior", ""),
        ("El precio se calcula sobre el beneficio, no sobre el ladrillo.", "calculator financial documents", ""),
        ("Se paga entre seis y ocho veces el beneficio anual.", "profit chart multiplier", "x6-x8"),
        ("Si el casino gana tres millones, pides veinte o más.", "money stacks counting", "20 M€"),
        ("Y el edificio muchas veces ni siquiera entra en el trato.", "building keys handover", ""),
    ],
    "La licencia que no se vende": [
        ("La licencia tampoco es para siempre.", "expiring document stamp", ""),
        ("Se renueva cada diez o quince años según la región.", "calendar years planning", "10-15 AÑOS"),
        ("Y en cada renovación vuelven a mirarte con lupa.", "magnifying glass documents", ""),
        ("Hay comunidades que llevan años sin conceder ninguna nueva.", "closed government office", ""),
        ("Eso convierte las existentes en un activo escaso.", "rare valuable item spotlight", ""),
        ("Y por escaso, carísimo, al margen de lo que gane la sala.", "auction gavel", ""),
        ("Tampoco puedes moverla de sitio cuando quieras.", "map location pin", ""),
        ("La licencia está atada a un municipio concreto.", "town hall building", ""),
        ("Si el barrio se muere, te mueres con él.", "empty street closed shops", ""),
        ("Y venderla exige otra vez el visto bueno del regulador.", "official approval stamp", ""),
        ("Comprar es difícil, pero salir lo es todavía más.", "locked door chain", ""),
    ],
    "Llenar la sala": [
        ("Las máquinas además pagan derechos al fabricante.", "slot machine manufacturer logo", ""),
        ("Un porcentaje de lo que recaudan, cada mes, para siempre.", "money flowing calculation", ""),
        ("Y hay que renovarlas cada cinco o seis años.", "new slot machines delivery", "5-6 AÑOS"),
        ("Una máquina vieja deja de atraer y ocupa metros caros.", "old arcade machine dusty", ""),
        ("Los botes progresivos son otra deuda escondida.", "jackpot display numbers", ""),
        ("Cada moneda jugada engorda un premio que tendrás que pagar.", "coins dropping machine", ""),
        ("Ese bote figura en tu balance como obligación pendiente.", "financial liability document", ""),
        ("Hasta la moqueta está pensada y cuesta una fortuna.", "patterned casino carpet", ""),
        ("Los dibujos marean lo justo para que mires hacia arriba.", "casino carpet pattern close", ""),
        ("Y arriba están las luces y las pantallas de premios.", "casino ceiling lights screens", ""),
        ("Nada en esa sala está puesto por casualidad.", "casino interior design wide", ""),
    ],
    "El dinero que no es tuyo": [
        ("Cada noche hay que contar todo lo que ha entrado.", "cash counting machine night", ""),
        ("Las cajas de las mesas se abren con dos personas presentes.", "two people opening safe", ""),
        ("Y siempre delante de una cámara que graba el recuento.", "surveillance camera counting room", ""),
        ("El efectivo sale en furgón blindado, no en un coche.", "armored truck security", ""),
        ("Ese servicio cuesta unos cien mil euros al año.", "security transport van", "100.000 €"),
        ("El seguro de la sala es otro capítulo caro.", "insurance policy documents", ""),
        ("Cubre robo, incendio y responsabilidad civil.", "fire safety equipment", ""),
        ("Y ronda los trescientos mil euros anuales.", "insurance contract signing", "300.000 €"),
        ("Porque asegurar un edificio lleno de dinero no es barato.", "vault door heavy", ""),
        ("Todo esto sigue sin producir ni un euro de ingreso.", "empty cash register", ""),
        ("Son costes de existir, no de funcionar.", "building at night lights", ""),
    ],
    "Trescientas personas": [
        ("Un crupier no se contrata: se forma.", "training class casino school", ""),
        ("Hacen falta meses para pagar una ruleta sin pensar.", "hands practicing chips", ""),
        ("Muchos casinos montan su propia escuela interna.", "classroom training tables", ""),
        ("Formar a uno cuesta varios miles de euros.", "student learning cards", ""),
        ("Y encima el personal necesita su propia autorización.", "id badge employee", ""),
        ("El regulador revisa antecedentes de cada empleado de sala.", "background check documents", ""),
        ("Uno rechazado es un puesto que se queda sin cubrir.", "empty chair workplace", ""),
        ("El turno de noche se paga más caro por ley.", "night shift worker tired", ""),
        ("Y la rotación en sala es alta, como en toda la hostelería.", "revolving door people", ""),
        ("Cada baja obliga a cerrar una mesa o pagar horas extra.", "closed casino table sign", ""),
        ("La plantilla es el músculo y también la hipoteca.", "team working together casino", ""),
    ],
    "El ojo en el techo": [
        ("Hay un registro de personas que se han autoprohibido jugar.", "database screen list", ""),
        ("Si entra una y no la detectas, la multa es tuya.", "fine penalty document", ""),
        ("Y las sanciones llegan a cientos de miles de euros.", "legal penalty stamp", "100.000 €+"),
        ("Por eso la entrada pide documento a todo el mundo.", "id check entrance", ""),
        ("Muchas salas ya cruzan la cara con el registro automáticamente.", "facial recognition screen", ""),
        ("El sistema tiene que estar activo en cada puerta.", "entrance turnstile security", ""),
        ("A eso súmale las inspecciones sin avisar.", "inspector clipboard visit", ""),
        ("Revisan máquinas, porcentajes de pago y libros de caja.", "inspector checking machine", ""),
        ("Una máquina fuera de rango se precinta en el acto.", "sealed machine tape", ""),
        ("Y con ella se va su ingreso hasta que se arregle.", "out of order sign", ""),
        ("Cumplir la ley aquí no es papeleo: es la licencia.", "legal documents official seal", ""),
    ],
    "La ventaja de la casa": [
        ("La ley fija cuánto tiene que devolver una máquina.", "regulation document gambling", ""),
        ("En España el mínimo ronda el ochenta y cinco por ciento.", "percentage display screen", "85%"),
        ("Eso significa que de cada cien euros devuelve ochenta y cinco.", "coins returning tray", ""),
        ("Los quince restantes son del casino, jugada tras jugada.", "money accumulating stack", "15%"),
        ("Y el jugador medio reinvierte lo que gana en la misma máquina.", "person playing slots absorbed", ""),
        ("Por eso el porcentaje real que se queda la casa es mayor.", "rising graph money", ""),
        ("El blackjack sobrevive porque atrae a otro tipo de cliente.", "blackjack table elegant", ""),
        ("Gente que se queda horas y consume mucho más.", "casino bar drinks people", ""),
        ("El casino calcula lo que espera ganarte y te devuelve una parte.", "calculator strategy", ""),
        ("En bebidas, en hotel, en cenas: se llama pérdida teórica.", "hotel room luxury", ""),
        ("Si esperan ganarte mil, invitarte a cien sale rentable.", "cocktail casino service", ""),
    ],
    "La cuenta final": [
        ("Compáralo con no hacer absolutamente nada.", "stock market chart calm", ""),
        ("Metes esos veintiocho millones en un fondo indexado.", "investment portfolio screen", "28 M€"),
        ("Sacarías cerca de dos millones al año sin levantarte.", "investment growth chart", "2 M€"),
        ("Sin licencias, sin inspecciones y sin trescientas nóminas.", "relaxed person laptop", ""),
        ("El casino te da tres, y con todo el riesgo encima.", "casino floor risk", "3 M€"),
        ("Por eso casi ningún casino cambia de manos.", "closed sign gate", ""),
        ("Quien tiene la licencia se la queda hasta que revienta.", "old casino sign faded", ""),
        ("El verdadero activo nunca fue el edificio.", "building demolition old", ""),
        ("Era el permiso para que la aritmética trabaje sola.", "roulette wheel slow motion", ""),
        ("Y ese permiso no se compra: se hereda o se paga carísimo.", "handshake formal deal", ""),
        ("Lo demás son luces, moqueta y bebida gratis.", "casino lights blur", ""),
    ],
}

METADATA = {
    "title": "Esto es lo que cuesta comprar un casino (la cuenta real)",
    "description": """🎰 28.000.000 € para comprarlo. 5.000.000 € más que no puedes tocar nunca. Y una ventaja de la casa del 2,7%.

Desglosamos lo que cuesta de verdad un casino: la licencia que no está a la venta, las 300 máquinas, las 100.000 fichas, el fondo de caja inmovilizado, las 300 nóminas y el impuesto autonómico que se lleva hasta el 55% del margen.

🎯 El dato que lo explica todo: un casino no apuesta contra ti. Te vende tiempo. Por eso no hay relojes, ni ventanas, ni salidas evidentes, y la bebida es gratis.

👁️ Y sobre tu cabeza hay más de mil cámaras que no están ahí solo por los tramposos.

🔔 Suscríbete: cada semana desmontamos otro problema millonario.

⏱️ CAPÍTULOS
{{CHAPTERS}}

📊 Cifras estimadas para España a partir de fuentes públicas del sector del juego. Cantidades redondeadas.

#Casinos #Negocios #Dinero""",
    "tags": [
        "cuanto cuesta un casino", "comprar un casino", "montar un casino",
        "negocio del casino", "ventaja de la casa", "como gana dinero un casino",
        "casinos españa", "licencia de casino", "casino las vegas negocio",
        "ruleta probabilidades", "maquinas tragaperras negocio",
        "cuanto gana un casino", "industria del juego", "casino", "apuestas",
        "modelo de negocio", "gastos ocultos", "economia explicada",
        "curiosidades de dinero", "rentabilidad de un negocio",
        "inversion millonaria", "problemas millonarios",
    ],
    "thumbnail_text": "ASÍ CUESTA UN CASINO",
    "thumbnail_figure": "28 M€",
}

ANCHORS = [
    "casino", "casino floor", "roulette wheel", "slot machine",
    "casino chips", "blackjack table", "las vegas casino", "croupier dealer",
]
KEYWORDS = [
    "casino", "roulette", "slot machine", "slots", "chips", "blackjack",
    "poker", "croupier", "dealer", "gambling", "jackpot", "las vegas",
    "dice", "playing cards", "betting",
]
KEYWORDS_PRIMARY = ["casino", "roulette", "slot machine", "blackjack", "jackpot"]


def main() -> int:
    hook = {
        "lines": [{"narration": t, "on_screen": label} for t, label in HOOK_LINES],
        "visuals": HOOK_VISUALS,
    }
    blocks = []
    for index, spec in enumerate(BLOCKS, start=1):
        scenes = list(spec["scenes"])
        extra = EXTRA_SCENES.get(spec["chapter_title"], [])
        if extra:
            # Van antes del cierre: la última escena es el bucle abierto que
            # engancha con el capítulo siguiente y tiene que seguir la última.
            scenes = scenes[:-1] + extra + scenes[-1:]
        blocks.append({
            "id": index,
            "chapter_title": spec["chapter_title"],
            "scenes": [
                {"narration": n, "broll_query": q, "on_screen": label}
                for n, q, label in scenes
            ],
        })

    script = {
        "outline": {
            "working_title": TITLE,
            "total_figure": "28 millones para comprarlo y 25 al año para mantenerlo",
            "comparison": "un 11% de margen, diez años para recuperar la compra",
            "broll_anchors": ANCHORS,
            "broll_keywords": KEYWORDS,
            "broll_keywords_primary": KEYWORDS_PRIMARY,
            "blocks": [
                {"id": b["id"], "chapter_title": b["chapter_title"], "thesis": "",
                 "key_figures": [], "open_loop": "",
                 "target_words": sum(len(s["narration"].split()) for s in b["scenes"])}
                for b in blocks
            ],
        },
        "hook": hook,
        "blocks": blocks,
        "metadata": METADATA,
    }

    target = CONFIG_DIR / "manual" / f"{SLUG}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")

    words = sum(len(l["narration"].split()) for l in hook["lines"])
    words += sum(len(s["narration"].split()) for b in blocks for s in b["scenes"])
    scenes = len(hook["lines"]) + sum(len(b["scenes"]) for b in blocks)
    tags = ",".join(METADATA["tags"])
    log.info(str(target))
    log.info(f"{len(blocks)} capítulos · {scenes} escenas · {words} palabras")
    log.info(f"~ {words / 165:.1f} minutos de narración")
    log.info(f"etiquetas: {len(tags)}/500 caracteres")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
