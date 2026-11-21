import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {EP} from './base';
import {A, Almacen, Caja, Camion, Carro, Chip, Cifra, Col, Escenario, Eti, Fabrica, Hoja, Mapa, Marca, Mundo, PAL, Persona, Sans, Sello, Serif, T, Tienda, Tira, c01, camara, centro, geo, io, lerp, miles, mini, pop, rebote, rnd, sal, tr} from './kit';
import {ESP, MK, MX, MY, PRT} from './m_gancho';
import {Im} from './m_vox';


/** Recorte real (webp con alfa). Centro en (x, y), `w` de ancho. */
export const Recorte: React.FC<{src?: string; x: number; y: number; w: number; t: number; rot?: number}> = ({src, x, y, w, t, rot = 0}) =>
  t < 0 || !src ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, opacity: c01(t / 3)}}>
      <Img src={staticFile('vox/media/' + src)} style={{position: 'absolute', width: w, left: -w / 2, transform: `translateY(-50%) rotate(${rot}deg) scale(${0.5 + 0.5 * rebote(t / 12, 1.6)})`, filter: 'drop-shadow(0 20px 30px rgba(0,0,0,0.5))'}} />
    </div>
  );

/** 226-230 s · no es una cadena de tiendas: es una cadena de proveedores con tiendas al final. */
export const Cadena: React.FC<EP> = ({t, p}) => {
  const b = p(1);
  const fuera = tr(b, -2, 8);
  const XS = [330, 645, 960, 1275, 1590];
  return (
    <AbsoluteFill>
      <Escenario />
      <div style={{position: 'absolute', left: 150, top: 742, width: 1620, height: 6, background: '#30364A'}} />
      {/* A: tiendas encadenadas */}
      <svg width={1920} height={1080} style={{position: 'absolute', opacity: 1 - fuera}}>
        <path d="M330,630 L1590,630" stroke="#fff" strokeWidth={8} strokeDasharray="4 22" strokeLinecap="round" opacity={0.5 * tr(t, 8, 10)} />
      </svg>
      {XS.map((x, i) => (
        <Tienda key={i} x={x} y={760} s={0.6 * pop(t - i * 2, 11, 1.6) * (1 - fuera)} nombre="MERCADONA" />
      ))}
      <T x={960} y={190} op={tr(t, 0, 8) * (1 - fuera)}>
        <Serif tam={100} peso={600}>¿Una cadena de tiendas?</Serif>
      </T>
      <Marca tipo="no" x={960} y={190} t={t - 34} s={3 * (1 - fuera)} grosor={8} />
      {/* B: proveedores... y la tienda al final */}
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d="M250,820 L1740,820" stroke={PAL.verde[0]} strokeWidth={8} strokeDasharray="26 22" opacity={tr(b, 14, 10)} />
      </svg>
      <Fabrica x={250} y={750} s={0.92 * pop(b - 2, 11, 1.6)} color="cian" t={t} />
      <Fabrica x={620} y={750} s={0.92 * pop(b - 5, 11, 1.6)} color="ambar" t={t + 12} />
      <Fabrica x={990} y={750} s={0.92 * pop(b - 8, 11, 1.6)} color="lila" t={t + 24} />
      <Almacen x={1370} y={750} s={0.52 * pop(b - 11, 11, 1.6)} />
      <Tienda x={1720} y={756} s={0.58 * pop(b - 16, 11, 1.8)} nombre="MERCADONA" />
      <T x={640} y={890} op={tr(b, 12, 8)}>
        <Eti tam={32} color="#C9CED8">proveedores</Eti>
      </T>
      <T x={1720} y={890} op={tr(b, 20, 8)}>
        <Eti tam={32} color={PAL.verde[0]}>tiendas</Eti>
      </T>
      <T x={960} y={170} op={tr(b, 2, 8)}>
        <Serif tam={92} peso={600}>Una cadena de <span style={{color: '#FFD95A'}}>proveedores</span></Serif>
      </T>
      <T x={960} y={290} op={tr(b, 18, 8)}>
        <Serif tam={64} peso={500} it color="#C9CED8">con tiendas al final</Serif>
      </T>
    </AbsoluteFill>
  );
};

