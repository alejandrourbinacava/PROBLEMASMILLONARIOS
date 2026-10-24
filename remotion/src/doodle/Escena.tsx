import React, {useContext} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {GRAFICOS} from './Graficos';
import {ESCENAS} from './Escenas';
import type {Cara, Pose} from './Personaje';
import {OBJ} from './Objetos';
import {Ctx, Defs, F, Fondo, GRANDE, L, R, T, TEXTO, ci, color, paleta, poli, rr, useFuentes} from './prim';
import {atras, azar, clamp01, may, parte, suave} from './util';

export type Obj = {o: string; e?: string};
export type PlanoD = {
  id: string;
  frames: number;
  fps?: number;
  objetos: Obj[];
  layout: 'heroe' | 'izq' | 'der' | 'duo' | 'trio';
  simbolo?: string;
  escena?: {id: string; foco?: string; burbuja?: string; cara: Cara; pose: Pose; v: number; tema: string} | null;
  etiqueta?: string;
  titular?: {texto: string; retardo?: number} | null;
  grafico?: Record<string, any> | null;
  epigrafe?: string;
  papel?: string;
  semilla: number;
  camara?: {k0: number; k1: number; dx: number; dy: number};
};

import {Entra, Etiqueta} from './anim';

// ------------------------------------------------------------------ titular
const lineasTitular = (texto: string, maxAncho: number, tamanos = [132, 116, 100, 88, 76]) => {
  // ajusta el cuerpo para que quepa en 3 lineas como mucho
  for (const px of tamanos) {
    const max = Math.floor(maxAncho / (px * 0.52));
    const l = parte(texto, max);
    if (l.length <= (px >= 100 ? 2 : 3)) return {px, l};
  }
  return {px: 70, l: parte(texto, Math.floor(maxAncho / (70 * 0.52)))};
};

const Trozos: React.FC<{linea: string}> = ({linea}) => {
  // *palabra* = acento: rojo con contorno, como un sello
  const partes = linea.split('*');
  return (
    <>
      {partes.map((p, i) =>
        i % 2 === 1 ? (
          <tspan key={i} fill="#F0584A" stroke="#1E1E24" strokeWidth={11} strokeLinejoin="round" paintOrder="stroke">{p}</tspan>
        ) : (
          <tspan key={i}>{p}</tspan>
        ),
      )}
    </>
  );
};

const Titular: React.FC<{texto: string; retardo: number; x: number; y: number; ancho: number; anchor: 'middle' | 'start'; fps: number; tamanos?: number[]}> = ({texto, retardo, x, y, ancho, anchor, fps, tamanos}) => {
  const f = useCurrentFrame();
  const t0 = Math.round(retardo * fps);
  const {px, l} = lineasTitular(may(texto), ancho, tamanos);
  const t = useContext(Ctx);
  const ult = l[l.length - 1].replace(/\*/g, '');
  const wUlt = Math.min(ancho, ult.length * px * 0.5);
  const yb = y + (l.length - 1) * px * 1.12 + 22;
  const xs = anchor === 'middle' ? x - wUlt / 2 : x;
  const draw = suave((f - t0 - l.length * 4 - 6) / 14);
  return (
    <g>
      {l.map((linea, i) => {
        const u = atras((f - t0 - i * 4) / 12, 1.6);
        return (
          <g key={i} opacity={clamp01((f - t0 - i * 4) / 4)} transform={`translate(${x},${y + i * px * 1.12}) scale(${Math.max(0.01, 0.6 + 0.4 * u)}) translate(${-x},${-(y + i * px * 1.12)})`}>
            <text x={x} y={y + i * px * 1.12} fontSize={px} fontFamily={`"${GRANDE}"`} fill={t.tinta} textAnchor={anchor}>
              <Trozos linea={linea} />
            </text>
          </g>
        );
      })}
      <path
        d={`M${xs},${yb} Q${xs + wUlt * 0.25},${yb - 12} ${xs + wUlt * 0.5},${yb + 2} T${xs + wUlt},${yb - 4}`}
        fill="none"
        stroke={t.c.rojo}
        strokeWidth={10}
        strokeLinecap="round"
        strokeDasharray={wUlt * 1.1}
        strokeDashoffset={wUlt * 1.1 * (1 - draw)}
      />
    </g>
  );
};

