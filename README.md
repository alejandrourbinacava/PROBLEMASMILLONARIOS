# Problemas Millonarios — fábrica de vídeos

Cada mañana, GitHub Actions escribe un guion, lo narra, busca los clips, lo monta
y lo deja **subido en privado** en el canal con título, descripción, capítulos,
500 caracteres de etiquetas y miniatura. Tú entras, lo revisas y le das a publicar.

```
tema → guion → voz → b-roll → montaje → miniatura → metadatos → YouTube (privado)
```

---

## ⚠️ Lo primero: "borrador" no existe en la API

La API de YouTube **no puede crear borradores** de Studio. Lo más cercano —y lo que
hace esto— es subir el vídeo como **privado** con absolutamente todo relleno.
Aparece en tu Studio listo para revisar; solo tienes que cambiar la visibilidad.
Funcionalmente es tu borrador.

---

## Puesta en marcha (una sola vez)

### 1. Claves de API

| Secret | Dónde se saca | Coste |
|---|---|---|
| `GENAIPRO_API_KEY` | genaipro.io → avatar → Manage Account → API Key | según plan |
| `ANTHROPIC_API_KEY` | console.anthropic.com | ~0,20 € por guion |
| `PEXELS_API_KEY` | pexels.com/api | gratis |
| `PIXABAY_API_KEY` | pixabay.com/api/docs | gratis |
| `YT_CLIENT_ID` | ver paso 3 | gratis |
| `YT_CLIENT_SECRET` | ver paso 3 | gratis |
| `YT_REFRESH_TOKEN` | ver paso 3 | gratis |

Se meten en **Settings → Secrets and variables → Actions → New repository secret**.
En local, cópialas a un archivo `.env` (mira `.env.example`). El `.env` está en
`.gitignore`: nunca subas claves al repo.

### 2. Elegir la voz

Hay dos opciones, y se cambian con `voice.provider` en `config/channel.yml`:

**Gratis, sin clave** (`provider: "edge"`, es lo que viene puesto). Usa el
servicio de lectura de Microsoft Edge. Voces en español de España:
`es-ES-AlvaroNeural` (masculina), `es-ES-ElviraNeural` y `es-ES-XimenaNeural`.
Además devuelve la posición exacta de **cada palabra**, así que la imagen cuadra
con la voz al milisegundo en vez de por reparto proporcional.

**De pago** (`provider: "genaipro"`), con tu `GENAIPRO_API_KEY`:

```bash
pip install -r requirements.txt
python scripts/list_voices.py --demo 4
```

Genera cuatro muestras en `build/_voice_demos/`. Escúchalas y pega el `voice_id`
en `config/channel.yml` → `voice.voice_id`.

### 3. Permiso de YouTube

