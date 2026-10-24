import React, {createContext, useContext, useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';

/**
 * Ilustracion por codigo: la MISMA escena se dibuja con cinco "pinceles".
 * Cada forma pasa por <F> (forma) y el estilo decide como se ve: relleno plano,
 * contorno de rotulador torcido, papel recortado con sombra, lapiz con rayado o tiza.
 */
export type Estilo = 'doodle' | 'plano' | 'recorte' | 'cuaderno' | 'tiza';
export const ESTILOS: Estilo[] = ['doodle', 'plano', 'recorte', 'cuaderno', 'tiza'];

type Tema = {
  fondo: string;
  tinta: string;
  texto: string;
  fuente: string;
  c: Record<string, string>;
};

const TEMAS: Record<Estilo, Tema> = {
  doodle: {
    fondo: '#FAF3E3',
    tinta: '#1E1E24',
    texto: '#1E1E24',
    fuente: 'D Fredoka',
    c: {rojo: '#F0584A', amarillo: '#FFC93C', azul: '#4F9BE0', verde: '#52B788', madera: '#E9A15B', piel: '#F7CFAE', blanco: '#FFFFFF', oscuro: '#3A3A44', gris: '#C9C3B5'},
  },
  plano: {
    fondo: '#16233B',
    tinta: '#16233B',
    texto: '#FFF4DC',
    fuente: 'D Anton',
    c: {rojo: '#FF6B57', amarillo: '#FFC447', azul: '#45B7D8', verde: '#3DC9A8', madera: '#C97B4A', piel: '#F4C7A1', blanco: '#FFF4DC', oscuro: '#24365A', gris: '#5B6F94'},
  },
  recorte: {
    fondo: '#C9A878',
    tinta: '#FFFFFF',
    texto: '#FFFFFF',
    fuente: 'D Fredoka',
    c: {rojo: '#D94F45', amarillo: '#F2B93B', azul: '#3E8EC4', verde: '#4DA37B', madera: '#B9763F', piel: '#F2C9A5', blanco: '#F8F1E1', oscuro: '#4A4048', gris: '#D8CFC0'},
  },
  cuaderno: {
    fondo: '#F6F4EE',
    tinta: '#2B2B30',
    texto: '#1C1C20',
    fuente: 'D Baloo',
    c: {rojo: '#CE2026', amarillo: '#F4D35E', azul: '#7DA7D9', verde: '#8CC7A1', madera: '#D9B38C', piel: '#F5DCC4', blanco: '#FFFFFF', oscuro: '#8A8F9A', gris: '#D6D8DE'},
  },
  tiza: {
    fondo: '#24433B',
    tinta: '#F4F1E6',
    texto: '#F4F1E6',
    fuente: 'D Fredoka',
    c: {rojo: '#FF8E7E', amarillo: '#FFE08A', azul: '#9FD8F0', verde: '#B6E8B0', madera: '#EBC9A0', piel: '#F4F1E6', blanco: '#F4F1E6', oscuro: '#F4F1E6', gris: '#C8D2CE'},
  },
};

const Ctx = createContext<{e: Estilo; t: Tema}>({e: 'doodle', t: TEMAS.doodle});

// ---------------------------------------------------------------- fuentes
const CARAS: [string, string][] = [
  ['D Fredoka', 'dibujo/fonts/Fredoka-SemiBold.ttf'],
  ['D Anton', 'dibujo/fonts/Anton-Regular.ttf'],
  ['D Baloo', 'dibujo/fonts/Baloo2-ExtraBold.ttf'],
];
let cargadas: Promise<void> | null = null;
const useFuentes = () => {
  const [ok, setOk] = useState(false);
  const [h] = useState(() => delayRender('fuentes del dibujo'));
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
const rr = (x: number, y: number, w: number, h: number, r = 12) =>
  `M${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h - r}Q${x + w},${y + h} ${x + w - r},${y + h}H${x + r}Q${x},${y + h} ${x},${y + h - r}V${y + r}Q${x},${y} ${x + r},${y}Z`;
const el = (cx: number, cy: number, rx: number, ry: number) =>
  `M${cx - rx},${cy}a${rx},${ry} 0 1,0 ${2 * rx},0a${rx},${ry} 0 1,0 ${-2 * rx},0Z`;
const ci = (cx: number, cy: number, r: number) => el(cx, cy, r, r);

// ---------------------------------------------------------------- forma
/** Una forma rellena. `c` es el nombre del color de la paleta. */
const F: React.FC<{d: string; c: string; op?: number; sombra?: boolean}> = ({d, c, op = 1, sombra = true}) => {
  const {e, t} = useContext(Ctx);
  const col = c === 'fondo' ? t.fondo : t.c[c] ?? c;
  switch (e) {
    case 'doodle':
      return (
        <g>
          <path d={d} fill={col} opacity={op} transform="translate(7,6)" />
          <path d={d} fill="none" stroke={t.tinta} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
        </g>
      );
    case 'plano':
      return <path d={d} fill={col} opacity={op} />;
    case 'recorte':
      return (
        <path
          d={d}
          fill={col}
          stroke="#FFFDF5"
          strokeWidth={8}
          strokeLinejoin="round"
          opacity={op}
          filter={sombra ? 'url(#sombraR)' : undefined}
        />
      );
    case 'cuaderno':
      return (
        <g>
          <path d={d} fill={col} opacity={0.55 * op} />
          <path d={d} fill="url(#raya)" opacity={0.5 * op} />
          <path d={d} fill="none" stroke={t.tinta} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round" />
        </g>
      );
    case 'tiza':
      return (
        <g>
          <path d={d} fill={col} opacity={0.16 * op} />
          <path d={d} fill="none" stroke={col} strokeWidth={5.5} strokeLinecap="round" strokeLinejoin="round" opacity={0.95 * op} />
        </g>
      );
  }
};

/** Una linea suelta (vapor, asa, grietas): solo trazo. */
const L: React.FC<{d: string; c?: string; w?: number}> = ({d, c = 'tinta', w = 6}) => {
  const {e, t} = useContext(Ctx);
  const col = c === 'tinta' ? (e === 'plano' ? t.c.blanco : e === 'recorte' ? '#FFFDF5' : t.tinta) : t.c[c] ?? c;
  return <path d={d} fill="none" stroke={col} strokeWidth={e === 'cuaderno' ? w * 0.6 : w} strokeLinecap="round" strokeLinejoin="round" />;
};

const T: React.FC<{x: number; y: number; px: number; children: React.ReactNode; c?: string; anchor?: 'start' | 'middle' | 'end'; rot?: number}> = ({
  x,
  y,
  px,
  children,
  c,
  anchor = 'start',
  rot = 0,
}) => {
  const {e, t} = useContext(Ctx);
  const col = c ? t.c[c] ?? c : t.texto;
  return (
    <text
      x={x}
      y={y}
      fontSize={px}
      fontFamily={`"${t.fuente}"`}
      fill={col}
      textAnchor={anchor}
      transform={rot ? `rotate(${rot} ${x} ${y})` : undefined}
      stroke={e === 'doodle' && c ? t.tinta : e === 'recorte' ? 'rgba(0,0,0,0.25)' : 'none'}
      strokeWidth={e === 'doodle' && c ? 7 : e === 'recorte' ? 2 : 0}
      paintOrder="stroke"
      strokeLinejoin="round"
      letterSpacing={e === 'plano' ? 2 : 0}
    >
      {children}
    </text>
  );
};

// ---------------------------------------------------------------- objetos
const Taza: React.FC<{x: number; y: number; k?: number}> = ({x, y, k = 1}) => (
  <g transform={`translate(${x},${y}) scale(${k})`}>
    <F d={el(0, 100, 140, 24)} c="gris" />
    <L d="M150,-30 q70,0 70,40 q0,40 -70,40" w={14} />
    <L d="M150,-30 q70,0 70,40 q0,40 -70,40" c="blanco" w={4} />
    <F d="M-100,-60 H100 Q100,80 0,80 Q-100,80 -100,-60 Z" c="blanco" />
    <F d={el(0, -60, 100, 22)} c="madera" />
    <L d="M-30,-130 q-30,-40 0,-70 q30,-30 0,-70" w={6} />
    <L d="M30,-120 q-30,-40 0,-70 q30,-30 0,-70" w={6} />
  </g>
);

const Persona: React.FC<{x: number; y: number; k?: number; pelo?: string; delantal?: string}> = ({x, y, k = 1, pelo = 'oscuro', delantal = 'rojo'}) => (
  <g transform={`translate(${x},${y}) scale(${k})`}>
    <F d={ci(0, -110, 62)} c={pelo} />
    <F d={rr(-90, -10, 180, 240, 70)} c="azul" />
    <F d={rr(-62, 40, 124, 190, 24)} c={delantal} />
    <F d={ci(0, -70, 70)} c="piel" />
    <F d={ci(0, -150, 34)} c={pelo} />
    <path d={ci(-24, -72, 6)} fill="#1E1E24" />
    <path d={ci(24, -72, 6)} fill="#1E1E24" />
    <L d="M-20,-40 Q0,-20 20,-40" w={5} />
  </g>
);

const Moneda: React.FC<{cx: number; y: number; r?: number; c?: string}> = ({cx, y, r = 72, c = 'amarillo'}) => (
  <g>
    <F d={rr(cx - r, y, r * 2, 20, 6)} c={c} />
    <F d={el(cx, y, r, r * 0.3)} c={c} />
  </g>
);
const Pila: React.FC<{cx: number; base: number; n: number; c?: string; r?: number; ini?: number}> = ({cx, base, n, c = 'amarillo', r = 72, ini = 0}) => {
  const f = useCurrentFrame();
  return (
    <g clipPath="url(#bajoTitulo)">
      <clipPath id="bajoTitulo"><rect x={0} y={250} width={1920} height={830} /></clipPath>
      {Array.from({length: n}).map((_, i) => {
        // cada moneda cae desde arriba con un rebote corto, una detras de otra
        const t0 = ini + i * 1.6;
        const u = Math.min(1, Math.max(0, (f - t0) / 9));
        if (f < t0) return null;
        const rebote = u < 1 ? (1 - u) * (1 - u) * -620 + Math.sin(u * Math.PI * 3) * 6 * (1 - u) : 0;
        return (
          <g key={i} transform={`translate(0,${rebote})`} opacity={Math.min(1, u * 4)}>
            <Moneda cx={cx} y={base - (i + 1) * 20} r={r} c={c} />
          </g>
        );
      })}
    </g>
  );
};
const useEntra = (t0: number, dur = 10) => {
  const f = useCurrentFrame();
  const u = Math.min(1, Math.max(0, (f - t0) / dur));
  return {u, esc: u < 1 ? 1 + (1 - u) * 0.0 : 1, op: Math.min(1, u * 3), dy: (1 - u) * (1 - u) * 60};
};
const Aparece: React.FC<{t0: number; children: React.ReactNode}> = ({t0, children}) => {
  const {op, dy} = useEntra(t0);
  return <g opacity={op} transform={`translate(0,${dy})`}>{children}</g>;
};

const Llave: React.FC<{x: number; y: number}> = ({x, y}) => (
  <g transform={`translate(${x},${y})`}>
    <F d={ci(0, 0, 60)} c="amarillo" />
    <F d={ci(0, 0, 22)} c="fondo" sombra={false} />
    <F d={rr(50, -14, 190, 28, 10)} c="amarillo" />
    <F d={rr(170, 14, 24, 50, 6)} c="amarillo" />
    <F d={rr(210, 14, 24, 36, 6)} c="amarillo" />
  </g>
);
const Barril: React.FC<{x: number; y: number}> = ({x, y}) => (
  <g transform={`translate(${x},${y})`}>
    <F d="M-110,-110 Q-150,0 -110,110 H110 Q150,0 110,-110 Z" c="madera" />
    <F d={rr(-132, -64, 264, 26, 8)} c="oscuro" />
    <F d={rr(-132, 40, 264, 26, 8)} c="oscuro" />
    <F d={ci(0, 0, 30)} c="amarillo" />
  </g>
);
const Sello: React.FC<{x: number; y: number}> = ({x, y}) => (
  <g transform={`translate(${x},${y})`}>
    <F d={rr(-24, -160, 48, 120, 18)} c="rojo" />
    <F d={rr(-70, -50, 140, 50, 12)} c="rojo" />
    <F d={rr(-120, 0, 240, 36, 10)} c="oscuro" />
    <F d={rr(-90, 50, 180, 12, 6)} c="azul" sombra={false} />
  </g>
);

// ---------------------------------------------------------------- fondos
const Fondo: React.FC<{w: number; h: number}> = ({w, h}) => {
  const {e, t} = useContext(Ctx);
  return (
    <>
      <rect width={w} height={h} fill={t.fondo} />
      {e === 'plano' && <rect width={w} height={h} fill="url(#degradado)" />}
      {e === 'recorte' && <rect width={w} height={h} filter="url(#grano)" opacity={0.28} />}
      {e === 'cuaderno' && <rect width={w} height={h} fill="url(#cuadro)" />}
      {e === 'tiza' && <rect width={w} height={h} fill="url(#pizarra)" />}
      {e === 'tiza' && <rect width={w} height={h} filter="url(#grano)" opacity={0.2} />}
      {e === 'doodle' && <rect width={w} height={h} filter="url(#grano)" opacity={0.08} />}
    </>
  );
};

const Defs: React.FC = () => {
  const {e} = useContext(Ctx);
  const esc = e === 'doodle' ? 8 : e === 'cuaderno' ? 4 : e === 'tiza' ? 7 : e === 'recorte' ? 3 : 0;
  return (
    <defs>
      <filter id="torcido" x="-5%" y="-5%" width="110%" height="110%">
        <feTurbulence type="fractalNoise" baseFrequency={e === 'tiza' ? 0.035 : 0.016} numOctaves={2} seed={4} result="r" />
        <feDisplacementMap in="SourceGraphic" in2="r" scale={esc} />
      </filter>
      <filter id="sombraR" x="-20%" y="-20%" width="140%" height="150%">
        <feDropShadow dx={6} dy={11} stdDeviation={7} floodColor="#2a1a08" floodOpacity={0.4} />
      </filter>
      <filter id="grano">
        <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves={2} seed={9} />
        <feColorMatrix type="saturate" values="0" />
      </filter>
      <linearGradient id="degradado" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#24365A" />
        <stop offset="1" stopColor="#101A2E" />
      </linearGradient>
      <radialGradient id="pizarra" cx="0.5" cy="0.45" r="0.8">
        <stop offset="0" stopColor="#2f5a4e" />
        <stop offset="1" stopColor="#1b342d" />
      </radialGradient>
      <pattern id="cuadro" width={46} height={46} patternUnits="userSpaceOnUse">
        <path d="M46,0V46M0,46H46" stroke="#AFC0D2" strokeWidth={1.4} opacity={0.6} fill="none" />
      </pattern>
      <pattern id="raya" width={14} height={14} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <path d="M0,0V14" stroke="#2B2B30" strokeWidth={1.6} opacity={0.5} />
      </pattern>
    </defs>
  );
};

// ---------------------------------------------------------------- escenas
const Bar: React.FC = () => (
  <g>
    <T x={110} y={130} px={92}>UN CAFÉ CON LECHE</T>
    <T x={110} y={206} px={52} c="rojo">en un bar de barrio</T>
    {/* ventana */}
    <F d={rr(1230, 270, 440, 300, 16)} c="azul" />
    <L d="M1450,270 V570 M1230,420 H1670" w={9} />
    <F d={rr(1210, 566, 480, 30, 8)} c="madera" />
    {/* balda y botellas */}
    <F d={rr(170, 440, 600, 24, 8)} c="madera" />
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <F key={i} d={rr(200 + i * 92, 340, 52, 100, 18)} c={['verde', 'amarillo', 'rojo', 'azul', 'verde', 'amarillo'][i]} />
    ))}
    {/* dueña */}
    <Persona x={560} y={600} k={1.18} />
    {/* barra */}
    <F d={rr(130, 770, 1660, 70, 16)} c="madera" />
    <F d={rr(170, 840, 1580, 190, 12)} c="oscuro" />
    <L d="M470,850 V1020 M770,850 V1020 M1070,850 V1020 M1370,850 V1020 M1670,850 V1020" w={5} />
    {/* taza */}
    <Taza x={1090} y={700} k={0.9} />
    {/* precio */}
    <g transform="rotate(-5 1500 640)">
      <F d={rr(1340, 560, 330, 160, 22)} c="amarillo" />
      <T x={1505} y={664} px={96} anchor="middle" c="oscuro">1,80 €</T>
      <T x={1505} y={706} px={32} anchor="middle" c="oscuro">café con leche</T>
    </g>
  </g>
);

