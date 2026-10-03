import React, {useLayoutEffect, useRef, useState} from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Plato as PlatoT, P, useFuentes} from './base';
import {GRAFICOS} from './Graficos';
import {Plato} from './Plato';
import {Titular} from './Titular';
import {Anim, animCapa, atrasK, clamp01, combina, factorAnim, may, rgb, suave} from './util';

/**
 * Un plano de plato entero: el papel, el titular y el grafico, con los
 * mismos tiempos que `render.render_escena` (retardos, entradas, salidas) y el
 * barrido de camara a la entrada o a la salida si el plano lo lleva.
 */
const DUR_LATIGO = 0.22;

/**
 * El bloom de `render.py` (LOOK["bloom"] = 0,38 sobre lo que pasa de 168, aqui a la mitad: el de
 * Pillow se mezcla con un desenfoque y el filtro actua pixel a pixel),
 * como curva por canal: aclara el papel cuatro o cinco puntos y no toca la
 * tinta. Sin esto el papel de Remotion sale mas apagado que el de los planos
 * de metraje que tiene al lado y el corte se nota.
 */
const GRANO = 0.22;
const BLOOM = '0.0000 0.0312 0.0625 0.0938 0.1250 0.1562 0.1875 0.2188 0.2500 0.2812 0.3125 0.3438 0.3750 0.4062 0.4375 0.4688 0.5000 0.5312 0.5625 0.5938 0.6250 0.6562 0.6925 0.7281 0.7627 0.7962 0.8285 0.8598 0.8900 0.9192 0.9472 0.9741 1.0000';


type Banda = {y0: number; y1: number} | null;

/** La franja vertical que ocupa el grafico, para la barra del barrido. */
const useBanda = (ref: React.RefObject<HTMLDivElement | null>, dep: unknown) => {
  const [banda, setBanda] = useState<Banda>(null);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    let y0 = Infinity;
    let y1 = -Infinity;
    el.querySelectorAll<HTMLElement>('div').forEach((d) => {
      const r = d.getBoundingClientRect();
      if (r.height > 20) {
        y0 = Math.min(y0, r.top);
        y1 = Math.max(y1, r.bottom);
      }
    });
    if (isFinite(y0) && (!banda || Math.abs(banda.y0 - y0) > 0.5 || Math.abs(banda.y1 - y1) > 0.5)) {
      setBanda({y0, y1});
    }
  }, [dep, banda]);
  return banda;
};

