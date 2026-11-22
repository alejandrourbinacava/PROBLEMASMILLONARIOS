import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {Chip, Cifra, Escenario, Eti, Flecha, Hoja, Mapa, Marca, Mundo, PAL, Palabras, Sans, Sello, Serif, T, c01, camara, geo, io, lerp, mini, pop, sal, tr} from './kit';
import {Detras} from './m_capas';
import {MK, MX, MY} from './m_gancho';
import {Im, deriva} from './m_vox';
import {AM, Am, CIAN, Dato, Ficha, Fondo, Movil, Parrafo, Quien, Tit, Ventana} from './p_comun';
import {PUNTOS} from './puntos';

const paso = (f: number) => Math.abs(Math.sin(f / 4.5)) * -7;
const Num: React.FC<{x: number; y: number; t: number; n: string; tam?: number}> = ({x, y, t, n, tam = 120}) => (
  <T x={x} y={y} s={pop(t, 12, 1.6)}>
    <span style={{display: 'inline-block', width: tam, height: tam, borderRadius: tam / 2, background: 'linear-gradient(180deg,#FFD95A,#F29A0B)', font: `${tam * 0.62}px/${tam * 1.04}px 'M Black'`, color: '#1B1D22', textAlign: 'center', boxShadow: '0 14px 36px rgba(0,0,0,0.45)'}}>{n}</span>
  </T>
);

// =============================================================== 3 · EL ANO QUE VENDIO CERO
/** Marzo de 2020: cualquier cadena pierde una parte; Primark lo pierde entero. */
export const Cierre: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  const fila = (y: number, nombre: string, color: 'humo' | 'cian', tApaga: number, online: boolean, tIn: number) => {
    const g = tr(tApaga, 0, 12);
    return tIn < 0 ? null : (
      <>
        <T x={900} y={y - 76} ancla="i" s={pop(tIn, 11, 1.4)}>
          <Chip tam={42} color={color}>{nombre}</Chip>
        </T>
        <div style={{position: 'absolute', left: 900, top: y - 30, width: (online ? 680 : 900) * io(tr(tIn, 4, 16)), height: 76, borderRadius: online ? '38px 0 0 38px' : 38, background: g > 0.5 ? 'linear-gradient(90deg,#5C6375,#2F3442)' : 'linear-gradient(90deg,#45D0FF,#0A7BD6)', overflow: 'hidden'}}>
          <div style={{font: "800 30px/76px 'D Sans'", color: '#fff', paddingLeft: 30, whiteSpace: 'nowrap'}}>{g > 0.5 ? 'tiendas · cerradas' : 'tiendas'}</div>
        </div>
        {online && (
          <div style={{position: 'absolute', left: 900 + 686, top: y - 30, width: 214 * io(tr(tIn, 12, 12)), height: 76, borderRadius: '0 38px 38px 0', background: 'linear-gradient(90deg,#FFD95A,#F29A0B)', overflow: 'hidden'}}>
            <div style={{font: "800 30px/76px 'D Sans'", color: '#1B1D22', paddingLeft: 24, whiteSpace: 'nowrap'}}>internet</div>
          </div>
        )}
      </>
    );
  };
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.32} />
      <Tit x={120} y={120} t={t} ancla="i" tam={80}>Cierran las tiendas en <Am>media Europa</Am></Tit>
      <Im src="g_tienda_p" x={420} y={1140} w={720} t={t - 2} de="aba" cam={cam} gris={tr(t, 20, 16)} luz={1 - 0.3 * tr(t, 20, 16)} />
      <Im src="g_persiana" x={420} y={1140} w={560} t={t - 16} de="arr" z={1.1} cam={cam} />
      {fila(430, 'Cualquier cadena de moda', 'humo', p(2), true, p(1))}
      <T x={900} y={520} ancla="i" op={tr(p(2), 6, 8)}>
        <Sans tam={34} peso={600} color="#D5DBE6">pierde una parte de su negocio</Sans>
      </T>
      {fila(760, 'Primark', 'cian', p(3) - 14, false, p(3))}
      <Sello x={1380} y={900} t={p(3) - 24} tam={76} rot={-5}>Lo pierde entero</Sello>
      <T x={1800} y={1010} ancla="d" op={tr(p(1), 10, 8)}>
        <Eti tam={22} color="#8D93A1">Esquema, sin escala</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** Mayo de 2020: de mas de 700 M EUR al mes a cero. Y 300 M EUR de ropa sin vender. */
export const Cero: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const v = p(2) < 0 ? 700 : Math.round(700 * (1 - io(tr(p(2), 0, 26))));
  const b = io(tr(p(3), -4, 14));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Hoja x={190} y={170} anio="2020" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={170} ancla="i" op={tr(t, 4, 8)}>
        <Serif tam={80} peso={600}>Mayo: Primark lo reconoce</Serif>
      </T>
      <Im src="g_fajos" x={lerp(480, 300, b)} y={1080} w={lerp(760, 420, b)} t={p(1) - 4} de="izq" op={1 - 0.85 * tr(p(2), 6, 20)} gris={tr(p(2), 6, 20)} />
      <T x={lerp(1250, 520, b)} y={lerp(430, 420, b)} s={pop(p(1), 12, 1.4) * lerp(1, 0.62, b)}>
        <Cifra tam={300} color={v === 0 ? 'rojo' : 'ambar'}>{v === 0 ? '0 €' : `${v} M€`}</Cifra>
      </T>
      <T x={lerp(1250, 520, b)} y={lerp(640, 560, b)} op={tr(p(1), 6, 8)}>
        <Sans tam={44} peso={700} color="#D5DBE6">en ventas al mes</Sans>
      </T>
      <Im src="g_monton" x={1330} y={1120} w={880} t={p(3)} de="aba" />
      <Dato x={1330} y={370} t={p(4)} cifra="−300 M€" pie="de valor para la ropa que se quedó sin vender" tam={160} color="rojo" />
    </AbsoluteFill>
  );
};