const Monedas: React.FC = () => (
  <g>
    <T x={960} y={140} px={88} anchor="middle">UN CAFÉ A 1,80 €</T>
    <T x={960} y={214} px={50} anchor="middle" c="rojo">¿adónde va cada céntimo?</T>
    <L d="M560,300 Q960,260 1360,300" w={5} />
    {/* tres pilas */}
    <Pila cx={430} base={900} n={11} c="verde" ini={6} />
    <Pila cx={960} base={900} n={22} c="azul" ini={26} />
    <Pila cx={1490} base={900} n={3} c="rojo" ini={64} />
    <Aparece t0={28}><T x={430} y={640} px={80} anchor="middle" c="verde">0,55 €</T></Aparece>
    <Aparece t0={62}><T x={960} y={420} px={80} anchor="middle" c="azul">1,10 €</T></Aparece>
    <Aparece t0={74}><T x={1490} y={760} px={80} anchor="middle" c="rojo">0,15 €</T></Aparece>
    <T x={430} y={970} px={44} anchor="middle">el producto</T>
    <T x={960} y={970} px={44} anchor="middle">alquiler, sueldos…</T>
    <T x={1490} y={970} px={44} anchor="middle">la dueña</T>
    <g transform="translate(1490,640)">
      <L d="M0,0 V-60 M-30,-30 L0,0 L30,-30" c="rojo" w={9} />
    </g>
  </g>
);

