import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {EP} from './base';
import {Chip, Cifra, Escenario, Eti, Flecha, Hoja, Mapa, Marca, Mundo, Palabras, Sans, Sello, Serif, T, c01, camara, io, lerp, miles, pop, rebote, sal, tr} from './kit';
import {Detras} from './m_capas';
import {MK, MX, MY} from './m_gancho';
import {Im, deriva} from './m_vox';
import {AM, Am, CIAN, Cursor, Dato, Ficha, Fondo, Movil, Parrafo, Quien, Tit, Ventana} from './p_comun';

const paso = (f: number) => Math.abs(Math.sin(f / 4.5)) * -7;

// =============================================================== GANCHO
/** 0-9 s · la web: esta todo, menos el boton de comprar. */
export const Web: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const W = 1420;
  const H = 860;
  const X = 250;
  const Y = 104;
  // el cursor va al boton que no existe y luego al que si
  const cx = lerp(1500, 1330, io(tr(p(4), 4, 14)));
  const cy0 = lerp(980, Y + 54 + 520, io(tr(p(4), 4, 14)));
  const cy = lerp(cy0, Y + 54 + 624, io(tr(p(5), 2, 12)));
  const clic = p(5) > 16 ? ((p(5) - 16) % 22) / 22 : 0;
  const sal7 = tr(p(7), 0, 10);
  const x7 = lerp(-320, 640, sal(tr(p(7), 0, 60))) + Math.max(0, p(7)) * 0.9;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} blur={10} luz={0.4} />
      <div style={{position: 'absolute', inset: 0, transform: `scale(${1 - 0.06 * sal7}) translateY(${-10 * sal7}px)`, transformOrigin: '70% 40%', filter: `brightness(${1 - 0.25 * sal7})`}}>
        <Ventana x={X} y={Y} w={W} h={H} t={t}>
          <Ficha w={W} h={H - 54} t={p(1)} fantasma={tr(p(4), 0, 8)} tachado={tr(p(5), 0, 8)} pulso={p(5)} precio={p(3)} />
        </Ventana>
        <Cursor x={cx} y={cy + (p(5) > 16 ? Math.sin(p(5) / 2.2) * 2 : 0)} clic={clic} op={tr(p(4), 0, 6)} />
        <Sello x={1300} y={668} t={p(6)} tam={66} rot={-5}>No se puede comprar</Sello>
      </div>
      <Im src="g_compradora" x={x7} y={1150 + paso(p(7))} w={500} t={p(7)} de="nada" z={1.2} />
      <T x={1260} y={965} s={pop(p(7) - 8, 12, 1.4)} rot={-2}>
        <Chip tam={66} fondo="#0B0C10" tinta="#F4F5F7" borde={CIAN}>Tienes que ir a por él</Chip>
      </T>
    </AbsoluteFill>
  );
};

/** 10-20 s · mas de 500 tiendas y 11.000 M EUR... y cero por internet. */
export const Gigante: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 40, 0.06);
  const a = 1 - tr(p(2), -4, 8);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.4} />
      <Im src="g_tienda_p" x={470} y={1150} w={860} t={t - 2} de="aba" z={0.8} cam={cam} />
      <Dato x={1340} y={270} t={t - 4} cifra="+500" pie="tiendas" tam={230} op={a} />
      <Dato x={1340} y={640} t={p(1)} cifra={`+${miles(Math.round(11000 * sal(p(1) / 30)))} M€`} pie="de ventas al año" tam={160} color="ambar" op={a} />
      <T x={1380} y={120} op={tr(p(2), 0, 8)}>
        <Eti tam={32} color="#C9CED8">Lo que venden por internet</Eti>
      </T>
      <Dato x={1380} y={330} t={p(3)} cifra="26,7 %" pie="de las ventas de Inditex, la dueña de Zara" tam={170} color="blanco" />
      <Dato x={1380} y={760} t={p(4)} cifra="0 %" pie="de las ventas de Primark" tam={270} color="rojo" />
    </AbsoluteFill>
  );
};

