import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

/**
 * Tres capas, una camara.
 *
 * Cielo detras de todo, la fachada del casino en medio, la gente delante y
 * abajo, en la entrada. Cada capa recorre lo suyo segun lo lejos que este: la
 * gente es la que mas se mueve y el cielo el que menos, y esa diferencia es lo
 * que se lee como profundidad.
 *
 * El cielo ademas tiene movimiento propio: las nubes van desplazandose
 * despacio hacia un lado al margen de la camara. Una capa de fondo quieta
 * delata que es una foto; unas nubes que se mueven la convierten en un cielo.
 */

const CURVA = Easing.bezier(0.33, 0, 0.15, 1);

// Cuanto recorre cada capa del movimiento de camara. El cielo casi nada.
const PARALLAX = {cielo: 0.08, casino: 0.35, gente: 1.0};

export const Entrada: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames, width} = useVideoConfig();

  // El recorrido de camara: entra acercandose, se retira, y todo el rato
  // deriva hacia la derecha. Tres movimientos encadenados, no un zoom.
  const zoom = interpolate(
    frame,
    [0, durationInFrames * 0.45, durationInFrames * 0.78, durationInFrames - 1],
    [1.0, 1.22, 1.16, 1.02],
    {easing: CURVA, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  const deriva = interpolate(frame, [0, durationInFrames - 1], [-90, 90], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Las nubes, por su cuenta. Lento y continuo: no acompaña a la camara.
  const nubes = interpolate(frame, [0, durationInFrames - 1], [0, -70], {
    extrapolateRight: 'clamp',
  });
  const nubesZoom = interpolate(frame, [0, durationInFrames - 1], [1.06, 1.14], {
    extrapolateRight: 'clamp',
  });

  const capa = (parallax: number) => ({
    // La camara agranda mas lo cercano que lo lejano.
    escala: 1 + (zoom - 1) * (0.3 + parallax * 0.7),
    x: deriva * parallax,
  });

  const cielo = capa(PARALLAX.cielo);
  const casino = capa(PARALLAX.casino);
  const gente = capa(PARALLAX.gente);

  return (
    <AbsoluteFill style={{backgroundColor: '#05060c', overflow: 'hidden'}}>
      {/* CIELO — detras de todo, con las nubes desplazandose solas */}
      <AbsoluteFill
        style={{
          transform: `translateX(${cielo.x + nubes}px) scale(${cielo.escala * nubesZoom})`,
        }}
      >
        <Img
          src={staticFile('entrada/cielo.png')}
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
      </AbsoluteFill>

      {/* Un velo de bruma entre el cielo y la fachada: separa los planos sin
          desenfocar nada, que es lo que hace que no parezcan pegados. */}
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(to bottom, rgba(20,28,48,0) 40%, rgba(24,30,52,0.55) 100%)',
          pointerEvents: 'none',
        }}
      />

      {/* CASINO — la fachada, apoyada en la parte baja del cuadro */}
      <AbsoluteFill
        style={{transform: `translateX(${casino.x}px) scale(${casino.escala})`}}
      >
        <Img
          src={staticFile('entrada/casino.png')}
          style={{
            position: 'absolute',
            left: '50%',
            bottom: '4%',
            height: '86%',
            width: 'auto',
            transform: 'translateX(-50%)',
            filter: 'brightness(0.94) saturate(1.05)',
          }}
        />
      </AbsoluteFill>

      {/* GENTE — la capa principal, delante y abajo, en la entrada */}
      <AbsoluteFill
        style={{transform: `translateX(${gente.x}px) scale(${gente.escala})`}}
      >
        <Img
          src={staticFile('entrada/gente.png')}
          style={{
            position: 'absolute',
            left: '50%',
            bottom: '-2%',
            width: `${width * 1.12}px`,
            height: 'auto',
            transform: 'translateX(-50%)',
            // Estan a contraluz contra la marquesina: se hunden un poco para
            // que la luz venga de detras y no de ellos.
            filter: 'brightness(0.72) contrast(1.12) saturate(0.9)',
          }}
        />
      </AbsoluteFill>

      {/* El resplandor de la marquesina, por delante de la gente */}
      <AbsoluteFill style={{mixBlendMode: 'screen', pointerEvents: 'none'}}>
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '46%',
            width: '58%',
            height: '46%',
            borderRadius: '50%',
            backgroundColor: '#C98B34',
            opacity: 0.22,
            filter: 'blur(140px)',
            transform: 'translate(-50%, -50%)',
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.5) 100%)',
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};
