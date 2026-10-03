import React from 'react';
import iconos from '../../public/p2/iconos.json';
import {FUERTE, MEDIA, NEGRA, P, T, medir} from './base';
import {clamp01, fmt, may, rgb, suave} from './util';

/**
 * Los siete graficos que usan los planos de plato, portados de
 * `efectos.grafico`. La geometria es la de Pillow (mismos margenes, mismas
 * alturas, mismos tamanos de letra): un plano de Remotion tiene que poder
 * ir al lado de uno de Pillow sin que se note el cambio de motor.
 *
 * `u` va de 0 a 1 a lo largo de la animacion del propio grafico.
 */
export type G = {spec: any; W: number; H: number; u: number; cy: number};

const TINTA = rgb(P.tinta);
const TENUE = rgb(P.tenue);

/** La tarjeta: sombra, cuerpo, contorno de tinta y galon de acento. */
export const Carta: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  radio?: number;
  acento?: number[] | null;
}> = ({x, y, w, h, radio = 32, acento}) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      width: w,
      height: h,
      borderRadius: radio,
      boxSizing: 'border-box',
      background: 'linear-gradient(to bottom, #ffffff, #f8f8f8)',
      border: `3px solid rgba(24,24,28,0.275)`,
      // Pillow: sombra de alfa 36 desplazada 18 px y desenfocada con sigma 18
      boxShadow: '0 18px 36px rgba(0,0,0,0.141)',
    }}
  >
    {acento ? (
      <div
        style={{
          position: 'absolute',
          left: -2,
          top: radio - 7,
          bottom: radio - 7,
          width: 6,
          borderRadius: 3,
          background: rgb(acento, 0.92),
        }}
      />
    ) : null}
  </div>
);

/** Epigrafe en versalitas: el titulo de la tarjeta. */
const Epigrafe: React.FC<{x: number; y: number; txt: string; color?: number[]}> = ({
  x,
  y,
  txt,
  color = P.acento,
}) => (
  <T x={x} y={y} px={29} familia={MEDIA} fill={rgb(color)} op={0.84} esp={5}>
    {txt.toUpperCase()}
  </T>
);

/** Una barra con los cantos redondos. Sobre papel va plana, como impresa. */
const Barra: React.FC<{x0: number; y0: number; x1: number; y1: number; col: number[]}> = ({
  x0,
  y0,
  x1,
  y1,
  col,
}) => {
  const w = Math.max(1, x1 - x0);
  const h = Math.max(1, y1 - y0);
  return <rect x={x0} y={y0} width={w} height={h} rx={Math.min(h / 2, 18)} fill={rgb(col)} opacity={0.97} />;
};

// ---------------------------------------------------------------------------
export const Contador: React.FC<G> = ({spec, W, u, cy}) => {
  const e = suave(clamp01(u));
  const ac = spec._ac as number[];
  const px = spec.px ?? 190;
  const val = spec.valor * e;
  const txt = (spec.prefijo ?? '') + fmt(val, spec.dec ?? 0);
  const sub: string = spec.sufijo ?? '';
  const pie: string = spec.pie ?? '';
  const an = medir(txt, px, NEGRA);
  const pxs = Math.floor(px * 0.32);
  const hueco = sub ? Math.floor(px * 0.11) : 0;
  const ans = sub ? medir(sub, pxs, MEDIA) : 0;
  const ap = pie ? medir(pie.toUpperCase(), 40, MEDIA, 4) : 0;

  const ancho = Math.floor(Math.max(an + hueco + ans, ap) + 170);
  const alto = Math.floor(px * 0.92) + 96 + (pie ? 76 : 0);
  const x0 = (W - ancho) / 2;
  const y0 = cy - alto / 2;
  const base = y0 + 62 + Math.floor(px * 0.7);
  const x = (W - (an + hueco + ans)) / 2;
  const subr = Math.max(4, Math.floor((an + hueco + ans) * e));
  return (
    <>
      <Carta x={x0} y={y0} w={ancho} h={alto} acento={ac} />
      <svg width={W} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <T x={x} y={base} px={px} familia={NEGRA} fill={rgb(ac)}>
          {txt}
        </T>
        {sub && (
          <T x={x + an + hueco} y={base} px={pxs} familia={MEDIA} fill={TINTA} op={0.92}>
            {sub}
          </T>
        )}
        <rect x={x} y={base + 20} width={subr} height={6} rx={3} fill={rgb(ac)} opacity={0.75} />
        {pie && (
          <T x={(W - ap) / 2} y={base + 82} px={40} familia={MEDIA} fill={TENUE} op={0.88} esp={4}>
            {pie.toUpperCase()}
          </T>
        )}
      </svg>
    </>
  );
};

