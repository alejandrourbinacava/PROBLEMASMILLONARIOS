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

Cuatro tipos, en `grafico`:

- **`contador`** — el número cuenta desde cero. Para cifras sueltas grandes.
- **`barras`** — comparación entre 2 y 4 elementos, crecen escalonadas.
  Con `destacar` se pinta una de otro color.
- **`anillo`** — un porcentaje. Para cuando la cifra *es* la frase.
- **`reparto`** — una barra partida: cuánto se lleva cada uno.

```json
"grafico": { "tipo": "anillo", "valor": 62.5, "sufijo": "%",
             "color": [255,110,86], "pie": "el tipo máximo de Maryland",
             "y": 0.48, "retardo": 0.5, "entrada": "golpe" }
```

`construir_guion.py` los engancha solo buscando la cifra en la locución.
Si al menos el 40% de las escenas con números no lleva gráfico,
`validar.py` avisa.

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

Máximo 34 caracteres o se sale del encuadre. `retardo` es lo que tarda en
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
