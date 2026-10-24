import React from 'react';
import {useCurrentFrame} from 'remotion';
import {F, GRANDE, L, R, T, ci, rr} from './prim';
import {atras, clamp01, fmt, may, parte, suave} from './util';

/**
 * Los graficos del canal en estilo dibujo: una tarjeta de papel, cifras
 * grandes con contorno de rotulador y barras que crecen con rebote.
 * Las mismas fichas (`grafico`) que ya usan los otros motores.
 */
export type Spec = Record<string, any>;
type P = {spec: Spec; fps: number; epigrafe?: string};

const COL: Record<string, string> = {acento: 'rojo', serie: 'azul', tenue: 'gris', hueso: 'oscuro'};
const col = (v: any, def: string) => (typeof v === 'string' ? COL[v] ?? v : def);

const useT = (retardo: number, fps: number) => {
  const f = useCurrentFrame();
  return f - Math.round(retardo * fps);
};

/** La palabra con el asterisco de acento quitado. */
const limpia = (s: string) => (s || '').replace(/\*/g, '');

const Epigrafe: React.FC<{texto?: string; f: number}> = ({texto, f}) => {
  if (!texto) return null;
  const u = suave(f / 12);
  return (
    <g opacity={u} transform={`translate(0,${(1 - u) * -30})`}>
      <T x={960} y={190} px={74} anchor="middle">{may(limpia(texto))}</T>
      <L d="M600,226 Q960,206 1320,228" c="rojo" w={8} />
    </g>
  );
};

// ------------------------------------------------------------------ contador
export const Contador: React.FC<P> = ({spec, fps, epigrafe}) => {
  const f = useCurrentFrame();
  const t = useT(spec.retardo ?? 0.3, fps);
  const dur = Math.max(18, Math.round(Math.min(spec.duracion ?? 1.8, 2) * fps * 0.7));
  const v = (spec.valor ?? 0) * suave(t / dur);
  const texto = (spec.prefijo ?? '') + fmt(v, spec.dec ?? 0) + (spec.sufijo ?? '');
  const px = texto.length > 9 ? 190 : texto.length > 6 ? 230 : 280;
  const u = atras(t / 14);
  const pie = parte(may(spec.pie || ''), 30);
  const alto = 280 + pie.length * 74;
  const y0 = 560 - alto / 2 + 40;
  return (
    <g>
      <Epigrafe texto={epigrafe} f={f} />
      <g transform={`translate(960,${y0 + alto / 2}) scale(${Math.max(0.01, u)}) rotate(-2)`} opacity={clamp01(t / 5)}>
        <F d={rr(-760, -alto / 2, 1520, alto, 46)} c="blanco" />
        <R d={rr(-720, -alto / 2 + 36, 70, 14, 7)} c="amarillo" />
        <T x={0} y={-alto / 2 + 238} px={px} anchor="middle" c={col(spec.color, 'rojo')} fam={GRANDE}>{texto}</T>
        {pie.map((l, i) => (
          <T key={i} x={0} y={-alto / 2 + 238 + 84 + i * 74} px={62} anchor="middle">{l}</T>
        ))}
      </g>
    </g>
  );
};

// ------------------------------------------------------------------ barras
export const Barras: React.FC<P> = ({spec, fps, epigrafe}) => {
  const f = useCurrentFrame();
  const items: [string, number][] = spec.items || [];
  const n = Math.max(1, items.length);
  const maxV = Math.max(...items.map((i) => i[1]), 1);
  const ancho = Math.min(230, (1500 / n) * 0.62);
  const paso = Math.min(1500 / n, 360);
  const x0 = 960 - (paso * (n - 1)) / 2;
  const base = 880;
  const H = 500;
  const dest = spec.destacar || {};
  const t = useT(spec.retardo ?? 0.3, fps);
  return (
    <g>
      <Epigrafe texto={spec.titulo || epigrafe} f={f} />
      <L d="M200,886 Q960,876 1720,886" w={8} />
      {items.map(([et, v], i) => {
        const u = atras((t - i * 7) / 20, 1.4);
        const h = Math.max(4, (v / maxV) * H * Math.max(0, u));
        const x = x0 + i * paso;
        const c = dest[et] ? col(dest[et], 'rojo') : ['azul', 'verde', 'amarillo', 'morado', 'naranja', 'rosa'][i % 6];
        const lineas = parte(may(et), n > 3 ? 12 : 18);
        const op = clamp01((t - i * 7) / 6);
        return (
          <g key={i} opacity={op}>
            <F d={rr(x - ancho / 2, base - h, ancho, h, 14)} c={c} />
            <T x={x} y={base - h - 24} px={n > 4 ? 56 : 68} anchor="middle" c="blanco" fam={GRANDE}>
              {fmt(v * Math.min(1, Math.max(0, u)), spec.dec ?? 0) + (spec.sufijo ?? '')}
            </T>
            {lineas.map((l, k) => (
              <T key={k} x={x} y={base + 62 + k * 46} px={n > 4 ? 38 : 46} anchor="middle">{l}</T>
            ))}
          </g>
        );
      })}
    </g>
  );
};

