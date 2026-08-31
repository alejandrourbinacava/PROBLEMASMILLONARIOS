#!/usr/bin/env python3
"""
Construye proyecto/guion.json para el episodio del casino.

Se escribe asi, y no a mano, por una razon: las capas se REUTILIZAN.
Un vídeo de 13 minutos son ~85 escenas. Con 3 capas cada una serian 255
PNG. Aqui son 34, porque el cielo del capitulo 1 es el mismo que el del
capitulo 6 y la fachada aparece en nueve escenas distintas.

    python3 construir_guion.py
"""
import json, os, math, collections

# El estilo se concatena a TODOS los prompts, tambien a los de interior. Con
# "noche, azul marino muy oscuro" dentro, pedir "interior de camara acorazada"
# devolvia un cielo nocturno: el modelo obedece al color antes que al sitio, y
# el episodio entero salia con el mismo telon azul detras de todo. Aqui va
# solo la CALIDAD y el criterio de luz; la hora y el lugar los pone cada
# fondo, que para eso es suyo.
ESTILO = ("fotorrealista cinematografico, gran presupuesto, optica de cine, "
          "iluminacion motivada por las fuentes que hay en la propia escena, "
          "contraste alto, mucha profundidad y detalle, sin texto, "
          "sin logotipos")

# ---------------------------------------------------------------------------
# FONDOS: uno por escena, SIEMPRE. Reutilizar el cielo era una optimizacion
# de coste que tenia sentido a 0,19 $ la imagen; a 0,0005 $ no la tiene, y
# el precio que se paga es que las 85 escenas parecen la misma. El fondo se
# describe a partir de lo que cuenta la escena, no de un catalogo.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# BIBLIOTECA DE CAPAS  ->  id: (rol, archivo, prompt)
# ---------------------------------------------------------------------------
A = {
 # --- fondos (opacos) ---
 "cielo":     ("fondo", "01_cielo.png",
    "cielo nocturno del desierto con nubes rotas y estrellas sobre azul "
    "marino profundo, con el resplandor de una ciudad en el borde de abajo"),
 "sala":      ("fondo", "f_sala.png",
    "interior de una sala de juego de casino llena, con mesas de tapete, "
    "lamparas de araña doradas, moqueta con dibujo y techo artesonado. "
    "Ligera falta de foco de fondo pero la sala se reconoce entera"),
 "desierto":  ("fondo", "f_desierto.png",
    "horizonte de desierto de Nevada de noche, montanas lejanas recortadas, "
    "resplandor anaranjado de una ciudad a lo lejos"),
 "despacho":  ("fondo", "f_despacho.png",
    "interior de un despacho oficial con estanterias de archivadores "
    "metalicos, persianas venecianas, mesa con lampara y suelo de linoleo, "
    "luz fria de fluorescente. Se reconoce la habitacion entera"),
 "obra":      ("fondo", "f_obra.png",
    "interior de un edificio en construccion, vigas de acero vistas, "
    "andamios, plasticos y focos de obra encendidos. Se ve el suelo de "
    "hormigon y el fondo de la nave"),
 "frio":      ("fondo", "f_frio.png",
    "interior de una sala de reuniones vacia en penumbra, mesa larga, sillas "
    "y una pared de cristal con la ciudad detras, luz fria"),
 "boveda":    ("fondo", "f_boveda.png",
    "interior de una camara acorazada de banco, paredes de cajas de "
    "seguridad de laton, puerta circular de acero abierta al fondo, suelo "
    "pulido, luz calida rasante"),

 # --- gente dentro de la escena ---
 "crupier":   ("figura", "f_crupier.png",
    "crupier de casino de pie detras de una mesa de juego, chaleco negro, "
    "camisa blanca y pajarita, de cuerpo entero y visto de frente"),
 "jugador":   ("figura", "f_jugador.png",
    "hombre de esmoquin de pie de perfil junto a una mesa de juego, de "
    "cuerpo entero, con una copa en la mano"),
 "jugadora":  ("figura", "f_jugadora.png",
    "mujer de vestido de noche largo de pie junto a una mesa de juego, de "
    "cuerpo entero, vista de tres cuartos"),
 "jugador2":  ("figura", "f_jugador2.png",
    "hombre mayor de traje oscuro de pie de espaldas tres cuartos junto a una "
    "mesa de juego, de cuerpo entero, con las manos en los bolsillos"),
 "jugadora2": ("figura", "f_jugadora2.png",
    "mujer joven de vestido de coctel de pie de perfil junto a una mesa de "
    "juego, de cuerpo entero, apoyada en el borde"),
 "mirones":   ("figura", "f_mirones.png",
    "dos personas de espaldas de pie muy juntas mirando una mesa de juego, "
    "de cuerpo entero, en traje de noche"),

 # --- planos de apoyo: lo que impide que el sujeto flote ---
 "vecinos":   ("horizonte", "h_vecinos.png",
    "fila continua de edificios de ciudad en SEGUNDO PLANO, en penumbra y "
    "casi en silueta, poco detalle, ventanas apenas insinuadas, todos de "
    "altura parecida, alineados de un extremo al otro sin perspectiva"),
 "vecinos2":  ("horizonte", "h_vecinos2.png",
    "manzana de edificios bajos en SEGUNDO PLANO, oscuros y sin detalle, "
    "apenas siluetas contra la noche, alineadas de un extremo al otro"),

 # --- medios (transparentes) ---
 "fachada":   ("medio", "01_casino.png",
    "fachada de casino art deco de noche, rotulo CASINO con bombillas, "
    "vista frontal simetrica"),
 "resort":    ("suelo", "m_resort.png",
    "torre de hotel resort de lujo iluminada de noche con marquesina en la base, "
    "vista frontal completa"),
 "nave":      ("medio", "m_nave.png",
    "casino independiente de una sola planta, edificio bajo y ancho con rotulo "
    "de neon, sin torre de hotel, vista frontal"),
 "planos":    ("suelo", "m_planos.png",
    "maqueta arquitectonica de un edificio sobre soporte junto a planos enrollados"),
 "maquinas":  ("suelo", "m_maquinas.png",
    "fila frontal de maquinas tragaperras encendidas, vista recta y simetrica"),
 "ruleta":    ("suelo", "m_ruleta.png",
    "mesa de ruleta de casino con tapete verde y rueda dorada, vista frontal"),
 "moqueta":   ("suelo", "m_moqueta.png",
    "fragmento de moqueta de casino con dibujo geometrico recargado, vista cenital"),
 "camaras":   ("medio", "m_camaras.png",
    "racimo de camaras de vigilancia tipo domo negras montadas en estructura de techo"),
 "expediente":("suelo", "m_expediente.png",
    "pila alta e inestable de carpetas de expediente y documentos con sellos oficiales"),
 "licencia":  ("suelo", "m_licencia.png",
    "documento de licencia oficial enmarcado con sello en relieve, vista frontal"),
 "gobierno":  ("medio", "m_gobierno.png",
    "edificio gubernamental neoclasico con columnas, vista frontal simetrica, de noche"),
 "mapa":      ("suelo", "m_mapa.png",
    "mapa de Estados Unidos estilizado en relieve solido, sin nombres ni texto"),
 "balanza":   ("suelo", "m_balanza.png",
    "balanza de justicia de metal pesado, vista frontal, un plato mucho mas bajo"),
 "billetes":  ("suelo", "m_billetes.png",
    "torre alta de fajos de billetes apilados, vista frontal"),
 "fichas_t":  ("suelo", "m_fichas_torre.png",
    "torres de fichas de casino apiladas a distintas alturas, vista frontal"),
 "pared":     ("medio", "m_pared.png",
    "pared lisa de casino con la marca circular mas clara donde faltaba un reloj"),
 "pasillo":   ("medio", "m_pasillo.png",
    "pasillo curvo de casino que gira sin salida visible, luces bajas"),
 "silla":     ("suelo", "m_silla.png",
    "silla de crupier vacia frente a una mesa de juego apagada"),
 "grafica":   ("suelo", "m_grafica.png",
    "grafica de barras ascendente construida como objeto fisico en relieve, sin texto"),
 "candado":   ("medio", "m_candado.png",
    "puerta doble de metal cerrada con cadena gruesa y candado"),
 "reloj":     ("suelo", "m_reloj.png",
    "reloj de fichar industrial con tarjetas de turno colgadas al lado"),
 "cadena":    ("medio", "m_cadena.png",
    "cadena gruesa de acero suspendida, rota por un eslabon"),
 "club":      ("suelo", "m_club.png",
    "hilera corta de sillones de cuero de club privado, todos ocupados por siluetas "
    "salvo el ultimo, vacio"),
 "maletin":   ("suelo", "m_maletin.png",
    "maletin metalico abierto lleno de fajos de billetes"),

 # --- frentes (transparentes, cortados por abajo) ---
 "multitud":  ("frente", "01_multitud.png",
    "multitud de espaldas en traje de gala, siluetas a contraluz, franja ancha"),
 "fichas_p":  ("frente", "p_fichas.png",
    "fichas de casino desparramadas muy cerca de la camara, desenfocadas"),
 "cordon":    ("frente", "p_cordon.png",
    "cordon de terciopelo rojo entre postes dorados, franja ancha"),
 "manos":     ("frente", "p_manos.png",
    "unicamente dos manos y dos antebrazos con punos de camisa, entrando desde el borde inferior y empujando fichas sobre el tapete. Nada de cabeza, nada de hombros, nada de torso: el encuadre empieza en los codos. Franja ancha"),
 "papeles":   ("frente", "p_papeles.png",
    "borde superior de documentos y carpetas apiladas vistos muy de cerca"),
 "hombros":   ("frente", "p_hombros.png",
    "hombros y nucas de varias personas en traje oscuro, franja ancha"),
 "monitores": ("frente", "p_monitores.png",
    "borde inferior de una pared de monitores de vigilancia encendidos"),
}

