import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {Fuentes} from './fuentes';

/**
 * "El banco de verdad es una hoja de calculo." Linea 42 del guion del banco.
 *
 * Es la version en movimiento de la ilustracion A. Aqui no hay imagen: el
 * plano se dibuja en cada fotograma a partir de la geometria, asi que el
 * movimiento sale gratis. Las losas se apilan de una en una, el margen entra
 * el ultimo -es el remate de la frase- y la cifra cuenta hasta 3,22.
 *
 * El orden es el de la locucion, no el que quede bonito: primero lo que la
 * gente deposita, luego lo que el banco presta, y solo entonces el margen.
 */

// ---------------------------------------------------------------- paleta
const FONDO = '#0B1220';
const PAPEL = '#EDE7DA';
const TINTA = '#0B1220';
const FRIO = '#7A92B2';
const ROJO = '#E85640';
const AMBAR = '#FFB03C';
const HUMO = '#1B2436';

const W = 1920;
const H = 1080;
const CX = W / 2;
const CY = H / 2 + 60;
const COS30 = Math.cos(Math.PI / 6);
const SEN30 = 0.5;

// ------------------------------------------------------------ geometria
const iso = (x: number, y: number, z = 0): [number, number] => [
  CX + (x - y) * COS30,
  CY + (x + y) * SEN30 - z,
];

const sombra = (hex: string, f: number) => {
  const n = parseInt(hex.slice(1), 16);
  const c = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) =>
    Math.max(0, Math.min(255, Math.round(v * f)))
  );
  return `#${c.map((v) => v.toString(16).padStart(2, '0')).join('')}`;
};

const pts = (a: [number, number][]) =>
  a.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');

/** Un prisma en isometrico. Solo se dibujan las tres caras que se ven. */
const Bloque: React.FC<{
  x: number; y: number; hw: number; hd: number;
  z0: number; alto: number; color: string;
  grosor?: number; opacidad?: number;
}> = ({x, y, hw, hd, z0, alto, color, grosor = 3, opacidad = 1}) => {
  const a = x - hw, b = x + hw, c = y - hd, d = y + hd, z1 = z0 + alto;
  const comun = {stroke: TINTA, strokeWidth: grosor, strokeLinejoin: 'round' as const};
  return (
    <g opacity={opacidad}>
      <polygon {...comun} fill={sombra(color, 0.74)}
        points={pts([iso(b, c, z1), iso(b, d, z1), iso(b, d, z0), iso(b, c, z0)])} />
      <polygon {...comun} fill={sombra(color, 0.55)}
        points={pts([iso(a, d, z1), iso(b, d, z1), iso(b, d, z0), iso(a, d, z0)])} />
      <polygon {...comun} fill={color}
        points={pts([iso(a, c, z1), iso(b, c, z1), iso(b, d, z1), iso(a, d, z1)])} />
    </g>
  );
};

// ------------------------------------------------------------- rotulos
const Rotulo: React.FC<{
  x: number; y: number; txt: string; px: number; color: string;
  esp?: number; op?: number; dy?: number; ancla?: 'start' | 'middle' | 'end';
}> = ({x, y, txt, px, color, esp = 4, op = 1, dy = 0, ancla = 'middle'}) => (
  <text
    x={x} y={y + dy} fontSize={px} fill={color} opacity={op}
    textAnchor={ancla} letterSpacing={esp}
    fontFamily="'Archivo Black', Arial, sans-serif"
  >
    {txt}
  </text>
);

// -------------------------------------------------------------- guion
const D = 170;              // separacion de las dos columnas
const LOSA = 20;            // alto de cada losa
const HUECO = 7;
const N_DEP = 9;            // hay mas depositado que prestado. Siempre.
const N_PRE = 6;

const F_HOJA = 4;           // la hoja entra
const F_DEP = 26;           // empieza la pila de depositos
const F_PRE = 84;           // empieza la de prestamos
const PASO = 5;             // fotogramas entre losa y losa
const F_MARGEN = 126;       // entra la lamina del margen
const F_CIFRA = 138;        // arranca el contador
const DUR_CIFRA = 46;
const F_FRASE = 214;

