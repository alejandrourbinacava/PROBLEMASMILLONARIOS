import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {Chip, Escenario, Eti, Hoja, Mapa, Marca, Mundo, Palabras, Sans, Sello, Serif, T, c01, camara, io, lerp, pop, sal, tr} from './kit';
import {Detras} from './m_capas';
import {MK, MX, MY} from './m_gancho';
import {Im, deriva} from './m_vox';
import {AM, Am, Dato, Fondo, Parrafo, Quien, Tit} from './p_comun';
import {Ciudad, Flor, GRIS, Reparto, ROJO} from './c_comun';

/**
 * «Por que Chupa Chups vende MAS fuera de Espana que dentro» · gancho y capitulos 1 y 2.
 * Cada plano: foto real desenfocada al fondo, elementos de foto de estudio y texto que entra con la voz.
 * La flor que se dibuja es una margarita generica (c_comun), no el logotipo de la marca.
 */
const ESP = (c: string) => (c === 'ESP' ? {fill: '#5A1A1E', borde: ROJO} : undefined);
// puntos del mapa (coordenadas del mundo: MX + x*MK, MY + y*MK)
export const VILLAMAYOR: [number, number] = [745.2, 784.7];
export const SANT_ESTEVE: [number, number] = [916.3, 844.6];
const PERPINAN: [number, number] = [940.8, 806.1];
const BAYONA: [number, number] = [836.7, 780.4];
/** Un caramelo de frente (bola envuelta) dibujado, para ensenar donde va la flor. */
const Bola: React.FC<{x: number; y: number; r: number; t: number; children?: React.ReactNode}> = ({x, y, r, t, children}) =>
  t < 0 ? null : (
    <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, transform: `scale(${pop(t, 12, 1.4)})`}}>
      <div style={{position: 'absolute', left: -13, top: r - 10, width: 26, height: r * 0.95, borderRadius: 13, background: 'linear-gradient(90deg,#fff,#C9CED8)'}} />
      <div style={{position: 'absolute', left: -r, top: -r, width: r * 2, height: r * 2, borderRadius: r, overflow: 'hidden', background: 'radial-gradient(circle at 34% 30%, #FF8A7E 0%, #E0352B 46%, #9A1118 100%)', boxShadow: '0 30px 60px rgba(0,0,0,0.5)'}}>{children}</div>
    </div>
  );

// =============================================================== GANCHO
/** Es un caramelo con un palo. No tiene mas misterio. */
export const Caramelo: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.08);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.36} blur={12} />
      <Detras x={960} y={320} t={t} tam={250}>Un caramelo</Detras>
      <Im src="g_piruleta" x={960} y={1210} w={300} t={t - 2} de="aba" cam={cam} />
      <T x={1400} y={650} s={pop(t - 16, 12, 1.5)} rot={-3}>
        <Chip tam={70} color="ambar" tinta="#1B1D22">con un palo</Chip>
      </T>
      <T x={500} y={820} s={pop(p(1), 12, 1.4)} rot={2}>
        <Chip tam={50} color="humo">No tiene más misterio</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Mas de 160 paises; lo dibujo Dali, lo llevo un entrenador del Barca y viajo a una estacion espacial. */
export const Tres: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Im src="g_globo" x={380} y={1100} w={390} t={t - 2} de="aba" cam={cam} />
      <Dato x={380} y={210} t={t - 4} cifra="+160" pie="países" tam={230} color="ambar" />
      <div style={{position: 'absolute', left: 860, top: 110, width: 2, height: 860, background: 'rgba(255,255,255,0.1)'}} />
      <Flor x={1010} y={270} r={84} u={tr(p(1), 0, 24)} relleno={tr(p(1), 18, 12)} trazo="#F4F5F7" grosor={5} />
      <T x={1150} y={270} ancla="i" op={tr(p(1), 6, 8)}>
        <Sans tam={54} peso={700}>Lo dibujó Salvador Dalí</Sans>
      </T>
      <Im src="g_balon" x={1010} y={640} w={170} t={p(2)} de="pop" />
      <Parrafo x={1150} y={494} w={700} t={p(2)} tam={54} peso={700}>Lo llevó en la boca un entrenador del Barça</Parrafo>
      <Im src="g_estacion" x={1010} y={880} w={250} t={p(3)} de="pop" />
      <T x={1150} y={850} ancla="i" op={tr(p(3), 6, 8)}>
        <Sans tam={54} peso={700}>Viajó a una estación espacial</Sans>
      </T>
    </AbsoluteFill>
  );
};

