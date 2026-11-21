import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {EP, H, W, c01, expo, miles, suave, useMarca} from './base';
import {Metraje} from './capas';
import {EUROPA, EUROPA_H, EUROPA_W} from './europa';

/**
 * COLLAGE POR CAPAS, como los insertos de Moatseek y los de Vox:
 *
 *   fondo oscuro  ->  cifra o anio gigante en hueco  ->  fotos en papel
 *   ->  recorte o silueta protagonista  ->  rotulo
 *
 * Reglas sacadas de mirar el canal fotograma a fotograma:
 *  - hay UN protagonista (un recorte, una silueta de pais, una cifra) que se
 *    queda quieto en su sitio todo el plano;
 *  - las fotos son GRANDES, con reborde blanco de papel, giradas, y entran de
 *    una en una lanzadas desde fuera del cuadro, una cada medio segundo;
 *  - nada se desvanece: entra de golpe y se queda. El plano corta en seco;
 *  - el remate es un cambio de color (las fotos a blanco y negro, el dato en
 *    color), no otro elemento mas.
 */
const SERIF = "'M Serif'";
const SANS = "'D Sans'";
const NEGRA = "'M Archivo'";
const PAPEL = '#F4F1EA';
const TINTA = '#F5F2EA';
const OSCURO = '#101213';
const AMAR = '#FFD23F';
const ROJO = '#E5332A';

const azar = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** Contorno de un papel cortado a mano: un rectangulo con el filo a mordiscos. */
const filo = (w: number, h: number, semilla: number, paso = 34, mordida = 7) => {
  const pts: string[] = [];
  let k = 0;
  const r = () => azar(semilla * 13.7 + k++) * mordida;
  for (let x = 0; x < w; x += paso) pts.push(`${x.toFixed(0)}px ${r().toFixed(1)}px`);
  for (let y = 0; y < h; y += paso) pts.push(`${(w - r()).toFixed(1)}px ${y.toFixed(0)}px`);
  for (let x = w; x > 0; x -= paso) pts.push(`${x.toFixed(0)}px ${(h - r()).toFixed(1)}px`);
  for (let y = h; y > 0; y -= paso) pts.push(`${r().toFixed(1)}px ${y.toFixed(0)}px`);
  return `polygon(${pts.join(',')})`;
};

const DIR: Record<string, [number, number]> = {izq: [-1, 0], der: [1, 0], arr: [0, -1], aba: [0, 1]};

/** Como entra una capa: lanzada desde fuera, frena en seco y asienta el giro. */
const lanzada = (t: number, ts: number, de: string, lejos: number) => {
  const [vx, vy] = DIR[de] ?? [1, 0];
  const u = expo(t / 11);
  const s = Math.pow(c01(ts / 9), 2);
  const k = 1 - u + s * 1.15;
  return {dx: vx * k * lejos, dy: vy * k * lejos, giro: (vx || vy) * (1 - suave(t / 14)) * 7, borr: Math.max(0, 1 - t / 5) * 9 + s * 8};
};

type CapaProps = {x: any; t: number; ts: number; i: number; par: [number, number]; gris: number; ctx: NonNullable<EP['ctx']>};

