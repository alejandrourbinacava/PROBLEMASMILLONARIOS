import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {EP} from './base';
import {A, Almacen, Barra, Camion, Casa, Chip, Cifra, Escenario, Eti, Fabrica, Fajo, GRIS, Hoja, Mapa, Marca, Moneda, Mundo, PAL, Sans, Sello, Serif, T, Tienda, Tira, c01, camara, geo, io, miles, pop, rebote, rnd, sal, tr} from './kit';
import {FondoReal, Sujeto, med} from './m_capas';
import {Im} from './m_vox';

import {MK, MX, MY, PRT, PilaMonedas} from './m_gancho';

const PORTO = geo([101, 772], MX, MY, MK);

/** Foto real en una tarjeta limpia (esquinas redondas, borde blanco). Esquina superior izquierda en (x, y). */
export const Foto: React.FC<{src?: string; x: number; y: number; w: number; h: number; t: number; rot?: number; foco?: string}> = ({src, x, y, w, h, t, rot = 0, foco}) =>
  t < 0 || !src ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: 30, overflow: 'hidden', border: '9px solid #fff', boxShadow: '0 30px 70px rgba(0,0,0,0.55)', transform: `rotate(${rot}deg) scale(${0.6 + 0.4 * rebote(t / 12, 1.3)})`, opacity: c01(t / 4), background: '#111'}}>
      <Img src={staticFile('vox/media/' + src)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: foco, transform: `scale(${1.04 + 0.04 * c01(t / 120)})`}} />
    </div>
  );

/** Pin de mapa. La punta esta en (x, y). */
export const Pin: React.FC<{x: number; y: number; s?: number; color?: string}> = ({x, y, s = 1, color = '#FFD95A'}) => (
  <A x={x} y={y} s={s}>
    <path d="M0,0 C-40,-60 -70,-90 -70,-130 A70,70 0 1 1 70,-130 C70,-90 40,-60 0,0 Z" fill={color} />
    <circle cx={0} cy={-130} r={30} fill="#1B1D22" />
  </A>
);

