import React from 'react';
import {F, L, R, T, ci, el, poli, rr, GRANDE} from './prim';

/**
 * Libreria de objetos dibujados. Cada uno vive centrado en (0,0) y cabe en
 * unos 340 x 340: la escena los coloca y los escala.
 */
type O = React.FC;

// ======================================================================= dinero
const Euro: O = () => (
  <g>
    <F d={ci(0, 0, 135)} c="amarillo" />
    <L d={ci(0, 0, 104)} w={5} />
    <T x={0} y={50} px={150} anchor="middle" fam={GRANDE}>€</T>
    <L d="M-85,-62 Q-60,-98 -22,-108" c="blanco" w={9} />
  </g>
);

const Monedas: O = () => (
  <g>
    {[0, 1, 2, 3, 4].map((i) => (
      <g key={i}>
        <F d={rr(-120, 70 - i * 38, 240, 38, 8)} c="amarillo" />
        <F d={el(0, 70 - i * 38, 120, 32)} c="amarillo" />
      </g>
    ))}
    <T x={0} y={-98} px={62} anchor="middle" fam={GRANDE}>€</T>
    <g transform="translate(150,110) rotate(-12)">
      <F d={ci(0, 0, 40)} c="amarillo" />
      <L d={ci(0, 0, 27)} w={4} />
    </g>
  </g>
);

const Billetes: O = () => (
  <g>
    {[-14, 0, 14].map((r, i) => (
      <g key={i} transform={`translate(${(i - 1) * 40},${(1 - i) * 6}) rotate(${r})`}>
        <F d={rr(-130, -70, 260, 140, 12)} c={['verde', 'verde', 'verde'][i]} />
        <L d={rr(-114, -54, 228, 108, 8)} c="blanco" w={4} />
        {i === 1 && (
          <g>
            <F d={ci(0, 0, 36)} c="amarillo" />
            <T x={0} y={14} px={46} anchor="middle" fam={GRANDE}>€</T>
          </g>
        )}
      </g>
    ))}
  </g>
);

const Hucha: O = () => (
  <g>
    <F d={el(0, 20, 150, 110)} c="rosa" />
    <F d={poli([[-70, -70], [-50, -130], [-10, -80]])} c="rosa" />
    <F d={rr(-90, 90, 40, 70, 10)} c="rosa" />
    <F d={rr(50, 90, 40, 70, 10)} c="rosa" />
    <F d={rr(130, -10, 60, 56, 20)} c="rosa" />
    <path d={ci(150, 10, 6)} fill="#1E1E24" />
    <path d={ci(168, 10, 6)} fill="#1E1E24" />
    <path d={ci(92, -22, 9)} fill="#1E1E24" />
    <L d="M-20,-86 H50" w={10} />
    <L d="M-150,10 q-30,-10 -20,-40" w={7} />
    <g transform="translate(15,-170)">
      <F d={ci(0, 0, 32)} c="amarillo" />
      <T x={0} y={12} px={38} anchor="middle" fam={GRANDE}>€</T>
    </g>
  </g>
);

const Caja: O = () => (
  <g>
    <F d={rr(-150, 0, 300, 130, 14)} c="oscuro" />
    <F d={poli([[-110, 0], [-80, -90], [80, -90], [110, 0]])} c="gris" />
    <F d={rr(-70, -150, 140, 66, 10)} c="azul" />
    <T x={0} y={-100} px={44} anchor="middle" c="blanco">1,80 €</T>
    {[0, 1, 2, 3].map((i) => (
      <F key={i} d={rr(-110 + i * 56, 24, 44, 28, 6)} c={['amarillo', 'verde', 'rojo', 'blanco'][i]} w={4} />
    ))}
    <F d={rr(-110, 76, 220, 32, 8)} c="gris" w={4} />
  </g>
);

const Ticket: O = () => (
  <g>
    <F d="M-110,-150 H110 V150 L88,130 L66,150 L44,130 L22,150 L0,130 L-22,150 L-44,130 L-66,150 L-88,130 L-110,150 Z" c="blanco" />
    <L d="M-70,-100 H70" w={6} />
    <L d="M-70,-60 H30" w={6} />
    <L d="M-70,-20 H50" w={6} />
    <L d="M-70,20 H0" w={6} />
    <L d="M-70,62 H80" w={4} />
    <T x={-70} y={108} px={40}>TOTAL</T>
    <T x={95} y={108} px={40} anchor="end" c="rojo">€</T>
  </g>
);