// ------------------------------------------------------------------ foto en papel
const Papel: React.FC<CapaProps> = ({x, t, ts, i, par, gris, ctx}) => {
  if (t < 0 || ts > 10) return null;
  const [cx, cy, w, h] = x.caja as number[];
  const m = lanzada(t, ts, x.de ?? 'der', Math.max(W, H) * 0.95);
  const b = x.borde ?? 16;
  const z = x.z ?? 1;
  return (
    <div style={{position: 'absolute', left: cx, top: cy, width: w, height: h, transform: `translate(${m.dx + par[0] * z}px, ${m.dy + par[1] * z}px) rotate(${(x.rot ?? 0) + m.giro}deg)`, filter: `drop-shadow(0 18px 30px rgba(0,0,0,0.55))${m.borr > 0.5 ? ` blur(${m.borr}px)` : ''}`}}>
      <div style={{position: 'absolute', inset: 0, background: PAPEL, clipPath: filo(w, h, i + 1)}} />
      <div style={{position: 'absolute', left: b, top: b, right: b, bottom: b, overflow: 'hidden', background: OSCURO}}>
        <div style={{position: 'absolute', inset: 0, transform: `scale(${1.03 + 0.05 * c01(t / 220)})`, filter: `grayscale(${gris}) contrast(${1.04 + 0.12 * gris}) saturate(1.06)`}}>
          <Metraje m={x} abs={ctx.f0 + x.en} dur={x.sale - x.en + 16} fps={ctx.fps} />
        </div>
      </div>
      {x.et && (
        <div style={{position: 'absolute', left: x.etPos === 'der' ? undefined : b + 14 + Math.max(0, 40 - cx), right: x.etPos === 'der' ? b + 14 + Math.max(0, cx + w - W + 40) : undefined, bottom: x.etArriba ? undefined : b + 14 + Math.max(0, cy + h - H + 70), top: x.etArriba ? b + 14 + Math.max(0, 50 - cy) : undefined, background: OSCURO, color: TINTA, font: `700 30px ${SANS}`, letterSpacing: 1.5, textTransform: 'uppercase', padding: '8px 16px', opacity: c01((t - 9) / 6)}}>{x.et}</div>
      )}
    </div>
  );
};

// ------------------------------------------------------------------ recorte con reborde
const Recorte: React.FC<CapaProps> = ({x, t, ts, par, gris}) => {
  if (t < 0 || ts > 10) return null;
  const [cx, cy, w, h] = x.caja as number[];
  const m = lanzada(t, ts, x.de ?? 'aba', 700);
  const z = x.z ?? 1.6;
  const pop = 0.82 + 0.18 * expo(t / 9);
  return (
    <div style={{position: 'absolute', left: cx, top: cy, width: w, height: h, transform: `translate(${m.dx + par[0] * z}px, ${m.dy + par[1] * z}px) rotate(${(x.rot ?? 0) + m.giro * 0.6}deg) scale(${pop})`, filter: `drop-shadow(0 16px 26px rgba(0,0,0,0.6))${m.borr > 0.5 ? ` blur(${m.borr}px)` : ''}`}}>
      <Img src={staticFile('vox/media/' + x.src)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'contain', objectPosition: x.pos ?? 'center', filter: gris > 0.01 ? `grayscale(${gris}) contrast(${1 + 0.15 * gris})` : undefined}} />
    </div>
  );
};

