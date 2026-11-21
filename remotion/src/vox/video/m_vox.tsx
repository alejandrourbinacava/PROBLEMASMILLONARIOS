import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {EP} from './base';
import {Chip, Cifra, Eti, Sans, Serif, T, c01, io, lerp, miles, pop, rebote, rnd, sal, tr} from './kit';
import {FondoReal} from './m_capas';

/**
 * Planos POR CAPAS de calidad (estilo Vox / documental). Cada plano es una pila:
 *
 *   metraje real desenfocado  ->  elementos GRANDES de fondo (algo oscuros y borrosos)
 *   ->  texto  ->  elemento protagonista nitido  ->  algo muy cerca de camara, desenfocado
 *
 * Los elementos son fotos de estudio recortadas (`g_*.webp`, `vox/cortar_blanco.py`),
 * nunca pictogramas, y ocupan el cuadro: pocos, grandes y a distinta profundidad.
 * La camara empuja despacio y cada capa se mueve segun su `z` (paralaje).
 */
export type Cam = {x: number; s: number};
/** Empuje lento de camara durante el tramo [t0, t1]. */
export const deriva = (t: number, t0: number, t1: number, dx = 46, ds = 0.07): Cam => {
  const u = c01((t - t0) / Math.max(1, t1 - t0));
  return {x: (u - 0.5) * dx, s: u * ds};
};

