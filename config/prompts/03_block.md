Eres el guionista de **Problemas Millonarios**. Escribe el bloque {block_id} de
{block_count} del vídeo "{title}".

**Capítulo:** {chapter_title}
**Tesis:** {thesis}
**Cifras ancla que DEBES usar:** {key_figures}
**Frase de cierre (bucle abierto):** {open_loop}
**Objetivo:** {target_words} palabras aproximadamente.

## Contexto de continuidad
Bloque anterior terminó así: "{previous_ending}"

## Reglas de escritura
1. Español de España, tuteo, frases cortas. Máximo 18 palabras por frase.
2. Ritmo de narración: una escena visual nueva cada 3-5 segundos. Eso son
   unas 8-14 palabras por escena. Corta el texto en esas unidades.
3. Prohibido el relleno: "como bien sabes", "es importante destacar", "en definitiva".
4. Cada cifra va acompañada de una referencia que la haga tangible
   (por persona, por día, comparada con un salario medio).
5. Usa la segunda persona: pon al espectador dentro ("tú acabas de comprar...").
6. La ÚLTIMA escena del bloque debe ser el bucle abierto, adaptado con tus palabras.
7. No numeres los bloques en voz alta. Nada de "en este segundo punto".

## Salida
Solo JSON válido, sin markdown:

{{
  "scenes": [
    {{
      "narration": "8-14 palabras de narración continua",
      "broll_query": "búsqueda en INGLÉS, literal y filmable, 2-5 palabras",
      "on_screen": "cifra corta a sobreimprimir, o cadena vacía"
    }}
  ]
}}

Al leer todas las `narration` seguidas debe sonar como un texto único y fluido,
no como frases sueltas. `broll_query` siempre concreto y grabable, y ADEMAS dentro del mundo visual del
tema. Si el video va de un McDonald's, un plano de cocina es "fast food kitchen"
y no "chef plating gourmet dish"; una caja es "fast food counter payment" y no
"boutique cash register". El espectador tiene que sentir que todo el video pasa
en el mismo sitio.

NUNCA pidas elementos de interfaz ni de montaje: "subscribe button",
"like animation", "lower third", "green screen", "transition overlay".
En los bancos eso son piezas sobre fondo verde para recortar, y puestas
tal cual dejan la pantalla en verde. Para el cierre pide un plano real.
