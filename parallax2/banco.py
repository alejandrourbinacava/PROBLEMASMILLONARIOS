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
def C(t, s, **kw):      # atajo para escena de codigo
    return (t, s, "codigo", [], kw.get("g"), kw.get("e", "pop"),
            kw.get("x", "corte"))


def E(t, s, capas, **kw):
    return (t, s, "capas", capas, kw.get("g"), kw.get("e", "pop"),
            kw.get("x", "corte"))


GUION = [
("GANCHO", 60, [
 C("Un banco medio de Estados Unidos gana tres coma veintidos dolares al ano "
   "por cada cien que tiene prestados.", 7,
   g=dict(tipo="contador", valor=3.22, dec=2, sufijo="$", pie="por cada 100 $ prestados")),
 C("Tres coma veintidos. Ese es el margen.", 4,
   g=dict(tipo="titular", lineas=["Tres coma", "*veintidos*"]), e="maquina"),
 E("Y con ese margen se pagan las oficinas, las nominas, los sistemas, los "
   "abogados y los accionistas.", 8, ["plantilla", "oficina"], e="pop+sube"),
 C("Suena a poco.", 3, g=dict(tipo="titular", lineas=["Suena a *poco*."])),
 E("Y sin embargo, no hay ningun negocio con una cola mas larga de gente "
   "esperando para entrar.", 8, ["cola", "oficina"], e="lateral+sube"),
 C("Porque un banco no gana dinero con su dinero. Lo gana con el tuyo.", 7,
   g=dict(tipo="reparto", valor=100, etiqueta_a="tu dinero", etiqueta_b="suyo"),
   e="barrido"),
 E("Coge lo que tu depositas, se lo presta a otro mas caro, y se queda la "
   "diferencia.", 8, ["familia", "hucha"], e="pop+sube"),
 C("Ese es el negocio entero. Todo lo demas es decoracion.", 5,
   g=dict(tipo="titular", lineas=["Todo lo demas", "es *decoracion*."])),
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
   g=dict(tipo="titular", lineas=["Eso es la *tienda*", "del banco."]), x="corte"),
 C("El banco de verdad es una hoja de calculo.", 5,
   g=dict(tipo="titular", lineas=["El banco es una", "*hoja de calculo*."])),
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
   g=dict(tipo="barras", sufijo="%",
          items=[["Nominas", 52], ["Alquiler", 21], ["Seguridad", 15], ["Resto", 12]]),
   e="barrido"),
 C("Y las oficinas son solo el quince por ciento de los gastos de un banco.", 7,
   g=dict(tipo="anillo", valor=15, sufijo="%", pie="lo que pesan las oficinas")),
 C("Lo que tu ves cuando piensas en un banco es la parte mas barata del banco.",
   7, g=dict(tipo="titular", lineas=["Lo que ves es", "lo mas *barato*."]),
   e="maquina", x="fundido"),
 E("Vamos a la cara.", 4, ["banquero", "boveda"], e="pop+sube"),
]),

("CAP2_CAPITAL", 100, [
 E("Para abrir un banco nuevo en Estados Unidos hace falta capital inicial.", 6,
   ["fundador", "maletin"], e="pop+sube"),
 C("Y no es una cifra simbolica.", 4,
   g=dict(tipo="titular", lineas=["No es una cifra", "*simbolica*."])),
 C("En dos mil veintiseis, los reguladores esperan entre veintisiete y "
   "cincuenta millones de dolares.", 8,
   g=dict(tipo="barras", sufijo=" M$", dec=0,
          items=[["Minimo", 27], ["Habitual", 50]]), e="barrido"),
 C("En algunos estados basta con diez o quince millones si el modelo es "
   "pequeno y sencillo.", 7,
   g=dict(tipo="barras", sufijo=" M$", dec=0,
          items=[["Estado pequeno", 12], ["Media", 38], ["Nueva York", 50]]),
   e="barrido"),
 E("En el area metropolitana de Nueva York, la cifra empieza en cincuenta y "
   "sube.", 7, ["banquero", "torre"], e="pop+sube", x="closer"),
 C("Y ahora la parte que casi nadie entiende.", 3,
   g=dict(tipo="titular", lineas=["Y ahora lo que", "*nadie* entiende."]), e="maquina"),
 E("Ese dinero no es para gastarlo.", 4, ["fundador", "billetes"], e="pop+cae"),
 C("No es para comprar el edificio, ni los ordenadores, ni pagar sueldos.", 6,
   g=dict(tipo="barras", sufijo="", dec=0,
          items=[["Edificio", 0], ["Sistemas", 0], ["Sueldos", 0]]), e="barrido"),
 E("Ese dinero es un colchon. Esta ahi para absorber perdidas si los prestamos "
   "salen mal.", 8, ["banquero", "paraguas"], e="pop+sube"),
 C("Se queda quieto, en el balance, demostrando que el banco aguanta un golpe.",
   6, g=dict(tipo="titular", lineas=["Se queda *quieto*."])),
 E("Es como si para abrir un restaurante te pidieran treinta millones y te "
   "dijeran: no los toques.", 8, ["fundador", "candado"], e="pop+cae"),
 C("El capital no es una cifra fija: es un porcentaje de lo que prestas.", 5,
   g=dict(tipo="titular", lineas=["Cuanto mas prestas,", "mas *capital*."]), x="corte"),
 C("El minimo del capital de maxima calidad es el cuatro coma cinco por ciento "
   "de los activos ponderados por riesgo.", 8,
   g=dict(tipo="anillo", valor=4.5, sufijo="%", pie="minimo regulatorio")),
 C("Para considerarte bien capitalizado, la ratio de apalancamiento tiene que "
   "estar en el cinco por ciento.", 7,
   g=dict(tipo="anillo", valor=5.0, sufijo="%", pie="para estar bien capitalizado")),
 C("En la practica, la mayoria de los bancos van entre el ocho y el once por "
   "ciento. Muy por encima del minimo.", 8,
   g=dict(tipo="barras", sufijo="%", destacar="Minimo legal",
          items=[["Minimo legal", 4.5], ["Banca real", 9.5]]), e="barrido"),
 E("Porque el que esta justo en el minimo es el que no sobrevive al primer "
   "susto.", 6, ["banquero", "grieta"], e="pop+lateral", x="fundido"),
]),

