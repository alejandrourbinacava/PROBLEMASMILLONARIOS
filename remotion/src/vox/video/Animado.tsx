import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {EP, Escena, MarcaCtx, Spec, useFuentes} from './base';
import {Metraje} from './capas';
import {A, Cifra, Defs, Escenario, FondoCtx, IdxCtx, Eti, FONDO, GRIS, PAL, Palabras, Sans, Serif, T, TINTA, c01, grad, io, pop, rebote, sal, tr} from './kit';
import {Detras, FondoReal, Sujeto, med} from './m_capas';
import {ESCENAS} from './mercadona';

/**
 * Piel `anim`: el video entero como una sucesion de escenas animadas (ver
 * kit.tsx), con corte seco entre ellas. Tipos:
 *
 *   anim      una escena del registro ESCENAS (d.comp)
 *   cita      tarjeta de cita: las palabras entran con la voz
 *   capitulo  cartela de capitulo
 *   broll     metraje real a sangre, limpio, con un rotulo
 */
const Cita: React.FC<EP> = ({d, t, p, dur, ctx}) => {
  const partes: string[] = d.partes;
  // cada parte ocupa el tramo entre su paso y el siguiente (o el final)
  const ini = (k: number) => t - p(k + 1);
  const act = partes.reduce((a, _, k) => (p(k + 1) >= 0 ? k : a), 0);
  const fin = act + 1 < partes.length ? ini(act + 1) : d.nota ? ini(partes.length) : dur - 6;
  const u = c01((t - ini(act)) / Math.max(10, (fin - ini(act)) * 0.86));
  const n = partes[act].length;
  // con retrato: plano por capas (fondo real desenfocado, el nombre detras, la persona delante)
  const ret = med(ctx, 'c_roig');
  const tam = ret ? (n > 170 ? 46 : n > 110 ? 56 : n > 62 ? 72 : n > 20 ? 92 : 170) : n > 170 ? 56 : n > 110 ? 68 : n > 62 ? 86 : 104;
  const X = ret ? 720 : 160;
  const AN = ret ? 1100 : 1600;
  const Y = ret ? 400 : 300;
  const AL = ret ? 480 : 520;
  const inic = String(d.autor).split(' ').map((x: string) => x[0]).join('').slice(0, 2);
  return (
    <AbsoluteFill>
      {ret ? <FondoReal ctx={ctx} t={t} dur={dur} blur={13} luz={0.34} /> : <Escenario />}
      {ret && <Detras x={650} y={236} t={t - 2} tam={190} ancla="i">{d.autor}</Detras>}
      {ret && <Sujeto src={ret} x={400} y={1110} alto={900} t={t - 5} de="aba" />}
      {!ret && <div style={{position: 'absolute', left: 140, top: 96, font: "700 380px/1 'M Serif'", color: PAL.verde[0], opacity: tr(t, 0, 6), transform: `scale(${0.6 + 0.4 * rebote(t / 12, 1.6)})`, transformOrigin: '20% 30%'}}>“</div>}
      {d.previo && (
        <T x={ret ? X + 4 : 372} y={ret ? 366 : 236} ancla="i" op={tr(t, 6, 8)}>
          <Eti tam={28} color={ret ? '#B9FFD9' : '#C9CED8'}>{d.previo}</Eti>
        </T>
      )}
      {ret && <div style={{position: 'absolute', left: X - 34, top: Y + 30, width: 10, height: AL - 60, borderRadius: 5, background: PAL.verde[0], opacity: tr(t, 8, 8)}} />}
      {d.pregunta && p(1) < 6 && (
        <div style={{position: 'absolute', left: X, top: Y, width: AN, height: AL, display: 'flex', alignItems: 'center', opacity: tr(t, 6, 8) * (1 - tr(p(1), -4, 8))}}>
          <div style={{font: `600 ${ret ? 96 : 124}px/1.1 'M Serif'`, color: TINTA, letterSpacing: -2, transform: `translateY(${(1 - sal(tr(t, 6, 16))) * 40}px)`}}>{d.pregunta}</div>
        </div>
      )}
      <div style={{position: 'absolute', left: X, top: Y, width: AN, height: AL, display: 'flex', alignItems: 'center', opacity: d.pregunta ? tr(p(1), 0, 6) : 1}}>
        <div key={act} style={{font: `700 ${tam}px/1.2 'D Sans'`, color: TINTA, letterSpacing: -tam * 0.012}}>
          <Palabras texto={partes[act]} u={p(act + 1) < 0 ? 0 : u} />
        </div>
      </div>
      {ret ? (
        <T x={X + 4} y={930} ancla="i" op={tr(t, 8, 8)}>
          <Sans tam={30} peso={600} color="#D5DBE6">{d.cargo}{d.cuando ? ' · ' + d.cuando : ''}</Sans>
        </T>
      ) : (
        <div style={{position: 'absolute', left: 160, top: 850, display: 'flex', alignItems: 'center', gap: 28, opacity: tr(t, 4, 8)}}>
          <div style={{width: 112, height: 112, borderRadius: 56, background: grad('verde', 150), font: "700 50px/112px 'M Serif'", color: '#fff', textAlign: 'center', boxShadow: '0 12px 30px rgba(0,0,0,0.4)'}}>{inic}</div>
          <div>
            <div><Sans tam={46} peso={800}>{d.autor}</Sans></div>
            <div><Sans tam={28} peso={500} color={GRIS}>{d.cargo}{d.cuando ? ' · ' + d.cuando : ''}</Sans></div>
          </div>
        </div>
      )}
      {d.nota && p(partes.length + 1) >= 0 && (
        <div style={{position: 'absolute', left: X, top: ret ? 770 : 880, width: AN, opacity: tr(p(partes.length + 1), 0, 8)}}>
          <Serif tam={ret ? 54 : 42} it color="#FFD95A">{d.nota}</Serif>
        </div>
      )}
    </AbsoluteFill>
  );
};