/** Enero de 2021: 305 de 389 tiendas cerradas. El beneficio, de 1.100 a 400 M EUR. */
export const Persianas: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const COLS = 30;
  const b = tr(p(3), -4, 10);
  const u1 = io(tr(p(3), 0, 20));
  const u2 = io(tr(p(4), 0, 20));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Hoja x={190} y={150} anio="2021" s={pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={150} ancla="i" op={tr(t, 4, 8)}>
        <Serif tam={76} peso={600}>Enero: otra ola de cierres</Serif>
      </T>
      <svg width={COLS * 46} height={13 * 42} style={{position: 'absolute', left: 270, top: 270, overflow: 'visible', opacity: 1 - b}}>
        {Array.from({length: 389}, (_, k) => {
          const e = pop(t - 6 - k * 0.05, 8, 1.8);
          if (e <= 0) return null;
          // cierran 305: todas menos una de cada cuatro o cinco, repartidas
          const abierta = k % 9 === 0 || k % 9 === 4;
          const cerrada = !abierta || k >= 378;
          const tc = p(1) - (k % 97) * 0.35;
          const gris = cerrada && tc >= 0;
          return mini((k % COLS) * 46 + 23, Math.floor(k / COLS) * 42 + 21, 1.7 * e, gris ? '#5C6375' : PAL.cian[0], gris ? '#8D93A1' : '#EEF1F6', k);
        })}
      </svg>
      <Dato x={960} y={884} t={p(2)} cifra="305 de 389" pie="tiendas con la persiana bajada" tam={128} color="rojo" op={1 - b} />
      <T x={960} y={290} op={tr(p(3), 0, 8)}>
        <Eti tam={32} color="#C9CED8">Beneficio anual de Primark</Eti>
      </T>
      <div style={{position: 'absolute', left: 620, top: 920 - 440 * u1, width: 240, height: 440 * u1, borderRadius: 16, background: 'linear-gradient(180deg,#45D0FF,#0A7BD6)'}} />
      <div style={{position: 'absolute', left: 1060, top: 920 - 164 * u2, width: 240, height: 164 * u2, borderRadius: 16, background: 'linear-gradient(180deg,#FF6A5C,#C4161C)'}} />
      <T x={740} y={420} s={pop(p(3) - 12, 12, 1.4)}>
        <Cifra tam={110} color="cian">≈ 1.100 M€</Cifra>
      </T>
      <T x={1180} y={700} s={pop(p(4) - 8, 12, 1.4)}>
        <Cifra tam={110} color="rojo">≈ 400 M€</Cifra>
      </T>
      <T x={740} y={970} op={tr(p(3), 6, 8)}>
        <Eti tam={28} color="#C9CED8">antes</Eti>
      </T>
      <T x={1180} y={970} op={tr(p(4), 6, 8)}>
        <Eti tam={28} color="#C9CED8">el año del covid</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** Todo el sector: ahora si, abre la tienda online. */
export const Sector: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const C: [number, number, number, number, 'humo' | 'ambar' | 'rosa' | 'lila'][] = [
    [420, 330, -6, 56, 'ambar'], [1500, 300, 5, 50, 'rosa'], [300, 640, 4, 46, 'lila'], [1500, 620, -4, 52, 'ambar'], [520, 900, -3, 44, 'rosa'], [1420, 900, 6, 48, 'lila'],
  ];
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={110} tam={76}>Todo el sector le decía lo mismo</Tit>
      <Im src="g_persiana" x={960} y={1080} w={780} t={t - 2} de="aba" luz={0.9} />
      {C.map(([x, y, rot, tam, col], i) => (
        <T key={i} x={x} y={y} s={pop(p(1) - i * 5, 11, 1.8)} rot={rot}>
          <Chip tam={tam} color={col} tinta={col === 'ambar' ? '#1B1D22' : '#fff'}>¡Abre la tienda online!</Chip>
        </T>
      ))}
    </AbsoluteFill>
  );
};

/** George Weston: «no por una pandemia que ocurre una vez cada cien anos». */
export const Weston: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Quien x={110} y={150} t={t} nombre="George Weston" cargo="Jefe del grupo dueño de Primark · en pleno confinamiento, 2020" />
      <Im src="g_persiana" x={1540} y={1090} w={640} t={t - 4} de="der" luz={0.85} cam={cam} />
      <div style={{position: 'absolute', left: 110, top: 400, width: 1100, font: "700 62px/1.2 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«Nuestras decisiones sobre internet se tomarán en su propio contexto, *no por una pandemia que ocurre una vez cada cien años*»." u={p(2) < 0 ? 0 : c01(p(2) / 190)} />
      </div>
    </AbsoluteFill>
  );
};