/** Inventado en 1958. En 1970, uno de cada diez fuera; en 1980, nueve de cada diez. */
export const Vuelta: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Hoja x={190} y={160} anio="1958" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Tit x={320} y={160} t={t - 4} ancla="i" tam={76}>Lo inventa un confitero español</Tit>
      <Reparto x={160} y={420} w={1080} t={p(1)} fuera={0.1} etiqueta="1970 · doce años después" />
      <T x={1290} y={462} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Chip tam={46} color="humo">1 de cada 10, fuera</Chip>
      </T>
      <Reparto x={160} y={690} w={1080} t={p(3)} fuera={0.9} etiqueta="1980 · diez años más tarde" />
      <T x={1290} y={732} ancla="i" s={pop(p(4), 12, 1.5)}>
        <Chip tam={50} color="ambar" tinta="#1B1D22">9 de cada 10, fuera</Chip>
      </T>
      <Im src="g_piruletas" x={1580} y={1150} w={440} t={t - 6} de="der" />
    </AbsoluteFill>
  );
};

/** Llego a vender fuera mas del 90 % de lo que facturaba. */
export const Noventa: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.07);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Im src="g_globo" x={500} y={1130} w={560} t={t - 2} de="aba" cam={cam} />
      <T x={1330} y={170} op={tr(t, 0, 8)}>
        <Eti tam={32} color={GRIS}>Ventas fuera de España</Eti>
      </T>
      <Dato x={1330} y={450} t={p(1)} cifra="+90 %" pie="de todo lo que facturaba" tam={330} color="ambar" />
    </AbsoluteFill>
  );
};

/** Y por eso hoy ya no es una empresa espanola. */
export const YaNo: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.06);
  const g = tr(p(1), 0, 14);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Im src="g_piruleta" x={520} y={1190} w={290} t={t - 2} de="aba" cam={cam} gris={0.55 * g} />
      <Parrafo x={860} y={230} w={900} t={t} tam={78} serif>Y esa es también la razón…</Parrafo>
      <Sello x={1300} y={680} t={p(1)} tam={96} rot={-6}>Ya no es española</Sello>
    </AbsoluteFill>
  );
};

/** La decision que parecia una locura: de doscientos productos a uno. */
export const Locura: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const g = tr(p(2), 0, 14);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={110} tam={72}>Una decisión que parecía <Am>una locura</Am></Tit>
      <Im src="g_caramelos" x={560} y={1010} w={860} t={p(1)} de="izq" gris={g} luz={1 - 0.35 * g} />
      <Dato x={560} y={370} t={p(1)} cifra="200" pie="productos" tam={230} color="blanco" op={1 - 0.6 * g} />
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d={`M1030,600 L${lerp(1030, 1260, io(tr(p(2), 0, 16)))},600`} stroke={AM} strokeWidth={12} strokeLinecap="round" opacity={tr(p(2), 0, 4)} />
        {tr(p(2), 0, 16) > 0.95 && <path d="M1260,600 L1222,570 M1260,600 L1222,630" stroke={AM} strokeWidth={12} strokeLinecap="round" />}
      </svg>
      <Im src="g_piruleta" x={1520} y={1160} w={190} t={p(2) - 4} de="pop" />
      <Dato x={1520} y={250} t={p(2) - 6} cifra="1" pie="solo" tam={210} color="ambar" />
    </AbsoluteFill>
  );
};

