import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {AMARILLO, EP, H, NEGRO, Rico, W, atras, c01, suave, useMarca} from './base';

/**
 * Las capas de imagen real: metraje a pantalla completa, recortes que entran
 * y salen por encima del grafico, y el plano de metraje con rotulos en tiras.
 * Todo lleva su propio momento de entrada y de salida: nada aparece a la vez
 * y nada se queda hasta el final porque si.
 */
export type Medio = {
  src: string; // nombre del fichero en vox/media
  foto?: boolean;
  desde?: number; // segundo del clip en el que empieza
  rate?: number;
  en: number; // fotograma (relativo a la escena) en que entra
  sale?: number; // fotograma en que sale
  caja?: [number, number, number, number];
  rot?: number;
  de?: 'izq' | 'der' | 'arr' | 'aba';
  z?: number; // profundidad: >1 se mueve mas con la camara
  pie?: string;
  marco?: 'blanco' | 'marca' | 'no';
  bn?: boolean;
  foco?: [number, number]; // punto de interes de la imagen, en %
};

const ruta = (src: string) => staticFile('vox/media/' + src);

/** Un clip (o una foto) que llena su caja. `abs` es el fotograma absoluto en que empieza a correr. */
export const Metraje: React.FC<{m: Medio; abs: number; dur: number; fps: number; estilo?: React.CSSProperties}> = ({m, abs, dur, fps, estilo}) => {
  const st: React.CSSProperties = {position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', objectPosition: m.foco ? `${m.foco[0]}% ${m.foco[1]}%` : undefined, ...estilo};
  if (m.foto) return <Img src={ruta(m.src)} style={st} />;
  return (
    <Sequence from={abs} durationInFrames={Math.max(1, dur)} layout="none">
      <OffthreadVideo src={ruta(m.src)} startFrom={Math.round((m.desde ?? 0) * fps)} playbackRate={m.rate ?? 1} muted style={st} />
    </Sequence>
  );
};

// ------------------------------------------------------------------ fondo de metraje
export type Velo = 'plano' | 'oscuro' | 'medio' | 'marca' | 'lado';
/**
 * Metraje a sangre detras de la escena. Dentro de una escena puede cortar de
 * un clip a otro (cada uno con su `en`); cada corte entra con un golpe de zoom.
 */
export const FondoClip: React.FC<{clips: Medio[]; f0: number; f1: number; f: number; fps: number; velo: Velo; i: number}> = ({clips, f0, f1, f, fps, velo, i}) => {
  const m = useMarca();
  const t = f - f0;
  let k = 0;
  for (let j = 0; j < clips.length; j++) if (t >= clips[j].en) k = j;
  const c = clips[k];
  const fin = k + 1 < clips.length ? clips[k + 1].en : f1 - f0 + 12;
  const tl = t - c.en;
  const u = c01(tl / Math.max(1, fin - c.en));
  const golpe = k > 0 ? (1 - suave(tl / 7)) * 0.1 : 0;
  // cada clip empuja hacia un lado distinto
  const sentido = (i + k) % 2 ? 1 : -1;
  const esc = 1.07 + 0.07 * u + golpe;
  const dx = sentido * (u - 0.5) * 46;
  const desenfoque = velo === 'oscuro' ? 7 : velo === 'marca' ? 5 : 0;
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: NEGRO}}>
      <AbsoluteFill style={{transform: `scale(${esc}) translateX(${dx}px)`, filter: `${desenfoque ? `blur(${desenfoque}px) ` : ''}saturate(${velo === 'plano' ? 1.08 : 0.8}) contrast(1.06)`}}>
        <Metraje key={k} m={c} abs={f0 + c.en} dur={fin - c.en + 2} fps={fps} />
      </AbsoluteFill>
      {velo === 'plano' && <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(4,14,9,0.42) 0%, rgba(4,14,9,0.05) 26%, rgba(4,14,9,0.1) 52%, rgba(4,14,9,0.74) 100%)'}} />}
      {velo === 'lado' && <AbsoluteFill style={{background: `linear-gradient(90deg, ${m.oscuro}F2 0%, ${m.oscuro}D9 46%, rgba(4,14,9,0.28) 78%, rgba(4,14,9,0.16) 100%)`}} />}
      {velo === 'medio' && <AbsoluteFill style={{background: `linear-gradient(100deg, ${m.oscuro}F0 0%, ${m.oscuro}B0 48%, rgba(4,16,10,0.3) 100%)`}} />}
      {velo === 'oscuro' && <AbsoluteFill style={{background: `linear-gradient(135deg, rgba(4,16,10,0.9) 0%, ${m.oscuro}D4 100%)`}} />}
      {velo === 'marca' && (
        <>
          <AbsoluteFill style={{background: m.color, mixBlendMode: 'multiply'}} />
          <AbsoluteFill style={{background: `linear-gradient(135deg, ${m.color}CC 0%, ${m.oscuro}B8 100%)`}} />
        </>
      )}
      {k > 0 && tl < 4 && <AbsoluteFill style={{background: '#fff', opacity: 0.22 * (1 - tl / 4)}} />}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ recorte