export const HojaCalculo: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();

  const muelle = (desde: number, damping = 14) =>
    spring({frame: f - desde, fps, config: {damping, mass: 0.6}});

  // La hoja: entra de golpe y asienta. Nada de fundidos largos.
  const hoja = muelle(F_HOJA, 16);
  const opHoja = interpolate(f, [F_HOJA, F_HOJA + 10], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // Deriva de camara: muy poca, pero sin ella diez segundos se congelan.
  const deriva = interpolate(f, [0, 300], [1, 1.035]);
  const derivaY = interpolate(f, [0, 300], [0, -14]);

  // El contador. Es el argumento del video, asi que va en pantalla.
  const valor = interpolate(f, [F_CIFRA, F_CIFRA + DUR_CIFRA], [0, 3.22], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const cifra = `${valor.toFixed(2).replace('.', ',')} %`;
  // Un golpe seco al llegar al total, y vuelve. Con un muelle se quedaba
  // clavada en 1,09 para siempre: sube y no baja.
  const FIN_CIFRA = F_CIFRA + DUR_CIFRA;
  const escalaCifra = interpolate(
    f, [FIN_CIFRA - 1, FIN_CIFRA + 4, FIN_CIFRA + 17], [1, 1.11, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  // El margen. Entra deslizando desde delante y late una vez.
  const mMargen = muelle(F_MARGEN, 11);
  const latido = interpolate(
    f, [F_MARGEN + 14, F_MARGEN + 26, F_MARGEN + 44], [26, 46, 30],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  // La guia se dibuja de arriba abajo
  const guia = interpolate(f, [F_MARGEN + 10, F_MARGEN + 30], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  const losas = (n: number, x: number, y: number, desde: number, color: string) =>
    Array.from({length: n}, (_, i) => {
      const t = desde + i * PASO;
      const s = muelle(t, 13);
      if (f < t) return null;
      return (
        <Bloque key={`${x}_${i}`} x={x} y={y} hw={100} hd={100}
          z0={i * (LOSA + HUECO) + (1 - s) * 260}
          alto={LOSA} color={color} opacidad={Math.min(1, s * 2.2)} />
      );
    });

  const ix = CX - 2 * D * COS30;
  const dx = CX + 2 * D * COS30;
  const [mx, my] = iso(0, 0, 58);

  const entraRotulo = (desde: number) => {
    const s = muelle(desde, 15);
    return {op: Math.min(1, s * 1.6), dy: (1 - s) * 26};
  };
  const rDep = entraRotulo(F_DEP + N_DEP * PASO - 8);
  const rPre = entraRotulo(F_PRE + N_PRE * PASO - 8);
  const rFrase = entraRotulo(F_FRASE);

  return (
    <AbsoluteFill style={{backgroundColor: FONDO}}>
      <Fuentes />

      {/* ---------------------------------------------------- sonido */}
      <Sequence from={0}>
        <Audio src={staticFile('audio/ambiente.mp3')} volume={0.09} />
      </Sequence>
      <Sequence from={F_HOJA} durationInFrames={40}>
        <Audio src={staticFile('audio/shutter.wav')} volume={0.32} />
      </Sequence>
      {Array.from({length: N_DEP}, (_, i) => (
        <Sequence key={`sd${i}`} from={F_DEP + i * PASO} durationInFrames={26}>
          {/* la velocidad sube con la pila: suena como algo que se apila */}
          <Audio src={staticFile('audio/pop.wav')} volume={0.30}
            playbackRate={0.92 + i * 0.05} />
        </Sequence>
      ))}
      {Array.from({length: N_PRE}, (_, i) => (
        <Sequence key={`sp${i}`} from={F_PRE + i * PASO} durationInFrames={26}>
          <Audio src={staticFile('audio/pop.wav')} volume={0.30}
            playbackRate={0.86 + i * 0.05} />
        </Sequence>
      ))}
      <Sequence from={F_MARGEN - 4} durationInFrames={60}>
        <Audio src={staticFile('audio/whoosh.wav')} volume={0.42} />
      </Sequence>
      <Sequence from={F_CIFRA + DUR_CIFRA - 2} durationInFrames={60}>
        <Audio src={staticFile('audio/impact.wav')} volume={0.46} />
      </Sequence>

      {/* ---------------------------------------------------- imagen */}
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <defs>
          <filter id="brillo" x="-160%" y="-160%" width="420%" height="420%">
            <feGaussianBlur stdDeviation={latido} result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect width={W} height={H} fill={FONDO} />

        <g transform={`translate(${CX} ${CY + derivaY}) scale(${deriva}) translate(${-CX} ${-CY})`}>
          {/* rejilla: sigue siendo una hoja de calculo */}
          <g stroke={HUMO} strokeWidth={1.6} opacity={opHoja * 0.9}>
            {Array.from({length: 23}, (_, k) => {
              const i = k - 11;
              const [x0, y0] = iso(i * 40, -440);
              const [x1, y1] = iso(i * 40, 440);
              const [x2, y2] = iso(-440, i * 40);
              const [x3, y3] = iso(440, i * 40);
              return (
                <g key={`r${i}`}>
                  <line x1={x0} y1={y0} x2={x1} y2={y1} />
                  <line x1={x2} y1={y2} x2={x3} y2={y3} />
                </g>
              );
            })}
          </g>

          {/* la hoja */}
          <g opacity={opHoja}
            transform={`translate(${CX} ${CY}) scale(${0.9 + hoja * 0.1}) translate(${-CX} ${-CY}) translate(0 ${(1 - hoja) * 90})`}>
            <Bloque x={0} y={0} hw={330} hd={330} z0={-26} alto={26}
              color={PAPEL} grosor={3.5} />
          </g>

          {/* las dos columnas */}
          {losas(N_DEP, -D, D, F_DEP, FRIO)}
          {losas(N_PRE, D, -D, F_PRE, ROJO)}

          {/* el margen */}
          {f >= F_MARGEN ? (
            <g filter="url(#brillo)" opacity={Math.min(1, mMargen * 2)}
              transform={`translate(${(1 - mMargen) * 90} ${(1 - mMargen) * 52})`}>
              <Bloque x={0} y={0} hw={62} hd={5} z0={0} alto={58}
                color={AMBAR} grosor={2} />
            </g>
          ) : null}

          {/* guia del margen hacia la cifra */}
          <line x1={mx} y1={my - 16} x2={mx}
            y2={my - 16 - (my - 16 - 188) * guia}
            stroke={AMBAR} strokeWidth={2} opacity={0.55} />
        </g>

        {/* rotulos: fuera de la deriva, para que no floten */}
        <Rotulo x={ix} y={906} txt="DEPÓSITOS" px={34} color={FRIO}
          esp={6} op={rDep.op} dy={rDep.dy} />
        <Rotulo x={ix} y={946} txt="lo que la gente dejó" px={25}
          color={sombra(PAPEL, 0.62)} esp={0} op={rDep.op * 0.9} dy={rDep.dy} />
        <Rotulo x={dx} y={906} txt="PRÉSTAMOS" px={34} color={ROJO}
          esp={6} op={rPre.op} dy={rPre.dy} />
        <Rotulo x={dx} y={946} txt="lo que el banco prestó" px={25}
          color={sombra(PAPEL, 0.62)} esp={0} op={rPre.op * 0.9} dy={rPre.dy} />

        {f >= F_CIFRA ? (
          <>
            <g transform={`translate(${CX} 118) scale(${escalaCifra}) translate(${-CX} -118)`}>
              <Rotulo x={CX} y={118} txt={cifra} px={92} color={PAPEL} esp={1} />
            </g>
            <Rotulo x={CX} y={170} txt="EL MARGEN" px={30} color={AMBAR} esp={8} />
          </>
        ) : null}

        <Rotulo x={CX} y={1032}
          txt="El banco de verdad es una hoja de cálculo."
          px={36} color={sombra(PAPEL, 0.80)} esp={0}
          op={rFrase.op} dy={rFrase.dy} />
      </svg>
    </AbsoluteFill>
  );
};