const Tarjeta: O = () => (
  <g transform="rotate(-8)">
    <F d={rr(-160, -100, 320, 200, 24)} c="azul" />
    <R d={rr(-160, -62, 320, 44, 0)} c="oscuro" />
    <F d={rr(-130, 8, 62, 46, 8)} c="amarillo" w={4} />
    <L d="M-130,80 H-30" c="blanco" w={7} />
    <L d="M30,80 H120" c="blanco" w={7} />
  </g>
);

const Porcentaje: O = () => (
  <g>
    <F d={ci(0, 0, 135)} c="rojo" />
    <T x={0} y={58} px={170} anchor="middle" c="blanco" fam={GRANDE}>%</T>
  </g>
);

const GrafBaja: O = () => (
  <g>
    <F d={rr(-150, -130, 300, 260, 18)} c="blanco" />
    <L d="M-110,-90 V90 H110" w={7} />
    <L d="M-90,-60 L-30,-10 L10,-30 L80,60" c="rojo" w={14} />
    <F d={poli([[104, 78], [60, 76], [90, 38]])} c="rojo" w={5} />
  </g>
);
const GrafSube: O = () => (
  <g>
    <F d={rr(-150, -130, 300, 260, 18)} c="blanco" />
    <L d="M-110,-90 V90 H110" w={7} />
    <L d="M-90,60 L-30,10 L10,30 L80,-60" c="verde" w={14} />
    <F d={poli([[104, -78], [60, -76], [90, -38]])} c="verde" w={5} />
  </g>
);
const Barras: O = () => (
  <g>
    <F d={rr(-140, -20, 70, 130, 8)} c="azul" />
    <F d={rr(-35, -90, 70, 200, 8)} c="amarillo" />
    <F d={rr(70, -150, 70, 260, 8)} c="rojo" />
    <L d="M-165,125 H165" w={7} />
  </g>
);

// ======================================================================= lugares
const Local: O = () => (
  <g>
    <F d={rr(-150, -60, 300, 210, 10)} c="blanco" />
    {[0, 1, 2, 3, 4, 5].map((i) => (
      <F key={i} d={`M${-150 + i * 50},-110 h50 v50 q-25,28 -50,0 Z`} c={i % 2 ? 'blanco' : 'rojo'} w={5} />
    ))}
    <F d={rr(-132, -10, 112, 90, 10)} c="azul" w={5} />
    <F d={rr(30, -10, 90, 160, 10)} c="madera" w={5} />
    <path d={ci(100, 70, 6)} fill="#1E1E24" />
    <F d={rr(-170, -150, 340, 44, 10)} c="verde" />
    <L d="M-110,-128 H110" c="blanco" w={7} />
  </g>
);

const Edificio: O = () => (
  <g>
    <F d={rr(-90, -150, 180, 300, 8)} c="azul" />
    {[0, 1, 2, 3].map((r) =>
      [0, 1].map((c) => <F key={`${r}${c}`} d={rr(-62 + c * 72, -118 + r * 66, 52, 44, 6)} c={(r + c) % 3 === 0 ? 'amarillo' : 'blanco'} w={4} />),
    )}
    <F d={rr(-120, 120, 240, 34, 8)} c="oscuro" />
  </g>
);

const Columnas = ({simbolo}: {simbolo: 'euro' | 'bandera'}) => (
  <g>
    <F d={poli([[-170, -50], [0, -150], [170, -50]])} c="blanco" />
    <F d={rr(-150, -50, 300, 28, 6)} c="gris" />
    {[-110, -37, 37, 110].map((x) => (
      <F key={x} d={rr(x - 22, -22, 44, 120, 6)} c="blanco" w={5} />
    ))}
    <F d={rr(-170, 98, 340, 26, 6)} c="gris" />
    <F d={rr(-190, 124, 380, 26, 6)} c="oscuro" />
    {simbolo === 'euro' ? (
      <T x={0} y={-68} px={64} anchor="middle" c="amarillo" fam={GRANDE}>€</T>
    ) : (
      <g transform="translate(0,-150)">
        <L d="M0,0 V-70" w={7} />
        <F d="M0,-70 H64 L48,-48 L64,-26 H0 Z" c="rojo" w={5} />
      </g>
    )}
  </g>
);
const Banco: O = () => <Columnas simbolo="euro" />;
const Ayuntamiento: O = () => <Columnas simbolo="bandera" />;

