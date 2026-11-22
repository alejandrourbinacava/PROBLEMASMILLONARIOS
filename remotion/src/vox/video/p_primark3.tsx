import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP} from './base';
import {Chip, Cifra, Escenario, Eti, Hoja, Mapa, Marca, Mundo, Sans, Sello, Serif, T, camara, io, lerp, pop, sal, tr} from './kit';
import {MK, MX, MY} from './m_gancho';
import {Im, deriva} from './m_vox';
import {AM, Am, CIAN, Dato, Ficha, Fondo, Parrafo, Tit, Ventana} from './p_comun';

/**
 * Epilogo de «Por que Primark NO vende por internet» (el ultimo minuto):
 * no es solo Primark, lo que le abre la puerta, quien aprieta por el otro lado
 * y lo despacio que despliega estas cosas.
 */
const paso = (f: number) => Math.abs(Math.sin(f / 4.5)) * -7;

/** Zara cobra 1,95 EUR por recoger una devolucion a domicilio; en tienda sigue siendo gratis. */
export const Zara: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  const xr = lerp(1040, 800, sal(tr(p(2), 0, 50)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit x={120} y={120} t={t} ancla="i" tam={80}>Y no vas a pagarlo <Am>solo en Primark</Am></Tit>
      <Hoja x={190} y={300} anio="2023" s={pop(p(1), 12, 1.4)} color="cian" />
      <T x={310} y={252} ancla="i" op={tr(p(1), 4, 8)}>
        <Eti tam={28} color={CIAN}>Desde febrero · España</Eti>
      </T>
      <T x={306} y={336} ancla="i" s={pop(p(2), 12, 1.5)}>
        <Chip tam={56} fondo="#F4F5F7" tinta="#0B0C10">Zara</Chip>
      </T>
      <Im src="g_devolucion" x={420} y={1090} w={620} t={p(2) - 4} de="izq" cam={cam} />
      <Im src="g_repartidor" x={xr} y={1100 + paso(p(2))} w={250} t={p(2)} de="nada" />
      <Dato x={1400} y={400} t={p(3)} cifra="1,95 €" pie="por recoger una devolución a domicilio" tam={230} color="ambar" />
      <Im src="g_tienda" x={1400} y={1110} w={420} t={p(4)} de="aba" />
      <T x={1400} y={640} s={pop(p(4) - 4, 12, 1.5)} rot={-2}>
        <Chip tam={48} color="verde">Devolverla en la tienda: gratis</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** Las grandes cadenas cobran lo que antes regalaban: eso le abre la puerta a Primark. */
export const Regalaban: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const a = 1 - tr(p(2), -4, 8);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <div style={{position: 'absolute', inset: 0, opacity: a}}>
        <Tit t={t} y={110} tam={70}>Empiezan a cobrar lo que antes <Am>regalaban</Am></Tit>
        <Im src="g_paquete" x={520} y={900} w={520} t={t - 4} de="izq" />
        <T x={520} y={370} s={pop(t - 8, 12, 1.4)} rot={-3}>
          <Chip tam={60} fondo="#F4F5F7" tinta="#0B0C10"><span style={{textDecoration: p(1) > 4 ? 'line-through' : 'none', textDecorationColor: '#E0352B', textDecorationThickness: 7}}>Envío gratis</span></Chip>
        </T>
        <Im src="g_devolucion" x={1400} y={900} w={560} t={t - 10} de="der" />
        <T x={1400} y={370} s={pop(t - 14, 12, 1.4)} rot={3}>
          <Chip tam={60} fondo="#F4F5F7" tinta="#0B0C10"><span style={{textDecoration: p(1) > 10 ? 'line-through' : 'none', textDecorationColor: '#E0352B', textDecorationThickness: 7}}>Devolución gratis</span></Chip>
        </T>
        <T x={760} y={520} s={pop(p(1) - 10, 11, 1.8)} rot={8}>
          <Chip tam={56} color="ambar" tinta="#1B1D22">+ €</Chip>
        </T>
        <T x={1660} y={520} s={pop(p(1) - 16, 11, 1.8)} rot={-6}>
          <Chip tam={56} color="ambar" tinta="#1B1D22">+ €</Chip>
        </T>
      </div>
      <Tit t={p(2)} y={110} tam={76}>Y eso le abre la puerta a <Am>Primark</Am></Tit>
      <Im src="g_portatil" x={540} y={1010} w={760} t={p(2)} de="izq" />
      <T x={540} y={330} s={pop(p(2) - 8, 12, 1.4)}>
        <Chip tam={50} color="cian">Vender por internet…</Chip>
      </T>
      <Im src="g_camiseta_2" x={1400} y={1050} w={820} t={p(2) - 6} de="der" />
      <Sello x={1400} y={420} t={p(3)} tam={84} rot={-5} color="#F4F5F7">Sin tocar el precio</Sello>
    </AbsoluteFill>
  );
};

