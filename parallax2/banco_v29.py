#!/usr/bin/env python3
"""
Guion visual del episodio 03 (el banco), estilo VOX.

    python3 banco.py

Saca dos cosas:
    proyecto_banco/guion.json     para el pipeline
    proyecto_banco/STORYBOARD.md  la tabla para leer y corregir a mano

Estructura de cada escena, segun el desglose del video de referencia:
    FONDO   papel, EL MISMO en las 120 escenas. Se genera una sola vez.
    MEDIO   el sujeto, recorte en blanco y negro con trazo rojo desplazado.
    FRENTE  la estructura, ilustracion plana a color, apoyada en el borde
            inferior, TAPA al sujeto de cintura para abajo.
    CODIGO  escenas sin ninguna imagen: tipografia y datos. Son casi la
            mitad, igual que en el video de referencia.
"""
import os, json, math, collections

# Paleta por nombre. Va pegada a todos los prompts para que las 40 piezas
# salgan de la misma gama sin depender de como interprete el modelo una
# descripcion de iluminacion.
PALETA = ("negro calido, hueso, azul tinta y verde billete apagado, "
          "con rojo teja como unico acento")

FONDO = ("f_papel.png", "textura de papel de periodico viejo, hueso claro, "
         "veladuras suaves y grano de imprenta, sin objetos, sin texto")

# ---------------------------------------------------------------------------
# BIBLIOTECA. id: (capa, archivo, prompt de contenido)
#   "medio"  -> se genera en blanco y negro y se pasa por semitono en local
#   "frente" -> ilustracion plana a color, se ancla abajo
# ---------------------------------------------------------------------------
A = {
 # --- sujetos (van detras, en semitono con trazo rojo) ---
 "cajero":    ("medio", "m_cajero.png",
   "cajera de banco tras un mostrador, de frente, encuadre de pecho para arriba"),
 "cola":      ("medio", "m_cola.png",
   "fila de ocho personas de espaldas esperando su turno, franja ancha"),
 "banquero":  ("medio", "m_banquero.png",
   "ejecutivo de banca en traje, de frente, brazos cruzados, de pecho para arriba"),
 "abogados":  ("medio", "m_abogados.png",
   "dos abogados de pie con carpetas bajo el brazo, de frente"),
 "inspector": ("medio", "m_inspector.png",
   "inspector con carpeta y gafas, de frente, expresion neutra, de pecho para arriba"),
 "plantilla": ("medio", "m_plantilla.png",
   "grupo de seis empleados de oficina de pie en fila, de frente"),
 "fundador":  ("medio", "m_fundador.png",
   "emprendedor de mediana edad mirando unos papeles, de pecho para arriba"),
 "familia":   ("medio", "m_familia.png",
   "pareja joven firmando un documento sentada, de frente"),
 "consultor": ("medio", "m_consultor.png",
   "consultor senalando una pizarra, de perfil, de pecho para arriba"),
 "guardia":   ("medio", "m_guardia.png",
   "guardia de seguridad de banco de pie, de frente, de pecho para arriba"),

 # --- estructuras y objetos (van delante, planos y a color) ---
 "oficina":   ("frente", "f_oficina.png",
   "fachada de una oficina bancaria de barrio con dos ventanales y puerta central"),
 "mostrador": ("frente", "f_mostrador.png",
   "mostrador largo de banco visto de frente, con tres puestos y mampara"),
 "atm":       ("frente", "f_atm.png",
   "cajero automatico empotrado en una pared, visto de frente"),
 "boveda":    ("frente", "f_boveda.png",
   "puerta circular de boveda acorazada con volante, vista de frente"),
 "regulador": ("frente", "f_regulador.png",
   "edificio institucional neoclasico con columnas y escalinata, vista frontal"),
 "torre":     ("frente", "f_torre.png",
   "rascacielos corporativo estrecho, vista frontal completa"),
 "servidor":  ("frente", "f_servidor.png",
   "armario rack de servidores con luces, visto de frente"),
 "terminal":  ("frente", "f_terminal.png",
   "terminal de ordenador de los anos ochenta con teclado, vista de tres cuartos"),
 "nube":      ("frente", "f_nube.png",
   "icono de nube conectada a tres servidores por lineas"),
 "balanza":   ("frente", "f_balanza.png",
   "balanza de dos platos, uno mucho mas bajo que el otro"),
 "llaves":    ("frente", "f_llaves.png",
   "manojo de tres llaves antiguas colgando de una anilla"),
 "candado":   ("frente", "f_candado.png",
   "candado cerrado grande con cadena"),
 "expediente":("frente", "f_expediente.png",
   "carpeta de expediente abultada con sello oficial y goma elastica"),
 "sello":     ("frente", "f_sello.png",
   "sello de caucho estampando la palabra en un documento"),
 "reloj":     ("frente", "f_reloj.png",
   "reloj de pared institucional redondo, visto de frente"),
 "calendario":("frente", "f_calendario.png",
   "calendario de pared de hojas arrancables"),
 "hucha":     ("frente", "f_hucha.png",
   "hucha de cerdito con una ranura, vista de perfil"),
 "billetes":  ("frente", "f_billetes.png",
   "fajo grueso de billetes con faja de papel"),
 "monedas":   ("frente", "f_monedas.png",
   "tres pilas de monedas de alturas muy distintas"),
 "paraguas":  ("frente", "f_paraguas.png",
   "paraguas abierto visto de frente"),
 "grieta":    ("frente", "f_grieta.png",
   "grieta irregular atravesando una pared lisa"),
 "cerrado":   ("frente", "f_cerrado.png",
   "puerta de cristal cerrada con un cartel colgado"),
 "escudo":    ("frente", "f_escudo.png",
   "escudo heraldico simple con una banda horizontal"),
 "engranaje": ("frente", "f_engranaje.png",
   "tres engranajes engranados de distinto tamano"),
 "libro":     ("frente", "f_libro.png",
   "libro de contabilidad abierto con dos columnas"),
 "obra":      ("frente", "f_obra.png",
   "andamio de obra delante de un local a medio construir"),
 "maletin":   ("frente", "f_maletin.png",
   "maletin de cuero cerrado, visto de frente"),
 "silla":     ("frente", "f_silla.png",
   "silla de oficina vacia, vista de frente"),
 "recibos":   ("frente", "f_recibos.png",
   "pinza de recibos con facturas ensartadas, vista de frente"),
 "tarta":     ("frente", "f_tarta.png",
   "grafico circular fisico con una porcion separada, vista de frente"),
 "regla":     ("frente", "f_regla.png",
   "regla metalica y escuadra cruzadas, vista de frente"),
 "vaso":      ("frente", "f_vaso.png",
   "vaso de agua lleno hasta un tercio, visto de frente"),
 "tijeras":   ("frente", "f_tijeras.png",
   "tijeras abiertas cortando una cinta, vista de frente"),
 "semaforo":  ("frente", "f_semaforo.png",
   "semaforo de tres luces, vista frontal"),
 "cinta":     ("frente", "f_cinta.png",
   "cinta metrica extendida y enrollada, vista de frente"),
 "pesa":      ("frente", "f_pesa.png",
   "pesa de gimnasio de una sola mano, vista de frente"),
 "cheque":    ("frente", "f_cheque.png",
   "cheque bancario relleno, visto de frente"),
}

# ---------------------------------------------------------------------------
# ENTRADAS estilo Vox. Todas con spring y rebasamiento, escalonadas.
#   pop       escala desde 0.72 con rebote. Es la entrada por defecto.
#   sube      entra desde debajo del borde inferior. Para las estructuras.
#   lateral   entra lanzada desde un lado. Para elementos que "llegan".
#   barrido   se descubre de izquierda a derecha. Para graficas y barras.
#   maquina   texto letra a letra. Solo para remates.
#   cae       cae desde arriba y asienta. Para lo que "se impone".
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# ESCENAS: (locucion, seg, tipo, [capas], grafico, entradas, transicion)
#   tipo:  capas | codigo
#   grafico: None o dict de motion graphics
# ---------------------------------------------------------------------------
def C(t, s, **kw):
    """
    Escena de codigo. Con `estruct` lleva ademas una estructura plana
    apoyada abajo: sirve para romper las rachas de escenas sin ninguna
    imagen, que leidas seguidas parecen un pase de diapositivas.
    """
    est = kw.get("estruct")
    return (t, s, "codigo" if not est else "capas", [est] if est else [],
            kw.get("g"), kw.get("e", "sube"), kw.get("x", "corte"))


def E(t, s, capas, **kw):
    return (t, s, "capas", capas, kw.get("g"), kw.get("e", "pop"),
            kw.get("x", "corte"))


