import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {Chip, Escenario, Eti, Hoja, Mapa, Marca, Mundo, Palabras, Sans, Sello, Serif, T, c01, camara, io, lerp, pop, tr} from './kit';
import {Detras} from './m_capas';
import {MK, MX, MY} from './m_gancho';
import {Im, deriva} from './m_vox';
import {AM, Am, Dato, Fondo, Parrafo, Quien, Tit} from './p_comun';
import {Ciudad, Columna, Flor, GRIS, ROJO} from './c_comun';
import {SANT_ESTEVE} from './c_chupa1';

/** «Por que Chupa Chups vende MAS fuera de Espana que dentro» · capitulo 5 y cierre. */
const Ok: React.FC<{x: number; y: number; t: number; children: React.ReactNode}> = ({x, y, t, children}) =>
  t < 0 ? null : (
    <>
      <T x={x} y={y} s={pop(t, 11, 1.6)}>
        <span style={{font: "56px 'M Black'", color: '#2BE38A'}}>✓</span>
      </T>
      <T x={x + 54} y={y} ancla="i" op={tr(t, 3, 8)}>
        <Sans tam={46} peso={700}>{children}</Sans>
      </T>
    </>
  );

// =============================================================== 5 · SE VENDE
/** 3 de julio de 2006: la familia vende la empresa entera a Perfetti Van Melle. */
export const Venta: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const u = io(tr(p(5), 0, 24));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Hoja x={190} y={150} anio="2006" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={100} ancla="i" op={tr(t, 2, 8)}>
        <Eti tam={28} color={GRIS}>3 de julio</Eti>
      </T>
      <Tit x={316} y={170} t={t - 4} ancla="i" tam={76}>La familia vende <Am>la empresa entera</Am></Tit>
      <T x={166} y={330} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={28} color={GRIS}>El comprador</Eti>
      </T>
      <T x={160} y={440} ancla="i" s={pop(p(1), 12, 1.4)}>
        <Chip tam={84} fondo="#F4F5F7" tinta="#0B0C10">Perfetti Van Melle</Chip>
      </T>
      <T x={160} y={590} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Chip tam={44} color="humo">Un grupo italiano y holandés</Chip>
      </T>
      <T x={160} y={690} ancla="i" s={pop(p(3), 12, 1.4)}>
        <Chip tam={44} color="ambar" tinta="#1B1D22">El dueño de Mentos</Chip>
      </T>
      <Sello x={1400} y={320} t={p(4)} tam={42} rot={-3} color={AM}>El mismo Van Melle de Alemania</Sello>
      <T x={1040} y={620} ancla="i" op={tr(p(5), 0, 8)}>
        <Eti tam={26} color={GRIS}>Facturación · Perfetti Van Melle (2005)</Eti>
      </T>
      <div style={{position: 'absolute', left: 1040, top: 650, width: 760 * u, height: 70, borderRadius: 35, background: 'linear-gradient(180deg,#F4F5F7,#AEB5C2)'}} />
      <T x={1040} y={790} ancla="i" op={tr(p(5), 8, 8)}>
        <Eti tam={26} color={GRIS}>Chupa Chups (2004)</Eti>
      </T>
      <div style={{position: 'absolute', left: 1040, top: 820, width: 140 * u, height: 70, borderRadius: 35, background: 'linear-gradient(180deg,#FF6A5C,#C4161C)'}} />
      <T x={1290} y={856} ancla="i" s={pop(p(5) - 16, 12, 1.5)}>
        <Chip tam={50} color="rojo">Cinco veces menos</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** El precio nunca se ha confirmado; la prensa hablo de unos 400 M EUR. */
export const Precio: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit x={120} y={130} t={t} ancla="i" tam={110}>¿El precio?</Tit>
      <Im src="g_fajos" x={500} y={1100} w={660} t={t - 2} de="izq" cam={cam} />
      <Sello x={470} y={340} t={t - 14} tam={62} rot={-5} color="#F4F5F7">Nunca confirmado</Sello>
      <Dato x={1400} y={470} t={p(1)} cifra="≈ 400 M€" pie="según la prensa" tam={180} color="ambar" />
    </AbsoluteFill>
  );
};