// ---------------------------------------------------------------------------
export const Barras: React.FC<G> = ({spec, W, u, cy}) => {
  const ac = spec._ac as number[];
  const items: [string, number][] = spec.items;
  const mx = Math.max(...items.map((i) => i[1])) || 1;
  const n = items.length;
  const ancho = Math.floor(W * 0.58);
  const x0 = Math.floor((W - ancho) / 2);
  const altoB = 30;
  const hueco = 92;
  const titulo: string = spec.titulo ?? '';
  const alto = (titulo ? 56 : 0) + n * (altoB + hueco) - hueco + 146;
  const y0 = cy - alto / 2;
  let yy = y0 + 76;
  const filas: React.ReactNode[] = [];
  if (titulo) yy += 56;
  items.forEach(([nom, v], i) => {
    const ui = suave(clamp01((u - i * 0.16) / 0.62));
    const col: number[] = spec._destacar && nom in spec._destacar ? spec._destacar[nom] : ac;
    const et = fmt(v * ui, spec.dec ?? 0) + (spec.sufijo ?? '');
    let largo = Math.floor(ancho * (v / mx) * ui);
    // una barra minuscula tiene que VERSE minuscula, no faltar
    if (v > 0 && ui > 0.02) largo = Math.max(6, largo);
    filas.push(
      <g key={i}>
        <T x={x0} y={yy} px={36} familia={MEDIA} fill={TENUE} op={0.92}>
          {may(nom)}
        </T>
        <T x={x0 + ancho} y={yy + 4} px={52} familia={NEGRA} fill={rgb(col)} anchor="end">
          {et}
        </T>
        {largo > 2 && (
          <Barra x0={x0} y0={yy + 24} x1={x0 + Math.max(Math.floor(altoB * 1.9), largo)} y1={yy + 24 + altoB} col={col} />
        )}
      </g>,
    );
    yy += altoB + hueco;
  });
  return (
    <>
      <Carta x={x0 - 60} y={y0} w={ancho + 120} h={alto} acento={ac} />
      <svg width={W} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {titulo && <Epigrafe x={x0} y={y0 + 76} txt={titulo} />}
        {filas}
      </svg>
    </>
  );
};

// ---------------------------------------------------------------------------
export const Anillo: React.FC<G> = ({spec, W, u, cy}) => {
  const e = suave(clamp01(u));
  const ac = spec._ac as number[];
  const val: number = spec.valor;
  const top: number = spec.max ?? 100;
  const r = Math.floor(spec.r ?? 180);
  const cx = Math.floor((spec.x ?? 0.5) * W);
  const gr = 30;
  const pie: string = spec.pie ?? '';
  const ap = pie ? medir(pie.toUpperCase(), 40, MEDIA, 4) : 0;
  const ancho = Math.floor(Math.max(r * 2 + 150, ap + 150));
  const alto = r * 2 + 130 + (pie ? 70 : 0);
  const ang = 360 * (val / top) * e;
  const rad = (a: number) => (a * Math.PI) / 180;
  const pt = (a: number) => [cx + r * Math.cos(rad(a)), cy + r * Math.sin(rad(a))];
  const [x1, y1] = pt(-90);
  const [x2, y2] = pt(-90 + ang);
  const grande = ang > 180 ? 1 : 0;
  const t = fmt(val * e, spec.dec ?? 1) + (spec.sufijo ?? '');
  return (
    <>
      <Carta x={cx - ancho / 2} y={cy - r - 64} w={ancho} h={alto} acento={ac} />
      <svg width={W} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <circle cx={cx} cy={cy} r={r - gr / 2} fill="none" stroke="rgba(24,24,28,0.133)" strokeWidth={gr} />
        <ArcoAnillo cx={cx} cy={cy} r={r - gr / 2} ang={ang} gr={gr} col={ac} />
        <T x={cx} y={cy + Math.floor(r * 0.16)} px={Math.floor(r * 0.46)} familia={NEGRA} fill={rgb(ac)} anchor="middle">
          {t}
        </T>
        {pie && (
          <T x={cx - ap / 2} y={cy + r + 66} px={40} familia={MEDIA} fill={TENUE} op={0.88} esp={4}>
            {pie.toUpperCase()}
          </T>
        )}
      </svg>
    </>
  );
};

