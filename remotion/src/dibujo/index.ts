import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {Dibujo} from './Dibujo';

const Raiz: React.FC = () =>
  React.createElement(Composition as any, {
    id: 'Dibujo',
    component: Dibujo as any,
    durationInFrames: 100,
    fps: 25,
    width: 1920,
    height: 1080,
    defaultProps: {estilo: 'doodle', escena: 'bar'},
  });

registerRoot(Raiz);
