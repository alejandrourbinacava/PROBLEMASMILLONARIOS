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

export type Direccion = 'drop' | 'lift';

export type PhotoDropProps = {
  imagenEscena: string;
  imagenMadera: string;
  duracion: number;
  direccion: Direccion;
};

/** Distancia del ojo al plano de la mesa. */
const PERSPECTIVA = 1200;
const BORDE = 40;

/** Los dos extremos de la animación. `drop` va de A a B; `lift`, de B a A. */
const PANTALLA = {escala: 1.9, rotX: 0, desplY: 0, rotZ: 0, sombra: 0, opacidad: 0};
const MESA = {escala: 0.42, rotX: 52, desplY: 60, rotZ: -3, sombra: 40, opacidad: 0.55};

const CURVA = Easing.bezier(0.33, 0, 0.15, 1);

export const PhotoDrop: React.FC<PhotoDropProps> = ({
  imagenEscena,
  imagenMadera,
  duracion,
  direccion,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  // `lift` es la misma curva recorrida al revés: la foto está en la mesa y
  // sube hasta llenar el encuadre. Se invierte el avance, no la curva, para
  // que la aceleración sea la misma en los dos sentidos.
  const bruto = interpolate(frame, [0, Math.max(1, duracion - 1)], [0, 1], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const avance = direccion === 'drop' ? bruto : 1 - bruto;

  const entre = (a: number, b: number) => a + (b - a) * avance;

  const escala = entre(PANTALLA.escala, MESA.escala);
  const rotX = entre(PANTALLA.rotX, MESA.rotX);
  const desplY = entre(PANTALLA.desplY, MESA.desplY);
  const rotZ = entre(PANTALLA.rotZ, MESA.rotZ);
  const desenfoque = entre(PANTALLA.sombra, MESA.sombra);
  const opacidad = entre(PANTALLA.opacidad, MESA.opacidad);

  return (
    <AbsoluteFill style={{backgroundColor: '#1a120b'}}>
      <Img
        src={staticFile(imagenMadera)}
        style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />

      <AbsoluteFill
        style={{
          perspective: `${PERSPECTIVA}px`,
          transformStyle: 'preserve-3d',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            // El div mide justo el encuadre y el borde va POR FUERA
            // (content-box), así que al empezar en escala 1,9 el marco blanco
            // queda fuera de cuadro y solo se ve la fotografía.
            width,
            height,
            boxSizing: 'content-box',
            border: `${BORDE}px solid #fdfdfb`,
            // Sombra proyectada con box-shadow, no con filter: un filtro sobre
            // la imagen la rasteriza al tamaño de pantalla y al escalarla a
            // 1,9 se ve blanda. box-shadow afecta a la caja, no al contenido.
            boxShadow: `0 ${desenfoque * 0.45}px ${desenfoque}px rgba(0,0,0,${opacidad})`,
            // El orden se aplica de derecha a izquierda: primero escala, luego
            // gira y por último se desplaza. Al revés, el desplazamiento se
            // escalaría también y la foto se saldría de la mesa.
            transform: `translateY(${desplY}px) rotateX(${rotX}deg) rotateZ(${rotZ}deg) scale(${escala})`,
            transformStyle: 'preserve-3d',
            backfaceVisibility: 'hidden',
          }}
        >
          <Img
            src={staticFile(imagenEscena)}
            style={{width: '100%', height: '100%', objectFit: 'cover', display: 'block'}}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
