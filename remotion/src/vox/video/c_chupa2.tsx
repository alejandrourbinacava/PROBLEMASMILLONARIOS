import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {Chip, Eti, Hoja, Marca, Palabras, Sans, Sello, Serif, T, c01, io, lerp, pop, sal, tr} from './kit';
import {Detras} from './m_capas';
import {Im, deriva} from './m_vox';
import {AM, Am, Dato, Fondo, Parrafo, Quien, Tit} from './p_comun';
import {Columna, GRIS, Linea, Reparto, ROJO} from './c_comun';

/** «Por que Chupa Chups vende MAS fuera de Espana que dentro» · capitulos 3 y 4. */

// =============================================================== 3 · NUEVE DE CADA DIEZ
/** 1970: uno de cada diez fuera. Japon, Estados Unidos, Alemania, Reino Unido. 1980: nueve de cada diez. */
export const Paises: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  const fila = (k: number, y: number, anio: string, txt: string) => (
    <>
      <T x={160} y={y} ancla="i" s={pop(p(k), 12, 1.4)}>
        <Chip tam={44} fondo="#F4F5F7" tinta="#0B0C10">{anio}</Chip>
      </T>
      <T x={anio.length > 5 ? 520 : 330} y={y + 2} ancla="i" op={tr(p(k), 4, 8)}>
        <Sans tam={50} peso={700}>{txt}</Sans>
      </T>
    </>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Im src="g_globo" x={1560} y={1100} w={470} t={t - 2} de="der" cam={cam} />
      <Reparto x={160} y={150} w={1040} t={t} fuera={0.1} etiqueta="1970 · uno de cada diez, fuera" />
      {fila(1, 380, '1977', 'Japón')}
      {fila(2, 490, '1980', 'Estados Unidos')}
      {fila(3, 600, 'Después', 'Alemania y el Reino Unido')}
      <Reparto x={160} y={790} w={1040} t={p(4)} fuera={0.9} etiqueta="La proporción se da la vuelta" />
      <T x={680} y={950} s={pop(p(5), 12, 1.5)}>
        <Chip tam={52} color="ambar" tinta="#1B1D22">9 de cada 10 ventas, de fuera</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Rusia (San Petersburgo, 1991), China, Mexico y una filial en Brasil. */
export const Fabricas: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit x={120} y={120} t={t} ancla="i" tam={80}>Y después, <Am>a fabricar fuera</Am></Tit>
      <T x={120} y={260} ancla="i" s={pop(t - 8, 12, 1.4)}>
        <Chip tam={44} color="humo">Finales de los ochenta: entra en Rusia</Chip>
      </T>
      <Im src="g_fabrica" x={1000} y={830} w={420} t={p(2)} de="aba" z={0.6} luz={0.6} blur={1.5} cam={cam} />
      <T x={1000} y={570} s={pop(p(2) - 4, 12, 1.4)}>
        <Chip tam={44} fondo="#F4F5F7" tinta="#0B0C10">China</Chip>
      </T>
      <Im src="g_fabrica" x={420} y={1040} w={700} t={p(1)} de="izq" cam={cam} />
      <T x={420} y={620} s={pop(p(1) - 4, 12, 1.4)}>
        <Chip tam={48} color="ambar" tinta="#1B1D22">San Petersburgo · 1991</Chip>
      </T>
      <Im src="g_fabrica" x={1520} y={1060} w={600} t={p(3)} de="der" flip z={1.1} cam={cam} />
      <T x={1520} y={690} s={pop(p(3) - 4, 12, 1.4)}>
        <Chip tam={46} fondo="#F4F5F7" tinta="#0B0C10">México</Chip>
      </T>
      <T x={1500} y={300} s={pop(p(4), 12, 1.4)} rot={-3}>
        <Chip tam={46} color="humo">Y una filial en Brasil</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 1990: 164 paises y 20.000 millones de unidades fabricadas. */
export const VeinteMil: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Hoja x={190} y={160} anio="1990" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Dato x={500} y={500} t={t - 4} cifra="164" pie="países donde se podía comprar" tam={330} color="blanco" />
      <Dato x={1380} y={330} t={p(1)} cifra="20.000 millones" pie="de unidades fabricadas hasta entonces" tam={120} color="ambar" />
      <Im src="g_piruletas" x={1380} y={1090} w={760} t={p(1) - 4} de="der" cam={cam} />
    </AbsoluteFill>
  );
};