/** 20-29 s · la pandemia: de mas de 700 M EUR al mes a cero. */
export const Pandemia: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const v = p(3) < 0 ? 700 : Math.round(700 * (1 - io(tr(p(3), 0, 26))));
  const cam = deriva(t, 0, ep.dur, 40, 0.07);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.34} />
      <Hoja x={200} y={170} anio="2020" s={1.05 * pop(t, 12, 1.4)} color="rojo" />
      <Tit x={330} y={170} t={t - 4} ancla="i" tam={76}>Una pandemia le cierra las tiendas</Tit>
      <Im src="g_persiana" x={960} y={1410} w={860} t={t - 6} de="arr" luz={0.95} cam={cam} />
      <T x={960} y={290} op={tr(p(2), 0, 8)}>
        <Eti tam={30} color="#C9CED8">Ventas de Primark al mes</Eti>
      </T>
      <T x={960} y={420} s={pop(p(2), 12, 1.4)}>
        <Cifra tam={230} color={v === 0 ? 'rojo' : 'ambar'}>{v === 0 ? '0 €' : `${v} M€`}</Cifra>
      </T>
    </AbsoluteFill>
  );
};

/** 29-39 s · «no nos salen las cuentas»... y este septiembre, que si. */
export const Cuentas: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const b = tr(p(2), -3, 10);
  const c = tr(p(4), -3, 8);
  const g = tr(p(3), 0, 12);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <div style={{position: 'absolute', inset: 0, opacity: 1 - c}}>
        <T x={960} y={lerp(300, 150, io(b))} op={tr(t, 0, 8)}>
          <Eti tam={30} color="#C9CED8">La respuesta, siempre la misma</Eti>
        </T>
        <T x={960} y={lerp(470, 270, io(b))} s={lerp(1, 0.62, io(b))} op={tr(p(1), 0, 6) * (1 - 0.4 * b)}>
          <Serif tam={140} peso={600}>«No nos salen las cuentas»</Serif>
        </T>
        <Hoja x={1250} y={620} anio="2026" s={1.5 * pop(p(2), 12, 1.5)} color="cian" />
        <T x={1250} y={452} s={pop(p(2) - 4, 11, 1.4)}>
          <Chip tam={40} color="cian">Septiembre</Chip>
        </T>
        <Sello x={1560} y={840} t={p(3) - 6} tam={120} rot={-8} color="#2BE38A">Sí</Sello>
      </div>
      <Im src="g_furgo" x={lerp(620, 960, io(c))} y={1060} w={lerp(760, 900, io(c))} t={t - 6} de="izq" gris={1 - g} luz={0.55 + 0.45 * g} />
      <div style={{position: 'absolute', inset: 0, opacity: 1 - g}}>
        <Marca tipo="no" x={620} y={920} t={t - 16} s={4.2} grosor={8} />
      </div>
      <Tit x={960} y={250} t={p(4)} tam={150}>¿Por qué ahora?</Tit>
      <Tit x={960} y={470} t={p(5)} tam={104} color={AM}>Antes hay que saber por qué no</Tit>
    </AbsoluteFill>
  );
};

