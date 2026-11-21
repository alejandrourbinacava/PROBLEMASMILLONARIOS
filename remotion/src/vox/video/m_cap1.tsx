import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {A, Almacen, Caja, Camion, Chip, Cifra, Col, Escenario, Eti, FONDO, Fajo, Flecha, GRIS, Hoja, Mapa, Marca, Mundo, PAL, Persona, Sans, Sello, Serif, T, Tienda, Tira, c01, camara, centro, geo, io, lerp, miles, pop, rebote, rnd, sal, tr} from './kit';
import {MK, MX, MY, Tiendas} from './m_gancho';
import {Im} from './m_vox';


const VERDE_PAIS = '#0F4A2D';
const GRIS_PAIS = '#3A3F4B';
const esp = centro('ESP', MX, MY, MK);
const ita = centro('ITA', MX, MY, MK);
const prt = centro('PRT', MX, MY, MK);

/** 42-50 s · 2013: el aterrizaje en Italia, muy avanzado... y aplazado. */
export const Italia: React.FC<EP> = ({t, p, dur}) => {
  const cam = camara(t, [
    [0, 960, 740, 1.7],
    [34, 990, 790, 2],
    [dur, 1004, 790, 2.1],
  ]);
  const apl = p(5);
  const uf = io(tr(p(1), -6, 24)) * (1 - tr(apl, 8, 10));
  const motivos = ['Come parecido', 'Está cerca', 'Un mercado enorme'];
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: VERDE_PAIS, borde: PAL.verde[1]} : c === 'ITA' ? (apl > 6 ? {fill: GRIS_PAIS} : {fill: '#F2A81D', op: tr(p(1), 12, 8), borde: '#FFD95A'}) : undefined)} />
        <Tiendas r={1.5} nPt={0} />
        <Flecha x0={esp[0] + 70} y0={esp[1] - 40} x1={ita[0] - 60} y1={ita[1] - 40} u={uf} curva={-0.22} grosor={4.5} />
      </Mundo>
      <T x={90} y={150} ancla="i" s={pop(t, 12, 1.3)}>
        <Serif tam={190} peso={600}>2013</Serif>
      </T>
      {motivos.map((m, i) => (
        <React.Fragment key={i}>
          <Marca tipo="si" x={124} y={356 + i * 112} t={p(i + 2) - 5} s={0.6} grosor={18} />
          <T x={182} y={356 + i * 112} ancla="i" s={pop(p(i + 2), 11, 1.4)}>
            <Chip tam={50} color="humo">{m}</Chip>
          </T>
        </React.Fragment>
      ))}
      <T x={1560} y={120} op={tr(p(1), 10, 8)}>
        <Serif tam={140} peso={600} color={apl > 6 ? GRIS : '#FFD95A'}>Italia</Serif>
      </T>
      <T x={1560} y={214} op={tr(p(1), 16, 8)}>
        <Eti tam={28} color="#C9CED8">el aterrizaje, muy avanzado</Eti>
      </T>
      <Sello x={1330} y={540} t={apl - 2} tam={104}>Aplazado</Sello>
    </AbsoluteFill>
  );
};