# ---------------------------------------------------------------------------
# ESCENAS  ->  (texto, duracion, movimiento, [capas de atras a delante])
# Una idea = una escena. Entre 6 y 14 s.
# ---------------------------------------------------------------------------
GUION = [
("GANCHO", 60, [
 ("En febrero de 2026, los casinos de Nevada ganaron 1.236 millones de dólares.",
  8, "push_in", ["cielo", "fachada", "multitud"]),
 ("Eso no es lo que apostaron los clientes. Eso es lo que perdieron. En un mes.",
  7, "estatico", ["sala", "fichas_t", "fichas_p"]),
 ("Solo el Strip de Las Vegas se quedó 696 millones. En veintiocho días.",
  8, "drift_izq", ["desierto", "resort", "multitud"]),
 ("No depende de si la temporada fue buena ni de si el marketing funcionó.",
  7, "pull_out", ["sala", "ruleta", "manos"]),
 ("Depende de una fórmula matemática que no falla nunca.",
  7, "push_in", ["frio", "ruleta", None]),
 ("Así que la pregunta se hace sola: cuánto cuesta tener uno.",
  6, "estatico", ["cielo", "fachada", "cordon"]),
 ("Con un McDonald's el problema era el dinero. Con un casino el dinero es la parte fácil.",
  9, "drift_der", ["boveda", "maletin", "fichas_p"]),
 ("Hay algo que nunca va a ser tuyo. Y te lo pueden quitar en cualquier momento.",
  8, "push_in", ["frio", "licencia", "papeles"]),
]),

("CAP1_DOS_CASINOS", 120, [
 ("Casino no es un negocio. Son dos, y no se parecen en nada.",
  8, "pull_out", ["cielo", "fachada", "multitud"]),
 ("El primero es lo que imaginas: torre de hotel, restaurantes, espectáculo, spa.",
  12, "push_in", ["desierto", "resort", "cordon"]),
 ("Construir uno de tres plantas cuesta entre sesenta y ciento cincuenta millones.",
  10, "estatico", ["obra", "resort", None]),
 ("Y esa cifra es solo el hormigón. Ni el terreno, ni las licencias, ni una sola máquina.",
  10, "drift_izq", ["obra", "planos", None]),
 ("El segundo casino es el que nadie enseña: una planta, sala de juego y poco más.",
  11, "push_in", ["desierto", "nave", None]),
 ("Un casino independiente de ese tipo se construye entre diez y cuarenta millones.",
  9, "estatico", ["obra", "nave", None]),
 ("Es la diferencia entre montar un hotel de lujo y montar una nave con máquinas dentro.",
  10, "drift_der", ["obra", "maquinas", None]),
 ("En el resort, el juego no es el negocio principal. Es el gancho.",
  11, "pull_out", ["sala", "resort", "multitud"]),
 ("El dinero de verdad está en las habitaciones, los restaurantes y las entradas.",
  10, "drift_izq", ["desierto", "resort", "cordon"]),
 ("En el casino pequeño, el juego es el negocio. Cien por cien.",
  8, "push_in", ["sala", "maquinas", None]),
 ("Dos modelos, dos estructuras de coste, dos formas distintas de perder dinero.",
  10, "estatico", ["frio", "grafica", None]),
 ("Vamos a seguir el pequeño, porque es donde la matemática se ve limpia.",
  11, "push_in", ["desierto", "nave", "hombros"]),
]),

("CAP2_EDIFICIO", 100, [
 ("Construir un casino cuesta entre trescientos y quinientos cincuenta dólares el pie cuadrado.",
  11, "push_in", ["obra", "planos", None]),
 ("En ubicaciones premium puede pasar de novecientos. Precio de hotel de cinco estrellas.",
  9, "drift_der", ["obra", "resort", None]),
 ("Porque el edificio es parte del producto.",
  8, "pull_out", ["sala", "fachada", "multitud"]),
 ("La moqueta de dibujos imposibles. La iluminación sin ventanas.",
  12, "push_in", ["sala", "moqueta", None]),
 ("La ausencia total de relojes. Los pasillos que nunca te llevan directo a la salida.",
  11, "drift_izq", ["sala", "pared", None]),
 ("Nada de eso es decoración. Es ingeniería de comportamiento, y sale cara.",
  9, "push_in", ["sala", "pasillo", None]),
 ("Las tragaperras no se compran sin más: muchas se arriendan con parte de la recaudación.",
  12, "estatico", ["sala", "maquinas", "fichas_p"]),
 ("Las mesas necesitan crupieres formados. La vigilancia es el estandar del sector.",
  11, "push_in", ["sala", "camaras", "monitores"]),
 ("Solo el equipamiento y el mobiliario superan los sesenta millones de dólares.",
  9, "estatico", ["boveda", "billetes", None]),
 ("Pero todo esto es dinero. Y el dinero se consigue. Lo siguiente, no.",
  8, "push_in", ["frio", "licencia", None]),
]),

("CAP3_LICENCIA", 140, [
 ("Aquí está el malentendido que tiene todo el mundo.",
  7, "estatico", ["despacho", "licencia", None]),
 ("La gente cree que una licencia de juego es un papel que se compra.",
  9, "push_in", ["despacho", "licencia", "papeles"]),
 ("Vamos a mirar los números oficiales de Nevada, porque son públicos.",
  8, "drift_der", ["despacho", "gobierno", None]),
 ("La licencia no restringida es la de un casino de verdad: dieciséis máquinas o cualquier mesa.",
  11, "estatico", ["sala", "maquinas", None]),
 ("La tasa de solicitud va, según la fuente, de siete mil quinientos a setenta y cinco mil dólares.",
  10, "push_in", ["despacho", "expediente", "papeles"]),
 ("Siete mil quinientos dólares. Para un negocio de cuarenta millones.",
  9, "estatico", ["boveda", "billetes", None]),
 ("Parece un chiste. Y lo es, porque la tasa no es el coste.",
  8, "pull_out", ["despacho", "licencia", None]),
 ("El coste es la investigación.",
  7, "push_in", ["despacho", "expediente", None]),
 ("El Nevada Gaming Control Board no evalúa tu plan de negocio. Te evalúa a ti.",
  11, "push_in", ["despacho", "gobierno", "hombros"]),
 ("Empieza en diez mil dólares y puede superar los cincuenta mil.",
  9, "estatico", ["despacho", "expediente", "papeles"]),
 ("Cada cuenta bancaria. El origen de cada dólar. Tus socios. Tu familia. Tus divorcios.",
  12, "drift_izq", ["despacho", "expediente", "papeles"]),
 ("No hay presunción de inocencia. La carga de la prueba es tuya.",
  9, "push_in", ["despacho", "balanza", None]),
 ("El proceso puede llevar más de un año.",
  7, "estatico", ["despacho", "reloj", None]),
 ("Una licencia de juego interactivo cuesta quinientos mil iniciales y doscientos cincuenta mil al año.",
  12, "push_in", ["frio", "licencia", "papeles"]),
 ("El gasto principal es la versión de ti que no consigue la licencia.",
  11, "pull_out", ["despacho", "candado", None]),
]),

("CAP4_SOCIO", 140, [
 ("Supongamos que la consigues. Estás dentro. Las máquinas están encendidas.",
  10, "push_in", ["sala", "maquinas", "fichas_p"]),
 ("Y entonces conoces a tu socio.",
  6, "estatico", ["frio", "gobierno", None]),
 ("El Estado no te cobra al final del año como a cualquier empresa.",
  10, "drift_der", ["despacho", "gobierno", None]),
 ("Se lleva un porcentaje de tu ganancia bruta de juego todos los meses. Antes que nadie.",
  12, "push_in", ["boveda", "fichas_t", "manos"]),
 ("Cuánto. Depende de donde pongas el casino, y las diferencias son brutales.",
  10, "pull_out", ["frio", "mapa", None]),
 ("En Nevada, el tramo más alto es del seis coma setenta y cinco por ciento.",
  11, "push_in", ["desierto", "nave", None]),
 ("No es casualidad: Nevada llego primero y fijo las reglas cuando nadie más queria esto.",
  11, "drift_izq", ["desierto", "fachada", None]),
 ("En Nueva Jersey son el ocho, el quince en juego online y el trece en apuestas deportivas.",
  12, "estatico", ["frio", "mapa", None]),
 ("Y en el otro extremo esta Maryland, donde el tipo máximo llega al sesenta y dos coma cinco.",
  12, "push_in", ["frio", "mapa", None]),
 ("Sesenta y dos coma cinco.",
  6, "estatico", ["frio", "balanza", None]),
 ("De cada dólar, más de sesenta centavos van al Estado antes de pagar una sola nomina.",
  12, "push_in", ["boveda", "billetes", "manos"]),
 ("La decisión más importante de tu negocio no es el producto ni la ubicación. Es la jurisdicción.",
  13, "pull_out", ["frio", "mapa", "hombros"]),
 ("El mismo casino en dos estados distintos son dos negocios completamente diferentes.",
  9, "drift_der", ["desierto", "nave", None]),
 ("Los operadores serios eligen el estado antes que el solar.",
  6, "estatico", ["obra", "planos", None]),
]),

("CAP5_INGRESOS", 100, [
 ("Vale. Y cuánto se gana.",
  6, "push_in", ["sala", "fichas_t", None]),
 ("Un restaurante depende de que la comida guste. Un casino depende de una fórmula.",
  10, "drift_izq", ["sala", "ruleta", "manos"]),
 ("Cada juego tiene una ventaja matemática fija para la casa.",
  8, "push_in", ["sala", "ruleta", None]),
 ("En la ruleta europea ese margen es del dos coma siete por ciento.",
  8, "estatico", ["frio", "ruleta", None]),
 ("En las máquinas lo fija el fabricante y lo aprueba el regulador.",
  8, "drift_der", ["sala", "maquinas", None]),
 ("Con suficientes apuestas, la ganancia deja de ser una probabilidad y pasa a ser una previsión.",
  10, "push_in", ["frio", "grafica", None]),
 ("Por eso el sector entero se mide en una sola métrica: el win, lo que pierden los clientes.",
  10, "estatico", ["sala", "fichas_t", "fichas_p"]),
 ("De julio de 2025 a febrero de 2026, Nevada acumuló diez mil quinientos ochenta y ocho millones.",
  11, "push_in", ["boveda", "billetes", None]),
 ("Suena a máquina de imprimir dinero. Y en cierto modo lo es.",
  7, "pull_out", ["boveda", "billetes", "fichas_p"]),
 ("Pero fijate en lo que hemos ido apilando encima.",
  6, "push_in", ["despacho", "expediente", None]),
 ("Nóminas veinticuatro horas al dia. La deuda. Y antes que todo eso, el Estado.",
  9, "drift_izq", ["despacho", "reloj", "hombros"]),
 ("La matemática garantiza que ganas dinero. No garantiza que quede algo para ti.",
  7, "estatico", ["sala", "silla", None]),
]),

("CAP6_GIRO", 80, [
 ("Y llegamos a lo que hace que este negocio sea distinto a todos los demas.",
  7, "push_in", ["cielo", "fachada", "multitud"]),
 ("En McDonald's, el franquiciado descubre al final que el edificio nunca fue suyo.",
  9, "drift_der", ["obra", "nave", None]),
 ("En un casino es peor. Lo que no es tuyo no es el ladrillo. Es el permiso para existir.",
  10, "push_in", ["frio", "licencia", None]),
 ("Una licencia no se compra. Se concede. Y lo que se concede se puede retirar.",
  9, "pull_out", ["despacho", "licencia", "papeles"]),
 ("No se retira solo por hacer trampas. Basta un socio inadecuado o un fallo de control.",
  10, "drift_izq", ["despacho", "cadena", None]),
 ("Mientras seas licenciatario, la investigación no termina. Sigue. Indefinidamente.",
  8, "push_in", ["despacho", "camaras", "monitores"]),
 ("En muchas jurisdicciones el número de licencias está limitado por ley.",
  8, "estatico", ["frio", "club", None]),
 ("No es un mercado abierto. Es un club cerrado donde las sillas las decide un parlamento.",
  9, "push_in", ["despacho", "club", "hombros"]),
 ("Los casinos no venden juego. Venden acceso a una escasez que ellos no crearon.",
  10, "pull_out", ["cielo", "fachada", "multitud"]),
]),

("CIERRE", 40, [
 ("Entonces, se puede comprar un casino.",
  6, "estatico", ["cielo", "fachada", None]),
 ("Con diez millones el edificio pequeño. Con cuarenta, uno decente. Con ciento cincuenta, un resort.",
  10, "push_in", ["desierto", "resort", None]),
 ("Pero no es un negocio que se compre con dinero. Es un negocio en el que te admiten.",
  9, "pull_out", ["frio", "club", None]),
 ("Tu socio mayoritario es un Estado. Tu activo principal es una licencia que no posees.",
  9, "push_in", ["despacho", "licencia", "papeles"]),
 ("El permiso temporal para operar una fórmula que no puede fallar. Mientras les sigas cayendo bien.",
  6, "estatico", ["cielo", "fachada", "multitud"]),
]),
]


