import React, {useContext} from 'react';
import {useCurrentFrame} from 'remotion';
import {Cara, LOOKS, Look, Pose, Rostro} from './Personaje';
import {Ctx, F, L, ci, color, oscurece, poli, rr} from './prim';

/**
 * Personaje de tebeo: cabeza redonda y blanca, cuerpo achaparrado con la
 * ropa del oficio, brazos gruesos que actuan y sombreado de dos tonos.
 * Mismo rig que `Personaje`/`Stick` (cadera en el origen, pies en y=+152).
 */
type Brazo = [number, number];
const POSES: Record<Pose, [Brazo, Brazo]> = {
  quieto: [[16, 8], [16, 8]],
  saluda: [[16, 8], [150, -25]],
  senala: [[16, 8], [86, 0]],
  celebra: [[165, -10], [165, -10]],
  encoge: [[56, 74], [56, 74]],
  sostiene: [[16, 8], [58, 50]],
  cadera: [[44, -48], [44, -48]],
  brazos_cruzados: [[60, -118], [60, -118]],
};
const rad = (g: number) => (g * Math.PI) / 180;

/** Un tubo grueso (brazo o pierna) con contorno y media sombra. */
const Tubo: React.FC<{d: string; c: string; w: number}> = ({d, c, w}) => {
  const t = useContext(Ctx);
  const col = color(t, c);
  return (
    <g>
      <path d={d} fill="none" stroke={t.tinta} strokeWidth={w + 8} strokeLinecap="round" strokeLinejoin="round" />
      <path d={d} fill="none" stroke={oscurece(col, 0.72)} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" />
      <path d={d} fill="none" stroke={col} strokeWidth={w * 0.62} strokeLinecap="round" strokeLinejoin="round" transform="translate(-3,-4)" />
    </g>
  );
};

