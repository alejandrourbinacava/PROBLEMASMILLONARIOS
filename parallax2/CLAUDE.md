# Pipeline parallax 2.5D — reglas

Convertimos un guion de texto en vídeo estilo MagnatesMedia: capas PNG
recortadas que se mueven a distinta velocidad para simular profundidad.

## El proveedor de imágenes no lo eliges tú

Está en `proveedores.json`. Si el usuario tiene un agregador (kie.ai,
aimlapi, api.market, openrouter…), casi todos exponen un endpoint
compatible con OpenAI: se pone su `base_url` y su clave, y funciona con el
mismo código. **No hay que usar la API oficial de OpenAI ni recomendarla.**

Antes de generar nada, siempre:

```bash
python3 generar.py proyecto/guion.json --estimar
```

Eso cuenta imágenes y coste sin gastar un céntimo. Si el número de PNG
únicos se acerca al número de escenas, la biblioteca de capas está mal
montada y hay que arreglar eso antes de generar, no después.

## Tu único trabajo

Del guion sacas **guion.json**. Nada más. No escribes código de render,
no calculas posiciones, no tocas `render.py`.

```
guion.txt  --(tú)-->  guion.json  --generar.py-->  PNGs  --render.py-->  MP4
```

## La regla que no se salta

**Nunca escribes coordenadas, tamaños ni valores de zoom.**

Eso vive en `PRESETS_ROL` dentro de `render.py`, está calibrado y no se
toca. Tú eliges un `rol` de esta lista cerrada y ya:

| rol | qué es | ejemplo |
|---|---|---|
| `fondo` | cielo, horizonte, ambiente. Opaco, va detrás de todo | cielo nocturno |
| `medio_lejos` | algo lejano y pequeño dentro de la escena | una torre al fondo |
| `medio` | **el sujeto de la escena**. Casi siempre hay uno | la fachada del casino |
| `frente` | primer plano que enmarca, cortado por abajo | la multitud de espaldas |
| `frente_bajo` | primer plano muy cercano y bajo | barandilla, mesa, hombros |

Si crees que necesitas un valor distinto, lo pones en `ajuste` y lo dices
en voz alta para que lo revise un humano. No lo hagas por costumbre.

## Coherencia de lugar: no se mezclan sitios

Cada capa lleva `lugar` (exterior, interior_juego, interior_oficina,
interior_boveda, abstracto) y `clase` (arquitectura, mueble, objeto,
persona, alto).

**Todas las capas de una escena tienen que compartir lugar.** Una fachada
de casino con un primer plano de manos de crupier es imposible: son dos
sitios distintos. `construir_guion.py` aborta si lo detecta. Solo las capas
`abstracto` (mapas, balanzas, gráficas) valen en cualquier sitio.

Y la **clase** corrige la geometría: el rol dice a qué distancia está la
capa, la clase dice qué es. Un edificio se ancla arriba y ocupa el ancho;
una ruleta es un `mueble` y va apoyada abajo al 80%; un documento es un
`objeto` y flota centrado al 52%. Con una sola geometría para todo salen
edificios colgando del cielo y mesas a la altura de un tejado.

## La biblioteca se genera ENTERA, de una vez

Lo que hace que las capas de una escena peguen entre sí no es el
planificador: es que se generaran en la misma tanda, con el mismo `estilo`,
el mismo modelo y el mismo tamaño. Una biblioteca acumulada a lo largo de
varias sesiones tiene luces distintas en cada capa y **no hay forma de
arreglarlo después**.

```bash
python3 generar.py proyecto/guion.json --lote --proveedor fal_2k
```

`--lote` se niega a arrancar si encuentra PNG de tandas anteriores sin
manifiesto, y al terminar escribe `crudas/lote.json` con el estilo, el
modelo y el tamaño usados. `validar.py` compara ese manifiesto con el
guion: si el estilo no coincide, es GRAVE.

Cambiar el `estilo` de un episodio obliga a regenerar la biblioteca
entera. No se parchea una capa suelta.

## Resolución: 1536 px no basta