/** 230-235 s · casi 8 de cada 10 EUR que vende son de sus marcas: Hacendado, Deliplus, Bosque Verde. */
export const Marcas: React.FC<EP> = ({t, p, ctx}) => {
  const noms: [string, Col][] = [['Hacendado', 'verde'], ['Deliplus', 'rosa'], ['Bosque Verde', 'cian']];
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={130} y={170} ancla="i" s={pop(t, 12, 1.4)}>
        <Cifra tam={160}>8 de cada 10 €</Cifra>
      </T>
      <T x={138} y={290} ancla="i" op={tr(t, 8, 8)}>
        <Sans tam={50} peso={700}>que vende son de sus propias marcas</Sans>
      </T>
      <Im src="g_lineal" x={560} y={1040} w={900} t={t - 4} de="aba" />
      <div style={{position: 'absolute', left: 112, top: 404, width: 730 * io(tr(t, 16, 26)), height: 634, border: '7px solid #2BE38A', borderRadius: 14, boxShadow: '0 0 40px rgba(43,227,138,0.35)', opacity: tr(t, 16, 6)}} />
      <T x={480} y={370} s={pop(t - 34, 11, 1.5)}>
        <Chip tam={36}>sus marcas</Chip>
      </T>
      <Im src="g_marcas" x={1490} y={720} w={760} t={t - 10} de="der" />
      {noms.map(([n, c], i) => (
        <T key={n} x={[1130, 1400, 1670][i]} y={830 + (i % 2) * 70} s={pop(p(i + 1), 11, 1.7)} rot={(i - 1) * 3}>
          <Chip tam={46} color={c}>{n}</Chip>
        </T>
      ))}
    </AbsoluteFill>
  );
};

const Catalogo: React.FC<{x: number; y: number; s: number}> = ({x, y, s}) => (
  <A x={x} y={y} s={s}>
    <rect x={-150} y={-190} width={300} height={380} rx={16} fill="#F1F3F7" />
    <rect x={-150} y={-190} width={36} height={380} rx={10} fill="#C5CBD7" />
    <rect x={-96} y={-160} width={220} height={44} rx={8} fill="url(#g-rosa)" />
    {[0, 1, 2, 3, 4, 5].map((k) => (
      <rect key={k} x={-96 + (k % 2) * 116} y={-96 + Math.floor(k / 2) * 92} width={104} height={78} rx={8} fill={['#FFD95A', '#45D0FF', '#B79CFF', '#FF6A5C', '#2BE38A', '#C5CBD7'][k]} opacity={0.85} />
    ))}
  </A>
);

/** 236-242 s · no compra de catalogo: encarga a fabricantes concretos, durante anos, cantidades enormes. */
export const Encargo: React.FC<EP> = ({t, p}) => {
  const u1 = tr(p(1), -4, 12);
  const ped = io(tr(p(1), 6, 22));
  return (
    <AbsoluteFill>
      <Escenario />
      <Im src="g_catalogo" x={lerp(960, 250, io(u1))} y={lerp(700, 340, io(u1))} w={lerp(760, 300, io(u1))} t={t} de="pop" />
      <T x={lerp(960, 250, io(u1))} y={lerp(830, 410, io(u1))} op={tr(t, 6, 8)} s={lerp(1, 0.62, io(u1))}>
        <Chip tam={54} color="humo">De catálogo</Chip>
      </T>
      <Marca tipo="no" x={lerp(960, 250, io(u1))} y={lerp(520, 250, io(u1))} t={t - 22} s={lerp(4.2, 1.9, io(u1))} grosor={8} />
      <div style={{position: 'absolute', left: 380, top: 842, width: 1420, height: 6, background: '#30364A', opacity: tr(p(1), 0, 8)}} />
      <Fabrica x={640} y={846} s={1.45 * pop(p(1), 12, 1.5)} t={t} />
      <Tienda x={1540} y={850} s={1.05 * pop(p(1) - 4, 12, 1.5)} nombre="MERCADONA" />
      <T x={640} y={930} op={tr(p(1), 8, 8)}>
        <Chip tam={44} color="ambar" tinta="#1B1D22">Un fabricante concreto</Chip>
      </T>
      {/* el encargo viaja de la tienda a la fabrica */}
      {p(1) >= 6 && p(3) < 0 && (
        <A x={lerp(1420, 800, ped)} y={560 - Math.sin(ped * Math.PI) * 120} s={1.1} rot={-8 + ped * 16}>
          <rect x={-46} y={-58} width={92} height={116} rx={8} fill="#FAFAF7" />
          {[0, 1, 2, 3].map((k) => <rect key={k} x={-30} y={-38 + k * 22} width={k === 3 ? 34 : 60} height={8} rx={4} fill="#9AA1AE" />)}
        </A>
      )}
      <T x={1090} y={380} op={tr(p(1), 10, 8) * (1 - tr(p(2), -2, 6))}>
        <Eti tam={32} color="#C9CED8">se lo encarga</Eti>
      </T>
      {[0, 1, 2, 3, 4].map((k) => (
        <Hoja key={k} x={830 + k * 130} y={330} anio={`año ${k + 1}`} s={0.62 * pop(p(2) - k * 4, 10, 1.8)} color="verde" tam={40} op={1 - tr(p(3), 20, 8) * 0.0} />
      ))}
      <T x={1090} y={236} op={tr(p(2), 4, 8)}>
        <Sans tam={46} peso={700}>Trabajan juntos durante años</Sans>
      </T>
      {[0, 1, 2].map((k) => {
        const u = tr(p(3), k * 9, 40);
        return u <= 0 || u >= 1 ? null : <Camion key={k} x={lerp(860, 1320, u)} y={850} s={0.5} avance={u * 900} />;
      })}
      <T x={1100} y={640} s={pop(p(3) - 4, 11, 1.5)}>
        <Chip tam={52}>Cantidades enormes</Chip>
      </T>
    </AbsoluteFill>
  );
};

