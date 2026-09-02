# Los tres bugs del último render, medidos

Ninguno era de Claude Code. Los tres estaban en mi `guion.json`.

## 1. El texto salía dos veces

`"Tres coma vein'"` gigante y cortado, y debajo `"Tres coma veintidós"`
pequeño. Dos capas con la misma frase.

Causa: yo tenía un **tipo de gráfico** llamado `titular` y un **rol de
capa** también llamado `titular`. Colisión de nombres. La escena generaba
una capa `grafico` con `forma: titular` y tamaño de dato (px_rel 0,20) y
otra capa `titular` con tamaño de titular (px_rel 0,06).

29 escenas afectadas. El tipo de gráfico pasa a llamarse
`frase_destacada`, y en vez de crear una segunda capa, **asciende** el
titular a tamaño grande.

## 2. La hucha ocupaba media pantalla

110 capas de imagen estaban definidas **solo con altura**. Sin ancho, el
ancho sale de la proporción de la imagen, y una hucha apaisada a `h=0.56`
acaba midiendo el 90% del cuadro.

Ahora toda caja lleva `w`, `h` y una regla de `encaje`:
`contener` (cabe dentro sin deformarse) o `cubrir` (rellena, para el mar
y las superficies).

## 3. El texto encima del sujeto

Mi separador movía el bloque de texto, pero no podía **encogerlo**, así
que si ningún hueco libre le servía se quedaba donde estaba. Ahora prueba
cinco posiciones y cinco tamaños, con un suelo de 0,042 (45 px a 1080):
por debajo de eso no se lee, y en vez de encoger más, **acorta la frase**.

Y la marca de rotulador ya no flota: se pega debajo del bloque de texto, o
encima si abajo hay una imagen.

---

## Autocomprobación al construir

`banco.py` ahora verifica cinco invariantes y **se niega a escribir el
JSON** si alguno falla:

- ninguna capa de texto duplicada
- ninguna caja de imagen sin `w`, `h` y `encaje`
- ningún texto sin `px_rel`, `lineas` y `max_chars`
- ningún texto que pise una imagen más de un 15%
- ninguna escena sin contenido visible

Si vuelve a salir mal, lo primero es lanzar `python3 banco.py`. Si dice
"invariantes: correctos", el fallo ya no está en el JSON.

## Además: menos texto, y más grande

Pasaba de 199 escenas con texto a 145. En la referencia, de siete planos
solo cuatro tienen tipografía, y los que la tienen la tienen grande.
Ahora solo lleva titular la escena que se lo gana: un remate marcado, una
escena que es puro dato, o una frase de menos de 42 caracteres.