/** La marca aparece donde mira todo el mundo: 1988, sin azucar y el concierto de Michael Jackson. */
export const Jackson: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit x={120} y={120} t={t} ancla="i" tam={66}>Y la marca aparece donde <Am>mira todo el mundo</Am></Tit>
      <Hoja x={190} y={340} anio="1988" s={1.05 * pop(p(1), 12, 1.4)} color="rojo" />
      <T x={320} y={340} ancla="i" s={pop(p(1) - 6, 12, 1.4)}>
        <Chip tam={46} color="humo">Saca su versión sin azúcar</Chip>
      </T>
      <Parrafo x={160} y={500} w={1200} t={p(2)} tam={84} serif>Patrocina el concierto de <Am>Michael Jackson</Am> en Barcelona</Parrafo>
      <Im src="g_piruleta" x={1620} y={1200} w={270} t={t - 4} de="aba" cam={cam} />
    </AbsoluteFill>
  );
};

/** 1991: Cruyff deja de fumar; en la banda, donde tenia un cigarrillo, un Chupa Chups. */
export const Cruyff: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const g = tr(p(3), 0, 12);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.34} blur={9} />
      <Hoja x={190} y={160} anio="1991" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Tit x={320} y={130} t={t - 4} ancla="i" tam={96}>Johan Cruyff</Tit>
      <T x={326} y={216} ancla="i" op={tr(t, 8, 8)}>
        <Eti tam={28} color={GRIS}>Entrenador del Barcelona</Eti>
      </T>
      <Im src="g_cigarrillo" x={520} y={1000} w={620} t={p(1)} de="izq" gris={g} luz={1 - 0.4 * g} />
      <T x={520} y={440} s={pop(p(1) - 4, 12, 1.4)} rot={-2}>
        <Chip tam={50} color="rojo">Tiene que dejar de fumar</Chip>
      </T>
      <T x={520} y={530} op={tr(p(1), 6, 8)}>
        <Eti tam={26} color={GRIS}>Un problema grave de corazón</Eti>
      </T>
      <Marca tipo="no" x={520} y={800} t={p(2)} s={4.6} grosor={8} />
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d={`M900,800 L${lerp(900, 1180, io(tr(p(3), 0, 16)))},800`} stroke={AM} strokeWidth={12} strokeLinecap="round" opacity={tr(p(3), 0, 4)} />
        {tr(p(3), 0, 16) > 0.95 && <path d="M1180,800 L1142,770 M1180,800 L1142,830" stroke={AM} strokeWidth={12} strokeLinecap="round" />}
      </svg>
      <Im src="g_piruleta" x={1480} y={1200} w={260} t={p(3)} de="pop" />
      <T x={1480} y={300} s={pop(p(3) - 6, 12, 1.5)}>
        <Chip tam={44} color="ambar" tinta="#1B1D22">En la banda, un Chupa Chups</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** El anuncio contra el tabaco: «El futbol me lo ha dado todo en la vida. Fumar casi me la quita». */
export const Anuncio: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Quien x={110} y={150} t={t} nombre="Johan Cruyff" cargo="Anuncio contra el tabaco · 1991" />
      <div style={{position: 'absolute', left: 110, top: 400, width: 1120, font: "700 72px/1.18 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«El fútbol me lo ha dado todo en la vida. *Fumar casi me la quita*»." u={p(1) < 0 ? 0 : c01(p(1) / 66)} />
      </div>
      <Im src="g_balon" x={1570} y={1080} w={440} t={t - 4} de="der" cam={cam} />
    </AbsoluteFill>
  );
};

