import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {PruebaVox} from './Prueba';

const Raiz: React.FC = () =>
  React.createElement(Composition as any, {id: 'PruebaVox', component: PruebaVox as any, durationInFrames: 280, fps: 25, width: 1920, height: 1080, defaultProps: {}});

registerRoot(Raiz);
