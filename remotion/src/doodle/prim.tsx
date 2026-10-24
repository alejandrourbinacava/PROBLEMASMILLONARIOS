import React, {createContext, useContext, useEffect, useId, useState} from 'react';
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
  stick?: boolean;
  toon?: boolean;
};

export const PAPELES: Record<string, string> = {
  crema: '#FAF3E3',
  menta: '#E7F3E8',
  rosa: '#FBE7E2',
  cielo: '#E4EFF9',
  mantequilla: '#FBF1C9',
  lila: '#EDE6F7',
};

const STICK: Record<string, string> = {
  rojo: '#E5483B',
  amarillo: '#FFD23F',
  azul: '#CFE3F5',
  verde: '#CDEBD5',
  madera: '#EBD7B8',
  piel: '#FFFFFF',
  blanco: '#FFFFFF',
  oscuro: '#55555E',
  gris: '#E4E4E4',
  rosa: '#F9D3DC',
  naranja: '#FBC48E',
  morado: '#DDD3F2',
  cielo: '#E4F1FA',
};
const TOON: Record<string, string> = {
  rojo: '#D94A3D',
  amarillo: '#F2B93B',
  azul: '#3F78B5',
  verde: '#4E9A6B',
  madera: '#B87A4B',
  piel: '#FFFBF2',
  blanco: '#FFFFFF',
  oscuro: '#3B3640',
  gris: '#B8B4AC',
  rosa: '#E58BA5',
  naranja: '#E8803A',
  morado: '#7C5BA8',
  cielo: '#9CCBE8',
};
export const paleta = (papel: string): Paleta =>
  papel.startsWith('toon')
    ? {fondo: papel === 'toon2' ? '#DCCBA3' : '#E9D9B5', tinta: '#1E1B22', c: TOON, toon: true}
    : papel.startsWith('stick')
    ? {fondo: papel === 'stick2' ? '#F3F0E8' : '#FFFFFF', tinta: '#1E1E24', c: STICK, stick: true}
    : paleta0(papel);

const paleta0 = (papel: string): Paleta => ({
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
export const color = (t: Paleta, c: string) =>
  c === 'fondo' ? t.fondo : t.stick && c.startsWith('#') && !t.c[c] ? t.fondo : t.c[c] ?? c;

/** Oscurece un #rrggbb para la sombra de tebeo. */
export const oscurece = (hex: string, k = 0.78) => {
  if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return hex;
  const n = parseInt(hex.slice(1), 16);
  const f = (v: number) => Math.max(0, Math.min(255, Math.round(v * k)));
  return '#' + [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => f(v).toString(16).padStart(2, '0')).join('');
};

export const F: React.FC<{d: string; c: string; op?: number; w?: number}> = ({d, c, op = 1, w = 6}) => {
  const t = useContext(Ctx);
  const col = color(t, c);
  const id = useId().replace(/[^a-zA-Z0-9]/g, '');
  if (t.toon) {
    const sombra = oscurece(col.startsWith('#') ? col : '#888888', col === '#FFFFFF' || col === '#FFFBF2' ? 0.84 : 0.74);
    return (
      <g opacity={op}>
        <clipPath id={`cl${id}`}>
          <path d={d} />
        </clipPath>
        <path d={d} fill={sombra} />
        <g clipPath={`url(#cl${id})`}>
          <path d={d} fill={col} transform="translate(-9,-11)" />
        </g>
        <path d={d} fill="none" stroke={t.tinta} strokeWidth={w ? Math.max(3.4, w * 0.72) : 0} strokeLinecap="round" strokeLinejoin="round" />
      </g>
    );
  }
  if (t.stick)
    return (
      <g>
        <path d={d} fill={col} opacity={op} />
        <path d={d} fill="none" stroke={t.tinta} strokeWidth={w ? w + 1.5 : 0} strokeLinecap="round" strokeLinejoin="round" />
      </g>
    );
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
  const conBorde = borde ?? !!c;
  const col = c ? (t.stick && c === 'blanco' && !conBorde ? t.tinta : color(t, c)) : t.tinta;
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
    <radialGradient id="vig" cx="0.5" cy="0.5" r="0.75">
      <stop offset="0.55" stopColor="#2a1d0a" stopOpacity={0} />
      <stop offset="1" stopColor="#2a1d0a" stopOpacity={0.32} />
    </radialGradient>
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
      <rect width={w} height={h} filter="url(#grano)" opacity={t.toon ? 0.2 : 0.08} />
    </>
  );
};
