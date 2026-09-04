import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {HojaCalculo} from './HojaCalculo';

/**
 * Entrada aparte, solo para las piezas de motion graphics.
 *
 * `index.ts` monta Root.tsx, que importa las quince composiciones del canal.
 * Siete de esos ficheros estan en el disco pero no en el repo, asi que en la
 * nube el bundle no resuelve y no compila nada -ni siquiera lo que no depende
 * de ellos-. Esta entrada carga solo lo que necesita.
 */
export const RaizMotion: React.FC = () => (
  <>
    <Composition
      id="HojaCalculo"
      component={HojaCalculo}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
    />
  </>
);

registerRoot(RaizMotion);