Los encuadres cerrados amplían mucho. Lo que hace falta de fuente:

| rol | ancho mínimo del PNG |
|---|---|
| `frente` | **2400 px** |
| `medio` | 2000 px |
| `fondo` | 1900 px |

`gpt-image-1` solo llega a 1536 px, y de ahí venían los PNG blandos.
Genera a 2K con Flux en fal o Seedream, o pasa las crudas por un escalador
antes de `recortar.py`.

`planificar.py` mide los PNG en disco y **descarta los encuadres que
pedirían más resolución de la que hay**, así que con imágenes pequeñas el
vídeo saldrá más abierto pero nítido, en vez de cerrado y blando.

## Profundidad de campo

Cada rol tiene su desenfoque y su atenuación, en `PRESETS_ROL`:

| rol | desenfoque | oscurecido |
|---|---|---|
| `fondo` | 11 px | 30% |
| `medio_lejos` | 4 px | 12% |
| `medio` | **0 (nítido)** | 0% |
| `frente` | 2,6 px | 22% |
| `frente_bajo` | 6 px | 34% |

Tres roles más que este pipeline añadió y la tabla de arriba no recoge:
`horizonte` (7 px, 22%) — el plano sobre el que se apoya el sujeto, edificios
vecinos o mesa; `figura` (1,2 px, 8%) — una persona de pie dentro de la
escena; y `suelo` (0 px, 0%) — un objeto apoyado, que **también es sujeto** y
por eso va nítido.

Solo el sujeto —`medio` y `suelo`— va nítido. El fondo desenfocado y bajado de
luz es lo que hace que el sujeto destaque, y separa las capas más que
cualquier movimiento de cámara. El primer plano lleva un desenfoque leve
porque está demasiado cerca del objetivo.

Se puede pisar por capa con `"desenfoque"` y `"oscurecer"` en el JSON,
pero rara vez hace falta.

## El montaje no se rota, se planifica

`planificar.py` reparte composición, movimiento, entrada, efecto y grade
sobre un `guion.json` ya construido. **No lo hagas a mano y no uses una
rotación módulo N**: eso garantiza que dos escenas seguidas no sean
iguales, pero produce un ciclo mecánico, no un montaje.

Primero decide el **tipo de escena**, que es lo que evita que las 225 se
lean igual por mucho que cambie el encuadre:

| tipo | capas | para qué |
|---|---|---|
| `pleno` | fondo + sujeto + primer plano | el plano de referencia |
| `detalle` | sujeto + primer plano, sin fondo | acercarse, poca profundidad |
| `silueta` | fondo + primer plano, sin sujeto | respirar entre dos ideas |
| `grafico` | solo fondo, el dato ocupa la pantalla | cifras |
| `rotulo` | solo fondo, una frase sola | remates de capítulo |
| `clip` | metraje de stock | cuando hay material real |

Nunca dos escenas seguidas del mismo tipo distinto de `pleno`: si se
encadenan, dejan de ser un cambio de registro. Los `rotulo` caen siempre en
el último plano de cada capítulo, con la cláusula más corta de la locución.

Las demás reglas:

- **Escala** — alterna ancho / medio / cerca siguiendo una respiración por
  capítulo. Cuando una idea se parte en varios planos, los planos **se
  acercan** (ancho → medio → cerca): eso se lee como intención, no como un
  salto suelto.
- **Lado** — ciclo I → D → C → D → I → C, y nunca el mismo lado dos veces
  seguidas. El centro es un descanso, no el valor por defecto. Si más de un
  tercio de las escenas cae centrada, el vídeo vuelve a leerse como una
  sola composición repetida.
- **Movimiento** — acorde al lado. Si el sujeto cae a la izquierda, la
  cámara deriva a la derecha: deja aire delante del sujeto en vez de
  comérselo.
- **Entrada y efecto** — nunca los dos últimos usados. Los efectos solo en
  una de cada tres escenas.
- **Grade** — uno por capítulo, no por escena.

```bash
python3 construir_guion.py
python3 planificar.py proyecto/guion.json
python3 previsual.py  proyecto/guion.json
```