const Calendario: O = () => (
  <g>
    <F d={rr(-130, -120, 260, 250, 18)} c="blanco" />
    <F d={rr(-130, -120, 260, 70, 18)} c="rojo" />
    <L d="M-70,-148 V-96 M70,-148 V-96" w={12} />
    {[0, 1, 2].map((r) =>
      [0, 1, 2, 3].map((c) => <R key={`${r}${c}`} d={rr(-96 + c * 54, -28 + r * 52, 36, 32, 6)} c={r === 1 && c === 2 ? 'rojo' : 'gris'} />),
    )}
  </g>
);

const Reloj: O = () => (
  <g>
    <F d={ci(0, 0, 135)} c="blanco" />
    {Array.from({length: 12}).map((_, i) => {
      const a = (i * Math.PI) / 6;
      return <L key={i} d={`M${Math.sin(a) * 104},${-Math.cos(a) * 104} L${Math.sin(a) * 120},${-Math.cos(a) * 120}`} w={7} />;
    })}
    <L d="M0,0 V-82" w={11} />
    <L d="M0,0 L58,32" c="rojo" w={11} />
    <path d={ci(0, 0, 10)} fill="#1E1E24" />
  </g>
);

const Mapa: O = () => (
  <g>
    <F d="M-160,-90 L-55,-120 L55,-90 L160,-120 V100 L55,130 L-55,100 L-160,130 Z" c="verde" />
    <L d="M-55,-120 V100 M55,-90 V130" w={5} />
    <L d="M-120,40 Q-20,0 40,50 T150,20" c="blanco" w={7} />
    <g transform="translate(40,-70)">
      <F d="M0,0 C-60,-60 -50,-130 0,-130 C50,-130 60,-60 0,0 Z" c="rojo" />
      <path d={ci(0, -85, 18)} fill="#FFFFFF" />
    </g>
  </g>
);

// ======================================================================= papeles
const Documento: O = () => (
  <g>
    <F d={rr(-105, -150, 210, 290, 14)} c="blanco" />
    {[-100, -62, -24, 14].map((y, i) => (
      <L key={y} d={`M-68,${y} H${i === 3 ? 10 : 68}`} w={6} />
    ))}
    <g transform="translate(40,92)">
      <F d={ci(0, 0, 40)} c="rojo" />
      <T x={0} y={14} px={40} anchor="middle" c="blanco" fam={GRANDE} borde={false}>★</T>
    </g>
    <L d="M-70,100 q20,-30 40,0 t40,-10" w={6} />
  </g>
);

const Contrato: O = () => (
  <g>
    <g transform="rotate(-6)">
      <F d={rr(-105, -150, 210, 290, 14)} c="blanco" />
      <T x={-70} y={-98} px={34}>CONTRATO</T>
      {[-62, -28, 6].map((y) => (
        <L key={y} d={`M-70,${y} H70`} w={5} />
      ))}
      <L d="M-70,80 q18,-34 34,0 t36,-4 t30,-8" c="azul" w={7} />
    </g>
    <g transform="translate(120,90) rotate(30)">
      <F d={rr(-16, -90, 32, 150, 10)} c="amarillo" />
      <F d={poli([[-16, 60], [16, 60], [0, 100]])} c="piel" w={5} />
    </g>
  </g>
);

const Sello: O = () => (
  <g>
    <F d={rr(-24, -160, 48, 120, 18)} c="rojo" />
    <F d={rr(-70, -50, 140, 50, 12)} c="rojo" />
    <F d={rr(-120, 0, 240, 36, 10)} c="oscuro" />
    <R d={rr(-90, 56, 180, 14, 6)} c="azul" />
  </g>
);

const Decimo: O = () => (
  <g transform="rotate(-6)">
    <F d={rr(-160, -90, 320, 180, 16)} c="verde" />
    <L d="M-110,-90 V90" w={4} op={0.5} />
    <T x={-60} y={-24} px={54} fam={GRANDE} c="blanco">00000</T>
    <L d="M-60,16 H130" c="blanco" w={6} />
    <L d="M-60,48 H80" c="blanco" w={6} />
    {[-60, -20, 20, 60].map((y) => (
      <path key={y} d={ci(-135, y, 6)} fill="#FAF3E3" />
    ))}
  </g>
);

const Alerta: O = () => (
  <g>
    <F d="M0,-140 L150,110 H-150 Z" c="amarillo" />
    <L d="M0,-60 V30" w={20} />
    <path d={ci(0, 72, 12)} fill="#1E1E24" />
  </g>
);

