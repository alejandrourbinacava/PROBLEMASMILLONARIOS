import React from 'react';
import {Eti, Sans, T, c01, io, pop, tr} from './kit';

/**
 * Piezas comunes de «Por que Chupa Chups vende MAS fuera de Espana que dentro».
 * El color de la marca es el rojo; el acento, el ambar de siempre.
 */
export const ROJO = '#FF6A5C';
export const GRIS = '#C9CED8';

/**
 * Una flor sencilla de ocho petalos que se dibuja a mano (`u` 0..1 el trazo, `relleno` 0..1).
 * Es una margarita generica: NO es el logotipo de la marca ni lleva su rotulo.
 */
export const Flor: React.FC<{x: number; y: number; r: number; u: number; relleno?: number; color?: string; trazo?: string; rot?: number; grosor?: number}> = ({x, y, r, u, relleno = 0, color = '#FFD95A', trazo = '#1B1D22', rot = 0, grosor = 6}) => {
  if (u <= 0) return null;
  const N = 120;
  const pts: string[] = [];
  for (let i = 0; i <= N; i++) {
    const a = (i / N) * Math.PI * 2;
    const rr = r * (0.8 + 0.2 * Math.cos(8 * a));
    pts.push(`${(Math.cos(a) * rr).toFixed(1)},${(Math.sin(a) * rr).toFixed(1)}`);
  }
  return (
    <svg width={1} height={1} style={{position: 'absolute', left: x, top: y, overflow: 'visible', transform: `rotate(${rot}deg)`}}>
      <path d={`M${pts.join('L')}Z`} fill={color} fillOpacity={relleno} stroke={trazo} strokeWidth={grosor} strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - c01(u)} />
    </svg>
  );
};

/** Barra partida en dos: lo que se vende en Espana (gris) y fuera (ambar). `fuera` 0..1; `u` la entrada. */
export const Reparto: React.FC<{x: number; y: number; w: number; h?: number; t: number; fuera: number; etiqueta: string}> = ({x, y, w, h = 84, t, fuera, etiqueta}) => {
  if (t < 0) return null;
  const u = io(tr(t, 0, 18));
  const wf = Math.max(0, w * fuera);
  return (
    <>
      <T x={x} y={y - 34} ancla="i" op={tr(t, 0, 8)}>
        <Eti tam={28} color={GRIS}>{etiqueta}</Eti>
      </T>
      <div style={{position: 'absolute', left: x, top: y, width: w * u, height: h, borderRadius: h / 2, overflow: 'hidden', display: 'flex', boxShadow: '0 20px 44px rgba(0,0,0,0.45)'}}>
        <div style={{width: w - wf, height: h, flexShrink: 0, background: 'linear-gradient(180deg,#5C6375,#2F3442)', font: `800 ${h * 0.36}px/${h}px 'D Sans'`, color: '#fff', paddingLeft: w - wf > 150 ? 26 : 0, whiteSpace: 'nowrap', overflow: 'hidden'}}>{w - wf > 150 ? 'España' : ''}</div>
        <div style={{width: wf, height: h, flexShrink: 0, background: 'linear-gradient(180deg,#FFD95A,#F29A0B)', font: `800 ${h * 0.36}px/${h}px 'D Sans'`, color: '#1B1D22', paddingLeft: wf > 150 ? 26 : 0, whiteSpace: 'nowrap', overflow: 'hidden'}}>{wf > 150 ? 'Fuera de España' : ''}</div>
      </div>
    </>
  );
};

/** Punto de una ciudad sobre el mapa (dentro de <Mundo>): coordenadas del mundo. */
export const Ciudad: React.FC<{x: number; y: number; t: number; nombre: string; lado?: 'i' | 'd'; color?: string; tam?: number}> = ({x, y, t, nombre, lado = 'd', color = '#FFD95A', tam = 13}) =>
  t < 0 ? null : (
    <>
      <svg width={1} height={1} style={{position: 'absolute', left: x, top: y, overflow: 'visible'}}>
        <circle r={5 + 10 * (1 - c01(t / 14))} fill="none" stroke={color} strokeWidth={1.2} opacity={c01(t / 4) * (1 - c01((t - 6) / 18))} />
        <circle r={3.6 * pop(t, 10, 1.6)} fill={color} stroke="#0B0C10" strokeWidth={0.8} />
      </svg>
      <div style={{position: 'absolute', left: lado === 'd' ? x + 8 : undefined, right: lado === 'i' ? 1920 - x + 8 : undefined, top: y - tam * 0.7, font: `800 ${tam}px 'D Sans'`, color: '#F4F5F7', whiteSpace: 'nowrap', opacity: tr(t, 4, 8), textShadow: '0 1px 4px rgba(0,0,0,0.9)'}}>{nombre}</div>
    </>
  );

/** Columna de un grafico de barras verticales con su cifra y su pie. */
export const Columna: React.FC<{x: number; base: number; w?: number; alto: number; t: number; cifra: string; pie: string; color?: string; tam?: number}> = ({x, base, w = 220, alto, t, cifra, pie, color = 'linear-gradient(180deg,#45D0FF,#0A7BD6)', tam = 84}) => {
  if (t < 0) return null;
  const h = alto * io(tr(t, 0, 22));
  return (
    <>
      <div style={{position: 'absolute', left: x - w / 2, top: base - h, width: w, height: h, borderRadius: 14, background: color, boxShadow: '0 20px 44px rgba(0,0,0,0.4)'}} />
      <T x={x} y={base - alto - tam * 0.62} s={pop(t - 12, 12, 1.4)}>
        <span style={{font: `${tam}px 'M Black'`, color: '#F4F5F7', whiteSpace: 'nowrap', textShadow: '0 6px 18px rgba(0,0,0,0.6)'}}>{cifra}</span>
      </T>
      <T x={x} y={base + 44} op={tr(t, 4, 8)}>
        <Eti tam={28} color={GRIS}>{pie}</Eti>
      </T>
    </>
  );
};

/** Linea de una lista: numero o marca a la izquierda y texto. */
export const Linea: React.FC<{x: number; y: number; t: number; children: React.ReactNode; tam?: number; color?: string; marca?: string}> = ({x, y, t, children, tam = 54, color = '#F4F5F7', marca = '•'}) =>
  t < 0 ? null : (
    <>
      <T x={x} y={y} s={pop(t, 11, 1.6)}>
        <span style={{font: `${tam}px 'M Black'`, color: ROJO}}>{marca}</span>
      </T>
      <T x={x + tam * 0.9} y={y} ancla="i" op={tr(t, 3, 8)}>
        <Sans tam={tam} peso={700} color={color}>{children}</Sans>
      </T>
    </>
  );
