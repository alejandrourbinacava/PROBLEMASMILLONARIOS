import React, {useContext} from 'react';
import {useCurrentFrame} from 'remotion';
import {Entra} from './anim';
import {OBJ} from './Objetos';
import {Personaje, Cara, Pose} from './Personaje';
import {Stick} from './Stick';
import {Ctx, F, L, R, T, ci, el, rr} from './prim';
import {atras, clamp01, suave} from './util';

/** Lo que recibe toda escena grande. */
export type EP = {
  foco?: string;
  burbuja?: string;
  cara: Cara;
  pose: Pose;
  v: number;
  tema: string;
  s: number;
  n: number;
};

export const PAREDES = ['#F6E2B8', '#DCEBDD', '#F3D4CF', '#D6E6F4', '#E6DDF2'];
export const SUELOS = ['#E2C99A', '#BFD9C2', '#E3B7AF', '#B5CDE6', '#CBBFE0'];

export const OWNER: Record<string, string> = {
  bar: 'duena',
  burger: 'burger',
  peluqueria: 'peluquera',
  estanco: 'estanquero',
  taxi: 'taxista',
  mercadona: 'camarero',
};
export const RUOTULO: Record<string, string> = {
  bar: 'BAR',
  burger: 'BURGER',
  peluqueria: 'PELUQUERÍA',
  estanco: 'ESTANCO',
  taxi: 'PARADA',
  mercadona: 'SUPER',
};

/** Un personaje que entra con rebote, pisando en (x, pies). */
export const Actor: React.FC<{
  x: number;
  pies: number;
  k?: number;
  look: string;
  pose?: Pose;
  cara?: Cara;
  voltea?: boolean;
  t0?: number;
  s?: number;
  mano?: React.ReactNode;
  piernas?: boolean;
}> = ({x, pies, k = 1, look, pose = 'quieto', cara = 'feliz', voltea, t0 = 4, s = 0, mano, piernas = true}) => {
  const stick = useContext(Ctx).stick;
  const C = stick ? Stick : Personaje;
  return (
    <Entra t0={t0} x={x} y={pies} k={1} rot={0} fase={s}>
      <C x={0} y={-152 * k} k={k} look={look} pose={pose} cara={cara} voltea={voltea} semilla={s} mano={mano} piernas={piernas} />
    </Entra>
  );
};

/** Un objeto de la libreria, con su sombra, entrando con rebote. */
export const Pieza: React.FC<{o?: string; x: number; y: number; k?: number; t0?: number; rot?: number; s?: number; sombra?: boolean}> = ({o, x, y, k = 1, t0 = 8, rot = -6, s = 0, sombra = true}) => {
  if (!o) return null;
  const C = OBJ[o] ?? OBJ.estrella;
  return (
    <g>
      {sombra && <ellipse cx={x} cy={y + 170 * k} rx={150 * k} ry={22 * k} fill="#1E1E24" opacity={0.12} />}
      <Entra t0={t0} x={x} y={y} k={k} rot={rot} fase={s}>
        <C />
      </Entra>
    </g>
  );
};

/** Burbuja de pensamiento con un objeto dentro. */
export const Burbuja: React.FC<{o?: string; x: number; y: number; k?: number; t0?: number; s?: number; cola?: 'izq' | 'der'}> = ({o, x, y, k = 1, t0 = 14, s = 0, cola = 'izq'}) => {
  if (!o) return null;
  const C = OBJ[o] ?? OBJ.estrella;
  const d = cola === 'izq' ? -1 : 1;
  return (
    <Entra t0={t0} x={x} y={y} k={k} rot={3} fase={s}>
      <g>
        <F d={ci(d * 130, 210, 18)} c="blanco" w={5} />
        <F d={ci(d * 90, 150, 28)} c="blanco" w={5} />
        <F d={ci(0, 0, 150)} c="blanco" />
        <g transform="scale(0.62)">
          <C />
        </g>
      </g>
    </Entra>
  );
};