// =============================================================== 1 · UN SOLO CARAMELO
/** Enric Bernat: «Vivi desde los nueve anos lo que era una industria». */
export const Bernat: React.FC<EP> = (ep) => {
  const {t, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Quien x={110} y={150} t={t} nombre="Enric Bernat" cargo="Hijo y nieto de confiteros · a El País, 1990" />
      <div style={{position: 'absolute', left: 110, top: 420, width: 1000, font: "700 70px/1.18 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«Viví desde los nueve años *lo que era una industria*»." u={c01((t - 8) / 70)} />
      </div>
      <Im src="g_caramelos" x={1500} y={1080} w={760} t={t - 4} de="der" cam={cam} />
    </AbsoluteFill>
  );
};

/** Granja Asturias, en Villamayor: dulces de manzana, a punto de quebrar. */
export const Granja: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 900, 800, 2.5],
    [dur, 870, 790, 2.9],
  ]);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={ESP} />
        <Ciudad x={VILLAMAYOR[0]} y={VILLAMAYOR[1]} t={p(2)} nombre="Villamayor (Asturias)" lado="i" />
      </Mundo>
      <T x={1110} y={130} ancla="i" op={tr(t, 0, 8)}>
        <Eti tam={32} color={GRIS}>Años cincuenta</Eti>
      </T>
      <T x={1106} y={260} ancla="i" s={pop(p(1), 12, 1.4)}>
        <Chip tam={72} fondo="#F4F5F7" tinta="#0B0C10">Granja Asturias</Chip>
      </T>
      <T x={1112} y={380} ancla="i" op={tr(p(1), 8, 8)}>
        <Sans tam={46} peso={600} color="#D5DBE6">Dulces de manzana</Sans>
      </T>
      <Sello x={1430} y={720} t={p(3)} tam={64} rot={-6}>A punto de quebrar</Sello>
    </AbsoluteFill>
  );
};

/** 1958: ya es suya. Deja de fabricar unos 200 caramelos para concentrarse en uno. */
export const UnoSolo: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const g = tr(p(2), 0, 14);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Hoja x={190} y={160} anio="1958" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Tit x={320} y={160} t={t - 4} ancla="i" tam={84}>La empresa ya es suya</Tit>
      <Im src="g_caramelos" x={580} y={1040} w={900} t={p(1)} de="izq" gris={g} luz={1 - 0.4 * g} />
      <T x={580} y={390} s={pop(p(2), 12, 1.4)} rot={-2}>
        <Chip tam={48} color="rojo">Deja de fabricar unos 200 caramelos</Chip>
      </T>
      <Marca tipo="no" x={580} y={800} t={p(2) - 8} s={5} grosor={8} />
      <Im src="g_piruleta" x={1520} y={1170} w={240} t={p(3)} de="pop" />
      <T x={1520} y={300} s={pop(p(3) - 6, 12, 1.5)}>
        <Chip tam={64} color="ambar" tinta="#1B1D22">Uno solo</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Quien comia caramelos: ninos. Y acababan con los dedos pegajosos. */
export const Ninos: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={110} tam={68}>¿Quién comía caramelos en España?</Tit>
      <Tit t={p(1)} y={300} tam={150} color={AM}>Sobre todo, niños</Tit>
      <Im src="g_caramelos" x={470} y={1060} w={720} t={p(2) - 4} de="izq" />
      <Parrafo x={960} y={520} w={860} t={p(2)} tam={58}>Se los sacaban de la boca <Am>con la mano</Am>…</Parrafo>
      <Sello x={1390} y={860} t={p(3)} tam={84} rot={-5}>Dedos pegajosos</Sello>
    </AbsoluteFill>
  );
};

