# Lo que llevaba diez rondas sin ver

Medido sobre tus dieciséis capturas con los tiempos del guion. La escena
del gráfico, de 0:26 a 0:39 — **trece segundos sin un solo corte**:

| t | qué pasa | cuadrantes |
|---|---|---|
| 0:26 | la gráfica CPI sola, centrada y grande | SI 31 · SD 31 |
| 0:30 | la gráfica se dibuja sola, mismo sitio | SI 31 · SD 31 |
| 0:33 | **encoge y se va a la izquierda**; entra el mapa | SI 33 · SD 8 |
| 0:35 | aparece "$39 TRILLION" sobre el mapa | SI 34 · SD 14 |
| 0:36 | **la gráfica sale**; mapa y texto se recolocan al centro | SI 17 · SD 15 |
| 0:37 | entra el obrero por la izquierda | II 53 · ID 6 |
| 0:39 | entra el soldado por la derecha: queda simétrico | II 54 · ID 67 |

**Los elementos persisten, se mueven, encogen y salen dentro del mismo
plano.** Siete momentos visuales, cero cortes.

## Por qué esto lo cambia todo

Yo tenía un modelo equivocado: escena = disposición fija + animación de
entrada, y el dinamismo salía de **cortar** cada 4 segundos.

El suyo es: escena = **un escenario continuo** donde los elementos se
acumulan y se reorganizan cada 2 segundos. Por eso él dice que se lee como
una toma continua y el nuestro como un pase de diapositivas.

Y explica la contradicción que me traía loco: sus 7 escenas en 47 s son
6,7 s cada una, pero la imagen cambia cada 2 s. No son cosas distintas.

## Cómo queda el guion

| | antes | ahora |
|---|---|---|
| escenas | 199 de 3-5 s | **111 de 6-11 s** |
| momentos visuales | 199 | **479** |
| cambio visual cada | 3,9 s (cortando) | **1,6 s (sin cortar)** |
| cortes en el episodio | 198 | 110 |

Cada escena lleva ahora `estados`: una coreografía con el momento exacto
en que entra cada elemento, adónde se aparta el anterior para hacerle
sitio, y cuándo sale.

```
gancho_03 · 8 s · 6 estados
  t=0.00  entra: oficina      → x=0.20 w=0.24
  t=1.60  gesto: asienta      → se afianza en el sitio
  t=3.20  entra: plantilla    → la oficina ENCOGE a w=0.17 y se aparta a x=0.065
  t=4.80  entra: titular      → primera mitad de la frase
  t=6.40  entra: titular_2    → la frase completa
  t=6.88  sale: oficina       → la plantilla y el texto se recolocan
```

Tres tipos de estado, no solo "entra algo nuevo":

- **entrada** — aparece un elemento y el que estaba cede sitio
- **asienta** — el elemento se afianza sin moverse (la gráfica dibujándose)
- **salida** — un elemento se va y los que quedan se recolocan

Y el texto se escribe en dos tiempos, como su remate: primero
"EMPIRES DON'T", después la frase entera.