/** 1995: unos Chupa Chups de San Petersburgo viajan a la estacion Mir. */
export const Mir: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.7} blur={2.5} arriba={0.6} abajo={0.6} />
      <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(8,9,12,0.86) 0%, rgba(8,9,12,0.55) 40%, rgba(8,9,12,0) 62%)'}} />
      <Hoja x={190} y={160} anio="1995" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={160} ancla="i" s={pop(t - 6, 12, 1.4)}>
        <Chip tam={40} color="humo">Fabricados en San Petersburgo</Chip>
      </T>
      <Parrafo x={120} y={320} w={820} t={p(1)} tam={104} serif>Viajan a la estación <Am>Mir</Am></Parrafo>
      <T x={120} y={720} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Chip tam={42} fondo="#F4F5F7" tinta="#0B0C10">Los cosmonautas salen con ellos en televisión</Chip>
      </T>
      <Im src="g_piruleta" x={1500 + Math.sin(t / 40) * 14} y={1150 + Math.cos(t / 34) * 10} w={150} t={p(1) - 4} de="pop" rot={-16 + t * 0.05} />
    </AbsoluteFill>
  );
};

/** Finales de los noventa: 40.000 millones de unidades, unos 440 M EUR, 2.000 empleados, 93 % fuera. */
export const Cumbre: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <T x={960} y={90} op={tr(t, 0, 8)}>
        <Eti tam={32} color={GRIS}>Finales de los noventa</Eti>
      </T>
      <div style={{position: 'absolute', left: 959, top: 170, width: 2, height: 800, background: 'rgba(255,255,255,0.1)'}} />
      <div style={{position: 'absolute', left: 160, top: 560, width: 1600, height: 2, background: 'rgba(255,255,255,0.1)'}} />
      <Dato x={480} y={300} t={t - 4} cifra="40.000 millones" pie="de unidades fabricadas" tam={104} color="ambar" />
      <Dato x={1440} y={300} t={p(1)} cifra="≈ 440 M€" pie="de ventas al año" tam={150} color="blanco" />
      <Dato x={480} y={740} t={p(2)} cifra="2.000" pie="empleados" tam={190} color="blanco" />
      <Dato x={1440} y={740} t={p(3)} cifra="93 %" pie="vendido fuera de España" tam={220} color="ambar" />
    </AbsoluteFill>
  );
};

/** Habia llegado, literalmente, hasta el espacio. */
export const Espacio: React.FC<EP> = (ep) => {
  const {t} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.5} blur={5} arriba={0.7} abajo={0.7} />
      <AbsoluteFill style={{background: 'rgba(8,9,12,0.35)'}} />
      <Tit x={960} y={400} t={t} tam={100}>Había llegado, literalmente,</Tit>
      <Tit x={960} y={580} t={t - 14} tam={190} color={AM}>hasta el espacio</Tit>
    </AbsoluteFill>
  );
};

// =============================================================== 4 · EL PROBLEMA
/** Fabricas en Espana, Francia, Rusia, Mexico y China: cada mercado, su filial. */
export const Fabricas5: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  const P: [string, number, number, number][] = [['España', 800, 420, -4], ['Francia', 1190, 250, 3], ['Rusia', 1590, 400, -3], ['México', 790, 720, 4], ['China', 1610, 700, -2]];
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit x={120} y={110} t={t} ancla="i" tam={66}>Para estar en todas partes…</Tit>
      <Im src="g_fabrica" x={330} y={1040} w={560} t={t - 4} de="izq" cam={cam} />
      <Im src="g_globo" x={1200} y={1090} w={500} t={t - 2} de="aba" cam={cam} />
      {P.map(([n, x, y, rot], i) => (
        <T key={n} x={x} y={y} s={pop(p(i + 1), 12, 1.6)} rot={rot}>
          <Chip tam={50} color={i === 0 ? 'rojo' : 'ambar'} tinta={i === 0 ? '#fff' : '#1B1D22'}>{n}</Chip>
        </T>
      ))}
      <T x={120} y={220} ancla="i" s={pop(p(6), 12, 1.4)}>
        <Chip tam={34} color="humo">Cada mercado nuevo, su filial; varios, su fábrica</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Para no depender de un caramelo: Smint (funciono), juguetes, relojes de chicle... y veinte empresas mas. */