/** Como consigue el precio: compra enorme, casi sin publicidad, sin perchas caras. Margen minimo, volumen enorme. */
export const Receta: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const col = (k: number, x: number, txt: React.ReactNode, hijo: React.ReactNode) => (
    <>
      {hijo}
      <Parrafo x={x - 250} y={640} w={500} t={p(k)} tam={44} centro>{txt}</Parrafo>
    </>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit t={t} y={100} tam={76}>Ese precio es <Am>todo lo que tiene</Am></Tit>
      <T x={960} y={190} op={tr(p(1), 0, 8)}>
        <Eti tam={28} color="#C9CED8">Cómo lo consigue, según la propia empresa</Eti>
      </T>
      {col(2, 340, <>Compra <Am>cantidades enormes</Am> de cada prenda</>, <Im src="g_monton" x={340} y={600} w={540} t={p(2)} de="izq" />)}
      {col(
        3,
        960,
        <>Apenas hace <Am>publicidad</Am></>,
        <>
          <div style={{position: 'absolute', left: 760, top: 300, width: 400, height: 250, borderRadius: 18, background: 'linear-gradient(180deg,#5C6375,#2F3442)', border: '6px solid #8D93A1', opacity: tr(p(3), 0, 8), transform: `scale(${pop(p(3), 12, 1.4)})`, boxShadow: '0 30px 60px rgba(0,0,0,0.5)'}}>
            <div style={{font: "800 58px/238px 'D Sans'", letterSpacing: 8, color: '#C9CED8', textAlign: 'center'}}>ANUNCIO</div>
          </div>
          <Marca tipo="no" x={960} y={425} t={p(3) - 10} s={4} grosor={8} />
        </>,
      )}
      {col(4, 1580, <>Se ahorra hasta las <Am>perchas caras</Am></>, <Im src="g_perchero" x={1580} y={600} w={400} t={p(4)} de="der" />)}
      <div style={{position: 'absolute', left: 260, top: 840, width: 1400, height: 2, background: 'rgba(255,255,255,0.14)', opacity: tr(p(5), 0, 8)}} />
      <Im src="g_moneda" x={400} y={985} w={110} t={p(5)} de="pop" />
      <T x={960} y={900} op={tr(p(5), 2, 8)}>
        <Serif tam={62} peso={600}>Gana muy poco con cada prenda…</Serif>
      </T>
      <T x={960} y={985} s={pop(p(6), 12, 1.4)}>
        <Serif tam={72} peso={600} color={AM}>…y vende muchísimas</Serif>
      </T>
    </AbsoluteFill>
  );
};

