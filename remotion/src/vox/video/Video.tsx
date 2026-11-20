import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {AMARILLO, Escena, Fondo, H, MarcaCtx, NEGRO, Spec, W, c01, suave, useFuentes} from './base';
import {Cortinilla, FondoClip, Recorte} from './capas';
import {Documental} from './Documental';
import {TIPOS} from './escenas';

/**
 * El video entero: una lista de escenas con su tramo de fotogramas. Cada
 * escena es una pila de capas con vida propia:
 *
 *   metraje a sangre (con sus cortes)  ->  grafico o rotulos  ->  recortes
 *
 * El grafico entra unos fotogramas antes de su frase; los recortes entran y
 * salen cuando la voz los nombra; la camara empuja y deriva sin parar, y cada
 * capa se mueve a distinta velocidad.
 */
const ENT = 11; // fotogramas de entrada
const SAL = 9; // fotogramas de salida

const Hud: React.FC<{f: number; esc: Escena | undefined; nombre: string; acento: string}> = ({f, esc, nombre, acento}) => {
  if (!esc) return null;
  const t = f - esc.f0;
  const sombra = '0 2px 10px rgba(0,0,0,0.75)';
  return (
    <>
      <div style={{position: 'absolute', left: 90, top: 60, display: 'flex', alignItems: 'center', gap: 16}}>
        <div style={{width: 18, height: 18, borderRadius: 9, background: acento}} />
        <div style={{font: "28px 'M Semi'", letterSpacing: 5, color: '#fff', textShadow: sombra}}>
          {nombre}
          {esc.capitulo ? <span style={{opacity: 0.78}}> · {esc.capitulo}</span> : null}
        </div>
      </div>
      {esc.fuente && (
        <div style={{position: 'absolute', left: 90, right: 90, bottom: 50, font: "21px 'M Medium'", letterSpacing: 2.2, textTransform: 'uppercase', color: 'rgba(255,255,255,0.82)', textShadow: sombra, opacity: c01((t - 10) / 8)}}>
          Fuente: {esc.fuente}
        </div>
      )}
    </>
  );
};

/** La piel la dice el spec: `doc` es la documental; sin nada, la moderna de tarjetas. */
export const Video: React.FC<{spec: Spec}> = ({spec}) => (spec?.piel === 'doc' ? <Documental spec={spec} /> : <Moderno spec={spec} />);