/** 124-130 s · julio de 2019: la primera tienda, en Canidelo. Y la cuenta. */
export const Canidelo: React.FC<EP> = ({t, p, dur, ctx}) => {
  const cam = camara(t, [
    [0, 790, 872, 3.9],
    [dur, 782, 868, 4.5],
  ]);
  const cae = 1 - rebote(tr(t, 4, 12), 1.2);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0C2A1C', borde: PAL.verde[1]} : c === 'PRT' ? {fill: '#12683D', borde: PAL.verde[0]} : undefined)} />
        <Pin x={PORTO[0]} y={PORTO[1] - cae * 60} s={0.13 * c01(t / 4)} />
      </Mundo>
      <Hoja x={166} y={176} anio="2019" s={1.1 * pop(t, 12, 1.4)} color="verde" />
      <T x={290} y={140} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={30} color={PAL.verde[0]}>2 de julio</Eti>
      </T>
      <T x={286} y={214} ancla="i" op={tr(t, 6, 8)}>
        <Serif tam={72} peso={600}>Abre la primera tienda</Serif>
      </T>
      <Foto src={ctx?.medios?.[0]?.src} x={1010} y={250} w={760} h={450} t={p(1)} rot={2} />
      <T x={1250} y={762} s={pop(p(1) - 8, 11, 1.4)}>
        <Chip tam={36} color="humo">Canidelo · junto a Oporto</Chip>
      </T>
      <div style={{position: 'absolute', left: 1580, top: 790, width: 0, height: 0, transform: `rotate(-5deg) scale(${0.92 * pop(p(2), 12, 1.5)})`, opacity: c01(p(2) / 3)}}>
        <div style={{position: 'absolute', left: -230, top: -40, width: 460, background: '#FAFAF7', padding: '30px 34px 44px', boxShadow: '0 30px 70px rgba(0,0,0,0.6)', clipPath: 'polygon(0 0,100% 0,100% 94%,94% 100%,88% 94%,82% 100%,76% 94%,70% 100%,64% 94%,58% 100%,52% 94%,46% 100%,40% 94%,34% 100%,28% 94%,22% 100%,16% 94%,10% 100%,4% 94%,0 100%)'}}>
          <div style={{font: "800 30px 'D Sans'", letterSpacing: 4, color: '#1B1D22', textAlign: 'center', borderBottom: '3px dashed #9AA1AE', paddingBottom: 16, marginBottom: 14}}>LA CUENTA DE PORTUGAL</div>
          {['El plan', 'Al abrir', 'Hasta 2025'].map((x) => (
            <div key={x} style={{display: 'flex', justifyContent: 'space-between', font: "600 34px/1.7 'D Sans'", color: '#3A4050'}}>
              <span>{x}</span>
              <span style={{color: '#C4161C', fontWeight: 800}}>? M€</span>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Un fajo de 25 M EUR (foto de estudio). El centro de su base esta en (x, y). */
const Bloque: React.FC<{x: number; y: number; s?: number; lleno?: number; resalta?: number}> = ({x, y, s = 1, lleno = 1, resalta = 0}) =>
  s <= 0 ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0}}>
      <Img src={staticFile('vox/media/g_fajo.webp')} style={{position: 'absolute', width: 150, maxWidth: 'none', left: -75, transform: `translateY(-100%) scale(${s})`, transformOrigin: '50% 100%', clipPath: lleno < 1 ? `inset(${(1 - lleno) * 100}% 0 0 0)` : undefined, filter: `brightness(${1 + 0.25 * resalta}) drop-shadow(0 6px 8px rgba(0,0,0,0.5))`}} />
    </div>
  );

/** 131-144 s · la cuenta: 25 M EUR de plan, 60 al abrir, 1.230 a cierre de 2025. Casi 50 veces. */
export const Cuenta: React.FC<EP> = ({t, p, dur}) => {
  const s = (k: number) => t - p(k);
  const cam = camara(t, [
    [0, 330, 800, 2.1],
    [s(1) - 2, 330, 800, 2.16],
    [s(1) + 16, 440, 760, 1.75],
    [s(2) - 2, 440, 760, 1.8],
    [s(2) + 22, 960, 540, 1],
    [dur, 960, 540, 1.03],
  ]);
  const P = 74;
  const PX = 154;
  const SUELO = 940;
  const n = Math.max(0, Math.min(49, Math.floor((p(3) + 44) / 1.15)));
  const cifra = n >= 49 ? 1230 : Math.max(60, n * 25);
  const lat = (k: number) => 1 + 0.1 * Math.sin(c01((p(4) - 4 - k * 0.4) / 10) * Math.PI);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <div style={{position: 'absolute', left: -600, top: SUELO + 4, width: 3200, height: 6, background: '#30364A'}} />
        {/* el plan */}
        <Bloque x={250} y={SUELO} s={pop(t - 2, 12, 1.6)} resalta={tr(p(4), 0, 8)} />
        <T x={250} y={770} s={pop(t - 6, 12, 1.4)}>
          <Cifra tam={84}>25 M€</Cifra>
        </T>
        <T x={250} y={996} op={tr(t, 8, 8)}>
          <Eti tam={28} color="#C9CED8">el plan · 2016</Eti>
        </T>
        {/* al abrir */}
        {[0, 1, 2].map((k) => (
          <Bloque key={k} x={560} y={SUELO - k * P - (1 - rebote(tr(p(1), k * 4, 10), 0.9)) * 260} s={p(1) - k * 4 >= 0 ? 1 : 0} lleno={k === 2 ? 0.4 : 1} />
        ))}
        <T x={560} y={640} s={pop(p(1) - 12, 12, 1.4)}>
          <Cifra tam={84}>60 M€</Cifra>
        </T>
        <T x={560} y={996} op={tr(p(1), 8, 8)}>
          <Eti tam={28} color="#C9CED8">al abrir · 2019</Eti>
        </T>
        {/* a cierre de 2025 */}
        {Array.from({length: n}, (_, k) => {
          const c = k % 5;
          const r = Math.floor(k / 5);
          const tt = p(3) + 44 - k * 1.15;
          return <Bloque key={k} x={980 + c * PX} y={SUELO - r * P} s={pop(tt, 8, 2.2) * lat(k)} />;
        })}
        <T x={1278} y={116} s={pop(p(2) - 14, 12, 1.4)}>
          <Cifra tam={140} color={n >= 49 ? 'ambar' : 'verde'}>{miles(cifra)} M€</Cifra>
        </T>
        <T x={1278} y={996} op={tr(p(2), 16, 8)}>
          <Eti tam={28} color="#C9CED8">inversión acumulada a cierre de 2025</Eti>
        </T>
        <T x={470} y={300} s={pop(p(4), 13, 1.7)}>
          <Cifra tam={270} color="ambar">×49</Cifra>
        </T>
        <T x={470} y={450} op={tr(p(4), 8, 8)}>
          <Sans tam={44} peso={700}>el plan inicial</Sans>
        </T>
      </Mundo>
    </AbsoluteFill>
  );
};