/** 823 trabajadores en Espana y casi 1.500 fuera. El comite se entero por el periodico. */
export const Comite: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Dato x={380} y={220} t={t - 4} cifra="823" pie="trabajadores en España" tam={200} color="blanco" />
      <Dato x={1010} y={220} t={p(1)} cifra="≈ 1.500" pie="en el resto del mundo" tam={200} color="ambar" />
      <Parrafo x={1330} y={400} w={540} t={p(2)} tam={50} peso={700}>El comité de empresa se enteró <Am>por el periódico</Am></Parrafo>
      <Im src="g_periodico" x={1560} y={1090} w={620} t={p(2) - 2} de="der" cam={cam} />
      <div style={{position: 'absolute', left: 120, top: 560, width: 1080, font: "700 58px/1.2 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«Quieren que transmitamos tranquilidad a los trabajadores. *Pero tranquilos no estamos*»." u={p(3) < 0 ? 0 : c01(p(3) / 110)} />
      </div>
      <T x={126} y={900} ancla="i" op={tr(p(3), 20, 8)}>
        <Eti tam={26} color={GRIS}>Un miembro del comité de empresa · julio de 2006</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** Xavier Bernat: «una oportunidad excepcional». El comprador promete sede, plantas y fabrica nueva. */
export const Promesas: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Quien x={110} y={140} t={t} nombre="Xavier Bernat" cargo="Presidente de Chupa Chups · julio de 2006" tam={96} />
      <div style={{position: 'absolute', left: 110, top: 360, width: 900, font: "700 56px/1.2 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«Una *oportunidad excepcional* para sus empleados y para el futuro de sus centros industriales»." u={p(1) < 0 ? 0 : c01((p(1) + 20) / 100)} />
      </div>
      <div style={{position: 'absolute', left: 1080, top: 300, width: 2, height: 620, background: 'rgba(255,255,255,0.12)', opacity: tr(p(2), 0, 8)}} />
      <T x={1150} y={330} ancla="i" op={tr(p(2), 0, 8)}>
        <Eti tam={30} color={GRIS}>El comprador promete</Eti>
      </T>
      <Ok x={1170} y={460} t={p(2)}>Mantener la sede</Ok>
      <Ok x={1170} y={590} t={p(2) - 16}>Las dos plantas españolas</Ok>
      <Ok x={1170} y={720} t={p(3)}>Una fábrica nueva</Ok>
    </AbsoluteFill>
  );
};

/** Las escuelas de negocios: «muy critica»; «el futuro de las marcas estara garantizado, pero no el de la empresa». */
export const Profesores: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit x={120} y={110} t={t} ancla="i" tam={60}>Las escuelas de negocios de Barcelona lo vieron de otra manera</Tit>
      <Im src="g_piruleta" x={1730} y={1210} w={230} t={t - 4} de="aba" gris={0.6} luz={0.8} cam={cam} />
      <T x={126} y={260} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={28} color={GRIS}>Robert Tornabell · ESADE</Eti>
      </T>
      <Parrafo x={120} y={290} w={1300} t={p(1)} tam={80} serif>«La situación era <Am>muy crítica</Am>»</Parrafo>
      <T x={126} y={540} ancla="i" op={tr(p(2), 0, 8)}>
        <Eti tam={28} color={GRIS}>Jaime Llopis · IESE</Eti>
      </T>
      <div style={{position: 'absolute', left: 120, top: 580, width: 1440, font: "700 72px/1.18 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«El futuro de las marcas estará garantizado, *pero no el de la empresa*»." u={p(3) < 0 ? 0 : c01(p(3) / 105)} />
      </div>
    </AbsoluteFill>
  );
};

/** Acerto a medias: la sede y la fabrica principal siguen en Sant Esteve Sesrovires. */
export const Medias: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 900, 830, 2.6],
    [dur, 910, 845, 3.0],
  ]);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#5A1A1E', borde: ROJO} : undefined)} />
        <Ciudad x={SANT_ESTEVE[0]} y={SANT_ESTEVE[1]} t={p(1)} nombre="Sant Esteve Sesrovires" lado="i" tam={12} />
      </Mundo>
      <Tit x={120} y={140} t={t} ancla="i" tam={110}>Acertó a medias</Tit>
      <T x={1130} y={700} ancla="i" s={pop(p(1) - 6, 12, 1.4)}>
        <Chip tam={42} color="verde" tinta="#06301B">Sede y fábrica principal</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 2010: el nuevo dueno anuncia el cierre de Villamayor, donde empezo todo. 121 personas. */