/** Al otro lado, quien si lleva la ropa a casa: Shein vendio unos 2.400 M EUR en el Reino Unido en 2024. */
export const SheinUk: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  const xr = lerp(1040, 1330, sal(tr(t, 6, 60)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit x={120} y={110} t={t} ancla="i" tam={70}>Al otro lado: quien <Am>sí lleva la ropa a casa</Am></Tit>
      <Im src="g_casa" x={1650} y={1110} w={460} t={t - 2} de="der" cam={cam} />
      <Im src="g_repartidor" x={xr} y={1105 + paso(t)} w={250} t={t - 6} de="nada" />
      <T x={1500} y={330} s={pop(t - 18, 12, 1.5)} rot={3}>
        <Chip tam={52} color="ambar" tinta="#1B1D22">…y más barata</Chip>
      </T>
      <T x={120} y={318} ancla="i" s={pop(p(2), 12, 1.4)}>
        <Chip tam={60} fondo="#F4F5F7" tinta="#0B0C10">Shein</Chip>
      </T>
      <T x={124} y={232} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={28} color={CIAN}>Solo en el Reino Unido · 2024</Eti>
      </T>
      <Dato x={120} y={540} t={p(3)} cifra="≈ 2.400 M€" pie="en ventas" tam={190} ancla="i" />
      <T x={120} y={790} ancla="i" s={pop(p(4), 12, 1.5)} rot={-2}>
        <Chip tam={54} color="rojo">Un tercio más que el año anterior</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** ¿Y cuando llegara a Espana? No ha dicho nada. Pero su historia da una pista: despacio. */
export const Cuando: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 900, 820, 2.3],
    [dur, 880, 850, 2.6],
  ]);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0B5E86', borde: CIAN} : undefined)} />
      </Mundo>
      <T x={560} y={590} s={pop(t - 4, 13, 1.6)}>
        <Cifra tam={300} color="blanco">?</Cifra>
      </T>
      <Parrafo x={1090} y={120} w={780} t={t} tam={84} serif>¿Y cuándo llegará a España?</Parrafo>
      <Sello x={1450} y={470} t={p(1)} tam={70} rot={-5}>No ha dicho nada</Sello>
      <Parrafo x={1090} y={640} w={760} t={p(2)} tam={64} serif>Pero su historia da <Am>una pista</Am> de cómo hace las cosas</Parrafo>
    </AbsoluteFill>
  );
};

/** La recogida en tienda, paso a paso: 25 tiendas, 57, el anuncio y las 187. Dos anos y medio. */
export const Escalera: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const BASE = 900;
  const barra = (x: number, n: number, tt: number, cuando: string, color: string) => {
    const h = (n / 187) * 440 * io(tr(tt, 0, 22));
    return tt < 0 ? null : (
      <>
        <div style={{position: 'absolute', left: x - 110, top: BASE - h, width: 220, height: h, borderRadius: 14, background: color}} />
        <T x={x} y={BASE - (n / 187) * 440 - 70} s={pop(tt - 10, 12, 1.4)}>
          <Cifra tam={110} color={n === 187 ? 'ambar' : 'cian'}>{String(Math.round(n * io(tr(tt, 0, 22))))}</Cifra>
        </T>
        <T x={x} y={BASE + 46} op={tr(tt, 4, 8)}>
          <Eti tam={28} color="#C9CED8">{cuando}</Eti>
        </T>
      </>
    );
  };
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit x={120} y={130} t={t} ancla="i" tam={130} color={AM}>Despacio</Tit>
      <T x={128} y={236} ancla="i" op={tr(t, 8, 8)}>
        <Eti tam={30} color="#C9CED8">La recogida en tienda, paso a paso</Eti>
      </T>
      <div style={{position: 'absolute', left: 120, top: BASE, width: 1680, height: 4, background: 'rgba(255,255,255,0.22)'}} />
      {barra(330, 25, t - 4, 'Noviembre de 2022', 'linear-gradient(180deg,#45D0FF,#0A7BD6)')}
      {barra(730, 57, p(1), 'Verano de 2023', 'linear-gradient(180deg,#45D0FF,#0A7BD6)')}
      <T x={730} y={BASE + 96} s={pop(p(1) - 12, 11, 1.4)}>
        <Chip tam={34} color="humo">Londres · ropa de mujer</Chip>
      </T>
      <Hoja x={1130} y={620} anio="2024" s={1.1 * pop(p(2), 12, 1.4)} color="cian" />
      <T x={1130} y={BASE + 46} op={tr(p(2), 4, 8)}>
        <Eti tam={28} color="#C9CED8">Abril de 2024</Eti>
      </T>
      <T x={1130} y={770} s={pop(p(3), 12, 1.5)} rot={-3}>
        <Chip tam={36} fondo="#F4F5F7" tinta="#0B0C10">Anuncia: a todo el país</Chip>
      </T>
      {barra(1560, 187, p(4), 'Mayo de 2025', 'linear-gradient(180deg,#FFD95A,#F29A0B)')}
      <Im src="g_bolsa" x={1800} y={BASE} w={170} t={p(4) - 8} de="pop" />
      <Sello x={1080} y={320} t={p(4) - 20} tam={72} rot={-4} color={AM}>Dos años y medio</Sello>
    </AbsoluteFill>
  );
};