/** 144-158 s · que ha ganado: perdio hasta 2022, en 2023 no perdio, en 2024 gano 7 M EUR. Ocho anos. */
export const Ganado: React.FC<EP> = ({t, p}) => {
  const X = (i: number) => 310 + i * 260;
  const fin = tr(p(5), -2, 8);
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={170} op={tr(t, 0, 8) * (1 - fin)}>
        <Serif tam={104} peso={600}>¿Y cuánto ha <span style={{color: '#FFD95A'}}>ganado</span> con eso?</Serif>
      </T>
      <T x={960} y={150} s={pop(p(5), 12, 1.5)}>
        <Cifra tam={190} color="ambar">8 años</Cifra>
      </T>
      <T x={960} y={280} op={tr(p(5), 8, 8)}>
        <Sans tam={44} peso={600} color="#C9CED8">después de tomar la decisión, para el primer beneficio</Sans>
      </T>
      {Array.from({length: 6}, (_, i) => {
        const pierde = i < 4;
        const tt = pierde ? p(2) - i * 4 : i === 4 ? p(3) : p(4);
        return (
          <React.Fragment key={i}>
            <Hoja x={X(i)} y={540} anio={String(2019 + i)} s={1.18 * pop(p(1) - i * 2, 11, 1.5)} color={tt < 0 ? 'humo' : pierde ? 'rojo' : i === 4 ? 'humo' : 'verde'} />
            <T x={X(i)} y={i === 5 ? 760 : 750} s={pop(tt, 11, 1.7)}>
              {pierde ? <Chip tam={42} color="rojo">▼ pierde</Chip> : i === 4 ? <Chip tam={42} color="humo">no pierde</Chip> : <Chip tam={70}>+7 M€</Chip>}
            </T>
          </React.Fragment>
        );
      })}
      <Moneda x={X(5) - 96} y={900} s={0.7 * pop(p(4) - 6, 11, 2)} />
      <Moneda x={X(5)} y={916} s={0.7 * pop(p(4) - 9, 11, 2)} />
      <Moneda x={X(5) + 96} y={900} s={0.7 * pop(p(4) - 12, 11, 2)} />
    </AbsoluteFill>
  );
};