/** Enero de 2021: la cuenta oficial responde a una clienta. */
export const Tuit: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Hoja x={190} y={170} anio="2021" s={1.05 * pop(t, 12, 1.4)} color="cian" />
      <T x={320} y={140} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={30} color={CIAN}>14 de enero</Eti>
      </T>
      <Parrafo x={316} y={170} w={760} t={t - 6} tam={66} serif>La cuenta oficial de Primark responde a una clienta</Parrafo>
      <Movil x={1100} top={30} w={840} t={p(1) - 10}>
        <div style={{position: 'absolute', inset: 0, background: '#fff', padding: '34px 24px'}}>
          <div style={{display: 'flex', gap: 14, alignItems: 'center', opacity: tr(p(2), 0, 6)}}>
            <div style={{width: 70, height: 70, borderRadius: 35, background: '#0AA5D8', font: "800 34px/70px 'D Sans'", color: '#fff', textAlign: 'center'}}>P</div>
            <div>
              <div style={{font: "800 27px 'D Sans'", color: '#1B1D22'}}>Primark <span style={{color: '#0AA5D8'}}>✓</span></div>
              <div style={{font: "500 20px 'D Sans'", color: '#6B7383'}}>cuenta oficial · 14 ene. 2021</div>
            </div>
          </div>
          <div style={{marginTop: 34, font: "600 35px/1.3 'D Sans'", color: '#1B1D22'}}>
            <Palabras texto="«Podemos confirmar que *no está en nuestros planes* abrir una tienda online»." u={p(2) < 0 ? 0 : c01(p(2) / 90)} resalta="#C4161C" color="#1B1D22" />
          </div>
          <div style={{marginTop: 30, height: 2, background: '#E4E8EE'}} />
          <div style={{marginTop: 18, font: "500 19px 'D Sans'", color: '#8D93A1'}}>Respuesta a una clienta · traducción</div>
        </div>
      </Movil>
      <Sello x={560} y={720} t={p(2) - 50} tam={66} rot={-5}>No está en sus planes</Sello>
    </AbsoluteFill>
  );
};

/** 15 de junio de 2020: reabren 153 tiendas en Inglaterra, con colas. La gente habia esperado. */
export const Colas: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const a = 1 - tr(p(1), -4, 8);
  const d = 1 - tr(p(4), -4, 8);
  const xc = lerp(-1300, 640, sal(tr(p(3), 0, 50)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.36} blur={9} />
      <Tit x={960} y={480} t={t} tam={120} op={a}>¿De dónde salía tanta seguridad?</Tit>
      <div style={{position: 'absolute', inset: 0, opacity: d}}>
        <Hoja x={190} y={170} anio="2020" s={1.05 * pop(p(1), 12, 1.4)} color="cian" />
        <T x={320} y={140} ancla="i" op={tr(p(1), 4, 8)}>
          <Eti tam={30} color={CIAN}>15 de junio</Eti>
        </T>
        <T x={316} y={210} ancla="i" op={tr(p(2), 0, 8)}>
          <Serif tam={72} peso={600}>Reabren sus 153 tiendas de Inglaterra</Serif>
        </T>
      </div>
      <Im src="g_tienda_p" x={1560} y={1140} w={640} t={p(1) - 2} de="der" />
      <Im src="g_cola" x={xc} y={1100} w={1500} t={p(3)} de="nada" z={1.1} />
      <T x={620} y={470} s={pop(p(3) - 12, 12, 1.4)} rot={-2} op={d}>
        <Chip tam={46} fondo="#F4F5F7" tinta="#0B0C10">Colas que daban la vuelta a la manzana</Chip>
      </T>
      <div style={{position: 'absolute', inset: 0, background: 'rgba(8,9,12,0.55)', opacity: tr(p(4), 0, 10)}} />
      <Tit x={960} y={200} t={p(4)} tam={96}>La gente no se había ido a otra parte</Tit>
      <Tit x={960} y={370} t={p(5)} tam={150} color={AM}>Había esperado</Tit>
    </AbsoluteFill>
  );
};

/** Espana, el ano del covid: solo un 24 % menos, sin vender nada por internet. */
export const EspanaCovid: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 900, 820, 2.3],
    [dur, 880, 850, 2.6],
  ]);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0B5E86', borde: CIAN} : undefined)} />
      </Mundo>
      <T x={1110} y={150} ancla="i" op={tr(t, 0, 8)}>
        <Eti tam={32} color={CIAN}>España · el año del covid</Eti>
      </T>
      <T x={1110} y={260} ancla="i" s={pop(t - 8, 11, 1.4)}>
        <Chip tam={40} color="humo">Tiendas cerradas durante semanas</Chip>
      </T>
      <T x={1110} y={360} ancla="i" s={pop(t - 24, 11, 1.4)}>
        <Chip tam={40} color="humo">Ni una prenda vendida por internet</Chip>
      </T>
      <Dato x={1110} y={630} t={p(1)} cifra="−24 %" pie="en ventas" tam={230} color="ambar" ancla="i" />
      <T x={1420} y={900} s={pop(p(2), 12, 1.6)} rot={-4}>
        <Chip tam={60} color="cian">Solo un 24</Chip>
      </T>
    </AbsoluteFill>
  );
};

