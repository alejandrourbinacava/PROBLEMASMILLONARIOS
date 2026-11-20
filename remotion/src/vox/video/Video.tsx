import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Escena, Fondo, H, MarcaCtx, NEGRO, Spec, W, c01, suave, useFuentes} from './base';
import {TIPOS} from './escenas';

/**
 * El video entero: una lista de escenas con su tramo de fotogramas. Cada
 * escena entra unos fotogramas antes de su frase y sale cuando empieza la
 * siguiente; el corte va escondido en un deslizamiento con desenfoque.
 */
const ENT = 11; // fotogramas de entrada
const SAL = 9; // fotogramas de salida

const Hud: React.FC<{f: number; esc: Escena | undefined; nombre: string; acento: string}> = ({f, esc, nombre, acento}) => {
  if (!esc) return null;
  const t = f - esc.f0;
  return (
    <>
      <div style={{position: 'absolute', left: 90, top: 60, display: 'flex', alignItems: 'center', gap: 16}}>
        <div style={{width: 18, height: 18, borderRadius: 9, background: acento}} />
        <div style={{font: "28px 'M Semi'", letterSpacing: 5, color: '#fff'}}>
          {nombre}
          {esc.capitulo ? <span style={{opacity: 0.7}}> · {esc.capitulo}</span> : null}
        </div>
      </div>
      {esc.fuente && (
        <div style={{position: 'absolute', left: 90, right: 90, bottom: 50, font: "21px 'M Medium'", letterSpacing: 2.2, textTransform: 'uppercase', color: 'rgba(255,255,255,0.74)', opacity: c01((t - 10) / 8)}}>
          Fuente: {esc.fuente}
        </div>
      )}
    </>
  );
};

export const Video: React.FC<{spec: Spec}> = ({spec}) => {
  const ok = useFuentes();
  const f = useCurrentFrame();
  if (!ok || !spec?.escenas?.length) return <AbsoluteFill style={{background: NEGRO}} />;
  const E = spec.escenas;
  // la escena "en curso" es la ultima que ya ha empezado
  let ia = 0;
  for (let i = 0; i < E.length; i++) if (f >= E[i].f0) ia = i;
  const actual = E[ia];
  const previa = ia > 0 ? E[ia - 1] : undefined;
  const mezcla = suave((f - actual.f0) / 12);
  const osc = (e?: Escena) => (e?.fondo === 'oscuro' ? 1 : 0);
  const oscuro = osc(previa) + (osc(actual) - osc(previa)) * mezcla;
  return (
    <MarcaCtx.Provider value={spec.marca}>
      <AbsoluteFill style={{background: NEGRO, overflow: 'hidden'}}>
        <Fondo f={f} oscuro={previa ? oscuro : osc(actual)} />
        {E.map((e, i) => {
          if (f < e.f0 - 1 || f > e.f1 + SAL) return null;
          const C = TIPOS[e.tipo];
          if (!C) return null;
          const t = f - e.f0;
          const ent = i === 0 ? 1 : suave(t / ENT);
          const sal = i === E.length - 1 ? 0 : Math.pow(c01((f - e.f1) / SAL), 2);
          // tres maneras de cambiar de plano, por turnos: sube, entra de lado, o se acerca
          const modo = i % 3;
          const dx = modo === 1 ? (1 - ent) * W * 0.6 - sal * W * 0.6 : 0;
          const dy = modo === 0 ? (1 - ent) * H * 0.8 - sal * H * 0.8 : 0;
          const zoom = modo === 2 ? 0.82 + 0.18 * ent + sal * 0.35 : 1;
          const borr = Math.sin(Math.PI * c01(ent < 1 ? ent : sal)) * (modo === 2 ? 10 : 16);
          const empuje = 1 + 0.03 * c01(t / Math.max(1, e.f1 - e.f0));
          const pasos = e.pasos ?? [0];
          const p = (k: number) => (pasos[k] !== undefined ? t - pasos[k] : k === 0 ? t : -1e6);
          return (
            <AbsoluteFill key={e.id} style={{transform: `translate(${dx}px, ${dy}px) scale(${zoom * empuje})`, filter: borr > 0.4 ? `blur(${borr}px)` : undefined, opacity: (modo === 2 ? ent : 1) * (1 - sal * (modo === 2 ? 1 : 0.3))}}>
              <C d={e.d} t={t} dur={e.f1 - e.f0} p={p} />
            </AbsoluteFill>
          );
        })}
        <Hud f={f} esc={actual} nombre={spec.marca.nombre} acento={spec.marca.acento} />
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 60%, rgba(0,0,0,0.28) 100%)', pointerEvents: 'none'}} />
      </AbsoluteFill>
    </MarcaCtx.Provider>
  );
};