/** 158-165 s · 2025: 69 tiendas, 2.092 M EUR de ventas y 26 M EUR de beneficio. */
export const Despega: React.FC<EP> = ({t, p, dur}) => {
  const cam = camara(t, [
    [0, 800, 892, 4.6],
    [dur, 804, 892, 5],
  ]);
  const fila = (i: number, y: number, cifra: React.ReactNode, pie: string, icono: React.ReactNode) => (
    <>
      {icono}
      <T x={1130} y={y} ancla="i" s={pop(p(i), 12, 1.4)}>
        <Cifra tam={150} color={i === 3 ? 'ambar' : 'verde'}>{cifra}</Cifra>
      </T>
      <T x={1140} y={y + 100} ancla="i" op={tr(p(i), 6, 8)}>
        <Sans tam={40} peso={600} color="#C9CED8">{pie}</Sans>
      </T>
    </>
  );
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0E1712', borde: '#1E3A2B'} : c === 'PRT' ? {fill: '#12683D', borde: PAL.verde[0]} : undefined)} />
        <svg width={1} height={1} style={{position: 'absolute', overflow: 'visible'}}>
          {PRT.slice(0, 69).map((q, i) => {
            const [x, y] = geo(q, MX, MY, MK);
            return <circle key={i} cx={x} cy={y} r={1.5 * pop(p(1) - i * 0.5, 8, 2.6)} fill="#B9FFD9" />;
          })}
        </svg>
      </Mundo>
      <Hoja x={166} y={176} anio="2025" s={1.1 * pop(t, 12, 1.4)} color="verde" />
      <T x={286} y={176} ancla="i" op={tr(t, 4, 8)}>
        <Serif tam={84} peso={600}>Portugal ya despega</Serif>
      </T>
      {fila(1, 330, miles(Math.round(69 * sal(p(1) / 26))), 'tiendas', <Tienda x={1030} y={410} s={0.56 * pop(p(1), 11, 1.6)} />)}
      {fila(2, 580, miles(Math.round(2092 * sal(p(2) / 30))) + ' M€', 'en ventas', <Fajo x={1030} y={590} s={1.25 * pop(p(2), 11, 1.6)} />)}
      {fila(3, 830, miles(Math.round(26 * sal(p(3) / 24))) + ' M€', 'de beneficio', <Moneda x={1030} y={836} s={1.2 * pop(p(3), 11, 1.6)} />)}
    </AbsoluteFill>
  );
};

