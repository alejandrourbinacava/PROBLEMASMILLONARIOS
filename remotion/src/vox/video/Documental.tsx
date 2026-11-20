import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Escena, MarcaCtx, Spec, c01, useFuentes} from './base';
import {Metraje} from './capas';
import {FONDO, TIPOS_DOC} from './doc';

/**
 * El video en piel documental. Cada plano es metraje a sangre con muy poco
 * encima, o un inserto oscuro (grafico, cita, documento, mapa) que entra por
 * fundido. Sin cortinillas, sin marcos y sin letrero fijo de marca.
 *
 *   corte      entre planos de metraje
 *   fundido    al entrar o salir de un inserto (8 fotogramas)
 *   a negro    en cada capitulo
 */
const X = 4; // media duracion del fundido
const INSERTOS = ['barras', 'linea', 'cita', 'documento', 'mapa', 'pares', 'duo'];

type Velo = 'limpio' | 'medio' | 'oscuro';
const FILTRO: Record<Velo, string> = {
  limpio: 'saturate(0.86) contrast(1.07) brightness(0.94)',
  medio: 'saturate(0.65) contrast(1.05) brightness(0.34) blur(3px)',
  oscuro: 'saturate(0.6) contrast(1.05) brightness(0.26) blur(7px)',
};

/** Metraje a sangre: cortes secos entre clips y un empuje lento, mas marcado en las fotos. */
const FondoDoc: React.FC<{e: Escena; f: number; fps: number; i: number}> = ({e, f, fps, i}) => {
  const clips: any[] = e.fondoClip ?? [];
  const t = f - e.f0;
  let k = 0;
  for (let j = 0; j < clips.length; j++) if (t >= clips[j].en) k = j;
  const c = clips[k];
  const fin = k + 1 < clips.length ? clips[k + 1].en : e.f1 - e.f0 + 12;
  const u = c01((t - c.en) / Math.max(1, fin - c.en));
  const sentido = (i + k) % 2 ? 1 : -1;
  const amp = c.foto ? 0.085 : 0.035;
  const esc = 1.03 + amp * (sentido > 0 ? u : 1 - u);
  const dx = sentido * (u - 0.5) * (c.foto ? 36 : 14);
  const velo = (e.velo as Velo) ?? 'limpio';
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: FONDO}}>
      <AbsoluteFill style={{transform: `scale(${esc + (velo === 'oscuro' ? 0.04 : 0)}) translateX(${dx}px)`, filter: FILTRO[velo] ?? FILTRO.limpio}}>
        <Metraje key={k} m={c} abs={e.f0 + c.en} dur={fin - c.en + 2} fps={fps} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const azar = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

export const Documental: React.FC<{spec: Spec}> = ({spec}) => {
  const ok = useFuentes();
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!ok || !spec?.escenas?.length) return <AbsoluteFill style={{background: FONDO}} />;
  const E = spec.escenas;
  const modo = (i: number): 'corte' | 'funde' | 'negro' => {
    if (i === 0) return 'corte';
    const e = E[i];
    if (e.trans === 'negro' || e.tipo === 'capitulo') return 'negro';
    if (e.trans === 'corte' || e.trans === 'funde') return e.trans as any;
    return INSERTOS.includes(e.tipo) || INSERTOS.includes(E[i - 1].tipo) ? 'funde' : 'corte';
  };
  let negro = 0;
  const g = Math.floor(f / 2);
  return (
    <MarcaCtx.Provider value={spec.marca}>
      <AbsoluteFill style={{background: FONDO, overflow: 'hidden'}}>
        {E.map((e, i) => {
          const t = f - e.f0;
          const dur = e.f1 - e.f0;
          if (t < -X - 10 || t > dur + X + 1) return null;
          const C = TIPOS_DOC[e.tipo];
          if (!C) return null;
          const md = modo(i);
          const sig = i + 1 < E.length ? modo(i + 1) : null;
          if (md === 'negro') negro = Math.max(negro, t < 0 ? c01((t + 9) / 9) : 1 - c01(t / 12));
          const ent = md === 'funde' ? c01((t + X) / (2 * X)) : t >= 0 ? 1 : 0;
          const visible = sig === 'funde' ? t <= dur + X : t < dur;
          if (ent <= 0 || !visible) return null;
          const pasos = e.pasos ?? [0];
          const p = (k: number) => (pasos[k] !== undefined ? t - pasos[k] : k === 0 ? t : -1e6);
          return (
            <AbsoluteFill key={e.id} style={{opacity: ent, background: FONDO}}>
              {e.fondoClip && <FondoDoc e={e} f={f} fps={fps} i={i} />}
              <C d={e.d} t={t} dur={dur} p={p} ancho={1920} ctx={{f0: e.f0, f, fps, medios: e.medios ?? []}} />
              {e.fuente && (
                <div style={{position: 'absolute', left: 110, right: 110, bottom: 52, font: "500 19px 'D Sans'", letterSpacing: 2.4, textTransform: 'uppercase', color: 'rgba(245,242,234,0.58)', textShadow: '0 1px 8px rgba(0,0,0,0.7)', opacity: c01((t - 14) / 10)}}>
                  Fuente: {e.fuente}
                </div>
              )}
            </AbsoluteFill>
          );
        })}
        {negro > 0 && <AbsoluteFill style={{background: '#000', opacity: negro}} />}
        {/* acabado: vineta y grano de pelicula, igual en todo el video */}
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 52%, rgba(0,0,0,0.42) 100%)', pointerEvents: 'none'}} />
        <AbsoluteFill style={{overflow: 'hidden', mixBlendMode: 'overlay', opacity: 0.2, pointerEvents: 'none'}}>
          <Img src={staticFile('vox/media/grano.jpg')} style={{position: 'absolute', width: 2400, height: 1400, left: -Math.round(azar(g) * 440), top: -Math.round(azar(g + 0.5) * 300)}} />
        </AbsoluteFill>
      </AbsoluteFill>
    </MarcaCtx.Provider>
  );
};