/** 56-71 s · 2016: el destino es Portugal. La nota de prensa: «cercano y proximo en lo logistico». */
export const PortugalElige: React.FC<EP> = ({t, p, dur}) => {
  const s = (k: number) => t - p(k);
  const cam = camara(t, [
    [0, 1004, 790, 2.1],
    [s(1), 996, 794, 2.12],
    [s(1) + 26, 690, 872, 3.1],
    [dur, 684, 880, 3.3],
  ]);
  const u2 = tr(p(2), -2, 8);
  const anillo = c01(p(2) / 26);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: VERDE_PAIS, borde: PAL.verde[1]} : c === 'ITA' ? {fill: GRIS_PAIS, op: 1 - tr(p(1), 0, 20)} : c === 'PRT' ? {fill: PAL.verde[0], op: u2, borde: '#B9FFD9'} : undefined)} />
        <Tiendas r={1.5} nPt={0} />
        {p(2) >= 0 && anillo < 1 && (
          <svg width={1} height={1} style={{position: 'absolute', overflow: 'visible'}}>
            <circle cx={prt[0]} cy={prt[1]} r={20 + anillo * 150} fill="none" stroke={PAL.verde[0]} strokeWidth={5 * (1 - anillo)} opacity={1 - anillo} />
          </svg>
        )}
      </Mundo>
      <T x={90} y={150} ancla="i" op={1 - tr(t, 2, 4)}>
        <Serif tam={190} peso={600}>2013</Serif>
      </T>
      <T x={90} y={150} ancla="i" s={pop(t - 5, 12, 1.5)}>
        <Serif tam={190} peso={600}>2016</Serif>
      </T>
      <T x={98} y={270} ancla="i" op={tr(t, 10, 8)}>
        <Eti tam={30} color="#C9CED8">tres años después</Eti>
      </T>
      <T x={98} y={440} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Serif tam={150} peso={600} color={PAL.verde[0]}>Portugal</Serif>
      </T>
      <T x={104} y={546} ancla="i" op={tr(p(2), 8, 8)}>
        <Eti tam={28} color="#C9CED8">el otro destino</Eti>
      </T>
      <T x={1010} y={640} op={tr(p(3), 4, 8)}>
        <Chip tam={30} color="humo">Nota de prensa de Mercadona · 23 de junio de 2016</Chip>
      </T>
      <Tira
        x={1010}
        y={820}
        t={p(3)}
        ancho={1620}
        tam={48}
        trozos={['«…por ser ', {m: 'un mercado cercano, próximo en lo logístico', en: p(3) - p(4)}, ' y que encaja con ', {m: 'el crecimiento orgánico y natural', en: p(3) - p(5)}, ' de la compañía»']}
      />
    </AbsoluteFill>
  );
};

/** 71-74 s · traducido: se puede llegar en camion desde los almacenes que ya tiene. */
export const CamionFrontera: React.FC<EP> = ({t, p, dur}) => {
  const x = lerp(720, 1150, io(tr(p(1), -4, 56)));
  const cam = camara(t, [
    [0, 920, 650, 1.2],
    [dur, 950, 650, 1.24],
  ]);
  const late = 1 + 0.05 * Math.sin(c01(p(2) / 14) * Math.PI);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <div style={{position: 'absolute', left: -400, top: 880, width: 2800, height: 8, background: '#30364A'}} />
        <svg width={1} height={1} style={{position: 'absolute', overflow: 'visible'}}>
          <path d="M-400,930 L2400,930" stroke="#30364A" strokeWidth={5} strokeDasharray="46 40" />
          <path d="M980,470 L980,880" stroke="#fff" strokeWidth={5} strokeDasharray="18 16" opacity={0.7} />
        </svg>
        <T x={980} y={436}>
          <Eti tam={28} color="#C9CED8">frontera</Eti>
        </T>
        <T x={480} y={590} op={tr(t, 2, 8)}>
          <Serif tam={84} peso={600}>España</Serif>
        </T>
        <T x={1500} y={510} op={tr(t, 6, 8)}>
          <Serif tam={84} peso={600} color={PAL.verde[0]}>Portugal</Serif>
        </T>
        <Almacen x={480} y={880} s={pop(t - 1, 12, 1.2) * late} nombre="BLOQUE LOGÍSTICO" />
        <Tienda x={1500} y={880} s={1.4 * pop(t - 5, 12, 1.2)} nombre="MERCADONA" />
        <Camion x={x} y={884} s={0.86} avance={x} nombre="MERCADONA" />
        <T x={480} y={960} op={tr(p(2), 0, 8)}>
          <Eti tam={28} color={PAL.verde[0]}>los almacenes que ya tiene</Eti>
        </T>
      </Mundo>
      <T x={960} y={84} s={pop(t, 11, 1.4)}>
        <Chip tam={36}>Traducido</Chip>
      </T>
      <T x={960} y={186} op={tr(p(1), -2, 8)}>
        <Serif tam={100} peso={600}>Se puede llegar <span style={{color: '#FFD95A'}}>en camión</span></Serif>
      </T>
    </AbsoluteFill>
  );
};