const esp = centro('ESP', MX, MY, MK);
/** 243-250 s · 30.200 M EUR a proveedores espanoles en un ano. Esa red es su ventaja... y su ancla. */
export const RedEs: React.FC<EP> = ({t, p, dur}) => {
  const cam = camara(t, [
    [0, 660, 850, 2.7],
    [dur, 650, 870, 2.95],
  ]);
  const N = 420;
  const hunde = sal(tr(p(2), 6, 26)) * 14;
  const lineas = React.useMemo(() => Array.from({length: 150}, (_, i) => [Math.floor(rnd(i * 2.3) * N), Math.floor(rnd(i * 5.1 + 2) * N)] as [number, number]).filter(([a, b]) => Math.hypot(ESP[a][0] - ESP[b][0], ESP[a][1] - ESP[b][1]) < 46), []);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <div style={{position: 'absolute', left: 0, top: hunde, width: 0, height: 0}}>
          <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0F4A2D', borde: PAL.verde[1]} : undefined)} />
          <svg width={1} height={1} style={{position: 'absolute', overflow: 'visible'}}>
            {lineas.map(([a, b], i) => {
              const [x0, y0] = geo(ESP[a], MX, MY, MK);
              const [x1, y1] = geo(ESP[b], MX, MY, MK);
              return <path key={i} d={`M${x0},${y0} L${x1},${y1}`} stroke="#FFD95A" strokeWidth={0.5} opacity={0.5 * tr(p(1), i * 0.12, 8)} />;
            })}
            {ESP.slice(0, N).map((q, i) => {
              const [x, y] = geo(q, MX, MY, MK);
              return <circle key={i} cx={x} cy={y} r={1.7 * pop(t - 4 - i * 0.12, 8, 2.6)} fill="#FFD95A" />;
            })}
          </svg>
          <Im src="g_ancla" x={esp[0] + 8} y={esp[1] + 80} w={78} t={p(2)} de="pop" luz={1.7} />
        </div>
      </Mundo>
      <T x={110} y={230} ancla="i" s={pop(t - 2, 12, 1.4)}>
        <Cifra tam={170} color="ambar">{miles(Math.round(30200 * sal(t / 46)))} M€</Cifra>
      </T>
      <T x={118} y={356} ancla="i" op={tr(t, 8, 8)}>
        <Sans tam={46} peso={700}>en compras a proveedores españoles</Sans>
      </T>
      <T x={118} y={420} ancla="i" op={tr(t, 12, 8)}>
        <Sans tam={40} peso={500} color="#C9CED8">en un solo año</Sans>
      </T>
      <T x={118} y={640} ancla="i" s={pop(p(1), 12, 1.5)}>
        <Chip tam={72}>Su ventaja</Chip>
      </T>
      <T x={118} y={790} ancla="i" s={pop(p(2), 12, 1.5)}>
        <Chip tam={72} color="humo">…y su ancla</Chip>
      </T>
    </AbsoluteFill>
  );
};