/** La solucion: un palo. «Como comerse un caramelo con tenedor». De madera y luego de plastico. */
export const Palo: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit x={120} y={120} t={t} ancla="i" tam={84}>La solución: <Am>clavarle un palo</Am></Tit>
      <Im src="g_tenedor" x={1420} y={1130} w={136} t={p(1)} de="aba" />
      <Parrafo x={120} y={300} w={1080} t={p(1)} tam={96} serif>«Como comerse un caramelo con tenedor»</Parrafo>
      <T x={126} y={590} ancla="i" op={tr(p(1), 10, 8)}>
        <Eti tam={28} color={GRIS}>Enric Bernat</Eti>
      </T>
      <Im src="g_sin_envolver" x={1700} y={1130} w={150} t={p(2)} de="aba" />
      <T x={120} y={760} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Chip tam={50} color="humo">Primero, de madera</Chip>
      </T>
      <T x={120} y={880} ancla="i" s={pop(p(3), 12, 1.4)}>
        <Chip tam={50} color="ambar" tinta="#1B1D22">Desde los sesenta, de plástico</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Gol, Chups, Chupa Chups: el caramelo acaba dando nombre a la empresa. */
export const Nombre: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  const Tachado: React.FC<{k: number; children: React.ReactNode}> = ({k, children}) => (
    <span style={{position: 'relative', display: 'inline-block', opacity: p(k) >= 4 ? 0.55 : 1}}>
      {children}
      {p(k) >= 4 && <span style={{position: 'absolute', left: -8, top: '56%', height: 10, width: `calc(${Math.round(100 * io(tr(p(k), 4, 10)))}% + 16px)`, background: ROJO, borderRadius: 5}} />}
    </span>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Im src="g_piruleta" x={330} y={1190} w={270} t={t - 2} de="aba" cam={cam} />
      <T x={660} y={170} ancla="i" op={tr(t, 2, 8)}>
        <Eti tam={28} color={GRIS}>Primero lo llamó</Eti>
      </T>
      <T x={656} y={290} ancla="i" s={pop(t - 6, 12, 1.4)}>
        <Tachado k={1}><Serif tam={150} peso={600}>Gol</Serif></Tachado>
      </T>
      <T x={660} y={440} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={28} color={GRIS}>Poco después</Eti>
      </T>
      <T x={656} y={560} ancla="i" s={pop(p(1), 12, 1.4)}>
        <Tachado k={2}><Serif tam={150} peso={600}>Chups</Serif></Tachado>
      </T>
      <T x={660} y={710} ancla="i" op={tr(p(2), 0, 8)}>
        <Eti tam={28} color={GRIS}>Un anuncio lo hizo famoso como</Eti>
      </T>
      <T x={652} y={840} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Serif tam={190} peso={600} color={AM}>Chupa Chups</Serif>
      </T>
      <T x={660} y={990} ancla="i" s={pop(p(3), 12, 1.4)}>
        <Chip tam={34} color="humo">La empresa acabó cambiándose el nombre por el del caramelo</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Una peseta: menos de un centimo de euro, y aun asi caro para la epoca. */
export const Peseta: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Im src="g_piruleta" x={430} y={1190} w={290} t={t - 2} de="aba" cam={cam} />
      <Dato x={1260} y={290} t={t - 4} cifra="1 peseta" pie="cada uno" tam={220} color="blanco" />
      <Dato x={1260} y={640} t={p(1)} cifra="< 0,01 €" pie="menos de un céntimo de euro" tam={170} color="ambar" />
      <Sello x={1280} y={930} t={p(2)} tam={44} rot={-4}>Caro para un caramelo de entonces</Sello>
    </AbsoluteFill>
  );
};