/** 75-82 s · el plan inicial: 4 supermercados, 25 M EUR, 200 empleos, apertura en 2019. */
export const PlanInicial: React.FC<EP> = ({t, p}) => {
  const X = [300, 740, 1180, 1620];
  const pie = (i: number, cifra: React.ReactNode, txt: string) => (
    <>
      <T x={X[i]} y={790} s={pop(p(i + 1), 12, 1.5)}>
        <Cifra tam={i === 1 ? 128 : 150}>{cifra}</Cifra>
      </T>
      <T x={X[i]} y={900} op={tr(p(i + 1), 6, 8)}>
        <Sans tam={40} peso={600} color="#C9CED8">{txt}</Sans>
      </T>
    </>
  );
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={128} op={tr(t, 0, 8)}>
        <Serif tam={96} peso={600}>El plan inicial era <span style={{color: '#FFD95A'}}>pequeño</span></Serif>
      </T>
      {[1, 2, 3].map((i) => (
        <div key={i} style={{position: 'absolute', left: (X[i - 1] + X[i]) / 2, top: 290, width: 2, height: 660, background: 'rgba(255,255,255,0.08)', opacity: tr(p(i + 1), -6, 8)}} />
      ))}
      {[0, 1, 2, 3].map((k) => (
        <Tienda key={k} x={X[0] + (k % 2 ? 105 : -105)} y={k < 2 ? 480 : 660} s={0.42 * pop(p(1) - k * 3, 11, 1.8)} />
      ))}
      {pie(0, '4', 'supermercados')}
      <Im src="g_fajo" x={X[1]} y={680} w={410} t={p(2)} de="pop" />
      {pie(1, '25 M€', 'de inversión')}
      <Im src="g_empleados" x={X[2]} y={690} w={420} t={p(3)} de="pop" />
      {pie(2, miles(Math.round(200 * sal(p(3) / 24))), 'empleos')}
      <Tienda x={X[3]} y={670} s={0.74 * pop(p(4), 12, 1.5)} nombre="MERCADONA" cierre={1 - io(tr(p(4), 12, 22))} />
      {pie(3, '2019', 'año de apertura')}
    </AbsoluteFill>
  );
};

/** 83-89 s · tres anos enteros entre decidir que vas y abrir la primera puerta. */
export const TresAnios: React.FC<EP> = ({t, p}) => {
  const u = io(tr(p(1), 0, 44));
  const x0 = 470;
  const x1 = 1450;
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={110} op={tr(t, 0, 8)}>
        <Eti tam={30}>Así trabaja esta empresa</Eti>
      </T>
      <div style={{position: 'absolute', left: x0, top: 476, width: x1 - x0, height: 8, borderRadius: 4, background: 'rgba(255,255,255,0.12)'}} />
      <div style={{position: 'absolute', left: x0, top: 476, width: (x1 - x0) * u, height: 8, borderRadius: 4, background: PAL.verde[0]}} />
      {[1, 2].map((i) => (
        <React.Fragment key={i}>
          <div style={{position: 'absolute', left: x0 + ((x1 - x0) * i) / 3 - 3, top: 462, width: 6, height: 36, borderRadius: 3, background: u > i / 3 ? PAL.verde[0] : 'rgba(255,255,255,0.2)'}} />
          <T x={x0 + ((x1 - x0) * i) / 3} y={536} op={0.4 + 0.6 * c01((u - i / 3) * 8)}>
            <Eti tam={28} color="#C9CED8">{2016 + i}</Eti>
          </T>
        </React.Fragment>
      ))}
      <Hoja x={330} y={480} anio="2016" s={1.35 * pop(t, 12, 1.4)} color="humo" />
      <T x={330} y={676} s={pop(t - 6, 11, 1.4)}>
        <Chip tam={38} color="humo">Decide ir</Chip>
      </T>
      <Hoja x={1590} y={480} anio="2019" s={1.35 * pop(p(1) - 38, 12, 1.6)} color="verde" />
      <T x={1590} y={676} s={pop(p(2), 11, 1.4)}>
        <Chip tam={38}>Abre la primera puerta</Chip>
      </T>
      <T x={960} y={300} s={pop(p(1) - 8, 12, 1.5)}>
        <Cifra tam={220} color="ambar">3 años</Cifra>
      </T>
      <Tienda x={960} y={1010} s={1.45 * pop(t - 4, 12, 1.2)} nombre="MERCADONA" cierre={1 - io(tr(p(2), 0, 20))} />
    </AbsoluteFill>
  );
};