# Rotacion de composiciones. No es aleatoria a proposito: una secuencia
# fija garantiza que nunca salgan dos iguales seguidas y que las ocho se
# usen por igual. El editor puede cambiar una escena suelta a mano.
# LOGICA DE APOYO. Un edificio recortado sobre un cielo cuelga del aire; una
# ruleta sobre un fondo abstracto flota. No es un fallo de colocacion, es que
# falta una capa: la del plano sobre el que la cosa se apoya. Para un edificio
# son los edificios vecinos, para un objeto es la mesa. Se inserta sola,
# detras del sujeto, y se alterna entre dos variantes para que quince escenas
# no compartan el mismo horizonte.
EDIFICIOS = {"fachada", "resort", "nave", "gobierno"}
SOBRE_MESA = {"ruleta", "fichas_t", "billetes", "maletin", "planos", "licencia",
              "expediente", "balanza", "reloj", "grafica", "mapa"}
APOYO = {"edificio": ["vecinos", "vecinos2"]}

# Un objeto NO lleva banda de mesa: su propia imagen ya trae la superficie
# sobre la que se apoya -la ruleta viene con su mesa, las fichas con su
# tapete-. Ponerle ademas una franja detras dejaba la ruleta por DEBAJO de la
# superficie, que es peor que no poner nada. Lo que si necesita un objeto es
# estar en una HABITACION: lo que lo hacia flotar era tenerlo recortado sobre
# un cielo o sobre un fondo abstracto, sin sitio donde estar.
INTERIORES = ["sala", "despacho", "boveda"]
EXTERIORES = {"cielo", "desierto", "frio"}
FUERA = ["cielo", "desierto"]

