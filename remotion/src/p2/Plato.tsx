import React from 'react';
import {AbsoluteFill} from 'remotion';
import {MEDIA, NEGRA, P, T} from './base';
import {atras, clamp01, rgb, suave} from './util';

/**
 * El plato del canal: la hoja de papel cuadriculado sobre la que se pone un
 * dato. Es el PORT de `efectos.plato` / `_plato_fondo` / `_plato_reticula`.
 *
 * Lo que se mueve: la cuadricula deriva despacio en diagonal y una sombra
 * cruza la pagina una sola vez, como cuando alguien pasa la mano por una hoja.
 * Un fondo de datos que se mueve mucho compite con el dato; lo que tiene que
 * hacer es no estar quieto del todo.
 */
const PASO = 46; // lado del cuadro, en pixeles

// Sobre papel la linea RESTA, que es lo que hace un lapiz; el tinte es azulado.
// Pillow resta (0.55, 0.32, 0.16) * 0.42 * intensidad; en CSS eso es una
// capa `multiply` del color que deja el papel (~245) restado.
const LINEA_FINA = 'rgb(235,243,249)'; // intensidad 120, ya atenuada por el bloom
const LINEA_GORDA = 'rgb(222,236,246)'; // intensidad 200 (cada quinta)

const fondoPapel = () => {
  // v = clip(1 - r*0.92)^1.35 con r elipitico; papel - (1 - v) * 16
  const stops: string[] = [];
  for (let i = 0; i <= 10; i++) {
    const r = i / 10; // 0..1 sobre el radio elipitico
    const v = Math.pow(Math.max(0, Math.min(1, 1 - r * 0.92)), 1.35);
    const c = P.papel.map((x) => Math.round(x - (1 - v) * 16));
    stops.push(`rgb(${c[0]},${c[1]},${c[2]}) ${i * 10}%`);
  }
  // r = sqrt((1.02 dx)^2 + (1.32 dy)^2): el radio 1 llega a 1/1.02 del ancho
  // y a 1/1.32 del alto, centrado un poco por encima del medio.
  return `radial-gradient(ellipse 98% 75.8% at 50% 44%, ${stops.join(',')})`;
};

export const Plato: React.FC<{
  W: number;
  H: number;
  f: number;
  n: number;
  fps: number;
  acento: number[];
  titulo: string;
  fase: number;
}> = ({W, H, f, n, fps, acento, titulo, fase}) => {
  const t = f / Math.max(1, n - 1);
  const dur = n / fps;
  const s = fase >= 0.5 ? -1 : 1;
  const dx = (((t * 0.55 * s) % 1) + 1) % 1 * PASO;
  const dy = ((((1 - t * 0.38 * s) % 1) + 1) % 1) * PASO;

  // la sombra que cruza
  const cx = s > 0 ? -0.25 + 1.5 * t : 1.25 - 1.5 * t;
  const sombra = [0, 0.25, 0.5, 0.75, 1].map((q) => {
    const g = Math.exp(-Math.pow(q * 2.2, 2));
    return `rgb(${Math.round(255 - g * 9)},${Math.round(255 - g * 8)},${Math.round(255 - g * 10)}) ${q * 100}%`;
  });

  // el epigrafe y la regla entran y salen con el plano
  const seg = t * dur;
  const ent = clamp01(seg / 0.42);
  const sal = clamp01((dur - seg) / 0.34);
  const vis = suave(ent) * suave(sal);

  const yb = Math.floor(H * 0.915);
  const xIni = Math.floor(W * 0.055);
  const reglaFin = xIni + (W * 0.945 - xIni) * suave(ent) * suave(sal);
  const xm = xIni + 82;
  const x0 = Math.floor(W * 0.09) - Math.floor(70 * (1 - atras(ent)));
  const y0 = Math.floor(H * 0.135);

  return (
    <AbsoluteFill style={{background: fondoPapel()}}>
      {/* cuadricula: cada quinta linea mas marcada */}
      <AbsoluteFill
        style={{
          mixBlendMode: 'multiply',
          backgroundImage: [
            `linear-gradient(to right, ${LINEA_GORDA} 1px, transparent 1px)`,
            `linear-gradient(to bottom, ${LINEA_GORDA} 1px, transparent 1px)`,
            `linear-gradient(to right, ${LINEA_FINA} 1px, transparent 1px)`,
            `linear-gradient(to bottom, ${LINEA_FINA} 1px, transparent 1px)`,
          ].join(','),
          backgroundSize: `${PASO * 5}px ${PASO * 5}px, ${PASO * 5}px ${PASO * 5}px, ${PASO}px ${PASO}px, ${PASO}px ${PASO}px`,
          backgroundPosition: `${-dx}px ${-dy}px`,
        }}
      />
      {/* sombra de la pagina */}
      <AbsoluteFill
        style={{
          mixBlendMode: 'multiply',
          background: `radial-gradient(${576 * 2.2}px ${810 * 2.2}px at ${cx * W}px ${0.4 * H}px, ${sombra.join(',')})`,
        }}
      />
      <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
        {/* la regla de la banda: se traza de izquierda a derecha */}
        {reglaFin > xIni + 2 && (
          <rect
            x={xIni}
            y={yb - 36}
            width={reglaFin - xIni}
            height={5}
            fill={rgb(acento)}
            opacity={0.78}
          />
        )}
        {/* el sello del canal: un euro blanco sobre tinta roja maciza */}
        <circle cx={xIni + 30} cy={yb + 4} r={30} fill={rgb(acento)} />
        <T x={xIni + 30} y={yb + 4 + 14} px={38} familia={NEGRA} fill="#fff" anchor="middle">
          €
        </T>
        <T x={xm} y={yb - 2} px={29} familia={NEGRA} fill={rgb(P.tinta)} op={0.96} esp={6}>
          PROBLEMAS MILLONARIOS
        </T>
        <T x={xm} y={yb + 30} px={21} familia={MEDIA} fill={rgb(P.tenue)} op={0.84} esp={5}>
          EL PRECIO DE SER EL DUEÑO
        </T>
        {/* el epigrafe del capitulo */}
        {titulo && vis > 0.01 && (
          <g opacity={vis}>
            <rect x={x0 - 4} y={y0 - 26} width={8} height={32} rx={3} fill={rgb(acento)} opacity={0.92} />
            <T x={x0 + 22} y={y0} px={30} familia={MEDIA} fill={rgb(P.tinta)} esp={5} op={0.96}>
              {titulo.toUpperCase()}
            </T>
          </g>
        )}
      </svg>
    </AbsoluteFill>
  );
};