("CAP3_LICENCIA", 140, [
 E("Con el capital reunido, empieza lo dificil.", 4, ["fundador", "regulador"],
   e="pop+sube"),
 C("Un banco necesita una ficha bancaria. Y una ficha bancaria no se compra.", 6,
   g=dict(tipo="titular", lineas=["No se compra.", "Se *concede*."]), e="maquina"),
 E("La solicitud al fondo de garantia de depositos cuesta cinco mil dolares.", 7,
   ["abogados", "expediente"], e="pop+sube",
   g=dict(tipo="contador", valor=5000, sufijo="$", pie="tasa de solicitud")),
 C("No reembolsables.", 3, g=dict(tipo="titular", lineas=["No *reembolsables*."])),
 C("Cinco mil dolares. Para un negocio de treinta millones.", 6,
   g=dict(tipo="barras", sufijo=" $", dec=0,
          items=[["Tasa", 5000], ["Capital exigido", 30000000]]), e="barrido"),
 C("Parece un chiste, y lo es, porque la tasa no es el coste.", 5,
   g=dict(tipo="titular", lineas=["La tasa no es", "el *coste*."])),
 E("El coste es todo lo que hay que poner encima de la tasa.", 5,
   ["abogados", "expediente"], e="pop+cae", x="closer"),
 E("Solo los abogados que preparan la solicitud se llevan doscientos mil "
   "dolares o mas.", 8, ["abogados", "maletin"], e="pop+sube",
   g=dict(tipo="contador", valor=200, sufijo="mil $", pie="solo abogados")),
 E("Los consultores que escriben el plan de negocio, otros ciento cincuenta mil.",
   7, ["consultor", "libro"], e="pop+sube",
   g=dict(tipo="contador", valor=150, sufijo="mil $", pie="consultores")),
 C("Y eso es antes de tener un solo cliente.", 4,
   g=dict(tipo="titular", lineas=["Antes de tener", "*un solo cliente*."]), e="maquina"),
 C("Desde agosto de dos mil veintiseis, el regulador concede una autorizacion "
   "condicionada en ciento veinte dias.", 10,
   g=dict(tipo="contador", valor=120, sufijo="dias", pie="autorizacion condicionada")),
 C("Antes el proceso se alargaba mucho mas de un ano.", 6,
   g=dict(tipo="barras", sufijo=" dias", dec=0,
          items=[["Ahora", 120], ["Antes", 400]]), e="barrido"),
 C("Pero condicionada quiere decir condicionada.", 5,
   g=dict(tipo="titular", lineas=["*Condicionada*."]), e="maquina"),
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
   g=dict(tipo="titular", lineas=["Siete anos", "*vigilado*."])),
 E("Y ahora la pregunta incomoda: que evaluan exactamente en esa solicitud.", 7,
   ["inspector", "sello"], e="pop+cae"),
 C("No evaluan solo tu plan de negocio. Te evaluan a ti.", 6,
   g=dict(tipo="titular", lineas=["Te evaluan", "*a ti*."]), e="maquina"),
 E("De donde sale cada dolar que has puesto. Quienes son tus socios. Que has "
   "hecho antes.", 10, ["fundador", "expediente"], e="pop+sube"),
 C("No hay presuncion de inocencia. La carga de la prueba es tuya.", 8,
   g=dict(tipo="titular", lineas=["La carga de la", "prueba es *tuya*."]),
   x="fundido"),
]),