const Moderno: React.FC<{spec: Spec}> = ({spec}) => {
  const ok = useFuentes();
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (!ok || !spec?.escenas?.length) return <AbsoluteFill style={{background: NEGRO}} />;
  const E = spec.escenas;
  const m = spec.marca;
  // la escena "en curso" es la ultima que ya ha empezado
  let ia = 0;
  for (let i = 0; i < E.length; i++) if (f >= E[i].f0) ia = i;
  const actual = E[ia];
  const previa = ia > 0 ? E[ia - 1] : undefined;
  const mezcla = suave((f - actual.f0) / 12);
  const osc = (e?: Escena) => (e?.fondo === 'oscuro' ? 1 : 0);
  const oscuro = osc(previa) + (osc(actual) - osc(previa)) * mezcla;
  const pares: [string, string][] = [[m.acento, '#fff'], [AMARILLO, NEGRO], [m.claro, '#fff'], [NEGRO, m.acento]];
  return (
    <MarcaCtx.Provider value={m}>
      <AbsoluteFill style={{background: NEGRO, overflow: 'hidden'}}>
        <Fondo f={f} oscuro={previa ? oscuro : osc(actual)} />
        {E.map((e, i) => {
          if (f < e.f0 - 1 || f > e.f1 + 13) return null;
          const C = TIPOS[e.tipo];
          if (!C) return null;
          const t = f - e.f0;
          const dur = e.f1 - e.f0;
          const sig = E[i + 1];
          const cort = e.trans === 'cortinilla';
          const sigCort = sig?.trans === 'cortinilla';
          const ent = i === 0 ? 1 : cort ? (t >= 0 ? 1 : 0) : suave(t / ENT);
          const sal = !sig ? 0 : sigCort ? (f >= e.f1 ? 1 : 0) : Math.pow(c01((f - e.f1) / SAL), 2);
          // maneras de cambiar de plano, por turnos: sube, entra de lado, o se acerca. Los planos de metraje cortan en seco.
          const seco = e.tipo === 'plano' || cort;
          const modo = seco ? 3 : i % 3;
          const dx = modo === 1 ? (1 - ent) * W * 0.6 - sal * W * 0.6 : 0;
          const dy = modo === 0 ? (1 - ent) * H * 0.8 - sal * H * 0.8 : 0;
          const zoom = modo === 2 ? 0.82 + 0.18 * ent + sal * 0.35 : 1;
          const borr = seco ? 0 : Math.sin(Math.PI * c01(ent < 1 ? ent : sal)) * (modo === 2 ? 10 : 16);
          // camara: empuja y deriva hacia un lado distinto en cada plano
          const u = c01(t / Math.max(1, dur));
          const cam: [number, number] = [(i % 2 ? 1 : -1) * (u - 0.5), (i % 3 === 0 ? 1 : -1) * (u - 0.5) * 0.6];
          const empuje = 1 + 0.035 * u;
          const pasos = e.pasos ?? [0];
          const p = (k: number) => (pasos[k] !== undefined ? t - pasos[k] : k === 0 ? t : -1e6);
          const [rx, rw] = e.region ?? [0, W];
          const opFondo = Math.min(i === 0 || cort ? (t >= 0 ? 1 : 0) : c01((t + 1) / 7), sig?.fondoClip && !sigCort ? 1 : sigCort ? (f >= e.f1 ? 0 : 1) : 1 - c01((f - e.f1) / 8));
          const opCont = (modo === 2 ? ent : seco ? c01(ent) : 1) * (1 - sal * (modo === 2 || seco ? 1 : 0.3));
          return (
            <React.Fragment key={e.id}>
              {e.fondoClip && f <= e.f1 + SAL && opFondo > 0 && (
                <AbsoluteFill style={{opacity: opFondo}}>
                  <FondoClip clips={e.fondoClip} f0={e.f0} f1={e.f1} f={f} fps={fps} velo={e.velo ?? 'plano'} i={i} />
                </AbsoluteFill>
              )}
              {f <= e.f1 + SAL && opCont > 0 && (
                <AbsoluteFill style={{transform: `translate(${dx + cam[0] * 26}px, ${dy + cam[1] * 18}px) scale(${zoom * empuje})`, filter: borr > 0.4 ? `blur(${borr}px)` : undefined, opacity: opCont}}>
                  <div style={{position: 'absolute', left: rx, top: 0, width: rw, height: H}}>
                    <C d={e.d} t={t} dur={dur} p={p} ancho={rw} />
                  </div>
                </AbsoluteFill>
              )}
              {(e.medios ?? []).map((x: any, k: number) => (
                <Recorte key={k} m={x} f0={e.f0} f={f} fps={fps} cam={[cam[0] * 2.4, cam[1] * 2.4]} fin={dur - 2} />
              ))}
            </React.Fragment>
          );
        })}
        {E.map((e, i) => (e.trans === 'cortinilla' && Math.abs(f - e.f0) < 12 ? <Cortinilla key={'c' + e.id} t={f - e.f0} sentido={i % 2 ? 1 : -1} colores={pares[i % pares.length]} /> : null))}
        <Hud f={f} esc={actual} nombre={m.nombre} acento={m.acento} />
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 58%, rgba(0,0,0,0.3) 100%)', pointerEvents: 'none'}} />
      </AbsoluteFill>
    </MarcaCtx.Provider>
  );
};