const Estante: React.FC<{x: number; y: number; filas?: number; ancho?: number}> = ({x, y, filas = 3, ancho = 900}) => (
  <>
    {Array.from({length: filas}, (_, r) => (
      <div key={r} style={{position: 'absolute', left: x, top: y + r * 200, width: ancho, height: 14, borderRadius: 7, background: '#4A5165'}} />
    ))}
    <div style={{position: 'absolute', left: x - 6, top: y - 190, width: 14, height: 200 * filas + 4, background: '#333949'}} />
    <div style={{position: 'absolute', left: x + ancho - 8, top: y - 190, width: 14, height: 200 * filas + 4, background: '#333949'}} />
  </>
);

/** 250-257 s · Carrefour o Lidl abren y llenan: marcas internacionales y su marca blanca de siempre. */
export const OtrosAbren: React.FC<EP> = ({t, p}) => {
  const COLS: Col[] = ['rojo', 'ambar', 'cian', 'lila', 'rosa', 'ambar', 'cian', 'rojo'];
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={130} y={140} ancla="i" s={pop(t, 11, 1.4)}>
        <Chip tam={60} color="azul">Carrefour</Chip>
      </T>
      <T x={560} y={140} ancla="i" s={pop(t - 4, 11, 1.4)}>
        <Chip tam={60} color="azul" tinta="#FFE600">Lidl</Chip>
      </T>
      <T x={136} y={270} ancla="i" op={tr(t, 8, 8)}>
        <Serif tam={64} peso={600}>abren en un país nuevo…</Serif>
      </T>
      <Tienda x={420} y={860} s={1.1 * pop(t - 8, 12, 1.5)} color="azul" />
      <Im src="g_lineal" x={1360} y={1000} w={1000} t={t - 6} de="nada" luz={0.16} gris={1} />
      <Im src="g_lineal" x={1360} y={1000} w={1000} t={p(1)} de="nada" recorte={`inset(0 ${(1 - io(tr(p(1), 0, 50))) * 100}% 0 0)`} />
      <T x={1350} y={196} s={pop(p(2), 11, 1.5)}>
        <Chip tam={46} color="humo">Marcas internacionales</Chip>
      </T>
      <T x={1350} y={1010} s={pop(p(3), 11, 1.5)}>
        <Chip tam={46} color="azul">Su marca blanca de siempre</Chip>
      </T>
      <Sello x={420} y={420} t={p(3) + 14} tam={84} rot={-8} color={PAL.verde[0]}>Lleno</Sello>
    </AbsoluteFill>
  );
};

/** 257-265 s · Mercadona tiene que volver a construir la red: quien le hace el pan, el pescado, el yogur. */
export const MercAbre: React.FC<EP> = ({t, p, ctx}) => {
  const col = (i: number, x: number, w: number, q: string) => (
    <>
      <Recorte src={ctx?.medios?.[i]?.src} x={x} y={520} w={w} t={p(i + 1)} rot={(i - 1) * 3} />
      <Fabrica x={x - 60} y={930} s={0.62 * pop(p(i + 1) - 6, 11, 1.6)} color="humo" t={0} />
      <T x={x + 70} y={850} s={pop(p(i + 1) - 10, 11, 2)}>
        <Chip tam={64} color="ambar" tinta="#1B1D22">?</Chip>
      </T>
      <T x={x} y={990} op={tr(p(i + 1), 6, 8)}>
        <Sans tam={42} peso={700}>{q}</Sans>
      </T>
    </>
  );
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={130} y={120} ancla="i" s={pop(t, 11, 1.4)}>
        <Chip tam={60}>Mercadona</Chip>
      </T>
      <T x={560} y={122} ancla="i" op={tr(t, 6, 8)}>
        <Serif tam={76} peso={600}>tiene que <span style={{color: '#FFD95A'}}>volver a construir la red</span></Serif>
      </T>
      {col(0, 400, 520, '¿Quién le hace el pan?')}
      {col(1, 960, 500, '¿Quién le trae el pescado?')}
      {col(2, 1520, 480, '¿Quién le fabrica el yogur?')}
      <T x={1520} y={250} s={pop(p(4), 11, 1.6)} rot={4}>
        <Chip tam={44} color="humo">a su manera y a su precio</Chip>
      </T>
    </AbsoluteFill>
  );
};

