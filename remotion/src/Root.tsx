import React from 'react';
import {Composition, staticFile} from 'remotion';
import {ParallaxScene, Manifest} from './ParallaxScene';

// El manifest vive en public/ junto a las capas, asi que se carga en el
// arranque y el Studio lo recoge sin recompilar.
import manifest from '../public/scene/manifest.json';

const FPS = 25;
const DURACION_S = 6;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="ParallaxScene"
      component={ParallaxScene}
      durationInFrames={FPS * DURACION_S}
      fps={FPS}
      width={1920}
      height={1080}
      defaultProps={{
        manifest: manifest as Manifest,
        assetDir: 'scene',
        title: undefined,
        // El movimiento lateral es lo que hace VISIBLE la separacion en capas.
        // Un dolly puro no vale: con las z de una escena normal, la capa mas
        // cercana crece un 13,6% y la mas lejana un 7,1%, o sea 6,5 puntos de
        // diferencia, que el ojo no distingue de un zoom sobre una foto plana.
        // Desplazando 260 px, la capa de delante recorre 260 y la del fondo
        // 144: 116 px de diferencia, y ahi si se lee la profundidad.
        startZ: 0,
        endZ: 90,
        panX: 260,
        panY: 0.02,
      }}
    />
  );
};
