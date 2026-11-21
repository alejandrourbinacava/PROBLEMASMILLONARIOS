import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {EP} from './base';
import {Metraje} from './capas';
import {Chip, Escenario, Eti, FONDO, Hoja, PAL, Serif, T, c01, io, lerp, pop, rebote, tr} from './kit';

/**
 * Escenas POR CAPAS con imagen real, como las de Moatseek:
 *
 *   fondo real desenfocado  ->  texto grande DETRAS  ->  recorte limpio delante  ->  graficos encima
 *
 * El sujeto (una persona, un edificio, un producto: `c_<nombre>.webp`, lo saca
 * `recortes.py --limpio`) tapa parte del texto, y eso es lo que da la profundidad.
 */
export type Ctx = EP['ctx'];
/** Nombre de fichero del medio `nombre` (sin extension) entre los que el plano declara en `fotos`. */
export const med = (ctx: Ctx, nombre: string): string | undefined => (ctx?.medios ?? []).find((m: any) => String(m.src).replace(/\.\w+$/, '') === nombre)?.src;

/** Metraje o foto real a sangre, desenfocado y bajado de luz. Corta entre los clips del plano. */
export const FondoReal: React.FC<{ctx: Ctx; t: number; dur: number; blur?: number; luz?: number}> = ({ctx, t, dur, blur = 11, luz = 0.5}) => {
  const clips: any[] = (ctx as any)?.clips ?? [];
  if (!clips.length || !ctx) return <Escenario />;
  let k = 0;
  for (let j = 0; j < clips.length; j++) if (t >= clips[j].en) k = j;
  const c = clips[k];
  const fin = k + 1 < clips.length ? clips[k + 1].en : dur + 12;
  const u = c01((t - c.en) / Math.max(1, fin - c.en));
  return (
    <AbsoluteFill style={{background: FONDO, overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${1.14 + 0.07 * u})`, filter: `blur(${blur}px) brightness(${luz}) saturate(0.92)`}}>
        <Metraje key={k} m={c} abs={ctx.f0 + c.en} dur={fin - c.en + 2} fps={ctx.fps} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(11,12,16,0.42) 0%, rgba(11,12,16,0.08) 42%, rgba(11,12,16,0.6) 100%)'}} />
    </AbsoluteFill>
  );
};

/** Recorte limpio. Su base (centro abajo) esta en (x, y). Entra desde `de` y se queda. */
export const Sujeto: React.FC<{src?: string; x: number; y: number; alto?: number; ancho?: number; t: number; de?: 'aba' | 'izq' | 'der' | 'arr' | 'pop'; rot?: number; op?: number; lejos?: number; gris?: number}> = ({src, x, y, alto, ancho, t, de = 'aba', rot = 0, op = 1, lejos = 260, gris = 0}) => {
  if (t < 0 || !src) return null;
  const u = rebote(t / 15, 0.7);
  const d = (1 - u) * lejos;
  const dx = de === 'izq' ? -d : de === 'der' ? d : 0;
  const dy = de === 'aba' ? d : de === 'arr' ? -d : 0;
  const s = de === 'pop' ? 0.4 + 0.6 * rebote(t / 12, 1.6) : 1;
  return (
    <div style={{position: 'absolute', left: x + dx, top: y + dy, width: 0, height: 0, opacity: c01(t / 4) * op}}>
      <Img src={staticFile('vox/media/' + src)} style={{position: 'absolute', height: alto, width: ancho, maxWidth: 'none', transform: `translate(-50%, -100%) rotate(${rot}deg) scale(${s})`, transformOrigin: '50% 100%', filter: `drop-shadow(0 26px 34px rgba(0,0,0,0.55)) grayscale(${gris})`}} />
    </div>
  );
};

/** Texto enorme en serif que va DETRAS del sujeto. */
export const Detras: React.FC<{x: number; y: number; t: number; children: React.ReactNode; tam?: number; color?: string; ancla?: 'c' | 'i' | 'd'; op?: number}> = ({x, y, t, children, tam = 300, color = '#F4F5F7', ancla = 'c', op = 1}) =>
  t < 0 ? null : (
    <T x={x} y={y + (1 - rebote(t / 14, 0.6)) * 60} ancla={ancla} op={c01(t / 5) * op}>
      <span style={{font: `600 ${tam}px/1 'M Serif'`, color, letterSpacing: -tam * 0.03, textShadow: '0 10px 60px rgba(0,0,0,0.45)'}}>{children}</span>
    </T>
  );

/** 50-56 s · antes, arreglar lo de casa: los productos frescos. */
export const Frescos: React.FC<EP> = ({t, p, dur, ctx}) => (
  <AbsoluteFill>
    <FondoReal ctx={ctx} t={t} dur={dur} blur={9} luz={0.5} />
    <T x={960} y={120} s={pop(t, 11, 1.4)}>
      <Chip tam={40} color="humo">Según contó el propio Roig</Chip>
    </T>
    <T x={960} y={450} op={tr(t, 4, 8) * (1 - tr(p(1), -5, 6))}>
      <Serif tam={110} peso={600}>Antes tenía que arreglar</Serif>
    </T>
    <T x={960} y={610} op={tr(t, 9, 8) * (1 - tr(p(1), -5, 6))}>
      <Serif tam={96} peso={600} color="#FFD95A">algo que no le funcionaba en casa</Serif>
    </T>
    <Detras x={960} y={330} t={p(1)} tam={380}>frescos</Detras>
    <Sujeto src="g_frescos.webp" x={960} y={1230} ancho={900} t={p(1) - 4} de="aba" />
  </AbsoluteFill>
);

/** 71-74 s · traducido: se puede llegar en camion desde los almacenes que ya tiene. */
export const CamionReal: React.FC<EP> = ({t, p, dur, ctx}) => {
  const x = lerp(520, 1210, io(tr(p(1), -6, 58)));
  return (
    <AbsoluteFill>
      <FondoReal ctx={ctx} t={t} dur={dur} blur={12} luz={0.42} />
      <T x={960} y={96} s={pop(t, 11, 1.4)}>
        <Chip tam={38}>Traducido</Chip>
      </T>
      <Detras x={960} y={330} t={p(1) - 4} tam={300}>en camión</Detras>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d="M985,520 L985,1010" stroke="#fff" strokeWidth={6} strokeDasharray="20 18" opacity={0.75 * tr(t, 6, 8)} />
      </svg>
      <T x={985} y={486} op={tr(t, 8, 8)}>
        <Eti tam={28} color="#fff">frontera</Eti>
      </T>
      <Sujeto src="g_nave.webp" x={400} y={930} ancho={820} t={t - 2} de="izq" />
      <Sujeto src="g_super_m.webp" x={1560} y={940} ancho={680} t={t - 6} de="der" />
      <T x={420} y={600} op={tr(t, 10, 8)}>
        <Chip tam={40} fondo="#F4F5F7" tinta="#0B0C10">España · sus almacenes</Chip>
      </T>
      <T x={1500} y={600} op={tr(t, 14, 8)}>
        <Chip tam={40}>Portugal</Chip>
      </T>
      <Sujeto src="g_camion_m.webp" x={x} y={1040 + Math.sin(x / 9) * 2} ancho={640} t={t - 8} de="izq" lejos={500} />
    </AbsoluteFill>
  );
};

/** 125-130 s · julio de 2019: la primera tienda, en Canidelo, junto a Oporto. Y la cuenta. */
export const CanideloReal: React.FC<EP> = ({t, p, dur, ctx}) => (
  <AbsoluteFill>
    <FondoReal ctx={ctx} t={t} dur={dur} blur={10} luz={0.5} />
    <Hoja x={166} y={170} anio="2019" s={1.1 * pop(t, 12, 1.4)} color="verde" />
    <T x={290} y={134} ancla="i" op={tr(t, 4, 8)}>
      <Eti tam={30} color="#B9FFD9">2 de julio</Eti>
    </T>
    <T x={286} y={208} ancla="i" op={tr(t, 6, 8)}>
      <Serif tam={72} peso={600}>Abre la primera tienda</Serif>
    </T>
    <Detras x={840} y={440} t={t - 4} tam={290}>Canidelo</Detras>
    <Sujeto src="g_tienda_m.webp" x={900} y={1000} ancho={1620} t={t - 8} de="aba" />
    <T x={380} y={980} s={pop(p(1), 11, 1.5)} rot={-3}>
      <Chip tam={44} fondo="#F4F5F7" tinta="#0B0C10">junto a Oporto</Chip>
    </T>
    <div style={{position: 'absolute', left: 1630, top: 150, width: 0, height: 0, transform: `rotate(5deg) scale(${0.9 * pop(p(2), 12, 1.5)})`, opacity: c01(p(2) / 3)}}>
      <div style={{position: 'absolute', left: -230, top: -40, width: 460, background: '#FAFAF7', padding: '30px 34px 44px', boxShadow: '0 30px 70px rgba(0,0,0,0.6)', clipPath: 'polygon(0 0,100% 0,100% 94%,94% 100%,88% 94%,82% 100%,76% 94%,70% 100%,64% 94%,58% 100%,52% 94%,46% 100%,40% 94%,34% 100%,28% 94%,22% 100%,16% 94%,10% 100%,4% 94%,0 100%)'}}>
        <div style={{font: "800 30px 'D Sans'", letterSpacing: 4, color: '#1B1D22', textAlign: 'center', borderBottom: '3px dashed #9AA1AE', paddingBottom: 16, marginBottom: 14}}>LA CUENTA DE PORTUGAL</div>
        {['El plan', 'Al abrir', 'Hasta 2025'].map((x) => (
          <div key={x} style={{display: 'flex', justifyContent: 'space-between', font: "600 34px/1.7 'D Sans'", color: '#3A4050'}}>
            <span>{x}</span>
            <span style={{color: '#C4161C', fontWeight: 800}}>? M€</span>
          </div>
        ))}
      </div>
    </div>
  </AbsoluteFill>
);

export const CAPAS = {frescos: Frescos, camion: CamionReal, canidelo: CanideloReal};
export {PAL};