/**
 * Una foto o un clip en su marco, que entra lanzado desde un lado, asienta con
 * un pequeno giro y luego SE VA por donde vino.
 */
export const Recorte: React.FC<{m: Medio; f0: number; f: number; fps: number; cam: [number, number]; fin: number}> = ({m, f0, f, fps, cam, fin}) => {
  const marca = useMarca();
  const t = f - f0 - m.en;
  const sale = m.sale ?? fin;
  const ts = f - f0 - sale;
  if (t < -1 || ts > 12) return null;
  const [x, y, w, h] = m.caja ?? [1180, 560, 650, 380];
  const de = m.de ?? 'der';
  const ent = atras(t / 13, 1.25);
  const sal = Math.pow(c01(ts / 10), 2.2);
  const lejos = 1 - ent + sal * 1.25;
  const vx = de === 'izq' ? -1 : de === 'der' ? 1 : 0;
  const vy = de === 'arr' ? -1 : de === 'aba' ? 1 : 0;
  const z = m.z ?? 1.3;
  const rot = (m.rot ?? 0) + (1 - suave(t / 16)) * (vx || vy) * 9 + sal * (vx || 1) * 7;
  const tx = vx * lejos * (W * 0.75) + cam[0] * (z - 1) * 60;
  const ty = vy * lejos * (H * 0.9) + cam[1] * (z - 1) * 60;
  const borr = Math.max(0, 1 - t / 7) * 14 + sal * 12;
  const marco = m.marco ?? 'blanco';
  const b = marco === 'no' ? 0 : 9;
  const vida = sale - m.en;
  const u = c01(t / Math.max(1, vida));
  return (
    <div
      style={{
        position: 'absolute', left: x, top: y, width: w, height: h, transform: `translate(${tx}px, ${ty}px) rotate(${rot}deg)`,
        opacity: c01((t + 1) / 3) * (1 - c01((ts - 6) / 5)), filter: borr > 0.5 ? `blur(${borr}px)` : undefined,
        borderRadius: 26, background: marco === 'marca' ? marca.acento : '#fff', boxShadow: '0 30px 70px rgba(0,0,0,0.5), 0 4px 14px rgba(0,0,0,0.3)',
      }}
    >
      <div style={{position: 'absolute', inset: b, borderRadius: 26 - b, overflow: 'hidden', background: NEGRO}}>
        <div style={{position: 'absolute', inset: 0, transform: `scale(${1.04 + 0.1 * u})`, filter: m.bn ? 'grayscale(1) contrast(1.12)' : 'saturate(1.08) contrast(1.04)'}}>
          <Metraje m={m} abs={f0 + m.en - 1} dur={vida + 16} fps={fps} />
        </div>
        {m.pie && (
          <div style={{position: 'absolute', left: 0, bottom: 0, right: 0, padding: '46px 22px 14px', background: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.78) 70%)', font: "27px/1.15 'M Semi'", color: '#fff', letterSpacing: 0.4, opacity: c01((t - 8) / 6)}}>
            {m.pie}
          </div>
        )}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ plano de metraje con rotulos
/**
 * Texto en tiras sobre metraje. Cada linea entra con su tira de color
 * barriendo de izquierda a derecha en la palabra que dice la voz, y las
 * anteriores se van (salvo `queda`). Asi el plano nunca acumula mas de dos
 * ideas en pantalla.
 */
const Tira: React.FC<{l: any; t: number; ts: number; base: number}> = ({l, t, ts, base}) => {
  const m = useMarca();
  const tam = l.tam ?? (l.tenue ? Math.max(54, Math.round(base * 0.7)) : base);
  const fondo = l.color === 'acento' ? m.acento : l.color === 'amarillo' ? AMARILLO : l.color === 'blanco' ? '#fff' : l.color === 'marca' ? m.color : l.tenue ? 'rgba(6,20,13,0.9)' : NEGRO;
  const tinta = l.color === 'amarillo' || l.color === 'blanco' ? NEGRO : '#fff';
  const u = suave(t / 9);
  const s = Math.pow(c01(ts / 8), 2);
  return (
    <div style={{marginBottom: 12, whiteSpace: 'nowrap', opacity: 1 - c01((ts - 3) / 5), transform: `translateX(${-s * 160}px)`}}>
      <div style={{display: 'inline-block', verticalAlign: 'top', clipPath: `inset(-60px ${(1 - u) * 100}% -60px -60px)`}}>
        <div style={{background: fondo, color: tinta, font: `${tam}px/${Math.round(tam * 1.34)}px 'M Black'`, letterSpacing: -1, padding: `0 ${Math.round(tam * 0.3)}px`, borderRadius: 10, boxShadow: '0 14px 40px rgba(0,0,0,0.35)'}}>
          <span style={{display: 'inline-block', transform: `translateX(${(1 - suave((t - 2) / 10)) * -40}px)`, opacity: c01((t - 2) / 5)}}>
            <Rico texto={l.t} t={t} t0={12} acento={l.color === 'acento' ? AMARILLO : undefined} />
          </span>
        </div>
      </div>
    </div>
  );
};

export const Plano: React.FC<EP> = ({d, p, dur}) => {
  const m = useMarca();
  const lineas: any[] = d.lineas ?? [];
  const largo = Math.max(1, ...lineas.filter((l) => !l.tenue).map((l) => l.t.replace(/[*_]/g, '').length));
  const base = d.tam ?? (largo < 16 ? 150 : largo < 24 ? 124 : largo < 32 ? 100 : largo < 40 ? 84 : 70);
  const pos = d.pos ?? 'bi';
  const caja: React.CSSProperties =
    pos === 'c' ? {left: 90, right: 90, top: 0, bottom: 0, justifyContent: 'center', alignItems: 'center'}
    : pos === 'ci' ? {left: 90, right: 90, top: 0, bottom: 0, justifyContent: 'center'}
    : pos === 'ai' ? {left: 90, right: 90, top: 170}
    : {left: 90, right: 90, bottom: 150, justifyContent: 'flex-end'};
  // una linea se va cuando entra la que la sustituye (grupo siguiente), salvo que lleve `queda`
  const grupo = (l: any, i: number) => l.grupo ?? i;
  return (
    <>
      <div style={{position: 'absolute', display: 'flex', flexDirection: 'column', ...caja}}>
        {lineas.map((l, i) => {
          const t = p(l.paso ?? i);
          const sig = lineas.find((o, j) => j > i && grupo(o, j) !== grupo(l, i));
          const ts = d.acumula || l.queda || !sig ? -1 : p(sig.paso ?? lineas.indexOf(sig)) + 3;
          if (t < 0 || ts > 12) return null;
          return <Tira key={i} l={l} t={t} ts={ts} base={base} />;
        })}
      </div>
      {d.etiqueta && (
        <div style={{position: 'absolute', right: 90, top: 150, textAlign: 'right', opacity: c01(p(d.etiqueta.paso ?? 0) / 6) * (d.etiqueta.sale !== undefined ? 1 - c01(p(d.etiqueta.sale) / 6) : 1), transform: `translateX(${(1 - suave(p(d.etiqueta.paso ?? 0) / 12)) * 80}px)`}}>
          <div style={{display: 'inline-block', background: '#fff', color: NEGRO, font: "40px 'M Black'", padding: '8px 22px', borderRadius: 10}}>{d.etiqueta.t}</div>
          {d.etiqueta.sub && <div style={{font: "28px 'M Semi'", color: '#fff', marginTop: 10, letterSpacing: 2, textTransform: 'uppercase', textShadow: '0 2px 12px rgba(0,0,0,0.8)'}}>{d.etiqueta.sub}</div>}
        </div>
      )}
      {(d.cifras ?? (d.cifra ? [d.cifra] : [])).map((x: any, i: number) => {
        const te = p(x.paso ?? 0);
        const ts = x.sale !== undefined ? p(x.sale) : -1;
        if (te < 0 || ts > 10) return null;
        return (
          <div key={i} style={{position: 'absolute', right: 90, top: x.arriba ? 150 : undefined, bottom: x.arriba ? undefined : 150, textAlign: 'right', opacity: c01(te / 4) * (1 - c01(ts / 6)), transform: `translateX(${Math.pow(c01(ts / 8), 2) * 240}px) scale(${0.6 + 0.4 * atras(te / 12, 2)})`, transformOrigin: 'right bottom'}}>
            <div style={{display: 'inline-block', textAlign: 'left', background: x.color === 'acento' ? m.acento : AMARILLO, color: x.color === 'acento' ? '#fff' : NEGRO, borderRadius: 26, padding: '18px 38px', transform: `rotate(${i % 2 ? 2 : -2.5}deg)`, boxShadow: '0 20px 60px rgba(0,0,0,0.45)'}}>
              <div style={{font: `${x.tam ?? 130}px/1 'M Archivo'`, letterSpacing: -2, whiteSpace: 'nowrap'}}>{x.t}</div>
              {x.pie && <div style={{font: "38px/1.15 'M Black'", marginTop: 6}}>{x.pie}</div>}
            </div>
          </div>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------ cortinilla de color
/** Dos bandas inclinadas que cruzan el cuadro y tapan el corte. */
export const Cortinilla: React.FC<{t: number; sentido: number; colores: [string, string]}> = ({t, sentido, colores}) => {
  if (t < -9 || t > 10) return null;
  const u = (t + 9) / 19; // 0..1; el corte cae cerca de 0.47
  const x = (u * 2 - 1) * W * 1.55 * sentido;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', overflow: 'hidden'}}>
      <div style={{position: 'absolute', left: -W * 0.35, top: -80, width: W * 1.7, height: H + 160, background: colores[0], transform: `translateX(${x}px) skewX(${-14 * sentido}deg)`}} />
      <div style={{position: 'absolute', left: -W * 0.35, top: -80, width: W * 0.5, height: H + 160, background: colores[1], transform: `translateX(${x + (sentido > 0 ? -0.62 : 1.82) * W}px) skewX(${-14 * sentido}deg)`}} />
    </AbsoluteFill>
  );
};
