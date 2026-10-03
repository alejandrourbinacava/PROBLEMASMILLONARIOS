import React from 'react';
import {NEGRA, P} from './base';
import {Anim, clamp01, expo, rgb} from './util';

/**
 * El titular de un plano: la frase corta que va en pantalla, con la palabra de
 * acento en rojo y SUBRAYADA. Port de `efectos.render_texto`.
 *
 * Las palabras entre *asteriscos* son las de acento. El rotulo encoge hasta
 * caber en el 86% del ancho (no baja de 56 px): el que lo escribe no tiene
 * que adivinar cuantos caracteres caben.
 */
let lienzo: CanvasRenderingContext2D | null = null;
const ctx = () => {
  if (!lienzo) lienzo = document.createElement('canvas').getContext('2d');
  return lienzo!;
};

const medir = (txt: string, px: number) => {
  const c = ctx();
  c.font = `${px}px "${NEGRA}"`;
  const m = c.measureText(txt);
  return {ancho: m.width, baja: m.actualBoundingBoxDescent};
};

type Parte = {txt: string; acento: boolean};

const partir = (txt: string): Parte[] => {
  const partes: Parte[] = [];
  let act = '';
  let en = false;
  for (const ch of txt) {
    if (ch === '*') {
      if (act) partes.push({txt: act, acento: en});
      act = '';
      en = !en;
    } else act += ch;
  }
  if (act) partes.push({txt: act, acento: en});
  return partes;
};

export const Titular: React.FC<{
  spec: any;
  W: number;
  H: number;
  anim: Anim;
  textoYaConMayuscula: string;
  pro?: boolean;
  tLoc?: number; // segundos desde que entra el titular
}> = ({spec, W, H, anim, textoYaConMayuscula, pro, tLoc = 99}) => {
  const partes = partir(textoYaConMayuscula);
  let px: number = spec.px ?? 132;
  const total = (p: number) => partes.reduce((a, x) => a + medir(x.txt, p).ancho, 0);
  let ancho = total(px);
  while (ancho > W * 0.86 && px > 56) {
    px = Math.floor(px * 0.94);
    ancho = total(px);
  }
  const ay: number = spec.y ?? 0.5;
  const claro = spec.halo === 'claro';
  const acento: number[] = spec.acento ?? P.acento;
  const color: number[] = spec.color ?? [255, 255, 255];
  // Pillow dibuja con ancla "la" desde y = ay*H - alto/2, y Poppins tiene el
  // ascendente en 1,05 em: la linea de base cae en ay*H + 0,425 px.
  const base = ay * H + 0.425 * px;
  const x0 = (W - ancho) / 2;

  let x = x0;
  let trozos = partes.map((p) => {
    const w = medir(p.txt, px).ancho;
    const t = {...p, x, w, baja: medir(p.txt, px).baja, p: 1, dy: 0};
    x += w;
    return t;
  });
  if (pro) {
    // palabra a palabra: cada una sube con frenada larga, 70 ms despues de la
    // anterior. Es lo que separa un rotulo que se escribe de uno que aparece.
    const palabras: typeof trozos = [];
    let cursor = x0;
    let k = 0;
    for (const p of partes) {
      for (const pedazo of p.txt.split(/(\s+)/)) {
        if (!pedazo) continue;
        const w = medir(pedazo, px).ancho;
        const esEspacio = /^\s+$/.test(pedazo);
        const prog = esEspacio ? 1 : expo(clamp01((tLoc - k * 0.07) / 0.38));
        palabras.push({
          txt: pedazo,
          acento: p.acento,
          x: cursor,
          w,
          baja: medir(pedazo, px).baja,
          p: prog,
          dy: (1 - prog) * 38,
        });
        if (!esEspacio) k++;
        cursor += w;
      }
    }
    trozos = palabras;
  }
  const sigma = px * 0.22;

  return (
    <svg
      width={W}
      height={H}
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        opacity: anim.op,
        transform: `translate(${anim.dx}px, ${anim.dy}px) scale(${anim.scale})`,
        transformOrigin: '50% 50%',
      }}
    >
      <defs>
        <filter id="halo-titular" x="-20%" y="-60%" width="140%" height="220%">
          <feGaussianBlur stdDeviation={sigma} />
        </filter>
      </defs>
      {claro && (
        <g filter="url(#halo-titular)" opacity={0.88}>
          {[0, 1].map((k) =>
            trozos.map((t, i) => (
              <text
                key={`${k}-${i}`}
                x={t.x}
                y={base}
                fontFamily={`"${NEGRA}"`}
                fontSize={px}
                fill="#fff"
              >
                {t.txt}
              </text>
            )),
          )}
        </g>
      )}
      {trozos.map((t, i) => (
        <text
          key={i}
          x={t.x}
          y={base + t.dy}
          opacity={t.p}
          fontFamily={`"${NEGRA}"`}
          fontSize={px}
          fill={rgb(t.acento ? acento : color)}
          style={{whiteSpace: 'pre'}}
        >
          {t.txt}
        </text>
      ))}
      {/* el SUBRAYADO ROJO de las miniaturas: la firma grafica del canal */}
      {claro &&
        trozos
          .filter((t) => t.acento)
          .map((t, i) => (
            <rect
              key={`u${i}`}
              x={t.x}
              y={base + t.baja + Math.max(4, Math.floor(px * 0.05))}
              width={t.w * t.p}
              height={Math.max(5, Math.floor(px / 14))}
              rx={3}
              fill={rgb(acento)}
            />
          ))}
    </svg>
  );
};