// =============================================================== 1 · UNA CAMISETA DE DOS EUROS
/** John Bason y la camiseta: «un tercio de la ropa se devuelve». */
export const Bason: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 36, 0.05);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.32} />
      <Quien x={110} y={150} t={t} nombre="John Bason" cargo="Entonces director financiero del grupo dueño de Primark" />
      <Im src="g_camiseta_2" x={1380} y={1040} w={1020} t={p(2)} de="der" cam={cam} />
      <T x={1380} y={300} s={pop(p(1), 11, 1.4)}>
        <Chip tam={40} color="humo">Su ejemplo: una camiseta de poco más de 2 €</Chip>
      </T>
      <div style={{position: 'absolute', left: 110, top: 400, width: 880, font: "700 66px/1.18 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«Todo el mundo cree que es clic, clic y ya." u={p(3) < 0 ? 0 : c01(p(3) / 48)} />
      </div>
      <div style={{position: 'absolute', left: 110, top: 660, width: 880, font: "700 66px/1.18 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="Pero *un tercio de la ropa se devuelve*»." u={p(4) < 0 ? 0 : c01(p(4) / 44)} />
      </div>
    </AbsoluteFill>
  );
};

/** El viaje de la camiseta: almacen, bolsa, reparto, casa... y vuelta. */
export const Viaje: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const xf = lerp(980, 1340, io(tr(p(2), 0, 44)));
  const Y = 800;
  const vuelta = io(tr(p(3), 0, 34));
  const et = (x: number, txt: string, tt: number) => (
    <T x={x} y={Y + 74} op={tr(tt, 4, 8)}>
      <Eti tam={28} color="#C9CED8">{txt}</Eti>
    </T>
  );
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Tit t={t} y={110} tam={76}>El viaje de una camiseta de <Am>2 €</Am></Tit>
      <div style={{position: 'absolute', left: 80, top: Y + 8, width: 1760, height: 6, background: 'rgba(255,255,255,0.22)'}} />
      <Im src="g_nave" x={330} y={Y} w={560} t={t - 2} de="izq" />
      <Im src="g_camiseta_2" x={330} y={Y - 210} w={250} t={t - 10} de="pop" />
      {et(330, 'almacén', t)}
      <Im src="g_paquete" x={790} y={Y + 6} w={300} t={p(1)} de="pop" />
      {et(790, 'a una bolsa', p(1))}
      <Im src="g_casa" x={1690} y={Y + 6} w={330} t={p(2) - 8} de="der" />
      {et(1690, 'hasta una casa', p(2))}
      <Im src="g_furgo" x={xf} y={Y + 10} w={430} t={p(2)} de="nada" />
      <Flecha x0={1600} y0={300} x1={390} y1={300} u={vuelta} curva={0.1} color="#FF6A5C" grosor={9} />
      <T x={1640} y={250} s={pop(p(3), 11, 1.5)}>
        <Chip tam={44} color="rojo">Y si vuelve…</Chip>
      </T>
      {[['recogerla', 1280], ['revisarla', 960], ['doblarla otra vez', 600]].map(([txt, x], i) => (
        <T key={i} x={x as number} y={400} s={pop(p(4 + i), 11, 1.6)} rot={(i - 1) * 2}>
          <Chip tam={42} fondo="#F4F5F7" tinta="#0B0C10">{txt}</Chip>
        </T>
      ))}
    </AbsoluteFill>
  );
};

/** En una prenda de 40 EUR el viaje se paga solo; en una de 2, cuesta mas que la prenda. */
export const CuarentaDos: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const col = (cx: number, t0: number, precio: number, etiqueta: string, tRojo: number, hijo: React.ReactNode) => {
    const x0 = cx - 330;
    return (
      <>
        <T x={cx} y={150} s={pop(t0, 11, 1.4)}>
          <Chip tam={48} color="humo">{etiqueta}</Chip>
        </T>
        {hijo}
        <T x={x0} y={690} ancla="i" op={tr(t0, 8, 8)}>
          <Sans tam={32} peso={700} color="#D5DBE6">Lo que vale</Sans>
        </T>
        <div style={{position: 'absolute', left: x0, top: 716, width: Math.max(0, precio * 16 * io(tr(t0, 8, 18))), height: 46, borderRadius: 23, background: 'linear-gradient(90deg,#45D0FF,#0A7BD6)'}} />
        <T x={x0} y={810} ancla="i" op={tr(t0, 14, 8)}>
          <Sans tam={32} peso={700} color="#D5DBE6">El viaje hasta casa</Sans>
        </T>
        <div style={{position: 'absolute', left: x0, top: 836, width: Math.max(0, 150 * io(tr(t0, 14, 18))), height: 46, borderRadius: 23, background: tRojo >= 0 ? 'linear-gradient(90deg,#FF6A5C,#C4161C)' : 'linear-gradient(90deg,#FFD95A,#F29A0B)'}} />
      </>
    );
  };
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      {col(500, t, 40, 'Una prenda de 40 €', -1, <Im src="g_jersey" x={500} y={640} w={360} t={t - 2} de="pop" />)}
      {col(1420, p(2), 2, 'Una camiseta de 2 €', p(3), <Im src="g_camiseta_2" x={1420} y={630} w={560} t={p(2)} de="pop" />)}
      <div style={{position: 'absolute', left: 959, top: 110, width: 2, height: 840, background: 'rgba(255,255,255,0.1)'}} />
      <Sello x={560} y={980} t={p(1)} tam={60} rot={-4} color="#2BE38A">Se paga solo</Sello>
      <Sello x={1440} y={980} t={p(3)} tam={52} rot={-4}>Cuesta más que la prenda</Sello>
    </AbsoluteFill>
  );
};

