# Qué hace ese vídeo distinto de lo que montamos

Tres decisiones suyas son **exactamente las contrarias** a las mías, y las
tres son mejores. No es cuestión de herramienta: es cuestión de criterio.

## 1. Fondo BLOQUEADO, no único por escena

> *"the reason why we have a locked background is because it gives that
> whole vox style animation where the background is static but then things
> are like moving in. So it looks like it's one continuous shot instead of
> having a lot of different cuts in the middle."*

Yo hice lo opuesto: tú me dijiste "cada escena debe ser única" y generé
**85 fondos distintos**. Los dos teníamos razón sobre el síntoma y yo me
equivoqué de solución. Lo que aburría no era el fondo repetido: era que
todo lo demás también se repetía.

Con un fondo fijo:
- desaparece el problema de coherencia de luz entre escenas
- desaparece el problema de resolución del fondo (uno solo, cuidado)
- de 116 PNG se baja a **1 fondo + 2 recortes por escena**
- el vídeo se lee como una toma continua, no como 225 cortes

## 2. Semitono en blanco y negro sobre los recortes

> *"you can tell claude code to make the image of Donald Trump in the
> folders black and white and give it a halftone pattern to finish (…) it
> gives that magazine sort of feel, that papery feel"*

**Esta es la respuesta a "las capas no pegan entre sí".** No era generarlas
en la misma tanda. Es pasarlas todas por el mismo filtro gráfico.

Dos fotos con luces distintas, de proveedores distintos y de sesiones
distintas, convertidas a semitono en blanco y negro, dejan de tener luz
propia. Ya no hay nada que casar. Tu biblioteca acumulada —la que dimos por
perdida— sirve tal cual pasándola por este filtro.

## 3. Trazo rojo desplazado detrás de cada recorte

> *"give me an offset red marker stroke behind each cutout"*

Hace dos cosas a la vez. Da el relieve característico del estilo, y **tapa
el borde del recorte**. Un alfa mediocre deja de importar porque nadie mira
el borde real, mira el trazo.

Ahí se van los problemas de croma, de rembg y de halo que llevamos
arrastrando desde el principio.

---

## Lo demás que hace bien

- **Voz primero, escenas después.** El guion se graba en ElevenLabs y las
  escenas se cortan contra la locución. Nosotros inventamos las duraciones
  y luego el rótulo llegaba cinco segundos antes de la frase.
- **Remotion Studio con controles de props.** Sliders de escala y posición
  que escriben de vuelta en el código. Es el bucle de trabajo que nos
  faltaba: yo ajustaba a ciegas y tú esperabas siete horas.
- **`spring()` y `interpolate()`.** Dos funciones para todo. Pop-in
  escalonado y movimientos. Nada de mis nueve tipos de entrada.
- **Carpeta por escena** con sus dos o tres recortes y el fondo compartido.

## Lo que sí conservamos

El troceo del guion en beats, la tabla de escena → capas → prompts (él la
tiene igual, mira la captura 4), el planificador de composición, y el
módulo de gráficos y tipografía.