// ------------------------------------------------------------------ apilada
const SEG = ['verde', 'rojo', 'azul', 'amarillo', 'morado', 'naranja'];
export const Apilada: React.FC<P> = ({spec, fps, epigrafe}) => {
  const f = useCurrentFrame();
  const items: [string, number][] = spec.items || [];
  const tot = items.reduce((a, i) => a + i[1], 0) || 1;
  const t = useT(spec.retardo ?? 0.3, fps);
  const W = 1500;
  const x0 = 210;
  let acc = 0;
  const colores = spec.colores || {};
  const cs = items.map((it, i) => {
    const m = colores[it[0]];
    return m === 'acento' ? 'rojo' : m === 'tenue' ? 'gris' : m === 'serie' ? 'azul' : SEG[i % SEG.length];
  });
  return (
    <g>
      <Epigrafe texto={epigrafe} f={f} />
      {spec.total && (
        <g opacity={clamp01(t / 8)}>
          <T x={960} y={440} px={92} anchor="middle" fam={GRANDE}>{may(limpia(spec.total))}</T>
        </g>
      )}
      {items.map((it, i) => {
        const w = (it[1] / tot) * W;
        const x = x0 + acc;
        acc += w;
        const u = suave((t - i * 9) / 18);
        return (
          <g key={i}>
            <g opacity={clamp01((t - i * 9) / 4)}>
              <F d={rr(x, 520, Math.max(8, w * u), 170, 18)} c={cs[i]} w={7} />
            </g>
            <g opacity={clamp01((t - i * 9 - 14) / 8)}>
              <T x={x + w / 2} y={780} px={60} anchor="middle" c={cs[i]} fam={GRANDE}>
                {fmt(it[1], spec.dec ?? 0) + (spec.sufijo ?? '')}
              </T>
              {parte(may(it[0]), 16).map((l, k) => (
                <T key={k} x={x + w / 2} y={842 + k * 44} px={40} anchor="middle">{l}</T>
              ))}
            </g>
          </g>
        );
      })}
    </g>
  );
};

// ------------------------------------------------------------------ anillo
export const Anillo: React.FC<P> = ({spec, fps, epigrafe}) => {
  const f = useCurrentFrame();
  const t = useT(spec.retardo ?? 0.3, fps);
  const u = suave(t / 40);
  const max = spec.max ?? 100;
  const frac = clamp01((spec.valor ?? 0) / max) * u;
  const r = 190;
  const circ = 2 * Math.PI * r;
  const pie = parte(may(spec.pie || ''), 30);
  return (
    <g>
      <Epigrafe texto={epigrafe} f={f} />
      <g transform="translate(960,520) rotate(-90)" opacity={clamp01(t / 6)}>
        <circle r={r} fill="none" stroke="#1E1E24" strokeWidth={96} />
        <circle r={r} fill="none" stroke="#FFFFFF" strokeWidth={80} />
        <circle r={r} fill="none" stroke="#F0584A" strokeWidth={80} strokeLinecap="butt" strokeDasharray={`${circ * frac} ${circ}`} />
      </g>
      <T x={960} y={570} px={132} anchor="middle" fam={GRANDE}>{fmt((spec.valor ?? 0) * u, spec.dec ?? 0) + (spec.sufijo ?? '%')}</T>
      {pie.map((l, i) => (
        <g key={i} opacity={clamp01((t - 12) / 8)}>
          <T x={960} y={840 + i * 68} px={58} anchor="middle">{l}</T>
        </g>
      ))}
    </g>
  );
};