// ------------------------------------------------------------------ silueta de pais en papel
const A3: Record<string, string> = {ES: 'ESP', PT: 'PRT', IT: 'ITA', DE: 'DEU', FR: 'FRA', GB: 'GBR'};
const cacheTrazo: Record<string, {d: string; caja: [number, number, number, number]}> = {};
/** El trazado de un pais sin las islas lejanas (Canarias, Azores, Madeira...). */
const trazo = (cod: string) => {
  if (cacheTrazo[cod]) return cacheTrazo[cod];
  const partes = (EUROPA[cod]?.d ?? '').split('M').filter(Boolean).map((s) => {
    const n = (s.match(/-?\d+(\.\d+)?/g) ?? []).map(Number);
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (let i = 0; i + 1 < n.length; i += 2) {
      x0 = Math.min(x0, n[i]); x1 = Math.max(x1, n[i]); y0 = Math.min(y0, n[i + 1]); y1 = Math.max(y1, n[i + 1]);
    }
    return {s: 'M' + s, x0, y0, x1, y1, a: (x1 - x0) * (y1 - y0)};
  });
  const g = partes.reduce((a, b) => (b.a > a.a ? b : a), partes[0]);
  const lado = Math.max(g.x1 - g.x0, g.y1 - g.y0);
  const cx = (g.x0 + g.x1) / 2;
  const cy = (g.y0 + g.y1) / 2;
  const vale = partes.filter((q) => q === g || (q.a > g.a * 0.004 && Math.hypot((q.x0 + q.x1) / 2 - cx, (q.y0 + q.y1) / 2 - cy) < lado * 0.8));
  const r = {d: vale.map((q) => q.s).join(''), caja: [Math.min(...vale.map((q) => q.x0)), Math.min(...vale.map((q) => q.y0)), Math.max(...vale.map((q) => q.x1)), Math.max(...vale.map((q) => q.y1))] as [number, number, number, number]};
  cacheTrazo[cod] = r;
  return r;
};
const Forma: React.FC<{x: any; t: number; ts: number; par: [number, number]; marca: string; p: (k: number) => number}> = ({x, t, ts, par, marca, p}) => {
  if (t < 0 || ts > 10) return null;
  const paises: string[] = (Array.isArray(x.pais) ? x.pais : [x.pais]).map((c: string) => A3[c] ?? c);
  // caja que encierra a los paises pedidos, a partir de sus trazados
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  paises.forEach((c) => {
    const q = trazo(c).caja;
    x0 = Math.min(x0, q[0]); y0 = Math.min(y0, q[1]); x1 = Math.max(x1, q[2]); y1 = Math.max(y1, q[3]);
  });
  const [cx, cy, w, h] = x.caja as number[];
  const m = 14;
  const k = Math.min(w / (x1 - x0 + 2 * m), h / (y1 - y0 + 2 * m));
  const pop = 0.6 + 0.4 * expo(t / 10);
  const col = (c?: string) => (c === 'amarillo' ? AMAR : c === 'rojo' ? ROJO : c === 'blanco' ? PAPEL : c === 'gris' ? '#5B6064' : marca);
  // el color puede cambiar a mitad de plano: se apaga, se enciende
  const cambio = x.cambia ? suave(p(x.cambia.paso) / 12) : 0;
  return (
    <div style={{position: 'absolute', left: cx, top: cy, width: w, height: h, transform: `translate(${par[0] * (x.z ?? 1.4)}px, ${par[1] * (x.z ?? 1.4)}px) rotate(${x.rot ?? 0}deg) scale(${pop})`, opacity: c01(t / 3) * (1 - c01(ts / 6)), filter: 'drop-shadow(0 16px 26px rgba(0,0,0,0.6))'}}>
      <svg viewBox={`${x0 - m} ${y0 - m} ${x1 - x0 + 2 * m} ${y1 - y0 + 2 * m}`} width={(x1 - x0 + 2 * m) * k} height={(y1 - y0 + 2 * m) * k} style={{position: 'absolute', left: (w - (x1 - x0 + 2 * m) * k) / 2, top: (h - (y1 - y0 + 2 * m) * k) / 2, overflow: 'visible'}}>
        {paises.map((c) => <path key={'b' + c} d={trazo(c).d} fill={PAPEL} stroke={PAPEL} strokeWidth={16 / k} strokeLinejoin="round" />)}
        {paises.map((c, i) => {
          const base = col(Array.isArray(x.color) ? x.color[i] : x.color);
          return (
            <g key={c}>
              <path d={trazo(c).d} fill={base} stroke={PAPEL} strokeWidth={paises.length > 1 ? 3 / k : 0} />
              {cambio > 0 && <path d={trazo(c).d} fill={col(x.cambia.color)} opacity={cambio} />}
            </g>
          );
        })}
        {(x.rotulos ?? []).map((r: any, i: number) => {
          const q = trazo(A3[r.pais] ?? r.pais).caja;
          const tr = p(r.paso ?? x.paso ?? 0);
          const [px, py] = [(q[0] + q[2]) / 2 + (r.dx ?? 0), (q[1] + q[3]) / 2 + (r.dy ?? 0)];
          return (
            <text key={i} x={px} y={py} textAnchor="middle" dominantBaseline="middle" style={{font: `${(r.tam ?? 90) / k}px ${NEGRA}`}} fill={r.color ?? OSCURO} opacity={c01(tr / 5)} transform={`translate(0 ${((1 - expo(tr / 9)) * 20) / k})`}>{r.t}</text>
          );
        })}
      </svg>
    </div>
  );
};