// =============================================================== 4 · EL ATAJO
/** El camino intermedio: el tramo mas caro, hasta tu puerta, lo haces tu. */
export const Tramo: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const Y = 800;
  const xcam = lerp(520, 900, io(tr(t, 10, 50)));
  const xc = lerp(1190, 1560, sal(tr(p(2), 0, 60)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={110}>Un camino <Am>intermedio</Am></Tit>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d={`M430,${Y + 12} L1010,${Y + 12}`} stroke={CIAN} strokeWidth={10} strokeLinecap="round" strokeDasharray={600} strokeDashoffset={600 * (1 - io(tr(t, 6, 30)))} />
        <path d={`M1200,${Y + 12} L1580,${Y + 12}`} stroke={AM} strokeWidth={10} strokeLinecap="round" strokeDasharray="26 22" opacity={tr(p(1), 0, 8)} />
      </svg>
      <Im src="g_nave" x={300} y={Y} w={460} t={t - 2} de="izq" />
      <Im src="g_tienda_p" x={1100} y={Y + 6} w={330} t={t - 8} de="pop" />
      <Im src="g_camion" x={xcam} y={Y + 8} w={360} t={t - 10} de="nada" />
      <Im src="g_casa" x={1700} y={Y + 6} w={230} t={p(1) - 4} de="der" />
      <T x={715} y={Y + 80} op={tr(t, 20, 8)}>
        <Eti tam={28} color={CIAN}>lo paga Primark</Eti>
      </T>
      <T x={1390} y={400} s={pop(p(1), 12, 1.5)} rot={-3}>
        <Chip tam={50} color="ambar" tinta="#1B1D22">El tramo más caro</Chip>
      </T>
      <Im src="g_compradora" x={xc} y={Y + 8 + paso(p(2))} w={170} t={p(2)} de="nada" />
      <T x={1390} y={Y + 150} s={pop(p(2) - 6, 12, 1.5)}>
        <Chip tam={54} color="cian">…lo sigues haciendo tú</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** La web de 2022 y 2023: todo el catalogo y un boton de disponibilidad. Un escaparate sin caja. */
export const Escaparate: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const W = 1260;
  const H = 700;
  const PR = ['g_jersey', 'g_camiseta', 'g_bolsa', 'g_perchero', 'g_camiseta', 'g_jersey', 'g_perchero', 'g_bolsa'];
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit x={120} y={120} t={t} ancla="i">Primero, <Am>la web</Am></Tit>
      <T x={900} y={90} ancla="i" s={pop(p(1), 11, 1.4)}>
        <Chip tam={40} color="humo">Reino Unido · 2022</Chip>
      </T>
      <T x={900} y={170} ancla="i" s={pop(p(2), 11, 1.4)}>
        <Chip tam={40} color="cian">España · abril de 2023</Chip>
      </T>
      <Ventana x={330} y={270} w={W} h={H} t={p(3)}>
        <div style={{position: 'absolute', left: 40, top: 26, font: "800 26px 'D Sans'", letterSpacing: 8, color: '#0AA5D8'}}>PRIMARK</div>
        {PR.map((f, i) => (
          <div key={i} style={{position: 'absolute', left: 40 + (i % 4) * 298, top: 84 + Math.floor(i / 4) * 236, width: 280, height: 218, borderRadius: 14, background: '#EEF0F3', transform: `scale(${pop(p(3) - 6 - i * 2, 10, 1.4)})`}}>
            <Im src={f} x={140} y={170} w={f === 'g_jersey' ? 140 : f === 'g_bolsa' ? 100 : 170} t={99} de="nada" />
            <div style={{position: 'absolute', left: 16, bottom: 14, width: 120, height: 10, borderRadius: 5, background: '#C5CBD7'}} />
          </div>
        ))}
        <div style={{position: 'absolute', left: 330, top: 566, width: 600, height: 64, borderRadius: 32, background: '#A8E3F6', font: "800 22px/64px 'D Sans'", letterSpacing: 1.6, color: '#1B1D22', textAlign: 'center', opacity: tr(p(4), 0, 6), transform: `scale(${1 + 0.07 * Math.sin(c01(p(4) / 16) * Math.PI)})`, boxShadow: p(4) > 0 ? '0 0 0 12px rgba(69,208,255,0.3)' : undefined}}>¿ESTÁ MI TALLA EN MI TIENDA?</div>
      </Ventana>
      <Sello x={960} y={640} t={p(5)} tam={104} rot={-6}>Un escaparate sin caja</Sello>
    </AbsoluteFill>
  );
};

/** 14 de noviembre de 2022: la recogida en tienda, en 25 tiendas y solo para ninos. */
export const Recogida: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const fila = (k: number, y: number, n: string, txt: string, hijo: React.ReactNode) => (
    <>
      {hijo}
      <Num x={1120} y={y} t={p(k)} n={n} tam={92} />
      <T x={1200} y={y} ancla="i" op={tr(p(k), 4, 8)}>
        <Sans tam={52} peso={800}>{txt}</Sans>
      </T>
    </>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit x={120} y={110} t={t} ancla="i" tam={80}>Después, <Am>la recogida en tienda</Am></Tit>
      <Hoja x={190} y={300} anio="2022" s={pop(p(1), 12, 1.4)} color="cian" />
      <T x={310} y={270} ancla="i" op={tr(p(1), 4, 8)}>
        <Eti tam={28} color={CIAN}>14 de noviembre</Eti>
      </T>
      <T x={306} y={326} ancla="i" op={tr(p(1), 6, 8)}>
        <Sans tam={46} peso={700}>Empieza una prueba</Sans>
      </T>
      <Dato x={120} y={600} t={p(2)} cifra="25" pie="tiendas" tam={260} ancla="i" />
      <T x={120} y={860} ancla="i" s={pop(p(3), 11, 1.4)}>
        <Chip tam={42} color="humo">Solo ropa y productos para niños</Chip>
      </T>
      <div style={{position: 'absolute', left: 1010, top: 250, width: 2, height: 720, background: 'rgba(255,255,255,0.12)', opacity: tr(p(4), -6, 8)}} />
      {fila(4, 370, '1', 'Pides por internet', <Im src="g_portatil" x={1790} y={440} w={200} t={p(4)} de="pop" />)}
      {fila(5, 620, '2', 'Pagas', <Im src="g_moneda" x={1790} y={685} w={120} t={p(5)} de="pop" />)}
      {fila(6, 870, '3', 'Pasas a recogerlo', <Im src="g_bolsa" x={1800} y={990} w={140} t={p(6)} de="pop" />)}
    </AbsoluteFill>
  );
};

