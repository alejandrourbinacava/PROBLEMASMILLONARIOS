import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Entra} from './anim';
import {OBJ} from './Objetos';
import {Personaje} from './Personaje';
import {F, L, R, T, ci, el, poli, rr} from './prim';
import {Actor, Bloque, Burbuja, Caja3, Cielo, EP, OWNER, PAREDES, Persiana, Pieza, RUOTULO, SUELOS, Suelo, Ventana, Letrero} from './escenario';
import {clamp01, suave} from './util';

/**
 * Escenas grandes: un lugar entero con sus personajes, y el objeto de la
 * frase como protagonista (`foco`) y/o en una burbuja de pensamiento.
 * Dejan libre la franja de arriba (y < 300) para el titular.
 */
const dueno = (tema: string) => OWNER[tema] ?? 'duena';
const CLIENTES = ['cliente', 'cliente2', 'cliente3'];

// ---------------------------------------------------------------- estanterias por tema
const Estante: React.FC<{tema: string; x: number; y: number}> = ({tema, x, y}) => {
  switch (tema) {
    case 'burger':
      return (
        <g>
          <F d={rr(x, y - 40, 560, 270, 16)} c="oscuro" />
          <T x={x + 30} y={y + 20} px={54} c="amarillo" fam="D Baloo" borde={false}>MENÚ</T>
          {[0, 1, 2].map((i) => (
            <g key={i}>
              <L d={`M${x + 30},${y + 70 + i * 52} H${x + 330}`} c="blanco" w={6} op={0.8} />
              <F d={ci(x + 420, y + 64 + i * 52, 22)} c="amarillo" w={4} />
            </g>
          ))}
          <g transform={`translate(${x + 480},${y + 30}) scale(0.28)`}>{React.createElement(OBJ.hamburguesa)}</g>
        </g>
      );
    case 'peluqueria':
      return (
        <g>
          <F d={rr(x, y - 40, 420, 300, 40)} c="madera" />
          <F d={rr(x + 24, y - 16, 372, 252, 28)} c="cielo" w={4} />
          <L d={`M${x + 60},${y + 40} L${x + 140},${y - 8}`} c="blanco" w={14} />
          <F d={rr(x + 440, y + 150, 220, 18, 6)} c="madera" />
          {[0, 1, 2].map((i) => (
            <F key={i} d={rr(x + 460 + i * 66, y + 80, 40, 70, 12)} c={['rosa', 'morado', 'azul'][i]} w={4} />
          ))}
        </g>
      );
    case 'estanco':
      return (
        <g>
          <F d={rr(x - 10, y - 40, 600, 270, 12)} c="madera" />
          {[0, 1, 2].map((r) => (
            <g key={r}>
              {Array.from({length: 9}).map((_, i) => (
                <F key={i} d={rr(x + 8 + i * 64, y - 22 + r * 84, 50, 66, 6)} c={['rojo', 'blanco', 'amarillo', 'azul', 'verde'][(i + r * 2) % 5]} w={4} />
              ))}
            </g>
          ))}
        </g>
      );
    case 'bar':
      return (
        <g>
          <F d={rr(x, y + 120, 600, 18, 6)} c="madera" />
          <F d={rr(x, y + 10 - 120, 600, 18, 6)} c="madera" />
          {Array.from({length: 8}).map((_, i) => (
            <g key={i}>
              <F d={rr(x + 24 + i * 70, y + 14, 44, 106, 14)} c={['verde', 'amarillo', 'rojo', 'azul', 'verde', 'naranja', 'rojo', 'azul'][i]} w={4} />
              <F d={rr(x + 34 + i * 70, y - 12, 24, 30, 6)} c="oscuro" w={4} />
            </g>
          ))}
          {Array.from({length: 6}).map((_, i) => (
            <F key={i} d={rr(x + 30 + i * 90, y - 110, 56, 100, 8)} c={['blanco', 'cielo'][i % 2]} w={4} />
          ))}
        </g>
      );
    default:
      return (
        <g>
          <F d={rr(x, y + 130, 600, 18, 6)} c="madera" />
          <F d={rr(x, y - 40, 600, 18, 6)} c="madera" />
          {[0, 1, 2, 3, 4].map((i) => (
            <Caja3 key={i} x={x + 70 + i * 115} y={y + 130} k={0.7} c={['madera', 'amarillo', 'verde', 'azul', 'rojo'][i]} />
          ))}
          {[0, 1, 2, 3].map((i) => (
            <Caja3 key={i} x={x + 120 + i * 130} y={y - 40} k={0.7} c={['verde', 'madera', 'rosa', 'amarillo'][i]} />
          ))}
        </g>
      );
  }
};

