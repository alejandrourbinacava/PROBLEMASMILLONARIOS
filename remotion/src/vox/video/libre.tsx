import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, getInputProps} from 'remotion';
import {EP} from './base';
import {Chip, Cifra, Col, Escenario, Eti, Flecha, Hoja, Mapa, Marca, Mundo, PAL, Palabras, Sans, Sello, Serif, T, c01, geo, io, lerp, pop, sal, tr} from './kit';
import {Detras} from './m_capas';
import {MK, MX, MY} from './m_gancho';
import {Im, deriva} from './m_vox';
import {AM, Fondo} from './p_comun';
import {PUNTOS} from './puntos';

/**
 * Plano libre: una composicion por capas escrita entera en el guion tecnico
 * (vox/planos.py). `d.items` es la lista de piezas, de atras a delante. Cada una:
 *
 *   k      tipo (im, tit, par, dato, chip, sello, eti, detras, hoja, si, no, flecha, barra, col,
 *          linea, cita, div, reparto, serie, rejilla, mapa, velo)
 *   p      paso en el que entra (0 = al empezar el plano); dt: fotogramas de retraso
 *   sale   paso en el que se va
 *
 * Los rotulos se encogen solos para caber en su hueco (`max`, o lo que quede hasta el borde), y
 * con `spec.vigia` la escena avisa por consola de lo que se sale del cuadro o se pisa.
 */
export type Item = Record<string, any>;

const Resalta: React.FC<{children: string; color?: string}> = ({children, color = AM}) => (
  <>
    {String(children).split(/(\*[^*]+\*)/g).filter(Boolean).map((x, i) => (x.startsWith('*') ? <span key={i} style={{color}}>{x.slice(1, -1)}</span> : <span key={i}>{x}</span>))}
  </>
);

/** Encoge lo que lleva dentro si es mas ancho que `max`. */
const Cabe: React.FC<{max: number; ancla: 'c' | 'i' | 'd'; children: React.ReactNode}> = ({max, ancla, children}) => {
  const ref = useRef<HTMLDivElement>(null);
  const [k, setK] = useState(1);
  useLayoutEffect(() => {
    const w = ref.current?.offsetWidth ?? 0;
    const q = w > max ? max / w : 1;
    if (Math.abs(q - k) > 0.004) setK(q);
  });
  return (
    <div ref={ref} style={{display: 'inline-block', transform: `scale(${k})`, transformOrigin: ancla === 'c' ? '50% 50%' : ancla === 'd' ? '100% 50%' : '0 50%'}}>{children}</div>
  );
};
const hueco = (x: number, ancla: string) => (ancla === 'c' ? 2 * Math.min(x - 50, 1870 - x) : ancla === 'd' ? x - 50 : 1870 - x);

/** Parrafo en caja: si ocupa mas alto que `alto`, baja el cuerpo. */
const Caja: React.FC<{it: Item; t: number; op: number}> = ({it, t, op}) => {
  const ref = useRef<HTMLDivElement>(null);
  const [tam, setTam] = useState<number>(it.tam ?? 52);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const alto = it.alto ?? 1010 - it.y;
    if (el.scrollHeight > alto && tam > 22) setTam(Math.max(22, Math.floor(tam * 0.94)));
  });
  const w = Math.min(it.w ?? 800, 1870 - it.x);
  return (
    <div ref={ref} data-v={'par:' + String(it.t).slice(0, 24)} data-op={op} style={{position: 'absolute', left: it.x, top: it.y + (1 - sal(t / 12)) * 24, width: w, opacity: c01(t / 6) * op, textAlign: it.centro ? 'center' : 'left', font: `${it.peso ?? (it.serif ? 600 : 700)} ${tam}px/1.18 ${it.serif ? "'M Serif'" : "'D Sans'"}`, color: it.color ?? '#F4F5F7', letterSpacing: it.serif ? -tam * 0.012 : 0}}>
      <Resalta>{it.t}</Resalta>
    </div>
  );
};