export const CasiTodo: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const chip = (k: number, y: number, txt: string) => (
    <T x={130} y={y} ancla="i" s={pop(p(k), 12, 1.4)}>
      <Chip tam={36} color="humo">{txt}</Chip>
    </T>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit x={120} y={100} t={t} ancla="i" tam={62}>Y para no depender de un solo caramelo, <Am>se metió en casi todo</Am></Tit>
      <T x={130} y={250} ancla="i" s={pop(p(1), 12, 1.4)}>
        <Chip tam={50} fondo="#F4F5F7" tinta="#0B0C10">Smint</Chip>
      </T>
      <T x={400} y={252} ancla="i" op={tr(p(1), 4, 8)}>
        <Sans tam={40} peso={600} color="#D5DBE6">pastillas de menta para adultos</Sans>
      </T>
      <Marca tipo="si" x={1060} y={250} t={p(1) - 26} s={1.5} grosor={9} />
      {chip(2, 400, 'Huevos de chocolate con juguete')}
      {chip(3, 480, 'Un reloj que daba chicles')}
      {chip(4, 560, 'Una piruleta con forma de teléfono móvil')}
      <Im src="g_juguetes" x={500} y={1010} w={700} t={p(2) - 2} de="izq" />
      <Dato x={1440} y={420} t={p(5)} cifra="+20" pie="empresas más con la marca" tam={230} color="blanco" />
      <Im src="g_accesorios" x={1430} y={1010} w={840} t={p(5) - 2} de="der" />
      <T x={1440} y={690} op={tr(p(6), 0, 8)}>
        <Eti tam={26} color={GRIS}>Ropa · relojes · calzado · gafas · papelería</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** 414 M EUR en 2001, 344 en 2002, 261 en 2004: mas de un tercio menos en tres anos. */
export const Caida: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const K = 1.25;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <T x={160} y={110} ancla="i" op={tr(t, 0, 8)}>
        <Eti tam={32} color={GRIS}>Facturación de Chupa Chups</Eti>
      </T>
      <div style={{position: 'absolute', left: 160, top: 900, width: 1080, height: 4, background: 'rgba(255,255,255,0.22)'}} />
      <Columna x={330} base={900} alto={414 * K} t={t - 4} cifra="414 M€" pie="2001" color="linear-gradient(180deg,#F4F5F7,#AEB5C2)" />
      <Columna x={700} base={900} alto={344 * K} t={p(1)} cifra="344 M€" pie="2002" color="linear-gradient(180deg,#FFD95A,#F29A0B)" />
      <Columna x={1070} base={900} alto={261 * K} t={p(2)} cifra="261 M€" pie="2004" color="linear-gradient(180deg,#FF6A5C,#C4161C)" />
      <Dato x={1550} y={450} t={p(3)} cifra="−37 %" pie="en tres años" tam={190} color="rojo" />
    </AbsoluteFill>
  );
};

/** Una empresa montada para 160 paises no encoge facil: la fabrica de Barcelona, a media capacidad. */
export const Encoge: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  const u = io(tr(p(2), 0, 24));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Parrafo x={120} y={100} w={1500} t={t} tam={66} serif>Una empresa montada para vender en 160 países <Am>no encoge con facilidad</Am></Parrafo>
      <Im src="g_fabrica" x={500} y={1080} w={800} t={t - 6} de="izq" gris={0.55} luz={0.8} cam={cam} />
      <T x={1040} y={520} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={23} color={GRIS}>Fábrica de Barcelona · capacidad utilizada</Eti>
      </T>
      {p(1) >= 0 && (
        <div style={{position: 'absolute', left: 1040, top: 560, width: 760, height: 76, borderRadius: 38, background: 'linear-gradient(180deg,#3A4052,#252936)', overflow: 'hidden'}}>
          <div style={{width: 380 * u, height: 76, background: 'linear-gradient(180deg,#FF6A5C,#C4161C)'}} />
        </div>
      )}
      <Dato x={1420} y={800} t={p(2)} cifra="50 %" pie="llegó a trabajar a la mitad" tam={210} color="rojo" />
    </AbsoluteFill>
  );
};