# UNA MESA DE JUEGO NO ESTA SOLA. Si hay una ruleta o una mesa de fichas, hay
# un crupier detras y gente alrededor: eso son tres capas mas, no una foto de
# un mueble. Una mesa sola en el cuadro no es una escena de casino, es un
# catalogo de muebles.
MESAS_DE_JUEGO = {"ruleta", "fichas_t", "maquinas", "silla"}
# El crupier va SIEMPRE -es quien lleva la mesa- y le acompanan uno o dos
# jugadores que rotan. Una mesa con tres personas alrededor y unas manos en
# primer plano son cinco capas, y es lo que hace que el plano tenga fondo,
# medio y frente de verdad en vez de un mueble sobre un decorado.
GENTE = ["crupier"]
ACOMPANA = ["jugador", "jugadora", "jugador2", "jugadora2", "mirones"]
# Manos en primer plano: son las del jugador que mira, y son lo que mete al
# espectador DENTRO de la mesa en vez de dejarlo mirando desde fuera.
MANOS = ["manos", "fichas_p"]

# Con que se rellena una escena que se ha quedado corta, segun DONDE pasa.
# Una escena de dos capas es un fondo y un recorte encima: no hay profundidad
# que ver. Con cuatro o cinco hay algo delante, algo detras y alguien dentro,
# y es entonces cuando el sujeto principal resalta en vez de flotar.
RELLENO = {
 "sala":     dict(frente=["fichas_p", "multitud", "cordon"], gente=["jugadora", "mirones"]),
 "despacho": dict(frente=["papeles", "hombros"],             gente=["jugador2"]),
 "boveda":   dict(frente=["fichas_p", "manos"],              gente=["jugador"]),
 "cielo":    dict(frente=["multitud", "cordon"],             gente=[]),
 "desierto": dict(frente=["multitud", "hombros"],            gente=[]),
 "obra":     dict(frente=["papeles", "hombros"],             gente=["jugador2"]),
 "frio":     dict(frente=["papeles", "monitores"],           gente=["jugador"]),
}
MINIMO_CAPAS = 4