const POVOA = geo([92.4, 764], MX, MY, MK);
const ALMEIRIM = geo([95, 826], MX, MY, MK);
/** 266-277 s · en Portugal: ~1.000 proveedores, 1.500 M EUR al ano, dos bloques logisticos, directores portugueses. */
export const RedPt: React.FC<EP> = ({t, p, dur}) => {
  const cam = camara(t, [
    [0, 800, 892, 4.6],
    [dur, 806, 892, 5],
  ]);
  const bloque = (q: [number, number], tt: number, nombre: string, yEt: number) => {
    const sx = 960 + (q[0] - cam.x) * cam.z;
    const sy = 540 + (q[1] - cam.y) * cam.z;
    return (
      <>
        <svg width={1920} height={1080} style={{position: 'absolute'}}>
          <path d={`M${sx - 16},${sy} L${130 + 330},${yEt}`} stroke="#fff" strokeWidth={3} opacity={0.6 * tr(tt, 4, 8)} />
        </svg>
        <div style={{position: 'absolute', left: sx, top: sy + 12, width: 0, height: 0}}>
          <Almacen x={0} y={0} s={0.2 * pop(tt, 11, 2.2)} />
        </div>
        <T x={120} y={yEt} ancla="i" s={pop(tt - 2, 11, 1.5)}>
          <Chip tam={36} fondo="#F4F5F7" tinta="#0B0C10">{nombre}</Chip>
        </T>
      </>
    );
  };
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0E1712', borde: '#1E3A2B'} : c === 'PRT' ? {fill: '#12683D', borde: PAL.verde[0]} : undefined)} />
        <svg width={1} height={1} style={{position: 'absolute', overflow: 'visible'}}>
          {PRT.map((q, i) => {
            const [x, y] = geo(q, MX, MY, MK);
            const e = pop(t - 6 - i * 0.045, 7, 2.4);
            return e <= 0 ? null : <circle key={i} cx={x} cy={y} r={0.85 * e} fill="#FFD95A" />;
          })}
        </svg>
      </Mundo>
      {bloque(POVOA, p(3), 'Póvoa de Varzim', 250)}
      {bloque(ALMEIRIM, p(4), 'Almeirim', 760)}
      <T x={1040} y={170} ancla="i" s={pop(t - 4, 12, 1.4)}>
        <Cifra tam={150} color="ambar">≈ {miles(Math.round(1000 * sal(t / 44)))}</Cifra>
      </T>
      <T x={1048} y={272} ancla="i" op={tr(t, 10, 8)}>
        <Sans tam={42} peso={600} color="#C9CED8">proveedores locales</Sans>
      </T>
      <T x={1040} y={420} ancla="i" s={pop(p(1), 12, 1.4)}>
        <Cifra tam={150}>{miles(Math.round(1500 * sal(p(1) / 30)))} M€</Cifra>
      </T>
      <T x={1048} y={522} ancla="i" op={tr(p(1), 6, 8)}>
        <Sans tam={42} peso={600} color="#C9CED8">de compras al año</Sans>
      </T>
      <T x={1040} y={660} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Cifra tam={150}>2</Cifra>
      </T>
      <T x={1170} y={664} ancla="i" op={tr(p(2), 6, 8)}>
        <Sans tam={46} peso={700}>bloques logísticos</Sans>
      </T>
      <Im src="g_empleados" x={1330} y={1072} w={370} t={p(5)} de="aba" />
      <T x={1330} y={768} s={pop(p(5) - 10, 12, 1.5)} rot={-2}>
        <Chip tam={38} color="ambar" tinta="#1B1D22">Todos sus directores, portugueses</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 284-293 s · segunda razon, y es decision suya: no compra cadenas. Abre tienda a tienda. */
export const Segunda: React.FC<EP> = ({t, p}) => {
  const b = p(2);
  const a = 1 - tr(b, -3, 6);
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={520} y={540} s={pop(t, 14, 1.5) * a} op={a}>
        <Cifra tam={620} color="ambar">2</Cifra>
      </T>
      <T x={820} y={470} ancla="i" op={tr(t, 6, 8) * a}>
        <Serif tam={130} peso={600}>La segunda razón</Serif>
      </T>
      <T x={826} y={620} ancla="i" op={tr(p(1), 0, 8) * a}>
        <Serif tam={84} peso={500} it color="#FFD95A">es una decisión suya</Serif>
      </T>
      {b >= 0 && (
        <>
          <T x={960} y={130} op={tr(b, 0, 6)}>
            <Serif tam={96} peso={600}>Mercadona <span style={{color: '#FF6A5C'}}>no compra</span> cadenas</Serif>
          </T>
          <Im src="g_carro" x={330} y={760} w={470} t={b} de="pop" />
          <Tienda x={330} y={420} s={0.5 * pop(b - 8, 11, 1.8)} color="rosa" />
          <Marca tipo="no" x={330} y={520} t={b - 22} s={4.2} grosor={9} />
          <Tira x={1230} y={440} t={p(3)} ancho={1100} tam={52} rot={1.5} trozos={['«No vamos a hacer adquisiciones. ', {m: 'Abriremos tienda a tienda', en: p(3) - p(4)}, '»']} color="rgba(43,227,138,0.6)" />
          <T x={1230} y={600} op={tr(p(3), 10, 8)}>
            <Eti tam={24}>Juan Roig · 12 de marzo de 2019</Eti>
          </T>
          <div style={{position: 'absolute', left: 660, top: 942, width: 1150, height: 6, background: '#30364A', opacity: tr(p(4), 0, 8)}} />
          {[0, 1, 2, 3].map((k) => (
            <Tienda key={k} x={800 + k * 290} y={950} s={0.5 * pop(p(4) - k * 9, 11, 1.8)} nombre="MERCADONA" />
          ))}
        </>
      )}
    </AbsoluteFill>
  );
};