GUION = [
("GANCHO", 60, [
 C("Un banco medio de Estados Unidos gana tres coma veintidos dolares al ano "
   "por cada cien que tiene prestados.", 7,
   g=dict(tipo="contador", valor=3.22, dec=2, sufijo="$", pie="por cada 100 $ prestados")),
 C("Tres coma veintidos. Ese es el margen.", 4,
   g=dict(tipo="frase_destacada", lineas=["Tres coma", "*veintidos*"]), e="maquina"),
 E("Y con ese margen se pagan las oficinas, las nominas, los sistemas, los "
   "abogados y los accionistas.", 8, ["plantilla", "oficina"], e="pop+sube"),
 C("Suena a poco.", 3, g=dict(tipo="frase_destacada", lineas=["Suena a *poco*."])),
 E("Y sin embargo, no hay ningun negocio con una cola mas larga de gente "
   "esperando para entrar.", 8, ["cola", "oficina"], e="lateral+sube"),
 C("Porque un banco no gana dinero con su dinero. Lo gana con el tuyo.", 7,
   g=dict(tipo="reparto", valor=100, etiqueta_a="tu dinero", etiqueta_b="suyo"),
   e="barrido"),
 E("Coge lo que tu depositas, se lo presta a otro mas caro, y se queda la "
   "diferencia.", 8, ["familia", "hucha"], e="pop+sube"),
 C("Ese es el negocio entero. Todo lo demas es decoracion.", 5,
   g=dict(tipo="frase_destacada", lineas=["Todo lo demas", "es *decoracion*."])),
 E("Asi que la pregunta se hace sola: cuanto cuesta montar uno.", 5,
   ["fundador", "oficina"], e="pop+sube"),
 E("Con un McDonald's era el dinero. Con un casino, la licencia.", 5,
   ["banquero", "llaves"], e="pop+cae"),
]),

("CAP1_DOS_BANCOS", 120, [
 E("Con un banco, el problema es que el dinero con el que trabajas no es "
   "tuyo. Nunca lo ha sido.", 8, ["cajero", "boveda"], e="pop+sube"),
 E("Cuando piensas en un banco, piensas en una oficina.", 7,
   ["cola", "oficina"], e="pop+sube"),
 E("Un mostrador, una cola, un cajero automatico en la fachada.", 8,
   ["cajero", "mostrador"], e="pop+sube"),
 E("Un cartel con el tipo de interes de las hipotecas.", 7, ["familia", "atm"],
   e="pop+lateral"),
 C("Eso no es el banco. Eso es la *tienda* del banco.", 5,
   g=dict(tipo="frase_destacada", lineas=["Eso es la *tienda*", "del banco."]), x="corte"),
 C("El banco de verdad es una hoja de calculo.", 5,
   g=dict(tipo="frase_destacada", lineas=["El banco es una", "*hoja de calculo*."])),
 E("A un lado, lo que la gente ha depositado. Al otro, lo que el banco ha "
   "prestado.", 9, ["banquero", "libro"], e="pop+sube", x="closer"),
 C("Y en medio, un margen muy fino que tiene que dar de comer a todo lo demas.",
   8, g=dict(tipo="reparto", valor=3.22, dec=2,
             etiqueta_a="margen", etiqueta_b="todo lo demas"), e="barrido"),
 C("Esa hoja tiene una regla que lo gobierna todo: no puedes prestar todo lo "
   "que te han dejado. Ni de lejos.", 9,
   g=dict(tipo="barras", sufijo="%", items=[["Depositado", 100], ["Prestable", 89]]),
   e="barrido"),
 E("Y esa regla no la pones tu.", 6, ["inspector", "regulador"], e="pop+cae"),
 E("Abrir una oficina nueva cuesta unos tres millones y medio de dolares.", 8,
   ["fundador", "obra"], e="pop+sube",
   g=dict(tipo="contador", valor=3.5, dec=1, sufijo="M $", pie="abrir una oficina")),
 C("Tarda cuatro anos en devolver lo invertido.", 7,
   g=dict(tipo="contador", valor=4, sufijo="anos", pie="hasta recuperar la inversion")),
 E("Mantenerla abierta cuesta unos cuatrocientos mil dolares al ano.", 8,
   ["plantilla", "mostrador"], e="pop+sube",
   g=dict(tipo="contador", valor=400, sufijo="mil $ / ano", pie="solo mantenerla abierta")),
 C("Entre nominas, alquiler, seguridad y mantenimiento.", 7,
   estruct="recibos", g=dict(tipo="barras", sufijo="%",
          items=[["Nominas", 52], ["Alquiler", 21], ["Seguridad", 15], ["Resto", 12]]),
   e="barrido"),
 C("Y las oficinas son solo el quince por ciento de los gastos de un banco.", 7,
   g=dict(tipo="anillo", valor=15, sufijo="%", pie="lo que pesan las oficinas")),
 C("Lo que tu ves cuando piensas en un banco es la parte mas barata del banco.",
   7, g=dict(tipo="frase_destacada", lineas=["Lo que ves es", "lo mas *barato*."]),
   e="maquina", x="fundido"),
 E("Vamos a la cara.", 4, ["banquero", "boveda"], e="pop+sube"),
]),

("CAP2_CAPITAL", 100, [
 E("Para abrir un banco nuevo en Estados Unidos hace falta capital inicial.", 6,
   ["fundador", "maletin"], e="pop+sube"),
 C("Y no es una cifra simbolica.", 4,
   g=dict(tipo="frase_destacada", lineas=["No es una cifra", "*simbolica*."])),
 C("En dos mil veintiseis, los reguladores esperan entre veintisiete y "
   "cincuenta millones de dolares.", 8,
   g=dict(tipo="barras", sufijo=" M$", dec=0,
          items=[["Minimo", 27], ["Habitual", 50]]), e="barrido"),
 C("En algunos estados basta con diez o quince millones si el modelo es "
   "pequeno y sencillo.", 7,
   estruct="monedas", g=dict(tipo="barras", sufijo=" M$", dec=0,
          items=[["Estado pequeno", 12], ["Media", 38], ["Nueva York", 50]]),
   e="barrido"),
 E("En el area metropolitana de Nueva York, la cifra empieza en cincuenta y "
   "sube.", 7, ["banquero", "torre"], e="pop+sube", x="closer"),
 C("Y ahora la parte que casi nadie entiende.", 3,
   g=dict(tipo="frase_destacada", lineas=["Y ahora lo que", "*nadie* entiende."]), e="maquina"),
 E("Ese dinero no es para gastarlo.", 4, ["fundador", "billetes"], e="pop+cae"),
 C("No es para comprar el edificio, ni los ordenadores, ni pagar sueldos.", 6,
   g=dict(tipo="barras", sufijo="", dec=0,
          items=[["Edificio", 0], ["Sistemas", 0], ["Sueldos", 0]]), e="barrido"),
 E("Ese dinero es un colchon. Esta ahi para absorber perdidas si los prestamos "
   "salen mal.", 8, ["banquero", "paraguas"], e="pop+sube"),
 C("Se queda quieto, en el balance, demostrando que el banco aguanta un golpe.",
   6, g=dict(tipo="frase_destacada", lineas=["Se queda *quieto*."])),
 E("Es como si para abrir un restaurante te pidieran treinta millones y te "
   "dijeran: no los toques.", 8, ["fundador", "candado"], e="pop+cae"),
 C("El capital no es una cifra fija: es un porcentaje de lo que prestas.", 5,
   g=dict(tipo="frase_destacada", lineas=["Cuanto mas prestas,", "mas *capital*."]), x="corte"),
 C("El minimo del capital de maxima calidad es el cuatro coma cinco por ciento "
   "de los activos ponderados por riesgo.", 8,
   estruct="vaso", g=dict(tipo="anillo", valor=4.5, sufijo="%", pie="minimo regulatorio")),
 C("Para considerarte bien capitalizado, la ratio de apalancamiento tiene que "
   "estar en el cinco por ciento.", 7,
   g=dict(tipo="anillo", valor=5.0, sufijo="%", pie="para estar bien capitalizado")),
 C("En la practica, la mayoria de los bancos van entre el ocho y el once por "
   "ciento. Muy por encima del minimo.", 8,
   estruct="regla", g=dict(tipo="barras", sufijo="%", destacar="Minimo legal",
          items=[["Minimo legal", 4.5], ["Banca real", 9.5]]), e="barrido"),
 E("Porque el que esta justo en el minimo es el que no sobrevive al primer "
   "susto.", 6, ["banquero", "grieta"], e="pop+lateral", x="fundido"),
]),

("CAP3_LICENCIA", 140, [
 E("Con el capital reunido, empieza lo dificil.", 4, ["fundador", "regulador"],
   e="pop+sube"),
 C("Un banco necesita una ficha bancaria. Y una ficha bancaria no se compra.", 6,
   g=dict(tipo="frase_destacada", lineas=["No se compra.", "Se *concede*."]), e="maquina"),
 E("La solicitud al fondo de garantia de depositos cuesta cinco mil dolares.", 7,
   ["abogados", "expediente"], e="pop+sube",
   g=dict(tipo="contador", valor=5000, sufijo="$", pie="tasa de solicitud")),
 C("No reembolsables.", 3, g=dict(tipo="frase_destacada", lineas=["No *reembolsables*."])),
 C("Cinco mil dolares. Para un negocio de treinta millones.", 6,
   estruct="cheque", g=dict(tipo="barras", sufijo=" $", dec=0,
          items=[["Tasa", 5000], ["Capital exigido", 30000000]]), e="barrido"),
 C("Parece un chiste, y lo es, porque la tasa no es el coste.", 5,
   g=dict(tipo="frase_destacada", lineas=["La tasa no es", "el *coste*."])),
 E("El coste es todo lo que hay que poner encima de la tasa.", 5,
   ["abogados", "expediente"], e="pop+cae", x="closer"),
 E("Solo los abogados que preparan la solicitud se llevan doscientos mil "
   "dolares o mas.", 8, ["abogados", "maletin"], e="pop+sube",
   g=dict(tipo="contador", valor=200, sufijo="mil $", pie="solo abogados")),
 E("Los consultores que escriben el plan de negocio, otros ciento cincuenta mil.",
   7, ["consultor", "libro"], e="pop+sube",
   g=dict(tipo="contador", valor=150, sufijo="mil $", pie="consultores")),
 C("Y eso es antes de tener un solo cliente.", 4,
   g=dict(tipo="frase_destacada", lineas=["Antes de tener", "*un solo cliente*."]), e="maquina"),
 C("Desde agosto de dos mil veintiseis, el regulador concede una autorizacion "
   "condicionada en ciento veinte dias.", 10,
   g=dict(tipo="contador", valor=120, sufijo="dias", pie="autorizacion condicionada")),
 C("Antes el proceso se alargaba mucho mas de un ano.", 6,
   estruct="calendario", g=dict(tipo="barras", sufijo=" dias", dec=0,
          items=[["Ahora", 120], ["Antes", 400]]), e="barrido"),
 C("Pero condicionada quiere decir condicionada.", 5,
   g=dict(tipo="frase_destacada", lineas=["*Condicionada*."]), e="maquina"),
 E("Un banco nuevo entra automaticamente en un periodo de supervision "
   "reforzada de tres anos.", 9, ["inspector", "reloj"], e="pop+cae",
   g=dict(tipo="contador", valor=3, sufijo="anos", pie="supervision reforzada")),
 C("Durante ese tiempo, los controles internos y las auditorias tienen que "
   "estar montados desde el primer dia.", 9,
   g=dict(tipo="barras", sufijo="", dec=0,
          items=[["Controles", 100], ["Auditoria", 100], ["Informes", 100]]),
   e="barrido"),
 E("Y las condiciones del seguro de depositos siguen encima durante siete "
   "anos.", 8, ["inspector", "escudo"], e="pop+sube",
   g=dict(tipo="contador", valor=7, sufijo="anos", pie="condiciones del seguro")),
 C("Siete anos vigilado. Con la licencia puesta a prueba todo el tiempo.", 7,
   g=dict(tipo="frase_destacada", lineas=["Siete anos", "*vigilado*."])),
 E("Y ahora la pregunta incomoda: que evaluan exactamente en esa solicitud.", 7,
   ["inspector", "sello"], e="pop+cae"),
 C("No evaluan solo tu plan de negocio. Te evaluan a ti.", 6,
   g=dict(tipo="frase_destacada", lineas=["Te evaluan", "*a ti*."]), e="maquina"),
 E("De donde sale cada dolar que has puesto. Quienes son tus socios. Que has "
   "hecho antes.", 10, ["fundador", "expediente"], e="pop+sube"),
 C("No hay presuncion de inocencia. La carga de la prueba es tuya.", 8,
   g=dict(tipo="frase_destacada", lineas=["La carga de la", "prueba es *tuya*."]),
   x="fundido"),
]),

("CAP4_SOCIO", 140, [
 E("Supongamos que la consigues. Estas dentro. Abres las puertas.", 9,
   ["plantilla", "oficina"], e="pop+sube"),
 C("Enhorabuena: acabas de meter un socio que no ha puesto un dolar y que no "
   "se va a ir nunca.", 9,
   g=dict(tipo="frase_destacada", lineas=["Un socio que", "no se va *nunca*."]), e="maquina"),
 E("El regulador no cobra un porcentaje de tus beneficios como haria un socio "
   "normal.", 10, ["inspector", "regulador"], e="pop+cae"),
 C("Cobra de otra forma: en trabajo que tienes que hacer y que no produce nada.",
   8, g=dict(tipo="frase_destacada", lineas=["Trabajo que", "no *produce* nada."])),
 C("En los bancos pequenos, el cumplimiento se lleva el ocho coma siete por "
   "ciento de los gastos que no son intereses.", 10,
   estruct="tarta", g=dict(tipo="anillo", valor=8.7, sufijo="%", pie="cumplimiento en banca pequena")),
 C("En los grandes, el dos coma nueve.", 6,
   g=dict(tipo="barras", sufijo="%", destacar="Banco pequeno",
          items=[["Banco pequeno", 8.7], ["Banco grande", 2.9]]), e="barrido"),
 C("Leelo otra vez.", 3, estruct="semaforo", g=dict(tipo="frase_destacada", lineas=["*Tres veces* mas."]),
   e="maquina"),
 E("El banco pequeno paga tres veces mas que el grande por cumplir exactamente "
   "las mismas normas.", 10, ["banquero", "balanza"], e="pop+cae", x="closer"),
 C("En personal es todavia mas claro: entre el once y el quince coma cinco por "
   "ciento del gasto en nominas.", 10,
   g=dict(tipo="barras", sufijo="%", destacar="Pequeno",
          items=[["Pequeno", 15.5], ["Grande", 9.5]]), e="barrido"),
 E("Y en los bancos por debajo de mil millones, solo el blanqueo se come entre "
   "el quince y el veinte por ciento del presupuesto.", 11,
   ["plantilla", "expediente"], e="pop+sube",
   g=dict(tipo="anillo", valor=20, sufijo="%", pie="solo normativa antiblanqueo")),
 C("Esa es la trampa del negocio bancario, y es puramente matematica.", 7,
   g=dict(tipo="frase_destacada", lineas=["La trampa es", "*matematica*."])),
 C("Las normas son fijas. Los costes de cumplirlas tambien.", 7,
   estruct="cinta", g=dict(tipo="barras", sufijo="", dec=0,
          items=[["Coste normativo", 100], ["Coste normativo", 100]]), e="barrido"),
 C("Asi que cuanto mas pequeno eres, mas pesan.", 6,
   g=dict(tipo="frase_destacada", lineas=["Cuanto mas pequeno,", "mas *pesan*."])),
 E("No es que el regulador tenga mania a los bancos pequenos.", 7,
   ["inspector", "engranaje"], e="pop+lateral"),
 C("Es que el coste de cumplir no baja cuando tu eres pequeno. Es el mismo, y "
   "lo pagas con menos ingresos.", 10,
   g=dict(tipo="reparto", valor=8.7, dec=1,
          etiqueta_a="cumplir", etiqueta_b="el negocio"), e="barrido"),
 E("Por eso los bancos pequenos desaparecen.", 6, ["silla", "cerrado"],
   e="pop+sube"),
 E("No los cierran: se venden, porque el unico modo de que esos costes cuadren "
   "es tener mas volumen.", 11, ["banquero", "torre"], e="pop+sube", x="fundido"),
]),

("CAP5_INGRESOS", 100, [
 C("Vamos a los numeros buenos, porque los hay.", 5,
   g=dict(tipo="frase_destacada", lineas=["Los numeros", "*buenos*."])),
 C("El margen de intermediacion medio de la banca estadounidense esta en el "
   "tres coma veintidos por ciento.", 9,
   g=dict(tipo="anillo", valor=3.22, dec=2, sufijo="%", pie="margen de intermediacion")),
 C("El rendimiento medio de los prestamos, en el seis coma cincuenta y uno.", 7,
   estruct="pesa", g=dict(tipo="contador", valor=6.51, dec=2, sufijo="%", pie="rendimiento de los prestamos")),
 C("Llego a tocar el siete coma trece a finales de dos mil veinticuatro y lleva "
   "bajando desde entonces.", 9,
   g=dict(tipo="barras", sufijo="%", destacar="2024",
          items=[["2024", 7.13], ["Hoy", 6.51]]), e="barrido"),
 E("La diferencia entre lo que cobras por prestar y lo que pagas por los "
   "depositos: ahi esta todo el negocio.", 10, ["banquero", "balanza"],
   e="pop+cae", x="closer"),
 C("Y a esa cuenta hay que restarle la maquinaria.", 5,
   g=dict(tipo="frase_destacada", lineas=["Restale la", "*maquinaria*."])),
 E("Un sistema informatico central para un banco pequeno cuesta entre "
   "doscientos setenta y cinco mil y ochocientos mil dolares.", 11,
   ["consultor", "servidor"], e="pop+sube",
   g=dict(tipo="barras", sufijo=" mil$", dec=0,
          items=[["Minimo", 275], ["Maximo", 800]])),
 E("Mantener cada cuenta en un sistema antiguo cuesta entre cuarenta y ochenta "
   "dolares al ano.", 9, ["cajero", "terminal"], e="pop+sube",
   g=dict(tipo="contador", valor=80, sufijo="$ / cuenta", pie="sistema antiguo")),
 E("En uno moderno en la nube, entre cuatro y quince.", 7, ["consultor", "nube"],
   e="pop+lateral",
   g=dict(tipo="barras", sufijo=" $", dec=0, destacar="Antiguo",
          items=[["Antiguo", 80], ["Nube", 15]])),
 C("Esa diferencia, multiplicada por cien mil cuentas, es la diferencia entre "
   "ganar dinero y no ganarlo.", 10,
   g=dict(tipo="contador", valor=6500000, sufijo="$ / ano", pie="la diferencia, x100.000 cuentas")),
 E("Por eso los bancos se pasan siete anos migrando sistemas que funcionan.", 9,
   ["plantilla", "servidor"], e="pop+sube"),
 C("No es capricho tecnologico: es que el coste por cuenta decide si el margen "
   "del tres coma veintidos da o no da.", 9,
   g=dict(tipo="reparto", valor=3.22, dec=2,
          etiqueta_a="margen", etiqueta_b="coste"), e="barrido", x="fundido"),
]),

("CAP6_GIRO", 80, [
 C("Y ahora la parte que cambia todo lo anterior.", 4,
   g=dict(tipo="frase_destacada", lineas=["Lo que cambia", "*todo*."]), e="maquina"),
 E("Has puesto treinta millones. Has conseguido la licencia. Has montado los "
   "sistemas.", 8, ["fundador", "boveda"], e="pop+sube"),
 E("Has contratado a la plantilla, has abierto las oficinas.", 6,
   ["plantilla", "oficina"], e="pop+sube"),
 C("Nada de eso te hace dueno del dinero que mueves.", 4,
   g=dict(tipo="frase_destacada", lineas=["Nada de eso te", "hace *dueno*."])),
 E("Los depositos son de los clientes. Tu los custodias.", 6,
   ["familia", "hucha"], e="pop+sube"),
 C("Puedes prestarlos, y de ahi sacas el margen, pero no son tuyos ni un "
   "segundo.", 7, g=dict(tipo="reparto", valor=100,
                         etiqueta_a="de los clientes", etiqueta_b="tuyo"), e="barrido"),
 C("Y el porcentaje que puedes prestar tampoco lo decides tu. Lo decide un "
   "ratio que escribio otro.", 9,
   g=dict(tipo="anillo", valor=4.5, sufijo="%", pie="lo decide otro")),
 E("Lo que de verdad tienes es un permiso para usar dinero ajeno dentro de "
   "unos limites que no controlas.", 9, ["banquero", "llaves"], e="pop+cae",
   x="closer"),
 E("Y ese permiso se puede retirar.", 4, ["inspector", "candado"], e="pop+cae"),
 E("Cuando un banco se queda sin liquidez, el regulador no negocia.", 6,
   ["inspector", "regulador"], e="pop+sube"),
 E("Interviene un viernes por la tarde, y el lunes el banco ya tiene otro "
   "dueno o ya no existe.", 10, ["guardia", "cerrado"], e="pop+sube",
   g=dict(tipo="contador", valor=48, sufijo="horas", pie="de viernes a lunes")),
 C("No hay concurso de acreedores. No hay meses de tribunales. Un fin de "
   "semana.", 7, g=dict(tipo="frase_destacada", lineas=["Un *fin de semana*."]),
   e="maquina", x="fundido"),
]),

("CIERRE", 40, [
 C("Entonces, cuanto cuesta tener un banco.", 4,
   g=dict(tipo="frase_destacada", lineas=["Cuanto cuesta", "tener un *banco*."])),
 C("Entre veintisiete y cincuenta millones de capital que no puedes tocar.", 7,
   estruct="monedas", g=dict(tipo="barras", sufijo=" M$", dec=0,
          items=[["Capital", 50], ["Oficina", 3.5], ["Abogados", 0.35],
                 ["Sistemas", 0.8]]), e="barrido"),
 C("Y despues, para siempre: un ocho coma siete por ciento de tus gastos "
   "dedicado a demostrar que cumples.", 9,
   g=dict(tipo="anillo", valor=8.7, sufijo="%", pie="para siempre")),
 C("A cambio, tres coma veintidos dolares al ano por cada cien prestados.", 7,
   estruct="hucha", g=dict(tipo="contador", valor=3.22, dec=2, sufijo="$", pie="por cada 100 prestados")),
 E("El negocio funciona. Lleva funcionando siglos. Pero solo si aceptas la "
   "condicion.", 8, ["banquero", "boveda"], e="pop+sube"),
 C("En un banco tu no eres el dueno del dinero. Eres el responsable del dinero "
   "de otros.", 5, g=dict(tipo="titular",
                          lineas=["No eres el dueno.", "Eres el *responsable*."]),
   e="maquina", x="fundido"),
]),
]