type ImP = {
  src: string;
  x: number; // centro
  y: number; // base
  w: number;
  t: number; // fotogramas desde que entra (negativo = aun no)
  de?: 'aba' | 'izq' | 'der' | 'arr' | 'pop' | 'nada';
  z?: number; // profundidad: 0 fondo, 1 sujeto, >1 primer plano
  blur?: number;
  luz?: number;
  gris?: number;
  rot?: number;
  flip?: boolean;
  cam?: Cam;
  op?: number;
  recorte?: string; // clip-path
};
/** Un elemento recortado, con su profundidad. */
export const Im: React.FC<ImP> = ({src, x, y, w, t, de = 'aba', z = 1, blur = 0, luz = 1, gris = 0, rot = 0, flip, cam, op = 1, recorte}) => {
  if (t < 0 || op <= 0) return null;
  const u = de === 'nada' ? 1 : rebote(t / 16, 0.6);
  const d = (1 - u) * 320;
  const dx = (de === 'izq' ? -d : de === 'der' ? d : 0) - (cam?.x ?? 0) * z;
  const dy = de === 'aba' ? d : de === 'arr' ? -d : 0;
  const s = (de === 'pop' ? 0.3 + 0.7 * rebote(t / 12, 1.5) : 1) * (1 + (cam?.s ?? 0) * z);
  return (
    <div style={{position: 'absolute', left: x + dx, top: y + dy, width: 0, height: 0, opacity: c01(t / 3) * op}}>
      <Img
        src={staticFile('vox/media/' + src + '.webp')}
        style={{position: 'absolute', width: w, maxWidth: 'none', left: -w / 2, transform: `translateY(-100%) rotate(${rot}deg) scale(${flip ? -s : s}, ${s})`, transformOrigin: '50% 100%', clipPath: recorte, filter: `${blur ? `blur(${blur}px) ` : ''}brightness(${luz}) grayscale(${gris}) drop-shadow(0 ${Math.round(18 * z)}px ${Math.round(22 * z)}px rgba(0,0,0,0.6))`}}
      />
    </div>
  );
};
/** Velo oscuro por abajo o por arriba, para asentar los elementos y leer el texto. */
const Velo: React.FC<{arriba?: number; abajo?: number}> = ({arriba = 0.55, abajo = 0.7}) => (
  <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(8,9,12,${arriba}) 0%, rgba(8,9,12,0) 38%, rgba(8,9,12,0) 62%, rgba(8,9,12,${abajo}) 100%)`}} />
);

// posiciones de las diez monedas: sueltas, de distinto tamano y giro, no en fila
const MONEDAS: [number, number, number, number][] = [
  [470, 470, 190, -18], [250, 440, 170, 24], [640, 640, 185, 40], [170, 640, 180, -8], [400, 700, 165, 62],
  [690, 430, 160, 33], [560, 880, 170, -30], [300, 900, 160, 12], [110, 860, 150, -50], [760, 800, 150, 80],
];
const CINTA: [number, number][] = [[1010, 772], [1130, 754], [1250, 737]];

/** 0-11 s · 41.858 M EUR, 1.672 tiendas y 3 de cada 10 euros de la compra. Tres planos con corte seco. */
export const Ventas: React.FC<EP> = ({t, p, dur, ctx}) => {
  const B = p(2);
  const C = p(3);
  if (B < 0) {
    // ---------------- A: el dinero
    const cam = deriva(t, 0, t - B, 60, 0.08);
    const x = lerp(-260, 760, sal(tr(t, 6, 70))) + t * 0.7;
    return (
      <AbsoluteFill>
        <FondoReal ctx={ctx} t={t} dur={dur} blur={7} luz={0.5} />
        <Velo />
        <Im src="g_fajos" x={1520} y={1230} w={880} t={t - 6} flip z={0.4} blur={2} luz={0.6} cam={cam} />
        <Im src="g_fajos" x={600} y={1230} w={1020} t={t - 1} z={0.7} luz={0.92} cam={cam} />
        <T x={960 - cam.x * 0.5} y={96} op={tr(t, 2, 6)}>
          <Serif tam={70} color="#D5DBE6">2025</Serif>
        </T>
        <T x={960 - cam.x * 0.5} y={250} s={0.86 + 0.14 * rebote(t / 14, 1.3) + cam.s * 0.5} op={tr(t, 0, 4)}>
          <Cifra tam={270}>{miles(Math.round(41858 * sal(t / 50)))}</Cifra>
          <Cifra tam={150}> M€</Cifra>
        </T>
        <T x={1300} y={430} s={pop(p(1), 11, 1.5)} rot={-2}>
          <Chip tam={46} fondo="#F4F5F7" tinta="#0B0C10">vendió Mercadona en un solo año</Chip>
        </T>
        <Im src="g_compradora" x={x} y={1100 + Math.abs(Math.sin(t / 4.5)) * -7} w={520} t={t - 4} de="nada" z={1.15} cam={cam} />
        <Im src="g_monedas" x={1800} y={1330} w={330} t={t - 3} z={1.9} blur={7} luz={0.75} cam={cam} />
      </AbsoluteFill>
    );
  }
  if (C < 0) {
    // ---------------- B: las tiendas, hasta donde alcanza la vista
    const cam = deriva(B, 0, C - B, 40, 0.09);
    const filas: [number, number, number, number, number, number][] = [
      // y, ancho, cuantas, x0, luz, blur
      [545, 250, 8, 80, 0.42, 2.4],
      [690, 350, 6, 150, 0.58, 1.4],
      [880, 500, 4, 230, 0.8, 0.5],
      [1150, 800, 2, 520, 1, 0],
    ];
    return (
      <AbsoluteFill>
        <FondoReal ctx={ctx} t={t} dur={dur} blur={9} luz={0.36} />
        <Velo arriba={0.75} abajo={0.5} />
        {filas.map(([y, w, n, x0, luz, blur], r) =>
          Array.from({length: n}, (_, i) => {
            const paso = (1920 - 2 * x0) / Math.max(1, n - 1);
            return <Im key={r + '-' + i} src="g_super_m" x={x0 + i * paso + (r % 2 ? 20 : -20)} y={y} w={w} t={B - (3 - r) * 3 - i * 1.2} de="pop" z={0.35 + r * 0.3} luz={luz} blur={blur} cam={cam} />;
          }),
        )}
        <T x={900} y={200} ancla="d" s={pop(B, 10, 1.4)}>
          <Cifra tam={280}>{miles(Math.round(1672 * sal(B / 26)))}</Cifra>
        </T>
        <T x={930} y={214} ancla="i" op={tr(B, 5, 6)}>
          <Serif tam={150} peso={600}>tiendas</Serif>
        </T>
      </AbsoluteFill>
    );
  }
  // ---------------- C: tres de cada diez euros pasan por sus cajas
  const D = p(4);
  const cam = deriva(C, 0, dur - (t - C), 50, 0.07);
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={8} luz={0.42} />
      <Velo arriba={0.7} abajo={0.6} />
      <Im src="g_caja" x={1380} y={1230} w={1150} t={C - 1} de="der" z={0.8} cam={cam} />
      <T x={110} y={140} ancla="i" op={tr(C, 2, 6)}>
        <Serif tam={128} peso={600}>De cada <span style={{color: '#FFD95A'}}>10 €</span></Serif>
      </T>
      <T x={116} y={250} ancla="i" op={tr(C, 6, 6)}>
        <Sans tam={40} peso={600} color="#D5DBE6">que se gastan en hacer la compra en España…</Sans>
      </T>
      {MONEDAS.map(([mx, my, w, rot], i) => {
        const tt = C - 5 - i * 2.2;
        if (tt < 0) return null;
        const cae = (1 - rebote(tt / 13, 0.9)) * -620;
        if (i < 3) {
          const u = io(tr(D, i * 5, 18));
          const x = lerp(mx, CINTA[i][0], u);
          const y = lerp(my, CINTA[i][1], u) - Math.sin(u * Math.PI) * 190;
          return (
            <div key={i} style={{position: 'absolute', left: 0, top: 0, transform: `translate(${-cam.x}px, 0)`}}>
              <div style={{position: 'absolute', left: x, top: y + cae, width: 0, height: 0, transform: `scaleY(${lerp(1, 0.62, u)})`}}>
                <Im src="g_moneda" x={0} y={lerp(w, 130, u) / 2} w={lerp(w, 130, u)} t={tt} de="nada" rot={rot + u * 200} z={1} />
              </div>
            </div>
          );
        }
        const ap = tr(D, 4, 12);
        return <Im key={i} src="g_moneda" x={mx} y={my + w / 2 + cae} w={w} t={tt} de="nada" rot={rot} z={1.1} cam={cam} gris={ap} luz={1 - 0.45 * ap} blur={ap * 1.2} />;
      })}
      <T x={1890} y={190} ancla="d" s={pop(D - 14, 12, 1.5)}>
        <Cifra tam={230}>28,5 %</Cifra>
      </T>
      <T x={1880} y={330} ancla="d" op={tr(D, 20, 8)}>
        <Sans tam={44} peso={700}>pasa por las cajas de Mercadona</Sans>
      </T>
      <T x={1880} y={392} ancla="d" op={tr(D, 24, 8)}>
        <Eti tam={24} color="#C9CED8">casi 3 de cada 10 euros</Eti>
      </T>
    </AbsoluteFill>
  );
};

export const VOX = {ventas: Ventas};
export {rnd};
