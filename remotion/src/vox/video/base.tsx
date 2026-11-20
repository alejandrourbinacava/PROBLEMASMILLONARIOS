import React, {createContext, useContext, useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile} from 'remotion';

/**
 * Base de la piel moderna (formato Moatseek, sin presentador): color de la
 * marca, tipografia gruesa, fichas, tarjetas oscuras. Las reglas de Vox que se
 * quedan: un dato por plano, el dato marcado, la fuente a la vista y cada
 * elemento entrando en su palabra.
 */
export const W = 1920;
export const H = 1080;
export const AMARILLO = '#FFE600';
export const NEGRO = '#0B1410';
export const ROJO = '#FF4D3D';

export type Marca = {nombre: string; color: string; claro: string; oscuro: string; acento: string};
export const MarcaCtx = createContext<Marca>({nombre: 'MARCA', color: '#12B25E', claro: '#1FD877', oscuro: '#053D22', acento: '#FF7A1A'});
export const useMarca = () => useContext(MarcaCtx);

export type Escena = {
  id: string;
  f0: number;
  f1: number;
  tipo: string;
  fondo?: 'marca' | 'oscuro';
  capitulo?: string;
  fuente?: string;
  pasos?: number[];
  d: Record<string, any>;
  /** metraje a sangre detras de la escena (uno o varios clips, con cortes) y el velo que lleva encima */
  fondoClip?: any[];
  velo?: 'plano' | 'oscuro' | 'marca' | 'lado';
  /** recortes (foto o clip) que entran y salen por encima */
  medios?: any[];
  /** franja horizontal [x, ancho] en la que se compone el grafico; el resto queda para los recortes */
  region?: [number, number];
  /** como entra: 'cortinilla' tapa el corte con dos bandas de color */
  trans?: string;
};
export type Spec = {fps: number; total: number; marca: Marca; escenas: Escena[]; medios?: Record<string, string>};
/** Lo que recibe cada tipo de escena. `p(k)` = fotogramas desde que arranco el paso k (negativo si aun no). */
export type EP = {d: Record<string, any>; t: number; dur: number; p: (k: number) => number; ancho: number};

