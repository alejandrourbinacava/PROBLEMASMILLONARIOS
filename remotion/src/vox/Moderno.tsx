import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';

/**
 * Prueba de la PIEL MODERNA (referencia: Moatseek) sobre las reglas de Vox:
 * se ensena la prueba, se marca el dato, la fuente va a la vista y cada capa
 * entra escalonada; pero el acabado es limpio, saturado y con el color de la
 * marca del episodio. Sin presentador: todo el plano es grafico.
 *
 * Tema: «Por que Mercadona NO quiere crecer fuera de Espana».
 * Cifras: resultados anuales de Mercadona, 10 de marzo de 2026.
 */
const W = 1920;
const H = 1080;
const VERDE = '#12B25E';
const VERDE_OSC = '#053D22';
const NARANJA = '#FF7A1A';
const AMARILLO = '#FFE600';
const NEGRO = '#0B1410';

const CARAS: [string, string][] = [
  ['M Archivo', 'vox/fonts/ArchivoBlack-Regular.ttf'],
  ['M Black', 'vox/fonts/Poppins-Black.ttf'],
  ['M Semi', 'vox/fonts/Poppins-SemiBold.ttf'],
  ['M Medium', 'vox/fonts/Poppins-Medium.ttf'],
];
let cargadas: Promise<void> | null = null;
const useFuentes = () => {
  const [ok, setOk] = useState(false);
  const [h] = useState(() => delayRender('fuentes moderno'));
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

const c01 = (u: number) => Math.min(1, Math.max(0, u));
const suave = (u: number) => 1 - Math.pow(1 - c01(u), 3);
const expo = (u: number) => (u >= 1 ? 1 : 1 - Math.pow(2, -10 * c01(u)));
const atras = (u: number, k = 1.5) => {
  const x = c01(u) - 1;
  return 1 + (k + 1) * x * x * x + k * x * x;
};
const miles = (v: number) => Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');

// ---------------------------------------------------------------- piezas
/** Entra desde abajo con rebase; `t` son fotogramas desde su arranque. */
const Sube: React.FC<{t: number; children: React.ReactNode; style?: React.CSSProperties; dy?: number}> = ({t, children, style, dy = 70}) => (
  <div style={{opacity: c01(t / 5), transform: `translateY(${(1 - atras(t / 14)) * dy}px)`, ...style}}>{children}</div>
);

const Ficha: React.FC<{t: number; cifra: string; pie: string; color?: string; tinta?: string; pulso?: number}> = ({t, cifra, pie, color = 'rgba(255,255,255,0.12)', tinta = '#fff', pulso = 0}) => (
  <div
    style={{
      opacity: c01(t / 4), transform: `scale(${(0.6 + 0.4 * atras(t / 12, 2)) * (1 + 0.05 * Math.sin(c01(pulso) * Math.PI))})`,
      background: color, color: tinta, borderRadius: 28, padding: '26px 38px 24px', minWidth: 330,
      border: '2px solid rgba(255,255,255,0.18)', boxShadow: '0 18px 50px rgba(0,0,0,0.25)',
    }}
  >
    <div style={{font: "76px/1 'M Archivo'", letterSpacing: -1}}>{cifra}</div>
    <div style={{font: "28px/1.2 'M Medium'", opacity: 0.9, marginTop: 8}}>{pie}</div>
  </div>
);

const Fuente: React.FC<{t: number; children: React.ReactNode; oscuro?: boolean}> = ({t, children}) => (
  <div style={{position: 'absolute', left: 90, bottom: 54, font: "22px 'M Medium'", letterSpacing: 2.4, textTransform: 'uppercase', color: 'rgba(255,255,255,0.72)', opacity: c01(t / 8)}}>
    {children}
  </div>
);

const Marca: React.FC<{t: number}> = ({t}) => (
  <div style={{position: 'absolute', left: 90, top: 64, display: 'flex', alignItems: 'center', gap: 16, opacity: c01(t / 6), transform: `translateX(${(1 - suave(t / 10)) * -40}px)`}}>
    <div style={{width: 18, height: 18, borderRadius: 9, background: NARANJA}} />
    <div style={{font: "30px 'M Semi'", letterSpacing: 5, color: '#fff'}}>MERCADONA · 2025</div>
  </div>
);

/** Subrayador que avanza por debajo del texto: una banda fina bajo la linea base, sin pisar las letras. */
const Marcado: React.FC<{u: number; children: React.ReactNode; color?: string; grueso?: number}> = ({u, children, color = AMARILLO, grueso = 13}) => (
  <span style={{display: 'inline-block', lineHeight: 1, backgroundImage: `linear-gradient(${color}, ${color})`, backgroundRepeat: 'no-repeat', backgroundSize: `${c01(u) * 100}% ${grueso}%`, backgroundPosition: '0 100%', padding: '0 6px 0.06em', margin: '0 -6px'}}>{children}</span>
);

// ---------------------------------------------------------------- fondo
const Fondo: React.FC<{f: number; oscuro?: boolean}> = ({f, oscuro}) => (
  <AbsoluteFill style={{background: oscuro ? `radial-gradient(ellipse at 30% 20%, #0E3A24 0%, ${NEGRO} 70%)` : `radial-gradient(ellipse at 28% 22%, #1FD877 0%, ${VERDE} 34%, ${VERDE_OSC} 100%)`}}>
    <div style={{position: 'absolute', left: 900 + Math.sin(f / 50) * 60, top: 380 + Math.cos(f / 43) * 40, width: 900, height: 900, borderRadius: 450, background: oscuro ? 'rgba(18,178,94,0.16)' : 'rgba(255,255,255,0.12)', filter: 'blur(120px)'}} />
    <svg width={W} height={H} style={{position: 'absolute', opacity: oscuro ? 0.1 : 0.13}}>
      <defs>
        <pattern id="malla" width={80} height={80} patternUnits="userSpaceOnUse" patternTransform={`translate(${-(f * 0.5) % 80},0)`}>
          <path d="M80,0V80M0,80H80" stroke="#fff" strokeWidth={1.2} fill="none" />
        </pattern>
      </defs>
      <rect width={W} height={H} fill="url(#malla)" />
    </svg>
  </AbsoluteFill>
);

// ---------------------------------------------------------------- escena 1: la cifra
const Escena1: React.FC<{t: number}> = ({t}) => {
  const v = 41858 * expo((t - 8) / 34);
  return (
    <AbsoluteFill>
      <Marca t={t - 2} />
      <div style={{position: 'absolute', left: 90, top: 190, color: '#fff'}}>
        <Sube t={t - 6}>
          <div style={{font: "44px 'M Semi'", opacity: 0.92}}>Vendió en un año</div>
        </Sube>
        <div style={{font: "268px/0.98 'M Archivo'", letterSpacing: -6, marginTop: 6, opacity: c01((t - 8) / 4)}}>
          <Marcado u={(t - 40) / 12}>{miles(v)}</Marcado>
          <span style={{font: "120px 'M Archivo'", letterSpacing: 0, marginLeft: 26}}>M€</span>
        </div>
      </div>
      <div style={{position: 'absolute', left: 90, top: 640, display: 'flex', gap: 30}}>
        <Ficha t={t - 44} cifra="1.672" pie="tiendas" />
        <Ficha t={t - 52} cifra="28,5 %" pie="de la compra en España" />
        <Ficha t={t - 60} cifra="2" pie="países" color={NARANJA} pulso={(t - 74) / 14} />
      </div>
      <Fuente t={t - 20}>Fuente: resultados anuales de Mercadona · 10 de marzo de 2026</Fuente>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- escena 2: el mapa de teselas
const PAISES: [string, number, number][] = [
  ['IS', 0, 0], ['NO', 4, 0], ['SE', 5, 0], ['FI', 6, 0],
  ['IE', 1, 1], ['GB', 2, 1], ['DK', 4, 1], ['EE', 6, 1],
  ['BE', 2, 2], ['NL', 3, 2], ['DE', 4, 2], ['PL', 5, 2], ['LV', 6, 2],
  ['FR', 2, 3], ['LU', 3, 3], ['CZ', 4, 3], ['SK', 5, 3], ['LT', 6, 3],
  ['PT', 0, 4], ['ES', 1, 4], ['CH', 3, 4], ['AT', 4, 4], ['HU', 5, 4], ['RO', 6, 4],
  ['IT', 3, 5], ['SI', 4, 5], ['HR', 5, 5], ['BG', 6, 5],
  ['GR', 5, 6],
];
const Escena2: React.FC<{t: number}> = ({t}) => {
  const L = 112;
  const G = 14;
  return (
    <AbsoluteFill>
      <Marca t={t} />
      <div style={{position: 'absolute', left: 90, top: 180, color: '#fff', width: 760}}>
        <Sube t={t - 4}>
          <div style={{font: "64px/1.08 'M Black'"}}>¿Dónde están esas tiendas?</div>
        </Sube>
        <div style={{font: "430px/0.9 'M Archivo'", marginTop: 26, opacity: c01((t - 46) / 4), transform: `scale(${0.5 + 0.5 * atras((t - 46) / 14, 2.2)})`, transformOrigin: 'left center'}}>
          <Marcado u={(t - 62) / 10}>2</Marcado>
        </div>
        <Sube t={t - 54}>
          <div style={{font: "60px/1.1 'M Black'"}}>países de toda Europa</div>
        </Sube>
      </div>
      <div style={{position: 'absolute', left: 930, top: 140, width: 7 * (L + G), height: 7 * (L + G)}}>
        {PAISES.map(([cod, cx, cy], i) => {
          const es = cod === 'ES' || cod === 'PT';
          const ti = t - 10 - (cx + cy) * 2.2;
          const on = es ? suave((t - 40 - (cod === 'PT' ? 6 : 0)) / 10) : 0;
          return (
            <div
              key={cod}
              style={{
                position: 'absolute', left: cx * (L + G), top: cy * (L + G), width: L, height: L, borderRadius: 22,
                background: es ? `rgba(255,255,255,${0.14 + 0.86 * on})` : 'rgba(255,255,255,0.13)',
                border: '2px solid rgba(255,255,255,0.2)', opacity: c01(ti / 4),
                transform: `scale(${(0.4 + 0.6 * atras(ti / 11, 2)) * (1 + 0.16 * on)})`,
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                color: on > 0.5 ? VERDE_OSC : 'rgba(255,255,255,0.72)', boxShadow: on > 0 ? `0 0 ${50 * on}px rgba(255,255,255,${0.55 * on})` : undefined, zIndex: es ? 2 : 1,
              }}
            >
              <div style={{font: `${es && on > 0.5 ? 26 : 32}px 'M Semi'`, letterSpacing: 2}}>{cod}</div>
              {es && on > 0.5 && <div style={{font: "31px/1 'M Archivo'"}}>{cod === 'ES' ? '1.603' : '69'}</div>}
            </div>
          );
        })}
      </div>
      <Fuente t={t - 16}>Tiendas por país · resultados anuales de Mercadona, marzo de 2026 · mapa esquemático</Fuente>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- escena 3: la tarjeta oscura
const BarraH: React.FC<{t: number; pais: string; valor: number; max: number; color: string}> = ({t, pais, valor, max, color}) => {
  const u = expo(t / 26);
  return (
    <div style={{marginBottom: 46, opacity: c01(t / 4)}}>
      <div style={{font: "36px 'M Semi'", color: 'rgba(255,255,255,0.85)', marginBottom: 12}}>{pais}</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 28}}>
        <div style={{height: 104, width: Math.max(10, (valor / max) * 1180 * u), borderRadius: 18, background: color}} />
        <div style={{font: "104px/1 'M Archivo'", color: '#fff'}}>{miles(valor * u)}</div>
      </div>
    </div>
  );
};
const Escena3: React.FC<{t: number}> = ({t}) => (
  <AbsoluteFill>
    <div style={{position: 'absolute', left: 90, top: 70, right: 90, bottom: 120, borderRadius: 40, background: 'rgba(8,16,12,0.86)', border: '2px solid rgba(255,255,255,0.12)', boxShadow: '0 30px 90px rgba(0,0,0,0.5)', padding: '56px 70px', opacity: c01(t / 5), transform: `scale(${0.94 + 0.06 * suave(t / 12)})`}}>
      <Sube t={t - 4}>
        <div style={{font: "58px 'M Black'", color: '#fff', marginBottom: 40}}>Sus 1.672 tiendas, por país</div>
      </Sube>
      <BarraH t={t - 14} pais="España" valor={1603} max={1603} color={`linear-gradient(90deg, #0E8F4A, #2BE07F)`} />
      <BarraH t={t - 26} pais="Portugal" valor={69} max={1603} color={NARANJA} />
      <div style={{position: 'absolute', right: 70, top: 56, background: AMARILLO, color: NEGRO, borderRadius: 22, padding: '16px 30px', font: "54px 'M Archivo'", opacity: c01((t - 50) / 4), transform: `scale(${0.5 + 0.5 * atras((t - 50) / 12, 2.4)}) rotate(-3deg)`}}>
        96 % en España
      </div>
      <div style={{position: 'absolute', left: 70, bottom: 50, font: "92px/1 'M Black'", color: '#fff', opacity: c01((t - 66) / 5), transform: `translateY(${(1 - atras((t - 66) / 14)) * 60}px)`}}>
        ¿Por qué <Marcado u={(t - 80) / 10} color={NARANJA}>no sale</Marcado> de aquí?
      </div>
    </div>
    <Fuente t={t - 16}>Resultados anuales de Mercadona, marzo de 2026 · porcentaje: cálculo propio</Fuente>
  </AbsoluteFill>
);

// ---------------------------------------------------------------- montaje
const CORTES = [0, 98, 200, 310];
const DUR = 12; // fotogramas del cambio de escena

export const PruebaModerna: React.FC = () => {
  const ok = useFuentes();
  const f = useCurrentFrame();
  if (!ok) return <AbsoluteFill style={{background: VERDE_OSC}} />;
  const escenas = [Escena1, Escena2, Escena3];
  return (
    <AbsoluteFill style={{background: NEGRO, overflow: 'hidden'}}>
      <Fondo f={f} oscuro={f >= CORTES[2] + DUR / 2} />
      {escenas.map((E, i) => {
        const a = CORTES[i];
        const b = CORTES[i + 1];
        if (f < a - 1 || f > b + DUR) return null;
        // entra subiendo desde abajo y sale hacia arriba, con desenfoque de movimiento
        const ent = i === 0 ? 1 : suave((f - a) / DUR);
        const sal = i === escenas.length - 1 ? 0 : Math.pow(c01((f - b) / DUR), 2);
        const dy = (1 - ent) * H * 0.9 - sal * H * 0.9;
        const borr = Math.sin(Math.PI * c01(ent < 1 ? ent : sal)) * 18;
        // empuje lento de camara dentro de cada escena
        const k = 1 + 0.035 * c01((f - a) / (b - a));
        return (
          <AbsoluteFill key={i} style={{transform: `translateY(${dy}px) scale(${k})`, filter: borr > 0.4 ? `blur(${borr}px)` : undefined, opacity: 1 - sal * 0.3}}>
            <E t={f - a} />
          </AbsoluteFill>
        );
      })}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 60%, rgba(0,0,0,0.28) 100%)', pointerEvents: 'none'}} />
    </AbsoluteFill>
  );
};