const Candado: O = () => (
  <g>
    <L d="M-62,-30 V-80 A62,62 0 0 1 62,-80 V-30" w={26} />
    <F d={rr(-105, -34, 210, 170, 22)} c="amarillo" />
    <path d={ci(0, 36, 20)} fill="#1E1E24" />
    <L d="M0,40 V80" w={14} />
  </g>
);

const Llave: O = () => (
  <g transform="rotate(-30)">
    <F d={ci(-90, 0, 62)} c="amarillo" />
    <path d={ci(-90, 0, 24)} fill="#FAF3E3" />
    <F d={rr(-30, -16, 210, 32, 10)} c="amarillo" />
    <F d={rr(100, 14, 28, 56, 6)} c="amarillo" />
    <F d={rr(146, 14, 28, 40, 6)} c="amarillo" />
  </g>
);

const Balanza: O = () => (
  <g>
    <L d="M0,-140 V120" w={12} />
    <F d={rr(-70, 112, 140, 28, 8)} c="oscuro" />
    <L d="M-140,-100 H140" w={11} />
    <L d="M-140,-100 L-190,20 M-140,-100 L-90,20 M140,-100 L90,20 M140,-100 L190,20" w={5} />
    <F d="M-200,20 H-80 Q-90,70 -140,70 Q-190,70 -200,20 Z" c="amarillo" />
    <F d="M80,20 H200 Q190,70 140,70 Q90,70 80,20 Z" c="amarillo" />
    <path d={ci(0, -140, 16)} fill="#1E1E24" />
  </g>
);

const Lupa: O = () => (
  <g>
    <F d={ci(-30, -30, 100)} c="cielo" />
    <path d={ci(-30, -30, 82)} fill="#E4EFF9" />
    <L d="M-90,-60 Q-80,-100 -40,-108" c="blanco" w={10} />
    <g transform="translate(40,40) rotate(45)"><F d={rr(0, -20, 170, 40, 18)} c="madera" /></g>
  </g>
);

// ======================================================================= personas
const Cara: React.FC<{pelo?: string; sonrisa?: boolean}> = ({pelo = 'oscuro', sonrisa = true}) => (
  <g>
    <F d={ci(0, -4, 70)} c="piel" />
    <F d={`M-72,-14 Q-76,-96 0,-92 Q76,-96 72,-14 Q40,-60 0,-56 Q-40,-60 -72,-14 Z`} c={pelo} />
    <path d={ci(-24, 0, 6)} fill="#1E1E24" />
    <path d={ci(24, 0, 6)} fill="#1E1E24" />
    {sonrisa ? <L d="M-22,30 Q0,48 22,30" w={5} /> : <L d="M-18,36 H18" w={5} />}
  </g>
);

const Persona = ({camisa = 'azul', delantal, pelo = 'oscuro', gafas}: {camisa?: string; delantal?: string; pelo?: string; gafas?: boolean}) => (
  <g transform="translate(0,-70)">
    <F d={rr(-96, 30, 192, 210, 70)} c={camisa} />
    {delantal && <F d={rr(-62, 78, 124, 162, 20)} c={delantal} />}
    <g transform="translate(0,-60)">
      <Cara pelo={pelo} />
      {gafas && <L d="M-44,-2 H-6 M6,-2 H44 M-6,-2 H6" w={5} />}
    </g>
  </g>
);

const Duena: O = () => <Persona delantal="rojo" pelo="madera" />;
const Cliente: O = () => <Persona camisa="verde" pelo="oscuro" />;
const Jefe: O = () => <Persona camisa="oscuro" pelo="gris" gafas />;
const Gente: O = () => (
  <g>
    <g transform="translate(-95,26) scale(0.78)"><Persona camisa="verde" pelo="oscuro" /></g>
    <g transform="translate(95,26) scale(0.78)"><Persona camisa="rojo" pelo="madera" /></g>
    <g transform="translate(0,48)"><Persona camisa="azul" pelo="oscuro" /></g>
  </g>
);

// ======================================================================= bar
const Taza: O = () => (
  <g>
    <F d={el(0, 100, 140, 24)} c="gris" />
    <L d="M95,-30 q80,0 80,44 q0,44 -80,44" w={16} />
    <L d="M95,-30 q80,0 80,44 q0,44 -80,44" c="blanco" w={5} />
    <F d="M-100,-60 H100 Q100,80 0,80 Q-100,80 -100,-60 Z" c="blanco" />
    <F d={el(0, -60, 100, 22)} c="madera" />
    <L d="M-30,-130 q-30,-40 0,-70 q30,-30 0,-70" w={6} />
    <L d="M30,-120 q-30,-40 0,-70 q30,-30 0,-70" w={6} />
  </g>
);