// ---------------------------------------------------------------- A. tienda con mostrador
export const Tienda: React.FC<EP> = ({foco, burbuja, cara, pose, v, tema, s}) => {
  const f = useCurrentFrame();
  const front = tema === 'burger' ? 'rojo' : tema === 'estanco' ? 'madera' : 'oscuro';
  return (
    <g>
      <R d={rr(0, 0, 1920, 790, 0)} c={PAREDES[v % 5]} />
      <Suelo y={790} c={SUELOS[v % 5]} />
      <Ventana x={110} y={330} w={330} h={260} />
      <Estante tema={tema} x={920} y={380} />
      <Actor x={700} pies={950} k={1.0} look={OWNER[tema] ?? 'duena'} pose={pose} cara={cara} s={s} t0={3} />
      {/* mostrador */}
      <F d={rr(60, 770, 1500, 56, 14)} c="madera" />
      <F d={rr(100, 826, 1420, 254, 10)} c={front} />
      {[0, 1, 2, 3, 4].map((i) => (
        <L key={i} d={`M${300 + i * 280},840 V1070`} w={4} op={0.35} />
      ))}
      <Pieza o={foco && foco !== 'local' ? foco : 'caja'} x={1190} y={620} k={0.8} t0={9} s={s} />
      <Actor x={1720} pies={1050} k={0.92} look={CLIENTES[s % 3]} pose="quieto" cara={cara === 'preocupado' ? 'sorpresa' : 'feliz'} voltea s={s + 3} t0={6} />
      <Burbuja o={burbuja} x={1640} y={400} k={0.8} s={s} cola="der" />
      <g transform={`translate(0,${Math.sin(f / 15) * 3})`}>
        <Letrero x={290} y={250} w={330} h={84} texto={RUOTULO[tema] ?? 'TIENDA'} c={tema === 'burger' ? 'rojo' : 'verde'} />
      </g>
    </g>
  );
};

// ---------------------------------------------------------------- B. calle
export const Calle: React.FC<EP> = ({foco, burbuja, cara, pose, v, tema, s, n}) => {
  const f = useCurrentFrame();
  const u = f / Math.max(1, n);
  const coche = OBJ.taxi;
  return (
    <g>
      <Cielo />
      <path d={ci(1650, 190, 70)} fill="#FFE27A" />
      <Bloque x={60} y={330} w={220} h={460} c="rosa" />
      <Bloque x={1480} y={300} w={260} h={490} c="azul" cols={3} />
      <Bloque x={1760} y={380} w={180} h={410} c="verde" cols={2} />
      {/* el local */}
      <F d={rr(430, 330, 780, 470, 12)} c="blanco" />
      <F d={rr(410, 300, 820, 60, 12)} c={PAREDES[v % 5]} />
      <Letrero x={820} y={420} w={560} h={110} texto={RUOTULO[tema] ?? 'TIENDA'} c={tema === 'burger' ? 'rojo' : 'verde'} px={78} />
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <F key={i} d={`M${450 + i * 96},500 h96 v70 q-48,40 -96,0 Z`} c={i % 2 ? 'blanco' : 'rojo'} w={5} />
      ))}
      <F d={rr(480, 620, 260, 180, 12)} c="amarillo" />
      <F d={rr(860, 620, 150, 180, 12)} c="madera" />
      <F d={rr(1050, 620, 120, 180, 12)} c="amarillo" />
      {/* acera y calle */}
      <R d={rr(0, 800, 1920, 70, 0)} c="gris" />
      <L d="M0,800 H1920" w={6} />
      <R d={rr(0, 870, 1920, 210, 0)} c="#8D8F9C" />
      <L d="M0,980 H1920" c="blanco" w={10} op={0.0} />
      {Array.from({length: 9}).map((_, i) => (
        <R key={i} d={rr(40 + i * 230 - ((f * 3) % 230), 968, 120, 14, 5)} c="blanco" />
      ))}
      {tema === 'taxi' && (
        <g transform={`translate(${-300 + u * 2400},${940 + Math.sin(f / 4) * 3}) scale(1.5)`}>{React.createElement(coche)}</g>
      )}
      <g transform="translate(1300,800)">
        <L d="M0,0 V-300 Q0,-340 40,-340 H80" w={12} />
        <F d={rr(60, -362, 70, 44, 10)} c="amarillo" w={5} />
      </g>
      <Actor x={1560} pies={880} k={0.9} look={CLIENTES[s % 3]} pose={foco ? 'senala' : pose} cara={cara} voltea s={s} t0={4} />
      <Pieza o={foco !== 'local' ? foco : undefined} x={1290} y={690} k={0.5} t0={12} s={s} rot={5} />
      <Burbuja o={burbuja} x={1770} y={310} k={0.5} s={s} cola="izq" />
    </g>
  );
};

