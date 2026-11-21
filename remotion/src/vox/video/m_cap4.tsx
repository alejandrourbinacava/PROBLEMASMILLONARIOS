import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {A, Almacen, Camion, Chip, Cifra, Col, Escenario, Eti, Flecha, Hoja, Mapa, Marca, Moneda, Mundo, PAL, Sans, Sello, Serif, T, Tienda, c01, camara, centro, io, lerp, mini, pop, rebote, rnd, sal, tr} from './kit';
import {Sujeto, med} from './m_capas';
import {Im} from './m_vox';

import {MK, MX, MY} from './m_gancho';

/** Rejilla de tiendas diminutas. `tt(k)` da los fotogramas desde que aparece la k; `color(k)` su color. */
export const Rejilla: React.FC<{x: number; y: number; n: number; cols: number; paso?: number; s?: number; tt: (k: number) => number; color: (k: number) => string}> = ({x, y, n, cols, paso = 34, s = 1.2, tt, color}) => (
  <svg width={cols * paso} height={Math.ceil(n / cols) * paso * 0.8} style={{position: 'absolute', left: x, top: y, overflow: 'visible'}}>
    {Array.from({length: n}, (_, k) => {
      const e = pop(tt(k), 8, 2.2);
      return e <= 0 ? null : mini((k % cols) * paso + paso / 2, Math.floor(k / cols) * paso * 0.8 + paso * 0.4, s * e, color(k), '#EEF1F6', k);
    })}
  </svg>
);

/** 322-326 s · antes lo intentaron los mas grandes del mundo. Y varios volvieron a casa. */
export const Vuelven: React.FC<EP> = ({t, p}) => {
  const G: [string, Col, string][] = [['Walmart', 'azul', '#FFC83D'], ['Tesco', 'azul', '#fff'], ['Carrefour', 'azul', '#fff'], ['Dia', 'rojo', '#fff']];
  void G[0][1];
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={150} op={tr(t, 0, 8)}>
        <Serif tam={80} peso={600}>Los más grandes del mundo <span style={{color: '#FFD95A'}}>ya lo intentaron</span></Serif>
      </T>
      {G.map(([n, c, tinta], i) => {
        const x = 330 + i * 420;
        const ida = io(tr(t, 10 + i * 5, 20));
        const vuelta = io(tr(p(1), i * 4, 22));
        return (
          <React.Fragment key={n}>
            <Tienda x={x} y={960} s={0.66 * pop(t - 4 - i * 4, 11, 1.6)} nombre={n.toUpperCase()} cierre={io(tr(p(1), i * 4 + 16, 12))} />
            <Flecha x0={x - 50} y0={700} x1={x - 50} y1={400} u={ida} curva={0} grosor={9} color="#F4F5F7" />
            <Flecha x0={x + 50} y0={400} x1={x + 50} y1={700} u={vuelta} curva={0} grosor={9} color={PAL.rojo[0]} />
          </React.Fragment>
        );
      })}
      <T x={960} y={300} s={pop(p(1) - 10, 12, 1.5)}>
        <Chip tam={60} color="rojo">Y varios volvieron a casa</Chip>
      </T>
    </AbsoluteFill>
  );
};