/** 166-180 s · de cada 100 EUR que vende: al grupo le quedan 4,1; a Portugal, 1,2. */
export const Margen: React.FC<EP> = ({t, p}) => {
  const rejilla = (cx: number, t0: number, tRes: number, cuantas: number) => (
    <>
      {Array.from({length: 100}, (_, k) => {
        const c = k % 10;
        const r = Math.floor(k / 10);
        const e = pop(t0 - (c + r) * 0.9, 8, 2);
        if (e <= 0) return null;
        const mia = k < cuantas;
        const u = c01(tRes / 10);
        const sc = e * (mia && tRes >= 0 ? 1 + 0.45 * rebote(c01((tRes - k * 3) / 10), 2) : 1);
        return (
          <React.Fragment key={k}>
            {mia && tRes >= 0 && <div style={{position: 'absolute', left: cx - 250 + c * 50 + 25 - 27, top: 330 + r * 50 + 25 - 27, width: 54, height: 54, borderRadius: 27, background: PAL.verde[0], transform: `scale(${sc})`}} />}
            <Moneda x={cx - 250 + c * 50 + 25} y={330 + r * 50 + 25} s={0.43 * sc} gris={mia ? 0 : u} />
          </React.Fragment>
        );
      })}
    </>
  );
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={104} op={tr(t, 0, 8) * (1 - tr(p(1), -2, 6))}>
        <Serif tam={92} peso={600}>Suena bien.</Serif>
      </T>
      <T x={960} y={104} op={tr(p(1), 2, 8)}>
        <Serif tam={84} peso={600}>De cada <span style={{color: '#FFD95A'}}>100 €</span> que vende, ¿cuánto le queda?</Serif>
      </T>
      <T x={520} y={250} s={pop(p(2), 11, 1.4)}>
        <Chip tam={44}>Grupo Mercadona</Chip>
      </T>
      {rejilla(520, p(2) - 4, p(3), 4)}
      <T x={520} y={920} s={pop(p(3), 12, 1.5)}>
        <Cifra tam={170}>4,1 €</Cifra>
      </T>
      <T x={1400} y={250} s={pop(p(4), 11, 1.4)}>
        <Chip tam={44} color="ambar" tinta="#1B1D22">Portugal</Chip>
      </T>
      {rejilla(1400, p(4) - 4, p(5), 1)}
      <T x={1400} y={920} s={pop(p(5), 12, 1.5)}>
        <Cifra tam={170} color="ambar">1,2 €</Cifra>
      </T>
      <div style={{position: 'absolute', left: 959, top: 250, width: 2, height: 740, background: 'rgba(255,255,255,0.08)'}} />
      <T x={960} y={1020} op={tr(p(6), 0, 8)}>
        <Eti tam={24}>Cálculo propio con las cifras de la compañía</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** 180-188 s · y no es que las tiendas vayan mal: cada una vende mas que la media espanola. */
export const PorTienda: React.FC<EP> = ({t, p}) => {
  const lado = (x: number, k: number, pais: string, cifra: string, n: number, color: 'ambar' | 'verde') => (
    <>
      <T x={x - 80} y={372} op={tr(p(k), 0, 8)}>
        <Serif tam={78} peso={600} color={color === 'ambar' ? '#FFD95A' : '#F4F5F7'}>{pais}</Serif>
      </T>
      <Tienda x={x - 80} y={760} s={1.3 * pop(p(k), 12, 1.4)} nombre="MERCADONA" />
      <PilaMonedas x={x + 210} y={742} n={n * io(tr(p(k), 6, 28))} s={1.25} />
      <T x={x} y={880} s={pop(p(k) - 14, 12, 1.5)}>
        <Cifra tam={130} color={color}>{cifra}</Cifra>
      </T>
      <T x={x} y={980} op={tr(p(k), 20, 8)}>
        <Sans tam={36} peso={600} color="#C9CED8">por tienda y año, de media</Sans>
      </T>
    </>
  );
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={150} s={pop(t, 12, 1.4)}>
        <Chip tam={70} color="humo">¿Las tiendas van mal?</Chip>
      </T>
      <Marca tipo="no" x={960} y={150} t={p(1) - 2} s={2.2} grosor={10} />
      <Sello x={1500} y={262} t={p(1) + 4} tam={64} rot={-7} color={PAL.verde[0]}>Al contrario</Sello>
      <div style={{position: 'absolute', left: 120, top: 762, width: 1680, height: 6, background: '#30364A'}} />
      {lado(520, 2, 'Portugal', '≈ 30 M€', 12, 'ambar')}
      {lado(1380, 3, 'España', '≈ 25 M€', 10, 'verde')}
    </AbsoluteFill>
  );
};

/** 188-191 s · mas de la mitad de los hogares de Portugal ya ha comprado en Mercadona. */
export const Hogares: React.FC<EP> = ({t}) => (
  <AbsoluteFill>
    <Escenario />
    <T x={960} y={190} s={pop(t, 12, 1.4)}>
      <Cifra tam={220}>{miles(55.6 * sal(t / 40), 1)} %</Cifra>
    </T>
    {Array.from({length: 20}, (_, k) => {
      const c = k % 10;
      const r = Math.floor(k / 10);
      const on = k < 11 ? tr(t, 10 + k * 2.4, 6) : 0;
      return <Casa key={k} x={330 + c * 140} y={r ? 760 : 580} s={1.1 * pop(t - 2 - k * 0.8, 10, 1.8)} color="verde" apagada={1 - on} />;
    })}
    <T x={960} y={900} op={tr(t, 8, 8)}>
      <Sans tam={56} peso={700}>de los hogares de Portugal ya ha comprado en Mercadona</Sans>
    </T>
  </AbsoluteFill>
);