/** Cifra que cuenta: si `desde` viene dado, el numero sube o baja hasta su valor. */
const contar = (cifra: string, desde: number | undefined, t: number) => {
  if (desde === undefined) return cifra;
  const m = cifra.match(/-?\d{1,3}(?:\.\d{3})+|\d+(?:,\d+)?/);
  if (!m) return cifra;
  const dec = m[0].includes(',') ? m[0].split(',')[1].length : 0;
  const fin = Number(m[0].replace(/\./g, '').replace(',', '.'));
  const v = desde + (fin - desde) * sal(c01(t / 28));
  const [e, f] = v.toFixed(dec).split('.');
  const s = e.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + (f ? ',' + f : '');
  return cifra.replace(m[0], t >= 28 ? m[0] : s);
};
const CLAROS = ['ambar', 'blanco', 'menta', 'cian'];
const V: React.FC<{n: string; op: number; children: React.ReactNode}> = ({n, op, children}) => (
  <span data-v={n} data-op={op} style={{display: 'inline-block'}}>{children}</span>
);

const Pieza: React.FC<{it: Item; ep: EP; cam: any}> = ({it, ep, cam}) => {
  const {p, dur} = ep;
  const t = p(it.p ?? 0) - (it.dt ?? 0);
  if (t < 0) return null;
  const op = (it.op ?? 1) * (it.sale !== undefined ? 1 - tr(p(it.sale), -4, 8) : 1);
  if (op <= 0) return null;
  const an: 'c' | 'i' | 'd' = it.ancla ?? 'c';
  const x: number = it.x ?? 960;
  const y: number = it.y ?? 540;
  const max: number = it.max ?? hueco(x, an);
  switch (it.k) {
    case 'im': {
      const g = it.grisEn !== undefined ? tr(p(it.grisEn), 0, 14) : 0;
      const m = it.mueve ? io(tr(p(it.mueve.p), it.mueve.dt ?? 0, it.mueve.dur ?? 40)) : 0;
      const bota = it.anda && m > 0 && m < 1 ? Math.abs(Math.sin(t / 4.5)) * -7 : 0;
      return (
        <Im
          src={it.src}
          x={it.mueve ? lerp(x, it.mueve.x ?? x, m) : x}
          y={(it.mueve ? lerp(y, it.mueve.y ?? y, m) : y) + bota}
          w={it.mueve?.w ? lerp(it.w, it.mueve.w, m) : it.w}
          t={t}
          de={it.de ?? 'aba'}
          z={it.z ?? 1}
          blur={it.blur ?? 0}
          luz={(it.luz ?? 1) * (1 - 0.3 * g)}
          gris={Math.max(it.gris ?? 0, 0.9 * g)}
          rot={it.rot ?? 0}
          flip={it.flip}
          cam={it.fijo ? undefined : cam}
          op={op}
        />
      );
    }
    case 'detras':
      return (
        <Detras x={x} y={y} t={t} tam={it.tam ?? 260} color={it.color} ancla={an} op={op}>
          <Cabe max={max} ancla={an}>{it.t}</Cabe>
        </Detras>
      );
    case 'tit':
      return (
        <T x={x} y={y + (1 - sal(t / 12)) * 28} ancla={an} op={c01(t / 6) * op}>
          <Cabe max={max} ancla={an}>
            <V n={'tit:' + it.t} op={op}><Serif tam={it.tam ?? 78} peso={600} color={it.color}><Resalta>{it.t}</Resalta></Serif></V>
          </Cabe>
        </T>
      );
    case 'par':
      return <Caja it={it} t={t} op={op} />;
    case 'dato': {
      const tam = it.tam ?? 170;
      return (
        <>
          <T x={x} y={y} s={pop(t, 12, 1.4)} ancla={an} op={op}>
            <Cabe max={max} ancla={an}>
              <V n={'dato:' + it.cifra} op={op}><Cifra tam={tam} color={(it.color ?? 'ambar') as Col}>{contar(it.cifra, it.desde, t)}</Cifra></V>
            </Cabe>
          </T>
          {it.pie && (
            <T x={x + (an === 'i' ? 8 : an === 'd' ? -8 : 0)} y={y + tam * 0.5 + Math.max(34, tam * 0.22)} ancla={an} op={tr(t, 6, 8) * op}>
              <Cabe max={it.maxPie ?? max} ancla={an}>
                <V n={'pie:' + it.pie} op={op}><Sans tam={it.tamPie ?? Math.max(32, Math.min(46, tam * 0.24))} peso={600} color="#E3E7EE">{it.pie}</Sans></V>
              </Cabe>
            </T>
          )}
        </>
      );
    }
    case 'chip':
      return (
        <T x={x} y={y} s={pop(t, 11, 1.5)} rot={it.rot ?? 0} ancla={an} op={op}>
          <Cabe max={max} ancla={an}>
            <V n={'chip:' + it.t} op={op}><Chip tam={it.tam ?? 46} color={(it.color ?? 'humo') as Col} fondo={it.claro ? '#F4F5F7' : it.fondo} tinta={it.claro || it.color === 'ambar' ? '#14161B' : it.tinta}>{it.t}</Chip></V>
          </Cabe>
        </T>
      );
    case 'sello':
      return (
        <div style={{position: 'absolute', inset: 0, opacity: op}}>
          <Sello x={x} y={y} t={t} tam={it.tam ?? 72} rot={it.rot ?? -5} color={it.color ?? '#FF6A5C'}>
            <Cabe max={max * 0.86} ancla="c"><V n={'sello:' + it.t} op={t > 8 ? op : 0}>{it.t}</V></Cabe>
          </Sello>
        </div>
      );
    case 'eti':
      return (
        <T x={x} y={y} ancla={an} op={tr(t, 0, 8) * op}>
          <Cabe max={max} ancla={an}><V n={'eti:' + it.t} op={op}><Eti tam={it.tam ?? 28} color={it.color ?? '#C9CED8'}>{it.t}</Eti></V></Cabe>
        </T>
      );
    case 'hoja':
      return <Hoja x={x} y={y} anio={String(it.t)} s={(it.s ?? 1) * pop(t, 12, 1.4)} op={op} color={(it.color ?? 'rojo') as Col} tam={it.tam ?? (String(it.t).length > 4 ? 40 : 54)} />;
    case 'si':
    case 'no':
      return <Marca tipo={it.k} x={x} y={y} t={t} s={it.s ?? 4} grosor={it.grosor ?? 8} op={op} />;
    case 'flecha':
      return (
        <div style={{opacity: op}}>
          <Flecha x0={it.x0} y0={it.y0} x1={it.x1} y1={it.y1} u={io(tr(t, 0, it.dur ?? 20))} curva={it.curva ?? 0} color={it.color ?? AM} grosor={it.grosor ?? 10} trazos={it.trazos ?? false} />
        </div>
      );
    case 'barra': {
      const w = Math.max(0, it.w * io(tr(t, 0, 20)));
      const col = (it.color ?? 'ambar') as Col;
      const [c1, c2] = PAL[col];
      const h = it.h ?? 76;
      return (
        <div style={{position: 'absolute', left: x, top: y, width: it.total ?? it.w, height: h, borderRadius: h / 2, background: it.total ? 'linear-gradient(180deg,#343B4C,#222733)' : undefined, opacity: op, overflow: 'hidden', boxShadow: '0 16px 36px rgba(0,0,0,0.4)'}}>
          <div style={{width: w, height: h, borderRadius: it.total ? 0 : h / 2, background: `linear-gradient(180deg,${c1},${c2})`, overflow: 'hidden'}}>
            {it.t && <div style={{font: `800 ${h * 0.4}px/${h}px 'D Sans'`, color: CLAROS.includes(col) ? '#14161B' : '#fff', paddingLeft: 28, whiteSpace: 'nowrap'}}>{it.t}</div>}
          </div>
        </div>
      );
    }
    case 'col': {
      const h = it.alto * io(tr(t, 0, 22));
      const [c1, c2] = PAL[(it.color ?? 'cian') as Col];
      const w = it.w ?? 200;
      const tam = it.tam ?? 76;
      const mx = it.max ?? w * 1.5;
      return (
        <div style={{opacity: op}}>
          <div style={{position: 'absolute', left: x - w / 2, top: y - h, width: w, height: h, borderRadius: 14, background: `linear-gradient(180deg,${c1},${c2})`, boxShadow: '0 20px 44px rgba(0,0,0,0.4)'}} />
          <T x={x} y={y - it.alto - tam * 0.62} s={pop(t - 10, 12, 1.4)}>
            <Cabe max={mx} ancla="c"><V n={'col:' + it.t} op={op}><span style={{font: `${tam}px/1 'M Black'`, color: '#F4F5F7', whiteSpace: 'nowrap', textShadow: '0 6px 18px rgba(0,0,0,0.6)'}}>{it.t}</span></V></Cabe>
          </T>
          {it.pie && (
            <T x={x} y={y + 44} op={tr(t, 4, 8)}>
              <Cabe max={mx} ancla="c"><V n={'cpie:' + it.pie} op={op}><Eti tam={it.tamPie ?? 26} color="#D5DBE6">{it.pie}</Eti></V></Cabe>
            </T>
          )}
        </div>
      );
    }
    case 'linea': {
      const tam = it.tam ?? 50;
      return (
        <>
          <T x={x} y={y} s={pop(t, 11, 1.6)} op={op}>
            <span style={{font: `${tam * 0.98}px/1 'M Black'`, color: it.color ?? '#FFD95A'}}>{it.marca ?? '•'}</span>
          </T>
          <T x={x + tam * 0.95} y={y} ancla="i" op={tr(t, 3, 8) * op}>
            <Cabe max={it.max ?? 1870 - x - tam * 0.95} ancla="i"><V n={'linea:' + it.t} op={op}><Sans tam={tam} peso={700}><Resalta>{it.t}</Resalta></Sans></V></Cabe>
          </T>
        </>
      );
    }
    case 'cita': {
      // entra con la voz: desde su paso hasta el paso `hasta` (o el final del plano)
      const fin = it.hasta !== undefined ? p(it.p ?? 0) - p(it.hasta) : p(it.p ?? 0) - ep.t + dur - 10;
      return (
        <div data-v={'cita:' + String(it.t).slice(0, 20)} data-op={op} style={{position: 'absolute', left: x, top: y, width: it.w ?? 1100, font: `700 ${it.tam ?? 68}px/1.18 'D Sans'`, color: '#F4F5F7', opacity: op}}>
          <Palabras texto={it.t} u={c01(t / Math.max(20, Math.abs(fin) * 0.8))} />
        </div>
      );
    }
    case 'div':
      return <div style={{position: 'absolute', left: x, top: y, width: it.w ?? 2, height: it.h ?? 720, background: 'rgba(255,255,255,0.14)', opacity: tr(t, 0, 8) * op}} />;
    case 'reparto': {
      const u = io(tr(t, 0, 20));
      const tot = it.partes.reduce((a: number, b: any) => a + b.v, 0);
      const h = it.h ?? 92;
      return (
        <div style={{position: 'absolute', left: x, top: y, width: it.w * u, height: h, borderRadius: h / 2, overflow: 'hidden', display: 'flex', opacity: op, boxShadow: '0 20px 44px rgba(0,0,0,0.45)'}}>
          {it.partes.map((q: any, i: number) => {
            const col = (q.color ?? 'humo') as Col;
            const [c1, c2] = PAL[col];
            return (
              <div key={i} style={{width: (it.w * q.v) / tot, flexShrink: 0, height: h, background: `linear-gradient(180deg,${c1},${c2})`, font: `800 ${h * 0.32}px/${h}px 'D Sans'`, color: CLAROS.includes(col) ? '#14161B' : '#fff', textAlign: 'center', whiteSpace: 'nowrap', overflow: 'hidden'}}>{q.t ?? ''}</div>
            );
          })}
        </div>
      );
    }
    case 'serie': {
      // lineas en el tiempo. series: [{v: [...], color, t}], ejes: etiquetas del eje x
      const w = it.w;
      const h = it.h;
      const mx = it.maximo ?? Math.max(...it.series.flatMap((s: any) => s.v));
      const mn = it.minimo ?? 0;
      const D = it.dur ?? 60;
      const u = io(tr(t, 0, D));
      const Y = (v: number) => y - (h * (v - mn)) / (mx - mn);
      return (
        <div style={{opacity: op}}>
          <svg width={1920} height={1080} style={{position: 'absolute', overflow: 'visible'}}>
            <path d={`M${x},${y} L${x + w},${y}`} stroke="rgba(255,255,255,0.28)" strokeWidth={4} />
            {it.series.map((s: any, i: number) => {
              const n = s.v.length;
              const P = s.v.map((v: number, j: number) => [x + (w * j) / (n - 1), Y(v)]);
              const hasta = u * (n - 1);
              const q = Math.floor(hasta);
              const pts = P.slice(0, q + 1);
              if (q < n - 1) pts.push([lerp(P[q][0], P[q + 1][0], hasta - q), lerp(P[q][1], P[q + 1][1], hasta - q)]);
              const c = PAL[(s.color ?? 'cian') as Col][0];
              const f = pts[pts.length - 1];
              return (
                <g key={i}>
                  <polyline points={pts.map((a: number[]) => a.join(',')).join(' ')} fill="none" stroke={c} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" />
                  <circle cx={f[0]} cy={f[1]} r={14} fill="#fff" stroke={c} strokeWidth={6} />
                </g>
              );
            })}
          </svg>
          {(it.ejes ?? []).map((e: string, j: number) => (
            <T key={j} x={x + (w * j) / (it.ejes.length - 1)} y={y + 40} op={tr(t, 4, 8)}>
              <Eti tam={24} color="#C9CED8">{e}</Eti>
            </T>
          ))}
          {it.series.map((s: any, i: number) =>
            s.t ? (
              <T key={'t' + i} x={x + w + 30} y={Y(s.v[s.v.length - 1]) + (s.dy ?? 0)} ancla="i" s={pop(t - D + 6, 12, 1.4)}>
                <Cabe max={1880 - (x + w + 30)} ancla="i"><V n={'serie:' + s.t} op={op}><span style={{font: `${s.tam ?? 52}px/1 'M Black'`, color: PAL[(s.color ?? 'cian') as Col][0]}}>{s.t}</span></V></Cabe>
              </T>
            ) : null,
          )}
        </div>
      );
    }
    case 'rejilla': {
      // n puntos; los `marcados` primeros cambian de color en el paso `pm`
      const s = it.s ?? 30;
      const tm = it.pm !== undefined ? p(it.pm) : -1;
      const c1 = PAL[(it.color ?? 'blanco') as Col][0];
      const c2 = PAL[(it.color2 ?? 'rojo') as Col][0];
      return (
        <svg width={1920} height={1080} style={{position: 'absolute', opacity: op}}>
          {Array.from({length: it.n}, (_, i) => {
            const e = pop(t - i * (it.ritmo ?? 0.06), 8, 1.8);
            const m = i < (it.marcados ?? 0) && tm - i * 0.1 >= 0;
            return <circle key={i} cx={x + (i % it.cols) * s} cy={y + Math.floor(i / it.cols) * s} r={s * 0.36 * Math.max(0, e)} fill={m ? c2 : c1} opacity={m ? 1 : it.marcados && tm >= 0 ? 0.5 : 0.95} />;
          })}
        </svg>
      );
    }
    case 'mapa': {
      const C = {x: it.cx ?? 900, y: it.cy ?? 820, z: (it.z ?? 2.3) * (1 + 0.06 * c01(ep.t / Math.max(1, dur)))};
      const pais: Record<string, string> = it.paises ?? {ESP: 'rojo'};
      const q = it.puntos;
      const n = q ? Math.min(q.n, Math.max(0, Math.floor(p(q.p ?? 0) * (q.n / 45)))) : 0;
      return (
        <AbsoluteFill style={{opacity: op}}>
          <Escenario cam={C} />
          <Mundo cam={C}>
            <Mapa x={MX} y={MY} k={MK} estilo={(c) => (pais[c] ? {fill: PAL[pais[c] as Col][1] + '99', borde: PAL[pais[c] as Col][0]} : undefined)} />
            {n > 0 && (
              <svg width={1} height={1} style={{position: 'absolute', overflow: 'visible'}}>
                {(PUNTOS as any)[q.pais].slice(0, n).map((g: [number, number], i: number) => {
                  const [gx, gy] = geo(g, MX, MY, MK);
                  return <circle key={i} cx={gx} cy={gy} r={q.r ?? 2.4} fill={PAL[(q.color ?? 'ambar') as Col][0]} stroke="#0B0C10" strokeWidth={0.5} />;
                })}
              </svg>
            )}
          </Mundo>
        </AbsoluteFill>
      );
    }
    case 'velo':
      return <AbsoluteFill style={{background: it.color ?? 'rgba(8,9,12,0.55)', opacity: tr(t, 0, 10) * op}} />;
  }
  return null;
};