const deu = centro('DEU', MX, MY, MK);
/** 327-335 s · Walmart entra en Alemania con sus precios bajos... y el precio bajo ya era de Aldi y de Lidl. */
export const WalmartEntra: React.FC<EP> = ({t, p, dur, ctx}) => {
  const cam = camara(t, [
    [0, 900, 560, 1.5],
    [30, 1010, 530, 2.5],
    [dur, 1020, 530, 2.7],
  ]);
  const cae = 1 - rebote(tr(t, 16, 14), 1.1);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'DEU' ? {fill: '#2B3348', borde: '#8D93A1'} : undefined)} />
      </Mundo>
      <T x={110} y={150} ancla="i" s={pop(t, 11, 1.4)}>
        <Chip tam={72} color="azul" tinta="#FFC83D">Walmart</Chip>
      </T>
      <T x={116} y={270} ancla="i" op={tr(t, 6, 8)}>
        <Sans tam={42} peso={600} color="#C9CED8">la mayor cadena del planeta</Sans>
      </T>
      <T x={116} y={380} ancla="i" op={tr(t, 14, 8)}>
        <Serif tam={90} peso={600}>entra en <span style={{color: '#FFD95A'}}>Alemania</span></Serif>
      </T>
      <Sujeto src={med(ctx, 'c_walmart')} x={1210} y={560 - cae * 700} ancho={860} t={t - 14} de="pop" />
      <T x={1210} y={270} s={pop(p(1), 11, 1.7)} rot={-4}>
        <Chip tam={52} color="ambar" tinta="#1B1D22">«Precios bajos»</Chip>
      </T>
      <Sujeto src={med(ctx, 'c_aldi')} x={830} y={910} alto={310} t={p(2)} de="pop" />
      <Sujeto src={med(ctx, 'c_lidl')} x={1560} y={910} ancho={560} t={p(3)} de="pop" />
      <T x={830} y={960} s={pop(p(2) - 8, 11, 1.6)}>
        <Chip tam={36} color="humo">precio bajo</Chip>
      </T>
      <T x={1600} y={960} s={pop(p(3) - 8, 11, 1.6)}>
        <Chip tam={36} color="humo">precio bajo</Chip>
      </T>
      <Sello x={430} y={640} t={p(3) + 8} tam={72} rot={-6}>Ya tenía dueño</Sello>
    </AbsoluteFill>
  );
};

/** 336-345 s · casi diez anos sin ganar; en 2006 vende sus 85 tiendas y asume ~800 M EUR. */
export const WalmartSale: React.FC<EP> = ({t, p}) => (
  <AbsoluteFill>
    <Escenario />
    <T x={110} y={110} ancla="i" s={pop(t, 11, 1.4)}>
      <Chip tam={52} color="azul" tinta="#FFC83D">Walmart en Alemania</Chip>
    </T>
    {Array.from({length: 9}, (_, k) => (
      <React.Fragment key={k}>
        <Hoja x={220 + k * 185} y={300} anio={`año ${k + 1}`} s={0.78 * pop(t - 6 - k * 2.5, 10, 1.7)} color="rojo" tam={40} />
        <T x={220 + k * 185} y={420} s={pop(t - 16 - k * 2.5, 9, 1.8)}>
          <span style={{font: "36px 'M Black'", color: PAL.rojo[0]}}>▼</span>
        </T>
      </React.Fragment>
    ))}
    <T x={960} y={500} op={tr(t, 30, 8)}>
      <Sans tam={48} peso={700}>Casi diez años sin ganar dinero</Sans>
    </T>
    <Hoja x={210} y={760} anio="2006" s={1.1 * pop(p(1), 12, 1.4)} color="humo" />
    <Rejilla x={360} y={640} n={85} cols={17} paso={46} s={1.7} tt={(k) => p(1) - 2 - k * 0.35} color={(k) => (p(1) - 30 - k * 0.3 >= 0 ? '#5C6375' : PAL.azul[0])} />
    <T x={750} y={860} ancla="c" op={tr(p(1), 8, 8)}>
      <Sans tam={44} peso={700}>85 tiendas</Sans>
    </T>
    <Sello x={750} y={730} t={p(1) + 34} tam={84} rot={-7}>Vendidas</Sello>
    <T x={1540} y={720} s={pop(p(2), 12, 1.5)}>
      <Cifra tam={140} color="rojo">≈ 800 M€</Cifra>
    </T>
    <T x={1540} y={840} op={tr(p(2), 8, 8)}>
      <Sans tam={44} peso={700}>de golpe</Sans>
    </T>
    <T x={1540} y={910} op={tr(p(3), -6, 8)}>
      <Sans tam={30} peso={500} color="#C9CED8">unos 1.000 millones de dólares de entonces</Sans>
    </T>
  </AbsoluteFill>
);

