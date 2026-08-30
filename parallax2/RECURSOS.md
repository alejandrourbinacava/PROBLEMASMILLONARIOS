# Biblioteca de recursos de montaje

Lo que usan los editores profesionales de documental animado, y en qué estado
está cada cosa en este motor. Tres columnas mentales: **hecho**, **se puede
hacer**, **no se puede** (y por qué).

---

## 1. Transiciones

### 1.1 Las que ya rota el motor

`montar.py` gira una rueda de siete, deliberadamente de familias distintas para
que el ritmo no sea adivinable. Alternar sólo `slideleft`/`slideright` —lo que
hacía antes— es el mismo gesto en espejo, y a los veinte cortes el ojo lo
predice.

| transición | familia | cuándo cae bien |
|---|---|---|
| `slideleft` / `slideright` | empujón lateral | corte normal con energía |
| `smoothleft` / `smoothright` | barrido suave | cambio de idea dentro del mismo tema |
| `wipeleft` | barrido duro | contraste, comparación |
| `circleopen` | apertura | revelación, "y entonces resulta que…" |
| `dissolve` | disolvencia | paso de tiempo |
| `fadeblack` | fundido a negro | **fin de capítulo** (lo pone `cierra_bloque`) |
| `corte` | seco, sin solape | dentro de un hilo y en los latigazos |

### 1.2 Las dos avanzadas, ya implementadas

**Transición invisible / match cut.** Varias escenas comparten el campo `hilo`.
El motor las trata como **un solo movimiento de cámara repartido entre ellas**:
la escena 2 arranca exactamente donde la 1 lo dejó, las capas no vuelven a
entrar, y el corte va seco. El ojo lee una panorámica continua, no un corte. Es
la técnica de "plano secuencia" de *1917* aplicada a capas.
→ `render.preparar()`, campo `"hilo"`.

**Whip pan (barrido con desenfoque).** La escena declara `"latigo": "izq"` o
`"der"`. Sale barriendo a toda velocidad con desenfoque de movimiento, y la
siguiente entra con el mismo barrido en el mismo sentido. Es lo que en After
Effects se hace con Motion Tile + Directional Blur. Lo que lo vende es el
desenfoque, no el desplazamiento: por eso el radio crece con la **velocidad** y
no con la distancia recorrida. → `efectos.latigo()`, campo `"latigo"`.

### 1.3 Disponibles en ffmpeg y sin usar todavía

Las 58 de `xfade`. Las que valdrían la pena, por familia:

- **Deslizamiento**: `slideup`, `slidedown`, `coverleft/right/up/down`,
  `revealleft/right/up/down`
- **Barrido**: `wipeup`, `wipedown`, `wipetl/tr/bl/br`, `hlslice`, `hrslice`,
  `vuslice`, `vdslice`
- **Forma**: `circlecrop`, `rectcrop`, `circleclose`, `vertopen/close`,
  `horzopen/close`, `radial`, `diagtl/tr/bl/br`
- **Óptica**: `hblur`, `pixelize`, `distance`, `zoomin`, `squeezeh/v`
- **Luz**: `fadewhite`, `fadegrays`, `fadefast`, `fadeslow`
- **Viento**: `hlwind`, `hrwind`, `vuwind`, `vdwind`

Cualquiera se pone por escena con `"transicion": "<nombre>"`.

### 1.4 Lo que falta y se puede hacer

- **Luma wipe** con textura (tinta, humo, rayado de película): `xfade` acepta
  `transition=custom` con una expresión, o se compone con `maskedmerge`.
- **Light leak / destello en el corte**: ya existe `efectos.fuga_luz()`; falta
  engancharlo al corte en vez de a la escena entera.
- **Morph cut**: caro y frágil. Sólo tiene sentido en un corte concreto muy
  preparado, nunca como recurso de rotación.
- **J-cut y L-cut** (el audio del plano siguiente entra antes que la imagen, o
  el del anterior se prolonga). Es de sonido, no de imagen, y es de lo que más
  disimula un corte. Hoy `voz.py` alinea cada frase con su plano; adelantar la
  voz 300-500 ms en los cambios de tema daría el J-cut.

---

## 2. Movimiento y dinamismo

### 2.1 Ya en el motor

- **Parallax por profundidad**: cada rol se desplaza y escala distinto
  (`PRESETS_ROL`). El frente se mueve casi cinco veces más que el fondo.
- **Movimientos de cámara**: `push_in`, `pull_out`, `drift_izq/der`,
  `contra_izq/der` (fondo y frente en sentidos **opuestos**, el que más separa
  las capas), `subir`, `bajar`, `estatico`.
- **Composición**: ocho encuadres (`centrado`, `izquierda`, `cerca`, `derecha`,
  `alto`, `diagonal`, `bajo`, `lejos`). Es lo que evita que 225 escenas sean el
  mismo plano con distinta foto.
- **Entradas duras por capa**: `golpe`, `latigo_izq/der`, `desplome`, `rebote`,
  escalonadas 90 ms entre capa y capa. Nada entra con un fundido.
- **Techo de 4 s por plano**: el dinamismo sale de cortar más, no de mover más
  la cámara dentro del mismo encuadre.

### 2.2 Principios de retención que gobiernan lo anterior