1. [Google Cloud Console](https://console.cloud.google.com/) → crea un proyecto.
2. APIs y servicios → Biblioteca → activa **YouTube Data API v3**.
3. Pantalla de consentimiento OAuth → tipo **Externo** → en *Usuarios de prueba*
   añade tu propio correo de Google.
4. Credenciales → Crear → **ID de cliente de OAuth** → tipo *Aplicación de
   escritorio*. Descarga el JSON y guárdalo como `client_secret.json` en la raíz.
5. Ejecuta:

```bash
python scripts/get_youtube_token.py
```

Se abre el navegador, das permiso con la cuenta del canal, y el script imprime los
tres valores `YT_*` para los secrets.

> Para poder poner la miniatura automáticamente el canal tiene que estar
> verificado por teléfono en [youtube.com/verify](https://youtube.com/verify).
> Si no lo está, el vídeo se sube igual y solo se salta la miniatura.

### 4. Música de fondo

Deja uno o varios `.mp3` en `assets/music/`. Sin música el vídeo sale solo con voz
y efectos, que suena plano. Fuentes seguras: la **Biblioteca de audio de YouTube**
(Studio → Audio library) o Pixabay Music. El pipeline elige una al azar por vídeo
y la baja sola cuando entra la voz.

### 4b. El sonido de transición

Hay dos caminos.

**Tus propios efectos** (lo que suena mejor). Descárgalos de donde quieras e
impórtalos:

```bash
python scripts/import_sfx.py --reset --whoosh "C:/ruta/Woosh.mp3" "C:/ruta/Otro.mp3" --pop "C:/ruta/Pop.wav" --impact "C:/ruta/Golpe.mp3"
```

El importador no se limita a copiar: **recorta el silencio inicial** (si el
efecto trae dos décimas de silencio delante, colocado sobre el corte suena
tarde y se pierde la transición), quita la cola muerta, **iguala el nivel** de
todos al mismo pico y detecta duplicados por contenido.

Los whoosh van a `assets/sfx/whoosh/` y el montaje **los rota** entre cortes,
eligiendo en cada uno el que quepa en el hueco hasta el siguiente. Repetir el
mismo golpe doscientas veces canta a plantilla.

`--pop` es el golpe que suena con cada cifra en pantalla, así que tiene que ser
muy corto y seco. `--shutter` solo se usa si reactivas el efecto del hook.

> Los efectos deben estar **commiteados en el repo**: GitHub Actions no ve tu
> carpeta de Descargas, y sin ellos el vídeo diario usaría los sintetizados.

**Sintetizados** (si no quieres buscar nada). Se generan solos, hay cuatro
estilos:

```bash
python scripts/preview_sfx.py
```

| Estilo | Cómo suena |
|---|---|
| `sweep` | Barrido ascendente con cuerpo. El estándar, y el que viene puesto. |
| `riser` | Sube y corta en seco. Muy agresivo, tipo tráiler. |
| `swish` | Corto y seco. El menos invasivo, para vídeos con mucho corte. |
| `sub` | Aire arriba y golpe de grave. El más "de canal grande". |

Escucha los `*_en_contexto.wav`, no los aislados: un whoosh suelto siempre suena
raro. Cuando elijas, ponlo en `config/channel.yml` → `audio.whoosh_style`.

`audio.whoosh_style` solo se usa si `assets/sfx/whoosh/` está vacío: tus
efectos siempre tienen prioridad.

### 5. Encender la automatización

El workflow `.github/workflows/daily-video.yml` ya está programado a las **05:30
UTC** (07:30 en España en verano). Para lanzarlo a mano: pestaña **Actions →
Vídeo diario → Run workflow**, donde puedes forzar un tema o desactivar la subida.

---

## Uso en local

```bash
python -m pipeline.cli --no-upload            # genera el vídeo sin publicarlo
python -m pipeline.cli --topic "Cuánto cuesta un submarino"
python -m pipeline.cli --resume               # retoma sin repetir guion ni voz
python scripts/smoke_render.py                # valida el montaje sin gastar API
python scripts/preview_sfx.py                 # compara los estilos de transición
python scripts/preview_hook.py build/<carpeta>  # escucha el hook ya montado
```

`preview_hook.py` es el atajo importante para afinar la intro: monta la voz real
con los obturadores y los whoosh en su sitio exacto, sin renderizar vídeo. Si el
hook no engancha en audio, no va a enganchar con clips encima.

`--resume` es el importante: si falla el montaje, no vuelve a pagar la síntesis de
voz. Cada paso deja su JSON en `build/<fecha>_<tema>/` y se relee.

---

## Cómo se consigue el estilo de edición

**Hook (primeros 9 s).** La voz va continua pero la imagen corta cada 0,28-0,55 s,
acelerando conforme avanza. Cada corte lleva flash blanco de un fotograma y un
golpe de zoom que se asienta. Son dos pistas independientes: por eso el guion
pide las frases y las imágenes en dos listas separadas.

El arranque **no lleva efecto de transición**: el sonido lo ponen las cifras.
Si lo quieres de vuelta, `edit.hook.shutter_sfx: true` y
`audio.opening_impact: true`.

Pasados esos 9 s los cortes **desaceleran** hasta el ritmo del cuerpo. Un hook
largo cortando a 0,3 s de principio a fin no engancha, machaca.

**Cuerpo.** Plano nuevo cada 3-5 s, atado a la escena de guion. Si una frase dura
más de 5 s se parte en dos planos. Zoom lento continuo alternando acercar/alejar,
transición sonora uno de cada dos cortes (en todos cansa), y subtítulos quemados
de 2-4 palabras con las cifras en amarillo de marca.

**Las cifras siempre salen en pantalla.** Si la narración dice un número, aparece
en el centro, enorme, con un golpe de sonido. Es lo que fija el dato y lo que
permite ver el vídeo sin audio.

Lo difícil es que el guion escribe los números **en letra** ("un millón
doscientos mil euros"), porque un TTS lee mucho mejor eso que "1.200.000". Así
que `pipeline/util/numbers.py` parsea numerales españoles y los pasa a dígitos:

| Narración | Rótulo |
|---|---|
| un millón doscientos mil euros | `1,2 M€` |
| cuarenta y cinco mil euros | `45.000 €` |
| entre el diez y el doce por ciento | `10-12%` |
| entre sesenta y setenta personas | `60-70 PERSONAS` |
| dieciocho horas | `18 H` |

Dos trampas del español que están resueltas: la "y" solo une decena con unidad
("cuarenta y cinco" = 45), nunca decena con decena — "sesenta y setenta" son dos
números de un rango, y sumarlos daría 130, justo lo contrario de lo que dice la
frase. Y "un" es a la vez el número uno y un artículo: "un McDonald's" no es una
cifra, "un millón" sí.

El rótulo aparece en el instante exacto en que se pronuncia el número, no al
empezar la frase, porque el paso de narración guarda la hora de cada palabra.

**Por qué todos los cortes son secos.** Un fundido encadenado obliga a recodificar
los 13 minutos enteros. Con cortes secos, cada plano se codifica una vez y se
pegan sin recodificar: el render baja de horas a minutos. La sensación de
transición la da el sonido, que es lo que realmente percibe el espectador.

---

## Qué tocar

Todo vive en **`config/channel.yml`**:

| Quiero... | Toco |
|---|---|
| Vídeos más largos o más cortos | `script.target_minutes` |
| Que corte más rápido | `edit.body.scene_min_s` / `scene_max_s` |
| Hook más largo o más agresivo | `edit.hook.*` |
| Menos whoosh | `edit.body.whoosh_every_n_cuts: 3` |
| Subtítulos más grandes | `captions.font_size` |
| Cifras más grandes o que duren más | `figures.font_size` / `figures.hold_s` |
| Quitar el golpe de las cifras | `figures.sound: false` |
| Quitar los rótulos de cifra | `figures.enabled: false` |
| Otro color de marca | `brand.accent` |
| Música más alta | `audio.music_volume_db` |
| Render más rápido (peor calidad) | `edit.master_preset: veryfast` |
| Voz más rápida | `voice.speed` |

**`config/topics.yml`** es la cola de temas. Se consumen en orden; cuando se
acaban, el modelo propone diez nuevos y los añade solo.

**`config/prompts/`** son los prompts del guion. Si los vídeos no te suenan como
quieres, se arregla ahí y no en el código.

---

## Los clips y las marcas registradas

Si el tema es una **marca registrada**, los bancos libres apenas tienen material.
Medido para McDonald's: de 266 candidatos, 50 son comida rápida y **solo 9
enseñan la marca**. Pixabay devuelve cero buscando "mcdonalds".

El pipeline lo gestiona así:

1. **Filtra por lo que se ve, no por lo que se buscó.** Pexels y Pixabay dan
   texto descriptivo de cada clip (Pexels en la URL, Pixabay en `tags`). Sin ese
   filtro entraban bosques nevados y restaurantes de manteles buscando
   "fast food restaurant".
2. **Reserva los clips de marca** (`broll_keywords_primary`) para el hook, los
   planos con cifra y las aperturas de capítulo, que es donde se mira.
3. **Rellena con contexto del tema** el resto.

Para llegar al 100% de marca solo hay un camino: **poner clips tuyos** en
`assets/broll/<slug-del-tema>/`. Se usan antes que nada del stock. Con 25-30
planos grabados con el móvil (fachada, mostrador, pantallas, bandeja) el vídeo
pasa a ser de marca casi entero, y valen para siempre.

Para temas que no son marca (yate, jet privado, gimnasio, estadio) esto no pasa:
el stock va sobrado.

---

## Si algo falla

| Síntoma | Causa habitual |
|---|---|
| `voice.voice_id está vacío` | Falta el paso 2 |
| `No hay ninguna clave de banco de vídeo` | Falta `PEXELS_API_KEY` / `PIXABAY_API_KEY` |
| Vídeo sin música | `assets/music/` vacío (paso 4) |
| Subtítulos con fuente rara | No se descargó Anton: `python scripts/fetch_fonts.py` |
| Miniatura no se sube | Canal sin verificar por teléfono |
| Muchos "relleno sintético" en el log | Las `broll_query` del guion no encuentran clips; suele arreglarse afinando `config/prompts/03_block.md` |
| Los clips no pegan con el tema | Faltan `broll_anchors` / `broll_keywords` en `config/topics.yml` |
| Un rótulo no aparece | Si lleva `%`, era el bug de `drawtext`; ya se pasa `expansion=none` |

Cuando el workflow falla sube un artefacto `diagnostico-N` con todos los JSON
intermedios: ahí se ve exactamente en qué paso se torció.

---

## Estructura

```
config/          channel.yml, topics.yml y los prompts
pipeline/
  cli.py         orquestador con --resume
  steps/         s1 tema · s2 guion · s3 voz · s4 b-roll
                 s5 montaje · s6 miniatura · s7 metadatos · s8 subida
  providers/     genaipro y freetts (voz) · llm · stock (Pexels/Pixabay) · youtube
  util/          ffmpeg · timing (sincronía) · captions (ASS)
                 numbers (numerales ES) · figures (rótulos de cifra)
                 sfx (diseño de sonido) · sfxbed (mezcla) · fonts
scripts/         list_voices · get_youtube_token · fetch_fonts
                 smoke_render · prune_cache · import_sfx
                 preview_sfx · preview_hook
config/manual/   guiones escritos a mano (script.provider: manual)
data/ledger.json temas publicados y clips usados (anti-repetición)
```
