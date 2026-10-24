import React from 'react';
import {AbsoluteFill} from 'remotion';
import {OBJ} from './Objetos';
import {Ctx, Defs, Fondo, paleta, T, useFuentes} from './prim';

/** Hoja de contacto de la libreria de objetos: para MIRARLOS. */
export const Hoja: React.FC<{papel?: string; desde?: number; hasta?: number}> = ({papel = 'crema', desde = 0, hasta = 99}) => {
  const ok = useFuentes();
  const t = paleta(papel);
  const nombres = Object.keys(OBJ).slice(desde, hasta);
  const cols = 6;
  const filas = Math.ceil(nombres.length / cols);
  const cw = 1920 / cols;
  const ch = 1080 / Math.max(filas, 1);
  if (!ok) return <AbsoluteFill style={{background: t.fondo}} />;
  return (
    <AbsoluteFill>
      <Ctx.Provider value={t}>
        <svg width={1920} height={1080} viewBox="0 0 1920 1080">
          <Defs />
          <Fondo w={1920} h={1080} />
          <g filter="url(#torcido)">
            {nombres.map((n, i) => {
              const C = OBJ[n];
              const x = (i % cols) * cw + cw / 2;
              const y = Math.floor(i / cols) * ch + ch / 2 - 18;
              const k = Math.min(cw, ch) / 420;
              return (
                <g key={n}>
                  <g transform={`translate(${x},${y}) scale(${k})`}>
                    <C />
                  </g>
                  <T x={x} y={y + ch / 2 - 8} px={26} anchor="middle">{n}</T>
                </g>
              );
            })}
          </g>
        </svg>
      </Ctx.Provider>
    </AbsoluteFill>
  );
};