// ------------------------------------------------------------------ reparto
export const Reparto: React.FC<P> = ({spec, fps, epigrafe}) => {
  const f = useCurrentFrame();
  const t = useT(spec.retardo ?? 0.3, fps);
  const v = clamp01((spec.valor ?? 0) / 100);
  const u = suave(t / 30);
  const W = 1500;
  const x0 = 210;
  const wa = W * v * u;
  return (
    <g>
      <Epigrafe texto={epigrafe} f={f} />
      <T x={960} y={420} px={170} anchor="middle" c="rojo" fam={GRANDE}>{fmt((spec.valor ?? 0) * u, spec.dec ?? 0) + ' %'}</T>
      <F d={rr(x0, 500, W, 160, 20)} c="blanco" />
      <F d={rr(x0, 500, Math.max(10, wa), 160, 20)} c="rojo" w={7} />
      <g opacity={clamp01((t - 10) / 8)}>
        <T x={x0 + (W * v) / 2} y={740} px={56} anchor="middle" c="rojo" fam={GRANDE}>{may(spec.etiqueta_a || '')}</T>
        <T x={x0 + W * v + (W * (1 - v)) / 2} y={740} px={56} anchor="middle">{may(spec.etiqueta_b || '')}</T>
      </g>
    </g>
  );
};

// ------------------------------------------------------------------ factura
export const Factura: React.FC<P> = ({spec, fps, epigrafe}) => {
  const t = useT(spec.retardo ?? 0.3, fps);
  const lineas: [string, string][] = spec.lineas || [];
  const n = lineas.length;
  const alto = 215 + n * 96 + 170;
  const ancho = 1480;
  const y0 = 90 + (900 - alto) / 2;
  const u = atras(t / 16, 1.1);
  const zig = (y: number) => {
    let d = `M${-ancho / 2},0 H${ancho / 2} V${alto}`;
    for (let x = ancho / 2; x > -ancho / 2; x -= 40) d += ` L${x - 20},${alto - 22} L${x - 40},${alto}`;
    return d + ' Z';
  };
  return (
    <g transform={`translate(960,${y0}) scale(${Math.max(0.01, u)})`} opacity={clamp01(t / 6)}>
      <F d={zig(0)} c="blanco" />
      <T x={0} y={92} px={64} anchor="middle" fam={GRANDE}>{may(limpia(spec.titulo || epigrafe || 'La cuenta'))}</T>
      <L d={`M${-ancho / 2 + 60},128 H${ancho / 2 - 60}`} w={5} op={0.5} />
      {lineas.map(([a, b], i) => {
        const ti = t - 14 - i * 11;
        const op = clamp01(ti / 6);
        return (
          <g key={i} opacity={op} transform={`translate(${(1 - suave(ti / 10)) * -40},0)`}>
            <T x={-ancho / 2 + 70} y={210 + i * 96} px={52} fam={GRANDE}>{may(a)}</T>
            <T x={ancho / 2 - 70} y={208 + i * 96} px={36} anchor="end" c="oscuro" borde={false}>{b}</T>
          </g>
        );
      })}
      <g opacity={clamp01((t - 20 - n * 11) / 8)}>
        <L d={`M${-ancho / 2 + 60},${alto - 190} H${ancho / 2 - 60}`} w={7} />
        <T x={-ancho / 2 + 70} y={alto - 78} px={46} borde={false}>{may(spec.etiqueta_total || 'Total')}</T>
        <T x={ancho / 2 - 70} y={alto - 66} px={124} anchor="end" c="rojo" fam={GRANDE}>{limpia(String(spec.total ?? ''))}</T>
      </g>
    </g>
  );
};

export const GRAFICOS: Record<string, React.FC<P>> = {
  contador: Contador,
  barras: Barras,
  apilada: Apilada,
  anillo: Anillo,
  reparto: Reparto,
  factura: Factura,
};