/** 294-307 s · la forma rapida: comprar a un competidor y cambiarle el letrero... con todo lo que heredas. */
export const Letrero: React.FC<EP> = ({t, p}) => {
  const XS = [300, 630, 960, 1290, 1620];
  const AN = [220, 300, 190, 260, 210];
  const ES = [1.1, 0.95, 1.2, 1, 1.15];
  const pegas = ['locales pequeños', 'su plantilla', 'sus contratos', 'sus vicios'];
  const igual = p(7);
  const fuera = tr(igual, -3, 7);
  return (
    <AbsoluteFill>
      <Escenario />
      <T x={130} y={130} ancla="i" op={tr(t, 0, 8) * (1 - tr(p(1), -3, 6))}>
        <Serif tam={92} peso={600}>Tienda a tienda: la forma <span style={{color: '#FFD95A'}}>lenta</span></Serif>
      </T>
      <T x={130} y={130} ancla="i" op={tr(p(1), 2, 8) * (1 - fuera)}>
        <Serif tam={84} peso={600}>La <span style={{color: '#FFD95A'}}>rápida</span>: comprar y cambiar el letrero</Serif>
      </T>
      <div style={{position: 'absolute', left: 120, top: 742, width: 1680, height: 6, background: '#30364A'}} />
      {p(1) < 0 && <Tienda x={960} y={760} s={1.2 * pop(t - 6, 14, 1.5)} nombre="MERCADONA" />}
      {XS.map((x, i) => {
        const u = tr(p(2), i * 4, 10);
        const giro = Math.abs(Math.cos(u * Math.PI));
        return (
          <div key={i} style={{position: 'absolute', left: x, top: 740, width: 0, height: 0, transform: `scaleX(${Math.max(0.05, giro)})`, opacity: 1 - fuera}}>
            <Tienda x={0} y={0} s={0.6 * ES[i] * pop(p(1) - 4 - i * 2, 11, 1.7)} ancho={AN[i] + 60} color={u > 0.5 ? 'verde' : 'rosa'} />
          </div>
        );
      })}
      {pegas.map((q, i) => (
        <T key={q} x={XS[i] + (i === 3 ? 165 : 0)} y={i === 3 ? 900 : 830} s={pop(p(i + 3), 11, 1.8) * (1 - fuera)} rot={(i % 2 ? 1 : -1) * 3}>
          <Chip tam={40} color="rojo">{q}</Chip>
        </T>
      ))}
      <T x={300} y={900} s={pop(p(3) - 8, 11, 1.5) * (1 - fuera)}>
        <Eti tam={28} color="#C9CED8">heredas</Eti>
      </T>
      {igual >= 0 && (
        <>
          <T x={960} y={170} op={tr(igual, 0, 6)}>
            <Serif tam={104} peso={600}>Y todas tienen que ser <span style={{color: '#FFD95A'}}>iguales</span></Serif>
          </T>
          {XS.map((x, i) => (
            <Tienda key={i} x={x} y={760} s={0.58 * pop(igual - i * 3, 9, 2)} nombre="MERCADONA" />
          ))}
        </>
      )}
    </AbsoluteFill>
  );
};

