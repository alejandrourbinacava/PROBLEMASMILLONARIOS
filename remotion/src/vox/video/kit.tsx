import React from 'react';
import {EUROPA} from './europa';

/**
 * Kit de animacion (piel `anim`): escenas construidas como las de Moatseek.
 * No hay fotos apiladas: cada idea se representa con actores planos de color
 * (personas, tiendas, camiones, fajos, monedas, paises) sobre un escenario
 * limpio, que se mueven y se cuentan delante del espectador, y una camara que
 * viaja de un grupo al siguiente.
 *
 *   Escenario  ->  Mundo (camara)  ->  actores  ->  cifras y rotulos
 *
 * Todo se coloca en coordenadas de mundo (1920 x 1080 es un encuadre a zoom 1).
 */
export const c01 = (u: number) => Math.min(1, Math.max(0, u));
export const io = (u: number) => {
  const x = c01(u);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
export const sal = (u: number) => 1 - Math.pow(1 - c01(u), 3);
export const rebote = (u: number, k = 1.7) => {
  const x = c01(u) - 1;
  return 1 + (k + 1) * x * x * x + k * x * x;
};
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
/** 0..1 desde el fotograma t0, en d fotogramas. */
export const tr = (t: number, t0: number, d = 12) => c01((t - t0) / d);
/** Escala de aparicion con rebote; 0 antes de empezar. */
export const pop = (t: number, d = 11, k = 1.9) => (t < 0 ? 0 : 0.25 + 0.75 * rebote(t / d, k));
export const rnd = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
export const miles = (v: number, dec = 0) => {
  const [e, d] = Math.abs(v).toFixed(dec).split('.');
  return (v < 0 ? '-' : '') + e.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + (d ? ',' + d : '');
};
/** Valor interpolado entre claves [fotograma, valor]. */
export const kf = (t: number, claves: [number, number][], curva: (u: number) => number = io) => {
  if (t <= claves[0][0]) return claves[0][1];
  for (let i = 1; i < claves.length; i++) {
    if (t <= claves[i][0]) {
      const [f0, v0] = claves[i - 1];
      const [f1, v1] = claves[i];
      return lerp(v0, v1, curva((t - f0) / Math.max(1, f1 - f0)));
    }
  }
  return claves[claves.length - 1][1];
};

// ---------------------------------------------------------------- color
export type Col = 'verde' | 'rosa' | 'azul' | 'cian' | 'ambar' | 'rojo' | 'blanco' | 'humo' | 'menta' | 'lila';
export const PAL: Record<Col, [string, string]> = {
  verde: ['#2BE38A', '#0A9150'],
  rosa: ['#FF4FA3', '#C4086A'],
  azul: ['#5B84FF', '#1B36C9'],
  cian: ['#45D0FF', '#0A7BD6'],
  ambar: ['#FFD95A', '#F29A0B'],
  rojo: ['#FF6A5C', '#C4161C'],
  blanco: ['#FFFFFF', '#D5DBE6'],
  humo: ['#5C6375', '#2F3442'],
  menta: ['#D9F7E3', '#9BDDB4'],
  lila: ['#B79CFF', '#6B3FE0'],
};
export const FONDO = '#0B0C10';
export const TINTA = '#F4F5F7';
export const GRIS = '#8D93A1';
export const grad = (c: Col, ang = 180) => `linear-gradient(${ang}deg, ${PAL[c][0]}, ${PAL[c][1]})`;

/** Degradados compartidos por todos los SVG. Se pinta una vez en la raiz. */
export const Defs: React.FC = () => (
  <svg width={0} height={0} style={{position: 'absolute'}}>
    <defs>
      {(Object.keys(PAL) as Col[]).map((c) => (
        <React.Fragment key={c}>
          <linearGradient id={`g-${c}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={PAL[c][0]} />
            <stop offset="1" stopColor={PAL[c][1]} />
          </linearGradient>
          {/* para figuras: el degradado recorre la figura entera, de la cabeza a los pies */}
          <linearGradient id={`gp-${c}`} gradientUnits="userSpaceOnUse" x1="0" y1="-235" x2="0" y2="0">
            <stop offset="0" stopColor={PAL[c][0]} />
            <stop offset="1" stopColor={PAL[c][1]} />
          </linearGradient>
        </React.Fragment>
      ))}
      <linearGradient id="g-oro" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#FFE27A" />
        <stop offset="1" stopColor="#D9940A" />
      </linearGradient>
      <linearGradient id="g-plata" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#F3F5F8" />
        <stop offset="1" stopColor="#A9B1BE" />
      </linearGradient>
      <linearGradient id="g-cristal" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#33405A" />
        <stop offset="1" stopColor="#141B2A" />
      </linearGradient>
    </defs>
  </svg>
);

// ---------------------------------------------------------------- escenario y camara
export type Cam = {x: number; y: number; z: number};
/** Camara por claves [fotograma, x, y, zoom]; entre clave y clave acelera y frena. */
export const camara = (t: number, claves: [number, number, number, number][]): Cam => ({
  x: kf(t, claves.map((c) => [c[0], c[1]] as [number, number])),
  y: kf(t, claves.map((c) => [c[0], c[2]] as [number, number])),
  z: kf(t, claves.map((c) => [c[0], c[3]] as [number, number])),
});

export const Mundo: React.FC<{cam: Cam; children: React.ReactNode; f?: number}> = ({cam, children}) => (
  <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0', transform: `translate(${960 - cam.x * cam.z}px, ${540 - cam.y * cam.z}px) scale(${cam.z})`}}>{children}</div>
);

/** Fondo del plano. `oscuro` es el de siempre; `verde` y `claro` cambian el registro. */
export const Escenario: React.FC<{tipo?: 'oscuro' | 'verde' | 'claro' | 'azul'; cam?: Cam}> = ({tipo = 'oscuro', cam}) => {
  const bg = tipo === 'verde' ? 'linear-gradient(180deg, #12B764 0%, #07753F 100%)' : tipo === 'azul' ? 'linear-gradient(180deg, #1F56D8 0%, #0B1FA8 100%)' : tipo === 'claro' ? 'linear-gradient(180deg, #FFFFFF 0%, #E7EAF0 100%)' : `radial-gradient(ellipse at 50% 40%, #14161D 0%, ${FONDO} 70%)`;
  const lin = tipo === 'claro' ? 'rgba(10,20,40,0.05)' : 'rgba(255,255,255,0.045)';
  // el dibujo de lineas se mueve muy poco con la camara: da profundidad sin distraer
  const dx = cam ? -cam.x * 0.06 : 0;
  const dy = cam ? -cam.y * 0.04 : 0;
  return (
    <div style={{position: 'absolute', inset: 0, background: bg, overflow: 'hidden'}}>
      <svg width={2600} height={1400} style={{position: 'absolute', left: -200 + (dx % 520), top: -120 + dy}} fill="none" stroke={lin} strokeWidth={2}>
        {[0, 1, 2, 3, 4].map((i) => (
          <g key={i} transform={`translate(${i * 520},0)`}>
            <path d="M40,160 L220,60 L400,160 L400,420 L220,520 L40,420 Z" />
            <path d="M300,620 L480,520 L660,620 L660,880 L480,980 L300,880 Z" />
            <path d="M-80,940 L100,840 L280,940 L280,1200" />
            <path d="M220,60 L220,-80 M480,980 L480,1200" />
          </g>
        ))}
      </svg>
    </div>
  );
};

type AP = {x: number; y: number; s?: number; rot?: number; op?: number; children?: React.ReactNode};
/** Un actor: se coloca en (x, y) del mundo y dibuja en pixeles alrededor de ese punto. */
export const A: React.FC<AP & {flip?: boolean}> = ({x, y, s = 1, rot = 0, op = 1, flip, children}) =>
  op <= 0 || s <= 0 ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, opacity: op, transform: `rotate(${rot}deg) scale(${flip ? -s : s}, ${s})`}}>
      <svg width={1} height={1} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        {children}
      </svg>
    </div>
  );
/** Lo mismo para contenido HTML (texto). `ancla`: c centro, i izquierda, d derecha. */
export const T: React.FC<AP & {ancla?: 'c' | 'i' | 'd'; arriba?: boolean; estilo?: React.CSSProperties}> = ({x, y, s = 1, rot = 0, op = 1, ancla = 'c', arriba, estilo, children}) =>
  op <= 0 || s <= 0 ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, opacity: op}}>
      <div style={{position: 'absolute', whiteSpace: 'nowrap', transform: `translate(${ancla === 'c' ? '-50%' : ancla === 'd' ? '-100%' : '0'}, ${arriba ? '0' : '-50%'}) rotate(${rot}deg) scale(${s})`, transformOrigin: ancla === 'c' ? '50% 50%' : ancla === 'd' ? '100% 50%' : '0 50%', ...estilo}}>{children}</div>
    </div>
  );