/** Funciono: 200.000 al dia y una flota de Seat 600 repartiendolos por Espana. */
export const Flota: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const xa = lerp(-360, 1500, tr(p(2), 0, 260));
  const xb = lerp(2400, 1180, sal(tr(p(2), 6, 70)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.32} />
      <Sello x={400} y={160} t={t - 2} tam={84} rot={-5} color="#2BE38A">Funcionó</Sello>
      <T x={520} y={330} op={tr(p(1), 0, 8)}>
        <Eti tam={30} color={GRIS}>Finales de los cincuenta</Eti>
      </T>
      <Dato x={520} y={480} t={p(1)} cifra="200.000" pie="unidades al día" tam={200} color="ambar" />
      <Im src="g_coche" x={xa} y={800} w={330} t={p(2)} de="nada" flip z={0.6} blur={1.5} luz={0.7} />
      <Im src="g_coche" x={xb} y={1070} w={760} t={p(2) - 6} de="nada" z={1.2} />
      <T x={1400} y={300} s={pop(p(3), 12, 1.4)} rot={-2}>
        <Chip tam={42} fondo="#F4F5F7" tinta="#0B0C10">Seat 600 con la marca, por toda España</Chip>
      </T>
      <T x={1400} y={386} op={tr(p(2), 10, 8)}>
        <Eti tam={24} color={GRIS}>Años sesenta · coche de la imagen, genérico</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** Un solo producto solo crece encontrando mas bocas. */
export const Bocas: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.06);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={110} tam={66}>Vivir de un solo producto tiene un problema</Tit>
      <Im src="g_piruleta" x={880} y={1210} w={250} t={t - 2} de="aba" cam={cam} />
      <Parrafo x={130} y={440} w={600} t={p(1)} tam={66} serif>Solo puede crecer de una manera…</Parrafo>
      <Tit x={1470} y={470} t={p(2)} tam={150} color={AM}>Más bocas</Tit>
      <T x={1470} y={620} op={tr(p(2), 8, 8)}>
        <Sans tam={44} peso={600} color="#D5DBE6">que encontrar</Sans>
      </T>
    </AbsoluteFill>
  );
};

/** Y las de Espana se acababan pronto: poco mas de 30 millones de habitantes. */
export const Techo: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 900, 820, 2.3],
    [dur, 880, 850, 2.6],
  ]);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={ESP} />
      </Mundo>
      <Parrafo x={1090} y={110} w={760} t={t} tam={72} serif>Las de España se acababan pronto</Parrafo>
      <T x={1100} y={420} ancla="i" s={pop(p(1), 12, 1.4)}>
        <Chip tam={44} color="humo">Un caramelo para niños</Chip>
      </T>
      <Dato x={1100} y={610} t={p(1) - 10} cifra="≈ 30 millones" pie="de habitantes (poco más)" tam={100} color="blanco" ancla="i" />
      <Sello x={1440} y={900} t={p(2)} tam={90} rot={-5}>Tiene techo</Sello>
    </AbsoluteFill>
  );
};

// =============================================================== 2 · NADA QUE TRADUCIR
/** 1967: segunda fabrica cerca de Barcelona y primera filial fuera, en Perpinan. 1969: fabrica en Bayona. */
export const Salida: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 820, 830, 3.0],
    [dur, 810, 800, 3.5],
  ]);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#5A1A1E', borde: ROJO} : c === 'FRA' && p(1) >= 0 ? {fill: '#5A450F', borde: AM} : undefined)} />
        <Ciudad x={SANT_ESTEVE[0]} y={SANT_ESTEVE[1]} t={t - 10} nombre="Segunda fábrica" lado="i" tam={10} color="#FF6A5C" />
        <Ciudad x={PERPINAN[0]} y={PERPINAN[1]} t={p(1)} nombre="Perpiñán · filial" tam={10} />
        <Ciudad x={BAYONA[0]} y={BAYONA[1]} t={p(2)} nombre="Bayona · fábrica" lado="i" tam={10} />
      </Mundo>
      <Hoja x={190} y={160} anio="1967" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Tit x={320} y={160} t={t - 4} ancla="i" tam={76}>Empieza a salir</Tit>
      <Hoja x={190} y={900} anio="1969" s={1.05 * pop(p(2), 12, 1.4)} color="ambar" />
      <T x={320} y={900} ancla="i" op={tr(p(2), 4, 8)}>
        <Serif tam={64} peso={600}>Ya fabrica en Francia</Serif>
      </T>
    </AbsoluteFill>
  );
};

