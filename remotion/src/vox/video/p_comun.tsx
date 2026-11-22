import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {EP} from './base';
import {Cifra, Col, Eti, Sans, Serif, T, c01, pop, rebote, sal, tr} from './kit';
import {FondoReal} from './m_capas';

/**
 * Piezas comunes de las escenas de «Por que Primark NO vende por internet».
 * Cada plano: metraje o foto real desenfocada al fondo, elementos de foto de
 * estudio grandes (`Im`, de m_vox) y texto grande que entra con la voz.
 */
export const AM = '#FFD95A';
export const CIAN = '#45D0FF';

/** Fondo real desenfocado + velo para asentar texto arriba y elementos abajo. */
export const Fondo: React.FC<{ep: EP; blur?: number; luz?: number; arriba?: number; abajo?: number}> = ({ep, blur = 11, luz = 0.36, arriba = 0.62, abajo = 0.66}) => (
  <>
    <FondoReal ctx={ep.ctx} t={ep.t} dur={ep.dur} blur={blur} luz={luz} />
    <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(8,9,12,${arriba}) 0%, rgba(8,9,12,0) 36%, rgba(8,9,12,0) 62%, rgba(8,9,12,${abajo}) 100%)`}} />
  </>
);

/** Titular en serif. */
export const Tit: React.FC<{x?: number; y?: number; t: number; tam?: number; ancla?: 'c' | 'i' | 'd'; op?: number; color?: string; children: React.ReactNode}> = ({x = 960, y = 120, t, tam = 84, ancla = 'c', op = 1, color, children}) =>
  t < 0 ? null : (
    <T x={x} y={y + (1 - sal(t / 12)) * 28} ancla={ancla} op={c01(t / 6) * op}>
      <Serif tam={tam} peso={600} color={color}>{children}</Serif>
    </T>
  );
export const Am: React.FC<{children: React.ReactNode}> = ({children}) => <span style={{color: AM}}>{children}</span>;

/** Cifra gorda con su pie. */
export const Dato: React.FC<{x: number; y: number; t: number; cifra: React.ReactNode; pie?: React.ReactNode; tam?: number; color?: Col; ancla?: 'c' | 'i' | 'd'; op?: number}> = ({x, y, t, cifra, pie, tam = 170, color = 'cian', ancla = 'c', op = 1}) =>
  t < 0 ? null : (
    <>
      <T x={x} y={y} s={pop(t, 12, 1.4)} ancla={ancla} op={op}>
        <Cifra tam={tam} color={color}>{cifra}</Cifra>
      </T>
      {pie && (
        <T x={x + (ancla === 'i' ? 8 : ancla === 'd' ? -8 : 0)} y={y + tam * 0.5 + Math.max(30, tam * 0.2)} ancla={ancla} op={tr(t, 6, 8) * op}>
          <Sans tam={Math.max(30, Math.min(46, tam * 0.24))} peso={600} color="#D5DBE6">{pie}</Sans>
        </T>
      )}
    </>
  );

/** Texto de varias lineas en una caja de ancho fijo (para frases largas). */
export const Parrafo: React.FC<{x: number; y: number; w: number; t: number; tam?: number; centro?: boolean; color?: string; peso?: number; serif?: boolean; children: React.ReactNode}> = ({x, y, w, t, tam = 44, centro, color = '#F4F5F7', peso = 600, serif, children}) =>
  t < 0 ? null : (
    <div style={{position: 'absolute', left: x, top: y + (1 - sal(t / 12)) * 24, width: w, opacity: c01(t / 6), textAlign: centro ? 'center' : 'left', font: `${peso} ${tam}px/1.22 ${serif ? "'M Serif'" : "'D Sans'"}`, color, letterSpacing: serif ? -tam * 0.012 : 0}}>{children}</div>
  );

/** Ventana de navegador. Dentro, el contenido se coloca en pixeles de la propia ventana. */
export const Ventana: React.FC<{x: number; y: number; w: number; h: number; t: number; url?: string; rot?: number; op?: number; children?: React.ReactNode}> = ({x, y, w, h, t, url = 'primark.com/es-es', rot = 0, op = 1, children}) =>
  t < 0 ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, borderRadius: 22, overflow: 'hidden', background: '#fff', boxShadow: '0 40px 100px rgba(0,0,0,0.62)', transform: `rotate(${rot}deg) scale(${0.72 + 0.28 * rebote(t / 13, 1.05)})`, opacity: c01(t / 4) * op}}>
      <div style={{height: 54, background: '#E4E8EE', display: 'flex', alignItems: 'center', gap: 10, padding: '0 20px'}}>
        {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
          <div key={c} style={{width: 15, height: 15, borderRadius: 8, background: c}} />
        ))}
        <div style={{marginLeft: 18, flex: 1, height: 32, borderRadius: 16, background: '#fff', font: "500 18px/32px 'D Sans'", color: '#5C6375', padding: '0 16px'}}>{url}</div>
      </div>
      <div style={{position: 'relative', width: w, height: h - 54, overflow: 'hidden'}}>{children}</div>
    </div>
  );

const BOTON: React.CSSProperties = {position: 'absolute', height: 74, borderRadius: 37, font: "800 25px/74px 'D Sans'", letterSpacing: 2.2, textAlign: 'center'};
/**
 * La ficha de producto de la web de Primark (hecha a mano: jersey, precio, tallas).
 * `fantasma` 0..1 ensena el boton «anadir a la cesta» que NO existe y `tachado` lo quita;
 * `pulso` hace latir el boton real.
 */
export const Ficha: React.FC<{w: number; h: number; t: number; fantasma?: number; tachado?: number; pulso?: number; precio?: number}> = ({w, h, t, fantasma = 0, tachado = 0, pulso = 0, precio = 0}) => {
  const izq = Math.round(w * 0.44);
  const x0 = izq + 70;
  const an = w - x0 - 70;
  return (
    <>
      <div style={{position: 'absolute', left: 0, top: 0, width: izq, height: h, background: '#EEF0F3'}}>
        <Img src={staticFile('vox/media/g_jersey.webp')} style={{position: 'absolute', height: h * 0.86, left: '50%', top: '7%', transform: `translateX(-50%) scale(${0.9 + 0.1 * sal(t / 30)})`}} />
      </div>
      <div style={{position: 'absolute', left: x0, top: 46, font: "800 30px 'D Sans'", letterSpacing: 9, color: '#0AA5D8'}}>PRIMARK</div>
      <div style={{position: 'absolute', left: x0, top: 112, width: an, font: "600 44px/1.15 'D Sans'", color: '#1B1D22', opacity: tr(t, 6, 8)}}>Jersey con grecas alpinas</div>
      <div style={{position: 'absolute', left: x0, top: 232, font: "800 84px 'D Sans'", color: '#1B1D22', opacity: tr(t, 12, 8), transform: `scale(${1 + 0.16 * Math.sin(c01(precio / 14) * Math.PI)})`, transformOrigin: '0 50%'}}>10,00 €</div>
      <div style={{position: 'absolute', left: x0, top: 372, display: 'flex', gap: 14, opacity: tr(t, 16, 8)}}>
        {['XS', 'S', 'M', 'L', 'XL'].map((s, i) => (
          <div key={s} style={{width: 76, height: 58, borderRadius: 12, border: `3px solid ${i === 2 ? '#1B1D22' : '#C5CBD7'}`, font: "700 24px/52px 'D Sans'", textAlign: 'center', color: '#1B1D22'}}>{s}</div>
        ))}
      </div>
      {fantasma > 0 && (
        <div style={{...BOTON, left: x0, top: 478, width: an, border: '4px dashed #9AA1AE', color: '#6B7383', opacity: fantasma * (1 - 0.72 * tachado), lineHeight: '66px'}}>
          <span style={{textDecoration: tachado > 0.5 ? 'line-through' : 'none', textDecorationThickness: 4}}>AÑADIR A LA CESTA</span>
        </div>
      )}
      <div style={{...BOTON, left: x0, top: 584, width: an, background: '#A8E3F6', color: '#1B1D22', opacity: tr(t, 20, 8), transform: `scale(${1 + 0.05 * Math.sin(c01(pulso / 16) * Math.PI)})`, boxShadow: pulso > 0 ? `0 0 0 ${Math.round(14 * c01(pulso / 10) * (1 - c01((pulso - 16) / 30) * 0.5))}px rgba(69,208,255,0.35)` : undefined}}>VER LA DISPONIBILIDAD</div>
    </>
  );
};

/** Cursor de raton. La punta esta en (x, y). `clic` 0..1 dibuja el anillo del clic. */
export const Cursor: React.FC<{x: number; y: number; clic?: number; op?: number}> = ({x, y, clic = 0, op = 1}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, opacity: op}}>
    {clic > 0 && clic < 1 && <div style={{position: 'absolute', left: -40 * clic - 6, top: -40 * clic - 6, width: 80 * clic + 12, height: 80 * clic + 12, borderRadius: '50%', border: '5px solid #FF5A4D', opacity: 1 - clic}} />}
    <svg width={64} height={78} viewBox="0 0 32 39" style={{position: 'absolute', left: -6, top: -4, filter: 'drop-shadow(0 6px 8px rgba(0,0,0,0.5))'}}>
      <path d="M3,2 L3,29 L10,22.5 L15,35 L20.5,32.8 L15.6,20.6 L25,20.6 Z" fill="#fff" stroke="#111" strokeWidth={2.4} strokeLinejoin="round" />
    </svg>
  </div>
);

const MOVIL_R = 1468 / 869;
/**
 * La mano con el movil (foto de estudio). (x, top) es la esquina de la imagen y `w` su ancho;
 * el brazo sale por abajo, asi que hay que dejar que se salga del cuadro. `children` es la pantalla.
 */
export const Movil: React.FC<{x: number; top: number; w: number; t: number; children?: React.ReactNode}> = ({x, top, w, t, children}) =>
  t < 0 ? null : (
    <div style={{position: 'absolute', left: x, top: top + (1 - rebote(t / 16, 0.6)) * 420, width: w, height: w * MOVIL_R, opacity: c01(t / 4), filter: 'drop-shadow(0 30px 40px rgba(0,0,0,0.6))'}}>
      <Img src={staticFile('vox/media/g_movil.webp')} style={{position: 'absolute', width: w, maxWidth: 'none'}} />
      <div style={{position: 'absolute', left: w * 0.133, top: w * MOVIL_R * 0.022, width: w * 0.428, height: w * MOVIL_R * 0.583, borderRadius: w * 0.05, overflow: 'hidden', background: '#fff'}}>{children}</div>
    </div>
  );

/** Tarjeta de cita sin retrato: quien habla y la frase, que entra palabra a palabra. */
export const Quien: React.FC<{x: number; y: number; t: number; nombre: string; cargo: string; tam?: number}> = ({x, y, t, nombre, cargo, tam = 110}) =>
  t < 0 ? null : (
    <>
      <T x={x} y={y} ancla="i" op={c01(t / 6)}>
        <Serif tam={tam} peso={600}>{nombre}</Serif>
      </T>
      <T x={x + 4} y={y + tam * 0.78} ancla="i" op={tr(t, 5, 8)}>
        <Eti tam={26} color="#C9CED8">{cargo}</Eti>
      </T>
    </>
  );