export const Toon: React.FC<{
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
  const L0: Look = typeof look === 'string' ? LOOKS[look] ?? LOOKS.cliente : look;
  let [bI, bD] = POSES[pose];
  if (pose === 'saluda') bD = [150, -25 + Math.sin((f + semilla * 7) / 3.5) * 26];
  if (pose === 'celebra') {
    const s = Math.sin((f + semilla * 3) / 5) * 14;
    bI = [165 + s, -10];
    bD = [165 - s, -10];
  }
  if (pose === 'senala') bD = [86 + Math.sin((f + semilla * 5) / 9) * 5, 0];
  if (pose === 'sostiene') bD = [58 + Math.sin((f + semilla * 4) / 12) * 6, 50];
  // gesticula: cada medio segundo largo levanta una mano como quien explica
  const gesto = Math.pow(Math.max(0, Math.sin((f + semilla * 11) / 9)), 2);
  if (pose === 'quieto') {
    bD = [16 + 52 * gesto, 8 + 40 * gesto];
    bI = [16 + 26 * Math.pow(Math.max(0, Math.sin((f + semilla * 5) / 13)), 2), 8];
  }
  if (pose === 'cadera') bI = [44 + 10 * gesto, -48];

  const hombros: [number, number][] = [[-62, -168], [62, -168]];
  const brazo = (b: Brazo, lado: -1 | 1, h: [number, number]) => {
    const a = rad(b[0]);
    const c = rad(b[0] + b[1]);
    const codo: [number, number] = [h[0] + lado * Math.sin(a) * 86, h[1] + Math.cos(a) * 86];
    const mano_: [number, number] = [codo[0] + lado * Math.sin(c) * 80, codo[1] + Math.cos(c) * 80];
    return {codo, mano: mano_};
  };
  const aI = brazo(bI, -1, hombros[0]);
  const aD = brazo(bD, 1, hombros[1]);
  const resp = 1 + Math.sin((f + semilla * 5) / 16) * 0.016;
  const cab = Math.sin((f + semilla * 3) / 22) * 3;
  const cruz = pose === 'brazos_cruzados';
  const manga = L0.camisa ?? 'azul';
  const pantalon = L0.pantalon ?? 'oscuro';
  const mitt = (p: [number, number]) => <F d={ci(p[0], p[1], 27)} c="piel" w={5} />;

  return (
    <g transform={`translate(${x},${y + Math.sin((f + semilla * 3) / 4) * 2.5 * k}) rotate(${Math.sin((f + semilla) / 26) * 1.2}) scale(${voltea ? -k : k},${k * resp})`}>
      {piernas && (
        <g>
          <Tubo d="M-30,20 L-36,138" c={pantalon} w={44} />
          <Tubo d="M30,20 L36,138" c={pantalon} w={44} />
          <F d="M-70,150 Q-70,128 -34,128 Q-6,130 -4,150 Q-4,160 -16,160 H-62 Q-70,160 -70,150 Z" c="oscuro" w={5} />
          <F d="M70,150 Q70,128 34,128 Q6,130 4,150 Q4,160 16,160 H62 Q70,160 70,150 Z" c="oscuro" w={5} />
        </g>
      )}
      {/* brazo del fondo */}
      {!cruz && (
        <g>
          <Tubo d={`M${hombros[0][0]},${hombros[0][1]} L${aI.codo[0]},${aI.codo[1]} L${aI.mano[0]},${aI.mano[1]}`} c={manga} w={44} />
          {mitt(aI.mano)}
        </g>
      )}
      {/* tronco */}
      <F d={rr(-82, -196, 164, 232, 64)} c={manga} w={6} />
      {L0.delantal && <F d={rr(-56, -104, 112, 140, 18)} c={L0.delantal} w={5} />}
      {L0.delantal && <L d="M-36,-104 L-30,-190 M36,-104 L30,-190" c="oscuro" w={6} />}
      {L0.corbata && <F d={poli([[-13, -200], [13, -200], [18, -120], [0, -92], [-18, -120]])} c={L0.corbata} w={4} />}
      {L0.camisa === 'oscuro' && <F d={poli([[-26, -196], [0, -150], [26, -196]])} c="blanco" w={4} />}
      {/* brazo delantero */}
      {cruz ? (
        <g>
          <Tubo d="M-62,-168 L30,-120 L-44,-104" c={manga} w={44} />
          <Tubo d="M62,-168 L-30,-134 L40,-112" c={manga} w={44} />
          {mitt([-44, -104])}
          {mitt([40, -112])}
        </g>
      ) : (
        <g>
          <Tubo d={`M${hombros[1][0]},${hombros[1][1]} L${aD.codo[0]},${aD.codo[1]} L${aD.mano[0]},${aD.mano[1]}`} c={manga} w={44} />
          {mitt(aD.mano)}
          {mano && <g transform={`translate(${aD.mano[0]},${aD.mano[1]})`}>{mano}</g>}
        </g>
      )}
      {/* cabeza */}
      <g transform={`rotate(${cab} 0 -230)`}>
        {L0.peloEstilo === 'largo' && (
          <g>
            <F d={rr(-116, -330, 52, 180, 26)} c={L0.pelo ?? 'oscuro'} w={5} />
            <F d={rr(64, -330, 52, 180, 26)} c={L0.pelo ?? 'oscuro'} w={5} />
          </g>
        )}
        {L0.peloEstilo === 'mono' && <F d={ci(0, -412, 38)} c={L0.pelo ?? 'oscuro'} w={5} />}
        <F d={ci(0, -300, 98)} c="piel" w={6} />
        {(L0.peloEstilo === 'corto' || !L0.peloEstilo) && (
          <F d="M-96,-318 Q-100,-410 0,-404 Q100,-410 96,-318 Q50,-366 0,-362 Q-50,-366 -96,-318 Z" c={L0.pelo ?? 'oscuro'} w={5} />
        )}
        {L0.peloEstilo === 'largo' && (
          <F d="M-96,-312 Q-100,-410 0,-404 Q100,-410 96,-312 Q50,-362 0,-358 Q-50,-362 -96,-312 Z" c={L0.pelo ?? 'oscuro'} w={5} />
        )}
        {L0.peloEstilo === 'mono' && (
          <F d="M-96,-318 Q-100,-408 0,-402 Q100,-408 96,-318 Q50,-362 0,-358 Q-50,-362 -96,-318 Z" c={L0.pelo ?? 'oscuro'} w={5} />
        )}
        {L0.peloEstilo === 'canoso' && (
          <F d="M-96,-318 Q-100,-408 0,-402 Q100,-408 96,-318 Q50,-360 0,-356 Q-50,-360 -96,-318 Z" c="gris" w={5} />
        )}
        {L0.peloEstilo === 'rizado' &&
          [-66, -33, 0, 33, 66].map((px) => <F key={px} d={ci(px, -390 + Math.abs(px) * 0.28, 32)} c="oscuro" w={4} />)}
        {L0.peloEstilo === 'gorra' && (
          <g>
            <F d="M-92,-322 Q-96,-410 0,-414 Q96,-410 92,-322 Z" c={L0.gorro ?? 'rojo'} w={5} />
            <F d="M30,-336 H140 Q146,-312 112,-308 H30 Z" c={L0.gorro ?? 'rojo'} w={5} />
          </g>
        )}
        {L0.gorro && L0.peloEstilo !== 'gorra' && <F d={rr(-70, -468, 140, 78, 24)} c={L0.gorro} w={5} />}
        <g transform="translate(0,-300) scale(1.45) translate(0,292)">
          <Rostro cara={cara} f={f} semilla={semilla} gafas={L0.gafas} bigote={L0.bigote} rubor={false} />
        </g>
      </g>
    </g>
  );
};