/** 345-357 s · Tesco en EE. UU.: seis anos sin un solo ano de beneficios. Carrefour vende China en 2019. */
export const Tesco: React.FC<EP> = ({t, p, ctx}) => {
  const b = p(4);
  const a = 1 - tr(b, -3, 6);
  return (
    <AbsoluteFill>
      <Escenario />
      {a > 0 && (
        <div style={{position: 'absolute', inset: 0, opacity: a}}>
          <T x={110} y={120} ancla="i" s={pop(t, 11, 1.4)}>
            <Chip tam={72} color="azul" tinta="#FF8A7D">Tesco</Chip>
          </T>
          <T x={420} y={124} ancla="i" op={tr(t, 6, 8)}>
            <Sans tam={42} peso={600} color="#C9CED8">el gigante británico</Sans>
          </T>
          <T x={300} y={330} s={pop(t - 8, 11, 1.4)}>
            <Chip tam={50} color="humo">Reino Unido</Chip>
          </T>
          <Flecha x0={520} y0={330} x1={880} y1={330} u={io(tr(t, 14, 20))} curva={-0.18} grosor={9} />
          <T x={1130} y={330} s={pop(t - 28, 11, 1.4)}>
            <Chip tam={50} color="humo">Estados Unidos</Chip>
          </T>
          <Sujeto src={med(ctx, 'c_fresh')} x={1640} y={470} ancho={430} t={t - 34} de="pop" gris={tr(p(3), 6, 10)} />
          <T x={1640} y={520} op={tr(t, 40, 8)}>
            <Eti tam={24} color="#C9CED8">una cadena nueva, desde cero</Eti>
          </T>
          {Array.from({length: 6}, (_, k) => (
            <React.Fragment key={k}>
              <Hoja x={260 + k * 215} y={740} anio={`año ${k + 1}`} s={0.95 * pop(p(1) - k * 3, 10, 1.7)} color={p(2) - k * 3 >= 0 ? 'rojo' : 'humo'} tam={42} />
              <Marca tipo="no" x={260 + k * 215} y={752} t={p(2) - k * 3} s={1.2} grosor={12} />
            </React.Fragment>
          ))}
          <T x={800} y={930} op={tr(p(2), 6, 8)}>
            <Sans tam={50} peso={700}>Ni un solo año de beneficios</Sans>
          </T>
          <Sello x={1640} y={350} t={p(3) + 4} tam={84} rot={-7}>Vendida</Sello>
        </div>
      )}
      {b >= 0 && (
        <>
          <T x={110} y={130} ancla="i" s={pop(b, 11, 1.4)}>
            <Chip tam={72} color="azul">Carrefour</Chip>
          </T>
          <Hoja x={330} y={480} anio="2019" s={1.5 * pop(b - 4, 12, 1.4)} color="rojo" />
          <T x={560} y={420} ancla="i" op={tr(b, 6, 8)}>
            <Serif tam={120} peso={600}>China</Serif>
          </T>
          <T x={566} y={540} ancla="i" op={tr(b, 12, 8)}>
            <Sans tam={40} peso={600} color="#C9CED8">vende la mayoría de su negocio</Sans>
          </T>
          <Tienda x={1500} y={820} s={1.15 * pop(b - 6, 12, 1.5)} color="azul" nombre="CARREFOUR" cierre={io(tr(b, 22, 18))} />
          <Sello x={1560} y={900} t={b + 30} tam={90} rot={-7}>Vendido</Sello>
        </>
      )}
    </AbsoluteFill>
  );
};