/** Si repite el orden (suposicion nuestra): no una furgoneta en tu calle, sino un mostrador de recogida. */
export const Mostrador: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 30, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit t={t} y={110} tam={76}>Si en España repite el orden…</Tit>
      <T x={960} y={215} s={pop(p(1), 12, 1.4)}>
        <Chip tam={40} color="humo">Suposición nuestra</Chip>
      </T>
      <div style={{position: 'absolute', left: 959, top: 300, width: 2, height: 700, background: 'rgba(255,255,255,0.1)', opacity: tr(p(3), 0, 8)}} />
      <T x={480} y={380} op={tr(p(3), 0, 8)}>
        <Sans tam={46} peso={700} color="#D5DBE6">No será una furgoneta en tu calle</Sans>
      </T>
      <Im src="g_furgo" x={480} y={900} w={760} t={p(3)} de="izq" gris={1} luz={0.6} />
      <Marca tipo="no" x={480} y={760} t={p(3) - 10} s={4.4} grosor={8} />
      <T x={1440} y={380} s={pop(p(4), 12, 1.4)}>
        <Chip tam={50} color="cian">Será un mostrador de recogida</Chip>
      </T>
      <Im src="g_tienda_p" x={1520} y={1150} w={600} t={p(4) - 2} de="aba" cam={cam} />
      <Im src="g_bolsa" x={1150} y={1120} w={260} t={p(4) - 10} de="pop" z={1.2} cam={cam} />
    </AbsoluteFill>
  );
};

/** Hasta entonces, el boton seguira diciendo «ver la disponibilidad». Y ya sabes por que. */
export const Boton: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const W = 1260;
  const H = 760;
  const b = io(tr(p(2), -4, 14));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <T x={960} y={84} op={tr(t, 0, 8) * (1 - b)}>
        <Eti tam={30} color={CIAN}>Hasta entonces, en España</Eti>
      </T>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${1 - 0.1 * b})`, transformOrigin: '50% 60%', filter: `brightness(${1 - 0.62 * b}) blur(${3 * b}px)`}}>
        <Ventana x={330} y={150} w={W} h={H} t={t}>
          <Ficha w={W} h={H - 54} t={t} pulso={p(1)} />
        </Ventana>
      </div>
      <Tit x={960} y={400} t={p(2)} tam={84}>Y si has llegado hasta aquí…</Tit>
      <Tit x={960} y={590} t={p(3)} tam={190} color={AM}>ya sabes por qué</Tit>
    </AbsoluteFill>
  );
};

export const PRIMARK3 = {zara: Zara, regalaban: Regalaban, receta: Receta, shein_uk: SheinUk, cuando: Cuando, escalera: Escalera, mostrador: Mostrador, boton: Boton};