// ---------------------------------------------------------------- texto
/** Cifra gorda con degradado y canto, como un bloque. */
export const Cifra: React.FC<{children: React.ReactNode; tam?: number; color?: Col; canto?: boolean}> = ({children, tam = 150, color = 'verde', canto = true}) => (
  <span style={{font: `${tam}px/1 'M Black'`, letterSpacing: -tam * 0.02, background: grad(color), WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', filter: canto ? `drop-shadow(0 ${Math.max(3, tam * 0.045)}px 0 ${PAL[color][1]}66) drop-shadow(0 ${tam * 0.1}px ${tam * 0.16}px rgba(0,0,0,0.45))` : undefined, padding: `0 ${tam * 0.04}px`}}>{children}</span>
);
export const Serif: React.FC<{children: React.ReactNode; tam?: number; color?: string; peso?: number; it?: boolean}> = ({children, tam = 64, color = TINTA, peso = 500, it}) => (
  <span style={{font: `${it ? 'italic ' : ''}${peso} ${tam}px/1.12 'M Serif'`, color, letterSpacing: -tam * 0.012}}>{children}</span>
);
/** Etiqueta pequena en mayusculas espaciadas. */
export const Eti: React.FC<{children: React.ReactNode; tam?: number; color?: string}> = ({children, tam = 26, color = GRIS}) => (
  <span style={{font: `600 ${tam}px/1.2 'D Sans'`, letterSpacing: tam * 0.14, textTransform: 'uppercase', color}}>{children}</span>
);
export const Sans: React.FC<{children: React.ReactNode; tam?: number; color?: string; peso?: number}> = ({children, tam = 40, color = TINTA, peso = 600}) => (
  <span style={{font: `${peso} ${tam}px/1.2 'D Sans'`, color}}>{children}</span>
);
/** Pastilla de color con texto (tambien para nombrar marcas sin usar su logotipo). */
export const Chip: React.FC<{children: React.ReactNode; color?: Col; tam?: number; tinta?: string; fondo?: string; borde?: string}> = ({children, color = 'verde', tam = 40, tinta = '#fff', fondo, borde}) => (
  <span style={{display: 'inline-block', font: `${tam}px/1 'M Black'`, color: tinta, background: fondo ?? grad(color), padding: `${tam * 0.34}px ${tam * 0.6}px ${tam * 0.3}px`, borderRadius: tam * 0.42, boxShadow: '0 10px 30px rgba(0,0,0,0.35)', border: borde ? `${Math.max(2, tam * 0.07)}px solid ${borde}` : undefined, letterSpacing: -0.5}}>{children}</span>
);
/** Numero gigante solo en contorno, detras de todo. */
export const Fantasma: React.FC<{x: number; y: number; children: React.ReactNode; tam?: number; op?: number; claro?: boolean}> = ({x, y, children, tam = 620, op = 1, claro}) => (
  <T x={x} y={y} op={op}>
    <span style={{font: `500 ${tam}px/1 'M Serif'`, color: 'transparent', WebkitTextStroke: `2px ${claro ? 'rgba(10,20,40,0.10)' : 'rgba(255,255,255,0.09)'}`, letterSpacing: -tam * 0.03}}>{children}</span>
  </T>
);
/** Palabras que aparecen una a una (para citas): u es el progreso 0..1 de la frase entera. */
export const Palabras: React.FC<{texto: string; u: number; resalta?: string; color?: string}> = ({texto, u, resalta = '#FFD95A', color = TINTA}) => {
  const trozos = texto.split(/(\*[^*]+\*)/g).filter(Boolean);
  const pal: {w: string; r: boolean}[] = [];
  trozos.forEach((x) => {
    const r = x.startsWith('*');
    (r ? x.slice(1, -1) : x).split(/\s+/).filter(Boolean).forEach((w) => pal.push({w, r}));
  });
  return (
    <>
      {pal.map((q, i) => {
        const v = c01(u * pal.length - i);
        return (
          <span key={i} style={{opacity: 0.12 + 0.88 * v, color: q.r ? resalta : color, display: 'inline-block', marginRight: '0.26em', transform: `translateY(${(1 - sal(v)) * 10}px)`}}>
            {q.w}
          </span>
        );
      })}
    </>
  );
};
/**
 * Tira de papel rasgada con el texto de un documento. `trozos`: texto normal o
 * {m: 'texto resaltado', en: fotograma en que se pinta el resaltado}.
 */
export const Tira: React.FC<{x: number; y: number; t: number; trozos: (string | {m: string; en: number})[]; ancho?: number; tam?: number; rot?: number; color?: string; sale?: number}> = ({x, y, t, trozos, ancho = 1500, tam = 46, rot = -1.5, color = 'rgba(255,90,80,0.5)', sale = 1e6}) => {
  if (t < 0 || t > sale + 8) return null;
  const e = rebote(t / 12, 1.2);
  const fuera = c01((t - sale) / 8);
  const n = 26;
  const borde = (y0: number, sd: number) => Array.from({length: n + 1}, (_, i) => `${(i / n) * 100}% ${y0 + (rnd(i * 3.1 + sd) - 0.5) * 9}%`);
  const clip = `polygon(${[...borde(7, 1), ...borde(93, 2).reverse()].join(',')})`;
  return (
    <div style={{position: 'absolute', left: x, top: y - fuera * 160, width: 0, height: 0}}>
      <div style={{position: 'absolute', width: ancho, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${0.7 + 0.3 * e})`, opacity: c01(t / 3) * (1 - fuera), filter: 'drop-shadow(0 18px 30px rgba(0,0,0,0.55))'}}>
        <div style={{background: '#FAFAF7', clipPath: clip, padding: `${tam * 0.95}px ${tam * 1.2}px`, font: `500 ${tam}px/1.5 'D Sans'`, color: '#1B1D22', textAlign: 'center'}}>
          {trozos.map((q, i) =>
            typeof q === 'string' ? (
              <span key={i}>{q}</span>
            ) : (
              <span key={i} style={{backgroundImage: `linear-gradient(${color}, ${color})`, backgroundRepeat: 'no-repeat', backgroundSize: `${c01((t - q.en) / 12) * 100}% 100%`, padding: '2px 6px', boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone'}}>{q.m}</span>
            ),
          )}
        </div>
      </div>
    </div>
  );
};

/** Hoja de calendario con un ano. Centro en (x, y). */
export const Hoja: React.FC<{x: number; y: number; anio: string; s?: number; op?: number; color?: Col; apagada?: number; tam?: number}> = ({x, y, anio, s = 1, op = 1, color = 'rojo', apagada = 0, tam = 54}) =>
  op <= 0 || s <= 0 ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, opacity: op}}>
      <div style={{position: 'absolute', left: -88, top: -98, width: 176, height: 196, borderRadius: 20, overflow: 'hidden', background: '#F4F5F7', transform: `scale(${s})`, boxShadow: '0 16px 40px rgba(0,0,0,0.45)', filter: `grayscale(${apagada}) brightness(${1 - apagada * 0.45})`}}>
        <div style={{height: 50, background: grad(color)}} />
        <div style={{position: 'absolute', left: 38, top: 16, width: 16, height: 16, borderRadius: 8, background: '#fff', opacity: 0.85}} />
        <div style={{position: 'absolute', right: 38, top: 16, width: 16, height: 16, borderRadius: 8, background: '#fff', opacity: 0.85}} />
        <div style={{font: `${tam}px/146px 'M Black'`, color: '#1B1D22', textAlign: 'center', letterSpacing: -1}}>{anio}</div>
      </div>
    </div>
  );

/** Sello de tampon: cae de golpe sobre lo que marca. */
export const Sello: React.FC<{x: number; y: number; t: number; children: React.ReactNode; rot?: number; tam?: number; color?: string}> = ({x, y, t, children, rot = -9, tam = 84, color = '#FF5A4D'}) =>
  t < 0 ? null : (
    <T x={x} y={y} rot={rot} s={1 + 1.6 * (1 - sal(t / 6))} op={c01(t / 3)}>
      <span style={{display: 'inline-block', font: `${tam}px/1 'M Black'`, color, border: `${tam * 0.1}px solid ${color}`, borderRadius: tam * 0.2, padding: `${tam * 0.22}px ${tam * 0.4}px ${tam * 0.16}px`, letterSpacing: 2, background: 'rgba(11,12,16,0.72)', textTransform: 'uppercase'}}>{children}</span>
    </T>
  );

// ---------------------------------------------------------------- actores
/** Persona de papel. Los pies estan en (x, y). `fase` (radianes) la hace andar. */
export const Persona: React.FC<AP & {color?: Col; fase?: number; flip?: boolean; brazo?: number}> = ({color = 'verde', fase, brazo, ...a}) => {
  const g = `url(#gp-${color})`;
  const an = fase === undefined ? 0 : Math.sin(fase);
  const bote = fase === undefined ? 0 : -Math.abs(Math.cos(fase)) * 5;
  const pierna = (lado: number) => <rect x={lado * 14 - 12} y={-104} width={24} height={104} rx={12} fill={g} transform={`rotate(${lado * an * 24} ${lado * 14} -100)`} />;
  const brz = (lado: number, ang: number) => <rect x={lado * 37 - 9.5} y={-172} width={19} height={84} rx={9.5} fill={g} transform={`rotate(${ang} ${lado * 37} -166)`} />;
  return (
    <A {...a}>
      <g transform={`translate(0 ${bote})`}>
        {pierna(-1)}
        {pierna(1)}
        {brz(-1, 9 + an * 20)}
        <path d="M-36,-150 Q-36,-182 -8,-182 L8,-182 Q36,-182 36,-150 L30,-104 Q28,-90 14,-90 L-14,-90 Q-28,-90 -30,-104 Z" fill={g} />
        {brz(1, brazo ?? -9 - an * 20)}
        <circle cx={0} cy={-208} r={27} fill={g} />
      </g>
    </A>
  );
};

/** Supermercado visto de frente. La base esta en (x, y). `cierre` 0..1 baja la persiana. */
export const Tienda: React.FC<AP & {color?: Col; nombre?: string; cierre?: number; ancho?: number; luz?: number}> = ({color = 'verde', nombre, cierre = 0, ancho = 280, luz = 1, ...a}) => {
  const w = ancho / 2;
  const hueco = (x0: number, x1: number, y0: number) => (
    <g>
      <rect x={x0} y={y0} width={x1 - x0} height={-y0} rx={5} fill="url(#g-cristal)" />
      <path d={`M${x0 + 8},${y0 + 40} L${x0 + 40},${y0 + 6} L${x0 + 58},${y0 + 6} L${x0 + 8},${y0 + 62} Z`} fill="#fff" opacity={0.12 * luz} />
      {cierre > 0 && <rect x={x0} y={y0} width={x1 - x0} height={-y0 * cierre} fill="#8E96A6" />}
      {cierre > 0 && Array.from({length: 7}, (_, i) => -y0 * cierre > (i + 1) * 16 && <rect key={i} x={x0} y={y0 + (i + 1) * 16} width={x1 - x0} height={2.5} fill="#6B7383" />)}
    </g>
  );
  return (
    <A {...a}>
      <ellipse cx={0} cy={4} rx={w + 26} ry={12} fill="#000" opacity={0.35} />
      <rect x={-w + 8} y={-150} width={ancho - 16} height={150} fill="#EEF1F6" />
      <rect x={-w + 8} y={-16} width={ancho - 16} height={16} fill="#CCD2DD" />
      {hueco(-w + 26, -40, -112)}
      {hueco(40, w - 26, -112)}
      <g transform="translate(0 -14)">{hueco(-30, 30, -112)}</g>
      <rect x={-1.5} y={-126} width={3} height={112} fill="#0B0F18" opacity={0.6} />
      <rect x={-w} y={-204} width={ancho} height={58} rx={10} fill={`url(#g-${color})`} />
      <rect x={-w} y={-152} width={ancho} height={8} fill={PAL[color][1]} />
      {nombre && (
        <text x={0} y={-164} textAnchor="middle" style={{font: `${nombre.length > 9 ? 27 : 32}px 'M Black'`}} fill="#fff">
          {nombre}
        </text>
      )}
    </A>
  );
};
/** Tienda diminuta para rejillas y mapas (se dibuja dentro de un <svg> propio). */
export const mini = (x: number, y: number, s: number, c1: string, c2 = '#EEF1F6', key?: React.Key, op = 1) => (
  <g key={key} transform={`translate(${x} ${y}) scale(${s})`} opacity={op}>
    <rect x={-9} y={-2} width={18} height={10} fill={c2} />
    <rect x={-11} y={-9} width={22} height={8} rx={2} fill={c1} />
    <rect x={-2.5} y={2} width={5} height={6} fill="#2A3346" />
  </g>
);

/** Camion mirando a la derecha. Las ruedas se apoyan en (x, y). `avance` gira las ruedas. */
export const Camion: React.FC<AP & {color?: Col; nombre?: string; flip?: boolean; avance?: number; carga?: number}> = ({color = 'verde', nombre, avance = 0, ...a}) => {
  const rueda = (cx: number) => (
    <g transform={`translate(${cx} -24)`}>
      <circle r={24} fill="#12151C" />
      <circle r={10} fill="#8E96A6" />
      <rect x={-1.5} y={-10} width={3} height={20} fill="#12151C" transform={`rotate(${avance * 2.4})`} />
    </g>
  );
  return (
    <A {...a}>
      <ellipse cx={0} cy={2} rx={220} ry={10} fill="#000" opacity={0.35} />
      <rect x={-210} y={-190} width={300} height={150} rx={12} fill="#F1F3F7" />
      <rect x={-210} y={-92} width={300} height={22} fill={`url(#g-${color})`} />
      <rect x={-210} y={-46} width={300} height={10} fill="#2B3140" />
      <path d="M98,-150 L150,-150 Q172,-150 182,-128 L204,-84 Q210,-74 210,-62 L210,-36 L98,-36 Z" fill={`url(#g-${color})`} />
      <path d="M112,-136 L150,-136 Q162,-136 168,-124 L186,-88 L112,-88 Z" fill="url(#g-cristal)" />
      {nombre && (
        <g transform={a.flip ? 'scale(-1 1)' : undefined}>
          <text x={a.flip ? 60 : -60} y={-124} textAnchor="middle" style={{font: "30px 'M Black'"}} fill={PAL[color][1]}>
            {nombre}
          </text>
        </g>
      )}
      {rueda(-150)}
      {rueda(-92)}
      {rueda(150)}
    </A>
  );
};

/** Bloque logistico / almacen. Base en (x, y). */
export const Almacen: React.FC<AP & {color?: Col; nombre?: string}> = ({color = 'verde', nombre, ...a}) => (
  <A {...a}>
    <ellipse cx={0} cy={4} rx={300} ry={12} fill="#000" opacity={0.35} />
    <rect x={-280} y={-170} width={560} height={170} fill="#E4E8EF" />
    <path d="M-290,-170 L-280,-196 L280,-196 L290,-170 Z" fill="#C5CBD7" />
    <rect x={-280} y={-150} width={560} height={30} fill={`url(#g-${color})`} />
    {[-220, -130, -40, 50, 140].map((x) => (
      <g key={x}>
        <rect x={x} y={-92} width={70} height={92} rx={4} fill="#2A3142" />
        {[0, 1, 2, 3].map((i) => <rect key={i} x={x} y={-76 + i * 20} width={70} height={3} fill="#454D61" />)}
      </g>
    ))}
    {nombre && (
      <text x={0} y={-127} textAnchor="middle" style={{font: "24px 'M Black'"}} fill="#fff">
        {nombre}
      </text>
    )}
  </A>
);

/** Fabrica con tejado en sierra. Base en (x, y). `t` mueve el humo. */
export const Fabrica: React.FC<AP & {color?: Col; t?: number}> = ({color = 'ambar', t = 0, ...a}) => (
  <A {...a}>
    <ellipse cx={0} cy={4} rx={170} ry={10} fill="#000" opacity={0.35} />
    {[0, 1, 2].map((i) => {
      const u = ((t + i * 16) % 48) / 48;
      return <circle key={i} cx={104 + u * 26} cy={-214 - u * 70} r={10 + u * 18} fill="#fff" opacity={0.28 * (1 - u)} />;
    })}
    <rect x={88} y={-210} width={32} height={120} fill="#C5CBD7" />
    <rect x={88} y={-210} width={32} height={14} fill={`url(#g-${color})`} />
    <path d="M-150,0 L-150,-120 L-90,-160 L-90,-120 L-30,-160 L-30,-120 L30,-160 L30,-120 L150,-120 L150,0 Z" fill="#E4E8EF" />
    <rect x={-150} y={-22} width={300} height={22} fill={`url(#g-${color})`} />
    {[-120, -60, 0, 60].map((x) => <rect key={x} x={x} y={-92} width={38} height={38} rx={4} fill="url(#g-cristal)" />)}
  </A>
);

/** Fajo de billetes de euro, visto de frente. Centro en (x, y). */
export const Fajo: React.FC<AP & {tono?: number}> = ({tono = 0, ...a}) => (
  <A {...a}>
    <rect x={-66} y={-27} width={132} height={58} rx={7} fill="#3E9C63" />
    <rect x={-66} y={-31} width={132} height={56} rx={7} fill={tono ? '#C9EFD6' : '#DDF6E5'} />
    <rect x={-58} y={-24} width={116} height={42} rx={4} fill="none" stroke="#6FBF8C" strokeWidth={2.5} />
    <circle cx={-34} cy={-3} r={12} fill="#8BD3A4" />
    <rect x={-10} y={-31} width={26} height={56} fill="#fff" />
    <rect x={-10} y={-31} width={26} height={56} fill="#19A05B" opacity={0.18} />
    <text x={3} y={7} textAnchor="middle" style={{font: "26px 'M Black'"}} fill="#128249">
      €
    </text>
    <rect x={30} y={-12} width={22} height={5} rx={2.5} fill="#6FBF8C" />
    <rect x={30} y={-1} width={16} height={5} rx={2.5} fill="#6FBF8C" />
  </A>
);

/** Moneda de un euro. Centro en (x, y), radio 50. `gris` la apaga. */
export const Moneda: React.FC<AP & {gris?: number; cara?: string}> = ({gris = 0, cara = '€', ...a}) => (
  <A {...a}>
    <circle r={50} cy={5} fill="#8A5E05" opacity={1 - gris} />
    <circle r={50} cy={5} fill="#3A3F4B" opacity={gris} />
    <circle r={50} fill="url(#g-oro)" />
    <circle r={33} fill="url(#g-plata)" />
    <circle r={50} fill="#4A5060" opacity={gris * 0.82} />
    <text y={15} textAnchor="middle" style={{font: "800 44px 'D Sans'"}} fill={gris > 0.5 ? '#8D93A1' : '#4A5160'}>
      {cara}
    </text>
  </A>
);

/** Caja de producto generica. Base en (x, y). */
export const Caja: React.FC<AP & {color?: Col; alto?: number; ancho?: number; marca?: string}> = ({color = 'verde', alto = 110, ancho = 78, marca, ...a}) => (
  <A {...a}>
    <rect x={-ancho / 2} y={-alto} width={ancho} height={alto} rx={8} fill="#F1F3F7" />
    <rect x={-ancho / 2} y={-alto * 0.72} width={ancho} height={alto * 0.4} fill={`url(#g-${color})`} />
    <rect x={-ancho / 2 + 10} y={-alto + 12} width={ancho * 0.5} height={7} rx={3.5} fill="#C5CBD7" />
    <rect x={-ancho / 2} y={-10} width={ancho} height={10} rx={4} fill="#C5CBD7" />
    {marca && (
      <text x={0} y={-alto * 0.47} textAnchor="middle" style={{font: `${ancho * 0.17}px 'M Black'`}} fill="#fff">
        {marca}
      </text>
    )}
  </A>
);

/** Carro de la compra. Ruedas en (x, y). */
export const Carro: React.FC<AP & {color?: string; lleno?: number}> = ({color = '#E8ECF2', lleno = 0, ...a}) => (
  <A {...a}>
    {lleno > 0 && (
      <g opacity={c01(lleno)}>
        <rect x={-34} y={-104} width={30} height={40} rx={5} fill="url(#g-ambar)" />
        <rect x={0} y={-112} width={28} height={48} rx={5} fill="url(#g-rosa)" />
        <rect x={30} y={-98} width={24} height={34} rx={5} fill="url(#g-cian)" />
      </g>
    )}
    <path d="M-78,-118 L-56,-118 L-44,-34 L52,-34" fill="none" stroke={color} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" />
    <path d="M-52,-88 L72,-88 L58,-44 L-46,-44 Z" fill="none" stroke={color} strokeWidth={8} strokeLinejoin="round" />
    <path d="M-18,-88 L-14,-44 M16,-88 L16,-44 M46,-88 L40,-44 M-50,-66 L64,-66" stroke={color} strokeWidth={5} />
    <circle cx={-34} cy={-12} r={12} fill={color} />
    <circle cx={44} cy={-12} r={12} fill={color} />
  </A>
);

/** Casa. Base en (x, y). */
export const Casa: React.FC<AP & {color?: Col; apagada?: number}> = ({color = 'verde', apagada = 0, ...a}) => (
  <A {...a}>
    <path d="M-52,0 L-52,-58 L0,-104 L52,-58 L52,0 Z" fill={`url(#g-${color})`} />
    <path d="M-52,0 L-52,-58 L0,-104 L52,-58 L52,0 Z" fill="#3A4050" opacity={apagada} />
    <path d="M-66,-52 L0,-112 L66,-52" fill="none" stroke={apagada > 0.5 ? '#5C6375' : '#fff'} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" opacity={0.9} />
    <rect x={-13} y={-44} width={26} height={44} rx={4} fill="#141B2A" opacity={0.75} />
  </A>
);

export const Marca: React.FC<AP & {tipo: 'si' | 'no'; t: number; grosor?: number; color?: string}> = ({tipo, t, grosor = 16, color, ...a}) => {
  const u = sal(t / 9);
  const c = color ?? (tipo === 'si' ? PAL.verde[0] : PAL.rojo[0]);
  return t < 0 ? null : (
    <A {...a}>
      {tipo === 'si' ? (
        <path d="M-42,2 L-12,34 L46,-36" fill="none" stroke={c} strokeWidth={grosor} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={150} strokeDashoffset={150 * (1 - u)} />
      ) : (
        <g stroke={c} strokeWidth={grosor} strokeLinecap="round">
          <path d="M-36,-36 L36,36" strokeDasharray={104} strokeDashoffset={104 * (1 - c01(u * 2))} />
          <path d="M36,-36 L-36,36" strokeDasharray={104} strokeDashoffset={104 * (1 - c01(u * 2 - 1))} />
        </g>
      )}
    </A>
  );
};

/** Recuadro de trazos, para agrupar actores. Esquina superior izquierda en (x, y). */
export const Recuadro: React.FC<{x: number; y: number; w: number; h: number; t: number; color?: string; relleno?: string; r?: number}> = ({x, y, w, h, t, color = 'rgba(255,255,255,0.75)', relleno = 'rgba(255,255,255,0.05)', r = 22}) =>
  t < 0 ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: r, border: `4px dashed ${color}`, background: relleno, opacity: c01(t / 5), transform: `scale(${0.8 + 0.2 * rebote(t / 11, 1.4)})`}} />
  );

/** Flecha curva de trazos que se dibuja de (x0,y0) a (x1,y1). `u` 0..1. */
export const Flecha: React.FC<{x0: number; y0: number; x1: number; y1: number; u: number; curva?: number; color?: string; grosor?: number; trazos?: boolean}> = ({x0, y0, x1, y1, u, curva = -0.25, color = '#fff', grosor = 8, trazos = true}) => {
  if (u <= 0) return null;
  const mx = (x0 + x1) / 2 + (y1 - y0) * curva;
  const my = (y0 + y1) / 2 - (x1 - x0) * curva;
  const q = (a: number, b: number, c: number, v: number) => (1 - v) * (1 - v) * a + 2 * (1 - v) * v * b + v * v * c;
  const v = c01(u);
  // punto y direccion en el extremo actual
  const px = q(x0, mx, x1, v);
  const py = q(y0, my, y1, v);
  const dx = 2 * (1 - v) * (mx - x0) + 2 * v * (x1 - mx);
  const dy = 2 * (1 - v) * (my - y0) + 2 * v * (y1 - my);
  const ang = (Math.atan2(dy, dx) * 180) / Math.PI;
  const n = 40;
  const pts = Array.from({length: Math.max(2, Math.round(n * v) + 1)}, (_, i) => {
    const w = Math.min(v, i / n);
    return `${q(x0, mx, x1, w).toFixed(1)},${q(y0, my, y1, w).toFixed(1)}`;
  });
  return (
    <svg width={1} height={1} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <polyline points={pts.join(' ')} fill="none" stroke={color} strokeWidth={grosor} strokeLinecap="round" strokeDasharray={trazos ? `${grosor * 2.2} ${grosor * 2}` : undefined} />
      <path d={`M${-grosor * 2.6},${-grosor * 2} L${grosor * 1.2},0 L${-grosor * 2.6},${grosor * 2} Z`} fill={color} transform={`translate(${px} ${py}) rotate(${ang})`} />
    </svg>
  );
};

/** Barra horizontal que crece. Esquina izquierda en (x, y). */
export const Barra: React.FC<{x: number; y: number; w: number; h?: number; u: number; color?: Col}> = ({x, y, w, h = 44, u, color = 'verde'}) => (
  <div style={{position: 'absolute', left: x, top: y - h / 2, width: Math.max(0, w * c01(u)), height: h, borderRadius: h / 2, background: grad(color, 90), boxShadow: '0 8px 22px rgba(0,0,0,0.35)'}} />
);

// ---------------------------------------------------------------- mapa
export const MAPA_W = 1000;
export const MAPA_H = 967;
export type EstiloPais = {fill?: string; op?: number; borde?: string};
/**
 * Europa. (x, y) es la esquina del mapa en el mundo y `k` su escala (el mapa
 * mide 1000 x 967 a k = 1). `estilo(cod)` colorea cada pais.
 */
export const Mapa: React.FC<{x: number; y: number; k: number; estilo?: (cod: string) => EstiloPais | undefined; base?: string; borde?: string}> = ({x, y, k, estilo, base = '#1A1D26', borde = '#2C3140'}) => (
  <svg width={MAPA_W * k} height={MAPA_H * k} viewBox={`0 0 ${MAPA_W} ${MAPA_H}`} style={{position: 'absolute', left: x, top: y, overflow: 'visible'}}>
    {Object.keys(EUROPA).map((cod) => {
      const e = estilo?.(cod);
      return <path key={cod} d={EUROPA[cod].d} fill={base} stroke={borde} strokeWidth={1.1 / k} strokeLinejoin="round" />;
    })}
    {Object.keys(EUROPA).map((cod) => {
      const e = estilo?.(cod);
      if (!e || !e.fill || (e.op ?? 1) <= 0) return null;
      return <path key={'c' + cod} d={EUROPA[cod].d} fill={e.fill} opacity={e.op ?? 1} stroke={e.borde ?? borde} strokeWidth={1.1 / k} strokeLinejoin="round" />;
    })}
  </svg>
);
/** Punto del mapa -> coordenadas de mundo. */
export const geo = (p: [number, number], x: number, y: number, k: number): [number, number] => [x + p[0] * k, y + p[1] * k];
export const centro = (cod: string, x: number, y: number, k: number) => geo(EUROPA[cod].c, x, y, k);