const fra = centro('FRA', MX, MY, MK);
const prt = centro('PRT', MX, MY, MK);
const espC = centro('ESP', MX, MY, MK);
/** 358-369 s · Dia, repartida por medio mundo: vende Francia (2014), sale de China (2018) y vende Portugal (2023). */
export const Dia: React.FC<EP> = ({t, p, dur}) => {
  const cam = camara(t, [
    [0, 760, 850, 2.6],
    [p(1) < 0 ? 40 : t - p(1), 770, 850, 2.6],
    [(p(1) < 0 ? 40 : t - p(1)) + 24, 830, 740, 1.7],
    [dur, 840, 736, 1.78],
  ]);
  const sx = (q: [number, number]) => 960 + (q[0] - cam.x) * cam.z;
  const sy = (q: [number, number]) => 540 + (q[1] - cam.y) * cam.z;
  const ROJO = '#C4161C';
  const GR = '#3A3F4B';
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa
          x={MX}
          y={MY}
          k={MK}
          estilo={(c) =>
            c === 'ESP' ? {fill: ROJO, borde: '#FF6A5C'} : c === 'FRA' ? (p(2) >= 6 ? {fill: GR} : {fill: ROJO, op: tr(p(1), 4, 10), borde: '#FF6A5C'}) : c === 'PRT' ? (p(4) >= 6 ? {fill: GR} : {fill: ROJO, op: tr(p(1), 0, 10), borde: '#FF6A5C'}) : undefined
          }
        />
      </Mundo>
      <T x={110} y={130} ancla="i" s={pop(t, 11, 1.4)}>
        <Chip tam={84} color="rojo">Dia</Chip>
      </T>
      <T x={320} y={104} ancla="i" op={tr(t, 6, 8)}>
        <Eti tam={28} color="#C9CED8">el ejemplo más cercano</Eti>
      </T>
      <T x={316} y={168} ancla="i" op={tr(p(1), 0, 8)}>
        <Serif tam={72} peso={600}>repartida por medio mundo</Serif>
      </T>
      {/* China queda fuera del mapa: una ficha */}
      <div style={{position: 'absolute', left: 1500, top: 300, width: 330, height: 300, borderRadius: 30, background: p(3) >= 6 ? GR : ROJO, border: '4px solid rgba(255,255,255,0.25)', opacity: tr(p(1), 8, 8), transform: `scale(${pop(p(1) - 8, 12, 1.4)})`}} />
      <T x={1665} y={370} op={tr(p(1), 12, 8)}>
        <Serif tam={76} peso={600}>China</Serif>
      </T>
      <Tienda x={1665} y={570} s={0.6 * pop(p(1) - 14, 11, 1.6)} color={p(3) >= 6 ? 'humo' : 'rojo'} nombre="DIA" cierre={io(tr(p(3), 6, 14))} />
      <Sello x={sx(fra) + 20} y={sy(fra) + 10} t={p(2)} tam={50} rot={-6}>2014 · vendida</Sello>
      <Sello x={1665} y={660} t={p(3)} tam={50} rot={5}>2018 · se va</Sello>
      <Sello x={sx(prt) - 60} y={sy(prt) + 40} t={p(4)} tam={50} rot={-5}>2023 · venta</Sello>
      <T x={sx(espC) + 10} y={sy(espC)} op={tr(p(4), 16, 8)}>
        <Chip tam={40} fondo="#F4F5F7" tinta="#0B0C10">solo en casa</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 369-373 s · el patron se repite: un supermercado es un negocio de centimos. */
export const Centimos: React.FC<EP> = ({t, p}) => {
  const u = io(tr(p(1), 2, 20));
  const ang = 0.041 * 2 * Math.PI;
  const R = 300;
  const x1 = Math.sin(ang) * R;
  const y1 = -Math.cos(ang) * R;
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={120} op={tr(t, 0, 8) * (1 - tr(p(1), -3, 6))}>
        <Serif tam={110} peso={600}>El patrón se repite.</Serif>
      </T>
      <T x={960} y={120} op={tr(p(1), 2, 8)}>
        <Serif tam={82} peso={600}>Un supermercado es un negocio de <span style={{color: '#FFD95A'}}>céntimos</span></Serif>
      </T>
      <Moneda x={520} y={620} s={6 * pop(t - 4, 14, 1.4)} cara="1 €" />
      <A x={520} y={620} s={pop(t - 4, 14, 1.4)}>
        <g transform={`translate(${u * 26} ${-u * 70})`} opacity={c01(p(1) / 4)}>
          <path d={`M0,0 L0,${-R} A${R},${R} 0 0 1 ${x1},${y1} Z`} fill={PAL.verde[0]} stroke="#0B0C10" strokeWidth={5} />
        </g>
      </A>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d="M590,280 L950,400" stroke="#fff" strokeWidth={4} strokeDasharray={360} strokeDashoffset={360 * (1 - tr(p(1), 18, 10))} opacity={0.8} />
      </svg>
      <T x={970} y={420} ancla="i" s={pop(p(1) - 22, 12, 1.5)}>
        <Cifra tam={130}>4 céntimos</Cifra>
      </T>
      <T x={978} y={540} ancla="i" op={tr(p(1), 30, 8)}>
        <Sans tam={46} peso={600} color="#C9CED8">le quedan a Mercadona de cada euro</Sans>
      </T>
      <T x={978} y={610} ancla="i" op={tr(p(1), 34, 8)}>
        <Sans tam={36} peso={500} color="#8D93A1">(4,1 € de cada 100 que vende)</Sans>
      </T>
    </AbsoluteFill>
  );
};