const Capitulo: React.FC<EP> = ({d, t, p}) => {
  const trozos = String(d.titulo).split(/(\*[^*]+\*)/g).filter(Boolean);
  return (
    <AbsoluteFill>
      <Escenario tipo="verde" />
      <T x={330} y={540} op={tr(t, 0, 6)} s={0.7 + 0.3 * rebote(t / 14, 1.3)}>
        <span style={{font: "700 760px/1 'M Serif'", color: 'transparent', WebkitTextStroke: '5px rgba(255,255,255,0.32)'}}>{d.num}</span>
      </T>
      <T x={620} y={380} ancla="i" op={tr(t, 3, 6)}>
        <Eti tam={32} color="rgba(255,255,255,0.8)">Capítulo {d.num}</Eti>
      </T>
      <div style={{position: 'absolute', left: 620, top: 430, width: 1180, font: "600 104px/1.08 'M Serif'", color: '#fff', letterSpacing: -1.5, opacity: tr(t, 4, 7), transform: `translateY(${(1 - sal(tr(t, 4, 14))) * 40}px)`}}>
        {trozos.map((x, i) => (x.startsWith('*') ? <span key={i} style={{color: '#FFE27A'}}>{x.slice(1, -1)}</span> : <span key={i}>{x}</span>))}
      </div>
      {d.sub && (
        <div style={{position: 'absolute', left: 620, top: 760, width: 1100, opacity: tr(p(1), 0, 8)}}>
          <Sans tam={36} peso={500} color="rgba(255,255,255,0.86)">{d.sub}</Sans>
        </div>
      )}
      <div style={{position: 'absolute', left: 620, top: 720, height: 8, width: 240 * io(tr(t, 6, 16)), borderRadius: 4, background: '#FFE27A'}} />
    </AbsoluteFill>
  );
};