- El primer bloque va con cambio de plano casi constante: ahí es donde se
  pierde la audiencia.
- **Interrupción de patrón cada 20-40 s**: un corte a otra cosa, un zoom, un
  gráfico, un efecto de sonido. Aquí lo dan los contadores, los rótulos, los
  cambios de grade y los latigazos.
- El cuadro **nunca** se queda quieto mientras se desarrolla una idea.
- No hay número mágico de cortes por minuto: importa el ritmo, no la cuenta. Un
  tema técnico aguanta más calma que uno de entretenimiento.

### 2.3 Lo que falta

- **Speed ramp**: acelerar el final de un plano justo antes del corte. Se hace
  variando el paso del tiempo dentro de `render_escena`.
- **Tipografía cinética** de verdad: hoy el rótulo entra entero. Palabra a
  palabra es posible — edge-tts ya devuelve el instante de cada palabra.
- **Congelado + rótulo**: parar la imagen cuando entra un dato.
- **Punch-in escalonado**: dos o tres zooms secos sobre el mismo plano.

---

## 3. Color

`efectos.GRADES` — cada entrada tiñe las sombras de un color y las luces del
complementario, que es de donde sale casi todo el "aspecto premium".

| grade | para qué |
|---|---|
| `dorado_noche` | casino, lujo, noche |
| `verde_dinero` | dinero, ingresos |
| `frio_institucional` | burocracia, licencias, tribunales |
| `sepia_archivo` | pasado, archivo |
| `acero` | obra, industria |
| `rojo_alerta` | giro, amenaza |
| `neutro` | nunca en un plano final |

Se elige **por capítulo**, no por escena: es lo que divide el episodio en actos
sin tener que anunciarlo. Un clip de stock sin grade canta a kilómetros.

---

## 4. Partículas y overlays

`efectos.PARTICULAS`, en modo pantalla (sólo suman luz, nunca oscurecen):
`brasas`, `polvo`, `ceniza`, `bokeh`, `chispas`, `billetes`. Más `fuga_luz`
aparte.

Rotan **dentro de cada capítulo**. El mismo polvo subiendo durante trece
minutos deja de leerse como atmósfera y se lee como un filtro puesto encima.

Faltan por hacer: lluvia, humo bajo, grano de proyector, viñeta animada,
scanlines para material "de archivo".

---

## 5. Sonido

### 5.1 Ya en `sonido.py`

- **Golpe en cada corte**, adelantado 120 ms. Un efecto que suena justo en el
  corte llega tarde al oído: tiene ataque, y si el ataque cae en el fotograma
  del cambio se percibe después de verlo.
- **Cuatro golpes distintos en rotación.** Repetir el mismo whoosh ochenta
  veces cansa el oído y aplana la dinámica.
- **Impacto cuando entra una cifra**, **pop cuando entra un rótulo**. La regla
  profesional es *whoosh de movimiento + impacto de aterrizaje*: el whoosh
  acompaña el desplazamiento, el impacto marca el instante en que la cosa se
  posa.
- **Música en bucle** por debajo de todo, muy baja.
- **Ducking**: la voz comprime efectos y música con `sidechaincompress`. La
  música se aparta más que los efectos, porque es lecho y no evento.

### 5.2 Errores clásicos que el diseño evita

- Sonido de movimiento constante: cansa el oído y aplana la dinámica.
- Whoosh brillante bajo una escena oscura: rompe la inmersión.
- Efectos en el mismo rango de frecuencia: emborronan la mezcla.

### 5.3 Lo que falta

- **Riser** antes de una cifra grande: 2-3 s de tensión que resuelven en el
  impacto.
- **Stinger** musical en el cambio de capítulo.
- **J-cut de voz** en los cambios de tema.
- Música distinta por capítulo: hay seis pistas en `assets/music`.

---

## 6. Fuentes

- [Whip pan en After Effects y Premiere — ProVideo Coalition](https://www.provideocoalition.com/whip-swish-pans-in-after-effects-premiere/)
- [Cómo hacer un whip pan — No Film School](https://nofilmschool.com/how-to-do-a-whip-pan)
- [Tipos de transiciones de montaje — StudioBinder](https://www.studiobinder.com/blog/types-of-editing-transitions-in-film/)
- [Guía de transiciones — Backstage](https://www.backstage.com/magazine/article/video-transitions-75727/)
- [Editar como MagnatesMedia — Motion Street](https://motionstreet.thinkingtales.com/article/edit-like-magnates-media-ep01)
- [Montaje para retención: ritmo, interrupciones de patrón, b-roll — MonitorYT](https://monitoryt.com/blog/editing-for-retention)
- [Retención en YouTube — Pixflow](https://pixflow.net/blog/youtube-video-retention-editing/)
- [Sonidos de transición para motion graphics — Pixflow](https://pixflow.net/blog/enhancing-motion-graphics-with-cinematic-transition-sounds/)
- [Whooshes en animación y VFX — AnimationXpress](https://www.animationxpress.com/latest-news/the-growing-role-of-whooshes-sound-effects-in-modern-animation-and-vfx/)
- [Tipografía cinética — Wikipedia](https://en.wikipedia.org/wiki/Kinetic_typography)
