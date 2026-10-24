import React from 'react';
import {useCurrentFrame} from 'remotion';
import {L, T} from './prim';
import {atras, clamp01, suave} from './util';

// ------------------------------------------------------------------ animacion
/** Entrada de un objeto: crece con rebasamiento, girando un poco, y luego respira. */
export const Entra: React.FC<{t0: number; x: number; y: number; k: number; rot?: number; fase?: number; children: React.ReactNode}> = ({t0, x, y, k, rot = 0, fase = 0, children}) => {
  const f = useCurrentFrame();
  const u = clamp01((f - t0) / 14);
  const s = k * (0.25 + 0.75 * atras(u, 2.1));
  const giro = rot * (1 - suave(u)) + Math.sin((f + fase) / 17) * 1.4;
  const dy = Math.sin((f + fase) / 13) * 7 * suave(u);
  return (
    <g transform={`translate(${x},${y + dy}) rotate(${giro}) scale(${Math.max(0.01, s)})`} opacity={clamp01(u * 4)}>
      {children}
    </g>
  );
};

export const Etiqueta: React.FC<{t0: number; x: number; y: number; texto: string; px?: number}> = ({t0, x, y, texto, px = 58}) => {
  const f = useCurrentFrame();
  const u = suave((f - t0) / 10);
  const w = Math.min(1500, texto.length * px * 0.5 + 60);
  return (
    <g opacity={u} transform={`translate(0,${(1 - u) * 24})`}>
      <T x={x} y={y} px={px} anchor="middle">{texto}</T>
      <L d={`M${x - w / 2},${y + 18} Q${x},${y + 8} ${x + w / 2},${y + 20}`} c="rojo" w={7} />
    </g>
  );
};