/** Metraje real a sangre, sin velo: un respiro entre animaciones. Cortes secos entre clips. */
const Broll: React.FC<EP & {e: Escena; f: number; fps: number}> = ({d, t, p, e, f, fps}) => {
  const clips: any[] = e.fondoClip ?? [];
  let k = 0;
  for (let j = 0; j < clips.length; j++) if (t >= clips[j].en) k = j;
  const c = clips[k];
  const fin = k + 1 < clips.length ? clips[k + 1].en : e.f1 - e.f0 + 12;
  const u = c01((t - c.en) / Math.max(1, fin - c.en));
  const fr: any[] = d.frases ?? [];
  let a = -1;
  fr.forEach((x, i) => {
    if (p(x.paso ?? i) >= 0) a = i;
  });
  return (
    <AbsoluteFill style={{background: FONDO, overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${1.04 + 0.05 * u})`, filter: 'saturate(1.08) contrast(1.05)'}}>
        <Metraje key={k} m={c} abs={e.f0 + c.en} dur={fin - c.en + 2} fps={fps} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,10,14,0.0) 45%, rgba(8,10,14,0.78) 100%)'}} />
      {d.anio && (
        <T x={960} y={470} op={tr(t, 2, 6)} s={0.8 + 0.2 * rebote(t / 12)}>
          <span style={{font: "500 520px/1 'M Serif'", color: '#fff', textShadow: '0 20px 80px rgba(0,0,0,0.5)', letterSpacing: -14}}>{d.anio}</span>
        </T>
      )}
      {a >= 0 && (
        <div key={a} style={{position: 'absolute', left: 120, right: 120, bottom: 110, textAlign: d.centro ? 'center' : 'left'}}>
          {fr[a].k && (
            <div style={{marginBottom: 14, opacity: tr(p(fr[a].paso ?? a), 0, 6)}}>
              <Chip2>{fr[a].k}</Chip2>
            </div>
          )}
          <div style={{font: `600 ${fr[a].tam ?? 84}px/1.1 'M Serif'`, color: '#fff', textShadow: '0 4px 30px rgba(0,0,0,0.6)', letterSpacing: -1, opacity: tr(p(fr[a].paso ?? a), 0, 5), transform: `translateY(${(1 - sal(tr(p(fr[a].paso ?? a), 0, 12))) * 30}px)`}}>
            {String(fr[a].t).split(/(\*[^*]+\*)/g).filter(Boolean).map((x: string, i: number) => (x.startsWith('*') ? <span key={i} style={{color: '#FFE27A'}}>{x.slice(1, -1)}</span> : <span key={i}>{x}</span>))}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
const Chip2: React.FC<{children: React.ReactNode}> = ({children}) => (
  <span style={{display: 'inline-block', font: "700 26px/1 'D Sans'", letterSpacing: 3.6, textTransform: 'uppercase', color: '#0B0C10', background: '#2BE38A', padding: '10px 16px 8px', borderRadius: 8}}>{children}</span>
);

export const Animado: React.FC<{spec: Spec}> = ({spec}) => {
  const ok = useFuentes();
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!ok || !spec?.escenas?.length) return <AbsoluteFill style={{background: FONDO}} />;
  return (
    <MarcaCtx.Provider value={spec.marca}>
      <AbsoluteFill style={{background: FONDO, overflow: 'hidden'}}>
        <Defs />
        {spec.escenas.map((e, idx) => {
          const t = f - e.f0;
          const dur = e.f1 - e.f0;
          if (t < 0 || t >= dur) return null;
          const pasos = e.pasos ?? [0];
          const p = (k: number) => (pasos[k] !== undefined ? t - pasos[k] : k === 0 ? t : -1e6);
          const ep: EP = {d: e.d, t, dur, p, ancho: 1920, ctx: {f0: e.f0, f, fps, medios: e.medios ?? [], clips: e.fondoClip}};
          const C = e.tipo === 'anim' ? ESCENAS[e.d.comp] : e.tipo === 'cita' ? Cita : e.tipo === 'capitulo' ? Capitulo : null;
          const claro = e.d?.claro;
          return (
            <AbsoluteFill key={e.id} style={{background: FONDO}}>
              <IdxCtx.Provider value={idx}>
                <FondoCtx.Provider value={e.tipo === 'anim' && e.fondoClip ? <FondoReal ctx={ep.ctx} t={t} dur={dur} blur={13} luz={0.3} /> : null}>
                  {e.tipo === 'broll' ? <Broll {...ep} e={e} f={f} fps={fps} /> : C ? <C {...ep} /> : null}
                </FondoCtx.Provider>
              </IdxCtx.Provider>
              {e.fuente && (
                <div style={{position: 'absolute', left: 60, bottom: 34, font: "500 18px 'D Sans'", letterSpacing: 2, textTransform: 'uppercase', color: claro ? 'rgba(20,30,50,0.55)' : 'rgba(255,255,255,0.42)', opacity: c01((t - 12) / 10)}}>
                  Fuente: {e.fuente}
                </div>
              )}
            </AbsoluteFill>
          );
        })}
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 62%, rgba(0,0,0,0.26) 100%)', pointerEvents: 'none'}} />
        {/* grano de pelicula, igual en todo el video: quita el aspecto de vector limpio */}
        <AbsoluteFill style={{overflow: 'hidden', mixBlendMode: 'overlay', opacity: 0.17, pointerEvents: 'none'}}>
          <Img src={staticFile('vox/media/grano.jpg')} style={{position: 'absolute', width: 2400, height: 1400, left: -((Math.floor(f / 2) * 173) % 440), top: -((Math.floor(f / 2) * 97) % 300)}} />
        </AbsoluteFill>
      </AbsoluteFill>
    </MarcaCtx.Provider>
  );
};
export {A, Cifra};