const Cana: O = () => (
  <g>
    <L d="M105,-60 q70,0 70,50 q0,70 -70,70" w={20} />
    <F d="M-95,-100 H105 L88,130 Q86,150 66,150 H-56 Q-76,150 -78,130 Z" c="amarillo" />
    <R d="M-70,-30 H88 L84,-4 H-66 Z" c="naranja" op={0.5} />
    <F d="M-110,-100 Q-120,-170 -60,-150 Q-40,-190 10,-160 Q60,-190 90,-150 Q130,-160 118,-100 Z" c="blanco" />
    <L d="M-50,-10 V90 M-10,-10 V90 M30,-10 V90" c="blanco" w={6} op={0.7} />
  </g>
);

const Botellas: O = () => (
  <g>
    {[
      [-110, 'verde'],
      [0, 'rojo'],
      [110, 'azul'],
    ].map(([x, c], i) => (
      <g key={i} transform={`translate(${x},${i === 1 ? -14 : 8})`}>
        <F d="M-24,-150 H24 V-90 Q60,-70 60,-30 V120 Q60,150 30,150 H-30 Q-60,150 -60,120 V-30 Q-60,-70 -24,-90 Z" c={c as string} />
        <F d={rr(-40, -10, 80, 70, 8)} c="blanco" w={4} />
        <F d={rr(-27, -172, 54, 30, 8)} c="oscuro" w={5} />
      </g>
    ))}
  </g>
);

const Cafetera: O = () => (
  <g>
    <F d={rr(-150, -130, 300, 190, 22)} c="gris" />
    <F d={rr(-130, -108, 260, 70, 12)} c="oscuro" />
    <path d={ci(-70, -72, 16)} fill="#F0584A" />
    <path d={ci(0, -72, 16)} fill="#52B788" />
    <path d={ci(70, -72, 16)} fill="#FFC93C" />
    <F d={rr(-90, 60, 180, 22, 6)} c="oscuro" />
    <F d={rr(-70, 82, 140, 60, 10)} c="blanco" />
    <F d={rr(-110, 142, 220, 24, 8)} c="oscuro" />
    <L d="M-20,10 V42 M20,10 V42" w={9} />
  </g>
);

const Nevera: O = () => (
  <g>
    <F d={rr(-90, -170, 180, 340, 22)} c="blanco" />
    <L d="M-90,-40 H90" w={6} />
    <L d="M60,-130 V-70 M60,0 V80" w={12} />
    <R d={rr(-70, -150, 30, 90, 8)} c="cielo" />
  </g>
);

const Taburete: O = () => (
  <g>
    <F d={el(0, -90, 120, 34)} c="rojo" />
    <R d={rr(-120, -90, 240, 34, 12)} c="rojo" />
    <L d="M-120,-90 V-56 Q-120,-30 0,-30 Q120,-30 120,-56 V-90" w={6} />
    <L d="M-60,-30 L-100,150 M60,-30 L100,150 M0,-26 V150 M-86,70 H86" w={12} />
  </g>
);

const Barra: O = () => (
  <g>
    <F d={rr(-170, -30, 340, 36, 12)} c="madera" />
    <F d={rr(-150, 6, 300, 140, 8)} c="oscuro" />
    <L d="M-60,16 V136 M50,16 V136" w={5} />
    <g transform="translate(-80,-90) scale(0.5)"><Taza /></g>
    <g transform="translate(95,-72) scale(0.42)"><Cana /></g>
  </g>
);

// ======================================================================= taxi
const Taxi: O = () => (
  <g>
    <F d="M-150,40 L-120,-30 Q-110,-60 -80,-60 H70 Q100,-60 112,-30 L150,40 Z" c="amarillo" />
    <F d={rr(-170, 20, 340, 80, 24)} c="amarillo" />
    <F d="M-100,-24 H-8 V20 H-122 Z" c="cielo" w={5} />
    <F d="M8,-24 H72 L108,20 H8 Z" c="cielo" w={5} />
    <F d={rr(-40, -96, 80, 34, 8)} c="blanco" w={5} />
    <T x={0} y={-70} px={26} anchor="middle" borde={false}>TAXI</T>
    <R d={rr(-170, 56, 340, 12, 0)} c="oscuro" />
    {[-100, 100].map((x) => (
      <g key={x}>
        <F d={ci(x, 100, 40)} c="oscuro" />
        <path d={ci(x, 100, 14)} fill="#C9C3B5" />
      </g>
    ))}
  </g>
);

