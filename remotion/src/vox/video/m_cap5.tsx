import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {EUROPA} from './europa';
import {A, Barra, Chip, Cifra, Escenario, Eti, Fajo, Flecha, Hoja, Mapa, Marca, Mundo, PAL, Persona, Sans, Sello, Serif, T, Tienda, c01, camara, centro, io, lerp, miles, mini, pop, rebote, rnd, sal, tr} from './kit';
import {Detras, FondoReal, Sujeto, med} from './m_capas';
import {MK, MX, MY, PilaMonedas, Tiendas} from './m_gancho';

/** 402-411 s · las que cotizan necesitan crecer cada trimestre; cuando su pais no da mas, solo queda salir. */
export const Bolsa: React.FC<EP> = ({t, p, dur, ctx}) => {
  const H = [150, 210, 270, 330];
  const techo = tr(p(3), 0, 10);
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={10} luz={0.42} />
      <T x={960} y={110} op={tr(t, 0, 8)}>
        <Serif tam={84} peso={600}>Muchas <span style={{color: '#FFD95A'}}>no tienen elección</span></Serif>
      </T>
      <Detras x={640} y={400} t={p(1) - 4} tam={360}>Bolsa</Detras>
      <Sujeto src={med(ctx, 'c_bolsa')} x={640} y={1130} ancho={1180} t={p(1)} de="aba" />
      {/* cada trimestre, mas */}
      {H.map((h, i) => {
        const u = io(tr(p(2), -10 + i * 7, 14));
        const tope = techo > 0 && i === 3;
        return (
          <React.Fragment key={i}>
            <div style={{position: 'absolute', left: 1310 + i * 130, top: 880 - h * u, width: 96, height: h * u, borderRadius: 14, background: tope ? 'linear-gradient(180deg,#FF6A5C,#C4161C)' : 'linear-gradient(180deg,#2BE38A,#0A9150)', boxShadow: '0 12px 30px rgba(0,0,0,0.4)'}} />
            <T x={1358 + i * 130} y={926} op={tr(p(2), -10 + i * 7, 8)}>
              <Eti tam={28} color="#fff">T{i + 1}</Eti>
            </T>
          </React.Fragment>
        );
      })}
      <T x={1550} y={410} s={pop(p(2), 11, 1.5)}>
        <Chip tam={44}>Crecer cada trimestre</Chip>
      </T>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d="M1280,540 L1830,540" stroke="#FF6A5C" strokeWidth={7} strokeDasharray="22 16" opacity={techo} />
      </svg>
      <T x={1556} y={496} op={techo}>
        <Eti tam={28} color="#FF8A7D">tu país ya no da más</Eti>
      </T>
      <Flecha x0={1760} y0={600} x1={1880} y1={300} u={io(tr(p(4), 0, 18))} curva={0.2} grosor={11} color="#FFD95A" trazos={false} />
      <T x={1640} y={250} s={pop(p(4) - 10, 11, 1.6)}>
        <Chip tam={56} color="ambar" tinta="#1B1D22">Salir fuera</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 411-414 s · Mercadona no tiene ese problema. Por dos motivos. */
export const DosMotivos: React.FC<EP> = ({t, p, dur, ctx}) => (
  <AbsoluteFill>
    <FondoReal ctx={ctx} t={t} dur={dur} blur={12} luz={0.45} />
    <Sujeto src={med(ctx, 'c_logo')} x={440} y={900} alto={640} t={t - 2} de="pop" />
    <T x={860} y={360} ancla="i" op={tr(t, 4, 8)}>
      <Serif tam={110} peso={600}>Mercadona no tiene</Serif>
    </T>
    <T x={860} y={490} ancla="i" op={tr(t, 8, 8)}>
      <Serif tam={110} peso={600}>ese problema.</Serif>
    </T>
    {[1, 2].map((n) => (
      <T key={n} x={920 + (n - 1) * 190} y={720} s={pop(p(1) - (n - 1) * 6, 12, 1.8)}>
        <span style={{display: 'inline-block', width: 150, height: 150, borderRadius: 75, background: 'linear-gradient(180deg,#FFD95A,#F29A0B)', font: "96px/156px 'M Black'", color: '#1B1D22', textAlign: 'center', boxShadow: '0 16px 40px rgba(0,0,0,0.45)'}}>{n}</span>
      </T>
    ))}
    <T x={1260} y={724} ancla="i" op={tr(p(1), 10, 8)}>
      <Sans tam={64} peso={800}>motivos</Sans>
    </T>
  </AbsoluteFill>
);

/** 414-429 s · primero: no cotiza. Es familiar: Roig y Hortensia Herrero tienen la mayoria. Nadie le mete prisa. */
export const Familiar: React.FC<EP> = ({t, p, dur, ctx}) => {
  const u = io(tr(p(3), -4, 30));
  const C = 2 * Math.PI * 150;
  const b = tr(p(4), -3, 8);
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={12} luz={0.4} />
      <T x={120} y={120} ancla="i" s={pop(t, 12, 1.6)}>
        <span style={{display: 'inline-block', width: 110, height: 110, borderRadius: 55, background: 'linear-gradient(180deg,#FFD95A,#F29A0B)', font: "70px/114px 'M Black'", color: '#1B1D22', textAlign: 'center'}}>1</span>
      </T>
      <T x={270} y={122} ancla="i" op={tr(t, 4, 8)}>
        <Serif tam={96} peso={600}>No cotiza en bolsa</Serif>
      </T>
      <Detras x={690} y={410} t={p(1) - 3} tam={270} ancla="i">Familiar</Detras>
      <Sujeto src={med(ctx, 'c_roig')} x={470} y={1110} alto={860} t={p(2) - 4} de="aba" />
      {/* el capital */}
      <div style={{position: 'absolute', inset: 0, opacity: (1 - b) * tr(p(3), -6, 8)}}>
        <svg width={420} height={420} viewBox="-210 -210 420 420" style={{position: 'absolute', left: 1040, top: 560}}>
          <circle r={150} fill="none" stroke="rgba(255,255,255,0.22)" strokeWidth={78} />
          <circle r={150} fill="none" stroke={PAL.verde[0]} strokeWidth={78} strokeDasharray={`${C * 0.8 * u} ${C}`} transform="rotate(-90)" />
        </svg>
        <T x={1250} y={770} op={tr(p(3), 10, 8)}>
          <Cifra tam={96}>80 %</Cifra>
        </T>
        <T x={1500} y={700} ancla="i" op={tr(p(3), 4, 8)}>
          <Sans tam={46} peso={800}>Juan Roig y</Sans>
        </T>
        <T x={1500} y={762} ancla="i" op={tr(p(3), 6, 8)}>
          <Sans tam={46} peso={800}>Hortensia Herrero</Sans>
        </T>
        <T x={1500} y={836} ancla="i" op={tr(p(3), 10, 8)}>
          <Sans tam={36} peso={500} color="#D5DBE6">la mayoría del capital</Sans>
        </T>
      </div>
      {/* nadie le mete prisa */}
      {p(4) >= -3 && (
        <>
          <Persona x={1560} y={1040} s={1.5 * pop(p(4), 12, 1.5)} color="rosa" />
          <T x={1500} y={590} s={pop(p(4) - 6, 11, 1.5)} rot={3} op={1 - tr(p(5), 0, 8) * 0.5}>
            <Chip tam={40} color="rosa">«¡Un país nuevo cada dos años!»</Chip>
          </T>
          <T x={1560} y={1010} op={tr(p(4), 8, 8)}>
            <Eti tam={26} color="#fff">un fondo de inversión</Eti>
          </T>
          <Marca tipo="no" x={1560} y={820} t={p(4) - 26} s={3.4} grosor={9} />
          <T x={1030} y={740} s={pop(p(5), 12, 1.5)}>
            <Cifra tam={150} color="ambar">8 años</Cifra>
          </T>
          <T x={1030} y={850} op={tr(p(5), 8, 8)}>
            <Sans tam={38} peso={700}>para ganar dinero en Portugal</Sans>
          </T>
          <Sello x={1030} y={980} t={p(6)} tam={90} rot={-6} color={PAL.verde[0]}>Puede</Sello>
        </>
      )}
    </AbsoluteFill>
  );
};