/** 89-101 s · el centro de Matosinhos: mas de 2.000 sesiones; 6 de cada 10 productos, a cambiar. */
export const Pruebas: React.FC<EP> = ({t, p}) => {
  const COLS: Col[] = ['verde', 'ambar', 'cian', 'verde', 'lila', 'ambar', 'verde', 'cian', 'lila', 'verde'];
  const MAL = [1, 3, 4, 6, 8, 9];
  const fase1 = 1 - tr(p(2), 0, 8);
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={140} y={136} ancla="i" op={tr(t, 0, 8) * fase1}>
        <Eti tam={30} color={PAL.verde[0]}>Matosinhos · centro de pruebas</Eti>
      </T>
      <T x={136} y={226} ancla="i" op={tr(t, 3, 8) * fase1}>
        <Serif tam={76} peso={600}>Tres años probando productos</Serif>
      </T>
      <T x={136} y={316} ancla="i" op={tr(t, 6, 8) * fase1}>
        <Serif tam={76} peso={600}>con clientes portugueses</Serif>
      </T>
      <T x={1780} y={196} ancla="d" s={pop(p(1), 12, 1.4)} op={fase1}>
        <Cifra tam={170}>+{miles(Math.round(2000 * sal(p(1) / 40)))}</Cifra>
      </T>
      <T x={1772} y={316} ancla="d" op={tr(p(1), 8, 8) * fase1}>
        <Sans tam={42} peso={600} color="#C9CED8">sesiones con clientes</Sans>
      </T>
      <T x={136} y={190} ancla="i" s={pop(p(3), 12, 1.5)}>
        <Cifra tam={190} color="rojo">6 de cada 10</Cifra>
      </T>
      <T x={144} y={326} ancla="i" op={tr(p(4), 0, 8)}>
        <Sans tam={54} peso={700}>productos había que cambiarlos para Portugal</Sans>
      </T>
      <Im src="g_clientes" x={960} y={1120} w={860} t={t - 4} de="aba" />
      <div style={{position: 'absolute', left: 220, top: 820, width: 1480, height: 30, borderRadius: 15, background: '#4A5165'}} />
      <div style={{position: 'absolute', left: 320, top: 850, width: 26, height: 230, background: '#333949'}} />
      <div style={{position: 'absolute', left: 1574, top: 850, width: 26, height: 230, background: '#333949'}} />
      {COLS.map((c, i) => {
        const mal = MAL.indexOf(i);
        const u = mal >= 0 ? tr(p(3), 4 + mal * 3, 12) : 0;
        const giro = Math.abs(Math.cos(u * Math.PI));
        const x = 330 + i * 140;
        return (
          <React.Fragment key={i}>
            <div style={{position: 'absolute', left: x, top: 820, width: 0, height: 0, transform: `scaleX(${Math.max(0.04, giro)})`}}>
              <Caja x={0} y={0} s={pop(t - 6 - i * 2, 11, 1.6)} alto={160} ancho={104} color={u > 0.5 ? 'rojo' : c} />
            </div>
            {mal >= 0 && <Marca tipo="no" x={x} y={612} t={p(3) - 12 - mal * 3} s={0.62} grosor={16} />}
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

/** 101-115 s · marzo de 2019: tres o cuatro paises en la cabeza, «en mancha de aceite», y «empieza por I». */
export const Mancha: React.FC<EP> = ({t, p, dur}) => {
  const s = (k: number) => t - p(k);
  const cam = camara(t, [
    [0, 800, 876, 3],
    [s(1) - 4, 806, 874, 3.1],
    [s(1) + 26, 990, 690, 1.5],
    [dur, 1000, 680, 1.58],
  ]);
  const porto = geo([101, 772], MX, MY, MK);
  const m = io(tr(p(3), 0, 50));
  const oscuro = tr(p(4), -4, 10) * 0.74;
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: VERDE_PAIS, borde: PAL.verde[1]} : c === 'PRT' ? {fill: '#12683D', borde: PAL.verde[0]} : undefined)} />
        {/* la mancha de aceite: crece desde la peninsula hacia los vecinos */}
        {m > 0 && (
          <div style={{position: 'absolute', left: esp[0] - 620, top: esp[1] - 620, width: 1240, height: 1240, mixBlendMode: 'screen', opacity: 0.9}}>
            {[[0, 0, 1], [150, -120, 0.74], [60, -210, 0.6], [240, -40, 0.5]].map(([dx, dy, k], i) => {
              const r = (150 + 330 * m) * k;
              return <div key={i} style={{position: 'absolute', left: 620 + dx * m - r, top: 620 + dy * m - r, width: 2 * r, height: 2 * r, borderRadius: r, background: 'radial-gradient(circle, rgba(43,227,138,0.50) 0%, rgba(43,227,138,0.30) 55%, rgba(43,227,138,0) 72%)'}} />;
            })}
          </div>
        )}
        <Tiendas r={1.5} nPt={0} />
        <A x={porto[0]} y={porto[1]} s={0.2 * pop(t - 8, 12, 2.4)}>
          <path d="M0,0 C-40,-60 -70,-90 -70,-130 A70,70 0 1 1 70,-130 C70,-90 40,-60 0,0 Z" fill="#FFD95A" />
          <circle cx={0} cy={-130} r={30} fill="#1B1D22" />
        </A>
      </Mundo>
      <Hoja x={176} y={176} anio="2019" s={1.1 * pop(t, 12, 1.4)} color="ambar" op={1 - tr(p(4), -6, 6)} />
      <T x={300} y={146} ancla="i" op={tr(t, 4, 8) * (1 - tr(p(4), -6, 6))}>
        <Eti tam={30} color="#FFD95A">marzo · a punto de abrir en Portugal</Eti>
      </T>
      <T x={296} y={216} ancla="i" op={tr(p(1), 0, 8) * (1 - tr(p(4), -6, 6))}>
        <Serif tam={64} peso={600}>¿Y el siguiente país?</Serif>
      </T>
      {[0, 1, 2, 3].map((i) => (
        <T key={i} x={1250 + i * 150} y={176} s={pop(p(2) - i * 3, 11, 2)} rot={(i % 2 ? 1 : -1) * 4} op={(i === 3 ? 0.55 : 1) * (1 - tr(p(4), -6, 6))}>
          <Chip tam={84} color="ambar" tinta="#1B1D22">?</Chip>
        </T>
      ))}
      <T x={1475} y={296} op={tr(p(2), 10, 8) * (1 - tr(p(4), -6, 6))}>
        <Eti tam={28} color="#C9CED8">«tres o cuatro» en la cabeza</Eti>
      </T>
      <T x={1380} y={900} s={pop(p(3) - 6, 12, 1.4)} op={1 - tr(p(4), -4, 6)}>
        <Chip tam={56} fondo="#F4F5F7" tinta="#0B0C10">«En mancha de aceite»</Chip>
      </T>
      <AbsoluteFill style={{background: FONDO, opacity: oscuro}} />
      <T x={960} y={236} op={tr(p(4), 0, 8)}>
        <Eti tam={34} color="#C9CED8">El siguiente país</Eti>
      </T>
      <T x={960} y={500} s={pop(p(4) - 2, 14, 1.4)}>
        <span style={{font: "700 430px/1 'M Serif'", color: '#FFD95A', letterSpacing: -10}}>«I…»</span>
      </T>
      <Tira x={960} y={850} t={p(5)} ancho={1180} tam={62} rot={-2} trozos={[{m: '«El año que viene te lo digo»', en: 16}]} color="rgba(255,217,90,0.75)" />
      <T x={960} y={990} op={tr(p(5), 10, 8)}>
        <Eti tam={26}>Juan Roig · 12 de marzo de 2019</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** 115-123 s · no lo dijo al ano siguiente, ni al otro: siete anos. Algo paso en Portugal. */
export const SieteAnios: React.FC<EP> = ({t, p}) => {
  const X = (i: number) => 190 + i * 220;
  const tacha = (i: number) => (i === 1 ? p(0) - 6 : i === 2 ? p(1) : i >= 3 && i <= 6 ? p(2) - (i - 3) * 3 : -1);
  if (p(4) >= 0) {
    const tt = p(4);
    const cam = camara(tt, [
      [0, 790, 880, 3.6],
      [60, 760, 890, 4.3],
    ]);
    return (
      <AbsoluteFill>
        <Escenario cam={cam} />
        <Mundo cam={cam}>
          <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0C2A1C', borde: PAL.verde[1]} : c === 'PRT' ? {fill: '#F2A81D', borde: '#FFD95A'} : undefined)} />
        </Mundo>
        <T x={900} y={500} ancla="i" op={tr(tt, 1, 6)}>
          <Serif tam={132} peso={600}>Algo pasó</Serif>
        </T>
        <T x={900} y={650} ancla="i" op={tr(tt, 5, 6)}>
          <Serif tam={132} peso={600}>en <span style={{color: '#FFD95A'}}>Portugal</span>.</Serif>
        </T>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill>
      <Escenario />
      {Array.from({length: 8}, (_, i) => {
        const tt = tacha(i);
        return (
          <React.Fragment key={i}>
            <Hoja x={X(i)} y={560} anio={String(2019 + i)} s={pop(t - i * 2, 11, 1.5) * (i === 7 ? 1 + 0.12 * Math.sin(c01(p(3) / 16) * Math.PI) : 1)} color={i === 0 ? 'ambar' : i === 7 && p(3) >= 0 ? 'rojo' : 'humo'} apagada={tt >= 4 ? 0.7 : 0} />
            <Marca tipo="no" x={X(i)} y={572} t={tt} s={1.5} grosor={12} />
          </React.Fragment>
        );
      })}
      <T x={X(0) + 40} y={730} s={pop(t - 4, 11, 1.4)}>
        <Chip tam={36} color="ambar" tinta="#1B1D22">«Empieza por I»</Chip>
      </T>
      <svg width={1920} height={1080} style={{position: 'absolute'}} fill="none" stroke="#fff" strokeWidth={5} strokeLinecap="round" opacity={0.8}>
        <path d={`M${X(0)},420 L${X(0)},390 L${X(7)},390 L${X(7)},420`} strokeDasharray={1700} strokeDashoffset={1700 * (1 - io(tr(p(2), 0, 22)))} />
      </svg>
      <T x={960} y={236} s={pop(p(2) - 6, 12, 1.5)}>
        <Cifra tam={210} color="ambar">7 años</Cifra>
      </T>
      <Sello x={1420} y={800} t={p(3) - 2} tam={78} rot={-5}>No hay tercer país</Sello>
    </AbsoluteFill>
  );
};

export const CAP1 = {italia: Italia, portugal_elige: PortugalElige, camion: CamionFrontera, plan_inicial: PlanInicial, tres_anios: TresAnios, pruebas: Pruebas, mancha: Mancha, siete_anios: SieteAnios};