/** 373-380 s · funciona cuando eres muy grande en un sitio: compras mas barato, llenas camiones, repartes costes. */
export const Grande: React.FC<EP> = ({t, p}) => {
  const X = [340, 960, 1580];
  const carga = Math.min(8, Math.max(0, Math.floor((p(2) - 4) / 2.2)));
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={140} op={tr(t, 0, 8)}>
        <Serif tam={104} peso={600}>Funciona si eres <span style={{color: '#FFD95A'}}>muy grande en un sitio</span></Serif>
      </T>
      {[1, 2].map((i) => (
        <div key={i} style={{position: 'absolute', left: (X[i - 1] + X[i]) / 2, top: 300, width: 2, height: 640, background: 'rgba(255,255,255,0.08)'}} />
      ))}
      {/* 1: el precio baja */}
      <A x={X[0]} y={560} s={1.5 * pop(p(1), 12, 1.6)} rot={-10 + 8 * Math.sin(Math.max(0, p(1)) / 8) * Math.exp(-Math.max(0, p(1)) / 30)}>
        <path d="M-110,-60 L60,-60 L130,0 L60,60 L-110,60 Z" fill="url(#g-ambar)" />
        <circle cx={78} cy={0} r={13} fill="#0B0C10" />
        <text x={-34} y={20} textAnchor="middle" style={{font: "58px 'M Black'"}} fill="#1B1D22">
          − €
        </text>
      </A>
      <T x={X[0]} y={860} op={tr(p(1), 6, 8)}>
        <Sans tam={54} peso={800}>Compras más barato</Sans>
      </T>
      {/* 2: el camion va lleno */}
      <Camion x={X[1] + 30} y={640} s={0.82 * pop(p(2), 12, 1.4)} />
      {[0, 1, 2].map((k) => (
        <Im key={k} src="g_pale" x={X[1] - 190 + k * 120} y={720 + (k % 2) * 14} w={150} t={p(2) - 6 - k * 5} de="pop" />
      ))}
      <T x={X[1]} y={860} op={tr(p(2), 6, 8)}>
        <Sans tam={54} peso={800}>Llenas los camiones</Sans>
      </T>
      {/* 3: un almacen para muchas tiendas */}
      <Almacen x={X[2]} y={520} s={0.5 * pop(p(3), 12, 1.5)} />
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        {[0, 1, 2, 3].map((k) => (
          <path key={k} d={`M${X[2]},530 L${X[2] - 195 + k * 130},680`} stroke={PAL.verde[0]} strokeWidth={4} strokeDasharray="10 9" opacity={tr(p(3), 8 + k * 2, 6)} />
        ))}
      </svg>
      {[0, 1, 2, 3].map((k) => (
        <Tienda key={k} x={X[2] - 195 + k * 130} y={750} s={0.24 * pop(p(3) - 10 - k * 2, 9, 2)} />
      ))}
      <T x={X[2]} y={860} op={tr(p(3), 6, 8)}>
        <Sans tam={54} peso={800}>Repartes los costes</Sans>
      </T>
    </AbsoluteFill>
  );
};