// ------------------------------------------------------------------ adornos
const ADORNOS = ['estrella', 'chispa', 'circulo', 'mas', 'rayas', 'onda'];
const Adorno: React.FC<{tipo: string; c: string}> = ({tipo, c}) => {
  switch (tipo) {
    case 'estrella':
      return <F d={poli(Array.from({length: 8}).map((_, i) => [Math.round(Math.sin((i * Math.PI) / 4) * (i % 2 ? 9 : 24)), Math.round(-Math.cos((i * Math.PI) / 4) * (i % 2 ? 9 : 24))] as [number, number]))} c={c} w={4} />;
    case 'chispa':
      return <g><L d="M0,-26 V26 M-26,0 H26" c={c} w={8} /><L d="M-14,-14 L14,14 M14,-14 L-14,14" c={c} w={5} /></g>;
    case 'circulo':
      return <L d={ci(0, 0, 18)} c={c} w={7} />;
    case 'mas':
      return <L d="M0,-18 V18 M-18,0 H18" c={c} w={9} />;
    case 'rayas':
      return <L d="M-22,-14 L-6,-20 M-22,0 L4,-8 M-22,14 L-2,8" c={c} w={7} />;
    default:
      return <L d="M-30,0 q10,-18 20,0 t20,0 t20,0" c={c} w={7} />;
  }
};

const Adornos: React.FC<{semilla: number; huecos: [number, number][]}> = ({semilla, huecos}) => {
  const f = useCurrentFrame();
  const r = azar(semilla * 7 + 3);
  const cols = ['rojo', 'amarillo', 'azul', 'verde', 'naranja', 'rosa'];
  return (
    <g>
      {huecos.map(([x, y], i) => {
        const tipo = ADORNOS[Math.floor(r() * ADORNOS.length)];
        const c = cols[Math.floor(r() * cols.length)];
        const rot = r() * 60 - 30;
        const t0 = 4 + i * 5;
        const u = clamp01((f - t0) / 12);
        return (
          <g key={i} transform={`translate(${x},${y + Math.sin((f + i * 20) / 21) * 5}) rotate(${rot + Math.sin((f + i * 9) / 30) * 6}) scale(${atras(u)})`} opacity={u}>
            <Adorno tipo={tipo} c={c} />
          </g>
        );
      })}
    </g>
  );
};

// ------------------------------------------------------------------ simbolos entre objetos
const Simbolo: React.FC<{s: string; t0: number}> = ({s, t0}) => {
  const f = useCurrentFrame();
  const u = atras((f - t0) / 12);
  return (
    <g transform={`translate(960,590) scale(${Math.max(0.01, u)})`} opacity={clamp01(u * 3)}>
      {s === '+' && <L d="M0,-50 V50 M-50,0 H50" c="rojo" w={22} />}
      {s === '=' && <L d="M-50,-22 H50 M-50,22 H50" c="rojo" w={20} />}
      {s === 'vs' && <T x={0} y={26} px={86} anchor="middle" c="rojo" fam={GRANDE}>VS</T>}
      {s === '→' && (
        <g>
          <L d="M-60,0 H50 M10,-40 L56,0 L10,40" c="rojo" w={22} />
        </g>
      )}
    </g>
  );
};

