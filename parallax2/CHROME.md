# Generar las capas con /chrome y tus extensiones

Whisk y Meta AI no dan PNG con transparencia, así que los prompts salen
pidiendo **fondo verde croma plano**. `recortar.py` ya sabe quitarlo, y con
ilustración plana el croma sale limpio a la primera.

---

## 1. Conectar Chrome a Claude Code

Instala la extensión **Claude in Chrome**, y dentro de Claude Code:

```
/chrome
```

Controla tu sesión real: tus cookies, tus logins y **tus extensiones ya
cargadas**. No hace falta Playwright ni perfiles aparte.

Si `/chrome` te da problemas, la alternativa es `chrome-profile-mcp`, que
lanza Chrome con tu perfil:

```json
{ "mcpServers": { "chrome": {
  "type": "stdio", "command": "npx",
  "args": ["-y", "chrome-profile-mcp", "--profile", "Default"] } } }
```

## 2. Sacar la cola de prompts

```bash
python3 cola.py proyecto/guion.json --lote 20
```

Deja en `proyecto/cola/`:

- `prompts_01.txt` … `prompts_06.txt` — un prompt por línea, para pegar
- `prompts_NN.csv` — con nombre de archivo, si tu extensión lee columnas
- `cola.json` — el manifiesto con el **orden**, que es lo que importa

**Tandas de 20, no de 116.** Si algo se descuadra, pierdes veinte, no todo.

## 3. Generar

Vacía la carpeta de descargas antes de empezar, o anota la hora para usar
`--desde` después. Luego, en Claude Code:

```
Usa /chrome. Abre Whisk en una pestaña.
Lee proyecto/cola/prompts_01.txt.
Pega los 20 prompts en la extensión de generación masiva EN ESE ORDEN,
sin reordenarlos ni saltarte ninguno.
Lanza la generación y espera a que descarguen los 20 archivos.
Dime cuántos han caído.
```

Lo crítico es el orden: `recoger.py` empareja por fecha de descarga
ascendente contra `cola.json`. Si reordenas, se descuadra a partir de ahí.

## 4. Recoger y renombrar

Primero en seco, para ver el emparejamiento:

```bash
python3 recoger.py proyecto/guion.json --descargas ~/Downloads \
        --desde 2026-09-01T16:00
```

Revisa la lista. Si cuadra:

```bash
python3 recoger.py proyecto/guion.json --descargas ~/Downloads \
        --desde 2026-09-01T16:00 --aplicar
```

Para la segunda tanda, `--saltar 20`. Tercera, `--saltar 40`.

## 5. Seguir con el pipeline normal

```bash
python3 recortar.py  proyecto/guion.json    # quita el croma
python3 validar.py   proyecto/guion.json    # NO seguir si hay GRAVES
python3 previsual.py proyecto/guion.json    # MIRA las hojas
```

---

## Lo que se va a romper, y qué hacer

**Las descargas no cuadran con la cola.** Es el fallo más probable. Alguna
generación falló, o descargaste otra cosa a la vez. Usa `--desde` con la
hora exacta y trabaja por tandas cortas.

**Whisk devuelve varias variantes por prompt.** Entonces el orden se rompe
del todo. Configura la extensión para una imagen por prompt, o quédate solo
con la primera de cada grupo antes de recoger.

**Las descargas son JPG.** `recoger.py` los convierte a PNG, pero el JPG
mete artefactos en el borde del croma. Si tu extensión deja elegir, PNG.

**El croma no sale plano.** Con ilustración plana no debería pasar. Si pasa,
`recortar.py` aborta y te dice cuál. Regenera esa suelta y vuelve a
recoger con `--saltar`.

**Un ojo a las licencias.** Whisk es un producto experimental de Google
Labs y Meta AI marca sus salidas. Para vídeos monetizados conviene que
sepas bajo qué términos estás publicando; eso no lo puede resolver el
pipeline.
