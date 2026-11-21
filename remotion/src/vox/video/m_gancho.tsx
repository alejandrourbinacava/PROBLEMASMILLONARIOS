import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {EUROPA} from './europa';
import {A, Barra, Casa, Chip, Cifra, Escenario, Eti, FONDO, Fajo, Flecha, GRIS, Mapa, Marca, Moneda, Mundo, PAL, Persona, Carro, Sans, Serif, T, Tienda, c01, camara, centro, geo, io, kf, lerp, miles, mini, pop, rebote, rnd, sal, tr} from './kit';
import {PUNTOS} from './puntos';

// El mapa de Europa en el mundo: esquina y escala comunes a todas las escenas de mapa.
export const MX = 560;
export const MY = 8;
export const MK = 1.1;
export const ESP = PUNTOS.ESP;
export const PRT = PUNTOS.PRT;
export const LIDL = ['DEU', 'FRA', 'GBR', 'IRL', 'ESP', 'PRT', 'ITA', 'NLD', 'BEL', 'LUX', 'AUT', 'CHE', 'DNK', 'SWE', 'FIN', 'POL', 'CZE', 'SVK', 'HUN', 'SVN', 'HRV', 'ROU', 'BGR', 'GRC', 'CYP', 'MLT', 'LTU', 'LVA', 'EST', 'SRB'];
const VERDE_PAIS = '#0F4A2D';

/** Los puntos de las tiendas ya colocados en su sitio (para las escenas que parten del mapa montado). */
export const Tiendas: React.FC<{r?: number; op?: number; nPt?: number; color?: string}> = ({r = 1.3, op = 1, nPt = 69, color = PAL.verde[0]}) => (
  <svg width={1} height={1} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', opacity: op}}>
    {ESP.map((q, i) => {
      const [x, y] = geo(q, MX, MY, MK);
      return <circle key={i} cx={x} cy={y} r={r} fill={color} />;
    })}
    {PRT.slice(0, nPt).map((q, i) => {
      const [x, y] = geo(q, MX, MY, MK);
      return <circle key={'p' + i} cx={x} cy={y} r={r} fill={color} />;
    })}
  </svg>
);

/** Niebla: el suelo se pierde en el fondo. */
const Niebla: React.FC<{y?: number; alto?: number}> = ({y = 860, alto = 260}) => (
  <div style={{position: 'absolute', left: -3000, top: y, width: 12000, height: alto, background: `linear-gradient(180deg, rgba(11,12,16,0) 0%, ${FONDO} 88%)`}} />
);