// ------------------------------------------------------------------ escena
/** El titular de una escena grande, sobre un cartel de papel para que se lea sobre cualquier fondo. */
const Cartel: React.FC<{texto: string; retardo: number; fps: number}> = ({texto, retardo, fps}) => {
  const f = useCurrentFrame();
  const {px, l} = lineasTitular(may(texto), 1500, [96, 84, 74, 66]);
  const w = Math.min(1480, Math.max(...l.map((x) => x.replace(/\*/g, '').length)) * px * 0.68 + 150);
  const h = l.length * px * 1.12 + 56;
  const u = atras((f - Math.round(retardo * fps)) / 14, 1.5);
  return (
    <g opacity={clamp01((f - Math.round(retardo * fps)) / 4)} transform={`translate(960,${60 + h / 2}) rotate(-1.2) scale(${Math.max(0.01, u)}) translate(-960,${-(60 + h / 2)})`}>
      <F d={rr(960 - w / 2, 60, w, h, 28)} c="blanco" />
      <Titular texto={texto} retardo={retardo + 0.1} x={960} y={60 + 30 + px * 0.82} ancho={1500} anchor="middle" fps={fps} tamanos={[96, 84, 74, 66]} />
    </g>
  );
};

const ICONO_TEMA: Record<string, string> = {bar: 'taza', burger: 'hamburguesa', taxi: 'taxi', peluqueria: 'tijeras', estanco: 'cajetilla', mercadona: 'carrito'};

/** Etiqueta de capitulo arriba a la izquierda y banda con el rotulo abajo a la derecha, como en los canales de historia. */
const Hud: React.FC<{p: PlanoD; fps: number}> = ({p, fps}) => {
  const f = useCurrentFrame();
  const m = /cap(\d+)/.exec(p.id);
  const capitulo = m ? 'CAP. ' + m[1] : p.id.startsWith('cierre') ? 'FIN' : 'INTRO';
  const Ico = OBJ[ICONO_TEMA[p.escena?.tema ?? 'bar'] ?? 'euro'] ?? OBJ.euro;
  const u = suave((f - 6) / 12);
  const txt = (p.etiqueta ?? '').toUpperCase();
  return (
    <g>
      <g transform={`translate(${24 - (1 - u) * 200},24)`}>
        <rect width={150} height={158} rx={16} fill="#1E1B22" opacity={0.86} />
        <g transform="translate(75,64) scale(0.26)">
          <Ico />
        </g>
        <text x={75} y={140} fontSize={30} textAnchor="middle" fill="#FFFFFF" fontFamily={`"${GRANDE}"`}>{capitulo}</text>
      </g>
      {txt && (
        <g transform={`translate(${(1 - u) * 700},0)`}>
          <path d="M1480,1080 L1520,1000 H1920 V1080 Z" fill="#1E1B22" />
          <text x={1890} y={1062} fontSize={54} textAnchor="end" fill="#FFFFFF" fontFamily={`"${GRANDE}"`}>{txt}</text>
        </g>
      )}
    </g>
  );
};