# ---------------------------------------------------------------------------
# ELEMENTOS DE CODIGO. Son capas de pleno derecho pero NO son imagenes: se
# dibujan en el render. Es lo que permite llegar a cinco o siete capas por
# escena sin disparar el numero de PNG a generar.
# ---------------------------------------------------------------------------
BANDAS = ["banda_inferior", "banda_lateral", "bloque_esquina"]
MARCAS = ["circulo_rotulador", "flecha", "subrayado", "corchete",
          "tachado", "asterisco", "bocadillo"]
ANCLAS = ["etiqueta_capitulo", "pie_fuente", "numero_escena"]

CROMA = ("sobre un fondo verde croma liso y uniforme, de un solo tono plano, "
         "sin degradado, sin sombra proyectada sobre el fondo, sin suelo")

# CORRECCION IMPORTANTE. Medido sobre los fotogramas del canal de
# referencia: la densidad de linea negra dura es del 0,3 al 3,9 %. Eso es
# FOTOGRAFIA RECORTADA, no ilustracion vectorial. Pedir "vector limpio,
# contorno marcado" devuelve dibujo de libro de colorear, con un 9-12 % de
# linea dura, que es lo que ha salido.
#
#   MEDIO  -> foto en blanco y negro, y el semitono se aplica en local
#   FRENTE -> foto A COLOR recortada. El contraste entre el sujeto en
#             blanco y negro y la estructura a color es la jerarquia
#             visual del estilo.
#   Vector plano SOLO para iconos pequenos (barril, escudo, flecha).
ENCUADRE = {
 "medio":  ("fotografia real en blanco y negro, alto contraste, sujeto "
            "recortado, sin dibujo ni contorno dibujado"),
 "frente": ("fotografia real a color, recortada, iluminacion neutra y "
            "uniforme, sin dibujo, sin contorno dibujado, sin estilo vector"),
 "icono":  ("icono plano de dos colores, contorno grueso, muy simple"),
 "fondo":  "textura plana, sin objetos, sin texto",
}
# los pocos elementos que SI son vectoriales
ICONOS = {"escudo", "balanza", "engranaje", "semaforo", "nube", "tarta",
          "regla", "cinta", "pesa"}