// ---------------------------------------------------------------- fuentes
const CARAS: [string, string][] = [
  ['M Archivo', 'vox/fonts/ArchivoBlack-Regular.ttf'],
  ['M Black', 'vox/fonts/Poppins-Black.ttf'],
  ['M Semi', 'vox/fonts/Poppins-SemiBold.ttf'],
  ['M Medium', 'vox/fonts/Poppins-Medium.ttf'],
  ['M Serif', 'vox/fonts/PlayfairDisplay-VF.ttf'],
];
let cargadas: Promise<void> | null = null;
export const useFuentes = () => {
  const [ok, setOk] = useState(false);
  const [h] = useState(() => delayRender('fuentes video'));
  useEffect(() => {
    if (!cargadas) {
      cargadas = Promise.all(
        CARAS.map(async ([n, r]) => {
          const f = new FontFace(n, `url(${staticFile(r)})`, n === 'M Serif' ? {weight: '400 900'} : {});
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

// ---------------------------------------------------------------- curvas
export const c01 = (u: number) => Math.min(1, Math.max(0, u));
export const suave = (u: number) => 1 - Math.pow(1 - c01(u), 3);
export const expo = (u: number) => (u >= 1 ? 1 : u <= 0 ? 0 : 1 - Math.pow(2, -10 * u));
export const atras = (u: number, k = 1.5) => {
  const x = c01(u) - 1;
  return 1 + (k + 1) * x * x * x + k * x * x;
};
export const miles = (v: number, dec = 0) => {
  const [e, d] = Math.abs(v).toFixed(dec).split('.');
  return (v < 0 ? '-' : '') + e.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + (d ? ',' + d : '');
};

// ---------------------------------------------------------------- piezas comunes
/** Entra desde abajo con un rebase corto. */
export const Sube: React.FC<{t: number; children: React.ReactNode; style?: React.CSSProperties; dy?: number}> = ({t, children, style, dy = 60}) => (
  <div style={{opacity: c01(t / 5), transform: `translateY(${(1 - atras(t / 13)) * dy}px)`, ...style}}>{children}</div>
);
/** Aparece creciendo, con rebote. */
export const Salta: React.FC<{t: number; children: React.ReactNode; style?: React.CSSProperties; k?: number}> = ({t, children, style, k = 2}) => (
  <div style={{opacity: c01(t / 4), transform: `scale(${0.55 + 0.45 * atras(t / 12, k)})`, ...style}}>{children}</div>
);

/** Subrayador: banda bajo la linea base que avanza. */
export const Marcado: React.FC<{u: number; children: React.ReactNode; color?: string; grueso?: number}> = ({u, children, color = AMARILLO, grueso = 16}) => (
  <span style={{backgroundImage: `linear-gradient(${color}, ${color})`, backgroundRepeat: 'no-repeat', backgroundSize: `${c01(u) * 100}% ${grueso}%`, backgroundPosition: '0 96%', padding: '0 4px', margin: '0 -4px', boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone'}}>{children}</span>
);

/**
 * Texto con marcas: *asi* lleva subrayador amarillo (se pinta a partir de
 * `t0`), _asi_ va en el color de acento.
 */
export const Rico: React.FC<{texto: string; t: number; t0?: number; acento?: string}> = ({texto, t, t0 = 8, acento}) => {
  const m = useMarca();
  const trozos = texto.split(/(\*[^*]+\*|_[^_]+_)/g).filter(Boolean);
  let n = 0;
  return (
    <>
      {trozos.map((x, i) => {
        if (x.startsWith('*')) {
          const u = (t - t0 - n++ * 6) / 10;
          return <Marcado key={i} u={u}>{x.slice(1, -1)}</Marcado>;
        }
        if (x.startsWith('_')) return <span key={i} style={{color: acento ?? m.acento}}>{x.slice(1, -1)}</span>;
        return <span key={i}>{x}</span>;
      })}
    </>
  );
};

export const Ficha: React.FC<{t: number; cifra: string; pie: string; color?: string; tinta?: string; ancho?: number; grande?: boolean}> = ({t, cifra, pie, color = 'rgba(255,255,255,0.13)', tinta = '#fff', ancho, grande}) => (
  <div
    style={{
      opacity: c01(t / 4), transform: `scale(${0.6 + 0.4 * atras(t / 12, 2)})`, background: color, color: tinta, borderRadius: 30,
      padding: grande ? '34px 44px 30px' : '26px 36px 24px', width: ancho, minWidth: ancho ? undefined : 300,
      border: '2px solid rgba(255,255,255,0.2)', boxShadow: '0 18px 50px rgba(0,0,0,0.25)',
    }}
  >
    <div style={{font: `${grande ? (cifra.length > 6 ? 78 : cifra.length > 4 ? 90 : 104) : 76}px/1 'M Archivo'`, letterSpacing: -1, whiteSpace: 'nowrap'}}>{cifra}</div>
    <div style={{font: `${grande ? 34 : 28}px/1.2 'M Medium'`, opacity: 0.92, marginTop: 10}}>{pie}</div>
  </div>
);

/** Tarjeta oscura que ocupa casi todo el cuadro. */
export const Tarjeta: React.FC<{t: number; children: React.ReactNode; pad?: string; bajo?: number}> = ({t, children, pad = '54px 70px', bajo = 118}) => (
  <div style={{position: 'absolute', left: 90, top: 150, right: 90, bottom: bajo, borderRadius: 40, background: 'rgba(8,16,12,0.86)', border: '2px solid rgba(255,255,255,0.12)', boxShadow: '0 30px 90px rgba(0,0,0,0.5)', padding: pad, opacity: c01(t / 5), transform: `scale(${0.95 + 0.05 * suave(t / 12)})`}}>
    {children}
  </div>
);

export const Titulo: React.FC<{t: number; children: React.ReactNode; tam?: number; style?: React.CSSProperties}> = ({t, children, tam = 60, style}) => (
  <Sube t={t} style={style}>
    <div style={{font: `${tam}px/1.1 'M Black'`, color: '#fff'}}>{children}</div>
  </Sube>
);

// ---------------------------------------------------------------- fondo
export const Fondo: React.FC<{f: number; oscuro: number}> = ({f, oscuro}) => {
  const m = useMarca();
  return (
    <AbsoluteFill style={{background: NEGRO}}>
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 28% 22%, ${m.claro} 0%, ${m.color} 34%, ${m.oscuro} 100%)`, opacity: 1 - oscuro}} />
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 30% 20%, ${m.oscuro} 0%, ${NEGRO} 72%)`, opacity: oscuro}} />
      <div style={{position: 'absolute', left: 900 + Math.sin(f / 50) * 60, top: 380 + Math.cos(f / 43) * 40, width: 900, height: 900, borderRadius: 450, background: 'rgba(255,255,255,0.11)', filter: 'blur(120px)', opacity: 1 - oscuro * 0.6}} />
      <svg width={W} height={H} style={{position: 'absolute', opacity: 0.12}}>
        <defs>
          <pattern id="malla" width={80} height={80} patternUnits="userSpaceOnUse" patternTransform={`translate(${-(f * 0.5) % 80},0)`}>
            <path d="M80,0V80M0,80H80" stroke="#fff" strokeWidth={1.2} fill="none" />
          </pattern>
        </defs>
        <rect width={W} height={H} fill="url(#malla)" />
      </svg>
    </AbsoluteFill>
  );
};