const Volante: O = () => (
  <g>
    <F d={ci(0, 0, 135)} c="oscuro" />
    <path d={ci(0, 0, 96)} fill="#FAF3E3" />
    <L d={ci(0, 0, 96)} w={5} />
    <L d="M-96,0 H-30 M96,0 H30 M0,30 V96" c="oscuro" w={26} />
    <F d={ci(0, 0, 38)} c="gris" />
  </g>
);

const Taximetro: O = () => (
  <g>
    <F d={rr(-150, -100, 300, 200, 24)} c="oscuro" />
    <F d={rr(-120, -72, 240, 80, 10)} c="verde" />
    <T x={100} y={-8} px={64} anchor="end" fam={GRANDE} borde={false}>12,40</T>
    {[0, 1, 2].map((i) => (
      <F key={i} d={ci(-90 + i * 90, 56, 18)} c={['rojo', 'amarillo', 'blanco'][i]} w={4} />
    ))}
  </g>
);

const Licencia: O = () => (
  <g transform="rotate(-5)">
    <F d={rr(-165, -105, 330, 210, 22)} c="blanco" />
    <F d={rr(-165, -105, 330, 64, 22)} c="amarillo" />
    <T x={-130} y={-56} px={46} borde={false}>LICENCIA</T>
    <F d={rr(-135, -20, 82, 96, 8)} c="cielo" w={5} />
    <path d={ci(-94, 8, 18)} fill="#1E1E24" opacity={0.5} />
    <L d="M-20,-4 H120 M-20,28 H120 M-20,60 H70" w={6} />
    <g transform="translate(110,70)"><F d={ci(0, 0, 30)} c="rojo" w={5} /></g>
  </g>
);

// ======================================================================= burger
const Hamburguesa: O = () => (
  <g>
    <F d="M-150,-30 Q-150,-130 0,-135 Q150,-130 150,-30 Z" c="madera" />
    <path d={ci(-60, -80, 7)} fill="#FAF3E3" />
    <path d={ci(0, -100, 7)} fill="#FAF3E3" />
    <path d={ci(60, -78, 7)} fill="#FAF3E3" />
    <F d="M-155,-30 q20,34 40,0 q20,34 40,0 q20,34 40,0 q20,34 40,0 q20,34 40,0 q20,34 40,0 q20,34 40,0 V-20 H-155 Z" c="verde" />
    <F d={rr(-150, -14, 300, 38, 16)} c="rojo" />
    <F d={rr(-148, 22, 296, 44, 20)} c="oscuro" />
    <F d={poli([[-140, 66], [140, 66], [120, 90], [-120, 90]])} c="amarillo" />
    <F d="M-150,90 H150 Q150,150 90,150 H-90 Q-150,150 -150,90 Z" c="madera" />
  </g>
);

const Patatas: O = () => (
  <g>
    {[-70, -38, -6, 26, 58].map((x, i) => (
      <F key={x} d={rr(x - 14, -150 + (i % 2) * 24, 28, 170, 8)} c="amarillo" w={5} />
    ))}
    <F d="M-110,-30 H110 L84,150 H-84 Z" c="rojo" />
    <T x={0} y={72} px={52} anchor="middle" c="amarillo" fam={GRANDE}>M</T>
  </g>
);

const Refresco: O = () => (
  <g>
    <L d="M30,-170 L60,-110" w={14} c="rojo" />
    <F d={rr(-90, -120, 180, 30, 10)} c="blanco" />
    <F d="M-80,-90 H80 L60,150 H-60 Z" c="rojo" />
    <R d="M-70,-20 H70 L66,10 H-66 Z" c="blanco" />
    <T x={0} y={92} px={44} anchor="middle" c="blanco" fam={GRANDE}>COLA</T>
  </g>
);

const Corona: O = () => (
  <g>
    <F d="M-150,100 L-170,-90 L-80,-10 L0,-130 L80,-10 L170,-90 L150,100 Z" c="amarillo" />
    <F d={rr(-152, 100, 304, 36, 10)} c="amarillo" />
    {[[-170, -90], [0, -130], [170, -90]].map(([x, y]) => (
      <F key={x} d={ci(x, y, 20)} c="rojo" w={5} />
    ))}
    <path d={ci(-60, 56, 14)} fill="#4F9BE0" />
    <path d={ci(0, 56, 14)} fill="#F0584A" />
    <path d={ci(60, 56, 14)} fill="#52B788" />
  </g>
);