def prompt(clave):
    capa, arch, txt = A[clave]
    enc = ENCUADRE["icono"] if clave in ICONOS else ENCUADRE[capa]
    return f"{txt}. {enc}. {CROMA}. Paleta: {PALETA}."


# Cuando la escena no tiene ni sujeto ni estructura, el texto ES la imagen
# y tiene que ocupar el cuadro. Un titular al 20% del ancho sobre papel
# vacio no es un plano, es una diapositiva a medio hacer.
MAQUETA_TEXTO = dict(w=0.72, h=0.34, x=0.42, y=0.40, px_rel=0.15)


def caja(rol, enc, solo_texto=False, sin_sujeto=False):
    """Coordenadas literales de la capa, en fracciones del lienzo."""
    m = dict(MAQUETA[enc])
    if sin_sujeto:
        # sin sujeto detras, la estructura tiene que llenar el hueco o el
        # plano queda medio vacio
        m["frente_w"] = min(1.25, m["frente_w"] * 1.30)
        m["frente_h"] = min(0.78, m["frente_h"] * 1.45)
    if solo_texto and rol in ("grafico", "titular"):
        return dict(x=MAQUETA_TEXTO["x"], y=MAQUETA_TEXTO["y"],
                    w=MAQUETA_TEXTO["w"], h=MAQUETA_TEXTO["h"],
                    px_rel=MAQUETA_TEXTO["px_rel"], anclaje="centro")
    if solo_texto and rol == "marca":
        return dict(x=0.5, y=0.74, w=0.52, anclaje="centro")
    if rol == "fondo":
        return dict(x=0.5, y=0.5, w=1.0, anclaje="centro")
    if rol == "banda":
        return dict(x=0.5, y=1.0, w=1.0, h=0.14, anclaje="abajo")
    if rol == "frente":
        return dict(x=0.5 + m["frente_dx"], y=1.02, w=m["frente_w"],
                    h=m["frente_h"], anclaje="abajo")
    if rol == "medio":
        # el sujeto se apoya DENTRO de la estructura: su base cae por
        # debajo del borde superior del primer plano, que es lo que le
        # tapa de cintura para abajo
        base = 1.0 - m["frente_h"] * 0.62
        return dict(x=0.5 + m["medio_dx"], y=base, h=m["medio_h"],
                    anclaje="abajo")
    if rol in ("grafico", "titular"):
        lado = 0.30 if m["texto_x"] == "izq" else 0.70
        return dict(x=lado, y=m["texto_y"] + 0.14, w=0.44, anclaje="centro")
    if rol == "marca":
        lado = 0.72 if m["texto_x"] == "izq" else 0.28
        return dict(x=lado, y=0.30, w=0.20, anclaje="centro")
    if rol == "ancla":
        return dict(x=0.06, y=0.06, w=0.16, anclaje="arriba_izq")
    return dict(x=0.5, y=0.5, w=1.0, anclaje="centro")


def cobertura(capas, enc, solo_texto=False, sin_sujeto=False):
    """Estimacion del area cubierta. Si baja del 55%, la escena esta vacia."""
    m = dict(MAQUETA[enc])
    if sin_sujeto:
        m["frente_w"] = min(0.98, m["frente_w"] * 1.18)
        m["frente_h"] = min(0.60, m["frente_h"] * 1.22)
    a = 0.0
    if any(c["rol"] == "frente" for c in capas):
        a += m["frente_w"] * m["frente_h"] * 0.72
    if any(c["rol"] == "medio" for c in capas):
        a += m["medio_h"] * 0.34
    if any(c["rol"] == "marca" for c in capas) and not solo_texto:
        a += 0.03
    if any(c["rol"] == "grafico" for c in capas):
        a += MAQUETA_TEXTO["w"] * MAQUETA_TEXTO["h"] * 1.45 if solo_texto else 0.10
    return round(min(1.0, a), 2)


# Tamano de fuente como fraccion del ALTO del lienzo, y cuantas lineas
# caben. Sin estos tres numeros el texto se sale del cuadro o se monta
# encima de una capa, que es exactamente lo que ha pasado.
# max_chars calculado, no inventado: con Poppins Bold un caracter ocupa
# ~0.55 de su altura. caracteres = (ancho_caja / (px * 0.55)) * lineas.
TIPO = {
 "titular_grande": dict(px_rel=0.090, lineas=2, max_chars=38),
 "titular":        dict(px_rel=0.060, lineas=3, max_chars=62),
 "titular_lateral":dict(px_rel=0.040, lineas=4, max_chars=70),
 "dato_grande":    dict(px_rel=0.20,  lineas=1, max_chars=12),
 "dato":           dict(px_rel=0.10,  lineas=1, max_chars=16),
 "pie":            dict(px_rel=0.030, lineas=2, max_chars=58),
}


