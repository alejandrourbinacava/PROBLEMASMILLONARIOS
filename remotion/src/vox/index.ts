import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {PruebaModerna} from './Moderno';
import {PruebaVox} from './Prueba';
import {Video} from './video/Video';

const Raiz: React.FC = () =>
  React.createElement(
    React.Fragment,
    null,
    React.createElement(Composition as any, {id: 'PruebaVox', component: PruebaVox as any, durationInFrames: 280, fps: 25, width: 1920, height: 1080, defaultProps: {}}),
    React.createElement(Composition as any, {
      id: 'Video',
      component: Video as any,
      durationInFrames: 100,
      fps: 25,
      width: 1920,
      height: 1080,
      defaultProps: {spec: {fps: 25, total: 100, marca: {nombre: 'MARCA', color: '#12B25E', claro: '#1FD877', oscuro: '#053D22', acento: '#FF7A1A'}, escenas: []}},
      calculateMetadata: ({props}: any) => ({durationInFrames: Math.max(1, props.spec.total), fps: props.spec.fps}),
    }),
    React.createElement(Composition as any, {id: 'PruebaModerna', component: PruebaModerna as any, durationInFrames: 310, fps: 25, width: 1920, height: 1080, defaultProps: {}}),
  );

registerRoot(Raiz);