/** Devoluciones: 8 % en tienda, 25 % por internet, 30-70 % en moda. */
export const Devoluciones: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={110}>Y luego están <Am>las devoluciones</Am></Tit>
      <Im src="g_compradora" x={340} y={640} w={230} t={p(1)} de="pop" />
      <Im src="g_paquete" x={960} y={640} w={400} t={p(2)} de="pop" />
      <Im src="g_devolucion" x={1580} y={640} w={460} t={p(3)} de="pop" />
      {[['En tienda', 340, 1], ['Por internet', 960, 2], ['Moda por internet', 1580, 3]].map(([txt, x, k]) => (
        <T key={k as number} x={x as number} y={240} s={pop(p(k as number), 11, 1.4)}>
          <Chip tam={40} color="humo">{txt}</Chip>
        </T>
      ))}
      <Dato x={340} y={780} t={p(1)} cifra="8 %" tam={170} color="verde" />
      <Dato x={960} y={780} t={p(2)} cifra="≈ 25 %" tam={146} color="ambar" />
      <Dato x={1580} y={780} t={p(3)} cifra="30–70 %" tam={124} color="rojo" />
      <T x={960} y={960} op={tr(p(1), 6, 8)}>
        <Eti tam={30} color="#C9CED8">de lo que se vende, se devuelve</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** Portsmouth: devolver una prenda de 6 EUR cuesta 7,50. Y 6 EUR es el precio medio de Primark. */
export const Portsmouth: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const a = 1 - tr(p(4), -4, 8);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <div style={{position: 'absolute', inset: 0, opacity: a}}>
        <T x={960} y={90} op={tr(t, 0, 8)}>
          <Eti tam={30} color={CIAN}>Universidad de Portsmouth · 2021</Eti>
        </T>
        <Tit t={t - 4} y={180} tam={80}>La cuenta de una devolución</Tit>
        <Im src="g_camiseta_6" x={480} y={720} w={640} t={p(1)} de="izq" />
        <Dato x={480} y={840} t={p(1)} cifra="≈ 6 €" pie="lo que vale la prenda" tam={170} />
        <Im src="g_devolucion" x={1440} y={720} w={600} t={p(2)} de="der" />
        <Dato x={1440} y={840} t={p(2)} cifra="≈ 7,50 €" pie="lo que cuesta tramitar su devolución" tam={170} color="rojo" />
        <T x={960} y={600} s={pop(p(2), 12, 1.6)}>
          <Cifra tam={220} color="blanco">{'<'}</Cifra>
        </T>
        <Sello x={960} y={420} t={p(3)} tam={84} rot={-5}>Más de lo que vale</Sello>
      </div>
      <Im src="g_perchero" x={520} y={1040} w={800} t={p(4)} de="izq" />
      <Dato x={1360} y={440} t={p(4) - 2} cifra="≈ 6 €" pie="cuesta de media una prenda de Primark" tam={280} />
      <T x={1360} y={720} op={tr(p(4), 12, 8)}>
        <Eti tam={26} color="#C9CED8">Estimación del sector, no de la compañía</Eti>
      </T>
    </AbsoluteFill>
  );
};