const Contenido: React.FC<{p: PlanoD; fps: number}> = ({p, fps}) => {
  const t = useContext(Ctx);
  const objs = p.objetos;
  const ret = Math.round(((p.titular?.retardo ?? 0.35) as number) * fps);
  const conTitular = !!p.titular;

  if (p.escena) {
    const S = ESCENAS[p.escena.id];
    if (S) {
      const e = p.escena;
      return (
        <g>
          <S foco={e.foco} burbuja={e.burbuja} cara={e.cara} pose={e.pose} v={e.v} tema={e.tema} s={p.semilla % 7} n={p.frames} />
          {t.toon && <Hud p={p} fps={fps} />}
          {(p.titular || p.etiqueta) && <Cartel texto={p.titular?.texto ?? (p.etiqueta as string)} retardo={p.titular?.retardo ?? 0.3} fps={fps} />}
        </g>
      );
    }
  }
  if (p.grafico) {
    const G = GRAFICOS[p.grafico.tipo];
    if (G) return <G spec={p.grafico} fps={fps} epigrafe={p.epigrafe} />;
  }

  const sitio = (i: number, n: number): [number, number, number] => {
    // x, y, escala segun layout
    const baja = conTitular ? 70 : 0;
    switch (p.layout) {
      case 'izq':
        return [i === 0 ? 560 : 560, 560, 1.75];
      case 'der':
        return [1360, 560, 1.75];
      case 'duo':
        return [i === 0 ? 560 : 1360, 590 + baja, conTitular ? 1.3 : 1.5];
      case 'trio':
        return [[360, 960, 1560][i], 600 + baja, conTitular ? 1.05 : 1.18];
      default:
        return [960, 580 + baja, conTitular ? 1.5 : 1.85];
    }
  };

  const lateral = p.layout === 'izq' || p.layout === 'der';
  const xt = p.layout === 'izq' ? 1000 : 150;
  return (
    <g>
      {conTitular && !lateral && (
        <Titular texto={p.titular!.texto} retardo={p.titular!.retardo ?? 0.35} x={960} y={190} ancho={1700} anchor="middle" fps={fps} />
      )}
      {conTitular && lateral && (
        <Titular texto={p.titular!.texto} retardo={p.titular!.retardo ?? 0.35} x={xt} y={480} ancho={780} anchor="start" fps={fps} />
      )}
      {objs.map((ob, i) => {
        const C = OBJ[ob.o] ?? OBJ.estrella;
        const [x, y, k] = sitio(i, objs.length);
        const t0 = 2 + i * 7;
        return (
          <g key={i}>
            <Entra t0={t0} x={x} y={y} k={k} rot={i % 2 ? 8 : -8} fase={i * 31 + p.semilla}>
              <C />
            </Entra>
            {ob.e && !conTitular && !lateral && (
              <Etiqueta t0={t0 + 8} x={x} y={y + 215 * k + 24} texto={may(ob.e)} px={objs.length > 2 ? 50 : 62} />
            )}
          </g>
        );
      })}
      {lateral && !conTitular && objs[0]?.e && (
        <Titular texto={objs[0].e} retardo={0.3} x={xt} y={500} ancho={780} anchor="start" fps={fps} />
      )}
      {objs.length === 2 && p.simbolo && <Simbolo s={p.simbolo} t0={16} />}
    </g>
  );
};

export const EscenaDoodle: React.FC<{plano: PlanoD; fps?: number}> = ({plano, fps = 25}) => {
  const ok = useFuentes();
  const f = useCurrentFrame();
  const t = paleta(plano.papel ?? 'crema');
  if (!ok) return <AbsoluteFill style={{background: t.fondo}} />;
  const n = plano.frames;
  const cam = plano.camara ?? {k0: 1, k1: 1.04, dx: 0, dy: 0};
  const u = clamp01(f / Math.max(1, n - 1));
  const k = cam.k0 + (cam.k1 - cam.k0) * u;
  const huecos: [number, number][] = [
    [150, 130], [1770, 120], [120, 560], [1800, 560], [190, 960], [1730, 950], [900, 1030], [1000, 70],
  ];
  const r = azar(plano.semilla + 11);
  const elegidos = huecos.filter(() => r() > 0.45).slice(0, plano.grafico ? 3 : 5);
  // el trazo "hierve": la semilla del ruido cambia cada tres fotogramas
  const hierve = (Math.floor(f / 3) % 4) + 1 + (plano.semilla % 5) * 4;
  return (
    <AbsoluteFill>
      <Ctx.Provider value={t}>
        <svg width={1920} height={1080} viewBox="0 0 1920 1080">
          <Defs semilla={hierve} />
          <Fondo w={1920} h={1080} />
          <g transform={`translate(960,540) scale(${k}) translate(${-960 + cam.dx * u},${-540 + cam.dy * u})`}>
            <g filter={t.toon ? undefined : 'url(#torcido)'}>
              <Adornos semilla={plano.semilla} huecos={elegidos} />
              <Contenido p={plano} fps={fps} />
            </g>
          </g>
        </svg>
      </Ctx.Provider>
    </AbsoluteFill>
  );
};