/** 307-319 s · objetivo de 2019: 150-200 tiendas en siete u ocho anos. Lleva 69; cerrara 2026 con 81. */
export const Objetivo: React.FC<EP> = ({t, p}) => {
  const fin = tr(p(5), -3, 8);
  return (
    <AbsoluteFill>
      <Escenario />
      <Hoja x={166} y={150} anio="2019" s={0.95 * pop(t, 12, 1.4)} color="humo" />
      <T x={280} y={114} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={28}>El objetivo en Portugal</Eti>
      </T>
      <T x={276} y={186} ancla="i" op={tr(p(1), -4, 8)}>
        <Serif tam={78} peso={600}>Entre 150 y 200 tiendas en siete u ocho años</Serif>
      </T>
      <svg width={1600} height={640} style={{position: 'absolute', left: 160, top: 300, overflow: 'visible', opacity: 1 - 0.92 * fin}}>
        {Array.from({length: 200}, (_, k) => {
          const c = k % 20;
          const r = Math.floor(k / 20);
          const e = pop(p(1) - 2 - (c + r) * 0.7, 8, 1.8);
          if (e <= 0) return null;
          const t69 = p(3) - k * 0.35;
          const t81 = p(4) - (k - 69) * 2;
          const llena = k < 69 ? t69 >= 0 : k < 81 ? t81 >= 0 : false;
          const x = c * 80 + 40;
          const y = r * 62 + 30;
          return llena ? (
            mini(x, y, 2.7 * (0.8 + 0.2 * rebote(c01((k < 69 ? t69 : t81) / 8), 2.4)), k < 69 ? PAL.verde[0] : '#FFD95A', '#EEF1F6', k)
          ) : (
            <rect key={k} x={x - 30} y={y - 24} width={60} height={46} rx={8} fill="none" stroke={k < 150 ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.22)'} strokeWidth={3} strokeDasharray={k < 150 ? undefined : '7 7'} transform={`scale(${e})`} style={{transformOrigin: `${x}px ${y}px`}} />
          );
        })}
      </svg>
      {fin < 1 && <Sello x={1500} y={330} t={p(5) < -3 ? p(2) : -1} tam={76} rot={-6}>Con retraso</Sello>}
      <T x={300} y={996} s={pop(p(3), 12, 1.5)} op={1 - fin}>
        <Cifra tam={130}>69</Cifra>
      </T>
      <T x={420} y={1000} ancla="i" op={tr(p(3), 6, 8) * (1 - fin)}>
        <Sans tam={40} peso={600} color="#C9CED8">a cierre de 2025</Sans>
      </T>
      <T x={1060} y={996} s={pop(p(4), 12, 1.5)} op={1 - fin}>
        <Cifra tam={130} color="ambar">81</Cifra>
      </T>
      <T x={1180} y={1000} ancla="i" op={tr(p(4), 6, 8) * (1 - fin)}>
        <Sans tam={40} peso={600} color="#C9CED8">previstas al acabar 2026</Sans>
      </T>
      <T x={960} y={560} op={tr(p(5), 2, 8)}>
        <Serif tam={112} peso={600}>Tienda a tienda, un país tarda</Serif>
      </T>
      <T x={960} y={720} s={pop(p(5) - 16, 12, 1.5)}>
        <Cifra tam={190} color="ambar">más de una década</Cifra>
      </T>
    </AbsoluteFill>
  );
};

export const CAP3 = {cadena: Cadena, marcas: Marcas, encargo: Encargo, red_es: RedEs, otros_abren: OtrosAbren, merc_abre: MercAbre, red_pt: RedPt, segunda: Segunda, letrero: Letrero, objetivo: Objetivo};