export const Villamayor: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.4} blur={8} />
      <Hoja x={190} y={150} anio="2010" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={100} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={28} color={GRIS}>Cuatro años después de la compra</Eti>
      </T>
      <Tit x={316} y={170} t={p(1)} ancla="i" tam={76}>Cierra la fábrica de <Am>Villamayor</Am></Tit>
      <Im src="g_persiana" x={470} y={1130} w={620} t={p(1) - 2} de="arr" cam={cam} />
      <Sello x={1370} y={390} t={p(2)} tam={50} rot={-4} color={AM}>Donde había empezado todo</Sello>
      <Dato x={1380} y={640} t={p(3)} cifra="121" pie="personas trabajaban en ella" tam={240} color="blanco" />
      <T x={1380} y={940} s={pop(p(4), 12, 1.4)}>
        <Chip tam={44} color="humo">La producción se va a Barcelona</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 2013: otro recorte, un expediente de regulacion de empleo para 57 personas. */
export const Ere: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Hoja x={190} y={150} anio="2013" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Tit x={320} y={150} t={t - 4} ancla="i" tam={84}>Otro recorte</Tit>
      <Im src="g_persiana" x={1560} y={1120} w={460} t={t - 2} de="arr" luz={0.75} cam={cam} />
      <Dato x={700} y={540} t={p(1)} cifra="57" pie="personas, en un expediente de regulación de empleo" tam={330} color="rojo" />
    </AbsoluteFill>
  );
};

/** La nave de Asturias, anos casi vacia; una parte, alquilada para almacenar kiwis. */
export const Kiwis: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.4} blur={8} />
      <Tit x={120} y={120} t={t} ancla="i" tam={72}>La nave de Asturias, años <Am>casi vacía</Am></Tit>
      <Im src="g_nave" x={560} y={980} w={940} t={t - 2} de="izq" gris={0.8} luz={0.7} cam={cam} />
      <Im src="g_kiwis" x={1480} y={1080} w={600} t={p(1)} de="pop" />
      <T x={1400} y={460} s={pop(p(1) - 4, 12, 1.4)} rot={-2}>
        <Chip tam={40} fondo="#F4F5F7" tinta="#0B0C10">Una parte, alquilada para almacenar kiwis</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 2025: la compra una queseria de Cantabria. 30 M EUR, 50 empleos; desde 2027, quesos. */
export const Quesos: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const g = tr(p(4), 0, 12);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Hoja x={190} y={150} anio="2025" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={100} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={28} color={GRIS}>Verano</Eti>
      </T>
      <Tit x={316} y={170} t={t - 4} ancla="i" tam={70}>La compra una quesería de Cantabria</Tit>
      <Dato x={400} y={430} t={p(1)} cifra="30 M€" pie="de inversión" tam={190} color="ambar" />
      <Dato x={400} y={780} t={p(2)} cifra="50" pie="empleos" tam={190} color="blanco" />
      <div style={{position: 'absolute', left: 820, top: 300, width: 2, height: 680, background: 'rgba(255,255,255,0.12)', opacity: tr(p(3), 0, 8)}} />
      <Hoja x={960} y={360} anio="2027" s={1.05 * pop(p(3), 12, 1.4)} color="ambar" />
      <Parrafo x={1080} y={310} w={760} t={p(3)} tam={46}>Donde durante medio siglo se hicieron Chupa Chups…</Parrafo>
      <Im src="g_piruleta" x={1060} y={1190} w={200} t={p(3) - 4} de="aba" gris={0.6 * g} luz={1 - 0.2 * g} />
      <Im src="g_quesos" x={1540} y={1070} w={640} t={p(4)} de="pop" />
      <T x={1540} y={600} s={pop(p(4) - 4, 12, 1.5)}>
        <Chip tam={60} color="ambar" tinta="#1B1D22">…se harán quesos</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Hoy: una de las tres marcas mundiales de un grupo de mas de 4.000 M EUR, 18.000 empleados y 34 fabricas. */
export const Hoy: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit x={120} y={110} t={t} ancla="i" tam={64}>Hoy: una de las tres marcas mundiales de su grupo</Tit>
      {['Mentos', 'Chupa Chups', 'Alpenliebe'].map((n, i) => (
        <T key={n} x={120 + [0, 300, 720][i]} y={240} ancla="i" s={pop(t - 10 - i * 6, 12, 1.4)}>
          <Chip tam={46} color={i === 1 ? 'rojo' : 'humo'}>{n}</Chip>
        </T>
      ))}
      <Dato x={400} y={500} t={p(1)} cifra="+4.000 M€" pie="factura el grupo al año" tam={112} color="ambar" />
      <Dato x={1030} y={500} t={p(2)} cifra="18.000" pie="empleados" tam={112} color="blanco" />
      <Dato x={1560} y={500} t={p(3)} cifra="34" pie="fábricas" tam={112} color="blanco" />
      <Im src="g_globo" x={380} y={1150} w={300} t={p(4) - 2} de="aba" cam={cam} />
      <Dato x={1160} y={860} t={p(4)} cifra="+150 países" pie="donde se sigue vendiendo el caramelo" tam={150} color="ambar" />
    </AbsoluteFill>
  );
};