/** El arco del anillo con remate redondo en las dos puntas. */
const ArcoAnillo: React.FC<{cx: number; cy: number; r: number; ang: number; gr: number; col: number[]}> = ({
  cx,
  cy,
  r,
  ang,
  gr,
  col,
}) => {
  if (ang <= 0.4) return null;
  const rad = (a: number) => (a * Math.PI) / 180;
  const a1 = -90;
  const a2 = -90 + Math.min(ang, 359.9);
  const p1 = [cx + r * Math.cos(rad(a1)), cy + r * Math.sin(rad(a1))];
  const p2 = [cx + r * Math.cos(rad(a2)), cy + r * Math.sin(rad(a2))];
  return (
    <path
      d={`M ${p1[0]} ${p1[1]} A ${r} ${r} 0 ${ang > 180 ? 1 : 0} 1 ${p2[0]} ${p2[1]}`}
      fill="none"
      stroke={rgb(col)}
      strokeWidth={gr}
      strokeLinecap="round"
    />
  );
};

// ---------------------------------------------------------------------------
export const Reparto: React.FC<G> = ({spec, W, u, cy}) => {
  const e = suave(clamp01(u));
  const ac = spec._ac as number[];
  const colA = spec._color_a as number[];
  const val = spec.valor / 100;
  const ancho = Math.floor(W * 0.6);
  const alto = 76;
  const x0 = Math.floor((W - ancho) / 2);
  const corte = Math.floor(ancho * val * e);
  const t = fmt(spec.valor * e, spec.dec ?? 1) + '%';
  const anT = medir(t, 54, NEGRA);
  const dentro = anT + 44 < corte;
  return (
    <>
      <Carta x={x0 - 60} y={cy - 114} w={ancho + 120} h={alto + 136} acento={ac} />
      <svg width={W} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <T x={x0} y={cy - 46} px={36} familia={MEDIA} fill={TENUE} op={0.92}>
          {may(spec.etiqueta_a ?? '')}
        </T>
        <T x={x0 + ancho} y={cy - 46} px={36} familia={MEDIA} fill={TENUE} op={0.92} anchor="end">
          {may(spec.etiqueta_b ?? '')}
        </T>
        {corte > 2 && <Barra x0={x0} y0={cy - 22} x1={x0 + Math.max(alto, corte)} y1={cy - 22 + alto} col={colA} />}
        {dentro ? (
          <T x={x0 + 26} y={cy + 34} px={54} familia={NEGRA} fill="rgb(12,14,20)">
            {t}
          </T>
        ) : (
          <T x={x0 + Math.max(alto, corte) + 22} y={cy + 34} px={54} familia={NEGRA} fill={rgb(colA)}>
            {t}
          </T>
        )}
      </svg>
    </>
  );
};