## Cada escena tiene que ser distinta

Tres campos independientes lo garantizan. Ninguno puede repetirse tres
veces seguidas:

- **`composicion`** — dónde cae el peso del encuadre: `centrado`,
  `izquierda`, `derecha`, `alto`, `bajo`, `cerca`, `lejos`, `diagonal`.
  Sin esto las 85 escenas son el mismo plano con distinta foto.
- **`movimiento`** — ver abajo.
- **`fondo` propio** — cada escena genera el suyo. Nunca se comparte un
  fondo entre escenas, ni siquiera dentro del mismo capítulo.

Las capas de `medio` y `frente` sí pueden repetirse, pero solo cuando es
un retorno deliberado (la fachada del gancho volviendo en el cierre). Si
se repite por comodidad, es un error.

## Personas en primer plano

Una capa `frente` con gente se describe **siempre** como *de espaldas,
solo cabezas y hombros* o *solo manos y antebrazos, sin torso ni cabeza*.

Nunca "un crupier", "una persona", "un hombre de traje". El recorte deja
el borde superior de la capa a media pantalla, y si ahí hay un cuello, el
resultado es un cuerpo decapitado. `validar.py` lo detecta midiendo si ese
borde es recto y macizo, pero es mejor no generarlo.

## Duración: 4 segundos es el techo

**El dinamismo sale de cortar más, no de mover más la cámara.** Una idea de
doce segundos se cuenta en tres planos distintos, no en uno largo con más
zoom. `construir_guion.py` trocea solo, y cada trozo cambia de movimiento y
de composición: se lee como un cambio de plano, no como un corte perdido.

Solo los clips de stock pueden pasar de 4 s, porque tienen movimiento
propio. `validar.py` lo marca como GRAVE.

## Las capas entran duro, y escalonadas

Ninguna capa entra con `ninguna` ni con `fundido`. Las entradas buenas
**rebasan el reposo y vuelven**, que es lo que se lee como vivo:

`golpe` (escala desde 1,3 con rebasamiento), `latigo_izq` / `latigo_der`
(entra lanzada desde un lado con desenfoque de movimiento), `desplome`
(cae desde arriba y asienta), `rebote`.

Duran 0,34 s, no más: una entrada larga se lee como estática. Y llevan un
escalón de 0,09 s entre capa y capa, de atrás hacia delante. **Que no
entren a la vez es la mitad del efecto**; entrando juntas se lee como una
sola imagen apareciendo.

## Motion graphics: toda cifra va en pantalla

Las cifras son el argumento del vídeo. Dejarlas solo en la voz las
desperdicia, y además rompe la monotonía de que todo sea parallax.

Diez tipos, en `grafico`:

- **`contador`** — el número cuenta desde cero. Para cifras sueltas grandes.
- **`barras`** — comparación entre 2 y 4 elementos, crecen escalonadas.
  Con `destacar` se pinta una de otro color. La etiqueta va **encima** de la
  barra, no a su izquierda: a la izquierda el ancho depende de lo larga que
  sea y «hoteles con su nombre» salió en pantalla como «oteles con su
  nombre».
- **`anillo`** — un porcentaje. Para cuando la cifra *es* la frase.
- **`reparto`** — una barra partida: cuánto se lleva cada uno.
- **`factura`** — **el gráfico del canal.** Las líneas que ya llevas en gris
  y la nueva en ámbar, con puntos guía y el total debajo. El formato es
  «cuánto cuesta comprar y mantener X» y lo que engancha no es cada cifra
  suelta: es ver la cuenta crecer. Una por capítulo, arrastrando el total.
- **`apilada`** — una barra partida en tramos con su leyenda debajo. Para
  los desgloses: «de 7,66 M€ que entran, 383.000 se los lleva el letrero».
- **`rejilla`** — cuenta de unidades. 200 cuadraditos son 200 personas y se
  entienden sin leer la cifra; un porcentaje en un anillo es abstracto.
