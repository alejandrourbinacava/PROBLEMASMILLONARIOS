import React, {createContext, useContext, useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

/**
 * Primitivas del estilo "doodle" del canal: papel de color, contorno de
 * rotulador grueso y relleno desplazado, como un sello mal alineado.
 * Todo lo que se dibuja pasa por <F> (forma), <L> (linea) y <T> (texto).
 */
export type Paleta = {
  fondo: string;
  tinta: string;
  c: Record<string, string>;
};

export const PAPELES: Record<string, string> = {
  crema: '#FAF3E3',
  menta: '#E7F3E8',
  rosa: '#FBE7E2',
  cielo: '#E4EFF9',
  mantequilla: '#FBF1C9',
  lila: '#EDE6F7',
};

export const paleta = (papel: string): Paleta => ({
  fondo: PAPELES[papel] ?? PAPELES.crema,
  tinta: '#1E1E24',
  c: {
    rojo: '#F0584A',
    amarillo: '#FFC93C',
    azul: '#4F9BE0',
    verde: '#52B788',
    madera: '#E9A15B',
    piel: '#F7CFAE',
    blanco: '#FFFFFF',
    oscuro: '#3A3A44',
    gris: '#C9C3B5',
    rosa: '#F59AB5',
    naranja: '#F5873A',
    morado: '#8F73D6',
    cielo: '#BFE0F5',
  },
});

export const Ctx = createContext<Paleta>(paleta('crema'));

// ---------------------------------------------------------------- fuentes
export const TEXTO = 'D Fredoka';
export const GRANDE = 'D Baloo';
const CARAS: [string, string][] = [
  [TEXTO, 'doodle/fonts/Fredoka-SemiBold.ttf'],
  [GRANDE, 'doodle/fonts/Baloo2-ExtraBold.ttf'],
];
let cargadas: Promise<void> | null = null;
export const useFuentes = () => {
  const [ok, setOk] = useState(false);
  const [h] = useState(() => delayRender('fuentes del doodle'));
  useEffect(() => {
    if (!cargadas) {
      cargadas = Promise.all(
        CARAS.map(async ([n, r]) => {
          const f = new FontFace(n, `url(${staticFile(r)})`);
          await f.load();
          (document as any).fonts.add(f);
        }),
      ).then(() => undefined);
    }
    cargadas.then(() => {
      setOk(true);
      continueRender(h);
    });
  }, [h]);
  return ok;
};

// ---------------------------------------------------------------- geometria
export const rr = (x: number, y: number, w: number, h: number, r = 12) =>
  `M${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h - r}Q${x + w},${y + h} ${x + w - r},${y + h}H${x + r}Q${x},${y + h} ${x},${y + h - r}V${y + r}Q${x},${y} ${x + r},${y}Z`;
export const el = (cx: number, cy: number, rx: number, ry: number) =>
  `M${cx - rx},${cy}a${rx},${ry} 0 1,0 ${2 * rx},0a${rx},${ry} 0 1,0 ${-2 * rx},0Z`;
export const ci = (cx: number, cy: number, r: number) => el(cx, cy, r, r);
export const poli = (pts: [number, number][]) => 'M' + pts.map((p) => p.join(',')).join('L') + 'Z';

// ---------------------------------------------------------------- forma
export const color = (t: Paleta, c: string) => (c === 'fondo' ? t.fondo : t.c[c] ?? c);

export const F: React.FC<{d: string; c: string; op?: number; w?: number}> = ({d, c, op = 1, w = 6}) => {
  const t = useContext(Ctx);
  const col = color(t, c);
  return (
    <g>
      <path d={d} fill={col} opacity={op} transform="translate(7,6)" />
      <path d={d} fill="none" stroke={t.tinta} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" />
    </g>
  );
};

/** Relleno sin contorno (reflejos, detalles pequenos). */
export const R: React.FC<{d: string; c: string; op?: number}> = ({d, c, op = 1}) => {
  const t = useContext(Ctx);
  return <path d={d} fill={color(t, c)} opacity={op} />;
};

export const L: React.FC<{d: string; c?: string; w?: number; op?: number}> = ({d, c = 'tinta', w = 6, op = 1}) => {
  const t = useContext(Ctx);
  const col = c === 'tinta' ? t.tinta : color(t, c);
  return <path d={d} fill="none" stroke={col} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" opacity={op} />;
};

export const T: React.FC<{
  x: number;
  y: number;
  px: number;
  children: React.ReactNode;
  c?: string;
  anchor?: 'start' | 'middle' | 'end';
  rot?: number;
  fam?: string;
  borde?: boolean;
}> = ({x, y, px, children, c, anchor = 'start', rot = 0, fam = TEXTO, borde}) => {
  const t = useContext(Ctx);
  const col = c ? color(t, c) : t.tinta;
  const conBorde = borde ?? !!c;
  return (
    <text
      x={x}
      y={y}
      fontSize={px}
      fontFamily={`"${fam}"`}
      fill={col}
      textAnchor={anchor}
      transform={rot ? `rotate(${rot} ${x} ${y})` : undefined}
      stroke={conBorde ? t.tinta : 'none'}
      strokeWidth={conBorde ? Math.max(5, px * 0.085) : 0}
      paintOrder="stroke"
      strokeLinejoin="round"
    >
      {children}
    </text>
  );
};

// ---------------------------------------------------------------- fondo y filtros
/** `semilla` cambia cada pocos fotogramas: el trazo "hierve" como un dibujo a mano. */
export const Defs: React.FC<{semilla?: number}> = ({semilla = 4}) => (
  <defs>
    <filter id="torcido" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency={0.016} numOctaves={2} seed={semilla} result="r" />
      <feDisplacementMap in="SourceGraphic" in2="r" scale={8} />
    </filter>
    <filter id="grano">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={2} seed={9} />
      <feColorMatrix type="saturate" values="0" />
    </filter>
  </defs>
);

export const Fondo: React.FC<{w: number; h: number}> = ({w, h}) => {
  const t = useContext(Ctx);
  return (
    <>
      <rect width={w} height={h} fill={t.fondo} />
      <rect width={w} height={h} filter="url(#grano)" opacity={0.08} />
    </>
  );
};