/** 0-11 s · 41.858 M EUR en fajos, 1.672 tiendas en rejilla y 3 de cada 10 euros. */
export const Ventas: React.FC<EP> = ({t, p, dur}) => {
  const s = (k: number) => t - p(k);
  const cam = camara(t, [
    [0, 960, 556, 1],
    [s(2) - 3, 960, 540, 1.07],
    [s(2) + 15, 2880, 540, 1],
    [s(3) - 3, 2880, 540, 1.05],
    [s(3) + 15, 4800, 540, 1],
    [dur, 4800, 546, 1.05],
  ]);
  // --- A: el muro de fajos
  const fajos: React.ReactNode[] = [];
  for (let c = 0; c < 12; c++) {
    const alto = 5 + Math.floor(rnd(c * 3.3) * 3);
    for (let r = 0; r < alto; r++) {
      const tt = t - (3 + r * 5 + rnd(c * 7 + r) * 8);
      if (tt < 0) continue;
      const y = 1004 - r * 64;
      fajos.push(<Fajo key={c + '-' + r} x={960 + (c - 5.5) * 146 + (rnd(c + r * 9) - 0.5) * 10} y={y - (1 - rebote(tt / 10, 0.9)) * 460} rot={(rnd(c * 5 + r) - 0.5) * 5} s={1.08} tono={(c + r) % 2} />);
    }
  }
  const px = lerp(-260, 520, sal(tr(t, 4, 56)));
  const anda = t < 58;
  // --- B: una tienda por cada tienda
  const COLS = 44;
  const FILAS = 38;
  const rejilla: React.ReactNode[] = [];
  if (p(2) > -2 && p(3) < 30) {
    for (let r = 0; r < FILAS; r++)
      for (let c = 0; c < COLS; c++) {
        const tt = p(2) - 4 - (c * 0.62 + r * 0.5 + rnd(c * 13 + r) * 5);
        if (tt < 0) continue;
        rejilla.push(mini(c * 27 + 13, r * 21 + 11, pop(tt, 8, 2.4), PAL.verde[0], '#E9EDF3', c + '-' + r));
      }
  }
  // --- C: diez euros
  const monedas = Array.from({length: 10}, (_, i) => {
    const x0 = 4800 + (i - 4.5) * 176;
    const e = pop(p(3) - 8 - i * 2, 10);
    if (i < 3) {
      const u = io(tr(p(4), i * 4, 17));
      const x = lerp(x0, 4340, u);
      const y = lerp(430, 700, u) - Math.sin(u * Math.PI) * 150;
      return <Moneda key={i} x={x} y={y} s={e * lerp(1.55, 0.5, u)} op={1 - tr(p(4), i * 4 + 14, 4)} rot={u * 300} />;
    }
    return <Moneda key={i} x={x0} y={430} s={e * 1.55} gris={tr(p(4), 4, 10)} />;
  });
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        {/* A */}
        <T x={960} y={118} op={tr(t, 2, 8)}>
          <Serif tam={84}>2025</Serif>
        </T>
        <T x={960} y={290} s={0.85 + 0.15 * rebote(t / 14, 1.4)} op={tr(t, 0, 5)}>
          <Cifra tam={236}>{miles(Math.round(41858 * sal(t / 52)))}</Cifra>
          <Cifra tam={132}> M€</Cifra>
        </T>
        <T x={960} y={452} op={tr(p(1), 0, 8)}>
          <Eti tam={34} color="#C9CED8">Vendió Mercadona en un solo año</Eti>
        </T>
        {fajos}
        <Carro x={px + 150} y={1046} s={1.5} lleno={1} />
        <Persona x={px} y={1046} s={1.55} color="verde" fase={anda ? px / 34 : undefined} brazo={-62} />
        <Niebla y={900} alto={200} />
        {/* B */}
        <T x={2270} y={318} op={tr(p(2), 6, 8)}>
          <Eti tam={30}>Sus supermercados</Eti>
        </T>
        <T x={2270} y={452} s={pop(p(2) - 4, 12, 1.4)}>
          <Cifra tam={216}>{miles(Math.round(1672 * sal((p(2) - 4) / 44)))}</Cifra>
        </T>
        <T x={2270} y={606} op={tr(p(2), 10, 8)}>
          <Sans tam={62} peso={800}>tiendas</Sans>
        </T>
        <svg width={COLS * 27} height={FILAS * 21} style={{position: 'absolute', left: 2600, top: 141, overflow: 'visible'}}>
          {rejilla}
        </svg>
        {/* C */}
        <T x={4800} y={200} op={tr(p(3), 8, 8)}>
          <Sans tam={62} peso={700}>De cada 10 € que se gastan en la compra en España…</Sans>
        </T>
        <Tienda x={4340} y={1010} s={1.75 * pop(p(3) - 22, 12, 1.4)} nombre="MERCADONA" />
        {monedas}
        <T x={5130} y={660} op={tr(p(4), 16, 8)}>
          <Eti tam={36} color="#C9CED8">casi 3 pasan por sus cajas</Eti>
        </T>
        <T x={5130} y={810} s={pop(p(4) - 14, 12, 1.5)}>
          <Cifra tam={250}>28,5 %</Cifra>
        </T>
        <T x={5130} y={956} op={tr(p(4), 20, 8)}>
          <Sans tam={44} peso={500} color={GRIS}>de cuota de mercado</Sans>
        </T>
      </Mundo>
    </AbsoluteFill>
  );
};