// ---------------------------------------------------------------------------
export const Factura: React.FC<G> = ({spec, W, u, cy}) => {
  const ac = spec._ac as number[];
  const lineas: [string, string | number][] = spec.lineas ?? [];
  const ancho = Math.floor(W * 0.58);
  const x0 = Math.floor((W - ancho) / 2);
  const altoL = 62;
  const titulo: string = spec.titulo ?? '';
  const alto = (titulo ? 62 : 22) + lineas.length * altoL + 240;
  const y0 = cy - alto / 2;
  let yy = y0 + 56;
  if (titulo) yy += 40;
  const filas: React.ReactNode[] = [];
  lineas.forEach((par, i) => {
    const nueva = i === lineas.length - 1;
    const ui = nueva ? clamp01((u - 0.16) / 0.4) : 1;
    if (ui > 0.02) {
      const col = nueva ? P.tinta : P.tenue;
      const colI = nueva ? ac : [178, 184, 200];
      const op = (nueva ? 1 : 0.8) * ui;
      const base = yy + 42;
      const impT = typeof par[1] === 'string' ? (par[1] as string) : fmt(par[1] as number, 1);
      const anI = medir(impT, 38, FUERTE);
      let txt = may(par[0]);
      while (medir(txt, 36, MEDIA) > ancho - anI - 80 && txt.length > 4) txt = txt.slice(0, -2);
      const anC = medir(txt, 36, MEDIA);
      const puntos: React.ReactNode[] = [];
      for (let px = x0 + anC + 18; px < x0 + ancho - anI - 18; px += 13) {
        puntos.push(<circle key={px} cx={px + 1.5} cy={base - 9.5} r={1.7} fill={rgb(P.tenue)} opacity={op * 0.5} />);
      }
      filas.push(
        <g key={i}>
          {nueva && <rect x={x0 - 28} y={base - 28} width={6} height={34} rx={3} fill={rgb(ac)} opacity={op} />}
          <T x={x0} y={base} px={36} familia={MEDIA} fill={rgb(col)} op={op}>
            {txt}
          </T>
          <T x={x0 + ancho} y={base} px={38} familia={FUERTE} fill={rgb(colI)} op={op} anchor="end">
            {impT}
          </T>
          {puntos}
        </g>,
      );
    }
    yy += altoL;
  });
  const yt = yy + 24;
  const ut = clamp01((u - 0.55) / 0.4);
  return (
    <>
      <Carta x={x0 - 64} y={y0} w={ancho + 128} h={alto} acento={ac} />
      <svg width={W} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {titulo && <Epigrafe x={x0} y={y0 + 56} txt={titulo} />}
        {filas}
        <line x1={x0} y1={yt} x2={x0 + ancho} y2={yt} stroke="rgba(24,24,28,0.16)" strokeWidth={2} />
        {ut > 0.02 && (
          <>
            <T x={x0} y={yt + 44} px={31} familia={MEDIA} fill={TENUE} op={0.82 * ut} esp={4}>
              {String(spec.etiqueta_total ?? 'llevas gastado').toUpperCase()}
            </T>
            <T x={x0 + ancho} y={yt + 104} px={78} familia={NEGRA} fill={rgb(ac)} op={ut} anchor="end">
              {spec.total ?? ''}
            </T>
          </>
        )}
      </svg>
    </>
  );
};