// ---------------------------------------------------------------- C. oficina / ventanilla
export const Oficina: React.FC<EP> = ({foco, burbuja, cara, pose, v, s}) => {
  const f = useCurrentFrame();
  const sello = f % 60 < 8 ? (f % 60) * 6 : 0;
  return (
    <g>
      <R d={rr(0, 0, 1920, 800, 0)} c="#E9E4D4" />
      <Suelo y={800} c="#C8CCD8" />
      <g transform="translate(150,330)">
        <F d={ci(80, 80, 90)} c="blanco" />
        <L d="M80,80 V30 M80,80 L118,98" w={9} />
        <L d="M80,-10 V2 M80,158 V170 M-10,80 H2 M158,80 H170" w={7} />
      </g>
      <F d={rr(440, 290, 240, 160, 8)} c="cielo" />
      <L d="M470,330 H650 M470,370 H620 M470,410 H600" w={6} />
      <Actor x={1150} pies={940} k={1.0} look="funcionario" pose="sostiene" cara={cara === 'feliz' ? 'serio' : cara} s={s} t0={3} />
      {/* ventanilla */}
      <F d={rr(820, 330, 660, 24, 8)} c="oscuro" />
      <F d={rr(800, 760, 700, 50, 12)} c="madera" />
      <F d={rr(830, 810, 640, 270, 10)} c="azul" />
      <T x={1150} y={960} px={64} anchor="middle" c="blanco" fam="D Baloo" borde={false}>VENTANILLA 3</T>
      {foco !== 'sello' && (
        <g transform={`translate(1000,${690 + sello * 0.5})`}>
          <g transform="scale(0.45)">{React.createElement(OBJ.sello)}</g>
        </g>
      )}
      <Pieza o={foco ?? 'documento'} x={1330} y={580} k={0.62} t0={9} s={s} />
      <Actor x={420} pies={1040} k={0.95} look={CLIENTES[s % 3]} pose="sostiene" cara={cara === 'feliz' ? 'pensando' : cara} s={s + 1} t0={5} mano={<g transform="translate(18,-30) rotate(14) scale(0.17)">{React.createElement(OBJ.documento)}</g>} />
      <Burbuja o={burbuja} x={300} y={400} k={0.55} s={s} cola="der" />
    </g>
  );
};

// ---------------------------------------------------------------- D. las cuentas, de noche
export const Cuentas: React.FC<EP> = ({foco, burbuja, cara, v, s}) => {
  const f = useCurrentFrame();
  return (
    <g>
      <R d={rr(0, 0, 1920, 820, 0)} c="#4A5A85" />
      <Suelo y={820} c="#34406A" />
      <Ventana x={1180} y={320} w={420} h={300} noche />
      <path d={ci(560, 430, 330)} fill="#FFE9A0" opacity={0.18 + Math.sin(f / 8) * 0.01} />
      <g transform="translate(560,300)">
        <L d="M0,0 V-60" w={8} />
        <F d="M-70,10 L70,10 L40,-70 L-40,-70 Z" c="amarillo" />
      </g>
      <Actor x={640} pies={1000} k={1.05} look={cara === 'preocupado' ? 'duena' : 'cliente'} pose="quieto" cara={cara} s={s} t0={3} />
      {/* mesa */}
      <F d={rr(260, 780, 1100, 50, 12)} c="madera" />
      <F d={rr(300, 830, 1020, 250, 8)} c="oscuro" />
      <g transform="translate(1180,730) scale(0.75)">
        <F d={rr(-100, -90, 200, 90, 12)} c="gris" />
        <F d={rr(-80, -76, 160, 28, 6)} c="verde" w={4} />
        {[0, 1, 2, 3].map((i) => (
          <F key={i} d={rr(-84 + i * 44, -34, 34, 22, 5)} c="blanco" w={4} />
        ))}
      </g>
      <Pieza o={foco ?? 'ticket'} x={900} y={560} k={0.82} t0={9} s={s} />
      {[0, 1, 2].map((i) => (
        <g key={i} transform={`translate(${1520 + i * 90},${680 - ((f * 1.6 + i * 40) % 220)}) rotate(${i * 18 - 10})`} opacity={1 - ((f * 1.6 + i * 40) % 220) / 260}>
          <F d={ci(0, 0, 30)} c="amarillo" w={5} />
          <T x={0} y={13} px={38} anchor="middle" fam="D Baloo" borde={false}>€</T>
        </g>
      ))}
      <Burbuja o={burbuja} x={380} y={380} k={0.62} s={s} cola="der" />
    </g>
  );
};