- **`flecha`** — quién le paga a quién. Dos cajas y una flecha que viaja.
- **`mapa`** — la silueta peninsular con puntos que se encienden y se apagan.
- **`ilustracion`** — un icono dentro de un medallón, con su anillo de
  progreso y, si la frase dice que algo sube o cae, una chapa con la flecha.
  Ver más abajo.

Todos se dibujan sobre la misma **tarjeta**: sombra, degradado vertical, filo
de luz arriba y galón de acento a la izquierda. Es lo que hace que un mapa y
una factura parezcan del mismo vídeo. No inventes otro panel.

Y la jerarquía se hace con el **peso de la letra**, no con el color:
Poppins Black para la cifra, SemiBold para los importes de una lista y Medium
para etiquetas y pies. Están las tres en `assets/fonts` y las resuelve
`efectos._fuente(px, peso)`. Nunca una ruta absoluta de fuente: las dos que
había (`/usr/share/fonts/...`) no existen ni en Windows ni en el runner, así
que durante meses todos los gráficos se renderizaron con la de reserva.

```json
"grafico": { "tipo": "anillo", "valor": 62.5, "sufijo": "%",
             "color": [255,110,86], "pie": "el tipo máximo de Maryland",
             "y": 0.48, "retardo": 0.5, "entrada": "golpe" }
```

`construir_guion.py` los engancha solo buscando la cifra en la locución.
Si al menos el 40% de las escenas con números no lleva gráfico,
`validar.py` avisa.

## El plató: cuando el fondo tiene que ser la marca

Un gráfico encima de un clip de stock siempre pierde. El clip se mueve, tiene
detalle en todas las frecuencias y trae su propia luz, así que la tarjeta
necesita opacidad y sombra solo para poder leerse — y aun así el ojo se va al
metraje. Y encima obliga a buscarle un plano que «pegue» a una cifra, que es
de donde salían las escenas que no venían a cuento.

Cuando el contenido **es** el dato, el plano no lleva metraje: lleva el plató.

```json
"fondo": "plato", "fondo_color": [255,196,90],
"fondo_titulo": "capítulo 1 · el edificio", "fondo_fase": 0.42
```

Es un degradado del canal, una retícula que deriva, la marca de agua del euro,
una luz que cruza el plano una vez, y abajo el rótulo **PROBLEMAS
MILLONARIOS / EL PRECIO DE SER EL DUEÑO**. Todo dibujado por código: no hay
ni un asset. `fondo_fase` cambia el sentido de la luz y de la retícula para
que veinte planos de plató no se lean como una plantilla.

Si algún día hay logotipo de verdad, se deja en `assets/brand/logo.png` y el
plató lo usa en lugar del monograma.

Una ficha de `graficos_*.json` lo pide con `"fondo": true` o
`"fondo": {"titulo": "..."}`. El título **solo** cuando la tarjeta no lleva
epígrafe propio: repetir «lo que has comprado» arriba y dentro se lee como un
fallo de montaje.

## Si no hay clip de calidad, se ILUSTRA

**La regla nueva del canal.** Una frase sin metraje que le pegue no se rellena
con el clip que toque por tema —de ahí salió el señor cortando pan en el
episodio de aerolíneas— ni se deja en texto blanco sobre negro. Se ilustra.

`vestir.py` lo hace solo: el plató, un medallón con el icono de lo que se está
diciendo, la flecha de dirección si la frase dice que algo sube o cae, y el
titular debajo. Veintitrés planos del episodio del hotel, que antes eran
veintitrés diapositivas.

El icono sale de `iconos.py`, que trae veintinueve pictogramas de línea y un
diccionario de español. Dos cosas que hay que respetar al tocarlo:

- **Lo específico va arriba en `TABLA`.** «hipoteca» tiene que caer en banco y
  no en euro aunque la frase diga las dos cosas.
- **Nada de palabras comunes.** «más», «menos» y «pierde» estaban en subir y
  bajar, y «cuando pierdes, cobran, y cuando ganas, cobran más» salía con una
  flecha de crecimiento.