/** 430-435 s · segundo: el dato que casi nadie mira. Sigue creciendo dentro de Espana, sin abrir tiendas. */
export const SinAbrir: React.FC<EP> = ({t, p, dur}) => {
  const cam = camara(t, [
    [0, 640, 850, 2.5],
    [dur, 630, 866, 2.8],
  ]);
  const esp = centro('ESP', MX, MY, MK);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0F4A2D', borde: PAL.verde[1]} : undefined)} />
        <Tiendas r={1.5} nPt={0} />
        <A x={esp[0] + 10} y={esp[1] + 10} s={0.9 * pop(p(1), 12, 1.6)}>
          <path d="M-60,40 L-20,0 L10,22 L62,-40 M30,-42 L64,-42 L64,-8" fill="none" stroke="#FFD95A" strokeWidth={13} strokeLinecap="round" strokeLinejoin="round" />
        </A>
      </Mundo>
      <T x={120} y={150} ancla="i" s={pop(t, 12, 1.6)}>
        <span style={{display: 'inline-block', width: 110, height: 110, borderRadius: 55, background: 'linear-gradient(180deg,#FFD95A,#F29A0B)', font: "70px/114px 'M Black'", color: '#1B1D22', textAlign: 'center'}}>2</span>
      </T>
      <T x={120} y={300} ancla="i" op={tr(t, 4, 8)}>
        <Serif tam={84} peso={600}>El dato que</Serif>
      </T>
      <T x={120} y={400} ancla="i" op={tr(t, 7, 8)}>
        <Serif tam={84} peso={600}>casi nadie mira</Serif>
      </T>
      <T x={120} y={600} ancla="i" s={pop(p(1), 12, 1.5)}>
        <Chip tam={54}>Sigue creciendo en España</Chip>
      </T>
      <Sello x={470} y={800} t={p(2)} tam={84} rot={-5} color="#FFD95A">Sin abrir tiendas</Sello>
    </AbsoluteFill>
  );
};