// ---------------------------------------------------------------------------
export const Apilada: React.FC<G> = ({spec, W, u, cy}) => {
  const ac = spec._ac as number[];
  const items: [string, number][] = spec.items;
  const suma = items.reduce((a, b) => a + b[1], 0) || 1;
  const ancho = Math.floor(W * 0.6);
  const altoB = 54;
  const x0 = Math.floor((W - ancho) / 2);
  const alto = 92 + altoB + 46 + items.length * 54;
  const y0 = cy - alto / 2;
  const yy = y0 + 58;
  const yb = yy + 34;
  const colorDe = (nom: string, i: number) =>
    spec._colores && nom in spec._colores ? spec._colores[nom] : i === 0 ? ac : P.aviso;
  const tramos: React.ReactNode[] = [];
  let cursor = 0;
  items.forEach(([nom, v], i) => {
    const ui = suave(clamp01((u - i * 0.24) / 0.52));
    const largo = ancho * (v / suma) * ui;
    if (largo > 0) {
      tramos.push(<rect key={i} x={x0 + cursor} y={yb} width={largo} height={altoB} fill={rgb(colorDe(nom, i))} opacity={0.97} />);
    }
    cursor += ancho * (v / suma);
  });
  const leyenda: React.ReactNode[] = [];
  let yl = yb + altoB + 42;
  items.forEach(([nom, v], i) => {
    const ui = clamp01((u - 0.26 - i * 0.2) / 0.38);
    if (ui > 0.02) {
      const col = colorDe(nom, i);
      leyenda.push(
        <g key={i} opacity={ui}>
          <rect x={x0} y={yl + 8} width={16} height={16} rx={4} fill={rgb(col)} />
          <T x={x0 + 34} y={yl + 26} px={34} familia={MEDIA} fill={TINTA} op={0.92}>
            {may(nom)}
          </T>
          <T x={x0 + ancho} y={yl + 28} px={42} familia={NEGRA} fill={rgb(col)} anchor="end">
            {fmt(v, spec.dec ?? 2) + (spec.sufijo ?? '')}
          </T>
        </g>,
      );
    }
    yl += 54;
  });
  return (
    <>
      <Carta x={x0 - 64} y={y0} w={ancho + 128} h={alto} acento={ac} />
      <svg width={W} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <defs>
          <clipPath id="pastilla">
            <rect x={x0} y={yb} width={ancho} height={altoB} rx={altoB / 2} />
          </clipPath>
        </defs>
        {spec.total && <Epigrafe x={x0} y={yy} txt={spec.total} color={P.tenue} />}
        <g clipPath="url(#pastilla)">{tramos}</g>
        {leyenda}
      </svg>
    </>
  );
};

// ---------------------------------------------------------------------------
type Prim = any;

/** Un trazo del icono, dibujado progresivamente con stroke-dash. */
const Trazo: React.FC<{p: Prim; w: number; prog: number; col: string}> = ({p, w, prog, col}) => {
  if (prog <= 0.001) return null;
  const comun = {fill: 'none', stroke: col, strokeWidth: w, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const};
  const dash = (len: number) => ({strokeDasharray: len, strokeDashoffset: len * (1 - prog)});
  switch (p.t) {
    case 'l': {
      const pts: number[][] = p.p;
      let len = 0;
      for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      return <polyline points={pts.map((q) => q.join(',')).join(' ')} {...comun} {...dash(len + 1)} />;
    }
    case 'c': {
      if (p.f) return <circle cx={p.cx} cy={p.cy} r={p.r * Math.max(0.2, prog)} fill={col} opacity={prog} />;
      const len = 2 * Math.PI * p.r;
      return (
        <circle
          cx={p.cx}
          cy={p.cy}
          r={p.r - p.w / 2}
          {...comun}
          strokeWidth={p.w}
          {...dash(len)}
          transform={`rotate(-90 ${p.cx} ${p.cy})`}
        />
      );
    }
    case 'r': {
      const len = 2 * (p.w_ + p.h);
      if (p.f) return <rect x={p.x} y={p.y} width={p.w_} height={p.h} rx={p.rx} fill={col} opacity={prog} />;
      return <rect x={p.x} y={p.y} width={p.w_} height={p.h} rx={p.rx} {...comun} strokeWidth={p.w} {...dash(len)} />;
    }
    case 'p':
      return <polygon points={p.p.map((q: number[]) => q.join(',')).join(' ')} fill={col} opacity={prog} />;
    case 'a': {
      const rad = (a: number) => (a * Math.PI) / 180;
      const r = p.r - p.w / 2;
      const a0 = p.a0;
      const a1 = p.a1;
      const sx = p.cx + r * Math.cos(rad(a0));
      const sy = p.cy + r * Math.sin(rad(a0));
      const ex = p.cx + r * Math.cos(rad(a1));
      const ey = p.cy + r * Math.sin(rad(a1));
      const len = r * rad(a1 - a0);
      return (
        <path
          d={`M ${sx} ${sy} A ${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${ex} ${ey}`}
          {...comun}
          strokeWidth={p.w}
          {...dash(len)}
        />
      );
    }
    default:
      return null;
  }
};