/** 2002: mas de 22 M EUR de perdidas y unos 120 de deuda. Tres ejercicios seguidos en rojo. */
export const Perdidas: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Hoja x={190} y={150} anio="2002" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Im src="g_fajos" x={500} y={1100} w={540} t={t - 2} de="izq" gris={0.9} luz={0.6} cam={cam} />
      <Dato x={520} y={430} t={t - 4} cifra="−22 M€" pie="de pérdidas (más de)" tam={240} color="rojo" />
      <Dato x={1400} y={430} t={p(2)} cifra="≈ 120 M€" pie="de deuda, según la prensa económica" tam={170} color="blanco" />
      <T x={1400} y={760} s={pop(p(3), 12, 1.4)}>
        <Chip tam={44} color="humo">Tres ejercicios seguidos en pérdidas</Chip>
      </T>
      <T x={1400} y={846} op={tr(p(3), 6, 8)}>
        <Eti tam={24} color={GRIS}>Lo recoge la Comisión Europea · 2002, 2003 y 2004</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** Llega un directivo de fuera: cierra los juguetes, vende media Shanghai, suelta Bayona, despidos en Asturias. */
export const Recortes: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Hoja x={190} y={150} anio="2002" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Tit x={320} y={120} t={t - 4} ancla="i" tam={72}>La familia pone al frente a alguien de fuera</Tit>
      <T x={326} y={200} ancla="i" op={tr(t, 8, 8)}>
        <Eti tam={26} color={GRIS}>Un directivo llegado de una gran empresa de alimentación</Eti>
      </T>
      <Im src="g_persiana" x={1570} y={1110} w={520} t={p(1) - 2} de="arr" cam={cam} />
      <Linea x={170} y={400} t={p(1)}>Cierra el negocio de los juguetes</Linea>
      <Linea x={170} y={530} t={p(2)}>Vende la mitad de la fábrica de Shanghái</Linea>
      <Linea x={170} y={660} t={p(3)}>Se deshace de la de Bayona</Linea>
      <Linea x={170} y={790} t={p(4)}>Despidos en Asturias</Linea>
    </AbsoluteFill>
  );
};

/** La familia pone 8 M EUR y cede a la empresa la propiedad de la marca. */
export const Familia: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Im src="g_fajo" x={480} y={1070} w={640} t={t - 2} de="izq" cam={cam} />
      <Dato x={480} y={300} t={t - 4} cifra="8 M€" pie="pone la familia de su bolsillo" tam={230} color="ambar" />
      <Parrafo x={1010} y={360} w={800} t={p(1)} tam={66} serif>…y cede a la empresa la propiedad de <Am>la marca</Am>, que hasta entonces era suya</Parrafo>
    </AbsoluteFill>
  );
};

/** Septiembre de 2003: para un credito de 35 M EUR, hipoteca lo mas valioso que tenia. */
export const Hipoteca: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Hoja x={190} y={150} anio="2003" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={150} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={32} color={GRIS}>Septiembre</Eti>
      </T>
      <Dato x={520} y={520} t={p(1)} cifra="35 M€" pie="de crédito" tam={280} color="ambar" />
      <Parrafo x={1010} y={200} w={820} t={p(2)} tam={80} serif>Hipoteca <Am>lo más valioso</Am> que tenía</Parrafo>
      <Im src="g_escritura" x={1410} y={1040} w={800} t={p(2) - 2} de="der" cam={cam} />
    </AbsoluteFill>
  );
};

