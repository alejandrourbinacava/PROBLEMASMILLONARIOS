import React from 'react';
import {useCurrentFrame} from 'remotion';
import {F, L, R, ci, el, poli, rr} from './prim';

/**
 * Personaje de cuerpo entero con poses y caras. El origen es el centro de la
 * cadera; mide unos 640 de alto (pies en y=+150, coronilla en y=-345).
 */
export type Cara = 'feliz' | 'serio' | 'sorpresa' | 'preocupado' | 'pensando' | 'enfadado';
export type Pose = 'quieto' | 'saluda' | 'senala' | 'celebra' | 'encoge' | 'sostiene' | 'cadera' | 'brazos_cruzados';
export type Pelo = 'corto' | 'largo' | 'mono' | 'calvo' | 'gorra' | 'canoso' | 'rizado';

export type Look = {
  piel?: string;
  pelo?: string;
  peloEstilo?: Pelo;
  camisa?: string;
  delantal?: string | null;
  pantalon?: string;
  gafas?: boolean;
  corbata?: string | null;
  bigote?: boolean;
  gorro?: string | null;
};

export const LOOKS: Record<string, Look> = {
  duena: {piel: 'piel', pelo: 'madera', peloEstilo: 'mono', camisa: 'azul', delantal: 'rojo', pantalon: 'oscuro'},
  duenio: {piel: 'piel', pelo: 'oscuro', peloEstilo: 'corto', camisa: 'verde', delantal: 'blanco', pantalon: 'oscuro', bigote: true},
  cliente: {piel: 'piel', pelo: 'oscuro', peloEstilo: 'corto', camisa: 'amarillo', pantalon: 'azul'},
  cliente2: {piel: '#E8B48E', pelo: 'madera', peloEstilo: 'largo', camisa: 'rosa', pantalon: 'oscuro'},
  cliente3: {piel: '#C98E63', pelo: 'oscuro', peloEstilo: 'rizado', camisa: 'verde', pantalon: 'gris'},
  casero: {piel: 'piel', pelo: 'gris', peloEstilo: 'canoso', camisa: 'oscuro', corbata: 'rojo', pantalon: 'oscuro', gafas: true, bigote: true},
  jefe: {piel: 'piel', pelo: 'gris', peloEstilo: 'canoso', camisa: 'oscuro', corbata: 'amarillo', pantalon: 'oscuro', gafas: true},
  funcionario: {piel: '#E8B48E', pelo: 'oscuro', peloEstilo: 'corto', camisa: 'cielo', corbata: 'azul', pantalon: 'oscuro', gafas: true},
  camarero: {piel: 'piel', pelo: 'oscuro', peloEstilo: 'corto', camisa: 'blanco', delantal: 'oscuro', pantalon: 'oscuro'},
  taxista: {piel: '#E8B48E', pelo: 'oscuro', peloEstilo: 'gorra', camisa: 'blanco', corbata: 'oscuro', pantalon: 'oscuro', gorro: 'amarillo'},
  cocinero: {piel: 'piel', pelo: 'oscuro', peloEstilo: 'corto', camisa: 'blanco', delantal: 'blanco', pantalon: 'gris', gorro: 'blanco'},
  burger: {piel: 'piel', pelo: 'oscuro', peloEstilo: 'gorra', camisa: 'rojo', delantal: 'amarillo', pantalon: 'oscuro', gorro: 'rojo'},
  peluquera: {piel: 'piel', pelo: 'morado', peloEstilo: 'largo', camisa: 'oscuro', delantal: 'blanco', pantalon: 'oscuro'},
  repartidor: {piel: '#C98E63', pelo: 'oscuro', peloEstilo: 'gorra', camisa: 'naranja', pantalon: 'azul', gorro: 'naranja'},
  estanquero: {piel: 'piel', pelo: 'gris', peloEstilo: 'canoso', camisa: 'madera', delantal: 'oscuro', pantalon: 'oscuro', bigote: true},
};

const POSES: Record<Pose, [number, number]> = {
  // angulo (grados) de cada brazo hacia afuera/arriba: [izquierdo de pantalla, derecho de pantalla]
  quieto: [8, 8],
  saluda: [8, 150],
  senala: [8, 82],
  celebra: [160, 160],
  encoge: [48, 48],
  sostiene: [8, 62],
  cadera: [38, 38],
  brazos_cruzados: [-10, -10],
};

