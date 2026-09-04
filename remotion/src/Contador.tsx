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
import {Fuentes} from './fuentes';

/**
 * G2: el contador de nueve digitos.
 *
 * "Eso no es lo que apostaron los clientes. Eso es lo que perdieron."
 *
 * El efecto es VER LLENARSE los nueve digitos, no que aparezca la cifra. Por
 * eso el contador sube digito a digito y no de golpe: 1.236.196.257 es una
 * cantidad que no significa nada leida, y significa mucho vista crecer.
 *
 * Dos detalles que hacen que no baile:
 *
 *   Los digitos van en `tabular-nums`. Sin eso, cada cifra tiene su propio
 *   ancho y el numero entero se mueve a cada fotograma.
 *
 *   El contador arranca ya con los nueve digitos puestos, rellenando con
 *   ceros. Si creciera de 1 a 1.236 millones, el numero cambiaria de longitud
 *   nueve veces y saltaria de sitio.
 */

const CURVA = Easing.bezier(0.33, 0, 0.15, 1);
const CIFRA = 1236196257;

const conPuntos = (n: number) =>
  Math.round(n).toString().padStart(10, '0').replace(/\B(?=(\d{3})+(?!\d))/g, '.');

export const Contador: React.FC<{
  duracion: number;
  frameFinal?: number;
  palabra?: string;
}> = ({duracion, frameFinal = 40, palabra = 'PERDIERON'}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();

  const valor = interpolate(frame, [0, frameFinal], [0, CIFRA], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // El golpe: al llenarse, la cifra da un tiron de escala y se recoge.
  const golpe = interpolate(
    frame,
    [frameFinal - 2, frameFinal + 3, frameFinal + 12],
    [1, 1.055, 1],
    {easing: CURVA, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  // La palabra entra despues, en seis frames, desde abajo.
  const tPalabra = interpolate(frame, [frameFinal + 6, frameFinal + 12], [0, 1], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Un respiro de luz al completarse, que muere enseguida.
  const destello = interpolate(
    frame,
    [frameFinal - 1, frameFinal + 2, frameFinal + 16],
    [0, 0.3, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill style={{backgroundColor: '#040407', overflow: 'hidden'}}>
      <Fuentes />
      <Img
        src={staticFile('biblioteca/fondo_negro_textura.png')}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${interpolate(frame, [0, duracion], [1.06, 1.0], {
            easing: CURVA,
            extrapolateRight: 'clamp',
          })})`,
        }}
      />

      <AbsoluteFill style={{mixBlendMode: 'screen', pointerEvents: 'none'}}>
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '48%',
            width: '70%',
            height: '50%',
            borderRadius: '50%',
            backgroundColor: '#C98B34',
            opacity: destello,
            filter: 'blur(180px)',
            transform: 'translate(-50%, -50%)',
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{textAlign: 'center', transform: `scale(${golpe})`}}>
          <div
            style={{
              fontFamily: "'Archivo Black', Poppins, sans-serif",
              fontSize: Math.round(width * 0.085),
              lineHeight: 1,
              color: '#F2E9D8',
              letterSpacing: '-0.015em',
              // Sin ancho fijo por digito, el numero baila a cada fotograma.
              fontVariantNumeric: 'tabular-nums',
              textShadow: '0 14px 46px rgba(0,0,0,0.8)',
              whiteSpace: 'nowrap',
            }}
          >
            ${conPuntos(valor)}
          </div>

          <div
            style={{
              marginTop: Math.round(width * 0.016),
              fontFamily: "'Archivo Black', Poppins, sans-serif",
              fontSize: Math.round(width * 0.038),
              letterSpacing: '0.1em',
              color: '#C9A227',
              opacity: tPalabra,
              transform: `translateY(${(1 - tPalabra) * 26}px)`,
              whiteSpace: 'nowrap',
            }}
          >
            {palabra}
          </div>
        </div>
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.6) 100%)',
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};