# CLIPS DE STOCK. Una frase de enlace no necesita tres capas generadas: un
# plano real bien graduado la cuenta igual y rompe la monotonia de que TODO
# sea composicion. Van por palabra clave, con cupo, para que sean condimento
# y no relleno. El clip de obra queda fuera a proposito: es de dia y no pega
# en un episodio nocturno.
# Catorce clips, todos de noche y todos revisados uno a uno en hoja de
# contactos: de los veinticuatro candidatos que el catalogo daba por buenos,
# once no eran lo que decian ser -un campo de tulipanes etiquetado "money in
# bank vault", un pajaro como "casino surveillance"-. Ninguna metrica detecta
# eso; hay que mirarlos.
CLIPS = [
 ("las vegas",     "stock/strip_aereo.mp4",     2),
 ("strip",         "stock/vegas_aereo.mp4",     2),
 ("nevada",        "stock/strip_aereo.mp4",     2),
 ("ruleta",        "stock/ruleta_girando.mp4",  3),
 ("crupier",       "stock/crupier_manos.mp4",   2),
 ("fichas",        "stock/fichas_apilando.mp4", 3),
 ("tragaperras",   "stock/tragaperras.mp4",     2),
 ("maquinas",      "stock/sala_maquinas.mp4",   3),
 ("sala de juego", "stock/mesa_jugadores.mp4",  2),
 ("clientes",      "stock/mesa_jugadores.mp4",  2),
 ("jugadores",     "stock/mesa_jugadores.mp4",  2),
 ("lujo",          "stock/lampara_lobby.mp4",   2),
 ("hotel",         "stock/lampara_lobby.mp4",   2),
 ("edificio",      "stock/casino_aereo.mp4",    2),
 ("puertas",       "stock/calle_casino.mp4",    2),
 ("ciudad",        "stock/ciudad_noche.mp4",    2),
 ("noche",         "stock/ciudad_noche.mp4",    2),
]
# Para una frase de enlace que no case con ninguna palabra clave: un exterior
# de casino de noche vale para casi cualquier cosa de este episodio.
CLIP_GENERICO = ("stock/casino_noche.mp4", 5)
SEPARACION_CLIPS = 5      # planos minimos entre un clip y el siguiente

# GRADE Y EFECTOS POR CAPITULO. El color es lo que le da al episodio su
# division en actos sin que haya que anunciarla: el capitulo de la licencia
# se ve frio y burocratico, el del dinero verde, el del giro rojo. Y los
# efectos ROTAN dentro de cada capitulo, porque el mismo polvo subiendo
# durante trece minutos deja de leerse como atmosfera y se lee como un
# filtro puesto encima.
# Cada capitulo mezcla DIRECCIONES, no solo texturas: algo que sube, algo que
# cae o cruza, y algo que ni se desplaza. Antes las paletas eran "polvo,
# bokeh, brasas" -las tres hacia arriba- y un capitulo entero salia con todo
# flotando en el mismo sentido, que se lee como un filtro pegado encima y no
# como aire.
CLIMA = {
 "GANCHO":           ("dorado_noche",       ["bokeh", "niebla", "destellos", "brasas"]),
 "CAP1_DOS_CASINOS": ("dorado_noche",       ["billetes", "bokeh", "humo", "destellos"]),
 "CAP2_EDIFICIO":    ("acero",              ["ceniza", "chispas", "niebla", "polvo"]),
 "CAP3_LICENCIA":    ("frio_institucional", ["polvo", "fuga_luz", "lluvia", "humo"]),
 "CAP4_SOCIO":       ("sepia_archivo",      ["humo", "polvo", "destellos", "fuga_luz"]),
 "CAP5_INGRESOS":    ("verde_dinero",       ["billetes", "destellos", "bokeh", "niebla"]),
 "CAP6_GIRO":        ("rojo_alerta",        ["brasas", "lluvia", "chispas", "humo"]),
 "CIERRE":           ("dorado_noche",       ["niebla", "brasas", "destellos", "bokeh"]),
}

# ROTULOS. Se disparan por palabra clave igual que los graficos, y el motor
# los cronometra contra la locucion. La primera palabra del rotulo TIENE que
# aparecer en la frase: es la que sirve de ancla.
# El estilo de entrada rota: si los dieciseis rotulos suben igual, el recurso
# se gasta en el minuto tres.
ROTULOS = [
 ("no depende",     dict(texto="NO DEPENDE DE NADA", px=96,  estilo="derecha")),
 ("matematica",     dict(texto="PURA MATEMATICA", px=104, estilo="escala")),
 ("cuanto cuesta",  dict(texto="¿CUÁNTO CUESTA?", px=118, estilo="baja")),
 ("no es tuyo",     dict(texto="NO ES TUYO", px=126, estilo="golpe")),
 ("cada dia",       dict(texto="TODOS LOS DÍAS", px=110, estilo="izquierda")),
 ("investigan",     dict(texto="TE INVESTIGAN", px=112, estilo="desenfoque")),
 ("para siempre",   dict(texto="PARA SIEMPRE", px=118, estilo="escala")),
 ("un solo error",  dict(texto="UN SOLO ERROR", px=116, estilo="golpe")),
 ("no falla nunca", dict(texto="NO FALLA NUNCA", px=112, estilo="izquierda")),
 ("perdieron",      dict(texto="PERDIERON", px=128, estilo="sube")),
 ("licencia",       dict(texto="LICENCIA", px=124, estilo="sube")),
 ("nunca va a ser tuyo", dict(texto="NUNCA ES TUYO", px=116, estilo="sube")),
 ("socio",          dict(texto="SOCIO OBLIGATORIO", px=96, estilo="derecha")),
 ("ventaja",        dict(texto="LA VENTAJA DE LA CASA", px=88, estilo="sube")),
 ("quitar",         dict(texto="TE LO PUEDEN QUITAR", px=92, estilo="baja")),
]

