Eres el guionista de **Problemas Millonarios**. Escribe el HOOK: los primeros
{hook_seconds} segundos del video. Es la parte mas importante del guion entero.

**Tema:** {title}
**Cifra total del video:** {total_figure}
**Comparacion final:** {comparison}

## Como se monta este hook
La VOZ va continua, rapida y a golpes. La IMAGEN va por su cuenta: cambia cada
0,3-0,5 segundos, con flash blanco y sonido de obturador de camara en cada corte.
Por eso te pido dos listas separadas y de longitud distinta.

## Regla de longitud (importante)
En {hook_seconds} segundos de narracion rapida en espanol caben unas
{hook_words} palabras. No te pases: si te pasas, el hook se corta a mitad de frase.

## 1. Narracion (`lines`)
1. Primera linea: la cifra mas brutal del video, sin contexto previo. Golpea y ya.
2. NO saludes. NO digas el nombre del canal. NO digas "hoy vamos a ver".
3. Frases de 4-9 palabras. Sujeto + verbo + cifra. Nada de subordinadas.
4. Entre 5 y 8 lineas, {hook_words} palabras en total como maximo.
5. La ultima linea abre el bucle principal: la pregunta que responde el video.
6. Espanol de Espana, tuteo, presente de indicativo.

## 2. Imagenes (`visuals`)
1. Exactamente {visual_count} busquedas de clips, en INGLES, de 2 a 5 palabras.
2. Cada una debe existir de verdad en un banco de video de stock: literal y
   filmable. "aerial view football stadium", "cash counting machine",
   "private jet taking off", "chef cooking restaurant kitchen".
   Nunca conceptos abstractos como "success" o "financial pressure", ni
   elementos de interfaz como "subscribe button": en los bancos eso son
   piezas sobre fondo verde y dejan la pantalla en verde.
3. Alterna escalas: plano general, detalle, gente, dinero, maquinaria, lujo.
   Que el ojo salte de una cosa a otra muy distinta en cada corte.
4. Las primeras 5 deben ser las mas espectaculares del video entero.

## Salida
Solo JSON valido, sin markdown, sin ```:

{{
  "lines": [
    {{"narration": "la frase, 4-9 palabras", "on_screen": "cifra corta o cadena vacia"}}
  ],
  "visuals": ["aerial view football stadium", "cash counting machine", "..."]
}}
