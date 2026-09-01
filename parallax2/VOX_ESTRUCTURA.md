# Cómo estructura él las escenas

Sacado de las capturas 3, 4 y 5. Cinco cosas que yo tenía al revés.

---

## 1. El orden de capas está INVERTIDO

Su leyenda, literal (captura 5):

> **Background** — locked paper texture, continuous across every scene
> **Midground** — the subjects, dropped in as cut-outs with a red marker stroke
> **Foreground** — **occludes the lower body** and anchors the shot

| | lo nuestro | lo suyo |
|---|---|---|
| fondo | cielo generado, uno por escena | papel, **el mismo siempre** |
| medio | el edificio | **los sujetos** (personas) |
| frente | la multitud | **la estructura** (edificio) |

En su escena 01, la Casa Blanca es el **primer plano** y Trump y Jamenei
son el **medio**, detrás. El edificio les tapa de cintura para abajo.

Eso resuelve dos cosas de golpe:

- **No hacen falta cuerpos enteros.** El recorte puede ser de medio cuerpo
  porque la estructura tapa el resto. Adiós al hombre decapitado.
- **El borde inferior del recorte, que es siempre el peor, queda oculto.**
  Ya no importa si la multitud acaba en una línea recta.

## 2. Contraste de color entre capas, no de profundidad

Mira las capturas 1 y 2:

- **Medio**: blanco y negro, semitono, trazo rojo desplazado.
- **Primer plano**: **a todo color**. El pagoda de Tiananmén en naranja, el
  mar en azul, la Casa Blanca en blanco y verde.

La jerarquía visual la da el color, no el desenfoque. Mi profundidad de
campo aquí no pinta nada: todo va nítido.

## 3. Casi todo el primer plano es CÓDIGO, no imagen

En su tabla, la columna "FOREGROUND PROMPT" dice `N/A — code-driven` en
4 de las 7 escenas:

| # | primer plano | qué es |
|---|---|---|
| 02 | página de opinión de *The Nation* | **construida en código** |
| 04 | titular "$39 TRILLION" | tipografía |
| 05 | etiqueta "Interest: $1 trillion" | tipografía |
| 07 | remate a máquina de escribir | tipografía |

Y en el medio pasa igual: la gráfica del IPC se dibuja sola **en código**,
el mapa isométrico de EE. UU. es un asset pero el gráfico encima no.

O sea: **de 7 escenas, 3 no llevan ninguna imagen generada.** Eso baja el
coste y el riesgo mucho más que cualquier optimización de proveedor.

## 4. Algunos assets son VÍDEO con alfa

- escena 03: clip de olas en bucle con canal alfa, y el petrolero encima
- escena 07: billete de 100 $ ardiendo, vídeo transparente, a cámara lenta

No son PNG. Son clips recortados que se mueven solos. Es lo que da vida sin
tener que animar nada.

## 5. Duraciones y cortes: yo me pasé de listo

- **47 segundos en 7 escenas = 6,7 s de media.** Mi techo de 4 s estaba mal
  para este estilo.
- Sus transiciones, columna a columna: `Hard cut`, `Hard cut`, `Slide-out`,
  `Closer move`, `Hard cut`, `Hard cut`, `Fade to black`.

**Cinco de siete son cortes secos.** Yo monté deslizamientos, desenfoques
de movimiento y destellos por capítulo. El estilo no los pide.

---

## La tabla, columna por columna

Es su storyboard y es lo que hay que reproducir:

```
#  | LOCUCIÓN | FONDO | ASSET MEDIO | ASSET FRENTE
   | PROMPT MEDIO | PROMPT FRENTE | TRANSICIÓN
```

Un ejemplo suyo entero:

```
06 | "And the world is quietly leaving the dollar behind."
   | (fondo bloqueado)
   | MEDIO:  recorte B/N de Xi y Putin dándose la mano
   |         + bocadillos de cómic
   | FRENTE: recorte de la puerta de Tiananmén
   |         (abarca toda la base del encuadre)
   | PROMPT MEDIO:  foto recortada en blanco y negro de dos líderes
   |                dándose la mano, fondo transparente, contorno de
   |                rotulador rojo desplazado
   | PROMPT FRENTE: ilustración plana de la puerta de Tiananmén,
   |                fondo transparente, sombra cálida
   | TRANSICIÓN: corte seco
```

Fíjate en dos detalles del prompt del primer plano: **"ilustración plana"**
y **"abarca toda la base"**. El primer plano no es una foto, es un dibujo,
y siempre se apoya en el borde inferior.

---

## Lo que hay que cambiar en el pipeline

1. `PRESETS_ROL`: invertir. `medio` = sujetos, arriba, semitono + trazo.
   `frente` = estructura, anclada abajo, a color, tapando.
2. Un solo fondo por episodio, no 116.
3. Quitar la profundidad de campo. Todo nítido.
4. Duración por escena: 5-8 s, no 3-4.
5. Transición por defecto: corte seco.
6. Marcar en el guion qué escenas son **solo código** (tipografía y datos).
   En su vídeo son casi la mitad.