export const Ilustracion: React.FC<G> = ({spec, W, u, cy}) => {
  const e = suave(clamp01(u));
  const ac = spec._ac as number[];
  const lado = Math.floor(spec.lado ?? 300);
  const x0 = Math.floor((W - lado) / 2);
  const y0 = cy - Math.floor(lado / 2);
  const cxm = x0 + lado / 2;
  const cym = y0 + lado / 2;
  const rAn = Math.floor(lado * 0.6);
  const m = Math.floor(lado * 0.22);
  const caja = lado - 2 * m;
  const ico = (iconos as any).iconos[spec.icono] ?? (iconos as any).iconos.dato;
  // cada paso entra un poco despues del anterior (como `paso(i)` en Python),
  // pero aqui se DIBUJA el trazo en vez de aparecer de golpe
  const uIco = clamp01(u / 0.92);
  const ang = 360 * e;
  const radA = (a: number) => (a * Math.PI) / 180;
  const dirn: string | undefined = spec.flecha;
  const opF = dirn && u > 0.45 ? Math.min(1, (u - 0.45) / 0.3) : 0;
  const bx = cxm + rAn * 0.74;
  const by = cym - rAn * 0.74;
  const colF = dirn === 'sube' ? P.ok : P.aviso;
  const sg = dirn === 'sube' ? 1 : -1;
  return (
    <>
      <Carta x={x0} y={y0} w={lado} h={lado} radio={lado / 2} acento={null} />
      <svg width={W} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <circle cx={cxm} cy={cym} r={rAn} fill="none" stroke="rgba(24,24,28,0.133)" strokeWidth={5} />
        {e > 0.01 && (
          <>
            <path
              d={`M ${cxm} ${cym - rAn} A ${rAn} ${rAn} 0 ${ang > 180 ? 1 : 0} 1 ${cxm + rAn * Math.cos(radA(-90 + Math.min(ang, 359.9)))} ${cym + rAn * Math.sin(radA(-90 + Math.min(ang, 359.9)))}`}
              fill="none"
              stroke={rgb(ac)}
              strokeWidth={5}
              opacity={0.78}
            />
            <circle
              cx={cxm + rAn * Math.cos(radA(-90 + ang))}
              cy={cym + rAn * Math.sin(radA(-90 + ang))}
              r={7}
              fill={rgb(ac)}
              opacity={0.92}
            />
          </>
        )}
        <g transform={`translate(${x0 + m} ${y0 + m}) scale(${caja / 1000})`}>
          {ico.prims.map((p: Prim, i: number) => {
            // el trazo del paso k empieza en 0.10 + 0.20 k y dura 0.28
            const ini = 0.1 + p.s * 0.2;
            const prog = clamp01((uIco - ini) / 0.28);
            return <Trazo key={i} p={p} w={(iconos as any).grosor} prog={prog} col={TINTA} />;
          })}
        </g>
        {opF > 0 && (
          <g opacity={opF}>
            <circle cx={bx} cy={by} r={38} fill="rgb(255,255,255)" fillOpacity={0.96} stroke={rgb(colF)} strokeWidth={3} />
            <line x1={bx - 15} y1={by + 15 * sg} x2={bx + 15} y2={by - 15 * sg} stroke={rgb(colF)} strokeWidth={6} strokeLinecap="round" />
            <polygon points={`${bx + 21},${by - 21 * sg} ${bx + 2},${by - 17 * sg} ${bx + 17},${by - 2 * sg}`} fill={rgb(colF)} />
          </g>
        )}
        {spec.nota && (
          <T x={W / 2 - medir(String(spec.nota).toUpperCase(), 30, MEDIA, 5) / 2} y={y0 + lado + 78} px={30} familia={MEDIA} fill={TENUE} op={0.84} esp={5}>
            {String(spec.nota).toUpperCase()}
          </T>
        )}
      </svg>
    </>
  );
};

export const GRAFICOS: Record<string, React.FC<G>> = {
  contador: Contador,
  barras: Barras,
  anillo: Anillo,
  reparto: Reparto,
  factura: Factura,
  apilada: Apilada,
  ilustracion: Ilustracion,
};