COMPOSICIONES = ["centrado", "izquierda", "cerca", "derecha",
                 "alto", "diagonal", "bajo", "lejos"]

# Al partir una escena larga, la segunda mitad cambia de movimiento: si no,
# el corte no se justifica y parece un fallo de montaje.
# ---------------------------------------------------------------------------
# MOTION GRAPHICS: se enganchan por lo que dice la locucion. Si la frase
# contiene la clave, la escena lleva ese grafico. Las cifras del guion son
# el argumento del video; dejarlas solo en la voz las desperdicia.
# ---------------------------------------------------------------------------
GRAFICOS = [
 ("1.236", dict(tipo="contador", valor=1236, sufijo="millones $",
                pie="perdidos en Nevada en un mes", y=0.30)),
 ("696",   dict(tipo="contador", valor=696, sufijo="millones $",
                pie="solo el Strip, en 28 dias", y=0.30)),
 ("sesenta y ciento cincuenta", dict(tipo="barras", y=0.5, sufijo=" M$", dec=0,
                items=[["Casino pequeno", 40], ["Resort", 150]])),
 ("diez y cuarenta", dict(tipo="contador", valor=40, sufijo="millones $",
                pie="un casino independiente", y=0.32)),
 ("quinientos cincuenta dolares", dict(tipo="contador", valor=550,
                sufijo="$ / pie cuadrado", pie="precio de hotel de cinco estrellas", y=0.30)),
 ("sesenta millones", dict(tipo="contador", valor=60, sufijo="millones $",
                pie="solo equipamiento y mobiliario", y=0.32)),
 ("setenta y cinco mil", dict(tipo="barras", y=0.5, sufijo=" $", dec=0,
                items=[["Tasa minima", 7500], ["Tasa maxima", 75000]])),
 ("cincuenta mil", dict(tipo="contador", valor=50000, sufijo="$",
                pie="lo que cuesta que te investiguen", y=0.32)),
 ("quinientos mil", dict(tipo="barras", y=0.5, sufijo=" k$", dec=0,
                items=[["Inicial", 500], ["Anual", 250], ["Deportivas", 250]])),
 ("seis coma setenta y cinco", dict(tipo="anillo", valor=6.75, sufijo="%",
                pie="se lleva Nevada", y=0.48)),
 ("ocho por ciento", dict(tipo="barras", y=0.5, sufijo="%",
                items=[["Casino", 8.0], ["Online", 15.0], ["Deportivas", 13.0]])),
 ("sesenta y dos coma cinco por ciento", dict(tipo="barras", y=0.5, sufijo="%",
                destacar={"Maryland": [255, 110, 86]},
                items=[["Nevada", 6.75], ["Nueva Jersey", 8.0], ["Maryland", 62.5]])),
 ("Sesenta y dos coma cinco.", dict(tipo="anillo", valor=62.5, sufijo="%",
                color=[255, 110, 86], pie="el tipo máximo de Maryland", y=0.48)),
 ("sesenta centavos", dict(tipo="reparto", valor=62.5, y=0.5,
                etiqueta_a="Estado", etiqueta_b="tu")),
 ("dos coma siete", dict(tipo="anillo", valor=2.7, sufijo="%",
                pie="ventaja de la casa en la ruleta europea", y=0.48)),
 ("quinientos ochenta y ocho", dict(tipo="contador", valor=10588,
                sufijo="millones $", pie="win acumulado en Nevada", y=0.30)),
 ("ciento cincuenta, un resort", dict(tipo="barras", y=0.5, sufijo=" M$", dec=0,
                items=[["Pequeno", 10], ["Decente", 40], ["Resort", 150]])),
]

# Entradas duras que se rotan por escena. Ninguna capa entra estatica.
ENTRADAS = ["golpe", "latigo_izq", "desplome", "rebote", "latigo_der", "golpe"]

PAREJA = {"push_in": "contra_der", "pull_out": "push_in",
          "estatico": "drift_izq", "drift_izq": "contra_izq",
          "drift_der": "contra_der", "contra_izq": "push_in",
          "contra_der": "pull_out", "subir": "estatico", "bajar": "push_in"}


def _con_entradas(lista, i):
    """Cada capa recibe una entrada dura y su escalon. Nunca 'ninguna'."""
    for j, c in enumerate(lista):
        c["entrada"] = ENTRADAS[(i + j) % len(ENTRADAS)]
        c["retardo"] = round(j * 0.09, 2)
    return lista


# ENCUADRES POR TROZO. Cuando una frase se parte en varios planos, repetir
# los mismos PNG con otro zoom NO es otro plano: es el mismo plano dos veces,
# y se nota. Un equipo de rodaje no repite la toma, la cubre desde otro sitio.
# Asi que cada trozo pide el MISMO sujeto con OTRO encuadre -mismo edificio,
# otro angulo- y ademas su propio fondo. Cuesta una imagen mas por trozo y es
# la diferencia entre un video montado y un video repetido.
# Cada fondo es propio de su escena, pero "variacion unica" a secas devuelve
# la misma foto con otra semilla. Pidiendo explicitamente OTRO punto de vista
# del mismo sitio, la sala se reconoce y el plano no se repite.
VARIACIONES = [
    "visto desde el centro de la sala",
    "visto desde un lateral, con la pared cerca a un lado",
    "visto desde el fondo, con la profundidad de la sala delante",
    "visto desde una esquina alta",
    "visto a la altura de la mesa, con el techo fuera de cuadro",
]

ANGULOS = [
    "",
    "visto en angulo de tres cuartos desde un lado",
    "visto en contrapicado corto desde abajo y muy cerca",
    "visto desde el lado contrario, mas de lejos",
]
SUFIJO = ["", "_b", "_c", "_d"]
VARIABLES = {"medio", "medio_lejos", "suelo", "figura", "frente", "frente_bajo"}