def partir_frase(txt, n):
    """
    Reparte la locucion entre los planos en los que se ha troceado.
    Cada plano lleva SU trozo de frase, no la frase entera cortada por la
    mitad ni la misma repetida: el texto sigue a la voz.
    """
    t = txt.strip()
    if n <= 1:
        return [t]
    # se corta por puntuacion real, y si no hay, por conectores
    import re
    piezas = [x.strip() for x in re.split(r"(?<=[.;:])\s+", t) if x.strip()]
    if len(piezas) < n:
        piezas = [x.strip() for x in re.split(r",\s+", t) if x.strip()]
    if len(piezas) < n:
        piezas = [x.strip() for x in re.split(r"\s+(?=y |que |pero |porque )", t)
                  if x.strip()]
    if len(piezas) < n:                       # reparto por palabras
        pal = t.split()
        k = max(1, len(pal) // n)
        piezas = [" ".join(pal[i:i + k]) for i in range(0, len(pal), k)]
    # agrupa hasta dejar exactamente n
    while len(piezas) > n:
        i = min(range(len(piezas) - 1),
                key=lambda j: len(piezas[j]) + len(piezas[j + 1]))
        piezas[i:i + 2] = [piezas[i] + " " + piezas[i + 1]]
    while len(piezas) < n:
        piezas.append(piezas[-1])
    return piezas


def estilo_texto(hueco, ancho):
    """El tamano depende del hueco: uno estrecho no admite titular grande."""
    if hueco == "dato":
        return dict(TIPO["dato_grande" if ancho >= 0.60 else "dato"])
    if ancho >= 0.66:
        return dict(TIPO["titular_grande"])
    if ancho >= 0.44:
        return dict(TIPO["titular"])
    return dict(TIPO["titular_lateral"])


def recortar_frase(txt, max_chars):
    """Corta por la frase, no por caracteres sueltos."""
    t = txt.strip()
    if len(t) <= max_chars:
        return t
    for sep in (". ", "; ", ", ", " y ", " que ", " "):
        cortes = t.split(sep)
        acc = ""
        for c in cortes:
            cand = (acc + sep + c).strip(sep + " ") if acc else c
            if len(cand) > max_chars:
                break
            acc = cand
        if 12 <= len(acc) <= max_chars:
            return acc.rstrip(" ,;.") + ("." if sep == ". " else "")
    return t[:max_chars - 1].rsplit(" ", 1)[0] + "…"


def rect(c):
    b = c["caja"]; w = b.get("w", 0.26); h = b.get("h", 0.30)
    an = b.get("anclaje", "centro")
    y0 = b["y"] - h if an == "abajo" else (b["y"] if an == "arriba_izq"
                                           else b["y"] - h / 2)
    return (b["x"] - w / 2, y0, b["x"] + w / 2, y0 + h)


def solapa(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    ar = (a[2] - a[0]) * (a[3] - a[1])
    return (ix * iy / ar) if ar else 0.0


def separar_texto(L):
    """
    El texto no puede montarse encima de una imagen. Si se pisan mas de un
    15%, el bloque de texto se va al hueco libre mas grande del cuadro.
    Es lo que fallaba: el titular caia sobre la boveda y no se leia nada.
    """
    imgs = [rect(c) for c in L if c["tipo_capa"] == "imagen"
            and c["rol"] != "fondo"]
    if not imgs:
        return L
    for c in L:
        if c["rol"] not in ("titular", "grafico"):
            continue
        # las marcas de rotulador se recolocan DESPUES, alrededor del texto
        r = rect(c)
        if max((solapa(r, m) for m in imgs), default=0) <= 0.15:
            continue
        w0 = c["caja"].get("w", 0.4); h0 = c["caja"].get("h", 0.16)
        mejor = None
        # Primero se prueba a moverlo. Si no cabe en ningun hueco libre, se
        # ENCOGE: mas vale un titular pequeno legible que uno grande encima
        # de la cara del sujeto.
        suelo = 0.042 / max(c["caja"].get("px_rel", 0.06), 1e-6)
        for escala in [e_ for e_ in (1.0, 0.86, 0.74, 0.64, 0.56)
                       if e_ >= min(1.0, suelo)] or [max(suelo, 0.56)]:
            w, h = w0 * escala, h0 * max(escala, 0.7)
            for cx in (0.24, 0.50, 0.76, 0.32, 0.68):
                for cy in (0.14, 0.24, 0.36, 0.50):
                    if cx - w / 2 < 0.03 or cx + w / 2 > 0.97:
                        continue
                    cand = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                    if max((solapa(cand, m) for m in imgs), default=0) <= 0.10:
                        mejor = (cx, cy, w, h, escala)
                        break
                if mejor:
                    break
            if mejor:
                break
        if mejor:
            cx, cy, w, h, escala = mejor
            c["caja"].update(x=cx, y=cy, w=round(w, 3), h=round(h, 3),
                             anclaje="centro")
            if escala < 1.0:
                c["caja"]["px_rel"] = round(c["caja"]["px_rel"] * escala, 4)
                c["caja"]["max_chars"] = max(18, int(c["caja"]["max_chars"] * escala))
                if c.get("texto"):
                    c["texto"] = recortar_frase(c["texto"], c["caja"]["max_chars"])
            c["reubicado"] = True

    # la marca acompana al texto: se pega justo debajo del bloque, nunca
    # encima de una imagen ni encima de la propia frase
    txt = next((c for c in L if c["rol"] == "titular"), None)
    for c in L:
        if c["rol"] != "marca" or not txt:
            continue
        b, t = c["caja"], txt["caja"]
        b["x"] = t["x"]
        b["y"] = min(0.92, t["y"] + t.get("h", 0.16) / 2 + 0.06)
        b["anclaje"] = "centro"
        if max((solapa(rect(c), m) for m in imgs), default=0) > 0.10:
            b["y"] = max(0.06, t["y"] - t.get("h", 0.16) / 2 - 0.05)
    return L


def pila_arq(capas, graf, ent, i, cap, arq, texto=""):
    """Pila construida desde el arquetipo: cada capa en su hueco."""
    H = ARQUETIPOS[arq]["huecos"]
    ents = ent.split("+")
    L = [{"rol": "fondo", "archivo": FONDO[0], "tipo_capa": "imagen",
          "hueco": "fondo", "caja": dict(x=0.5, y=0.5, w=1.0, anclaje="centro"),
          "entrada": "ninguna", "retardo": 0.0, "prompt": FONDO[1]}]

    for k, (clave, hueco) in enumerate(repartir(arq, capas)):
        capa, arch, _ = A[clave]
        L.append({"rol": capa, "archivo": arch, "clave": clave,
                  "funcion": funcion_de(clave), "hueco": hueco,
                  "caja": dict(H[hueco]), "tipo_capa": "imagen",
                  "prompt": prompt(clave),
                  "tratamiento": "semitono+trazo" if capa == "medio"
                                 else "color_recorte",
                  "entrada": ents[min(k, len(ents) - 1)],
                  "retardo": round(0.12 * (k + 1), 2)})

    # frase_destacada no es un grafico aparte: convierte el titular en
    # titular grande y le pasa sus lineas con los asteriscos de acento.
    destacada = None
    if graf and graf.get("tipo") == "frase_destacada":
        destacada = " ".join(graf.get("lineas", []))
        graf = None
    if graf and "dato" in H:
        cj = dict(H["dato"])
        cj.update(estilo_texto("dato", cj.get("w", 0.3)))
        L.append({"rol": "grafico", "tipo_capa": "codigo", "hueco": "dato",
                  "forma": graf["tipo"], "datos": graf, "caja": cj,
                  "entrada": "pop", "retardo": round(0.12 * (len(L)), 2)})
    # NO todas las escenas llevan texto. En la referencia, de siete planos
    # solo cuatro tienen tipografia, y los que la tienen la tienen GRANDE.
    # Poner una frase pequena en cada plano es lo que produce ese goteo de
    # texto de 40 px que no se lee y ensucia el encuadre.
    frase_util = (destacada or "").strip() or texto.strip()
    merece = (destacada is not None                       # remate marcado
              or arq == "dato_pleno"                      # la frase ES el plano
              or len(frase_util) <= 42)                   # cabe grande
    if "titular" in H and merece:
        cj = dict(H["titular"])
        est = estilo_texto("titular", cj.get("w", 0.4))
        if destacada:
            est = dict(TIPO["titular_grande"])
            cj["y"] = min(cj["y"], 0.42)
            cj["w"] = max(cj.get("w", 0.4), 0.72)
            cj["h"] = max(cj.get("h", 0.16), 0.24)
        # si el hueco es bajo, no cabe un titular grande por ancho que sea
        elif cj.get("h", 0.2) < 0.18 and est["px_rel"] > 0.062:
            est = dict(TIPO["titular"])
        cj.update(est)
        bruto = destacada or texto
        frase = recortar_frase(bruto, est["max_chars"])
        L.append({"rol": "titular", "tipo_capa": "codigo", "hueco": "titular",
                  "forma": "frase_destacada" if destacada else "frase",
                  "texto": frase, "caja": cj,
                  "entrada": "sube", "retardo": round(0.12 * (len(L)), 2)})
    for h in ("marca_a", "pie"):
        if h in H and len(L) < 6:
            L.append({"rol": "marca", "tipo_capa": "codigo", "hueco": h,
                      "forma": MARCAS[(i + len(L)) % len(MARCAS)],
                      "caja": dict(H[h]), "entrada": "trazo", "retardo": 0.5})
    L.append({"rol": "ancla", "tipo_capa": "codigo", "hueco": "esquina",
              "forma": ANCLAS[i % len(ANCLAS)],
              "caja": dict(x=0.06, y=0.06, w=0.16, anclaje="arriba_izq"),
              "texto": cap.split("_")[0].upper(),
              "entrada": "fundido", "retardo": 0.04})
    visibles = [c for c in L if c["rol"] in ("medio", "frente", "grafico",
                                             "titular")]
    if not visibles:
        cj = dict(x=0.5, y=0.44, w=0.78, h=0.24, anclaje="centro")
        cj.update(TIPO["titular_grande"])
        L.append({"rol": "titular", "tipo_capa": "codigo", "hueco": "rescate",
                  "forma": "frase", "caja": cj,
                  "texto": recortar_frase(texto, 46),
                  "entrada": "sube", "retardo": 0.2})
    L = separar_texto(L)
    for k, c in enumerate(L):
        c["id"] = f"l{k}"
    while len(L) < 5:
        L.append({"rol": "acabado", "tipo_capa": "codigo", "id": f"l{len(L)}",
                  "forma": ["rejilla", "vineta", "grano"][len(L) % 3],
                  "caja": dict(x=0.5, y=0.5, w=1.0, anclaje="centro"),
                  "entrada": "ninguna", "retardo": 0.0})
    return L


def pila(ident, capas, graf, ent, i, cap, enc, solo_texto=False,
         sin_sujeto=False):
    """
    Devuelve la pila completa de la escena. Minimo cinco capas siempre:
        1 fondo de papel (bloqueado)
        2 banda o bloque de color            <- codigo
        3 sujeto en semitono con trazo rojo  <- imagen (si la escena la lleva)
        4 estructura plana a color abajo     <- imagen (si la escena la lleva)
        5 marca de rotulador                 <- codigo
        6 etiqueta o pie                     <- codigo
        7 motion graphic                     <- codigo
    Las escenas sin imagenes llegan igual a cinco con las capas de codigo.
    """
    ents = ent.split("+")
    L = [{"rol": "fondo", "archivo": FONDO[0], "tipo_capa": "imagen",
          "entrada": "ninguna", "retardo": 0.0, "prompt": FONDO[1],
          "caja": caja("fondo", enc, solo_texto, sin_sujeto)}]
    # Sin banda decorativa. En la referencia no hay ninguna franja de
    # adorno: lo que ancla el borde inferior es SIEMPRE contenido (el mar,
    # el tejado del templo, el tanque). Una raya de color abajo convierte
    # el plano en un juego de plataformas.

    for k, clave in enumerate(capas):
        capa, arch, _ = A[clave]
        L.append({"rol": capa, "archivo": arch, "clave": clave,
                  "tipo_capa": "imagen", "prompt": prompt(clave),
                  "tratamiento": "semitono+trazo" if capa == "medio"
                                 else "plano_color",
                  "entrada": ents[min(k, len(ents) - 1)],
                  "caja": caja(capa, enc, solo_texto, sin_sujeto),
                  "retardo": round(0.12 * (k + 1), 2)})

    L.append({"rol": "marca", "tipo_capa": "codigo",
              "forma": MARCAS[(i * 3 + len(capas)) % len(MARCAS)],
              "caja": caja("marca", enc, solo_texto, sin_sujeto),
              "entrada": "trazo", "retardo": round(0.12 * (len(capas) + 1), 2)})
    L.append({"rol": "ancla", "tipo_capa": "codigo",
              "forma": ANCLAS[i % len(ANCLAS)], "caja": caja("ancla", enc, solo_texto, sin_sujeto),
              "texto": cap.split("_")[0].upper(),
              "entrada": "fundido", "retardo": 0.04})
    if graf:
        L.append({"rol": "grafico", "tipo_capa": "codigo",
                  "forma": graf["tipo"], "caja": caja("grafico", enc, solo_texto, sin_sujeto),
                  "entrada": "pop",
                  "retardo": round(0.12 * (len(capas) + 2), 2)})

    # Relleno hasta cinco. Son capas de compositing reales, no adorno:
    # la rejilla de imprenta y la vineta van SOBRE todo lo demas y son las
    # que hacen que el conjunto se lea como una pagina impresa.
    relleno = [("rejilla", "fundido"), ("vineta", "fundido"),
               ("grano", "ninguna")]
    k = 0
    while len(L) < 5 and k < len(relleno):
        f, e = relleno[k]
        L.append({"rol": "acabado", "tipo_capa": "codigo", "forma": f,
                  "entrada": e, "retardo": 0.0})
        k += 1
    return L


# ---------------------------------------------------------------------------
# MAQUETA. Numeros, no adjetivos.
#
# Un campo llamado "encuadre" con el valor "cerca_der" no significa nada
# para quien monta la escena: hay que darle coordenadas. Todo va en
# fracciones del lienzo, con el origen arriba a la izquierda.
#
#   frente_w   ancho de la estructura (1.0 = todo el lienzo)
#   frente_h   cuanto ocupa por abajo (0.45 = la mitad inferior)
#   medio_h    ALTO del sujeto (0.62 = casi dos tercios de la pantalla)
#   *_dx       desplazamiento horizontal respecto al centro
#   texto_x    donde cae el texto: al lado contrario del sujeto
#
# Regla dura: el contenido tiene que cubrir mas del 55% del cuadro. Con
# elementos al 25% y el resto papel, no es estilo Vox, es una plantilla
# de presentacion a medio rellenar.
# ---------------------------------------------------------------------------
# Medido sobre los fotogramas del canal de referencia:
#   - el contenido solo cubre del 27% al 47% del cuadro. El vacio es
#     deliberado: mi regla anterior de "mas del 55%" era falsa.
#   - la mitad inferior esta al 49-68%; la superior al 1-38%. El peso va
#     abajo SIEMPRE, pero el hueco de arriba no se rellena con adorno: se
#     deja vacio o lleva el texto.
#   - un solo elemento domina y mide del 55% al 75% del ALTO del cuadro.
#     Eso es lo que faltaba: pocos elementos y grandes, no muchos y chicos.
# ---------------------------------------------------------------------------
# ARQUETIPOS DE COMPOSICION
#
# La rotacion de encuadres no sabe lo que dice la frase, y por eso coloca
# elementos "por poner". En la referencia la composicion EXPRESA la frase:
#
#   petrolero   el barco navega SOBRE el mar     -> sobre
#   Xi y Putin  estan DETRAS de la puerta que
#               les corta por la cintura         -> detras
#   obrero vs   dos columnas simetricas, porque
#   soldado     la frase los compara             -> contraste
#   billete     un objeto solo, texto encima     -> unico
#
# Cada arquetipo define huecos con NOMBRE y con coordenadas. El asset se
# mete en el hueco que le corresponde por su funcion, no por su rol.
# ---------------------------------------------------------------------------
ARQUETIPOS = {
 # dos grupos enfrentados. Para "X frente a Y", "en los grandes, en los
 # pequenos", cualquier frase que compare dos cosas.
 "contraste": dict(
   simetria="espejo",
   huecos={
     "izq_sujeto": dict(x=0.22, y=0.90, w=0.30, h=0.66, anclaje="abajo",
                        encaje="contener"),
     "izq_base":   dict(x=0.20, y=1.01, w=0.30, h=0.24, anclaje="abajo", encaje="contener"),
     "der_sujeto": dict(x=0.78, y=0.90, w=0.30, h=0.66, anclaje="abajo",
                        encaje="contener"),
     "der_base":   dict(x=0.80, y=1.01, w=0.32, h=0.26, anclaje="abajo", encaje="contener"),
     "dato":       dict(x=0.50, y=0.34, w=0.30, anclaje="centro"),
     "titular":    dict(x=0.50, y=0.14, w=0.52, anclaje="centro"),
   }),

 # el sujeto detras de una estructura que le tapa de cintura para abajo
 "detras": dict(
   simetria="centrada",
   huecos={
     "sujeto":    dict(x=0.62, y=0.86, w=0.36, h=0.70, anclaje="abajo",
                       encaje="contener"),
     "estructura":dict(x=0.56, y=1.02, w=0.64, h=0.40, anclaje="abajo",
                       encaje="contener"),
     "titular":   dict(x=0.22, y=0.30, w=0.34, h=0.30, anclaje="centro"),
     "marca_a":   dict(x=0.22, y=0.62, w=0.16, h=0.08, anclaje="centro"),
   }),

 # algo apoyado o navegando sobre una superficie
 "sobre": dict(
   simetria="asimetrica",
   huecos={
     "superficie":dict(x=0.50, y=1.01, w=1.12, h=0.20, anclaje="abajo", encaje="cubrir"),
     "objeto":    dict(x=0.42, y=0.87, w=0.66, h=0.34, anclaje="abajo", encaje="contener"),
     "dato":      dict(x=0.78, y=0.36, w=0.30, anclaje="centro"),
     "titular":   dict(x=0.30, y=0.16, w=0.40, anclaje="centro"),
   }),

 # una cosa diminuta al lado de otra enorme. Para "5.000 $ para un
 # negocio de 30 millones".
 "escala": dict(
   simetria="asimetrica",
   huecos={
     "pequeno":   dict(x=0.26, y=0.93, w=0.12, h=0.16, anclaje="abajo",
                        encaje="contener"),
     "grande":    dict(x=0.72, y=0.97, w=0.40, h=0.62, anclaje="abajo",
                        encaje="contener"),
     "dato":      dict(x=0.28, y=0.38, w=0.28, anclaje="centro"),
     "titular":   dict(x=0.30, y=0.16, w=0.42, anclaje="centro"),
   }),

 # tres elementos en fila sobre la misma linea. Para enumeraciones.
 "cadena": dict(
   simetria="rejilla",
   huecos={
     "item_1":    dict(x=0.20, y=0.94, w=0.24, h=0.34, anclaje="abajo",
                        encaje="contener"),
     "item_2":    dict(x=0.50, y=0.94, w=0.24, h=0.34, anclaje="abajo",
                        encaje="contener"),
     "item_3":    dict(x=0.80, y=0.94, w=0.24, h=0.34, anclaje="abajo",
                        encaje="contener"),
     "titular":   dict(x=0.50, y=0.20, w=0.60, anclaje="centro"),
   }),

 # un solo objeto dominando, texto encima
 "unico": dict(
   simetria="centrada",
   huecos={
     "objeto":    dict(x=0.50, y=0.96, w=0.52, h=0.56, anclaje="abajo",
                        encaje="contener"),
     "titular":   dict(x=0.50, y=0.24, w=0.60, anclaje="centro"),
     "marca_a":   dict(x=0.80, y=0.40, w=0.16, anclaje="centro"),
   }),

 # solo tipografia y datos
 "dato_pleno": dict(
   simetria="centrada",
   huecos={
     "dato":      dict(x=0.50, y=0.40, w=0.76, h=0.26, anclaje="centro",
                       px_rel=0.20),
     "titular":   dict(x=0.50, y=0.66, w=0.72, h=0.14, anclaje="centro",
                       px_rel=0.075),
     "marca_a":   dict(x=0.50, y=0.82, w=0.24, h=0.06, anclaje="centro"),
   }),
}


# Que puede hacer cada asset dentro de un plano. Un edificio OCLUYE, un
# monton de monedas se APILA a los pies, una persona es SUJETO. Sin esto,
# el maletin acaba flotando encima de un libro.
FUNCION = {
 "sujeto":     {"cajero","cola","banquero","abogados","inspector","plantilla",
                "fundador","familia","consultor","guardia"},
 "ocluye":     {"oficina","mostrador","boveda","regulador","torre","atm",
                "obra","cerrado","servidor"},
 "superficie": {"libro","mostrador","monedas","expediente","recibos"},
 "apilable":   {"monedas","billetes","expediente","maletin","recibos",
                "llaves","candado","hucha","sello","cheque","terminal"},
 "icono":      {"escudo","balanza","engranaje","semaforo","nube","tarta",
                "regla","cinta","pesa","paraguas","grieta","reloj",
                "calendario","silla","vaso","tijeras"},
}


def funcion_de(clave):
    for f, s_ in FUNCION.items():
        if clave in s_:
            return f
    return "apilable"


def repartir(arq, capas):
    """
    Mete cada asset en el hueco que le toca por funcion. Devuelve pares
    (clave, hueco). Si un hueco no tiene candidato, se queda vacio: mejor
    un plano con dos elementos bien puestos que con cuatro mal.
    """
    huecos = ARQUETIPOS[arq]["huecos"]
    suj = [c for c in capas if funcion_de(c) == "sujeto"]
    est = [c for c in capas if funcion_de(c) in ("ocluye", "superficie")]
    obj = [c for c in capas if funcion_de(c) in ("apilable", "icono")]
    par = []

    if arq == "contraste":
        col = [("izq_sujeto", "izq_base"), ("der_sujeto", "der_base")]
        for k, (hs, hb) in enumerate(col):
            if k < len(suj):
                par.append((suj[k], hs))
            elif k < len(est):
                par.append((est[k], hs))
            base = (obj + est)[k:k + 1]
            if base:
                par.append((base[0], hb))
    elif arq == "detras":
        if suj:
            par.append((suj[0], "sujeto"))
        if est:
            par.append((est[0], "estructura"))
        elif obj:
            par.append((obj[0], "estructura"))
    elif arq == "sobre":
        if est:
            par.append((est[0], "superficie"))
        resto = suj + obj
        if resto:
            par.append((resto[0], "objeto"))
    elif arq == "escala":
        chico = obj or est
        grande = suj or est or obj
        if chico:
            par.append((chico[0], "pequeno"))
        if grande and grande[0] != (chico[0] if chico else None):
            par.append((grande[0], "grande"))
    elif arq == "cadena":
        for k, c in enumerate((obj + est + suj)[:3]):
            par.append((c, f"item_{k+1}"))
    elif arq == "unico":
        uno = est or obj or suj
        if uno:
            par.append((uno[0], "objeto"))
    return par


def retorica(txt, capas, graf):
    """
    Elige el arquetipo por lo que HACE la frase, no por rotacion.
    Es la diferencia entre colocar elementos y componer un plano.
    """
    t = txt.lower()
    n_suj = sum(1 for c in capas if A[c][0] == "medio")
    n_est = sum(1 for c in capas if A[c][0] == "frente")

    if not capas:
        return "dato_pleno"
    # comparaciones explicitas
    if any(k in t for k in ("en los grandes", "en los pequenos", "frente a",
                            "mas que el", "tres veces", "a un lado", "al otro",
                            "dos bancos", "y en los")):
        return "contraste"
    # ordenes de magnitud muy distintos
    if any(k in t for k in ("para un negocio de", "cinco mil dolares. para",
                            "por cada cien", "multiplicada por")):
        return "escala"
    # enumeraciones de tres o mas
    if t.count(",") >= 3 or any(k in t for k in ("entre nominas", "ni el",
                                                 "ni los", "quienes son")):
        return "cadena"
    # una persona con un edificio o un mueble que la tapa
    if n_suj and n_est:
        return "detras"
    # objeto sobre una superficie
    if n_est and any(k in t for k in ("oficina", "abrir", "mostrador",
                                      "puertas", "fachada")):
        return "sobre"
    return "unico"


# Al partir una idea en varios planos, el segundo y el tercero cambian de
# arquetipo: es un contraplano de la misma frase, no el mismo plano otra
# vez. Solo se salta a arquetipos que admitan los mismos assets.
ALTERNATIVA = {
 "detras":    ["unico", "sobre", "detras"],
 "unico":     ["detras", "escala", "unico"],
 "contraste": ["detras", "contraste", "unico"],
 "sobre":     ["detras", "unico", "sobre"],
 "escala":    ["unico", "detras", "escala"],
 "cadena":    ["unico", "cadena", "detras"],
 "dato_pleno":["dato_pleno"],
}


def rotar_assets(capas, j):
    """
    Los trozos de una misma idea no repiten el mismo par de imagenes: se
    rota cual va delante. Con dos assets, el segundo plano cierra sobre el
    otro elemento en vez de repetir el mismo encuadre con la misma pila.
    """
    if not capas or j == 0:
        return capas
    if len(capas) == 1:
        return capas
    k = j % len(capas)
    return capas[k:] + capas[:k]


def variar(arq, j, capas):
    if j == 0:
        return arq
    alt = ALTERNATIVA[arq]
    cand = alt[(j - 1) % len(alt)]
    # un arquetipo que necesita dos grupos no vale con un solo asset
    if cand == "contraste" and len(capas) < 2:
        cand = "detras"
    if cand == "escala" and len(capas) < 2:
        cand = "unico"
    return cand


MAQUETA = {
 "ancho":     dict(frente_w=0.86, frente_h=0.40, frente_dx=-0.06,
                   medio_h=0.58, medio_dx= 0.10, texto_x="der", texto_y=0.16),
 "ancho_izq": dict(frente_w=0.92, frente_h=0.38, frente_dx=-0.14,
                   medio_h=0.56, medio_dx=-0.16, texto_x="der", texto_y=0.18),
 "medio":     dict(frente_w=0.72, frente_h=0.46, frente_dx= 0.10,
                   medio_h=0.68, medio_dx=-0.14, texto_x="der", texto_y=0.14),
 "medio_izq": dict(frente_w=0.70, frente_h=0.46, frente_dx=-0.16,
                   medio_h=0.70, medio_dx=-0.20, texto_x="der", texto_y=0.14),
 "medio_der": dict(frente_w=0.70, frente_h=0.46, frente_dx= 0.16,
                   medio_h=0.70, medio_dx= 0.20, texto_x="izq", texto_y=0.14),
 "cerca":     dict(frente_w=0.52, frente_h=0.48, frente_dx=-0.08,
                   medio_h=0.76, medio_dx= 0.08, texto_x="der", texto_y=0.12),
 "cerca_izq": dict(frente_w=0.50, frente_h=0.48, frente_dx=-0.20,
                   medio_h=0.74, medio_dx=-0.24, texto_x="der", texto_y=0.12),
 "cerca_der": dict(frente_w=0.50, frente_h=0.48, frente_dx= 0.20,
                   medio_h=0.74, medio_dx= 0.24, texto_x="izq", texto_y=0.12),
}
ENC = list(MAQUETA)
ENT_ROT = ["pop+sube", "lateral+sube", "cae+sube", "pop+cae",
           "lateral+cae", "pop+lateral"]


# ---------------------------------------------------------------------------
# ESTADOS DENTRO DE UNA MISMA TOMA
#
# Esto es lo que llevaba diez rondas sin ver. Medido sobre la escena del
# grafico del canal de referencia, 0:26 a 0:39, trece segundos SIN UN SOLO
# CORTE:
#
#   0:26  la grafica CPI sola, centrada y grande
#   0:30  la grafica ENCOGE y se va a la izquierda; entra el mapa
#   0:33  aparece "$39 TRILLION" sobre el mapa
#   0:35  la grafica SALE; mapa y texto se recolocan al centro
#   0:36  entra el obrero por la izquierda
#   0:39  entra el soldado por la derecha y queda simetrico
#
# Los elementos PERSISTEN, se mueven, encogen y salen dentro del mismo
# plano. El dinamismo no sale de cortar cada 4 s: sale de que el escenario
# se reorganiza cada 2 s sin cortar. Por eso el suyo se lee como una toma
# continua y el nuestro como un pase de diapositivas.
#
# Una escena = un beat de locucion, de 6 a 13 s, un solo plano.
# Un estado  = un momento de ~2 s dentro de ese plano.
# ---------------------------------------------------------------------------
# Medido sobre el video de referencia completo (48 s, 1920x1080, 30 fps):
#   6 cortes duros  -> 7 planos, 6,9 s de media
#   11 cambios de estado SIN cortar
#   = 17 sucesos visuales en 48 s -> uno cada 2,8 s
# Mi 1,6 s era demasiado rapido. El ritmo real es mas pausado de lo que
# parece, y lo que lo hace vivo no es la frecuencia: es que entre suceso y
# suceso la composicion DERIVA despacio, un 1% por segundo.
PASO_ESTADO = 2.8
DERIVA = 0.010          # fraccion del lienzo por segundo, dentro del estado


def trocear(dur, tope=5.0, minimo=3.0):
    """Ya no se trocea en planos: la escena es una sola toma continua."""
    return [dur]


def guion_estados(L, dur, texto):
    """
    Coreografia construida DESDE LAS CAPAS YA RESUELTAS.

    Antes se construia aparte, desde el arquetipo crudo, y las cajas salian
    sin px_rel ni max_chars. Resultado: el texto se dibujaba dos veces, una
    gigante sin tamano y otra pequena correcta, y las imagenes salian
    diminutas. Ahora un estado solo dice QUE capa se ve y DONDE; el estilo
    es siempre el de la capa, nunca se recalcula.
    """
    # En la referencia cada plano tiene 2,6 momentos de media (el inicial
    # mas 1,6 cambios). Con mas, el plano deja de respirar.
    n = max(2, min(5, int(dur // 3)))
    por_id = {c["id"]: c for c in L}
    fijas = [c["id"] for c in L if c["rol"] in ("fondo", "ancla", "acabado",
                                                "marca")]
    orden = ([c["id"] for c in L if c["tipo_capa"] == "imagen"
              and c["rol"] != "fondo"]
             + [c["id"] for c in L if c["rol"] == "grafico"]
             + [c["id"] for c in L if c["rol"] == "titular"])
    tiene_txt = any(c["rol"] == "titular" for c in L)

    guion = list(orden)
    # No todos los estados son "entra algo nuevo". En la referencia, la
    # grafica primero SE DIBUJA sola (mismo sitio, dos segundos) y solo
    # despues encoge. Y el remate escribe la frase en dos tiempos.
    # el gesto de "asentarse" solo cabe en planos largos
    if dur >= 8 and guion and por_id[guion[0]]["tipo_capa"] == "imagen":
        guion.insert(1, "@asienta")
    guion = guion[:n] or [orden[0] if orden else fijas[0]]
    dos_tiempos = tiene_txt and len(texto) > 46 and dur >= 7

    estados, en_escena = [], []
    primera = next((g for g in guion if g != "@asienta"), None)
    for k, nuevo in enumerate(guion):
        if nuevo != "@asienta":
            en_escena = en_escena + [nuevo]
        e = {"t": round(k * (dur / len(guion)), 2),
             "entra": None if nuevo == "@asienta" else nuevo,
             "gesto": "asienta" if nuevo == "@asienta" else None,
             "visibles": fijas + list(en_escena),
             "elementos": []}
        for ref in en_escena:
            # la caja SALE DE LA CAPA, con su px_rel y su max_chars
            caja = dict(por_id[ref]["caja"])
            # el que dominaba cede sitio al que entra: encoge y se aparta
            if ref != nuevo and ref == primera and len(en_escena) > 2:
                caja["w"] = round(caja.get("w", 0.5) * 0.74, 3)
                caja["h"] = round(caja.get("h", 0.4) * 0.74, 3)
                caja["x"] = round(0.5 + (caja["x"] - 0.5) * 1.40, 3)
                if "px_rel" in caja:
                    caja["px_rel"] = round(caja["px_rel"] * 0.74, 4)
            e["elementos"].append({"ref": ref, "caja": caja})
        # deriva lenta dentro del estado: el plano nunca esta del todo
        # quieto, pero tampoco se mueve lo suficiente como para notarlo
        e["deriva"] = {"dx": round(DERIVA * (1 if k % 2 else -1), 4),
                       "dy": round(-DERIVA * 0.4, 4)}
        estados.append(e)

    # la frase se escribe en dos tiempos: primera mitad y frase completa
    if dos_tiempos:
        tid = next(c["id"] for c in L if c["rol"] == "titular")
        completo = por_id[tid].get("texto", texto)
        mitad = " ".join(completo.split()[: max(2, len(completo.split()) // 2)])
        visto = False
        for e in estados:
            for x in e["elementos"]:
                if x["ref"] != tid:
                    continue
                x["texto"] = completo if visto else mitad
                if not visto:
                    visto = True

    # el ultimo estado suelta lo que ya no aporta, como hace el suyo cuando
    # la grafica sale y el mapa se recoloca
    if len(estados) >= 4 and len(guion) > 2:
        ult = dict(estados[-1])
        ult["sale"] = primera
        ult["visibles"] = [v for v in ult["visibles"] if v != primera]
        ult["elementos"] = [x for x in ult["elementos"] if x["ref"] != primera]
        for x in ult["elementos"]:
            x["caja"]["x"] = round(0.5 + (x["caja"]["x"] - 0.5) * 0.55, 3)
        estados.append({**ult, "t": round(dur * 0.86, 2), "entra": None})
    return estados


def main():
    dest = "proyecto_banco"
    os.makedirs(dest, exist_ok=True)
    escenas, usados = [], collections.Counter()
    filas_md, total = [], 0

    ultima_estruct = None
    print(f'{"capitulo":18s} {"esc":>4s} {"seg":>5s} {"obj":>5s}')
    for cap, objetivo, beats in GUION:
        suma = sum(b[1] for b in beats)
        total += suma
        marca = "  ok" if suma == objetivo else f"  <-- {suma-objetivo:+d}"
        print(f"{cap:18s} {len(beats):4d} {suma:5d} {objetivo:5d}{marca}")

        for i, (txt, dur, tipo, capas, graf, ent, trans) in enumerate(beats, 1):
            for c in capas:
                usados[c] += 1
                if A[c][0] == "frente":
                    ultima_estruct = c
            trozos = trocear(dur)
            frases = partir_frase(txt, len(trozos))
            for j, d in enumerate(trozos):
                ident = f"{cap.lower()}_{i:02d}" + ("" if j == 0 else chr(96 + j))
                g = graf if j == 0 else None
                e = ent if j == 0 else ENT_ROT[(len(escenas) + j) % len(ENT_ROT)]
                # Si la idea no llevaba imagen y se ha partido, los trozos
                # posteriores toman prestada la ultima estructura vista: dos
                # planos seguidos de pura tipografia pasan; cuatro, no.
                cap_esc = capas
                if not capas and j > 0 and ultima_estruct:
                    cap_esc = [ultima_estruct]
                cap_esc = rotar_assets(cap_esc, j)
                arq = variar(retorica(txt, cap_esc, g), j, cap_esc)
                st = not cap_esc
                lista = pila_arq(cap_esc, g, e, len(escenas), cap, arq,
                                 frases[j])
                enc = arq
                estados = guion_estados(lista, d, frases[j])
                esc = {"id": ident, "texto": txt, "frase": frases[j],
                       "duracion": d,
                       "estados": estados,
                       "n_estados": len(estados),
                       "arquetipo": arq,
                       "simetria": ARQUETIPOS[arq]["simetria"],
                       "solo_texto": st,
                       "capas": lista,
                       "n_capas": len(lista),
                       "imagenes": sum(1 for c in lista
                                       if c["tipo_capa"] == "imagen"),
                       "transicion": trans if j == 0 else "corte"}
                if g:
                    esc["grafico"] = dict(g, entrada="pop", retardo=None)
                escenas.append(esc)
                filas_md.append((ident, txt, d, esc["arquetipo"],
                                 [A[c][1] for c in cap_esc], e,
                                 (g or {}).get("tipo", "—"),
                                 esc["transicion"], len(lista)))

    fallos = []
    for e in escenas:
        cs = e["capas"]
        txt = [c for c in cs if c["rol"] in ("titular", "grafico")]
        if len(txt) > 1 and len({c.get("texto") for c in txt if c.get("texto")}) < len(
                [c for c in txt if c.get("texto")]):
            fallos.append(f'{e["id"]}: dos capas con el mismo texto')
        for c in cs:
            b = c["caja"]
            if c["tipo_capa"] == "imagen" and c["rol"] != "fondo":
                if "w" not in b or "h" not in b:
                    fallos.append(f'{e["id"]}: {c["rol"]} sin caja completa')
                if "encaje" not in b:
                    fallos.append(f'{e["id"]}: {c["rol"]} sin regla de encaje')
            if c["rol"] in ("titular", "grafico"):
                if "px_rel" not in b:
                    fallos.append(f'{e["id"]}: texto sin tamano')
                elif c.get("texto") and len(c["texto"]) > b["max_chars"]:
                    fallos.append(f'{e["id"]}: texto de {len(c["texto"])} '
                                  f'chars en caja de {b["max_chars"]}')
        if not any(c["rol"] in ("medio", "frente", "grafico", "titular")
                   for c in cs):
            fallos.append(f'{e["id"]}: escena vacia')
        ids = {c["id"] for c in cs}
        for st in e["estados"]:
            for x in st["elementos"]:
                if x["ref"] not in ids:
                    fallos.append(f'{e["id"]}: estado apunta a {x["ref"]}, '
                                  f'que no existe en capas')
                    continue
                capa = next(c for c in cs if c["id"] == x["ref"])
                if capa["rol"] in ("titular", "grafico") and \
                        "px_rel" not in x["caja"]:
                    fallos.append(f'{e["id"]}: estado con texto sin tamano')
            if len(st["elementos"]) != len({x["ref"] for x in st["elementos"]}):
                fallos.append(f'{e["id"]}: el mismo elemento dos veces en '
                              f'un estado')
        imgs = [rect(c) for c in cs if c["tipo_capa"] == "imagen"
                and c["rol"] != "fondo"]
        for c in cs:
            if c["rol"] in ("titular", "grafico") and imgs:
                if max(solapa(rect(c), m) for m in imgs) > 0.15:
                    fallos.append(f'{e["id"]}: texto encima de una imagen')
    if fallos:
        print(f"\n{len(fallos)} INVARIANTES ROTOS:")
        for f_ in fallos[:12]:
            print("   ", f_)
        raise SystemExit(1)
    print("\ninvariantes: correctos "
          "(sin texto duplicado, sin cajas abiertas, sin solapes, "
          "sin escenas vacias)")

    # Barra de progreso: en la referencia es el UNICO elemento decorativo y
    # resulta que es funcional. Cruza el video entero de 0 a 100%.
    acum = 0.0
    for e in escenas:
        e["progreso"] = [round(acum / total, 4),
                         round((acum + e["duracion"]) / total, 4)]
        acum += e["duracion"]

    guion = {"lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
             "estilo": PALETA, "fondo_bloqueado": FONDO[0],
             "papel_rgb": [227, 221, 211],
             "barra_progreso": {"color": [252, 136, 2], "alto": 0.022,
                                "borde": "inferior"},
             "cobertura_objetivo": [0.10, 0.50],
             "como_leer": [
               "Cada escena es UN SOLO PLANO continuo. NO se corta entre",
               "estados: los elementos animan de una caja a la siguiente.",
               "",
               "capas[]  = declaracion. Cada capa se declara UNA vez, con su",
               "           id, su archivo o forma, su texto y su caja. La",
               "           caja lleva x, y, w, h en fracciones del lienzo,",
               "           y si es texto tambien px_rel, lineas y max_chars.",
               "",
               "estados[] = coreografia. Cada estado dice, en el instante t,",
               "           que capas estan visibles y en que caja. Una capa",
               "           que no aparece en 'visibles' NO SE DIBUJA.",
               "",
               "NUNCA se dibuja una capa dos veces. NUNCA se recalcula el",
               "tamano: el de la caja del estado es el bueno.",
               "",
               "px_rel es la altura de la fuente como fraccion del alto del",
               "lienzo: px_rel 0.06 a 1080 son 65 px."
             ],
             "escenas": escenas}
    json.dump(guion, open(f"{dest}/guion.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # --- storyboard legible ---
    with open(f"{dest}/STORYBOARD.md", "w", encoding="utf-8") as f:
        f.write("# Episodio 03 · El banco · storyboard\n\n")
        f.write(f"**{len(escenas)} escenas · {total//60}:{total%60:02d} · "
                f"{len(usados)} imagenes a generar + 1 fondo**\n\n")
        f.write("Fondo bloqueado en las " + str(len(escenas)) +
                " escenas: `" + FONDO[0] + "`\n\n")
        f.write("| # | locucion | s | arquetipo | imagenes (hueco) | entrada | "
                "graphic | corte | capas |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for ident, txt, dur, enc, arch, ent, g, tr, nc in filas_md:
            capas = "—" if not arch else " + ".join(arch)
            f.write(f"| `{ident}` | {txt[:64]} | {dur} | {enc} | {capas} | "
                    f"{ent} | {g} | {tr} | {nc} |\n")

        f.write("\n\n## Prompts para Meta AI\n\n")
        f.write(f"### fondo (uno solo, para todo el episodio)\n\n"
                f"**`{FONDO[0]}`**\n\n> {FONDO[1]}. "
                f"Ilustracion plana. Paleta: {PALETA}.\n\n")
        f.write("### sujetos — se generan en blanco y negro y luego se les "
                "aplica semitono y trazo rojo en local\n\n")
        for k, (capa, arch, _) in sorted(A.items(), key=lambda x: x[1][1]):
            if capa != "medio":
                continue
            f.write(f"**`{arch}`** · usado en {usados[k]} escenas\n\n"
                    f"> {prompt(k)}\n\n")
        f.write("### estructuras — planas y a color, se anclan al borde "
                "inferior y tapan al sujeto\n\n")
        for k, (capa, arch, _) in sorted(A.items(), key=lambda x: x[1][1]):
            if capa != "frente":
                continue
            f.write(f"**`{arch}`** · usado en {usados[k]} escenas\n\n"
                    f"> {prompt(k)}\n\n")

    nc = [e["n_capas"] for e in escenas]
    im = [e["imagenes"] for e in escenas]
    print(f"\n{len(escenas)} escenas · {total}s ({total//60}:{total%60:02d})")
    print(f"duracion: min {min(e['duracion'] for e in escenas)}s  "
          f"max {max(e['duracion'] for e in escenas)}s  "
          f"media {total/len(escenas):.1f}s")
    print(f"capas por escena: min {min(nc)}  max {max(nc)}  "
          f"media {sum(nc)/len(nc):.1f}")
    import collections as _c
    est = [e["n_estados"] for e in escenas]
    print(f"estados por escena: min {min(est)}  max {max(est)}  "
          f"media {sum(est)/len(est):.1f}  ·  {sum(est)} momentos en total")
    print(f"un cambio visual cada "
          f"{sum(e['duracion'] for e in escenas)/sum(est):.1f} s, sin cortar")
    arqs = _c.Counter(e["arquetipo"] for e in escenas)
    print("arquetipos:", dict(arqs))
    cob = [0.4 for e in escenas]
    print(f"imagenes por escena: media {sum(im)/len(im):.1f} · "
          f"{len(usados)+1} PNG unicos en total")

    print(f"-> {dest}/guion.json y {dest}/STORYBOARD.md")


if __name__ == "__main__":
    main()