/** La web se cayo el primer dia. */
export const Caida: React.FC<EP> = (ep) => {
  const {t} = ep;
  const tiembla = t < 44 ? Math.sin(t * 1.7) * 6 * (1 - t / 44) : 0;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <T x={960} y={84} op={tr(t, 0, 8)}>
        <Eti tam={30} color={CIAN}>14 de noviembre de 2022 · primer día</Eti>
      </T>
      <div style={{position: 'absolute', inset: 0, transform: `translate(${tiembla}px, ${-tiembla * 0.5}px)`}}>
        <Ventana x={380} y={150} w={1160} h={720} t={t} rot={-1.5} url="primark.com">
          <div style={{position: 'absolute', inset: 0, background: '#F6F7F9', textAlign: 'center'}}>
            <div style={{marginTop: 110, font: "800 150px 'D Sans'", color: '#C5CBD7'}}>:(</div>
            <div style={{marginTop: 26, font: "800 50px 'D Sans'", color: '#1B1D22'}}>No se puede acceder a este sitio</div>
            <div style={{marginTop: 18, font: "500 30px 'D Sans'", color: '#6B7383'}}>La página ha tardado demasiado en responder</div>
            <div style={{margin: '44px auto 0', width: 64, height: 64, borderRadius: 32, border: '8px solid #D5DBE6', borderTopColor: '#0AA5D8', transform: `rotate(${t * 14}deg)`}} />
          </div>
        </Ventana>
      </div>
      <Sello x={1240} y={850} t={t - 22} tam={92} rot={-6}>Se cayó el primer día</Sello>
    </AbsoluteFill>
  );
};

/** Mayo de 2025: recogida en las 187 tiendas de Gran Bretana. */
export const Gb187: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 900, 440, 2.0],
    [dur, 880, 400, 2.2],
  ]);
  const n = Math.min(187, Math.max(0, Math.floor((p(1) + 2) * 2.4)));
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} />
        <svg width={1} height={1} style={{position: 'absolute', overflow: 'visible'}}>
          {PUNTOS.GB.slice(0, n).map((q, i) => {
            const [x, y] = geo(q, MX, MY, MK);
            return <circle key={i} cx={x} cy={y} r={2.6} fill={CIAN} stroke="#0B0C10" strokeWidth={0.5} />;
          })}
        </svg>
      </Mundo>
      <Hoja x={1180} y={200} anio="2025" s={1.1 * pop(t, 12, 1.4)} color="cian" />
      <T x={1310} y={200} ancla="i" op={tr(t, 4, 8)}>
        <Serif tam={84} peso={600}>Mayo</Serif>
      </T>
      <Dato x={1110} y={520} t={p(1)} cifra={String(n)} pie="tiendas de Gran Bretaña: todas" tam={300} ancla="i" />
    </AbsoluteFill>
  );
};

/** El truco: el pedido va donde ya van los camiones, se devuelve en el mostrador y el cliente compra algo mas. */
export const Truco: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const col = (k: number, x: number, txt: React.ReactNode, hijo: React.ReactNode) => (
    <>
      {hijo}
      <Parrafo x={x - 250} y={760} w={500} t={p(k)} tam={42} centro>{txt}</Parrafo>
    </>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit t={t} y={110}>Y aquí está <Am>el truco</Am></Tit>
      {[650, 1270].map((x) => (
        <div key={x} style={{position: 'absolute', left: x, top: 250, width: 2, height: 720, background: 'rgba(255,255,255,0.1)'}} />
      ))}
      {col(1, 340, <>El pedido viaja a un sitio al que <Am>ya manda camiones</Am> todos los días</>, <Im src="g_camion" x={340} y={640} w={520} t={p(1)} de="izq" />)}
      {col(2, 960, <>La devolución se hace <Am>en el mostrador</Am></>, <Im src="g_devolucion" x={960} y={650} w={470} t={p(2)} de="pop" />)}
      {col(
        3,
        1580,
        <>Y el cliente, ya que está dentro, <Am>suele llevarse algo más</Am></>,
        <>
          <Im src="g_compradora" x={1520} y={690} w={230} t={p(3)} de="pop" />
          <Im src="g_bolsa" x={1720} y={690} w={150} t={p(3) - 10} de="pop" />
          <T x={1730} y={380} s={pop(p(3) - 14, 11, 1.8)}>
            <Chip tam={50} color="ambar" tinta="#1B1D22">+</Chip>
          </T>
        </>,
      )}
    </AbsoluteFill>
  );
};

/** Vender por internet sin pagar lo mas caro de vender por internet. */
export const SinPagar: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.06);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Im src="g_furgo" x={1560} y={1090} w={700} t={t - 4} de="der" gris={1} luz={0.6} blur={1.5} z={0.6} cam={cam} />
      <Marca tipo="no" x={1560} y={900} t={p(1) - 6} s={4.4} grosor={8} />
      <Im src="g_bolsa" x={260} y={1180} w={420} t={t - 2} de="izq" z={1.5} blur={2} cam={cam} />
      <Tit x={960} y={330} t={t} tam={124}>Vender por internet</Tit>
      <Tit x={960} y={500} t={p(1)} tam={124} color={AM}>sin pagar lo más caro</Tit>
      <Tit x={960} y={670} t={p(1) - 10} tam={124}>de vender por internet</Tit>
    </AbsoluteFill>
  );
};

// =============================================================== 5 · LO QUE HA CAMBIADO
/** El negocio de siempre ha dejado de crecer solo: -2,6 % en las tiendas que ya tenia; -4,7 % en Europa. */
export const Dejado: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit t={t} y={110} tam={72}>El negocio de siempre ha dejado de <Am>crecer solo</Am></Tit>
      <Im src="g_tienda_p" x={400} y={1140} w={700} t={t - 4} de="aba" cam={cam} />
      <T x={900} y={270} ancla="i" s={pop(p(1), 11, 1.4)}>
        <Chip tam={46} color="verde">Vendió más que nunca…</Chip>
      </T>
      <T x={906} y={352} ancla="i" op={tr(p(2), 0, 8)}>
        <Sans tam={38} peso={600} color="#D5DBE6">…pero únicamente porque abrió tiendas nuevas</Sans>
      </T>
      <Dato x={900} y={560} t={p(3)} cifra="−2,6 %" pie="en las tiendas que ya tenía" tam={230} color="rojo" ancla="i" />
      <Dato x={900} y={880} t={p(4)} cifra="−4,7 %" pie="en Europa continental" tam={170} color="rojo" ancla="i" />
    </AbsoluteFill>
  );
};