// ---------------------------------------------------------------- E. trastienda / cocina
export const Trastienda: React.FC<EP> = ({foco, burbuja, cara, pose, v, tema, s}) => {
  const f = useCurrentFrame();
  return (
    <g>
      <R d={rr(0, 0, 1920, 800, 0)} c="#D9C2A4" />
      {Array.from({length: 9}).map((_, r) =>
        Array.from({length: 12}).map((_, c) => (
          <L key={`${r}${c}`} d={`M${c * 170 + (r % 2) * 85},${r * 90} h140`} w={3} op={0.12} />
        )),
      )}
      <Suelo y={800} c="#A89A86" />
      <g>
        <F d={rr(1160, 330, 640, 18, 6)} c="madera" />
        <F d={rr(1160, 560, 640, 18, 6)} c="madera" />
        {[0, 1, 2, 3].map((i) => (
          <Caja3 key={i} x={1250 + i * 150} y={330} k={0.9} c={['madera', 'amarillo', 'verde', 'azul'][i]} />
        ))}
        {[0, 1, 2].map((i) => (
          <Caja3 key={i} x={1280 + i * 190} y={560} k={0.9} c={['rosa', 'madera', 'rojo'][i]} />
        ))}
      </g>
      <g transform="translate(260,640) scale(1.7)">{React.createElement(tema === 'burger' ? OBJ.fuego : OBJ.nevera)}</g>
      <Actor x={820} pies={960} k={1.0} look={tema === 'burger' ? 'cocinero' : OWNER[tema] ?? 'duena'} pose="sostiene" cara={cara} s={s} t0={3} mano={<g transform="translate(10,-40) scale(0.38)">{React.createElement(OBJ.bolsa)}</g>} />
      <F d={rr(1180, 790, 560, 60, 10)} c="madera" />
      <F d={rr(1210, 850, 500, 230, 8)} c="oscuro" />
      <Pieza o={foco ?? 'caja'} x={1460} y={640} k={0.72} t0={9} s={s} />
      <Burbuja o={burbuja} x={540} y={450} k={0.55} s={s} cola="der" />
      <g transform={`translate(${1680 + Math.sin(f / 20) * 6},210)`}>
        <F d={ci(0, 0, 52)} c="blanco" w={5} />
        <L d="M0,0 V-34 M0,0 L24,14" w={6} />
      </g>
    </g>
  );
};

// ---------------------------------------------------------------- F. cola de clientes
export const Cola: React.FC<EP> = ({foco, burbuja, cara, pose, v, tema, s}) => {
  const looks = ['cliente', 'cliente2', 'cliente3', 'cliente', 'cliente2'];
  const caras = ['serio', 'preocupado', 'feliz', 'sorpresa', 'serio'] as const;
  return (
    <g>
      <R d={rr(0, 0, 1920, 800, 0)} c={PAREDES[(v + 1) % 5]} />
      <Suelo y={800} c={SUELOS[(v + 1) % 5]} />
      <F d={rr(1380, 330, 380, 460, 12)} c="madera" />
      <F d={rr(1410, 370, 320, 400, 8)} c="cielo" />
      <Letrero x={1570} y={290} w={420} h={80} texto={RUOTULO[tema] ?? 'TIENDA'} c="rojo" px={56} />
      {[0, 1, 2, 3].map((i) => (
        <Actor key={i} x={1250 - i * 310} pies={1030 - i * 12} k={0.88 - i * 0.03} look={looks[i]} pose={i === 0 ? 'senala' : i === 2 ? 'cadera' : 'quieto'} cara={i === 0 ? cara : caras[i]} s={s + i} t0={3 + i * 5} />
      ))}
      <Pieza o={foco} x={1570} y={560} k={0.5} t0={14} s={s} />
      <Burbuja o={burbuja} x={560} y={420} k={0.6} s={s} cola="der" />
    </g>
  );
};