/** 380-383 s · ser pequeno en diez paises no vale lo que ser enorme en uno. */
export const Balanza: React.FC<EP> = ({t, p}) => {
  const incl = 9 * rebote(tr(p(1), 0, 22), 1.4);
  return (
    <AbsoluteFill>
      <Escenario />
      <div style={{position: 'absolute', left: 960, top: 650, width: 0, height: 0, transform: `rotate(${incl}deg)`}}>
        <div style={{position: 'absolute', left: -760, top: -8, width: 1520, height: 16, borderRadius: 8, background: '#8D93A1'}} />
        {/* izquierda: diez paises, una tienda en cada uno */}
        <div style={{position: 'absolute', left: -700, top: -250, width: 560, height: 240, transform: `rotate(${-incl}deg)`, transformOrigin: '50% 100%'}}>
          {Array.from({length: 10}, (_, k) => (
            <div key={k} style={{position: 'absolute', left: (k % 5) * 112, top: Math.floor(k / 5) * 118, width: 100, height: 100, borderRadius: 50, border: '3px dashed rgba(255,255,255,0.45)', transform: `scale(${pop(t - 4 - k * 1.5, 9, 1.8)})`}}>
              <svg width={100} height={100}>{mini(50, 52, 2.2, PAL.rosa[0], '#EEF1F6')}</svg>
            </div>
          ))}
        </div>
        {/* derecha: un pais lleno */}
        <div style={{position: 'absolute', left: 150, top: -470, width: 520, height: 460, transform: `rotate(${-incl}deg)`, transformOrigin: '50% 100%'}}>
          <div style={{position: 'absolute', left: 30, top: 0, width: 460, height: 460, borderRadius: 230, border: `5px solid ${PAL.verde[0]}`, background: 'rgba(43,227,138,0.08)', transform: `scale(${pop(p(1) - 2, 12, 1.4)})`}} />
          <svg width={520} height={460} style={{position: 'absolute', overflow: 'visible'}}>
            {Array.from({length: 61}, (_, k) => {
              const a = k * 2.399963;
              const r = 23.5 * Math.sqrt(k + 0.5);
              return mini(260 + Math.cos(a) * r, 232 + Math.sin(a) * r, 1.9 * pop(p(1) - 6 - k * 0.3, 8, 2.2), PAL.verde[0], '#EEF1F6', k);
            })}
          </svg>
        </div>
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d="M960,650 L880,960 L1040,960 Z" fill="#5C6375" />
      </svg>
      <T x={480} y={150} op={tr(t, 0, 8)}>
        <Serif tam={84} peso={600}>Pequeño en diez países</Serif>
      </T>
      <T x={1440} y={150} op={tr(p(1), 0, 8)}>
        <Serif tam={84} peso={600} color="#FFD95A">Enorme en uno</Serif>
      </T>
    </AbsoluteFill>
  );
};

/** 384-390 s · Walmart, numero uno del mundo: en Alemania, 85 tiendas frente a rivales con cientos. */
export const Walmart85: React.FC<EP> = ({t, p}) => (
  <AbsoluteFill>
    <Escenario />
    <T x={130} y={130} ancla="i" s={pop(t, 11, 1.4)}>
      <Chip tam={64} color="azul" tinta="#FFC83D">Walmart</Chip>
    </T>
    <T x={520} y={134} ancla="i" op={tr(t, 6, 8) * (1 - tr(p(1), -3, 6))}>
      <Serif tam={80} peso={600}>la número uno del mundo</Serif>
    </T>
    <T x={520} y={134} ancla="i" op={tr(p(1), 2, 8)}>
      <Serif tam={80} peso={600}>en Alemania, <span style={{color: '#FFD95A'}}>una cadena más</span></Serif>
    </T>
    <T x={960} y={600} s={pop(t - 6, 13, 1.5)} op={1 - tr(p(2), -6, 8)}>
      <Cifra tam={330} color="ambar">N.º 1</Cifra>
    </T>
    <Rejilla x={130} y={330} n={85} cols={10} paso={48} s={1.8} tt={(k) => p(2) - k * 0.4} color={() => PAL.azul[0]} />
    <T x={370} y={760} s={pop(p(2), 12, 1.5)}>
      <Cifra tam={170} color="azul">85</Cifra>
    </T>
    <T x={370} y={880} op={tr(p(2), 6, 8)}>
      <Sans tam={44} peso={700}>tiendas de Walmart</Sans>
    </T>
    <Rejilla x={820} y={300} n={400} cols={25} paso={40} s={1.5} tt={(k) => p(3) - k * 0.09} color={() => PAL.rosa[0]} />
    <T x={1320} y={880} s={pop(p(3) - 6, 12, 1.5)}>
      <Cifra tam={150} color="rosa">≈ 400</Cifra>
    </T>
    <T x={1320} y={990} op={tr(p(3), 12, 8)}>
      <Sans tam={40} peso={700}>tiendas de Kaufland <span style={{color: '#8D93A1', fontWeight: 500}}>· Metro, unas 550</span></Sans>
    </T>
  </AbsoluteFill>
);

export const CAP4 = {vuelven: Vuelven, walmart_entra: WalmartEntra, walmart_sale: WalmartSale, tesco: Tesco, dia: Dia, centimos: Centimos, grande: Grande, balanza: Balanza, walmart85: Walmart85};
export {rnd, sal, lerp, deu};