/** 191-197 s · 7,4 % de cuota en siete anos: mas que Lidl en Espana tras tres decadas. */
export const Cuota: React.FC<EP> = ({t, p}) => {
  const uM = io(tr(t, 6, 34));
  const uL = io(tr(p(2), 0, 60));
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={140} y={130} ancla="i" op={tr(t, 0, 8)}>
        <Eti tam={30}>Cuota de mercado</Eti>
      </T>
      <T x={140} y={270} ancla="i" s={pop(t, 11, 1.4)}>
        <Chip tam={48}>Mercadona en Portugal</Chip>
      </T>
      <Barra x={140} y={390} w={1150} h={84} u={uM} />
      <T x={140 + 1150 * uM + 30} y={390} ancla="i" s={pop(p(1), 12, 1.4)}>
        <Cifra tam={140}>{miles(7.4 * uM, 1)} %</Cifra>
      </T>
      <T x={144} y={490} ancla="i" op={tr(t, 24, 8)}>
        <Sans tam={46} peso={700} color="#FFD95A">en 7 años</Sans>
      </T>
      <T x={140} y={660} ancla="i" s={pop(p(2), 11, 1.4)}>
        <Chip tam={48} color="azul" tinta="#FFE600">Lidl en España</Chip>
      </T>
      <Barra x={140} y={780} w={1134} h={84} u={uL} color="azul" />
      <T x={140 + 1134 * uL + 30} y={780} ancla="i" s={pop(p(2) - 4, 12, 1.4)}>
        <Cifra tam={140} color="azul">{miles(7.3 * uL, 1)} %</Cifra>
      </T>
      <T x={144} y={880} ancla="i" op={tr(p(3), -4, 8)}>
        <Sans tam={46} peso={700} color="#FFD95A">después de tres décadas</Sans>
      </T>
    </AbsoluteFill>
  );
};

/** 198-201 s · el problema no esta en la tienda: esta en todo lo que hay detras. */
export const Detras: React.FC<EP> = ({t, p, dur}) => {
  const s = (k: number) => t - p(k);
  const cam = camara(t, [
    [0, 1420, 620, 1.5],
    [s(1) - 2, 1420, 620, 1.56],
    [s(1) + 30, 390, 560, 0.76],
    [dur, 380, 560, 0.78],
  ]);
  const cosas: [number, string][] = [[940, 'transporte'], [390, 'bloques logísticos'], [-170, 'fabricantes'], [-630, 'productores']];
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <div style={{position: 'absolute', left: -1600, top: 864, width: 4400, height: 8, background: '#30364A'}} />
        <svg width={1} height={1} style={{position: 'absolute', overflow: 'visible'}}>
          <path d="M-1100,930 L1300,930" stroke={PAL.verde[0]} strokeWidth={7} strokeDasharray="30 26" opacity={tr(p(1), 14, 10)} />
        </svg>
        <Fabrica x={-630} y={864} s={1.1} color="cian" t={t} />
        <Fabrica x={-170} y={864} s={1.25} t={t + 20} />
        <Almacen x={390} y={864} s={0.9} nombre="BLOQUE LOGÍSTICO" />
        <Camion x={940} y={868} s={0.84} nombre="MERCADONA" avance={t * 3} />
        <Tienda x={1420} y={864} s={1.55} nombre="MERCADONA" />
        {cosas.map(([x, n], i) => (
          <T key={n} x={x} y={1006} op={tr(p(1), 22 + i * 4, 8)}>
            <Eti tam={36} color="#C9CED8">{n}</Eti>
          </T>
        ))}
      </Mundo>
      <T x={960} y={120} op={tr(t, 0, 8) * (1 - tr(p(1), -2, 6))}>
        <Serif tam={90} peso={600}>El problema no está en la tienda.</Serif>
      </T>
      <T x={960} y={120} op={tr(p(1), 4, 8)}>
        <Serif tam={90} peso={600}>Está en <span style={{color: '#FFD95A'}}>todo lo que hay detrás</span>.</Serif>
      </T>
    </AbsoluteFill>
  );
};