/** No monto tiendas: se apoyo en quien ya llegaba a los mostradores. */
export const Socios: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit x={120} y={120} t={t} ancla="i" tam={84}>No montó tiendas</Tit>
      <Im src="g_expositor" x={400} y={1050} w={460} t={t - 4} de="aba" cam={cam} />
      <Parrafo x={800} y={250} w={1000} t={p(1)} tam={58}>En cada país se apoyó en quien <Am>ya llegaba a los mostradores</Am></Parrafo>
      <T x={800} y={600} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Chip tam={48} fondo="#F4F5F7" tinta="#0B0C10">Italia</Chip>
      </T>
      <T x={1010} y={602} ancla="i" op={tr(p(2), 6, 8)}>
        <Sans tam={42} peso={600} color="#D5DBE6">lo repartía otro fabricante de golosinas</Sans>
      </T>
      <T x={800} y={760} ancla="i" s={pop(p(3), 12, 1.4)}>
        <Chip tam={48} fondo="#F4F5F7" tinta="#0B0C10">Estados Unidos</Chip>
      </T>
      <T x={1250} y={762} ancla="i" op={tr(p(3), 6, 8)}>
        <Sans tam={42} peso={600} color="#D5DBE6">un gran mayorista</Sans>
      </T>
    </AbsoluteFill>
  );
};

/** En Alemania, un acuerdo con una empresa holandesa: Van Melle. Quedate con ese nombre. */
export const VanMelle: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 930, 520, 2.5],
    [dur, 950, 505, 2.8],
  ]);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'DEU' ? {fill: '#3A4052', borde: '#8D93A1'} : c === 'NLD' ? {fill: '#7A4A08', borde: AM} : undefined)} />
      </Mundo>
      <T x={110} y={120} ancla="i" op={tr(t, 0, 8)}>
        <Eti tam={32} color={GRIS}>En Alemania</Eti>
      </T>
      <Parrafo x={110} y={170} w={640} t={t - 4} tam={64} serif>Un acuerdo con una empresa holandesa de caramelos</Parrafo>
      <T x={110} y={640} ancla="i" s={pop(p(1), 12, 1.5)}>
        <Chip tam={96} fondo="#F4F5F7" tinta="#0B0C10">Van Melle</Chip>
      </T>
      <Sello x={520} y={860} t={p(2)} tam={54} rot={-5} color={AM}>Quédate con ese nombre</Sello>
    </AbsoluteFill>
  );
};

/** Lo que tiene cualquier caramelo duro: aguanta meses sin nevera y cabe en cualquier mostrador. */
export const Duro: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={110} tam={66}>Y tenía a favor lo de cualquier caramelo duro</Tit>
      <Im src="g_piruletas" x={560} y={1050} w={900} t={t - 4} de="izq" cam={cam} />
      <T x={1430} y={400} s={pop(p(1), 12, 1.5)} rot={-3}>
        <Chip tam={56} color="ambar" tinta="#1B1D22">Aguanta meses sin nevera</Chip>
      </T>
      <T x={1430} y={640} s={pop(p(2), 12, 1.5)} rot={3}>
        <Chip tam={52} fondo="#F4F5F7" tinta="#0B0C10">Cabe en cualquier mostrador</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Le faltaba una imagen que se entendiera en cualquier idioma. */
export const Imagen: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.06);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Im src="g_piruleta" x={260} y={1200} w={250} t={t - 2} de="aba" cam={cam} />
      <Tit x={1100} y={220} t={t} tam={104}>Le faltaba una cosa</Tit>
      <Parrafo x={560} y={420} w={1080} t={p(1)} tam={84} centro serif>Una imagen que se entendiera en <Am>cualquier idioma</Am></Parrafo>
    </AbsoluteFill>
  );
};

/** 1969: se la pide a un amigo, Salvador Dali, que dibuja una margarita en menos de una hora. */
export const Dali: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.62} blur={3} arriba={0.7} abajo={0.75} />
      <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(8,9,12,0.82) 0%, rgba(8,9,12,0.5) 42%, rgba(8,9,12,0) 62%)'}} />
      <Hoja x={190} y={160} anio="1969" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={160} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={32} color={GRIS}>Se la pide a un amigo</Eti>
      </T>
      <Tit x={120} y={350} t={p(1)} ancla="i" tam={124}>Salvador Dalí</Tit>
      <Flor x={420} y={640} r={160} u={tr(p(2), 0, 34)} relleno={tr(p(2), 26, 14)} trazo="#F4F5F7" grosor={7} />
      <T x={480} y={880} s={pop(p(3), 12, 1.4)}>
        <Chip tam={44} color="humo">Dicen que tardó menos de una hora</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** El consejo: el dibujo arriba del todo, no en un lado, para que se vea entero. */