/** El beneficio baja un 12 % y el margen, del 11,9 al 10,2 %. */
export const Margen2: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const X = 980;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Im src="g_fajos" x={430} y={1090} w={720} t={t - 2} de="izq" gris={0.35} />
      <Dato x={430} y={300} t={t - 4} cifra="−12 %" pie="de beneficio" tam={230} color="rojo" />
      <T x={X} y={330} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={32} color="#C9CED8">Margen de explotación</Eti>
      </T>
      <T x={X} y={430} ancla="i" op={tr(p(1), 2, 8)}>
        <Sans tam={36} peso={700} color="#D5DBE6">El año pasado</Sans>
      </T>
      <div style={{position: 'absolute', left: X, top: 468, width: 440 * io(tr(p(1), 4, 20)), height: 80, borderRadius: 40, background: 'linear-gradient(90deg,#45D0FF,#0A7BD6)'}} />
      <T x={X + 465} y={508} ancla="i" s={pop(p(1) - 14, 12, 1.4)}>
        <Cifra tam={104} color="cian">11,9 %</Cifra>
      </T>
      <T x={X} y={660} ancla="i" op={tr(p(2), 0, 8)}>
        <Sans tam={36} peso={700} color="#D5DBE6">Este año</Sans>
      </T>
      <div style={{position: 'absolute', left: X, top: 698, width: 377 * io(tr(p(2), 2, 20)), height: 80, borderRadius: 40, background: 'linear-gradient(90deg,#FFD95A,#F29A0B)'}} />
      <T x={X + 402} y={738} ancla="i" s={pop(p(2) - 12, 12, 1.4)}>
        <Cifra tam={104} color="ambar">10,2 %</Cifra>
      </T>
    </AbsoluteFill>
  );
};

/** La prensa apunta a Shein: ropa todavia mas barata, y que llega a casa. */
export const Shein: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const xr = lerp(700, 1250, sal(tr(p(3), 0, 50)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit t={t} y={100} tam={68}>La prensa económica apunta a un nombre</Tit>
      <Detras x={760} y={400} t={p(1)} tam={400}>Shein</Detras>
      <Im src="g_paquete" x={560} y={1090} w={760} t={p(2)} de="izq" />
      <T x={560} y={690} s={pop(p(2) - 6, 12, 1.5)} rot={-3}>
        <Chip tam={52} fondo="#F4F5F7" tinta="#0B0C10">Ropa todavía más barata</Chip>
      </T>
      <Im src="g_casa" x={1640} y={1100} w={470} t={p(3) - 6} de="der" />
      <Im src="g_repartidor" x={xr} y={1100 + paso(p(3))} w={260} t={p(3)} de="nada" />
      <T x={1560} y={330} s={pop(p(3), 12, 1.5)} rot={3}>
        <Chip tam={56} color="ambar" tinta="#1B1D22">…y llega a casa</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Segundo motivo: el grupo separara Primark de la alimentacion y cotizara sola antes de fin de 2027. */
export const Escision: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const a = 1 - tr(p(1), -4, 8);
  const sep = io(tr(p(2), 0, 26));
  const b = 1 - tr(p(4), -4, 8);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <div style={{position: 'absolute', inset: 0, opacity: a}}>
        <Num x={560} y={520} t={t} n="2" tam={300} />
        <Tit x={800} y={520} t={t - 4} ancla="i" tam={130}>Un segundo motivo</Tit>
      </div>
      <div style={{position: 'absolute', inset: 0, opacity: b}}>
        <Hoja x={190} y={170} anio="2026" s={pop(p(1), 12, 1.4)} color="cian" />
        <T x={310} y={140} ancla="i" op={tr(p(1), 4, 8)}>
          <Eti tam={28} color={CIAN}>Abril · anuncio del grupo</Eti>
        </T>
        <T x={306} y={200} ancla="i" op={tr(p(1), 6, 8)}>
          <Serif tam={66} peso={600}>Primark se separa del resto</Serif>
        </T>
        <div style={{position: 'absolute', left: 300 - 60 * sep, top: 420, width: 560, height: 300, borderRadius: 30, background: 'linear-gradient(180deg,#5C6375,#2F3442)', opacity: tr(p(1), 6, 8), boxShadow: '0 30px 60px rgba(0,0,0,0.45)'}}>
          <div style={{font: "800 56px/300px 'D Sans'", color: '#fff', textAlign: 'center'}}>Alimentación</div>
        </div>
        <div style={{position: 'absolute', left: 880 + 240 * sep, top: 420 - 40 * sep, width: 560, height: 300, borderRadius: 30, background: 'linear-gradient(180deg,#45D0FF,#0A7BD6)', opacity: tr(p(1), 10, 8), boxShadow: '0 30px 60px rgba(0,0,0,0.45)'}}>
          <div style={{font: "800 64px/300px 'D Sans'", letterSpacing: 6, color: '#fff', textAlign: 'center'}}>PRIMARK</div>
        </div>
        <Flecha x0={1400} y0={760} x1={1400} y1={900} u={io(tr(p(3), 0, 14))} curva={0} color={AM} grosor={10} trazos={false} />
        <T x={1400} y={960} s={pop(p(3) - 8, 12, 1.4)}>
          <Chip tam={48} color="ambar" tinta="#1B1D22">Cotizará en bolsa por su cuenta</Chip>
        </T>
        <T x={560} y={900} op={tr(p(3), 10, 8)}>
          <Eti tam={30} color="#C9CED8">antes de que acabe 2027</Eti>
        </T>
      </div>
      <Im src="g_tienda_p" x={400} y={1150} w={700} t={p(4) - 2} de="aba" />
      <Parrafo x={800} y={300} w={1020} t={p(4)} tam={78} serif>A una empresa que va a cotizar sola le conviene llegar con <Am>algo más que tiendas</Am></Parrafo>
      <T x={1180} y={840} s={pop(p(5), 12, 1.4)}>
        <Chip tam={44} color="humo">Lectura nuestra, no una frase suya</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Mayo de 2026: su postura sobre el reparto a domicilio no habia cambiado. */
export const Mayo: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Hoja x={190} y={170} anio="2026" s={1.05 * pop(t, 12, 1.4)} color="humo" />
      <T x={320} y={140} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={30} color="#C9CED8">Mayo</Eti>
      </T>
      <T x={316} y={210} ancla="i" op={tr(t, 6, 8)}>
        <Serif tam={84} peso={600}>¿Reparto a domicilio?</Serif>
      </T>
      <Im src="g_furgo" x={960} y={1010} w={1000} t={t - 4} de="der" gris={0.9} luz={0.75} />
      <Sello x={960} y={640} t={p(1)} tam={110} rot={-6} color="#F4F5F7">Postura sin cambios</Sello>
    </AbsoluteFill>
  );
};