/** 202-222 s · «cuesta mucho»: las cuatro cosas que hay que hacer en un pais nuevo. Y aun no estan hechas. */
export const Lista: React.FC<EP> = ({t, p, dur, ctx}) => {
  const intro = 1 - tr(p(1), -8, 8);
  const filas = ['Empezar una operación en un país', 'Corregir lo que no está bien hecho', 'Adaptar el surtido a los consumidores', 'Encontrar buenos proveedores de frescos'];
  const apaga = 0.45 * tr(p(5), 0, 8) * (1 - tr(p(7), 0, 8));
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={14} luz={0.26} />
      <Sujeto src={med(ctx, 'c_roig')} x={420} y={1110} alto={860} t={t - 3} de="aba" op={intro} />
      <T x={800} y={470} ancla="i" op={tr(t, 6, 8) * intro}>
        <Serif tam={88} peso={600}>La frase más importante</Serif>
      </T>
      <T x={800} y={585} ancla="i" op={tr(t, 10, 8) * intro}>
        <Serif tam={88} peso={600} color="#FFD95A">de todo el vídeo</Serif>
      </T>
      <T x={140} y={110} ancla="i" op={tr(t, 0, 8)}>
        <Eti tam={30} color={PAL.verde[0]}>Juan Roig · 10 de marzo de 2026</Eti>
      </T>
      <T x={132} y={212} ancla="i" op={tr(p(1), -4, 8)}>
        <Serif tam={110} peso={600}>«Cuesta mucho…»</Serif>
      </T>
      <div style={{position: 'absolute', inset: 0, opacity: 1 - apaga}}>
        {filas.map((f, i) => {
          const tt = p(i + 1);
          const y = 372 + i * 128;
          const pulso = 1 + 0.14 * Math.sin(c01((p(7) - 6 - i * 5) / 12) * Math.PI);
          return tt < 0 ? null : (
            <React.Fragment key={i}>
              <div style={{position: 'absolute', left: 130, top: y - 54, width: 1660, height: 108, borderRadius: 26, background: 'rgba(255,255,255,0.055)', opacity: c01(tt / 5), transform: `translateX(${(1 - sal(tt / 12)) * -80}px)`}} />
              <T x={196} y={y} s={pop(tt, 11, 1.7)}>
                <span style={{display: 'inline-block', width: 76, height: 76, borderRadius: 38, background: 'linear-gradient(180deg,#2BE38A,#0A9150)', font: "44px/80px 'M Black'", color: '#fff', textAlign: 'center'}}>{i + 1}</span>
              </T>
              <T x={270} y={y} ancla="i" op={tr(tt, 2, 8)}>
                <Sans tam={58} peso={700}>{f}</Sans>
              </T>
              <div style={{position: 'absolute', left: 1690 - 36, top: y - 36, width: 72, height: 72, borderRadius: 16, border: `6px solid ${p(7) >= 6 + i * 5 ? '#FFD95A' : 'rgba(255,255,255,0.5)'}`, opacity: tr(tt, 6, 8), transform: `scale(${pulso})`}} />
            </React.Fragment>
          );
        })}
      </div>
      <Tira x={960} y={958} t={p(5)} ancho={1640} tam={50} rot={-1} sale={p(5) - p(7)} trozos={['«', {m: 'Cuando todo eso esté hecho', en: p(5) - p(6) + 4}, ', ganaremos lo mismo que en España»']} color="rgba(255,217,90,0.8)" />
      <T x={540} y={940} s={pop(p(8), 12, 1.5)}>
        <Cifra tam={150} color="ambar">7 años</Cifra>
      </T>
      <T x={850} y={946} ancla="i" op={tr(p(8), 6, 8)}>
        <Sans tam={52} peso={700}>después de abrir</Sans>
      </T>
      <Sello x={1330} y={610} t={p(8) + 10} tam={110} rot={-8}>Todavía no</Sello>
    </AbsoluteFill>
  );
};

export const CAP2 = {canidelo: Canidelo, cuenta: Cuenta, ganado: Ganado, despega: Despega, margen: Margen, por_tienda: PorTienda, hogares: Hogares, cuota: Cuota, detras: Detras, lista: Lista};
export {GRIS, Fajo, rnd};
