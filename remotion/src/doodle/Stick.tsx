import React, {useContext} from 'react';
import {useCurrentFrame} from 'remotion';
import {Cara, LOOKS, Look, Pose, Rostro} from './Personaje';
import {Ctx, F, L, ci, color, el, poli, rr} from './prim';

/**
 * Muneco de palitos con cuerpo de color: cabeza blanca, tronco redondeado del
 * color de la camiseta y brazos y piernas de linea. Mismas poses y caras que
 * `Personaje`, mismo origen (cadera) y mismo tamano (pies en y=+152).
 */
type Brazo = [number, number]; // [angulo desde abajo hacia afuera, codo]
const POSES: Record<Pose, [Brazo, Brazo]> = {
  quieto: [[14, 6], [14, 6]],
  saluda: [[14, 6], [150, -25]],
  senala: [[14, 6], [88, 0]],
  celebra: [[165, -10], [165, -10]],
  encoge: [[52, 72], [52, 72]],
  sostiene: [[14, 6], [55, 48]],
  cadera: [[42, -46], [42, -46]],
  brazos_cruzados: [[60, -118], [60, -118]],
};

const rad = (g: number) => (g * Math.PI) / 180;

export const Stick: React.FC<{
  x: number;
  y: number;
  k?: number;
  look?: string | Look;
  pose?: Pose;
  cara?: Cara;
  voltea?: boolean;
  semilla?: number;
  mano?: React.ReactNode;
  piernas?: boolean;
}> = ({x, y, k = 1, look = 'cliente', pose = 'quieto', cara = 'feliz', voltea = false, semilla = 0, mano, piernas = true}) => {
  const f = useCurrentFrame();
  const t = useContext(Ctx);
  const L0: Look = typeof look === 'string' ? LOOKS[look] ?? LOOKS.cliente : look;
  const ink = t.tinta;
  const camisa = color(t, L0.camisa ?? 'azul');
  let [bI, bD] = POSES[pose];
  if (pose === 'saluda') bD = [150, -25 + Math.sin((f + semilla * 7) / 3.5) * 24];
  if (pose === 'celebra') {
    const s = Math.sin((f + semilla * 3) / 5) * 12;
    bI = [165 + s, -10];
    bD = [165 - s, -10];
  }
  if (pose === 'senala') bD = [88 + Math.sin((f + semilla * 5) / 9) * 4, 0];

  const S: [number, number][] = [[-8, -200], [8, -200]];
  const brazo = (b: Brazo, lado: -1 | 1, hombro: [number, number]) => {
    const a = rad(b[0]);
    const c = rad(b[0] + b[1]);
    const codo: [number, number] = [hombro[0] + lado * Math.sin(a) * 88, hombro[1] + Math.cos(a) * 88];
    const mano_: [number, number] = [codo[0] + lado * Math.sin(c) * 82, codo[1] + Math.cos(c) * 82];
    return {codo, mano: mano_};
  };
  const aI = brazo(bI, -1, S[0]);
  const aD = brazo(bD, 1, S[1]);
  const resp = 1 + Math.sin((f + semilla * 5) / 18) * 0.012;
  const cab = Math.sin((f + semilla * 3) / 22) * 2.2;
  const cruz = pose === 'brazos_cruzados';

  return (
    <g transform={`translate(${x},${y}) scale(${voltea ? -k : k},${k * resp})`}>
      {/* piernas */}
      {piernas && (
        <g>
          <L d="M-14,10 Q-40,80 -50,150" w={15} />
          <L d="M14,10 Q40,80 50,150" w={15} />
          <F d={el(-62, 152, 36, 13)} c="oscuro" w={4} />
          <F d={el(62, 152, 36, 13)} c="oscuro" w={4} />
        </g>
      )}
      {/* brazo del fondo */}
      {!cruz && <L d={`M${S[0][0]},${S[0][1]} L${aI.codo[0]},${aI.codo[1]} L${aI.mano[0]},${aI.mano[1]}`} w={15} />}
      {/* tronco */}
      <F d={rr(-44, -214, 88, 250, 42)} c={L0.camisa ?? 'azul'} w={7} />
      {L0.delantal && <F d={poli([[-34, -110], [34, -110], [40, 30], [-40, 30]])} c={L0.delantal} w={5} />}
      {L0.corbata && <F d={poli([[-9, -208], [9, -208], [14, -140], [0, -118], [-14, -140]])} c={L0.corbata} w={4} />}
      {/* brazo delantero */}
      {cruz ? (
        <g>
          <L d="M-8,-190 L40,-130 L-30,-120" w={15} />
          <L d="M8,-190 L-40,-140 L30,-125" w={15} />
        </g>
      ) : (
        <L d={`M${S[1][0]},${S[1][1]} L${aD.codo[0]},${aD.codo[1]} L${aD.mano[0]},${aD.mano[1]}`} w={15} />
      )}
      {!cruz && mano && <g transform={`translate(${aD.mano[0]},${aD.mano[1]})`}>{mano}</g>}
      {/* cabeza */}
      <g transform={`rotate(${cab} 0 -230)`}>
        {L0.peloEstilo === 'largo' && <L d="M-62,-300 Q-84,-250 -66,-210 M62,-300 Q84,-250 66,-210" c="tinta" w={14} />}
        {L0.peloEstilo === 'mono' && <F d={ci(0, -372, 26)} c={L0.pelo ?? 'oscuro'} w={5} />}
        <F d={ci(0, -292, 70)} c="blanco" w={8} />
        {L0.peloEstilo === 'corto' && <path d="M-66,-312 Q-60,-370 0,-364 Q60,-370 66,-312 Q30,-340 0,-336 Q-30,-340 -66,-312 Z" fill={ink} />}
        {L0.peloEstilo === 'canoso' && <path d="M-66,-312 Q-60,-366 0,-362 Q60,-366 66,-312 Q30,-336 0,-334 Q-30,-336 -66,-312 Z" fill={color(t, 'gris')} stroke={ink} strokeWidth={5} />}
        {L0.peloEstilo === 'rizado' &&
          [-48, -24, 0, 24, 48].map((px) => <F key={px} d={ci(px, -356 + Math.abs(px) * 0.25, 20)} c="oscuro" w={4} />)}
        {L0.peloEstilo === 'gorra' && (
          <g>
            <F d="M-68,-316 Q-70,-376 0,-380 Q70,-376 68,-316 Z" c={L0.gorro ?? 'rojo'} w={6} />
            <F d="M20,-322 H110 Q116,-304 92,-302 H20 Z" c={L0.gorro ?? 'rojo'} w={5} />
          </g>
        )}
        {L0.gorro && L0.peloEstilo !== 'gorra' && <F d={rr(-52, -418, 104, 60, 18)} c={L0.gorro} w={5} />}
        <g transform="translate(0,-292) scale(0.86) translate(0,292)">
          <Rostro cara={cara} f={f} semilla={semilla} gafas={L0.gafas} bigote={L0.bigote} rubor={false} />
        </g>
      </g>
    </g>
  );
};