const Brazo: React.FC<{lado: 1 | -1; ang: number; manga: string; piel: string; mano?: React.ReactNode}> = ({lado, ang, manga, piel, mano}) => (
  // lado 1 = izquierdo de pantalla (x negativo)
  <g transform={`translate(${-lado * 86},-140) rotate(${lado * ang})`}>
    <F d={rr(-19, -8, 38, 140, 18)} c={manga} w={5} />
    <F d={ci(0, 144, 25)} c={piel} w={5} />
    {mano && <g transform="translate(0,150)">{mano}</g>}
  </g>
);

const PeloAtras: React.FC<{e: Pelo; c: string}> = ({e, c}) =>
  e === 'largo' ? <F d={rr(-84, -352, 168, 128, 54)} c={c} /> : e === 'mono' ? <F d={ci(0, -432, 36)} c={c} /> : null;

const PeloFrente: React.FC<{e: Pelo; c: string; gorro?: string | null}> = ({e, c, gorro}) => {
  if (e === 'calvo') return <L d="M-30,-405 q10,-14 20,0 M12,-405 q10,-14 20,0" c={c} w={6} />;
  if (e === 'gorra')
    return (
      <g>
        <F d="M-76,-332 Q-80,-412 0,-416 Q80,-412 76,-332 Z" c={gorro ?? 'rojo'} />
        <F d={rr(-86, -354, 172, 24, 10)} c={gorro ?? 'rojo'} w={5} />
        <F d="M30,-348 H130 Q134,-326 104,-324 H30 Z" c={gorro ?? 'rojo'} w={5} />
      </g>
    );
  const base = (
    <F d="M-78,-318 Q-84,-410 0,-412 Q84,-410 78,-318 Q44,-366 0,-362 Q-44,-366 -78,-318 Z" c={c} />
  );
  if (e === 'rizado')
    return (
      <g>
        {[-60, -30, 0, 30, 60].map((x) => (
          <F key={x} d={ci(x, -386 + Math.abs(x) * 0.3, 28)} c={c} w={5} />
        ))}
      </g>
    );
  return (
    <g>
      {base}
      {gorro && <F d={rr(-62, -462, 124, 66, 20)} c={gorro} w={5} />}
    </g>
  );
};

const Rostro: React.FC<{cara: Cara; f: number; semilla: number; gafas?: boolean; bigote?: boolean}> = ({cara, f, semilla, gafas, bigote}) => {
  const parpadeo = (f + semilla * 13) % 96 < 4 ? 0.1 : 1;
  const ojo = cara === 'sorpresa' ? 11 : 8;
  const mov = Math.sin((f + semilla) / 30) * 2;
  return (
    <g>
      <g transform={`translate(${mov},0)`}>
        {[-27, 27].map((x) => (
          <g key={x} transform={`translate(${x},-290) scale(1,${parpadeo})`}>
            <path d={el(0, 0, ojo * 0.85, ojo * 1.15)} fill="#1E1E24" />
            {parpadeo === 1 && <path d={ci(2, -3, 3)} fill="#FFFFFF" />}
          </g>
        ))}
      </g>
      {/* cejas */}
      {cara === 'preocupado' && <L d="M-46,-322 L-14,-334 M46,-322 L14,-334" w={6} />}
      {cara === 'enfadado' && <L d="M-46,-336 L-14,-322 M46,-336 L14,-322" w={7} />}
      {cara === 'sorpresa' && <L d="M-46,-330 Q-30,-342 -14,-330 M46,-330 Q30,-342 14,-330" w={5} />}
      {cara === 'pensando' && <L d="M-46,-326 L-14,-322 M18,-340 Q34,-348 48,-338" w={6} />}
      {(cara === 'feliz' || cara === 'serio') && <L d="M-44,-322 Q-30,-330 -14,-324 M44,-322 Q30,-330 14,-324" w={5} />}
      {/* boca */}
      {cara === 'feliz' && (
        <g>
          <F d="M-30,-250 Q0,-204 30,-250 Z" c="blanco" w={5} />
          <R d="M-14,-232 Q0,-216 14,-232 Z" c="rojo" />
        </g>
      )}
      {cara === 'serio' && <L d="M-20,-234 H20" w={6} />}
      {cara === 'sorpresa' && <F d={el(0, -234, 13, 20)} c="oscuro" w={5} />}
      {cara === 'preocupado' && <L d="M-24,-226 Q0,-248 24,-226" w={6} />}
      {cara === 'enfadado' && <L d="M-24,-224 Q0,-246 24,-224" w={7} />}
      {cara === 'pensando' && <L d="M-16,-234 Q10,-226 26,-244" w={6} />}
      {cara === 'preocupado' && <R d="M70,-300 q10,22 0,30 q-12,-8 0,-30 Z" c="cielo" />}
      {gafas && <g><L d={ci(-27, -290, 23)} w={4} /><L d={ci(27, -290, 23)} w={4} /><L d="M-4,-290 H4" w={4} /></g>}
      {bigote && <F d="M-34,-252 Q-18,-270 0,-254 Q18,-270 34,-252 Q18,-244 0,-250 Q-18,-244 -34,-252 Z" c="gris" w={4} />}
      <path d={ci(-42, -258, 11)} fill="#F0584A" opacity={0.22} />
      <path d={ci(42, -258, 11)} fill="#F0584A" opacity={0.22} />
    </g>
  );
};