/** Avisa por consola de los rotulos que se salen del cuadro o se pisan. */
const vigila = (raiz: HTMLDivElement | null) => {
  if (!raiz) return;
  const R: {n: string; x0: number; x1: number; y0: number; y1: number}[] = [];
  raiz.querySelectorAll('[data-v]').forEach((e) => {
    const b = e.getBoundingClientRect();
    if (b.width < 2 || Number((e as HTMLElement).dataset.op ?? 1) < 0.5) return;
    R.push({n: (e as HTMLElement).dataset.v ?? '', x0: b.left, x1: b.right, y0: b.top, y1: b.bottom});
  });
  R.forEach((r) => {
    if (r.x0 < 18 || r.x1 > 1904 || r.y0 < 8 || r.y1 > 1074) console.log(`VIGIA FUERA [${r.n}] x ${Math.round(r.x0)}..${Math.round(r.x1)} y ${Math.round(r.y0)}..${Math.round(r.y1)}`);
  });
  for (let i = 0; i < R.length; i++)
    for (let j = i + 1; j < R.length; j++) {
      const a = R[i];
      const b = R[j];
      const w = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0);
      const h = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
      if (w <= 0 || h <= 0) continue;
      const ar = Math.min((a.x1 - a.x0) * (a.y1 - a.y0), (b.x1 - b.x0) * (b.y1 - b.y0));
      if ((w * h) / ar > 0.1) console.log(`VIGIA PISA [${a.n}] con [${b.n}]`);
    }
};

export const Libre: React.FC<EP> = (ep) => {
  const {d, t, dur} = ep;
  const items: Item[] = d.items ?? [];
  const cam = deriva(t, 0, dur, d.paneo ?? 34, d.empuje ?? 0.055);
  const raiz = useRef<HTMLDivElement>(null);
  const mapa = items.some((i) => i.k === 'mapa');
  useEffect(() => {
    if (!(getInputProps() as any)?.spec?.vigia || !raiz.current) return;
    // se mira un poco despues: los rotulos se encogen en un segundo pase
    const h = delayRender('vigia');
    const reloj = setTimeout(() => {
      vigila(raiz.current);
      continueRender(h);
    }, 60);
    return () => {
      clearTimeout(reloj);
      continueRender(h);
    };
  });
  return (
    <AbsoluteFill ref={raiz}>
      {!mapa && <Fondo ep={ep} luz={d.luz ?? 0.86} blur={d.blur ?? 5} arriba={d.arriba ?? 0.5} abajo={d.abajo ?? 0.4} />}
      {items.map((it, i) => (
        <Pieza key={i} it={it} ep={ep} cam={cam} />
      ))}
    </AbsoluteFill>
  );
};
