import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  Series,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {PhotoDrop} from './PhotoDrop';

export type DemoProps = {
  imagenEscena: string;
  imagenMadera: string;
  duracionTransicion: number;
  duracionEscena: number;
};

/**
 * La transición completa de ida y vuelta:
 *
 *     lift   la foto está en la mesa y sube hasta llenar el encuadre
 *     escena empuje lento, ya dentro
 *     drop   la imagen se convierte otra vez en fotografía y cae a la mesa
 *
 * Sirve para ver si el empalme entre los tres tramos es limpio, que es lo
 * único que no se puede juzgar viendo las transiciones por separado.
 */
export const Demo: React.FC<DemoProps> = ({
  imagenEscena,
  imagenMadera,
  duracionTransicion,
  duracionEscena,
}) => {
  return (
    <Series>
      <Series.Sequence durationInFrames={duracionTransicion}>
        <PhotoDrop
          imagenEscena={imagenEscena}
          imagenMadera={imagenMadera}
          duracion={duracionTransicion}
          direccion="lift"
        />
      </Series.Sequence>

      <Series.Sequence durationInFrames={duracionEscena}>
        <Empuje imagenEscena={imagenEscena} duracion={duracionEscena} />
      </Series.Sequence>

      <Series.Sequence durationInFrames={duracionTransicion}>
        <PhotoDrop
          imagenEscena={imagenEscena}
          imagenMadera={imagenMadera}
          duracion={duracionTransicion}
          direccion="drop"
        />
      </Series.Sequence>
    </Series>
  );
};

/**
 * El tramo de en medio. Arranca exactamente en 1,9, que es donde deja la foto
 * el `lift` y donde la recoge el `drop`: si empezara en 1,0 se vería un salto
 * de escala en cada empalme.
 */
const Empuje: React.FC<{imagenEscena: string; duracion: number}> = ({
  imagenEscena,
  duracion,
}) => {
  const frame = useCurrentFrame();

  const escala = interpolate(frame, [0, Math.max(1, duracion - 1)], [1.9, 2.02], {
    easing: Easing.bezier(0.4, 0, 0.6, 1),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <Img
          src={staticFile(imagenEscena)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${escala})`,
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