/** Las demas: o venden mas caro, o cobran el envio. Primark, ninguna: solo vende el precio. */
export const DosManeras: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const x3 = tr(p(3), 0, 8);
  const a = 1 - tr(p(4), -4, 8);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <div style={{position: 'absolute', inset: 0, opacity: a}}>
        <Tit t={t} y={120} tam={72}>Las demás cadenas lo resuelven de dos maneras</Tit>
        <div style={{position: 'absolute', inset: 0, opacity: 1 - 0.5 * x3}}>
          <Im src="g_jersey" x={520} y={700} w={380} t={p(1)} de="pop" />
          <T x={690} y={360} s={pop(p(1) - 6, 11, 1.8)} rot={8}>
            <Chip tam={60} color="ambar" tinta="#1B1D22">+ €</Chip>
          </T>
          <T x={520} y={790} s={pop(p(1), 11, 1.4)}>
            <Chip tam={52} color="humo">Vender más caro</Chip>
          </T>
          <Im src="g_paquete" x={1400} y={700} w={520} t={p(2)} de="pop" />
          <T x={1640} y={380} s={pop(p(2) - 6, 11, 1.8)} rot={-6}>
            <Chip tam={54} color="ambar" tinta="#1B1D22">+ envío</Chip>
          </T>
          <T x={1400} y={790} s={pop(p(2), 11, 1.4)}>
            <Chip tam={52} color="humo">Cobrar el envío</Chip>
          </T>
        </div>
        <Marca tipo="no" x={520} y={520} t={p(3)} s={4.2} grosor={8} />
        <Marca tipo="no" x={1400} y={520} t={p(3) - 5} s={4.2} grosor={8} />
        <T x={960} y={940} s={pop(p(3) - 8, 12, 1.5)}>
          <Chip tam={56} color="cian">Primark no quería ninguna de las dos</Chip>
        </T>
      </div>
      <T x={960} y={130} op={tr(p(4), 0, 8)}>
        <Eti tam={32} color="#C9CED8">Lo único que vende de verdad</Eti>
      </T>
      <Detras x={960} y={360} t={p(4)} tam={330}>el precio</Detras>
      <Im src="g_camiseta_2" x={960} y={1060} w={980} t={p(4) - 3} de="aba" />
    </AbsoluteFill>
  );
};

