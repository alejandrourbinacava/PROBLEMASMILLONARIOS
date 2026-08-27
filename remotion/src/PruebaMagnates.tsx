import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {MagnatesScene, MagnatesSceneProps} from './MagnatesScene';

export type PasoMagnates = Omit<MagnatesSceneProps, 'duracion'> & {
  /** Hasta que segundo dura, sacado de las marcas del SRT de la narracion. */
  hasta: number;
};

export type PruebaMagnatesProps = {
  pasos: PasoMagnates[];
  audio?: string;
};

/**
 * Encadena escenas de tres capas. Los cortes salen de las marcas del SRT, no
 * de un cronometro: asi el rotulo aparece cuando se pronuncia.
 *
 * No hay transicion entre escenas a proposito. Cada una arranca su propio
 * movimiento de camara desde cero, y el corte seco entre dos camaras en marcha
 * ya lee como un cambio de plano. Meter ademas un deslizamiento encima seria
 * dos efectos peleandose por lo mismo.
 */
export const PruebaMagnates: React.FC<PruebaMagnatesProps> = ({pasos, audio}) => {
  const {fps} = useVideoConfig();

  let anterior = 0;
  const tramos = pasos.map((paso) => {
    const desde = anterior;
    const hasta = Math.round(paso.hasta * fps);
    anterior = hasta;
    return {paso, desde, duracion: Math.max(1, hasta - desde)};
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {audio ? <Audio src={staticFile(audio)} /> : null}
      {tramos.map(({paso, desde, duracion}, indice) => (
        <Sequence key={indice} from={desde} durationInFrames={duracion} layout="none">
          <MagnatesScene {...paso} duracion={duracion} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