/** 10 de septiembre de 2026: Mexico con franquicia y reparto a domicilio en Gran Bretana. Sheffield, fin de 2027. */
export const Anuncio: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const a = 1 - tr(p(3), -4, 8);
  const xf = lerp(2200, 1400, sal(tr(p(2), 0, 40)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Hoja x={190} y={170} anio="2026" s={1.05 * pop(t, 12, 1.4)} color="cian" />
      <T x={320} y={140} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={30} color={CIAN}>10 de septiembre</Eti>
      </T>
      <T x={316} y={210} ancla="i" op={tr(t, 6, 8)}>
        <Serif tam={84} peso={600}>Dos anuncios a la vez</Serif>
      </T>
      <div style={{position: 'absolute', inset: 0, opacity: a}}>
        <T x={480} y={420} s={pop(p(1), 12, 1.4)}>
          <Chip tam={44} color="humo">Entra en México, con franquicia</Chip>
        </T>
        <Im src="g_tienda_p" x={480} y={1090} w={540} t={p(1) - 2} de="aba" />
      </div>
      <Im src="g_nave" x={480} y={990} w={800} t={p(3)} de="izq" />
      <T x={480} y={480} s={pop(p(3) - 4, 12, 1.4)}>
        <Chip tam={42} fondo="#F4F5F7" tinta="#0B0C10">Sheffield · almacén automatizado</Chip>
      </T>
      <T x={1410} y={420} s={pop(p(2), 12, 1.4)}>
        <Chip tam={42} color="cian">Reparto a domicilio en Gran Bretaña</Chip>
      </T>
      <Im src="g_furgo" x={xf} y={1010} w={760} t={p(2)} de="nada" />
      <Im src="g_repartidor" x={1010} y={1040} w={230} t={p(2) - 18} de="pop" />
      <Sello x={1400} y={620} t={p(4)} tam={76} rot={-5} color={CIAN}>Antes de fin de 2027</Sello>
    </AbsoluteFill>
  );
};

/** La explicacion oficial: «el exito de la recogida en tienda nos ha dado la confianza...». */
export const Oficial: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Quien x={110} y={150} t={t} nombre="La explicación oficial" cargo="Comunicado de Primark · 10 de septiembre de 2026" tam={96} />
      <Im src="g_bolsa" x={1570} y={1130} w={560} t={t - 4} de="der" cam={cam} />
      <div style={{position: 'absolute', left: 110, top: 380, width: 1140, font: "700 64px/1.2 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«El éxito de la recogida en tienda nos ha dado la confianza de que *este es el momento adecuado*»." u={p(1) < 0 ? 0 : c01(p(1) / 150)} />
      </div>
    </AbsoluteFill>
  );
};

/** La cuenta de la camiseta no ha cambiado: cambia quien la paga. */
export const QuienPaga: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const b = 1 - tr(p(5), -4, 8);
  const xm = lerp(1160, 1640, io(tr(p(2), 10, 30)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit x={120} y={110} t={t} ancla="i" tam={76}>¿Y la cuenta de la camiseta?</Tit>
      <Im src="g_camiseta_2" x={520} y={900} w={800} t={t - 4} de="izq" />
      <Sello x={520} y={450} t={p(1)} tam={86} rot={-6} color="#F4F5F7">No ha cambiado</Sello>
      <div style={{position: 'absolute', inset: 0, opacity: b}}>
        <Tit x={1400} y={290} t={p(2)} tam={110}>Cambia</Tit>
        <Tit x={1400} y={420} t={p(2) - 6} tam={110} color={AM}>quién la paga</Tit>
        <T x={1160} y={610} s={pop(p(2) - 8, 11, 1.4)}>
          <Chip tam={40} color="humo">Antes: Primark</Chip>
        </T>
        <T x={1640} y={610} s={pop(p(2) - 26, 11, 1.4)}>
          <Chip tam={40} color="cian">Ahora: el cliente</Chip>
        </T>
        <Im src="g_moneda" x={xm} y={790} w={130} t={p(2) - 8} de="pop" rot={(xm - 1160) * 0.7} />
        <T x={1200} y={900} s={pop(p(3), 11, 1.5)} rot={-3}>
          <Chip tam={48} color="ambar" tinta="#1B1D22">Pedido mínimo</Chip>
        </T>
        <T x={1610} y={900} s={pop(p(4), 11, 1.5)} rot={3}>
          <Chip tam={48} color="ambar" tinta="#1B1D22">Envío de pago</Chip>
        </T>
        <T x={1400} y={990} op={tr(p(3), 6, 8)}>
          <Eti tam={24} color="#C9CED8">Según la prensa especializada británica</Eti>
        </T>
      </div>
      <T x={1010} y={300} ancla="i" op={tr(p(5), 0, 8)}>
        <Eti tam={28} color={CIAN}>George Weston sostiene que…</Eti>
      </T>
      <Parrafo x={1010} y={350} w={800} t={p(5)} tam={62}>hoy los clientes ya aceptan pagar <Am>el envío y las devoluciones</Am></Parrafo>
      <Parrafo x={1010} y={690} w={800} t={p(6)} tam={50} color="#D5DBE6">…y con eso se cubre la mayor parte del coste</Parrafo>
    </AbsoluteFill>
  );
};