("CAP4_SOCIO", 140, [
 E("Supongamos que la consigues. Estas dentro. Abres las puertas.", 9,
   ["plantilla", "oficina"], e="pop+sube"),
 C("Enhorabuena: acabas de meter un socio que no ha puesto un dolar y que no "
   "se va a ir nunca.", 9,
   g=dict(tipo="titular", lineas=["Un socio que", "no se va *nunca*."]), e="maquina"),
 E("El regulador no cobra un porcentaje de tus beneficios como haria un socio "
   "normal.", 10, ["inspector", "regulador"], e="pop+cae"),
 C("Cobra de otra forma: en trabajo que tienes que hacer y que no produce nada.",
   8, g=dict(tipo="titular", lineas=["Trabajo que", "no *produce* nada."])),
 C("En los bancos pequenos, el cumplimiento se lleva el ocho coma siete por "
   "ciento de los gastos que no son intereses.", 10,
   g=dict(tipo="anillo", valor=8.7, sufijo="%", pie="cumplimiento en banca pequena")),
 C("En los grandes, el dos coma nueve.", 6,
   g=dict(tipo="barras", sufijo="%", destacar="Banco pequeno",
          items=[["Banco pequeno", 8.7], ["Banco grande", 2.9]]), e="barrido"),
 C("Leelo otra vez.", 3, g=dict(tipo="titular", lineas=["*Tres veces* mas."]),
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
   g=dict(tipo="titular", lineas=["La trampa es", "*matematica*."])),
 C("Las normas son fijas. Los costes de cumplirlas tambien.", 7,
   g=dict(tipo="barras", sufijo="", dec=0,
          items=[["Coste normativo", 100], ["Coste normativo", 100]]), e="barrido"),
 C("Asi que cuanto mas pequeno eres, mas pesan.", 6,
   g=dict(tipo="titular", lineas=["Cuanto mas pequeno,", "mas *pesan*."])),
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
   g=dict(tipo="titular", lineas=["Los numeros", "*buenos*."])),
 C("El margen de intermediacion medio de la banca estadounidense esta en el "
   "tres coma veintidos por ciento.", 9,
   g=dict(tipo="anillo", valor=3.22, dec=2, sufijo="%", pie="margen de intermediacion")),
 C("El rendimiento medio de los prestamos, en el seis coma cincuenta y uno.", 7,
   g=dict(tipo="contador", valor=6.51, dec=2, sufijo="%", pie="rendimiento de los prestamos")),
 C("Llego a tocar el siete coma trece a finales de dos mil veinticuatro y lleva "
   "bajando desde entonces.", 9,
   g=dict(tipo="barras", sufijo="%", destacar="2024",
          items=[["2024", 7.13], ["Hoy", 6.51]]), e="barrido"),
 E("La diferencia entre lo que cobras por prestar y lo que pagas por los "
   "depositos: ahi esta todo el negocio.", 10, ["banquero", "balanza"],
   e="pop+cae", x="closer"),
 C("Y a esa cuenta hay que restarle la maquinaria.", 5,
   g=dict(tipo="titular", lineas=["Restale la", "*maquinaria*."])),
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
   g=dict(tipo="titular", lineas=["Lo que cambia", "*todo*."]), e="maquina"),
 E("Has puesto treinta millones. Has conseguido la licencia. Has montado los "
   "sistemas.", 8, ["fundador", "boveda"], e="pop+sube"),
 E("Has contratado a la plantilla, has abierto las oficinas.", 6,
   ["plantilla", "oficina"], e="pop+sube"),
 C("Nada de eso te hace dueno del dinero que mueves.", 4,
   g=dict(tipo="titular", lineas=["Nada de eso te", "hace *dueno*."])),
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
   "semana.", 7, g=dict(tipo="titular", lineas=["Un *fin de semana*."]),
   e="maquina", x="fundido"),
]),