/** 436-448 s · 2015: 1.587 tiendas y 20.831 M EUR. 2025: 1.603 (16 mas) y casi 40.000 M EUR. */
export const DiezAnios: React.FC<EP> = ({t, p}) => {
  const col = (x0: number, anio: string, n: number, tT: number, tV: number, ventas: number, nf: number, extra: number) => (
    <>
      <Hoja x={x0 + 90} y={150} anio={anio} s={0.92 * pop(tT + 2, 12, 1.4)} color={extra ? 'verde' : 'humo'} />
      <T x={x0 + 200} y={120} ancla="i" s={pop(tT - 2, 12, 1.4)}>
        <Cifra tam={100}>{miles(Math.round(n * sal(tT / 30)))}</Cifra>
      </T>
      <T x={x0 + 206} y={196} ancla="i" op={tr(tT, 8, 8)}>
        <Sans tam={34} peso={600} color="#C9CED8">tiendas{extra ? ' · 16 más' : ''}</Sans>
      </T>
      <svg width={760} height={440} style={{position: 'absolute', left: x0, top: 260, overflow: 'visible'}}>
        {Array.from({length: n}, (_, k) => {
          const c = k % 46;
          const r = Math.floor(k / 46);
          const nueva = extra && k >= n - 16;
          const e = nueva ? pop(p(3) - (k - (n - 16)) * 1.2, 8, 2.6) : c01((tT - 2 - r * 0.6 - c * 0.12) / 3);
          return e <= 0 ? null : mini(c * 16.4 + 8, r * 12.4 + 7, 0.62 * e, nueva ? '#FFD95A' : PAL.verde[0], nueva ? '#FFD95A' : '#E9EDF3', k);
        })}
      </svg>
      {Array.from({length: nf}, (_, k) => {
        const tt = tV - k * 0.9;
        return tt < 0 ? null : <Fajo key={k} x={x0 + 44 + (k % 10) * 74} y={770 + Math.floor(k / 10) * 44 - (1 - rebote(tt / 9, 0.9)) * 120} s={0.52} tono={k % 2} />;
      })}
      <T x={x0} y={990} ancla="i" s={pop(tV - 4, 12, 1.4)}>
        <Cifra tam={100} color={extra ? 'ambar' : 'verde'}>{miles(Math.round(ventas * sal(tV / 30)))} M€</Cifra>
      </T>
      <T x={x0 + 560} y={996} ancla="i" op={tr(tV, 8, 8)}>
        <Sans tam={34} peso={600} color="#C9CED8">en ventas</Sans>
      </T>
    </>
  );
  return (
    <AbsoluteFill>
      <Escenario />
      {col(110, '2015', 1587, p(0), p(1), 20831, 21, 0)}
      {col(1050, '2025', 1603, p(2), p(4), 39766, 40, 1)}
      <div style={{position: 'absolute', left: 959, top: 90, width: 2, height: 920, background: 'rgba(255,255,255,0.08)'}} />
      <T x={960} y={520} s={pop(p(5), 13, 1.7)} rot={-4}>
        <Chip tam={84} color="ambar" tinta="#1B1D22">El doble de ventas</Chip>
      </T>
      <T x={960} y={650} s={pop(p(5) - 10, 12, 1.5)} rot={2}>
        <Chip tam={50} fondo="#F4F5F7" tinta="#0B0C10">con casi las mismas tiendas</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 449-457 s · cada supermercado ha pasado de mover ~13 M EUR al ano a ~25. */
export const PorTiendaEs: React.FC<EP> = ({t, p}) => {
  const u = io(tr(p(1), 0, 34));
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={130} op={tr(t, 0, 8)}>
        <Serif tam={90} peso={600}>Lo que mueve <span style={{color: '#FFD95A'}}>cada supermercado</span> al año</Serif>
      </T>
      <div style={{position: 'absolute', left: 240, top: 852, width: 1440, height: 6, background: '#30364A'}} />
      <Tienda x={640} y={850} s={1.7 * pop(t - 4, 12, 1.4)} nombre="MERCADONA" />
      <PilaMonedas x={1010} y={832} n={c01(t / 6) * 9 + u * 8.3} s={1.5} />
      <Hoja x={1380} y={420} anio={u > 0.5 ? '2025' : '2015'} s={1.05 * pop(t - 6, 12, 1.4) * (1 + 0.15 * Math.sin(c01((p(1) - 12) / 12) * Math.PI))} color={u > 0.5 ? 'verde' : 'humo'} />
      <T x={1380} y={640} s={pop(t - 10, 12, 1.4)}>
        <Cifra tam={170} color={u > 0.5 ? 'ambar' : 'verde'}>≈ {Math.round(lerp(13, 25, u))} M€</Cifra>
      </T>
      <T x={1380} y={770} op={tr(p(1), 20, 8)}>
        <Chip tam={48} color="ambar" tinta="#1B1D22">casi el doble</Chip>
      </T>
      <T x={960} y={1000} op={tr(p(2), 0, 8)}>
        <Eti tam={24}>Cuentas propias, hechas con las cifras de la compañía</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** 457-466 s · como: cierra tiendas pequenas y abre grandes (43 aperturas, 45 cierres). Mas frescos, platos, parking. */
export const Como: React.FC<EP> = ({t, p, ctx}) => {
  const cierra = io(tr(p(1), 4, 18));
  const extras = ['+ frescos', '+ comida preparada', '+ aparcamiento'];
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={960} y={130} s={pop(t, 12, 1.5)}>
        <Serif tam={130} peso={600}>¿Cómo?</Serif>
      </T>
      <div style={{position: 'absolute', left: 120, top: 852, width: 1680, height: 6, background: '#30364A'}} />
      <div style={{position: 'absolute', inset: 0, opacity: 1 - 0.55 * tr(p(2), 0, 12)}}>
        <Tienda x={420} y={850} s={1.05 * pop(p(1) - 2, 12, 1.4)} ancho={210} cierre={cierra} color="humo" />
      </div>
      <T x={420} y={930} op={tr(p(1), 6, 8)}>
        <Sans tam={42} peso={700} color="#C9CED8">Cierra las pequeñas</Sans>
      </T>
      <T x={420} y={470} s={pop(p(4), 12, 1.5)}>
        <Cifra tam={150} color="rojo">45</Cifra>
      </T>
      <T x={420} y={570} op={tr(p(4), 6, 8)}>
        <Sans tam={36} peso={600} color="#C9CED8">cierres en 2025</Sans>
      </T>
      <Tienda x={1180} y={850} s={1.85 * pop(p(2), 13, 1.5)} ancho={420} nombre="MERCADONA" />
      <T x={1180} y={930} op={tr(p(2), 6, 8)}>
        <Sans tam={42} peso={700}>Abre las grandes</Sans>
      </T>
      <T x={1180} y={290} s={pop(p(3), 12, 1.5)}>
        <Cifra tam={150}>43</Cifra>
      </T>
      <T x={1180} y={390} op={tr(p(3), 6, 8)}>
        <Sans tam={36} peso={600} color="#C9CED8">aperturas en 2025</Sans>
      </T>
      {extras.map((x, i) => (
        <T key={x} x={1610} y={520 + i * 110} s={pop(p(5 + i), 11, 1.7)} rot={(i - 1) * 3}>
          <Chip tam={44} color={i === 0 ? 'cian' : i === 1 ? 'ambar' : 'lila'} tinta={i === 1 ? '#1B1D22' : '#fff'}>{x}</Chip>
        </T>
      ))}
      <Sujeto src={med(ctx, 'c_pescado')} x={1610} y={470} ancho={300} t={p(5) - 2} de="pop" />
    </AbsoluteFill>
  );
};

/** 466-476 s · el plan que si tiene: no se llama Italia. Tienda 9: 3.700 M EUR hasta 2033. */
export const Tienda9: React.FC<EP> = ({t, p, dur, ctx}) => {
  const it = (1 - tr(p(2), -3, 6)) * tr(p(1), -4, 6);
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={11} luz={0.42} />
      <T x={960} y={110} op={tr(t, 0, 8)}>
        <Serif tam={84} peso={600}>El plan que <span style={{color: '#FFD95A'}}>sí</span> tiene sobre la mesa</Serif>
      </T>
      <div style={{position: 'absolute', inset: 0, opacity: it}}>
        <svg width={520} height={600} viewBox="438 592 210 226" style={{position: 'absolute', left: 700, top: 240}}>
          <path d={EUROPA.ITA.d} fill="#F2A81D" stroke="#FFD95A" strokeWidth={1.2} />
        </svg>
        <Marca tipo="no" x={960} y={540} t={p(1) + 8} s={5} grosor={7} />
        <T x={960} y={920} s={pop(p(1) + 4, 11, 1.5)}>
          <Chip tam={60} color="humo">No se llama Italia</Chip>
        </T>
      </div>
      <Detras x={960} y={390} t={p(2)} tam={340}>Tienda 9</Detras>
      <Sujeto src={med(ctx, 'c_tienda')} x={960} y={900} ancho={1400} t={p(2) - 4} de="aba" />
      <T x={700} y={970} s={pop(p(3), 12, 1.5)}>
        <Cifra tam={150} color="ambar">{miles(Math.round(3700 * sal(p(3) / 34)))} M€</Cifra>
      </T>
      <T x={1090} y={950} ancla="i" op={tr(p(3), 8, 8)}>
        <Sans tam={40} peso={700}>para rehacer todos</Sans>
      </T>
      <T x={1090} y={1004} ancla="i" op={tr(p(3), 10, 8)}>
        <Sans tam={40} peso={700}>sus supermercados</Sans>
      </T>
      <Hoja x={1700} y={300} anio="2033" s={1.2 * pop(p(4), 12, 1.6)} color="verde" />
    </AbsoluteFill>
  );
};

/** 477-487 s · entre 1.200 millones en otro pais o en las tiendas que ya conoce, Roig elige lo segundo. */
export const Eleccion: React.FC<EP> = ({t, p, dur, ctx}) => {
  const el = tr(p(3), 0, 10);
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={13} luz={0.36} />
      <Detras x={960} y={250} t={t - 2} tam={200}>La respuesta</Detras>
      <div style={{position: 'absolute', inset: 0, opacity: 1 - 0.6 * el}}>
        <T x={330} y={420} s={pop(p(1), 11, 1.5)}>
          <Chip tam={54} color="humo">Otro país</Chip>
        </T>
        <T x={330} y={570} s={pop(p(1) - 6, 12, 1.5)}>
          <Cifra tam={130} color="rojo">1.230 M€</Cifra>
        </T>
        <T x={330} y={690} op={tr(p(1), 12, 8)}>
          <Sans tam={38} peso={600} color="#D5DBE6">y una década para ganar</Sans>
        </T>
        <T x={330} y={742} op={tr(p(1), 14, 8)}>
          <Sans tam={38} peso={600} color="#D5DBE6">lo que gana en casa</Sans>
        </T>
      </div>
      <Sujeto src={med(ctx, 'c_roig')} x={960} y={1110} alto={800} t={t - 6} de="aba" />
      <T x={1590} y={420} s={pop(p(2), 11, 1.5) * (1 + 0.12 * el)}>
        <Chip tam={54}>Sus tiendas</Chip>
      </T>
      <T x={1570} y={570} s={pop(p(2) - 6, 12, 1.5) * (1 + 0.08 * el)}>
        <Cifra tam={116}>3.700 M€</Cifra>
      </T>
      <T x={1590} y={690} op={tr(p(2), 12, 8)}>
        <Sans tam={38} peso={600} color="#D5DBE6">en las que ya conoce</Sans>
      </T>
      <T x={1590} y={742} op={tr(p(2), 14, 8)}>
        <Sans tam={38} peso={600} color="#D5DBE6">y cada año venden más</Sans>
      </T>
      <Flecha x0={1150} y0={880} x1={1400} y1={800} u={io(tr(p(3), 0, 16))} curva={-0.2} grosor={11} color="#FFD95A" trazos={false} />
      <Sello x={1530} y={900} t={p(3) + 10} tam={60} rot={-5} color={PAL.verde[0]}>Elige lo segundo</Sello>
    </AbsoluteFill>
  );
};