// ------------------------------------------------------------------ rotulos
const Texto: React.FC<{x: any; t: number; ts: number; i: number; par: [number, number]; marca: string}> = ({x, t, ts, i, par, marca}) => {
  if (t < 0 || ts > 8) return null;
  const est = x.estilo ?? 'serif';
  const txt = x.valor !== undefined ? miles(x.valor * expo((t - 2) / 30), x.dec ?? 0) + (x.sufijo ?? '') : x.t;
  const ancla = x.ancla ?? 'c';
  const tr = ancla === 'c' ? 'translate(-50%, -50%)' : ancla === 'd' ? 'translate(-100%, -50%)' : 'translate(0, -50%)';
  const u = expo(t / 9);
  const col = (c?: string) => (c === 'amarillo' ? AMAR : c === 'rojo' ? ROJO : c === 'marca' ? marca : c === 'tinta' ? OSCURO : c ?? TINTA);
  const z = x.z ?? 2;
  const comun: React.CSSProperties = {position: 'absolute', left: x.x, top: x.y, transform: `${tr} translate(${par[0] * z}px, ${par[1] * z + (1 - u) * 34}px) rotate(${x.rot ?? 0}deg) scale(${est === 'papel' || est === 'etiqueta' ? 0.7 + 0.3 * u : 1})`, opacity: c01(t / 4) * (1 - c01(ts / 5)), textAlign: ancla === 'c' ? 'center' : ancla === 'd' ? 'right' : 'left', whiteSpace: 'nowrap'};
  const pie = x.pie && <div style={{font: `700 ${x.tamPie ?? 34}px/1.2 ${SANS}`, letterSpacing: 2, textTransform: 'uppercase', color: est === 'papel' ? '#3A3D40' : col(x.colorPie ?? 'amarillo'), marginTop: 8, whiteSpace: 'normal', maxWidth: x.ancho ?? 660, marginLeft: ancla === 'c' ? 'auto' : undefined, marginRight: ancla === 'c' ? 'auto' : undefined, opacity: c01((t - 6) / 6)}}>{x.pie}</div>;
  if (est === 'papel') {
    // tira de papel con el dato en tinta
    return (
      <div style={{...comun, filter: 'drop-shadow(0 14px 24px rgba(0,0,0,0.55))'}}>
        <div style={{background: x.fondo ? col(x.fondo) : PAPEL, color: col(x.color ?? 'tinta'), padding: `${Math.round((x.tam ?? 110) * 0.16)}px ${Math.round((x.tam ?? 110) * 0.36)}px ${Math.round((x.tam ?? 110) * 0.22)}px`, clipPath: 'polygon(0.6% 3%, 14% 0%, 31% 2.4%, 52% 0.4%, 73% 2.8%, 99.2% 0.6%, 100% 36%, 99% 71%, 99.8% 97%, 78% 99.6%, 55% 97.4%, 30% 100%, 9% 97.6%, 0% 99.2%, 0.9% 62%, 0% 31%)'}}>
          <div style={{font: `${x.serif ? `700 ${x.tam ?? 110}px/1 ${SERIF}` : `${x.tam ?? 110}px/1 ${NEGRA}`}`, letterSpacing: -1, fontVariantNumeric: 'lining-nums'}}>{txt}</div>
          {pie}
        </div>
      </div>
    );
  }
  if (est === 'etiqueta') {
    return (
      <div style={comun}>
        <div style={{background: x.fondo ? col(x.fondo) : OSCURO, color: col(x.color), font: `700 ${x.tam ?? 34}px ${SANS}`, letterSpacing: 2, textTransform: 'uppercase', padding: '9px 18px', boxShadow: '0 10px 24px rgba(0,0,0,0.45)'}}>{txt}</div>
      </div>
    );
  }
  const sombra = '0 6px 40px rgba(0,0,0,0.7), 0 2px 4px rgba(0,0,0,0.5)';
  return (
    <div style={comun}>
      <div style={{font: est === 'negra' ? `${x.tam ?? 150}px/1 ${NEGRA}` : `${x.peso ?? 600} ${x.tam ?? 150}px/1.04 ${SERIF}`, letterSpacing: est === 'negra' ? -2 : -1, color: col(x.color), textShadow: x.sinSombra ? undefined : sombra, fontVariantNumeric: 'lining-nums', fontStyle: x.cursiva ? 'italic' : undefined}}>{txt}</div>
      {pie}
      {void i}
    </div>
  );
};