// ---------------------------------------------------------------- G. edificio grande
export const Edificio: React.FC<EP> = ({foco, burbuja, cara, pose, v, tema, s}) => {
  const f = useCurrentFrame();
  const K = foco === 'banco' ? OBJ.banco : OBJ.ayuntamiento;
  return (
    <g>
      <Cielo />
      <path d={el(420, 330, 150, 46)} fill="#FFFFFF" />
      <path d={el(1500, 270, 120, 36)} fill="#FFFFFF" />
      <g transform="translate(960,560) scale(2.55)">{React.createElement(K)}</g>
      <R d={rr(0, 930, 1920, 150, 0)} c="#9AB68A" />
      <L d="M0,930 H1920" w={6} />
      <F d={rr(720, 930, 480, 150, 10)} c="gris" />
      <g transform={`translate(1560,500)`}>
        <L d="M0,500 V-30" w={10} />
        <F d={`M0,-30 H${130 + Math.sin(f / 6) * 8} L${100 + Math.sin(f / 6) * 8},10 L${130 + Math.sin(f / 6) * 8},50 H0 Z`} c="rojo" w={5} />
      </g>
      <Actor x={460} pies={1050} k={0.8} look={CLIENTES[s % 3]} pose="senala" cara={cara} s={s} t0={5} />
      <Pieza o={foco !== 'banco' && foco !== 'ayuntamiento' ? foco : undefined} x={1530} y={800} k={0.55} t0={11} s={s} />
      <Burbuja o={burbuja} x={300} y={500} k={0.55} s={s} cola="der" />
    </g>
  );
};

// ---------------------------------------------------------------- H. reparto
export const Reparto: React.FC<EP> = ({foco, burbuja, cara, v, tema, s, n}) => {
  const f = useCurrentFrame();
  const u = suave(f / Math.max(24, n * 0.45));
  return (
    <g>
      <Cielo />
      <Bloque x={1380} y={330} w={240} h={470} c="amarillo" cols={2} />
      <Bloque x={1650} y={400} w={230} h={400} c="rosa" cols={2} />
      <R d={rr(0, 800, 1920, 70, 0)} c="gris" />
      <L d="M0,800 H1920" w={6} />
      <R d={rr(0, 870, 1920, 210, 0)} c="#8D8F9C" />
      {Array.from({length: 9}).map((_, i) => (
        <R key={i} d={rr(40 + i * 230, 968, 120, 14, 5)} c="blanco" />
      ))}
      <g transform={`translate(${-420 + u * 1020},${860 + Math.sin(f / 3.5) * 3}) scale(2.1)`}>{React.createElement(OBJ.camion)}</g>
      {[0, 1, 2].map((i) => (
        <g key={i} opacity={clamp01((f - 24 - i * 8) / 6)}>
          <Caja3 x={1010 + i * 120} y={880 - (i === 2 ? 70 : 0)} k={0.9} c={['madera', 'amarillo', 'verde'][i]} />
        </g>
      ))}
      <Actor x={1520} pies={930} k={0.85} look="repartidor" pose="sostiene" cara={cara} s={s} t0={20} />
      <Pieza o={foco} x={1260} y={460} k={0.6} t0={26} s={s} />
      <Burbuja o={burbuja} x={1760} y={360} k={0.5} s={s} cola="izq" />
    </g>
  );
};