def apoyo_para(capas):
    """Que plano de apoyo necesita esta escena, si es que necesita alguno.

    Solo los edificios. Un objeto de mesa no lleva plano de apoyo: su propia
    imagen ya trae la superficie, y lo que necesita es que el FONDO sea una
    habitacion, cosa que se resuelve aparte.
    """
    if any(k in EDIFICIOS for k in capas if k):
        return "edificio"
    return None


def main():
    escenas, usados = [], collections.Counter()
    cupo = collections.Counter()
    beats_hechos = []
    apoyos_puestos = [0]
    uso_sujeto = collections.Counter()
    ultimo_clip = -99
    print(f'{"capitulo":22s} {"escenas":>8s} {"seg":>6s} {"objetivo":>9s}')
    total = 0

    for cap, objetivo, beats in GUION:
        grade, paleta_fx = CLIMA.get(cap, ("dorado_noche", ["polvo"]))
        primera_del_cap = len(escenas)
        suma = sum(b[1] for b in beats)
        total += suma
        marca = "  ok" if suma == objetivo else f"  <-- descuadra {suma-objetivo:+d}"
        print(f"{cap:22s} {len(beats):8d} {suma:6d} {objetivo:9d}{marca}")

        for i, (texto, dur, mov, capas) in enumerate(beats, 1):
            ident = f"{cap.lower()}_{i:02d}"

            # Un clip de stock donde encaje, con cupo y separacion.
            # El primer plano de un capitulo y cualquiera que lleve una
            # cifra o un rotulo NO pueden ser stock: son los que sostienen el
            # bloque, y ahi hace falta una composicion propia. Un clip es
            # para una frase de enlace.
            clip = None
            reservado = (i == 1
                         or any(c.lower() in texto.lower() for c, _ in GRAFICOS)
                         or any(c.lower() in texto.lower() for c, _ in ROTULOS))
            libre = (not reservado
                     and len(escenas) - ultimo_clip >= SEPARACION_CLIPS)
            for clave, ruta, tope in CLIPS:
                if libre and clave in texto.lower() and cupo[ruta] < tope:
                    clip = ruta
                    break
            if libre and not clip:
                ruta, tope = CLIP_GENERICO
                if cupo[ruta] < tope:
                    clip = ruta
            if clip:
                cupo[clip] += 1
                ultimo_clip = len(escenas)

            # ...y si no, la capa de apoyo que le falte para no flotar.
            # Si la frase se parte, el clip va en el SEGUNDO trozo: la frase
            # abre en plano compuesto -que es el que cuenta- y corta a
            # metraje real a mitad. Es como se monta una cortinilla de b-roll,
            # y evita que una idea empiece en stock.
            k_clip = 1 if (clip and math.ceil(dur / 4.0) > 1) else 0

            capas = [k for k in capas if k]
            fondos = {"cielo", "sala", "desierto", "despacho", "obra", "frio",
                      "boveda"}

            # Un objeto de mesa recortado sobre un cielo o sobre un fondo
            # abstracto no tiene donde estar: se le cambia el fondo por una
            # habitacion.
            if any(k in SOBRE_MESA for k in capas):
                for x, k in enumerate(capas):
                    if k in EXTERIORES:
                        capas[x] = INTERIORES[len(escenas) % len(INTERIORES)]
            # Y al reves: un EDIFICIO dentro de una sala de juego es una
            # maqueta encima de una mesa. Si el sujeto es un edificio, el
            # fondo tiene que ser de exterior.
            elif any(k in EDIFICIOS for k in capas):
                for x, k in enumerate(capas):
                    if k in INTERIORES:
                        capas[x] = FUERA[len(escenas) % len(FUERA)]

            # gente alrededor de la mesa
            if any(k in MESAS_DE_JUEGO for k in capas) and                     not any(A[k][0] == "figura" for k in capas):
                # DETRAS de la mesa, no delante: las capas se pintan en orden
                # y la ultima queda encima. Un crupier delante de la ruleta
                # seria un crupier de rodillas sobre el tapete.
                donde = next(x for x, k in enumerate(capas)
                             if k in MESAS_DE_JUEGO)
                gente = ["crupier",
                         ACOMPANA[len(escenas) % len(ACOMPANA)],
                         ACOMPANA[(len(escenas) + 2) % len(ACOMPANA)]]
                capas[donde:donde] = gente
                # y unas manos delante si la escena no traia primer plano
                if not any(A[k][0].startswith("frente") for k in capas):
                    capas.append(MANOS[len(escenas) % len(MANOS)])

            tipo = apoyo_para(capas)
            if tipo:
                variantes = APOYO[tipo]
                # se cuenta cuantas veces se ha puesto un apoyo, no cuantas
                # frases van: contando frases, dos escenas de edificio
                # separadas por una de interior caian en la misma paridad y
                # repetian vecinos
                elegida = variantes[apoyos_puestos[0] % len(variantes)]
                apoyos_puestos[0] += 1
                corte = 1 if capas and capas[0] in fondos else 0
                capas.insert(corte, elegida)
            # Rellenar hasta el minimo. El orden importa: primero algo
            # delante, que es lo que da profundidad, y despues gente, que es
            # lo que da escala.
            sitio = next((k for k in capas if k in RELLENO), None)
            if sitio and not clip:
                r = RELLENO[sitio]
                if not any(A[k][0].startswith("frente") for k in capas):
                    for cand in r["frente"]:
                        if cand not in capas:
                            capas.append(cand); break
                giro = len(escenas)
                for cand in r["gente"]:
                    if len(capas) >= MINIMO_CAPAS:
                        break
                    if cand in capas:
                        continue
                    # la gente va detras del sujeto, delante del fondo
                    capas.insert(1 if capas[0] in RELLENO else 0, cand)
                # y si aun falta, otro elemento de primer plano distinto
                for cand in r["frente"][::-1] if giro % 2 else r["frente"]:
                    if len(capas) >= MINIMO_CAPAS:
                        break
                    if cand not in capas:
                        capas.append(cand)

            beats_hechos.append(ident)

            def capas_de(j, ident_escena):
                # se mira cuantas veces lleva usado ese archivo para no
                # sacar la misma torre nueve veces en dos minutos
                nonlocal_uso = uso_sujeto
                """Las capas de UN trozo: fondo propio y sujeto en otro angulo."""
                out = []
                for key in capas:
                    rol, archivo, prompt = A[key]
                    if rol == "fondo":
                        archivo = f"fondo_{ident_escena}.png"
                        prompt = (f"{prompt}. "
                                  f"{VARIACIONES[len(escenas) % len(VARIACIONES)]}")
                    elif rol in VARIABLES:
                        # El indice de variante NO es el del trozo: es cuantas
                        # veces se ha usado ya ese sujeto en el episodio. Con
                        # el del trozo, un sujeto que aparece en nueve frases
                        # distintas salia nueve veces con el mismo encuadre.
                        v = (j + nonlocal_uso[archivo]) % len(SUFIJO)
                        nonlocal_uso[archivo] += 1
                        if v:
                            archivo = archivo.replace(".png", SUFIJO[v] + ".png")
                            prompt = f"{prompt}, {ANGULOS[v]}"
                    usados[key] += 1
                    out.append({"rol": rol, "archivo": archivo,
                                "prompt": prompt})
                return out

            lista = capas_de(0, ident)
            # Techo de 4 s. Una idea de 12 s se cuenta en tres planos, no en
            # uno largo: el dinamismo sale de la frecuencia de corte, no de
            # mover mas la camara dentro del mismo encuadre.
            k = max(1, int(math.ceil(dur / 4.0)))
            paso = dur / k
            m = mov
            trozos = []
            for j in range(k):
                trozos.append((round(paso, 2), m))
                m = PAREJA.get(m, "estatico")

            graf = None
            for clave, spec in GRAFICOS:
                if clave.lower() in texto.lower():
                    graf = dict(spec); break
            rot = None
            for clave, spec in ROTULOS:
                if clave.lower() in texto.lower():
                    rot = dict(spec); break

            escenas.append({
                "id": ident,
                "texto": texto,
                "duracion": trozos[0][0],
                "movimiento": trozos[0][1],
                "composicion": COMPOSICIONES[len(escenas) % len(COMPOSICIONES)],
                "grade": grade,
                "efectos": [paleta_fx[len(escenas) % len(paleta_fx)]],
                "capas": [] if (clip and k_clip == 0)
                         else _con_entradas(lista, len(escenas)),
            })
            if clip and k_clip == 0:
                escenas[-1]["clip"] = clip
            if graf:
                escenas[-1]["grafico"] = dict(graf, retardo=0.5,
                                              entrada="golpe")
            if rot:
                escenas[-1]["texto_pantalla"] = rot
            # Los trozos de un mismo plano son UNA idea contada en varios
            # encuadres, asi que van hilados: la camara no reinicia su
            # movimiento en cada corte, lo continua. Es la transicion
            # invisible, y es lo que evita que partir para ganar ritmo se
            # note como partir.
            # El hilo -la camara que cruza el corte sin reiniciarse- exige
            # que los dos planos compartan los mismos elementos, y ahora cada
            # trozo trae su propio fondo y su propio encuadre del sujeto. Una
            # panoramica continua sobre contenido distinto no es continuidad,
            # es un error. Asi que el constructor ya no los emite; el campo
            # "hilo" sigue en el motor para ponerlo a mano donde toque.
            # Su papel de tapar el corte lo hace el latigazo, que si funciona
            # entre planos distintos: para eso esta el desenfoque.
            hilado = False
            if hilado:
                escenas[-1]["hilo"] = ident
            for j, (d2, m2) in enumerate(trozos[1:], 1):
                escenas.append({
                    "id": f"{ident}{chr(97 + j)}",
                    "texto": texto,
                    "duracion": d2,
                    "movimiento": m2,
                    "composicion": COMPOSICIONES[len(escenas) % len(COMPOSICIONES)],
                    "grade": grade,
                    "efectos": [paleta_fx[len(escenas) % len(paleta_fx)]],
                    "capas": [] if (clip and j >= k_clip) else _con_entradas(
                        capas_de(j, f"{ident}{chr(97 + j)}"), len(escenas)),
                })
                if clip and j >= k_clip:
                    escenas[-1]["clip"] = clip
                    escenas[-1]["clip_desde"] = round(1.0 + 3.0 * (j - k_clip), 2)
                if hilado:
                    escenas[-1]["hilo"] = ident

        # Fin de capitulo: fundido a negro corto. Es la unica pausa del
        # episodio, y la que deja respirar antes del bloque siguiente.
        escenas[-1]["cierra_bloque"] = True

        # Un latigazo cada pocos planos dentro del capitulo, y solo donde no
        # rompe un hilo ni el cierre: barre la imagen y tapa el corte. Uno
        # cada cinco planos es un acento; uno en cada corte es un tic.
        for k in range(primera_del_cap, len(escenas) - 1):
            e, sig = escenas[k], escenas[k + 1]
            if e.get("hilo") or sig.get("hilo") or e.get("cierra_bloque"):
                continue
            if (k - primera_del_cap) % 5 == 3:
                e["latigo"] = "izq" if k % 2 else "der"

    guion = {
        "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
        "estilo": ESTILO,
        "escenas": escenas,
    }
    os.makedirs("proyecto", exist_ok=True)
    with open("proyecto/guion.json", "w", encoding="utf-8") as f:
        json.dump(guion, f, ensure_ascii=False, indent=2)

    print(f'\n{len(escenas)} escenas · {total}s ({total//60}:{total%60:02d})')
    import collections as _c
    print(f'{sum(1 for e in escenas if e.get("clip"))} escenas de clip | '
          f'{sum(1 for e in escenas if any(c["rol"]=="horizonte" for c in e["capas"]))} con plano de apoyo')
    print(f'{sum(1 for e in escenas if e.get("hilo"))} escenas hiladas | '
          f'{sum(1 for e in escenas if e.get("latigo"))} latigazos | '
          f'{sum(1 for e in escenas if e.get("grafico"))} graficos | '
          f'{sum(1 for e in escenas if e.get("texto_pantalla"))} rotulos')
    print("grades:  " + ", ".join(
        f"{k} x{v}" for k, v in _c.Counter(e["grade"] for e in escenas).most_common()))
    print("efectos: " + ", ".join(
        f"{k} x{v}" for k, v in _c.Counter(e["efectos"][0] for e in escenas).most_common()))
    png = {c["archivo"] for e in escenas for c in e["capas"]}
    print(f"{len(png)} PNG unicos para {sum(len(e['capas']) for e in escenas)} usos de capa")
    print("mas reutilizados:", ", ".join(
        f"{k} x{n}" for k, n in usados.most_common(6)))
    huerfanos = [k for k in A if k not in usados]
    if huerfanos:
        print("sin usar:", ", ".join(huerfanos))


if __name__ == "__main__":
    main()
