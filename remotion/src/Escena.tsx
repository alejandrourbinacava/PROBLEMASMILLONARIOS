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

export type Zoom = 'in' | 'out';

export type EscenaProps = {
  fondo: string;
  /** El sujeto principal. Uno, no varios. */
  sujeto?: string;
  /** Como mucho un elemento mas. Si hace falta un tercero, sobra. */
  elemento?: string;
  texto?: string;
  zoom: Zoom;
  /** Donde se planta el sujeto, en fraccion de ancho. */
  ladoSujeto?: number;
  /** Altura del sujeto sobre el alto del encuadre. */
  altoSujeto?: number;
  duracion: number;
};

/**
 * Una escena del montaje: fondo, un sujeto y un rotulo.
 *
 * Lo que mas cuesta aqui es no meter mas cosas. Viendo el tutorial fotograma a
 * fotograma, sus escenas casi nunca pasan de tres capas: el fondo, UNA persona
 * u objeto, y el texto. La sensacion de riqueza no viene de la cantidad de
 * elementos, viene de que los pocos que hay se mueven a velocidades distintas.
 *
 * El sujeto lleva algo mas de zoom que el fondo. Esa diferencia es todo el
 * efecto: con el mismo zoom en las dos capas, la escena se lee como una foto
 * ampliandose.
 */
export const Escena: React.FC<EscenaProps> = ({
  fondo,
  sujeto,
  elemento,
  texto,
  zoom,
  ladoSujeto = 0.5,
  altoSujeto = 0.72,
  duracion,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const avance = interpolate(frame, [0, Math.max(1, duracion - 1)], [0, 1], {
    easing: Easing.bezier(0.32, 0, 0.2, 1),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Zoom in: entra. Zoom out: se aleja. El fondo recorre menos que el sujeto.
  const [fondoA, fondoB] = zoom === 'in' ? [1.06, 1.2] : [1.2, 1.06];
  const [sujA, sujB] = zoom === 'in' ? [1.0, 1.16] : [1.16, 1.0];
  const escalaFondo = fondoA + (fondoB - fondoA) * avance;
  const escalaSujeto = sujA + (sujB - sujA) * avance;

  // El texto entra en los primeros seis fotogramas y se queda quieto: si
  // tambien se moviera competiria con el zoom y marearia.
  const entradaTexto = interpolate(frame, [0, 6], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const altoPx = height * altoSujeto;

  return (
    <AbsoluteFill style={{backgroundColor: '#0a0a0c', overflow: 'hidden'}}>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <Img
          src={staticFile(fondo)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${escalaFondo})`,
          }}
        />
      </AbsoluteFill>

      {/* Un velo oscuro entre el fondo y el sujeto: separa los dos planos y
          deja sitio para que el rotulo se lea sin contorno ni caja. */}
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(to bottom, rgba(8,8,14,0.55), rgba(8,8,14,0.18) 45%, rgba(8,8,14,0.72))',
        }}
      />

      {elemento ? (
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
          <Img
            src={staticFile(elemento)}
            style={{
              height: `${altoSujeto * 55}%`,
              objectFit: 'contain',
              transform: `scale(${1 + (escalaSujeto - 1) * 0.6})`,
              opacity: 0.92,
            }}
          />
        </AbsoluteFill>
      ) : null}

      {texto ? (
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
          <div
            style={{
              maxWidth: '82%',
              textAlign: 'center',
              fontFamily: 'Poppins, sans-serif',
              fontWeight: 900,
              fontSize: Math.round(width * 0.058),
              lineHeight: 1.04,
              letterSpacing: '-0.015em',
              color: '#fff',
              textShadow: '0 10px 40px rgba(0,0,0,0.72), 0 2px 10px rgba(0,0,0,0.6)',
              opacity: entradaTexto,
              transform: `translateY(${(1 - entradaTexto) * 22}px)`,
            }}
          >
            {texto}
          </div>
        </AbsoluteFill>
      ) : null}

      {/* El sujeto va DELANTE del texto: es lo que da la sensacion de estar
          dentro de un espacio y no delante de un cartel. */}
      {sujeto ? (
        <AbsoluteFill>
          <Img
            src={staticFile(sujeto)}
            style={{
              position: 'absolute',
              bottom: 0,
              left: `${ladoSujeto * 100}%`,
              height: altoPx,
              width: 'auto',
              objectFit: 'contain',
              transform: `translateX(-50%) scale(${escalaSujeto})`,
              transformOrigin: 'bottom center',
              filter: 'drop-shadow(0 24px 46px rgba(0,0,0,0.62))',
            }}
          />
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
