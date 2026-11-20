import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {PruebaModerna} from './Moderno';
import {PruebaVox} from './Prueba';

const Raiz: React.FC = () =>
  React.createElement(
    React.Fragment,
    null,
    React.createElement(Composition as any, {id: 'PruebaVox', component: PruebaVox as any, durationInFrames: 280, fps: 25, width: 1920, height: 1080, defaultProps: {}}),
    React.createElement(Composition as any, {id: 'PruebaModerna', component: PruebaModerna as any, durationInFrames: 310, fps: 25, width: 1920, height: 1080, defaultProps: {}}),
  );

registerRoot(Raiz);