// =============================================================== CIERRE
/** ¿Y en Espana? De momento, nada: el boton sigue diciendo «ver la disponibilidad». */
export const EspanaHoy: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const b = io(tr(p(3), -4, 14));
  const W = 1260;
  const H = 760;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <T x={960} y={lerp(380, 110, b)} s={lerp(1, 0.5, b)} op={tr(t, 0, 6)}>
        <Serif tam={170} peso={600}>¿Y en España?</Serif>
      </T>
      <Sello x={lerp(960, 1560, b)} y={lerp(600, 120, b)} t={p(1)} tam={lerp(110, 54, b)} rot={-5}>De momento, nada</Sello>
      <T x={960} y={800} s={pop(p(2), 12, 1.4)} op={1 - b}>
        <Chip tam={50} color="humo">El anuncio es solo para Gran Bretaña</Chip>
      </T>
      <Ventana x={330} y={230} w={W} h={H} t={p(3)}>
        <Ficha w={W} h={H - 54} t={p(3)} pulso={p(4)} />
      </Ventana>
    </AbsoluteFill>
  );
};

/** Por que no vendia: cada pedido le costaba dinero; lo comprobo, lo mantuvo y encontro un atajo. */
export const Recap: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const col = (k: number, x: number, txt: string, hijo: React.ReactNode) => (
    <>
      {hijo}
      <Parrafo x={x - 210} y={740} w={420} t={p(k)} tam={44} centro>{txt}</Parrafo>
    </>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit t={t} y={110} tam={72}>Por qué Primark <Am>no vendía</Am> por internet</Tit>
      {col(0, 270, 'A sus precios, cada pedido le costaba dinero', <Im src="g_camiseta_2" x={270} y={640} w={400} t={t - 4} de="pop" />)}
      {col(1, 730, 'Lo comprobó con Asos', <Im src="g_portatil" x={730} y={650} w={380} t={p(1)} de="pop" />)}
      {col(2, 1190, 'Lo mantuvo cuando una pandemia la dejó a cero', <Im src="g_persiana" x={1190} y={660} w={340} t={p(2)} de="pop" />)}
      {col(3, 1650, 'Y encontró un atajo para no pagar el último tramo', <Im src="g_bolsa" x={1650} y={670} w={230} t={p(3)} de="pop" />)}
    </AbsoluteFill>
  );
};

/** No es que la cuenta le salga mejor: es que quedarse quieta ha empezado a salirle peor. */
export const Quieta: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  const u = io(tr(p(1), 4, 30));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Im src="g_tienda_p" x={380} y={1150} w={660} t={t - 2} de="aba" gris={0.6} luz={0.7} cam={cam} />
      <Tit x={1260} y={260} t={t} tam={64} color="#8D93A1">No es que la cuenta le salga mejor</Tit>
      <Parrafo x={800} y={370} w={920} t={p(1)} tam={96} centro serif>Es que <Am>quedarse quieta</Am> ha empezado a salirle peor</Parrafo>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d={`M860,800 L${lerp(860, 1660, u)},${lerp(800, 960, u)}`} stroke="#FF6A5C" strokeWidth={14} strokeLinecap="round" />
        {u > 0.95 && <path d="M1660,960 L1608,926 M1660,960 L1622,996" stroke="#FF6A5C" strokeWidth={14} strokeLinecap="round" />}
      </svg>
    </AbsoluteFill>
  );
};

/** La camiseta sigue costando 2 EUR y llevarla a casa, mas. La diferencia: ese viaje lo vas a pagar tu. */
export const Final: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.08);
  const xf = lerp(2300, 1420, sal(tr(p(1), 0, 50)));
  const b = tr(p(3), -4, 10);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.34} blur={9} />
      <Detras x={600} y={300} t={t} tam={440} op={1 - b}>2 €</Detras>
      <Im src="g_camiseta_2" x={600} y={1070} w={980} t={t - 3} de="aba" cam={cam} />
      <Im src="g_furgo" x={xf} y={1040} w={760} t={p(1)} de="nada" z={1.2} cam={cam} />
      <T x={1400} y={520} s={pop(p(1) - 10, 12, 1.4)} rot={-3} op={1 - b}>
        <Chip tam={48} color="rojo">El viaje cuesta más que la camiseta</Chip>
      </T>
      <T x={1300} y={130} op={tr(p(2), 0, 8)}>
        <Eti tam={26} color="#C9CED8">Si se confirma lo que adelanta la prensa británica…</Eti>
      </T>
      <Tit x={1300} y={280} t={p(3)} tam={120}>ese viaje lo vas</Tit>
      <Tit x={1300} y={430} t={p(3) - 8} tam={150} color={AM}>a pagar tú</Tit>
    </AbsoluteFill>
  );
};

export const PRIMARK2 = {cierre: Cierre, cero: Cero, persianas: Persianas, sector: Sector, weston: Weston, tuit: Tuit, colas: Colas, espana_covid: EspanaCovid, tramo: Tramo, escaparate: Escaparate, recogida: Recogida, caida: Caida, gb187: Gb187, truco: Truco, sin_pagar: SinPagar, dejado: Dejado, margen2: Margen2, shein: Shein, escision: Escision, mayo: Mayo, anuncio: Anuncio, oficial: Oficial, quien_paga: QuienPaga, espana_hoy: EspanaHoy, recap: Recap, quieta: Quieta, final: Final};