// =============================================================== 2 · YA LO HABIA PROBADO
/** 2013: la prueba con Asos. Y la conclusion de Bason. */
export const Asos: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const PRENDAS = ['g_camiseta', 'g_jersey', 'g_bolsa', 'g_jersey', 'g_camiseta', 'g_bolsa', 'g_jersey', 'g_camiseta'];
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.3} />
      <Hoja x={190} y={150} anio="2013" s={1.05 * pop(t, 12, 1.4)} color="cian" />
      <Tit x={320} y={150} t={t - 4} ancla="i" tam={84}>Primark hizo <Am>la prueba</Am></Tit>
      <Parrafo x={120} y={262} w={1040} t={p(1)} tam={44}>Puso a la venta una selección de su ropa…</Parrafo>
      <T x={120} y={390} ancla="i" s={pop(p(2), 12, 1.5)}>
        <Chip tam={60} fondo="#F4F5F7" tinta="#0B0C10">…en Asos</Chip>
      </T>
      <T x={124} y={462} ancla="i" op={tr(p(2), 8, 8)}>
        <Eti tam={24} color="#C9CED8">una de las mayores tiendas de moda por internet</Eti>
      </T>
      <Movil x={1160} top={60} w={700} t={t - 6}>
        <div style={{position: 'absolute', inset: 0, background: '#fff'}}>
          <div style={{height: 70, background: '#1B1D22', font: "800 30px/70px 'D Sans'", letterSpacing: 6, color: '#fff', textAlign: 'center', opacity: tr(p(2), 0, 8)}}>ASOS</div>
          {PRENDAS.map((f, i) => (
            <div key={i} style={{position: 'absolute', left: 14 + (i % 2) * 144, top: 86 + Math.floor(i / 2) * 166, width: 130, height: 152, borderRadius: 12, background: '#EEF0F3', transform: `scale(${pop(p(1) - i * 4, 10, 1.6)})`}}>
              <Img src={staticFile(`vox/media/${f}.webp`)} style={{position: 'absolute', maxWidth: 104, maxHeight: 118, left: '50%', top: '46%', transform: 'translate(-50%,-50%)'}} />
              <div style={{position: 'absolute', left: 12, bottom: 10, width: 60, height: 8, borderRadius: 4, background: '#C5CBD7'}} />
            </div>
          ))}
        </div>
      </Movil>
      <Sello x={600} y={596} t={p(3)} tam={66} rot={-5}>No pasó de prueba</Sello>
      <T x={124} y={730} ancla="i" op={tr(p(4), 0, 8)}>
        <Eti tam={26} color={CIAN}>La conclusión de John Bason</Eti>
      </T>
      <div style={{position: 'absolute', left: 120, top: 770, width: 1010, font: "700 46px/1.2 'D Sans'", color: '#F4F5F7'}}>
        <Palabras texto="«Lo que aprendimos es que podemos vender con beneficio en la calle *mucho más barato* de lo que nadie puede hacerlo por internet»." u={p(4) < 0 ? 0 : c01(p(4) / 190)} />
      </div>
    </AbsoluteFill>
  );
};

/** El negocio contrario al de una web: no lleva la ropa; el cliente va a por ella. */
export const Contrario: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const xf = lerp(520, 1380, io(tr(p(1), 4, 60)));
  const xc = lerp(560, 1500, sal(tr(p(3), 0, 70)));
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={100} tam={76}>El negocio <Am>contrario</Am> al de una web</Tit>
      {/* una web */}
      <T x={960} y={220} s={pop(p(1), 11, 1.4)}>
        <Chip tam={40} color="humo">Una web lleva la ropa al cliente</Chip>
      </T>
      <div style={{position: 'absolute', left: 120, top: 478, width: 1680, height: 5, background: 'rgba(255,255,255,0.2)', opacity: tr(p(1), 0, 8)}} />
      <Im src="g_nave" x={300} y={474} w={420} t={p(1)} de="izq" />
      <Im src="g_casa" x={1690} y={480} w={190} t={p(1) - 4} de="der" />
      <Im src="g_furgo" x={xf} y={482} w={330} t={p(1) - 4} de="nada" />
      {/* Primark */}
      <T x={960} y={600} s={pop(p(2), 11, 1.4)}>
        <Chip tam={40} color="cian">Primark: el cliente va a por ella… y se la lleva él</Chip>
      </T>
      <div style={{position: 'absolute', left: 120, top: 1008, width: 1680, height: 5, background: 'rgba(255,255,255,0.2)', opacity: tr(p(2), 0, 8)}} />
      <Im src="g_tienda_p" x={320} y={1016} w={360} t={p(2)} de="izq" />
      <Im src="g_casa" x={1690} y={1010} w={190} t={p(2) - 4} de="der" />
      <Flecha x0={1560} y0={850} x1={560} y1={850} u={io(tr(p(2), 6, 26)) * (1 - tr(p(3), 0, 10))} curva={0.08} color="#fff" grosor={7} />
      <Im src="g_compradora" x={xc} y={1012 + paso(p(3))} w={185} t={p(3)} de="nada" />
    </AbsoluteFill>
  );
};

