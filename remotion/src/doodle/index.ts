import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {EscenaDoodle} from './Escena';
import {Hoja} from './Hoja';

const VACIO = {
  id: 'demo',
  frames: 75,
  objetos: [{o: 'taza', e: 'el café'}],
  layout: 'heroe',
  semilla: 1,
  papel: 'crema',
};

const Raiz: React.FC = () =>
  React.createElement(
    React.Fragment,
    null,
    React.createElement(Composition as any, {id: 'Hoja', component: Hoja as any, durationInFrames: 1, fps: 25, width: 1920, height: 1080, defaultProps: {}}),
    React.createElement(Composition as any, {
      id: 'Plano',
      component: EscenaDoodle as any,
      durationInFrames: 75,
      fps: 25,
      width: 1920,
      height: 1080,
      defaultProps: {plano: VACIO, fps: 25},
      calculateMetadata: ({props}: any) => ({durationInFrames: Math.max(1, props.plano.frames), fps: props.fps ?? 25}),
    }),
  );

registerRoot(Raiz);