const Fachada: React.FC = () => (
  <g>
    <T x={960} y={120} px={84} anchor="middle">SEIS DUEÑOS EN TU BAR</T>
    {/* edificio */}
    <F d={rr(560, 330, 800, 650, 12)} c="blanco" />
    <F d={rr(540, 300, 840, 54, 10)} c="oscuro" />
    <F d={rr(660, 380, 600, 110, 18)} c="verde" />
    <T x={960} y={466} px={96} anchor="middle" c="blanco">BAR</T>
    {/* toldo */}
    {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
      <F key={i} d={`M${600 + i * 90},520 h90 v60 q-45,36 -90,0 Z`} c={i % 2 ? 'blanco' : 'rojo'} />
    ))}
    <F d={rr(630, 640, 260, 220, 14)} c="amarillo" />
    <F d={rr(1030, 640, 260, 220, 14)} c="amarillo" />
    <F d={rr(890, 620, 140, 360, 14)} c="madera" />
    <path d={ci(1010, 800, 8)} fill="#1E1E24" />
    {/* los dueños */}
    <g transform="scale(0.8) translate(150,330)">
      <Llave x={90} y={90} />
    </g>
    <T x={190} y={560} px={44} anchor="middle" c="amarillo">el casero</T>
    <g transform="translate(1620,430) scale(0.8)">
      <Barril x={0} y={0} />
    </g>
    <T x={1620} y={560} px={44} anchor="middle" c="amarillo">la cervecera</T>
    <g transform="translate(300,850) scale(0.8)">
      <Sello x={0} y={0} />
    </g>
    <T x={300} y={940} px={44} anchor="middle" c="amarillo">el ayuntamiento</T>
    <g transform="translate(1620,900)">
      <Pila cx={0} base={0} n={3} c="rojo" r={60} />
    </g>
    <T x={1620} y={960} px={44} anchor="middle" c="amarillo">y tú, el último</T>
    <L d="M330,540 Q460,560 540,600" w={5} />
    <L d="M1450,540 Q1400,580 1360,620" w={5} />
    <L d="M400,760 Q470,780 540,800" w={5} />
    <L d="M1560,860 Q1460,860 1370,840" w={5} />
  </g>
);

export type Escena = 'bar' | 'monedas' | 'fachada';
const ESCENAS: Record<Escena, React.FC> = {bar: Bar, monedas: Monedas, fachada: Fachada};

export const Dibujo: React.FC<{estilo: Estilo; escena: Escena}> = ({estilo, escena}) => {
  const ok = useFuentes();
  const t = TEMAS[estilo];
  const S = ESCENAS[escena];
  if (!ok) return <AbsoluteFill style={{background: t.fondo}} />;
  return (
    <AbsoluteFill>
      <Ctx.Provider value={{e: estilo, t}}>
        <svg width={1920} height={1080} viewBox="0 0 1920 1080">
          <Defs />
          <Fondo w={1920} h={1080} />
          <g filter={estilo === 'plano' ? undefined : 'url(#torcido)'}>
            <S />
          </g>
        </svg>
      </Ctx.Provider>
    </AbsoluteFill>
  );
};