("CIERRE", 40, [
 C("Entonces, cuanto cuesta tener un banco.", 4,
   g=dict(tipo="titular", lineas=["Cuanto cuesta", "tener un *banco*."])),
 C("Entre veintisiete y cincuenta millones de capital que no puedes tocar.", 7,
   g=dict(tipo="barras", sufijo=" M$", dec=0,
          items=[["Capital", 50], ["Oficina", 3.5], ["Abogados", 0.35],
                 ["Sistemas", 0.8]]), e="barrido"),
 C("Y despues, para siempre: un ocho coma siete por ciento de tus gastos "
   "dedicado a demostrar que cumples.", 9,
   g=dict(tipo="anillo", valor=8.7, sufijo="%", pie="para siempre")),
 C("A cambio, tres coma veintidos dolares al ano por cada cien prestados.", 7,
   g=dict(tipo="contador", valor=3.22, dec=2, sufijo="$", pie="por cada 100 prestados")),
 E("El negocio funciona. Lleva funcionando siglos. Pero solo si aceptas la "
   "condicion.", 8, ["banquero", "boveda"], e="pop+sube"),
 C("En un banco tu no eres el dueno del dinero. Eres el responsable del dinero "
   "de otros.", 5, g=dict(tipo="titular",
                          lineas=["No eres el dueno.", "Eres el *responsable*."]),
   e="maquina", x="fundido"),
]),
]

CROMA = ("sobre un fondo verde croma liso y uniforme, de un solo tono plano, "
         "sin degradado, sin sombra proyectada sobre el fondo, sin suelo")

ENCUADRE = {
 "medio":  ("fotografia en blanco y negro de alto contraste, bordes nitidos, "
            "sujeto recortado contra el fondo"),
 "frente": ("ilustracion editorial plana, vector limpio, contorno marcado, "
            "sombra calida suave, sin degradados"),
 "fondo":  "textura plana, sin objetos, sin texto",
}


def prompt(clave):
    capa, arch, txt = A[clave]
    return f"{txt}. {ENCUADRE[capa]}. {CROMA}. Paleta: {PALETA}."


def main():
    dest = "proyecto_banco"
    os.makedirs(dest, exist_ok=True)
    escenas, usados = [], collections.Counter()
    filas_md, total = [], 0

    print(f'{"capitulo":18s} {"esc":>4s} {"seg":>5s} {"obj":>5s}')
    for cap, objetivo, beats in GUION:
        suma = sum(b[1] for b in beats)
        total += suma
        marca = "  ok" if suma == objetivo else f"  <-- {suma-objetivo:+d}"
        print(f"{cap:18s} {len(beats):4d} {suma:5d} {objetivo:5d}{marca}")

        for i, (txt, dur, tipo, capas, graf, ent, trans) in enumerate(beats, 1):
            ident = f"{cap.lower()}_{i:02d}"
            lista = [{"rol": "fondo", "archivo": FONDO[0], "clase": "papel",
                      "entrada": "ninguna", "prompt": FONDO[1]}]
            for k, clave in enumerate(capas):
                capa, arch, _ = A[clave]
                usados[clave] += 1
                lista.append({"rol": capa, "archivo": arch, "clave": clave,
                              "prompt": prompt(clave),
                              "tratamiento": "semitono+trazo" if capa == "medio"
                                             else "plano_color",
                              "entrada": ent.split("+")[min(k, len(ent.split("+")) - 1)],
                              "retardo": round(0.10 * (k + 1), 2)})
            esc = {"id": ident, "texto": txt, "duracion": dur, "tipo": tipo,
                   "capas": lista, "transicion": trans}
            if graf:
                esc["grafico"] = dict(graf, entrada="pop", retardo=None)
            escenas.append(esc)

            filas_md.append((ident, txt, dur, tipo,
                             [A[c][1] for c in capas], ent,
                             (graf or {}).get("tipo", "—"), trans))

    guion = {"lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
             "estilo": PALETA, "fondo_bloqueado": FONDO[0], "escenas": escenas}
    json.dump(guion, open(f"{dest}/guion.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # --- storyboard legible ---
    with open(f"{dest}/STORYBOARD.md", "w", encoding="utf-8") as f:
        f.write("# Episodio 03 · El banco · storyboard\n\n")
        f.write(f"**{len(escenas)} escenas · {total//60}:{total%60:02d} · "
                f"{len(usados)} imagenes a generar + 1 fondo**\n\n")
        f.write("Fondo bloqueado en las " + str(len(escenas)) +
                " escenas: `" + FONDO[0] + "`\n\n")
        f.write("| # | locucion | s | capas | entrada | motion graphic | corte |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for ident, txt, dur, tipo, arch, ent, g, tr in filas_md:
            capas = "solo codigo" if not arch else " + ".join(arch)
            f.write(f"| `{ident}` | {txt[:78]} | {dur} | {capas} | {ent} | "
                    f"{g} | {tr} |\n")

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

    print(f"\n{len(escenas)} escenas · {total}s ({total//60}:{total%60:02d})")
    print(f"{len(usados)+1} imagenes ({sum(1 for e in escenas if e['tipo']=='codigo')} "
          f"escenas son solo codigo)")
    print(f"-> {dest}/guion.json y {dest}/STORYBOARD.md")


if __name__ == "__main__":
    main()