const Bolsa: O = () => (
  <g>
    <L d="M-50,-90 Q-50,-160 0,-160 Q50,-160 50,-90" w={12} />
    <F d="M-120,-90 H120 L100,150 H-100 Z" c="rojo" />
    <T x={0} y={44} px={80} anchor="middle" c="amarillo" fam={GRANDE}>€</T>
  </g>
);

const Camion: O = () => (
  <g>
    <F d={rr(-170, -90, 200, 160, 12)} c="blanco" />
    <F d="M30,-40 H100 L150,20 V70 H30 Z" c="azul" />
    <F d="M50,-24 H92 L124,20 H50 Z" c="cielo" w={5} />
    <R d={rr(-170, 56, 320, 14, 0)} c="oscuro" />
    {[-100, 90].map((x) => (
      <g key={x}>
        <F d={ci(x, 78, 36)} c="oscuro" />
        <path d={ci(x, 78, 13)} fill="#C9C3B5" />
      </g>
    ))}
    <L d="M-120,-40 H-20 M-120,-4 H-60" w={6} />
  </g>
);

const Carrito: O = () => (
  <g>
    <L d="M-170,-120 H-110 L-62,70 H110" w={13} />
    <F d="M-100,-80 H150 L120,30 H-70 Z" c="verde" />
    <L d="M-30,-80 V30 M40,-80 V30" w={4} />
    {[-40, 80].map((x) => (
      <F key={x} d={ci(x, 108, 22)} c="oscuro" w={5} />
    ))}
  </g>
);

// ======================================================================= peluqueria
const Tijeras: O = () => (
  <g transform="rotate(-20)">
    <F d={poli([[-14, -10], [14, -10], [26, -170], [0, -190], [-26, -170]])} c="gris" w={5} />
    <g transform="rotate(14)">
      <F d={poli([[-14, -10], [14, -10], [26, -170], [0, -190], [-26, -170]])} c="gris" w={5} />
    </g>
    <L d={ci(-48, 90, 46)} c="rojo" w={20} />
    <L d={ci(66, 90, 46)} c="rojo" w={20} />
    <L d="M-14,-6 L-34,56 M14,-6 L48,58" w={11} />
    <path d={ci(0, -4, 11)} fill="#1E1E24" />
  </g>
);

const Peine: O = () => (
  <g transform="rotate(-8)">
    <F d={rr(-170, -64, 340, 62, 18)} c="azul" />
    {Array.from({length: 12}).map((_, i) => (
      <F key={i} d={rr(-158 + i * 28, -4, 16, 84, 6)} c="azul" w={4} />
    ))}
  </g>
);

const Secador: O = () => (
  <g transform="rotate(-12)">
    <F d={rr(-60, -20, 160, 100, 36)} c="rosa" />
    <F d={rr(100, -6, 50, 72, 8)} c="oscuro" />
    <F d={rr(-20, 60, 52, 130, 18)} c="oscuro" />
    <L d="M-100,-10 H-150 M-100,30 H-170 M-100,70 H-140" w={8} />
    <path d={ci(0, 24, 12)} fill="#FAF3E3" />
  </g>
);

const Espejo: O = () => (
  <g>
    <F d={el(0, -30, 110, 140)} c="madera" />
    <path d={el(0, -30, 90, 120)} fill="#E4EFF9" />
    <L d="M-58,-96 Q-44,-130 -16,-138" c="blanco" w={12} />
    <F d={rr(-22, 110, 44, 66, 8)} c="madera" />
  </g>
);

const Silla: O = () => (
  <g>
    <F d={rr(-70, -170, 140, 160, 30)} c="rojo" />
    <F d={rr(-110, -20, 220, 64, 24)} c="rojo" />
    <F d={rr(-22, 44, 44, 80, 6)} c="gris" />
    <F d={rr(-100, 124, 200, 28, 12)} c="oscuro" />
    <F d={rr(-124, -60, 30, 90, 10)} c="oscuro" />
  </g>
);