/** No era una fabrica: la Casa Batllo, de Gaudi, en el paseo de Gracia. Valorada en 71 M EUR. */
export const Batllo: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.07);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.36} blur={10} />
      <T x={120} y={90} ancla="i" op={tr(t, 0, 8) * (1 - tr(p(1), 0, 8))}>
        <Serif tam={76} peso={600} color="#C9CED8">No era una fábrica</Serif>
      </T>
      <Detras x={560} y={180} t={p(1)} tam={170}>Casa Batlló</Detras>
      <Im src="g_batllo" x={560} y={1070} w={460} t={p(1) - 3} de="aba" cam={cam} />
      <T x={1190} y={470} ancla="i" s={pop(p(1) - 12, 12, 1.4)}>
        <Chip tam={50} fondo="#F4F5F7" tinta="#0B0C10">Un edificio de Gaudí</Chip>
      </T>
      <T x={1196} y={560} ancla="i" op={tr(p(1), 16, 8)}>
        <Sans tam={40} peso={600} color="#D5DBE6">Paseo de Gracia, Barcelona</Sans>
      </T>
      <T x={1196} y={650} ancla="i" op={tr(p(2), 0, 8)}>
        <Sans tam={35} peso={700} color={AM}>De los Bernat desde los años noventa</Sans>
      </T>
      <Dato x={1190} y={850} t={p(3)} cifra="71 M€" pie="valor de tasación" tam={190} color="ambar" ancla="i" />
    </AbsoluteFill>
  );
};

/** Diciembre de 2003: muere Enric Bernat. */
export const Muere: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Hoja x={190} y={150} anio="2003" s={1.05 * pop(t, 12, 1.4)} color="humo" />
      <T x={320} y={150} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={32} color={GRIS}>Diciembre · tres meses después</Eti>
      </T>
      <Tit x={160} y={470} t={p(1)} ancla="i" tam={130}>Muere Enric Bernat</Tit>
      <T x={166} y={600} ancla="i" op={tr(p(1), 8, 8)}>
        <Eti tam={34} color={GRIS}>1923 – 2003</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** Principios de 2004: la casa, hipotecada otra vez por 15 M EUR para pagar a Hacienda a plazos. */
export const Hacienda: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Hoja x={190} y={150} anio="2004" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Im src="g_batllo" x={420} y={1070} w={430} t={t - 2} de="aba" cam={cam} />
      <Im src="g_escritura" x={790} y={1050} w={440} t={t - 10} de="pop" z={1.2} cam={cam} />
      <Parrafo x={940} y={140} w={920} t={t - 4} tam={72} serif>La casa, hipotecada <Am>otra vez</Am></Parrafo>
      <Dato x={1400} y={560} t={p(1)} cifra="+15 M€" pie="segunda hipoteca" tam={220} color="ambar" />
      <T x={1400} y={860} s={pop(p(2), 12, 1.4)}>
        <Chip tam={44} color="humo">Para pagar a Hacienda a plazos</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Aquel credito acaba en Bruselas: en 2007, no fue ayuda de Estado. Pero ya habia otro dueno. */
export const Bruselas: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit x={120} y={120} t={t} ancla="i" tam={80}>Aquel crédito acaba en <Am>Bruselas</Am></Tit>
      <T x={120} y={270} ancla="i" s={pop(t - 10, 12, 1.4)}>
        <Chip tam={44} color="humo">Alguien lo denuncia ante la Comisión Europea</Chip>
      </T>
      <Hoja x={190} y={500} anio="2007" s={1.05 * pop(p(1), 12, 1.4)} color="ambar" />
      <Sello x={960} y={500} t={p(1) - 6} tam={72} rot={-4} color="#2BE38A">No fue ayuda de Estado</Sello>
      <Parrafo x={160} y={700} w={1560} t={p(2)} tam={88} serif>Pero para entonces Chupa Chups ya tenía <Am>otro dueño</Am></Parrafo>
    </AbsoluteFill>
  );
};

export const CHUPA2 = {paises: Paises, fabricas: Fabricas, veinte_mil: VeinteMil, jackson: Jackson, cruyff: Cruyff, anuncio: Anuncio, mir: Mir, cumbre: Cumbre, espacio: Espacio, fabricas5: Fabricas5, casi_todo: CasiTodo, caida: Caida, encoge: Encoge, perdidas: Perdidas, recortes: Recortes, familia: Familia, hipoteca: Hipoteca, batllo: Batllo, muere: Muere, hacienda: Hacienda, bruselas: Bruselas};
export {ROJO, sal};