// ---------------------------------------------------------------- I. interior del taxi
export const TaxiInt: React.FC<EP> = ({foco, burbuja, cara, v, s, n}) => {
  const f = useCurrentFrame();
  return (
    <g>
      <Cielo />
      {/* ciudad que pasa */}
      {Array.from({length: 7}).map((_, i) => {
        const x = ((i * 380 - f * 5) % 2660 + 2660) % 2660 - 340;
        return <Bloque key={i} x={x} y={260 + (i % 3) * 40} w={260} h={440 - (i % 3) * 40} c={['rosa', 'azul', 'verde', 'amarillo', 'lila', 'naranja', 'cielo'][i]} cols={2} filas={3} />;
      })}
      <R d={rr(0, 700, 1920, 380, 0)} c="#5C5F73" />
      <L d="M0,700 H1920" w={7} />
      {/* parabrisas */}
      <F d="M110,170 H1810 L1880,730 H40 Z" c="blanco" op={0} w={9} />
      <F d={rr(0, 0, 1920, 120, 0)} c="oscuro" />
      <F d={rr(820, 100, 280, 80, 14)} c="cielo" />
      <Actor x={560} pies={1120} k={1.18} look="taxista" pose="quieto" cara={cara} s={s} t0={3} piernas={false} />
      {/* salpicadero */}
      <F d="M0,760 Q960,690 1920,760 V1080 H0 Z" c="oscuro" />
      <g transform={`translate(560,860) rotate(${Math.sin(f / 22) * 7}) scale(1.3)`}>{React.createElement(OBJ.volante)}</g>
      <g transform="translate(1180,830) scale(1.25)">{React.createElement(OBJ.taximetro)}</g>
      <Pieza o={foco} x={1560} y={820} k={0.62} t0={10} s={s} sombra={false} />
      <Burbuja o={burbuja} x={900} y={470} k={0.5} s={s} cola="izq" />
    </g>
  );
};

// ---------------------------------------------------------------- J. salon de peluqueria
export const Salon: React.FC<EP> = ({foco, burbuja, cara, v, s}) => {
  const f = useCurrentFrame();
  return (
    <g>
      <R d={rr(0, 0, 1920, 800, 0)} c={PAREDES[(v + 2) % 5]} />
      <Suelo y={800} c="#E8E0F0" />
      <F d={rr(300, 300, 520, 400, 60)} c="madera" />
      <F d={rr(330, 328, 460, 344, 40)} c="cielo" w={5} />
      <L d="M380,400 L520,330" c="blanco" w={18} />
      <F d={rr(1240, 380, 520, 18, 6)} c="madera" />
      {[0, 1, 2, 3, 4].map((i) => (
        <F key={i} d={rr(1270 + i * 96, 300, 56, 80, 12)} c={['rosa', 'morado', 'azul', 'verde', 'amarillo'][i]} w={4} />
      ))}
      {/* sillon y cliente con capa */}
      <g transform="translate(560,640) scale(1.5)">{React.createElement(OBJ.silla)}</g>
      <Actor x={560} pies={1010} k={0.95} look="cliente2" pose="quieto" cara={cara === 'preocupado' ? 'preocupado' : 'feliz'} s={s + 2} t0={4} piernas={false} />
      <F d="M390,720 Q560,650 730,720 L800,1040 H320 Z" c="blanco" />
      <L d="M470,730 Q560,770 650,730" w={5} />
      <Actor x={1010} pies={1020} k={1.0} look="peluquera" pose="sostiene" cara="feliz" s={s} t0={3} voltea mano={<g transform="translate(-10,-20) rotate(-30) scale(0.3)">{React.createElement(OBJ.tijeras)}</g>} />
      <Pieza o={foco} x={1500} y={640} k={0.7} t0={10} s={s} />
      <Burbuja o={burbuja} x={1180} y={420} k={0.5} s={s} cola="izq" />
      {[0, 1, 2].map((i) => (
        <g key={i} transform={`translate(${690 + i * 36},${760 + ((f * 2 + i * 30) % 90)}) rotate(${i * 40})`} opacity={1 - ((f * 2 + i * 30) % 90) / 110}>
          <F d={rr(-4, -22, 8, 44, 4)} c="oscuro" w={3} />
        </g>
      ))}
    </g>
  );
};