// =============================================================== CIERRE
/** Entonces, ¿por que vende mas fuera que dentro? */
export const Pregunta: React.FC<EP> = (ep) => {
  const {t, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.07);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Im src="g_piruleta" x={190} y={1210} w={230} t={t - 2} de="aba" cam={cam} />
      <Im src="g_globo" x={1730} y={1140} w={320} t={t - 6} de="aba" cam={cam} />
      <Parrafo x={330} y={230} w={1260} t={t} tam={112} centro serif>¿Por qué Chupa Chups vende <Am>más fuera de España</Am> que dentro?</Parrafo>
    </AbsoluteFill>
  );
};

/** Tres razones: un solo producto, nada que traducir y saliendo desde 1967. */
export const Porque: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      {[650, 1270].map((x) => (
        <div key={x} style={{position: 'absolute', left: x, top: 170, width: 2, height: 800, background: 'rgba(255,255,255,0.1)'}} />
      ))}
      <Im src="g_piruleta" x={250} y={640} w={120} t={t - 2} de="pop" />
      <Im src="g_globo" x={430} y={640} w={230} t={t - 8} de="pop" />
      <Parrafo x={80} y={700} w={520} t={t - 4} tam={44} centro>Nació con un solo producto, y un solo producto necesita <Am>el mundo entero</Am></Parrafo>
      <Flor x={960} y={440} r={140} u={tr(p(1), 0, 26)} relleno={tr(p(1), 20, 12)} trazo="#F4F5F7" grosor={6} />
      <Parrafo x={700} y={700} w={520} t={p(1)} tam={44} centro>Un caramelo, un palo y una flor <Am>no hay que traducirlos</Am></Parrafo>
      <Hoja x={1580} y={440} anio="1967" s={2.3 * pop(p(2), 12, 1.4)} color="rojo" />
      <Parrafo x={1320} y={700} w={520} t={p(2)} tam={44} centro>Lleva saliendo fuera <Am>desde 1967</Am></Parrafo>
    </AbsoluteFill>
  );
};

/** Vender en todo el mundo tiene un precio: demasiado grande para una familia, acabo comprada por el. */
export const Comprado: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.06);
  const u = io(tr(p(3), -34, 30));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit x={120} y={120} t={t} ancla="i" tam={72}>Pero vender en todo el mundo <Am>tiene un precio</Am></Tit>
      <Parrafo x={120} y={290} w={880} t={p(1)} tam={58}>Cuando las ventas cayeron, la empresa era <Am>demasiado grande para una sola familia</Am></Parrafo>
      <Im src="g_piruleta" x={lerp(1020, 1380, u)} y={lerp(1180, 1020, u)} w={lerp(210, 70, u)} t={p(2)} de="pop" op={1 - 0.9 * tr(p(3), -8, 12)} />
      <Im src="g_globo" x={1430} y={1130} w={540} t={t - 2} de="der" cam={cam} z={1.1} />
      <Sello x={580} y={800} t={p(3) - 4} tam={58} rot={-5}>Acabó comprada por él</Sello>
    </AbsoluteFill>
  );
};