/** 2005-2015: la ropa por internet pasa del 5 al 17 %... y Primark multiplica casi por seis. */
export const Seis: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  const u = io(tr(p(1), 0, 40));
  const b = io(tr(p(3), 0, 34));
  const X0 = 150;
  const X1 = 850;
  const y5 = 800;
  const y17 = 470;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.26} />
      <Tit t={t} y={110}>Y le ha ido <Am>muy bien</Am> así</Tit>
      <div style={{position: 'absolute', inset: 0, opacity: 1 - 0.68 * tr(p(5), 0, 8)}}>
      <T x={X0} y={250} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={28} color="#C9CED8">Ropa vendida por internet · Reino Unido</Eti>
      </T>
      <svg width={1920} height={1080} style={{position: 'absolute'}}>
        <path d={`M${X0},880 L${X1},880`} stroke="rgba(255,255,255,0.25)" strokeWidth={4} opacity={tr(p(1), 0, 8)} />
        <path d={`M${X0},${y5} L${lerp(X0, X1, u)},${lerp(y5, y17, u)}`} stroke={CIAN} strokeWidth={12} strokeLinecap="round" fill="none" />
        {p(1) >= 0 && <circle cx={lerp(X0, X1, u)} cy={lerp(y5, y17, u)} r={16} fill="#fff" />}
      </svg>
      <T x={X0} y={930} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={28} color="#C9CED8">2005</Eti>
      </T>
      <T x={X1} y={930} ancla="d" op={tr(p(1), 30, 8)}>
        <Eti tam={28} color="#C9CED8">2015</Eti>
      </T>
      <T x={X0 + 10} y={y5 - 80} ancla="i" s={pop(p(1) - 2, 11, 1.4)}>
        <Cifra tam={96} color="blanco">5,5 %</Cifra>
      </T>
      <T x={X1 + 20} y={y17 - 20} ancla="i" s={pop(p(2), 12, 1.5)}>
        <Cifra tam={130} color="cian">17 %</Cifra>
      </T>
      <T x={1420} y={250} op={tr(p(3), 0, 8)}>
        <Eti tam={28} color="#C9CED8">Ventas de Primark</Eti>
      </T>
      <div style={{position: 'absolute', left: 1180, top: 880 - 90 * c01(b * 3), width: 170, height: 90 * c01(b * 3), borderRadius: 12, background: 'linear-gradient(180deg,#5C6375,#2F3442)'}} />
      <div style={{position: 'absolute', left: 1480, top: 880 - 522 * b, width: 170, height: 522 * b, borderRadius: 12, background: 'linear-gradient(180deg,#FFD95A,#F29A0B)'}} />
      <T x={1265} y={930} op={tr(p(3), 0, 8)}>
        <Eti tam={28} color="#C9CED8">2005</Eti>
      </T>
      <T x={1565} y={930} op={tr(p(3), 20, 8)}>
        <Eti tam={28} color="#C9CED8">2016</Eti>
      </T>
      <T x={1290} y={420} s={pop(p(4), 13, 1.6)} rot={-4}>
        <Cifra tam={200} color="ambar">×6</Cifra>
      </T>
      <T x={1290} y={545} op={tr(p(4), 8, 8)}>
        <Sans tam={34} peso={700} color="#D5DBE6">casi</Sans>
      </T>
      </div>
      <Sello x={960} y={610} t={p(5)} tam={104} rot={-5} color={CIAN}>Sin una sola venta online</Sello>
    </AbsoluteFill>
  );
};

/** La Gran Via de Madrid: cinco plantas, 12.400 m2, mas de cinco millones de compras al ano. */
export const GranVia: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = deriva(t, 0, dur, 44, 0.07);
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.4} blur={9} />
      <Tit t={t} y={96} tam={64} op={1 - tr(p(1), -4, 8)}>Tiendas enormes, justo por donde pasa todo el mundo</Tit>
      <T x={150} y={110} ancla="i" op={tr(p(1), 0, 8)}>
        <Eti tam={30} color={CIAN}>Madrid</Eti>
      </T>
      <Detras x={620} y={300} t={p(1)} tam={300}>Gran Vía</Detras>
      <Im src="g_tienda_p" x={620} y={1130} w={840} t={p(1) - 4} de="aba" cam={cam} />
      <Dato x={1500} y={290} t={p(2)} cifra="5" pie="plantas" tam={190} />
      <Dato x={1500} y={570} t={p(3)} cifra="+12.000 m²" pie="de tienda" tam={116} color="blanco" />
      <Dato x={1500} y={830} t={p(4)} cifra="+5 millones" pie="de compras al año" tam={112} color="ambar" />
    </AbsoluteFill>
  );
};