Y hay un **suelo por episodio** (`iconos.del_tema`): si la frase no dice de
qué va, el icono es el del tema del vídeo. En un episodio sobre un hotel, un
hotel siempre viene a cuento; el círculo genérico no dice nada nunca. Eso pasó
ocho frases de veintitrés del genérico a su icono real.

Si el plano ya lleva un gráfico —`motion_banco` le puso un contador porque la
frase dice una cifra— se respeta: una cifra contada siempre gana a un icono.

## Los rótulos entran cuando se dicen

No pongas `retardo` a mano. Si lo dejas fuera, el render localiza la
primera palabra del rótulo dentro de la locución de la escena y convierte
su posición a segundos con el ritmo del guion (140 ppm). Un rótulo que
dice "una fórmula" sobre una locución de nueve palabras entra a los 0,86 s,
no a los 0,35.

Para que eso funcione, **la primera palabra del rótulo tiene que aparecer
literalmente en el campo `texto` de la escena**. `validar.py` avisa si no.

Y las locuciones van **con tildes**. El rótulo se dibuja tal cual: si
escribes "formula" en el JSON, en pantalla sale "formula".

## Acabado: lo que separa un vídeo de aficionado de uno premium

Cuatro campos opcionales por escena. Ninguno es decoración: son lo que
hace que 85 planos fijos parezcan una producción.

**`grade`** — la gradación de color, elegida **por capítulo**, no por
escena. `dorado_noche`, `frio_institucional`, `verde_dinero`,
`rojo_alerta`, `sepia_archivo`, `acero`, `neutro`. Cambiar de grade marca
un cambio de tema: el capítulo del casino va cálido, el de la licencia va
frío e institucional, el del Estado va acero. Menos de la mitad de las
escenas deben quedar en `neutro`.

**`efectos`** — lista de capas de pantalla, sumadas como luz:
`brasas`, `polvo`, `ceniza`, `bokeh`, `chispas`, `billetes`, `fuga_luz`.
Se eligen por lo que cuenta la escena, no por bonitas: `polvo` en el
despacho de expedientes, `billetes` cuando se habla de dinero, `brasas`
solo si hay fuego o tensión. Una o dos por escena, nunca cuatro.

**`texto_pantalla`** — las cifras del guion van en pantalla. Las palabras
entre `*asteriscos*` salen en color de acento.

```json
"texto_pantalla": {
  "texto": "1.236 *millones*", "px": 150, "y": 0.30,
  "acento": [255,196,90], "estilo": "sube", "retardo": 0.6
}
```

El rótulo **se encoge solo** hasta caber en el encuadre, así que 34
caracteres es una guía y no un acantilado. `retardo` es lo que tarda en
aparecer tras el inicio de la escena: nunca a cero, el texto entra
**después** de que el ojo haya leído la imagen.

**`entrada`** / **`salida`** por capa — `fundido`, `sube`, `baja`,
`izquierda`, `derecha`, `escala`, `escala_atras`, `desenfoque`, `ninguna`.
Hay valores por defecto según el rol (el fondo no entra nunca, el frente
sube), así que solo se declaran cuando quieres otra cosa.

## Clips de stock

Cuando una escena es fácil de cubrir con metraje real, se usa en vez de
capas:

```json
{ "id": "cap4_03", "duracion": 8, "movimiento": "push_in",
  "clip": "stock/dinero_contando.mp4", "clip_desde": 2.5,
  "grade": "verde_dinero", "efectos": ["polvo"], "capas": [] }
```

**Un clip de stock sin `grade` canta a kilómetros.** El grade, el grano y
la viñeta son lo que lo integra con las escenas de parallax; el render
también le aplica un Ken Burns suave por lo mismo. `validar.py` avisa si
te dejas un clip en `neutro`.

## Estructura de una escena

Una frase o idea del guion = una escena. Entre 6 y 12 segundos.