export const Personaje: React.FC<{
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
  const L0 = typeof look === 'string' ? LOOKS[look] ?? LOOKS.cliente : look;
  const piel = L0.piel ?? 'piel';
  const [aI, aD0] = POSES[pose];
  let aD = aD0;
  if (pose === 'saluda') aD = 150 + Math.sin((f + semilla * 7) / 3.5) * 16;
  if (pose === 'senala') aD = 82 + Math.sin((f + semilla * 5) / 9) * 5;
  if (pose === 'celebra') {
    const s = Math.sin((f + semilla * 3) / 5) * 14;
    return (
      <Cuerpo {...{x, y, k, L0, piel, cara, voltea, semilla, f, mano, piernas}} aI={160 + s} aD={160 - s} brazoCruz={false} />
    );
  }
  return <Cuerpo {...{x, y, k, L0, piel, cara, voltea, semilla, f, mano, piernas}} aI={aI + Math.sin((f + semilla) / 25) * 3} aD={aD} brazoCruz={pose === 'brazos_cruzados'} />;
};

const Cuerpo: React.FC<any> = ({x, y, k, L0, piel, cara, voltea, semilla, f, mano, piernas, aI, aD, brazoCruz}) => {
  const resp = 1 + Math.sin((f + semilla * 5) / 18) * 0.012;
  const cabeza = Math.sin((f + semilla * 3) / 22) * 2.2;
  return (
    <g transform={`translate(${x},${y}) scale(${voltea ? -k : k},${k * resp})`}>
      {piernas && (
        <g>
          <F d={rr(-62, 20, 52, 130, 14)} c={L0.pantalon ?? 'oscuro'} w={5} />
          <F d={rr(10, 20, 52, 130, 14)} c={L0.pantalon ?? 'oscuro'} w={5} />
          <F d={el(-38, 152, 44, 16)} c="oscuro" w={5} />
          <F d={el(38, 152, 44, 16)} c="oscuro" w={5} />
        </g>
      )}
      <Brazo lado={1} ang={aI} manga={L0.camisa ?? 'azul'} piel={piel} />
      <F d={rr(-82, -200, 164, 240, 52)} c={L0.camisa ?? 'azul'} />
      {L0.delantal && <F d={rr(-58, -120, 116, 150, 18)} c={L0.delantal} w={5} />}
      {L0.corbata && <F d={poli([[-14, -196], [14, -196], [20, -110], [0, -86], [-20, -110]])} c={L0.corbata} w={4} />}
      {brazoCruz ? (
        <g>
          <F d={rr(-96, -80, 192, 44, 22)} c={L0.camisa ?? 'azul'} w={5} />
          <F d={ci(-86, -58, 25)} c={piel} w={5} />
        </g>
      ) : (
        <Brazo lado={-1} ang={aD} manga={L0.camisa ?? 'azul'} piel={piel} mano={mano} />
      )}
      <g transform={`rotate(${cabeza} 0 -230)`}>
        <PeloAtras e={L0.peloEstilo ?? 'corto'} c={L0.pelo ?? 'oscuro'} />
        <F d={rr(-22, -236, 44, 40, 10)} c={piel} w={5} />
        <F d={ci(0, -292, 80)} c={piel} />
        <PeloFrente e={L0.peloEstilo ?? 'corto'} c={L0.pelo ?? 'oscuro'} gorro={L0.gorro} />
        <Rostro cara={cara} f={f} semilla={semilla} gafas={L0.gafas} bigote={L0.bigote} />
      </g>
    </g>
  );
};