/** 11-22 s · las 1.672 tiendas caen sobre el mapa: solo dos paises. Lidl enciende treinta. */
export const MapaDos: React.FC<EP> = ({t, p, dur}) => {
  const s = (k: number) => t - p(k);
  const cam = camara(t, [
    [0, 960, 540, 1],
    [6, 960, 540, 1],
    [36, 790, 852, 3],
    [s(4) - 12, 790, 852, 3.12],
    [s(4) + 10, 960, 540, 1],
    [dur, 960, 540, 1.03],
  ]);
  const orden = React.useMemo(() => {
    const o = EUROPA.DEU.c;
    return [...LIDL].sort((a, b) => Math.hypot(EUROPA[a].c[0] - o[0], EUROPA[a].c[1] - o[1]) - Math.hypot(EUROPA[b].c[0] - o[0], EUROPA[b].c[1] - o[1]));
  }, []);
  const tL = (cod: string) => p(5) + 8 - orden.indexOf(cod) * 1.55;
  const encendidos = orden.filter((c) => tL(c) >= 0).length;
  const r = 2.3 / Math.sqrt(cam.z);
  const punto = (q: [number, number], i: number) => {
    const [gx, gy] = geo(q, MX, MY, MK);
    const u = c01((t - 3 - rnd(i * 1.7) * 26) / 13);
    if (u <= 0) return null;
    const v = u * u;
    return <circle key={i} cx={gx + (1 - v) * (rnd(i + 0.3) - 0.5) * 160} cy={lerp(gy - 260 - rnd(i + 0.6) * 420, gy, v)} r={r * (u < 1 ? 1.5 : 1)} fill={PAL.verde[0]} />;
  };
  const hud = 1 - tr(p(4), -14, 8);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa
          x={MX}
          y={MY}
          k={MK}
          estilo={(cod) => {
            if (cod === 'ESP' || cod === 'PRT') return {fill: VERDE_PAIS, op: tr(t, 10, 14), borde: PAL.verde[1]};
            if (LIDL.includes(cod) && tL(cod) >= 0) return {fill: PAL.azul[1], op: 0.9 * tr(tL(cod), 0, 5), borde: '#5B84FF'};
            return undefined;
          }}
        />
        <svg width={1} height={1} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
          {ESP.map(punto)}
          {PRT.slice(0, 69).map((q, i) => punto(q, i + 2000))}
          {orden.map((cod) => {
            const tt = tL(cod);
            if (tt < 0) return null;
            const [x, y] = centro(cod, MX, MY, MK);
            return (
              <g key={cod} transform={`translate(${x} ${y}) scale(${pop(tt, 9, 2.6)})`}>
                <circle r={9} fill="#FFE600" stroke={PAL.azul[1]} strokeWidth={4} />
              </g>
            );
          })}
        </svg>
      </Mundo>
      {/* rotulos del acercamiento, en pantalla */}
      <AbsoluteFill style={{opacity: hud}}>
        <T x={960} y={128} s={pop(p(1), 12, 1.5)}>
          <Cifra tam={170} color="blanco">2 países</Cifra>
        </T>
        <svg width={1920} height={1080} style={{position: 'absolute'}} fill="none" stroke="#fff" strokeWidth={3} opacity={0.7}>
          <path d="M470,646 L560,660" strokeDasharray={100} strokeDashoffset={100 * (1 - tr(p(2), 9, 8))} />
          <path d="M1470,470 L1300,520" strokeDasharray={180} strokeDashoffset={180 * (1 - tr(p(2), 2, 8))} />
        </svg>
        <T x={1500} y={388} ancla="i" op={tr(p(2), 0, 6)}>
          <Serif tam={70}>España</Serif>
        </T>
        <T x={1492} y={500} ancla="i" s={pop(p(2), 12, 1.4)}>
          <Cifra tam={150}>1.603</Cifra>
        </T>
        <T x={1500} y={600} ancla="i" op={tr(p(2), 4, 6)}>
          <Eti tam={28} color="#C9CED8">tiendas</Eti>
        </T>
        <T x={452} y={560} ancla="d" op={tr(p(2), 7, 6)}>
          <Serif tam={70}>Portugal</Serif>
        </T>
        <T x={460} y={672} ancla="d" s={pop(p(2) - 7, 12, 1.4)}>
          <Cifra tam={150}>69</Cifra>
        </T>
        <T x={452} y={772} ancla="d" op={tr(p(2), 11, 6)}>
          <Eti tam={28} color="#C9CED8">tiendas</Eti>
        </T>
      </AbsoluteFill>
      {/* panel de la comparacion, en pantalla */}
      <T x={84} y={226} ancla="i" op={tr(p(4), 0, 8)}>
        <Eti tam={27}>Cuota de mercado en España</Eti>
      </T>
      <T x={84} y={306} ancla="i" s={pop(p(4) - 2, 11, 1.4)}>
        <Chip tam={40}>Mercadona</Chip>
      </T>
      <Barra x={84} y={386} w={330} u={io(tr(p(4), 4, 16))} />
      <T x={430} y={386} ancla="i" op={tr(p(4), 14, 6)}>
        <Sans tam={44} peso={800}>28,5 %</Sans>
      </T>
      <T x={84} y={496} ancla="i" s={pop(p(4) - 12, 11, 1.4)}>
        <Chip tam={40} color="azul" tinta="#FFE600">Lidl</Chip>
      </T>
      <Barra x={84} y={576} w={85} u={io(tr(p(4), 16, 12))} color="azul" />
      <T x={186} y={576} ancla="i" op={tr(p(4), 24, 6)}>
        <Sans tam={44} peso={800}>7,3 %</Sans>
      </T>
      <T x={84} y={716} ancla="i" op={tr(p(5), -4, 8)}>
        <Eti tam={27}>Países con tiendas</Eti>
      </T>
      <T x={76} y={846} ancla="i" s={pop(p(5) + 4, 11, 1.4)}>
        <Cifra tam={170}>2</Cifra>
      </T>
      <T x={250} y={846} ancla="i" s={pop(p(5), 11, 1.4)}>
        <Cifra tam={170} color="azul">{encendidos >= LIDL.length ? '+30' : String(encendidos)}</Cifra>
      </T>
      <T x={84} y={960} ancla="i" op={tr(p(5), 2, 8)}>
        <Sans tam={30} peso={600} color={PAL.verde[0]}>Mercadona</Sans>
      </T>
      <T x={258} y={960} ancla="i" op={tr(p(5), 2, 8)}>
        <Sans tam={30} peso={600} color="#7FA0FF">Lidl</Sans>
      </T>
    </AbsoluteFill>
  );
};