/** 488-490 s · asi que no: Mercadona no se queda en Espana por miedo. */
export const NoMiedo: React.FC<EP> = ({t, p}) => (
  <AbsoluteFill>
    <Escenario tipo="verde" />
    <T x={960} y={400} s={pop(t, 13, 1.5)}>
      <span style={{font: "700 230px/1 'M Serif'", color: '#fff', letterSpacing: -6}}>Así que no.</span>
    </T>
    <T x={960} y={680} op={tr(p(1), 0, 8)}>
      <Serif tam={90} peso={600}>No se queda en España por <span style={{color: '#FFE27A', textDecoration: 'line-through', textDecorationThickness: 8}}>miedo</span></Serif>
    </T>
  </AbsoluteFill>
);

const Num: React.FC<{n: number; t: number}> = ({n, t}) => (
  <T x={170} y={150} s={pop(t, 12, 1.6)}>
    <span style={{display: 'inline-block', width: 130, height: 130, borderRadius: 65, background: 'linear-gradient(180deg,#FFD95A,#F29A0B)', font: "84px/136px 'M Black'", color: '#1B1D22', textAlign: 'center', boxShadow: '0 14px 36px rgba(0,0,0,0.45)'}}>{n}</span>
  </T>
);
/** 491-499 s · se queda porque ya sabe lo que cuesta un pais: 1.230 M EUR, 8 anos y menos de 1/3 del margen. */
export const Recap1: React.FC<EP> = ({t, p}) => {
  const D: [string, string, 'rojo' | 'ambar' | 'verde'][] = [['1.230 M€', 'de inversión', 'rojo'], ['8 años', 'hasta el primer beneficio', 'ambar'], ['< 1/3', 'del margen que tiene en casa', 'verde']];
  return (
    <AbsoluteFill>
      <Escenario />
      <Num n={1} t={t} />
      <T x={280} y={110} ancla="i" op={tr(t, 3, 8)}>
        <Eti tam={30}>Se queda porque</Eti>
      </T>
      <T x={276} y={188} ancla="i" op={tr(t, 5, 8)}>
        <Serif tam={96} peso={600}>ya sabe lo que <span style={{color: '#FFD95A'}}>cuesta un país</span></Serif>
      </T>
      {D.map(([c, pie, col], i) => (
        <React.Fragment key={c}>
          <div style={{position: 'absolute', left: 120 + i * 570, top: 400, width: 530, height: 540, borderRadius: 36, background: 'rgba(255,255,255,0.055)', border: '2px solid rgba(255,255,255,0.08)', opacity: tr(p(i + 1), 0, 6), transform: `translateY(${(1 - sal(tr(p(i + 1), 0, 14))) * 80}px)`}} />
          <T x={385 + i * 570} y={620} s={pop(p(i + 1) - 3, 12, 1.5)}>
            <Cifra tam={i === 0 ? 122 : 160} color={col}>{c}</Cifra>
          </T>
          <T x={385 + i * 570} y={800} op={tr(p(i + 1), 8, 8)}>
            <Sans tam={38} peso={600} color="#C9CED8">{pie}</Sans>
          </T>
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};

/** 500-510 s · porque lo que la hace ganar no cabe en un camion: una red de 40 anos, y en cada frontera, otra vez. */
export const Recap2: React.FC<EP> = ({t, p, dur, ctx}) => {
  const x = lerp(-300, 560, sal(tr(t, 6, 40)));
  const pegas = ['No son las tiendas ni el nombre', 'Es una red de proveedores', 'En cada frontera, empezar otra vez'];
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={12} luz={0.4} />
      <Num n={2} t={t} />
      <T x={280} y={110} ancla="i" op={tr(t, 3, 8)}>
        <Eti tam={30} color="#fff">Se queda porque</Eti>
      </T>
      <T x={276} y={188} ancla="i" op={tr(t, 5, 8)}>
        <Serif tam={84} peso={600}>lo que la hace ganar <span style={{color: '#FFD95A'}}>no cabe en un camión</span></Serif>
      </T>
      <Detras x={600} y={520} t={p(2) + 14} tam={300}>40 años</Detras>
      <Sujeto src={med(ctx, 'c_furgo')} x={x} y={1040} ancho={900} t={t - 6} de="izq" lejos={0} />
      {pegas.map((q, i) => (
        <T key={q} x={1820} y={470 + i * 150} ancla="d" s={pop(p(i + 1), 11, 1.5)} rot={(i - 1) * 2}>
          <Chip tam={i === 1 ? 54 : 46} color={i === 1 ? 'verde' : 'humo'}>{q}</Chip>
        </T>
      ))}
    </AbsoluteFill>
  );
};

/** 510-518 s · y porque nadie le obliga a irse: sin bolsa, sin prisa y vendiendo el doble sin abrir tiendas. */
export const Recap3: React.FC<EP> = ({t, p, dur, ctx}) => {
  const pegas = ['Sin bolsa', 'Sin prisa', 'Vende el doble que hace diez años'];
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={12} luz={0.4} />
      <Num n={3} t={t} />
      <T x={280} y={110} ancla="i" op={tr(t, 3, 8)}>
        <Eti tam={30} color="#fff">Se queda porque</Eti>
      </T>
      <T x={276} y={188} ancla="i" op={tr(t, 5, 8)}>
        <Serif tam={96} peso={600}>nadie le <span style={{color: '#FFD95A'}}>obliga a irse</span></Serif>
      </T>
      <Sujeto src={med(ctx, 'c_roig')} x={1420} y={1110} alto={840} t={t - 6} de="der" />
      {pegas.map((q, i) => (
        <T key={q} x={130} y={480 + i * 160} ancla="i" s={pop(p(i + 1), 11, 1.5)} rot={(1 - i) * 2}>
          <Chip tam={i === 2 ? 52 : 76} color={i === 2 ? 'ambar' : 'verde'} tinta={i === 2 ? '#1B1D22' : '#fff'}>{q}</Chip>
        </T>
      ))}
      <T x={138} y={890} ancla="i" op={tr(p(3), 10, 8)}>
        <Sans tam={40} peso={600} color="#fff">sin abrir más tiendas</Sans>
      </T>
    </AbsoluteFill>
  );
};

/** 525-527 s · y eso, de momento, no ha pasado. */
export const NoPasado: React.FC<EP> = ({t, p}) => (
  <AbsoluteFill>
    <Escenario />
    <T x={140} y={150} ancla="i" op={tr(t, 0, 8)}>
      <Eti tam={30}>Lo que le queda de cada 100 € que vende</Eti>
    </T>
    <T x={140} y={330} ancla="i" s={pop(t, 11, 1.4)}>
      <Chip tam={50}>España (grupo)</Chip>
    </T>
    <Barra x={140} y={450} w={1300} h={90} u={io(tr(t, 2, 20))} />
    <T x={1470} y={450} ancla="i" s={pop(t - 12, 12, 1.4)}>
      <Cifra tam={130}>4,1 €</Cifra>
    </T>
    <T x={140} y={630} ancla="i" s={pop(t - 4, 11, 1.4)}>
      <Chip tam={50} color="ambar" tinta="#1B1D22">Portugal</Chip>
    </T>
    <div style={{position: 'absolute', left: 140, top: 705, width: 1300, height: 90, borderRadius: 45, border: '4px dashed rgba(255,255,255,0.35)'}} />
    <Barra x={140} y={750} w={380} h={90} u={io(tr(t, 8, 20))} color="ambar" />
    <T x={550} y={750} ancla="i" s={pop(t - 18, 12, 1.4)}>
      <Cifra tam={130} color="ambar">1,2 €</Cifra>
    </T>
    <Sello x={1320} y={900} t={p(1)} tam={100} rot={-6}>De momento, no</Sello>
  </AbsoluteFill>
);

/** 527-535 s · la mayoria crece porque no sabe estarse quieta. Mercadona ha hecho de quedarse en casa su mejor negocio. */
export const Final: React.FC<EP> = ({t, p, dur, ctx}) => {
  const b = p(1);
  const cam = camara(t, [
    [0, 960, 540, 1],
    [dur, 960, 540, 1.08],
  ]);
  const paises = ['DEU', 'FRA', 'GBR', 'ITA', 'NLD', 'SWE', 'POL', 'CHE', 'AUT', 'BEL'];
  if (b < 0) {
    return (
      <AbsoluteFill>
        <Escenario cam={cam} />
        <Mundo cam={cam}>
          <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0F4A2D', borde: PAL.verde[1]} : paises.includes(c) ? {fill: '#2B3348'} : undefined)} />
          {paises.map((c, i) => {
            const o = centro(c, MX, MY, MK);
            const d = centro(paises[(i * 3 + 4) % paises.length], MX, MY, MK);
            return <Flecha key={c} x0={o[0]} y0={o[1]} x1={lerp(o[0], d[0], 0.8)} y1={lerp(o[1], d[1], 0.8)} u={io(tr(t, 4 + i * 3, 18))} curva={i % 2 ? 0.25 : -0.25} grosor={4} color={PAL.rosa[0]} />;
          })}
        </Mundo>
        <T x={80} y={430} ancla="i" op={tr(t, 2, 8)}>
          <Serif tam={78} peso={600}>La mayoría crece</Serif>
        </T>
        <T x={80} y={530} ancla="i" op={tr(t, 6, 8)}>
          <Serif tam={78} peso={600}>porque no sabe</Serif>
        </T>
        <T x={80} y={630} ancla="i" op={tr(t, 10, 8)}>
          <Serif tam={78} peso={600} color="#FF8FC3">estarse quieta</Serif>
        </T>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={9} luz={0.5} />
      <Detras x={960} y={360} t={b + 4} tam={400}>en casa</Detras>
      <Sujeto src={med(ctx, 'c_tienda')} x={960} y={900} ancho={1500} t={b} de="aba" />
      <T x={960} y={980} op={tr(b, 14, 10)}>
        <Serif tam={70} peso={600}>Quedarse fue <span style={{color: '#FFD95A'}}>su mejor negocio</span></Serif>
      </T>
    </AbsoluteFill>
  );
};

export const CAP5 = {bolsa: Bolsa, dos_motivos: DosMotivos, familiar: Familiar, sin_abrir: SinAbrir, diez_anios: DiezAnios, por_tienda_es: PorTiendaEs, como: Como, tienda9: Tienda9, eleccion: Eleccion, no_miedo: NoMiedo, recap1: Recap1, recap2: Recap2, recap3: Recap3, no_pasado: NoPasado, final: Final};
export {rnd};
