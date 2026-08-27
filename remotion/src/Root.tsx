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
        // Dolly-in muy lento: 6 segundos para recorrer 120 unidades. La deriva
        // vertical es del 2,5% del alto, lo justo para que no parezca una foto.
        startZ: 0,
        endZ: 120,
        panX: 0,
        panY: 0.025,
      }}
    />
  );
};