export const EscenaPlato: React.FC<{plato: PlatoT; W: number; H: number; fps: number; estilo?: string}> = ({
  plato,
  W,
  H,
  fps,
  estilo = 'paridad',
}) => {
  const pro = estilo === 'pro';
  const listo = useFuentes();
  const f = useCurrentFrame();
  const n = plato.frames;
  const refG = useRef<HTMLDivElement>(null);
  const banda = useBanda(refG, f);
  if (!listo) return <AbsoluteFill style={{background: rgb(P.papel)}} />;

  // --- titular -----------------------------------------------------------
  const txt = plato.texto_pantalla;
  let animT: Anim | null = null;
  if (txt) {
    const f0 = Math.floor((txt.retardo ?? 0.35) * fps);
    if (f >= f0) {
      const [te, ts] = factorAnim(Math.max(0, f - f0), n - f0, fps, txt.dur_entrada ?? 0.5, txt.dur_salida ?? 0.4);
      const estiloT = txt.estilo ?? 'sube';
      animT = combina(
        pro ? animCapa('ninguna', 1, W, H) : animCapa(estiloT, te, W, H),
        animCapa(estiloT, ts, W, H, true),
      );
    }
  }

  // --- grafico -----------------------------------------------------------
  const graf = plato.grafico;
  let animG: Anim | null = null;
  let ug = 0;
  let tsG = 0;
  let borde: number | null = null;
  if (graf) {
    const f0 = Math.floor((graf.retardo ?? 0.25) * fps);
    if (f >= f0) {
      const durG = graf.duracion ?? Math.min(1.6, (n / fps) * 0.55);
      ug = Math.min(1, (f - f0) / Math.max(1, Math.floor(durG * fps)));
      tsG = (f - f0) / fps;
      const dEnt = graf.entrada === 'barrido' ? 0.58 : 0.32;
      const [ge, gs] = factorAnim(f - f0, n - f0, fps, dEnt, 0.25);
      if (graf.entrada === 'barrido' && ge < 0.999) {
        borde = -0.12 + 1.24 * suave(clamp01(ge));
        animG = {dx: 0, dy: 0, scale: 1, op: 1, blur: 0};
      } else {
        const estiloG = graf.entrada === 'barrido' ? 'sube' : graf.entrada ?? 'golpe';
        // tras un barrido solo queda la SALIDA (que baja y se desvanece)
        let entrada = graf.entrada === 'barrido' ? animCapa('ninguna', 1, W, H) : animCapa(estiloG, ge, W, H);
        if (pro && graf.entrada !== 'barrido') {
          // "pro": una tarjeta que entra con muelle -pasa de largo y vuelve-,
          // sube desde abajo y se enfoca, en vez del golpe de escala
          const sp = atrasK(ge, 1.3);
          entrada = {dx: 0, dy: (1 - sp) * 30, scale: 0.9 + 0.1 * sp, op: clamp01(ge * 3), blur: (1 - ge) * 5};
        }
        animG = combina(entrada, animCapa(estiloG, gs, W, H, true));
        if (pro) {
          // y mientras el dato esta puesto, no se queda congelado: una deriva
          // muy lenta de escala y una flotacion de un par de pixeles
          const h = f / Math.max(1, n);
          animG = {...animG, scale: animG.scale * (1 + 0.014 * h), dy: animG.dy + Math.sin((f / fps) * 1.6) * 2};
        }
      }
    }
  }
  const Graf = graf ? GRAFICOS[graf.tipo] : null;

  // --- barrido de camara -------------------------------------------------
  const nlat = Math.max(1, Math.floor(fps * DUR_LATIGO));
  let lat: {dx: number; sigma: number; oscuro: number} | null = null;
  const lpar = (dir: number, u: number) => {
    const uu = clamp01(u);
    if (uu <= 0.001) return null;
    return {
      dx: dir * W * 0.95 * uu * uu,
      sigma: W * 0.055 * Math.min(1, 2 * uu) * 0.577,
      oscuro: 1 - 0.22 * uu * uu,
    };
  };
  if (plato.lat_ent !== null && f < nlat) lat = lpar(plato.lat_ent, 1 - f / nlat);
  if (plato.lat_sal !== null && f >= n - nlat) lat = lpar(plato.lat_sal, (f - (n - nlat)) / nlat);

  return (
    <AbsoluteFill style={{background: rgb(P.papel), filter: 'url(#bloom)'}}>
      <svg width={0} height={0} style={{position: 'absolute'}}>
        <defs>
          <filter id="bloom" colorInterpolationFilters="sRGB">
            <feComponentTransfer>
              <feFuncR type="table" tableValues={BLOOM} />
              <feFuncG type="table" tableValues={BLOOM} />
              <feFuncB type="table" tableValues={BLOOM} />
            </feComponentTransfer>
          </filter>
          <filter id="grano" x="0" y="0" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="1" seed={f % 97} result="r" />
            <feColorMatrix in="r" type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  1.2 0 0 0 -0.1" />
          </filter>
          <filter id="latigo" x="-30%" y="0%" width="160%" height="100%">
            <feGaussianBlur stdDeviation={`${lat ? lat.sigma : 0} 0`} />
          </filter>
        </defs>
      </svg>
      <AbsoluteFill
        style={{
          transform: lat ? `translateX(${lat.dx}px)` : undefined,
          filter: lat ? `url(#latigo) brightness(${lat.oscuro})` : undefined,
        }}
      >
        <Plato
          W={W}
          H={H}
          f={f}
          n={n}
          fps={fps}
          acento={plato.acento}
          titulo={plato.fondo_titulo}
          fase={plato.fase}
        />
        {txt && animT && animT.op > 0.01 && (
          <Titular
            spec={txt}
            W={W}
            H={H}
            anim={animT}
            textoYaConMayuscula={may(txt.texto)}
            pro={pro}
            tLoc={(f - Math.floor((txt.retardo ?? 0.35) * fps)) / fps}
          />
        )}
        {graf && Graf && animG && (
          <AbsoluteFill
            style={{
              opacity: animG.op,
              transform: `translate(${animG.dx}px, ${animG.dy}px) scale(${animG.scale})`,
              transformOrigin: '50% 50%',
              filter: animG.blur > 0.3 ? `blur(${animG.blur}px)` : undefined,
              WebkitMaskImage:
                borde !== null
                  ? `linear-gradient(to right, #000 ${(borde - 0.09) * 100}%, transparent ${borde * 100}%)`
                  : undefined,
              maskImage:
                borde !== null
                  ? `linear-gradient(to right, #000 ${(borde - 0.09) * 100}%, transparent ${borde * 100}%)`
                  : undefined,
            }}
          >
            <div ref={refG} style={{position: 'absolute', inset: 0}}>
              <Graf spec={graf} W={W} H={H} u={ug} cy={Math.floor((graf.y ?? 0.5) * H)} pro={pro} ts={tsG} />
            </div>
          </AbsoluteFill>
        )}
        {/* grano de pelicula: Pillow suma ruido gaussiano (sigma 3) a TODO */}
        <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'overlay', opacity: GRANO}}>
          <rect width={W} height={H} filter="url(#grano)" />
        </svg>
        {/* la barra de rotulador que lleva el borde del barrido */}
        {borde !== null && banda && borde < 1.02 && (
          <div
            style={{
              position: 'absolute',
              left: borde * W - 6,
              top: banda.y0 - 14,
              width: 12,
              height: banda.y1 - banda.y0 + 28,
              background: rgb(graf._ac ?? P.acento),
              opacity: 0.82,
            }}
          />
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