// ======================================================================= estanco
const Cajetilla: O = () => (
  <g transform="rotate(-8)">
    <F d={rr(-100, -150, 200, 300, 14)} c="blanco" />
    <R d={rr(-100, -150, 200, 100, 14)} c="rojo" />
    <L d="M-100,-50 H100" w={5} />
    <F d={rr(-70, 0, 140, 90, 10)} c="amarillo" w={5} />
    <g transform="translate(110,-70) rotate(20)">
      <F d={rr(-12, -110, 24, 190, 8)} c="blanco" w={5} />
      <R d={rr(-12, -110, 24, 60, 8)} c="madera" />
    </g>
  </g>
);

const Mechero: O = () => (
  <g>
    <F d={rr(-60, -40, 120, 190, 20)} c="azul" />
    <F d={rr(-60, -80, 120, 50, 12)} c="gris" />
    <F d="M0,-190 Q36,-140 20,-96 Q0,-84 -20,-96 Q-36,-140 0,-190 Z" c="naranja" w={5} />
    <R d="M0,-150 Q14,-124 6,-104 Q-8,-104 -10,-122 Z" c="amarillo" />
  </g>
);

const Gota: O = () => (
  <g>
    <F d="M0,-160 C-130,10 -110,140 0,140 C110,140 130,10 0,-160 Z" c="azul" />
    <L d="M-60,30 Q-60,80 -20,100" c="blanco" w={12} />
  </g>
);
const Bombilla: O = () => (
  <g>
    <F d="M0,-150 C-100,-150 -120,-30 -50,30 C-30,50 -34,70 -34,80 H34 C34,70 30,50 50,30 C120,-30 100,-150 0,-150 Z" c="amarillo" />
    <F d={rr(-42, 80, 84, 24, 6)} c="gris" w={5} />
    <F d={rr(-30, 104, 60, 22, 8)} c="oscuro" w={5} />
    <L d="M-30,-20 L0,20 L30,-20" w={6} />
    <L d="M0,-190 V-170 M-130,-130 L-115,-115 M130,-130 L115,-115" w={9} />
  </g>
);
const Fuego: O = () => (
  <g>
    <F d="M0,-170 C60,-100 120,-50 100,40 C90,110 -90,110 -100,40 C-110,-20 -50,-60 0,-170 Z" c="naranja" />
    <F d="M0,-30 C40,10 60,40 40,80 C20,110 -30,110 -40,80 C-50,40 -20,10 0,-30 Z" c="amarillo" w={5} />
  </g>
);
const Estrella: O = () => (
  <g>
    <F
      d={poli(Array.from({length: 10}).map((_, i) => {
        const r = i % 2 ? 62 : 150;
        const a = (i * Math.PI) / 5;
        return [Math.round(Math.sin(a) * r), Math.round(-Math.cos(a) * r)] as [number, number];
      }))}
      c="amarillo"
    />
  </g>
);
const Escudo: O = () => (
  <g>
    <F d="M-120,-120 H120 V10 Q120,100 0,160 Q-120,100 -120,10 Z" c="azul" />
    <L d="M-52,0 L-14,40 L58,-40" c="blanco" w={20} />
  </g>
);

export type ObjDef = {C: O; nombre: string};
export const OBJ: Record<string, O> = {
  euro: Euro, monedas: Monedas, billetes: Billetes, hucha: Hucha, caja: Caja, ticket: Ticket, tarjeta: Tarjeta,
  porcentaje: Porcentaje, graf_baja: GrafBaja, graf_sube: GrafSube, barras: Barras,
  local: Local, edificio: Edificio, banco: Banco, ayuntamiento: Ayuntamiento, calendario: Calendario, reloj: Reloj, mapa: Mapa,
  documento: Documento, contrato: Contrato, sello: Sello, decimo: Decimo, alerta: Alerta, candado: Candado, llave: Llave,
  balanza: Balanza, lupa: Lupa,
  duena: Duena, cliente: Cliente, jefe: Jefe, gente: Gente,
  taza: Taza, cana: Cana, botellas: Botellas, cafetera: Cafetera, nevera: Nevera, taburete: Taburete, barra: Barra,
  taxi: Taxi, volante: Volante, taximetro: Taximetro, licencia: Licencia,
  hamburguesa: Hamburguesa, patatas: Patatas, refresco: Refresco, corona: Corona, bolsa: Bolsa, camion: Camion, carrito: Carrito,
  tijeras: Tijeras, peine: Peine, secador: Secador, espejo: Espejo, silla: Silla,
  cajetilla: Cajetilla, mechero: Mechero,
  gota: Gota, bombilla: Bombilla, fuego: Fuego, estrella: Estrella, escudo: Escudo,
};
