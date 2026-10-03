import React from 'react';
import {Composition} from 'remotion';
import {Plato} from './base';
import {EscenaPlato} from './Escena';

/**
 * La composicion de un plano de plato. `render-platos.mjs` la pide una vez por
 * plano con sus datos (`plato`) y los fotogramas exactos que tiene que durar.
 */
type Props = {plato: Plato; W: number; H: number; fps: number};

const VACIO: Plato = {
  archivo: 'demo.mp4',
  frames: 75,
  id: 'demo',
  duracion: 3,
  fondo_titulo: '',
  acento: [206, 32, 38],
  fase: 0,
  grafico: {
    tipo: 'contador',
    valor: 1729,
    sufijo: ' M€',
    pie: 'de beneficio en 2025',
    px: 170,
    y: 0.5,
    retardo: 0.4,
    duracion: 1.6,
    entrada: 'barrido',
    _ac: [206, 32, 38],
  },
  texto_pantalla: null,
  lat_ent: null,
  lat_sal: null,
};

export const RootP2: React.FC = () => (
  <Composition
    id="Plato"
    component={EscenaPlato as unknown as React.FC<Props>}
    durationInFrames={75}
    fps={25}
    width={1920}
    height={1080}
    defaultProps={{plato: VACIO, W: 1920, H: 1080, fps: 25}}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.max(1, (props as Props).plato.frames),
      fps: (props as Props).fps,
      width: (props as Props).W,
      height: (props as Props).H,
    })}
  />
);