// ------------------------------------------------------------------ documento
const Doc: React.FC<{x: any; t: number; ts: number; par: [number, number]; p: (k: number) => number}> = ({x, t, ts, par, p}) => {
  if (t < 0 || ts > 10) return null;
  const [cx, cy, w, h] = x.caja as number[];
  const m = lanzada(t, ts, x.de ?? 'aba', 1100);
  const tm = p(x.pasoMarca ?? x.paso);
  return (
    <div style={{position: 'absolute', left: cx, top: cy, width: w, height: h, transform: `translate(${m.dx + par[0] * 1.2}px, ${m.dy + par[1] * 1.2}px) rotate(${(x.rot ?? -1.2) + m.giro * 0.5}deg)`, filter: `drop-shadow(0 26px 40px rgba(0,0,0,0.6))${m.borr > 0.5 ? ` blur(${m.borr}px)` : ''}`}}>
      <div style={{position: 'absolute', inset: 0, background: '#F7F4EC', clipPath: filo(w, h, 91, 46, 5)}} />
      <div style={{position: 'absolute', inset: 0, padding: '50px 64px', color: '#17191B'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: '3px solid #17191B', paddingBottom: 14}}>
          <div style={{font: `800 ${x.tamCab ?? 34}px ${SANS}`}}>{x.cabecera}</div>
          <div style={{font: `600 24px ${SANS}`, color: '#5B6168', letterSpacing: 2}}>{x.fecha}</div>
        </div>
        <div style={{font: `400 ${x.tam ?? 46}px/1.46 ${SERIF}`, marginTop: 32, color: '#24282C'}}>
          {x.antes}{' '}
          <span style={{backgroundImage: 'linear-gradient(#FFE04A, #FFE04A)', backgroundRepeat: 'no-repeat', backgroundPosition: '0 62%', backgroundSize: `${c01(tm / 22) * 100}% 84%`, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone', color: '#111', padding: '0 4px'}}>{x.marca}</span>{' '}
          {x.despues}
        </div>
        {x.pie && <div style={{position: 'absolute', left: 64, bottom: 34, font: `500 20px ${SANS}`, color: '#6B7178', letterSpacing: 1.5}}>{x.pie}</div>}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ el plano
export const Collage: React.FC<EP> = ({d, p, t, dur, ctx}) => {
  const marca = useMarca();
  if (!ctx) return null;
  const u = c01(t / Math.max(1, dur));
  // camara: empuje lento; si se pide, se acerca a un punto a partir de un paso
  let esc = 1 + 0.04 * u;
  let ox = 50;
  let oy = 50;
  if (d.camara) {
    const k = suave(p(d.camara.paso ?? 0) / 26);
    esc = esc + (d.camara.s - 1) * k;
    ox = d.camara.x / 19.2;
    oy = d.camara.y / 10.8;
  }
  const par: [number, number] = [(u - 0.5) * (d.deriva ?? 1) * 22, (u - 0.5) * -8];
  const detras: any[] = d.detras ?? [];
  const media: any[] = ctx.medios ?? [];
  const todas = [...media.map((x) => ({...x, _m: true})), ...(d.capas ?? [])].sort((a, b) => (a.o ?? 0) - (b.o ?? 0));
  const fondo = d.fondo ?? 'oscuro';
  const tGris = d.gris ? p(d.gris.paso) : -1;
  const gris = d.gris ? suave(tGris / 10) : 0;
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: fondo === 'marca' ? `linear-gradient(160deg, ${marca.oscuro} 0%, #04160C 100%)` : fondo === 'azul' ? 'linear-gradient(170deg, #173A8F 0%, #0A1C52 100%)' : fondo === 'clip' ? undefined : OSCURO}}>
      {fondo !== 'clip' && (
        <svg viewBox={`0 0 ${EUROPA_W} ${EUROPA_H}`} style={{position: 'absolute', left: -700 + par[0] * 0.4, top: -900, width: 3400, height: 3400 * (EUROPA_H / EUROPA_W), opacity: fondo === 'oscuro' ? 0.55 : 0.2}}>
          {Object.entries(EUROPA).map(([c, pais]) => <path key={c} d={pais.d} fill={fondo === 'oscuro' ? '#181B1D' : 'rgba(255,255,255,0.12)'} stroke={fondo === 'oscuro' ? '#0B0D0E' : 'rgba(0,0,0,0.25)'} strokeWidth={0.6} />)}
        </svg>
      )}
      <AbsoluteFill style={{transform: `scale(${esc})`, transformOrigin: `${ox}% ${oy}%`}}>
        {/* la cifra o el anio en hueco, detras de todo */}
        {detras.map((x, i) => {
          const te = p(x.paso ?? 0);
          const sig = detras[i + 1];
          const ts = sig ? p(sig.paso) : x.sale !== undefined ? p(x.sale) : -1;
          if (te < 0 || ts > 8) return null;
          const n = String(x.t).length;
          const tam = x.tam ?? (n <= 2 ? 1000 : n <= 4 ? 700 : n <= 6 ? 520 : 400);
          return (
            <div key={i} style={{position: 'absolute', left: (x.x ?? 960) + par[0] * 0.5, top: (x.y ?? 540) + (1 - expo(te / 12)) * 120 - c01(ts / 8) * 120, transform: 'translate(-50%, -50%)', font: `600 ${tam}px/1 ${SERIF}`, letterSpacing: -tam * 0.02, color: 'rgba(255,255,255,0.045)', WebkitTextStroke: '2.5px rgba(255,255,255,0.3)', whiteSpace: 'nowrap', opacity: c01(te / 5) * (1 - c01(ts / 6)), fontVariantNumeric: 'lining-nums'}}>
              {x.t}
            </div>
          );
        })}
        {todas.map((x, i) => {
          if (x._m) {
            const te = t - x.en;
            const ts = t - x.sale;
            const g = x.bn ? 1 : x.color ? 0 : gris;
            return x.k === 'recorte' ? <Recorte key={i} x={x} t={te} ts={ts} i={i} par={par} gris={g} ctx={ctx} /> : <Papel key={i} x={x} t={te} ts={ts} i={i} par={par} gris={g} ctx={ctx} />;
          }
          const te = p(x.paso ?? 0) - (x.mas ?? 0);
          const ts = x.sale !== undefined ? p(x.sale) : -1;
          if (x.k === 'forma') return <Forma key={i} x={x} t={te} ts={ts} par={par} marca={marca.claro} p={p} />;
          if (x.k === 'doc') return <Doc key={i} x={x} t={te} ts={ts} par={par} p={p} />;
          return <Texto key={i} x={x} t={te} ts={ts} i={i} par={par} marca={marca.claro} />;
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