const PilaMonedas: React.FC<{x: number; y: number; n: number; s?: number}> = ({x, y, n, s = 1}) => (
  <A x={x} y={y} s={s}>
    {Array.from({length: Math.ceil(n)}, (_, i) => {
      const e = c01(n - i);
      return (
        <g key={i} transform={`translate(0 ${-i * 17 - (1 - sal(e)) * 60})`} opacity={e}>
          <ellipse cx={0} cy={6} rx={44} ry={13} fill="#B67806" />
          <rect x={-44} y={0} width={88} height={6} fill="#B67806" />
          <ellipse cx={0} cy={0} rx={44} ry={13} fill="url(#g-oro)" />
          <ellipse cx={0} cy={0} rx={30} ry={8} fill="none" stroke="#B67806" strokeWidth={2} opacity={0.5} />
        </g>
      );
    })}
  </A>
);
export {PilaMonedas};

/** 30-39 s · gana mas que nunca y se niega a salir. No es miedo ni dinero: ya lo intento una vez. */
export const Niega: React.FC<EP> = ({t, p, dur}) => {
  const s = (k: number) => t - p(k);
  const cam = camara(t, [
    [0, 930, 690, 1.62],
    [s(4) - 2, 950, 680, 1.74],
    [s(4) + 18, 760, 880, 3.6],
    [dur, 770, 880, 3.8],
  ]);
  const esp = centro('ESP', MX, MY, MK);
  const dest = ['FRA', 'ITA', 'DEU'].map((c) => centro(c, MX, MY, MK));
  const uf = kf(p(1), [[0, 0], [9, 0.72], [15, 0.72], [23, 0]]);
  const oscuro = kf(t, [[s(2) - 2, 0], [s(2) + 6, 0.62], [s(4) - 2, 0.62], [s(4) + 8, 0]]);
  const chips = 1 - tr(p(4), -2, 6);
  const pt = tr(p(4), 6, 10);
  const casa = 1 - tr(p(4), 0, 8);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa
          x={MX}
          y={MY}
          k={MK}
          estilo={(cod) => (cod === 'ESP' ? {fill: pt > 0.5 ? '#0C2A1C' : VERDE_PAIS, borde: PAL.verde[1]} : cod === 'PRT' ? {fill: pt > 0 ? '#F2A81D' : VERDE_PAIS, borde: pt > 0 ? '#FFD95A' : PAL.verde[1]} : undefined)}
        />
        <Tiendas r={1.5} op={1 - pt * 0.72} />
        {dest.map((d, i) => (
          <Flecha key={i} x0={esp[0] + 20} y0={esp[1] - 20} x1={d[0]} y1={d[1]} u={uf} curva={i === 1 ? 0.12 : -0.14} grosor={5} color="#fff" />
        ))}
        {dest.map((d, i) => {
          const tt = p(1) - 9;
          const x = lerp(esp[0] + 20, d[0], 0.74);
          const y = lerp(esp[1] - 20, d[1], 0.74);
          return <Marca key={'x' + i} tipo="no" x={x} y={y - (i === 1 ? -14 : 22)} t={tt - i * 2} s={0.5 * (1 - tr(p(1), 30, 6))} grosor={14} />;
        })}
        <PilaMonedas x={esp[0] - 44} y={esp[1] + 8} n={c01(t / 4) + 7 * io(tr(t, 4, 30))} s={0.62 * casa} />
        <A x={esp[0] + 16} y={esp[1] - 16} s={pop(t - 12, 12, 2) * 0.9 * casa}>
          <path d="M0,34 L0,-22 M-20,-4 L0,-26 L20,-4" fill="none" stroke={PAL.verde[0]} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" />
        </A>
        <Casa x={esp[0] + 78} y={esp[1] + 36} s={0.62 * pop(p(1) - 24, 12, 2) * casa} />
      </Mundo>
      <AbsoluteFill style={{background: FONDO, opacity: oscuro}} />
      <AbsoluteFill style={{opacity: chips}}>
        <T x={590} y={500} s={pop(p(2), 11, 1.5)} rot={-3}>
          <Chip tam={104} color="humo">¿Miedo?</Chip>
        </T>
        <Marca tipo="no" x={590} y={500} t={p(2) - 12} s={2.6} grosor={11} />
        <T x={1310} y={560} s={pop(p(3), 11, 1.5)} rot={2}>
          <Chip tam={104} color="humo">¿Dinero?</Chip>
        </T>
        <Marca tipo="no" x={1310} y={560} t={p(3) - 14} s={2.6} grosor={11} />
      </AbsoluteFill>
      <T x={860} y={300} ancla="i" op={tr(p(4), 16, 8)}>
        <Eti tam={32} color="#FFD95A">Portugal</Eti>
      </T>
      <T x={856} y={410} ancla="i" op={tr(p(4), 12, 8)}>
        <Serif tam={100} peso={600}>Ya lo intentó una vez.</Serif>
      </T>
      <T x={1290} y={680} s={pop(p(5), 12, 1.6)} rot={-5 + Math.sin(Math.max(0, p(5)) / 9) * 2.5 * Math.exp(-Math.max(0, p(5)) / 40)}>
        <Chip tam={84} color="ambar" tinta="#1B1D22">¿Cuánto le costó?</Chip>
      </T>
    </AbsoluteFill>
  );
};

export const GANCHO = {ventas: Ventas, mapa_dos: MapaDos, niega: Niega};
// usados por otras escenas
export {Fajo, Moneda, Tienda};