/** Un ultimo detalle: la Casa Batllo sigue siendo de los Bernat. Abierta en 2002, Patrimonio en 2005. */
export const Casa: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.07);
  const a = 1 - tr(p(1), -4, 8);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.36} blur={10} />
      <Tit x={960} y={460} t={t} tam={130} op={a}>Queda un último detalle</Tit>
      <Detras x={560} y={180} t={p(1)} tam={170}>Casa Batlló</Detras>
      <Im src="g_batllo" x={560} y={1070} w={460} t={p(1) - 3} de="aba" cam={cam} />
      <Parrafo x={1190} y={360} w={640} t={p(1)} tam={42} color="#D5DBE6">La que hipotecaron para salvar los caramelos</Parrafo>
      <Sello x={1490} y={590} t={p(2)} tam={44} rot={-4} color="#2BE38A">Sigue siendo de los Bernat</Sello>
      <Hoja x={1240} y={750} anio="2002" s={0.7 * pop(p(3), 12, 1.4)} color="rojo" />
      <T x={1330} y={750} ancla="i" op={tr(p(3), 4, 8)}>
        <Sans tam={44} peso={700}>Abre al público</Sans>
      </T>
      <Hoja x={1240} y={930} anio="2005" s={0.7 * pop(p(4), 12, 1.4)} color="ambar" />
      <T x={1330} y={930} ancla="i" op={tr(p(4), 4, 8)}>
        <Sans tam={40} peso={700}>Patrimonio de la Humanidad</Sans>
      </T>
    </AbsoluteFill>
  );
};

/** 2023: mas de 1,5 millones de visitantes, el doble que diez anos antes, y 56 M EUR de ingresos. */
export const Visitantes: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.5} blur={6} arriba={0.72} abajo={0.75} />
      <AbsoluteFill style={{background: 'rgba(8,9,12,0.4)'}} />
      <Hoja x={190} y={150} anio="2023" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <T x={320} y={150} ancla="i" op={tr(t, 4, 8)}>
        <Eti tam={30} color={GRIS}>Casa Batlló</Eti>
      </T>
      <Dato x={470} y={470} t={t - 4} cifra="+1,5 millones" pie="de visitantes" tam={112} color="blanco" />
      <T x={470} y={720} s={pop(p(1), 12, 1.4)}>
        <Chip tam={46} color="humo">El doble que diez años antes</Chip>
      </T>
      <Dato x={1430} y={500} t={p(2)} cifra="56 M€" pie="de ingresos" tam={240} color="ambar" />
    </AbsoluteFill>
  );
};

/** La empresa espanola de los Chupa Chups factura unos 90 M EUR; el edificio ingresa mas de la mitad. */
export const Comparacion: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const K = 4.6;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <div style={{position: 'absolute', left: 200, top: 860, width: 1520, height: 4, background: 'rgba(255,255,255,0.22)'}} />
      <Im src="g_piruleta" x={300} y={860} w={130} t={t - 2} de="pop" />
      <Columna x={620} base={860} alto={90 * K} t={p(1)} cifra="≈ 90 M€" pie="la empresa española que los fabrica" color="linear-gradient(180deg,#FF6A5C,#C4161C)" tam={90} />
      <T x={620} y={950} op={tr(p(1), 8, 8)}>
        <Eti tam={22} color={GRIS}>Facturación anual, según la prensa</Eti>
      </T>
      <Columna x={1300} base={860} alto={56 * K} t={p(2)} cifra="56 M€" pie="el edificio" color="linear-gradient(180deg,#FFD95A,#F29A0B)" tam={90} />
      <Im src="g_batllo" x={1640} y={860} w={270} t={p(2) - 2} de="pop" />
      <Sello x={960} y={170} t={p(2) + 0 - 22} tam={64} rot={-3} color={AM}>Más de la mitad, sin fabricar nada</Sello>
    </AbsoluteFill>
  );
};

/** Perdieron el caramelo. Se quedaron con la casa. */
export const Final: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.08);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.34} blur={10} />
      <Im src="g_piruleta" x={460} y={1210} w={270} t={t - 2} de="aba" gris={0.6 * tr(t, 10, 14)} cam={cam} />
      <Tit x={480} y={140} t={t - 4} tam={70} color="#C9CED8">Perdieron el caramelo</Tit>
      <div style={{position: 'absolute', left: 959, top: 110, width: 2, height: 860, background: 'rgba(255,255,255,0.1)'}} />
      <Im src="g_batllo" x={1440} y={1070} w={440} t={p(1) - 2} de="aba" cam={cam} />
      <Tit x={1440} y={140} t={p(1)} tam={76} color={AM}>Se quedaron con la casa</Tit>
    </AbsoluteFill>
  );
};

export const CHUPA3 = {venta: Venta, precio: Precio, comite: Comite, promesas: Promesas, profesores: Profesores, medias: Medias, villamayor: Villamayor, ere: Ere, kiwis: Kiwis, quesos: Quesos, hoy: Hoy, pregunta: Pregunta, porque: Porque, comprado: Comprado, casa: Casa, visitantes: Visitantes, comparacion: Comparacion, final: Final};
export {Detras as _Detras, Marca as _Marca, Serif as _Serif};