// ---------------------------------------------------------------- K. terraza
export const Terraza: React.FC<EP> = ({foco, burbuja, cara, v, tema, s}) => {
  const f = useCurrentFrame();
  const Mesa: React.FC<{x: number; c: string}> = ({x, c}) => (
    <g>
      <L d={`M${x},500 V860`} w={12} />
      <F d={`M${x - 190},520 Q${x},330 ${x + 190},520 Z`} c={c} />
      <L d={`M${x - 100},470 Q${x - 60},520 ${x - 60},520 M${x},420 V520 M${x + 100},470 Q${x + 60},520 ${x + 60},520`} w={5} />
      <F d={el(x, 830, 130, 28)} c="blanco" />
      <L d={`M${x},830 V1010 M${x - 70},1010 H${x + 70}`} w={9} />
    </g>
  );
  return (
    <g>
      <Cielo />
      <Bloque x={40} y={280} w={300} h={520} c="lila" />
      <F d={rr(1480, 300, 400, 500, 12)} c="blanco" />
      <Letrero x={1680} y={380} w={340} h={84} texto={RUOTULO[tema] ?? 'BAR'} c="verde" px={58} />
      <R d={rr(0, 800, 1920, 280, 0)} c="#CFC3A8" />
      <L d="M0,800 H1920" w={6} />
      <Mesa x={560} c="rojo" />
      <Mesa x={1180} c="amarillo" />
      <Actor x={400} pies={1000} k={0.78} look="cliente" pose="quieto" cara="feliz" s={s} t0={5} piernas={false} />
      <Actor x={720} pies={1000} k={0.78} look="cliente2" pose="saluda" cara="feliz" voltea s={s + 1} t0={8} piernas={false} />
      <Actor x={1560} pies={1040} k={0.92} look="camarero" pose="sostiene" cara={cara} s={s + 2} t0={4} mano={<g transform="translate(10,-34) scale(0.2)">{React.createElement(OBJ.taza)}</g>} />
      <Pieza o={foco ?? 'cana'} x={1180} y={730} k={0.4} t0={12} s={s} sombra={false} />
      <Burbuja o={burbuja} x={560} y={260} k={0.5} s={s} cola="der" />
    </g>
  );
};

// ---------------------------------------------------------------- L. cierre de noche
export const Cierre: React.FC<EP> = ({foco, burbuja, cara, v, tema, s, n}) => {
  const f = useCurrentFrame();
  const u = suave(f / Math.max(20, n * 0.6));
  return (
    <g>
      <Cielo noche />
      {[[300, 150], [700, 90], [1100, 200], [1500, 120], [1750, 260], [200, 380]].map(([x, y], i) => (
        <path key={i} d={ci(x, y, 5 + (i % 3))} fill="#FFF3B0" opacity={0.6 + Math.sin(f / 9 + i) * 0.3} />
      ))}
      <path d={ci(1600, 200, 80)} fill="#FFF3B0" />
      <path d={ci(1636, 182, 70)} fill="#46557F" />
      <F d={rr(400, 330, 840, 470, 12)} c="#E5E2D8" />
      <Letrero x={820} y={400} w={560} h={110} texto={RUOTULO[tema] ?? 'TIENDA'} c="oscuro" px={78} />
      <Persiana x={470} y={500} w={700} h={300} u={u} />
      <R d={rr(0, 800, 1920, 280, 0)} c="#39405E" />
      <L d="M0,800 H1920" w={6} />
      <g transform="translate(1320,800)">
        <L d="M0,0 V-300" w={12} />
        <path d={ci(0, -310, 90)} fill="#FFE9A0" opacity={0.25} />
        <F d={ci(0, -312, 30)} c="amarillo" w={5} />
      </g>
      <Actor x={1480} pies={1030} k={0.95} look={OWNER[tema] ?? 'duena'} pose="sostiene" cara={cara === 'feliz' ? 'serio' : cara} voltea s={s} t0={5} mano={<g transform="translate(0,-10) scale(0.26) rotate(-20)">{React.createElement(OBJ.llave)}</g>} />
      <Pieza o={foco} x={280} y={700} k={0.62} t0={10} s={s} />
      <Burbuja o={burbuja} x={1620} y={480} k={0.5} s={s} cola="izq" />
    </g>
  );
};

export const ESCENAS: Record<string, React.FC<EP>> = {
  tienda: Tienda,
  calle: Calle,
  oficina: Oficina,
  cuentas: Cuentas,
  trastienda: Trastienda,
  cola: Cola,
  edificio: Edificio,
  reparto: Reparto,
  taxi_int: TaxiInt,
  salon: Salon,
  terraza: Terraza,
  cierre: Cierre,
};