/** Espana: desde 2006, segundo mercado, mas de 1.900 M EUR. Y un margen de casi el 12 %. */
export const Espana: React.FC<EP> = (ep) => {
  const {t, p, dur} = ep;
  const cam = camara(t, [
    [0, 900, 820, 2.3],
    [dur, 880, 850, 2.6],
  ]);
  const a = 1 - tr(p(4), -4, 8);
  return (
    <AbsoluteFill>
      <Escenario cam={cam} />
      <Mundo cam={cam}>
        <Mapa x={MX} y={MY} k={MK} estilo={(c) => (c === 'ESP' ? {fill: '#0B5E86', borde: CIAN} : undefined)} />
      </Mundo>
      <Hoja x={1180} y={210} anio="2006" s={1.2 * pop(p(1), 12, 1.5) * (a > 0 ? 1 : 0)} color="cian" op={a} />
      <T x={1320} y={210} ancla="i" op={tr(p(1), 4, 8) * a}>
        <Serif tam={66} peso={600}>Entra en España</Serif>
      </T>
      <T x={1110} y={430} ancla="i" s={pop(p(2), 12, 1.4)} op={a}>
        <Chip tam={54} color="cian">Su 2.º mercado</Chip>
      </T>
      <Dato x={1110} y={690} t={p(3)} cifra="+1.900 M€" pie="en ventas" tam={136} color="ambar" ancla="i" op={a} />
      <T x={1470} y={300} op={tr(p(4), 0, 8)}>
        <Eti tam={30} color="#C9CED8">Margen de explotación de Primark</Eti>
      </T>
      <Dato x={1470} y={540} t={p(4)} cifra="≈ 12 %" pie="hasta el año pasado (11,9 %)" tam={220} />
    </AbsoluteFill>
  );
};

/** Asos, que solo vende por internet: en perdidas, y mas de 300 M EUR el ano anterior. */
export const AsosPierde: React.FC<EP> = (ep) => {
  const {t, p} = ep;
  return (
    <AbsoluteFill>
      <Fondo ep={ep} luz={0.28} />
      <Tit t={t} y={110} tam={76}>Compáralo con quien <Am>solo</Am> vende por internet</Tit>
      <Im src="g_paquete" x={300} y={1060} w={520} t={p(1) - 4} de="izq" z={1.2} />
      <Im src="g_paquete" x={690} y={980} w={340} t={p(1)} de="aba" flip luz={0.55} blur={2} z={0.6} />
      <T x={470} y={400} s={pop(p(1), 12, 1.4)}>
        <Chip tam={110} fondo="#F4F5F7" tinta="#0B0C10">Asos</Chip>
      </T>
      <Dato x={1340} y={380} t={p(2)} cifra="En pérdidas" pie="último ejercicio, sin contar la venta de dos almacenes" tam={130} color="rojo" />
      <Dato x={1340} y={760} t={p(3)} cifra="+300 M€" pie="de pérdidas el año anterior" tam={220} color="rojo" />
    </AbsoluteFill>
  );
};

export const PRIMARK1 = {web: Web, gigante: Gigante, pandemia: Pandemia, cuentas: Cuentas, bason: Bason, viaje: Viaje, cuarenta_dos: CuarentaDos, devoluciones: Devoluciones, portsmouth: Portsmouth, dos_maneras: DosManeras, asos: Asos, contrario: Contrario, seis: Seis, gran_via: GranVia, espana: Espana, asos_pierde: AsosPierde};
export {rebote};