export const Arriba: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit t={t} y={100} tam={66}>Un consejo que valía más que el dibujo</Tit>
      <T x={960} y={196} s={pop(t - 10, 11, 1.4)}>
        <Chip tam={34} color="humo">Según se cuenta</Chip>
      </T>
      <Bola x={1360} y={460} r={170} t={p(1)}>
        <Flor x={170} y={170} r={108} u={tr(p(1), 6, 20)} relleno={tr(p(1), 20, 10)} />
      </Bola>
      <T x={1360} y={850} op={tr(p(1), 6, 8)}>
        <Sans tam={50} peso={800}>Arriba del todo</Sans>
      </T>
      <Marca tipo="si" x={1590} y={320} t={p(3)} s={2.4} grosor={9} />
      <T x={1360} y={940} s={pop(p(3), 12, 1.4)}>
        <Chip tam={40} color="ambar" tinta="#1B1D22">Se ve entero desde cualquier ángulo</Chip>
      </T>
      <Bola x={560} y={460} r={170} t={p(2)}>
        <Flor x={315} y={170} r={108} u={1} relleno={1} />
      </Bola>
      <T x={560} y={850} op={tr(p(2), 6, 8)}>
        <Sans tam={50} peso={800} color="#8D93A1">En un lado</Sans>
      </T>
      <Marca tipo="no" x={560} y={460} t={p(2) - 12} s={4.6} grosor={8} />
    </AbsoluteFill>
  );
};

/** Un caramelo redondo, un palo y una flor: no habia nada que traducir. */
export const Traducir: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const et = (x: number, txt: string, tt: number) => (
    <T x={x} y={690} op={tr(tt, 4, 8)}>
      <Sans tam={50} peso={700}>{txt}</Sans>
    </T>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      {t >= 0 && <div style={{position: 'absolute', left: 480 - 120, top: 420 - 120, width: 240, height: 240, borderRadius: 120, background: 'radial-gradient(circle at 34% 30%, #FF8A7E 0%, #E0352B 46%, #9A1118 100%)', transform: `scale(${pop(t, 12, 1.4)})`, boxShadow: '0 30px 60px rgba(0,0,0,0.5)'}} />}
      {et(480, 'Un caramelo redondo', t)}
      {t >= 22 && <div style={{position: 'absolute', left: 960 - 14, top: 260, width: 28, height: 330 * io(tr(t, 22, 16)), borderRadius: 14, background: 'linear-gradient(90deg,#fff,#C9CED8)', boxShadow: '0 20px 40px rgba(0,0,0,0.5)'}} />}
      {et(960, 'un palo', t - 22)}
      <Flor x={1440} y={420} r={130} u={tr(t, 40, 22)} relleno={tr(t, 56, 12)} trazo="#F4F5F7" grosor={6} />
      {et(1440, 'y una flor', t - 40)}
      <Tit t={p(1)} y={900} tam={116} color={AM}>No había nada que traducir</Tit>
    </AbsoluteFill>
  );
};

export const CHUPA1 = {caramelo: Caramelo, tres: Tres, vuelta: Vuelta, noventa: Noventa, ya_no: YaNo, locura: Locura, bernat: Bernat, granja: Granja, uno_solo: UnoSolo, ninos: Ninos, palo: Palo, nombre: Nombre, peseta: Peseta, flota: Flota, bocas: Bocas, techo: Techo, salida: Salida, socios: Socios, van_melle: VanMelle, duro: Duro, imagen: Imagen, dali: Dali, arriba: Arriba, traducir: Traducir};