/** Ventana con cielo y cruceta. */
export const Ventana: React.FC<{x: number; y: number; w: number; h: number; noche?: boolean}> = ({x, y, w, h, noche}) => {
  const tt = useContext(Ctx);
  const fondoNoche = tt.stick ? tt.fondo : '#2E3A63';
  return (
  <g>
    <F d={rr(x, y, w, h, 14)} c={noche ? '#2E3A63' : 'cielo'} />
    {noche ? (
      <g>
        <path d={ci(x + w * 0.72, y + h * 0.3, 34)} fill="#FFF3B0" />
        <path d={ci(x + w * 0.72 + 14, y + h * 0.3 - 8, 30)} fill={fondoNoche} />
        {[[0.2, 0.25], [0.4, 0.6], [0.55, 0.2], [0.3, 0.75]].map(([a, b], i) => (
          <path key={i} d={ci(x + w * a, y + h * b, 4)} fill="#FFF3B0" />
        ))}
      </g>
    ) : (
      <g>
        <path d={el(x + w * 0.3, y + h * 0.3, 54, 20)} fill="#FFFFFF" opacity={0.9} />
        <path d={el(x + w * 0.38, y + h * 0.26, 36, 16)} fill="#FFFFFF" opacity={0.9} />
      </g>
    )}
    <L d={`M${x + w / 2},${y} V${y + h} M${x},${y + h / 2} H${x + w}`} w={7} />
    <F d={rr(x - 18, y + h - 2, w + 36, 26, 8)} c="madera" />
  </g>
  );
};

export const Letrero: React.FC<{x: number; y: number; w: number; h?: number; texto: string; c?: string; px?: number; t0?: number}> = ({x, y, w, h = 90, texto, c = 'verde', px = 62, t0 = 2}) => (
  <Entra t0={t0} x={x} y={y} k={1} rot={-2}>
    <F d={rr(-w / 2, -h / 2, w, h, 16)} c={c} />
    <T x={0} y={px * 0.34} px={px} anchor="middle" c="blanco" fam="D Baloo" borde={false}>{texto}</T>
  </Entra>
);

/** Reparto de suelo: baldosas con lineas. */
export const Suelo: React.FC<{y: number; c: string; v?: number}> = ({y, c}) => (
  <g>
    <R d={rr(0, y, 1920, 1080 - y, 0)} c={c} />
    <L d={`M0,${y} H1920`} w={6} />
    {Array.from({length: 14}).map((_, i) => (
      <L key={i} d={`M${i * 160},${y} L${i * 160 - 200 + (i - 7) * 40},1080`} w={3} op={0.18} />
    ))}
    <L d={`M0,${y + 90} H1920 M0,${y + 200} H1920`} w={3} op={0.15} />
  </g>
);

export const Cielo: React.FC<{noche?: boolean}> = ({noche}) => <R d={rr(0, 0, 1920, 1080, 0)} c={noche ? '#46557F' : '#CDE8F7'} />;

/** Un edificio de fondo con ventanas. */
export const Bloque: React.FC<{x: number; y: number; w: number; h: number; c: string; filas?: number; cols?: number}> = ({x, y, w, h, c, filas = 4, cols = 3}) => (
  <g>
    <F d={rr(x, y, w, h, 8)} c={c} w={5} />
    {Array.from({length: filas}).map((_, r) =>
      Array.from({length: cols}).map((_, q) => (
        <F key={`${r}${q}`} d={rr(x + 18 + q * ((w - 36) / cols), y + 22 + r * ((h - 60) / filas), (w - 36) / cols - 16, (h - 60) / filas - 18, 6)} c={(r + q) % 3 === 0 ? 'amarillo' : 'cielo'} w={4} />
      )),
    )}
  </g>
);

/** Cajas apiladas. */
export const Caja3: React.FC<{x: number; y: number; k?: number; c?: string}> = ({x, y, k = 1, c = 'madera'}) => (
  <g transform={`translate(${x},${y}) scale(${k})`}>
    <F d={rr(-70, -100, 140, 100, 8)} c={c} w={5} />
    <L d="M-70,-62 H70 M-14,-100 V-62" w={4} />
    <R d={rr(-14, -100, 28, 38, 0)} c="amarillo" op={0.7} />
  </g>
);

export const Persiana: React.FC<{x: number; y: number; w: number; h: number; u: number}> = ({x, y, w, h, u}) => (
  <g>
    <F d={rr(x, y, w, Math.max(10, h * u), 8)} c="gris" />
    {Array.from({length: 14}).map((_, i) => (y + 20 + i * 24 < y + h * u ? <L key={i} d={`M${x + 8},${y + 20 + i * 24} H${x + w - 8}`} w={3} op={0.5} /> : null))}
  </g>
);

export const useF = () => useCurrentFrame();
export {atras, clamp01, suave};