```json
{
  "id": "03_ruina",
  "texto": "Para 1987 lo había perdido todo.",
  "duracion": 8,
  "movimiento": "push_in",
  "capas": [
    { "rol": "fondo",  "archivo": "03_cielo.png",  "prompt": "..." },
    { "rol": "medio",  "archivo": "03_sujeto.png", "prompt": "..." },
    { "rol": "frente", "archivo": "03_frente.png", "prompt": "..." }
  ]
}
```

Movimientos: `push_in` (tensión), `pull_out` (revelar, cierres),
`drift_izq` / `drift_der` (cambio de tema), `subir` / `bajar` (revelar
altura o peso), `estatico` (cuando la voz lleva mucha información), y
`contra_izq` / `contra_der`, que mueven fondo y frente en sentidos
opuestos — es el que más separa las capas y el que hay que usar cuando una
escena se ve plana.

Ninguno debe pasar del 40% de las escenas.

**Mínimo 2 capas, ideal 3, máximo 5.** Con una sola capa no hay parallax,
es una foto con zoom. Con seis se convierte en papilla.

## Coherencia entre escenas

El campo `estilo` de la raíz se concatena a **todos** los prompts. Ahí van
la hora del día, la temperatura de color, la dirección de la luz y el
grado de realismo. Escríbelo una vez, al principio, y no lo cambies a
mitad del vídeo salvo que la narración cambie de época o de sitio.

Esto es lo que evita el fondo que no pega con el sujeto.

## Prompts de imagen

Todas las imágenes se generan **opacas**. Las capas que no son `fondo` se
generan sobre **croma verde** y se recortan después en local con
`recortar.py`. Nunca se le pide transparencia al generador: sale peor, es
más caro y te ata a un proveedor concreto.

`generar.py` ya añade solo las coletillas de encuadre y de croma según el
rol. Tú describes **solo el contenido**.

- Sé concreto con el encuadre: "vista frontal simétrica", "plano lateral".
- El `fondo` no lleva nunca el sujeto principal dentro.
- El `frente` se describe como franja ancha, y se asume cortado por abajo.
- Nada de texto en las imágenes salvo que sea el punto de la escena.

## Comprobar antes de dar nada por bueno

```bash
python3 generar.py  proyecto/guion.json --proveedor fal   # PNG opacos -> crudas/
python3 recortar.py proyecto/guion.json                   # quita el croma
python3 validar.py  proyecto/guion.json                   # ANTES de renderizar
python3 render_par.py proyecto/guion.json --procesos 8    # clips en _escenas/
python3 montar.py   proyecto/guion.json ep02.mp4          # deslizamientos
```

`validar.py` devuelve código 1 si hay algo GRAVE. No se renderiza con
graves pendientes: son horas de máquina tiradas.

Para regenerar una sola imagen que no ha salido bien:

```bash
rm proyecto/m_ruleta.png proyecto/crudas/m_ruleta.png
python3 generar.py proyecto/guion.json --solo m_ruleta.png
python3 recortar.py proyecto/guion.json
rm _escenas/*ruleta*   # el render es reanudable, solo repite lo borrado
```

Mira el fotograma. Si algo baila, es el PNG, no el render:

- **Capa demasiado pequeña o mal colocada** → el PNG trae un halo de alfa
  casi invisible y el recorte se va. `render.py` ya umbraliza a 40, pero
  si el sujeto sale con bordes muy difuminados, regenéralo.
- **Se ve el fondo a través del sujeto** → alfa a 252 en vez de 255.
  Corregido en el render, pero indica un recorte flojo.
- **Manchón verde en el plano** → el croma no se quitó. `recortar.py` ahora
  aborta con error en vez de dejarlo pasar; si aborta, regenera esa imagen
  con un verde plano de verdad, no la fuerces.
- **Un rectángulo más claro sobre el cielo** → esa capa no se recortó y
  conserva su propio fondo. Mismo remedio: no renderizar hasta arreglarlo.
- **Aviso "se amplía x1.9"** → el PNG es demasiado chico para su rol.
  Regenera a 1536x1024, no lo estires.
- **Bordes vacíos al final del movimiento** → falta sangrado. Es un
  problema de `ajuste`, no lo arregles moviendo la capa a mano.
