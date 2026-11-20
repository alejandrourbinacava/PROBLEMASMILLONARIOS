import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame} from 'remotion';

/**
 * Prueba del estilo VOX por capas (ver parallax2/ESTILO_VOX.md): una mesa de
 * papel con tres pruebas —recorte del periodico del canal, ticket de caja y
 * grafico— y una camara que viaja de una a otra. Las marcas se dibujan a
 * 12 fps; la camara va fluida.
 */
const W = 1920;
const H = 1080;
const TINTA = '#131313';
const AMARILLO = '#FFF200';
const ROJO = '#D0261E';

// ---------------------------------------------------------------- fuentes
const CARAS: [string, string, string?][] = [
  ['V Playfair', 'vox/fonts/PlayfairDisplay-VF.ttf', '400 900'],
  ['V Old', 'vox/fonts/OldStandard-Regular.ttf'],
  ['V OldI', 'vox/fonts/OldStandard-Italic.ttf'],
  ['V Franklin', 'vox/fonts/LibreFranklin-VF.ttf', '100 900'],
  ['V Caveat', 'vox/fonts/Caveat-VF.ttf', '400 700'],
  ['V Courier', 'vox/fonts/CourierPrime-Regular.ttf'],
  ['V CourierB', 'vox/fonts/CourierPrime-Bold.ttf'],
];
let cargadas: Promise<void> | null = null;
const useFuentes = () => {
  const [ok, setOk] = useState(false);
  const [h] = useState(() => delayRender('fuentes vox'));
  useEffect(() => {
    if (!cargadas) {
      cargadas = Promise.all(
        CARAS.map(async ([n, r, peso]) => {
          const f = new FontFace(n, `url(${staticFile(r)})`, peso ? {weight: peso} : {});
          await f.load();
          (document as any).fonts.add(f);
        }),
      ).then(() => undefined);
    }
    cargadas.then(() => {
      setOk(true);
      continueRender(h);
    });
  }, [h]);
  return ok;
};

// ---------------------------------------------------------------- utilidades
const c01 = (u: number) => Math.min(1, Math.max(0, u));
const suave = (u: number) => 1 - Math.pow(1 - c01(u), 3);
const inout = (u: number) => {
  const x = c01(u);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
const atras = (u: number, k = 1.6) => {
  const x = c01(u) - 1;
  return 1 + (k + 1) * x * x * x + k * x * x;
};
/** Fotograma "a doses": lo dibujado se mueve a 12 fps. */
const a12 = (f: number) => Math.floor(f / 2) * 2;
const ruido = (n: number) => {
  const s = Math.sin(n * 127.1) * 43758.5453;
  return s - Math.floor(s);
};

// ---------------------------------------------------------------- marcas a mano
/** Escala un trazo escrito en una caja de 100 x 100 al tamano real en pixeles. */
const escala = (d: string, sx: number, sy: number) =>
  d.replace(/(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)/g, (_, x, y) => `${(Number(x) * sx).toFixed(1)},${(Number(y) * sy).toFixed(1)}`);

/**
 * Trazo que se dibuja: `u` de 0 a 1. Se mide a si mismo para dibujar en
 * pixeles reales: con la caja estirada el grosor salia desigual y el
 * punteado del revelado se rompia.
 */
const Trazo: React.FC<{d: string; u: number; color?: string; w?: number; style?: React.CSSProperties}> = ({d, u, color = ROJO, w = 5, style}) => {
  const ref = useRef<SVGSVGElement>(null);
  const [t, setT] = useState<[number, number] | null>(null);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const a = el.clientWidth;
    const b = el.clientHeight;
    if (a && b && (!t || Math.abs(t[0] - a) > 0.5 || Math.abs(t[1] - b) > 0.5)) setT([a, b]);
  });
  return (
    <svg ref={ref} style={{position: 'absolute', overflow: 'visible', pointerEvents: 'none', ...style}}>
      {t && (
        <path d={escala(d, t[0] / 100, t[1] / 100)} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - c01(u)} />
      )}
    </svg>
  );
};

/** Texto con subrayador amarillo que avanza. */
const Resalte: React.FC<{u: number; children: React.ReactNode}> = ({u, children}) => (
  <span style={{backgroundImage: `linear-gradient(${AMARILLO}, ${AMARILLO})`, backgroundRepeat: 'no-repeat', backgroundSize: `${c01(u) * 100}% 86%`, backgroundPosition: '0 60%', padding: '0 3px', margin: '0 -3px', boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone'}}>
    {children}
  </span>
);

/** Circulo de rotulador alrededor de lo que envuelve. */
const Rodea: React.FC<{u: number; children: React.ReactNode; color?: string}> = ({u, children, color = ROJO}) => (
  <span style={{position: 'relative', display: 'inline-block'}}>
    {children}
    <Trazo u={u} color={color} w={6} d="M6,54 C2,18 40,2 62,6 C96,10 102,46 92,70 C80,98 22,100 8,74 C0,58 6,30 30,16" style={{left: '-9%', top: '-22%', width: '118%', height: '144%'}} />
  </span>
);

// ---------------------------------------------------------------- papel
const Papel: React.FC<{x: number; y: number; w: number; h?: number; giro?: number; color?: string; children: React.ReactNode; entra: number; f: number; pad?: string; zig?: boolean}> = ({x, y, w, h, giro = 0, color = '#F3ECDA', children, entra, f, pad = '54px 64px', zig}) => {
  // el recorte cae y asienta con un giro, no se desvanece
  const u = atras((a12(f) - entra) / 10, 1.3);
  const visible = f >= entra;
  return (
    <div
      style={{
        position: 'absolute', left: x, top: y, width: w, height: h, padding: pad, background: color, color: TINTA,
        transform: `translateY(${(1 - u) * -90}px) rotate(${giro + (1 - u) * 5}deg) scale(${0.94 + 0.06 * u})`,
        opacity: visible ? 1 : 0,
        boxShadow: '7px 11px 0 rgba(30,22,8,0.20), 14px 22px 26px rgba(30,22,8,0.18)',
        filter: 'url(#rugoso)',
        clipPath: zig ? 'polygon(0 0,100% 0,100% calc(100% - 18px),96% 100%,92% calc(100% - 18px),88% 100%,84% calc(100% - 18px),80% 100%,76% calc(100% - 18px),72% 100%,68% calc(100% - 18px),64% 100%,60% calc(100% - 18px),56% 100%,52% calc(100% - 18px),48% 100%,44% calc(100% - 18px),40% 100%,36% calc(100% - 18px),32% 100%,28% calc(100% - 18px),24% 100%,20% calc(100% - 18px),16% 100%,12% calc(100% - 18px),8% 100%,4% calc(100% - 18px),0 100%)' : undefined,
      }}
    >
      <svg width="100%" height="100%" style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'multiply', opacity: 0.55, pointerEvents: 'none'}}>
        <rect width="100%" height="100%" filter="url(#fibra)" />
      </svg>
      <div style={{position: 'relative'}}>{children}</div>
    </div>
  );
};

/** Un recorte de apoyo: solo lineas grises, desenfocado. */
const Apoyo: React.FC<{x: number; y: number; w: number; h: number; giro: number}> = ({x, y, w, h, giro}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: '#EDE5D0', transform: `rotate(${giro}deg)`, boxShadow: '5px 8px 0 rgba(30,22,8,0.14)', filter: 'blur(2.5px)', padding: 26, opacity: 0.9}}>
    <div style={{height: 22, background: '#3a3833', width: '70%', marginBottom: 16}} />
    {Array.from({length: Math.floor((h - 90) / 15)}).map((_, i) => (
      <div key={i} style={{height: 5, background: '#8f897b', marginBottom: 10, width: `${72 + ((i * 37) % 28)}%`}} />
    ))}
  </div>
);

// ---------------------------------------------------------------- las tres pruebas
const Periodico: React.FC<{f: number}> = ({f}) => {
  const g = a12(f);
  return (
    <Papel x={180} y={40} w={1560} giro={-1.4} entra={2} f={f}>
      <div style={{borderTop: `7px solid ${TINTA}`, borderBottom: `2px solid ${TINTA}`, padding: '10px 0 6px', textAlign: 'center'}}>
        <div style={{font: "900 84px/1 'V Playfair'", letterSpacing: 2}}>EL PRECIO DE SER EL DUEÑO</div>
      </div>
      <div style={{display: 'flex', justifyContent: 'space-between', font: "600 17px 'V Franklin'", letterSpacing: 3, textTransform: 'uppercase', padding: '8px 2px', borderBottom: `2px solid ${TINTA}`}}>
        <span>Nº 7 · Hostelería</span>
        <span>Noviembre de 2026</span>
        <span>Edición de barrio</span>
      </div>
      <div style={{font: "800 70px/1.04 'V Playfair'", margin: '26px 0 6px', letterSpacing: -0.5}}>
        Un café con leche cuesta 1,80 €. A la dueña le quedan{' '}
        <Rodea u={(g - 40) / 12}>quince céntimos</Rodea>
      </div>
      <div style={{font: "italic 27px/1.25 'V OldI'", color: '#3a3833', marginBottom: 18}}>
        Las cuentas de una cafetería de Viladecans, tal como las contó en El Español en julio de 2026
      </div>
      <div style={{columnCount: 3, columnGap: 40, columnRule: '1px solid #9a9486', font: "23px/1.34 'V Old'", textAlign: 'justify', hyphens: 'auto'}} lang="es">
        <p style={{margin: 0}}>
          <span style={{font: "900 60px/0.8 'V Playfair'", float: 'left', padding: '6px 8px 0 0'}}>U</span>na cafetería de barrio sirve el café con leche a un euro con ochenta. El café, la leche y el azúcar le cuestan al bar cincuenta y cinco céntimos por taza. El resto no es beneficio: se va en el alquiler del local, en los sueldos, en la luz y en todo lo que hace falta para levantar la persiana cada mañana.
        </p>
        <p style={{margin: '10px 0 0'}}>
          Hechas las cuentas, al final del año <Resalte u={(g - 58) / 16}>a la dueña le quedan unos quince céntimos de cada taza.</Resalte> No es una media: es un caso real, con nombre y con números.
        </p>
        <p style={{margin: '10px 0 0'}}>
          El local factura unos 138.000 euros al año y, de esa cifra, el 88 % se va antes de que ella cobre nada. Antes que la dueña cobran el casero, la cervecera, el ayuntamiento, los cobros y el camarero. Ella es la última de la fila.
        </p>
      </div>
    </Papel>
  );
};

const Linea: React.FC<{a: string; b: string; fuerte?: boolean}> = ({a, b, fuerte}) => (
  <div style={{display: 'flex', justifyContent: 'space-between', font: fuerte ? "28px/1.5 'V CourierB'" : "26px/1.5 'V Courier'"}}>
    <span>{a}</span>
    <span>{b}</span>
  </div>
);

const Ticket: React.FC<{f: number}> = ({f}) => {
  const g = a12(f);
  return (
    <>
      <Papel x={2760} y={120} w={620} giro={2.2} color="#FBFAF6" entra={92} f={f} pad="46px 44px 70px" zig>
        <div style={{textAlign: 'center', font: "34px/1.2 'V CourierB'", letterSpacing: 4}}>TICKET DE CAJA</div>
        <div style={{textAlign: 'center', font: "22px 'V Courier'", margin: '4px 0 14px'}}>BAR · MESA 3</div>
        <div style={{borderTop: `2px dashed ${TINTA}`, margin: '8px 0'}} />
        <Linea a="1 CAFÉ CON LECHE" b="1,80 €" fuerte />
        <div style={{borderTop: `2px dashed ${TINTA}`, margin: '8px 0 14px'}} />
        <div style={{font: "22px 'V Courier'", marginBottom: 6}}>ADÓNDE VA CADA EURO:</div>
        <Linea a="Café, leche, azúcar" b="0,55 €" />
        <Linea a="Alquiler, sueldos" b="" />
        <Linea a="  y todo lo demás" b="1,10 €" />
        <div style={{position: 'relative', marginTop: 10}}>
          <Linea a="LE QUEDA A LA DUEÑA" b="0,15 €" fuerte />
          <Trazo u={(g - 118) / 10} d="M2,60 Q30,30 60,56 T98,44" w={6} style={{left: '-2%', bottom: -16, width: '104%', height: 22}} />
          <Trazo u={(g - 128) / 8} d="M4,50 Q40,70 96,40" w={5} style={{left: '0%', bottom: -27, width: '100%', height: 20}} />
        </div>
        <div style={{borderTop: `2px dashed ${TINTA}`, margin: '34px 0 10px'}} />
        <div style={{textAlign: 'center', font: "20px 'V Courier'"}}>GRACIAS POR SU VISITA</div>
      </Papel>
      {/* anotacion a mano con su flecha */}
      <div style={{position: 'absolute', left: 3480, top: 500, width: 520, opacity: c01((g - 134) / 4)}}>
        <Trazo u={(g - 134) / 10} d="M96,30 C66,10 30,20 6,56 M6,56 L12,28 M6,56 L34,52" w={6} style={{left: -120, top: 30, width: 130, height: 90}} />
        <div style={{font: "700 64px/1 'V Caveat'", color: ROJO, transform: 'rotate(-4deg)'}}>esto es todo<br />lo que gana</div>
      </div>
      {/* la cita, en su tarjeta */}
      <Papel x={3440} y={150} w={640} giro={-2.5} color="#F3ECDA" entra={104} f={f} pad="38px 42px">
        <div style={{font: "italic 44px/1.16 'V OldI'"}}>«El 88 % se va antes de que ella cobre nada»</div>
        <div style={{font: "600 15px/1.4 'V Franklin'", letterSpacing: 2.5, textTransform: 'uppercase', marginTop: 16, color: '#55524b'}}>Caso de una cafetería de Viladecans<br />El Español · julio de 2026</div>
      </Papel>
    </>
  );
};

const Barra: React.FC<{y: number; etiqueta: string; valor: number; texto: string; color: string; t: number; destaca?: boolean; marca?: number}> = ({y, etiqueta, valor, texto, color, t, destaca, marca = 0}) => {
  const u = suave(t / 14);
  const ancho = (valor / 1.1) * 880 * u;
  return (
    <div style={{position: 'absolute', left: 0, top: y, width: 1400, opacity: c01(t / 3)}}>
      <div style={{font: "600 26px 'V Franklin'", marginBottom: 8, color: destaca ? ROJO : '#3a3833'}}>{etiqueta}</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
        <div style={{height: 78, width: Math.max(4, ancho), background: color}} />
        <div style={{font: "800 62px/1 'V Playfair'", color: destaca ? ROJO : TINTA}}>
          {destaca ? <Rodea u={marca} color={TINTA}>{texto}</Rodea> : texto}
        </div>
      </div>
    </div>
  );
};

const Grafico: React.FC<{f: number}> = ({f}) => {
  const g = a12(f);
  const t = g - 188;
  return (
    <div style={{position: 'absolute', left: 5000, top: 70, width: 1500, height: 940, color: TINTA, opacity: f >= 180 ? 1 : 0}}>
      <div style={{font: "800 76px/1.02 'V Playfair'", opacity: c01(t / 4), transform: `translateY(${(1 - suave(t / 8)) * 24}px)`}}>
        Adónde va un café de <Resalte u={(t - 8) / 10}>1,80 €</Resalte>
      </div>
      <div style={{font: "600 17px 'V Franklin'", letterSpacing: 2.6, textTransform: 'uppercase', color: '#6b675d', marginTop: 12, opacity: c01((t - 6) / 4)}}>
        Caso de una cafetería de Viladecans · El Español, julio de 2026
      </div>
      <div style={{position: 'absolute', left: 0, top: 230, width: 3, height: 560, background: TINTA, transform: `scaleY(${suave((t - 6) / 10)})`, transformOrigin: 'top'}} />
      <div style={{position: 'absolute', left: 26, top: 0, width: 1400, height: 900}}>
        <Barra y={250} etiqueta="Café, leche y azúcar" valor={0.55} texto="0,55 €" color="#A9A396" t={t - 14} />
        <Barra y={420} etiqueta="Alquiler, sueldos y todo lo demás" valor={1.1} texto="1,10 €" color="#55524B" t={t - 24} />
        <Barra y={590} etiqueta="Lo que le queda a la dueña" valor={0.15} texto="0,15 €" color={ROJO} t={t - 36} destaca marca={(t - 52) / 12} />
      </div>
      <div style={{position: 'absolute', left: 520, top: 760, opacity: c01((t - 60) / 4)}}>
        <Trazo u={(t - 60) / 10} d="M96,92 C90,40 60,14 8,10 M8,10 L34,6 M8,10 L26,34" w={6} style={{left: -150, top: -70, width: 140, height: 110}} />
        <div style={{font: "700 60px/1 'V Caveat'", color: ROJO, transform: 'rotate(-3deg)'}}>8 céntimos de cada euro</div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- camara
type Clave = {f: number; x: number; y: number; k: number; viaje?: boolean};
const CLAVES: Clave[] = [
  {f: 0, x: 960, y: 370, k: 0.96},
  {f: 82, x: 1000, y: 410, k: 1.22},
  {f: 100, x: 3420, y: 480, k: 0.98, viaje: true},
  {f: 170, x: 3450, y: 530, k: 1.14},
  {f: 190, x: 5730, y: 500, k: 0.98, viaje: true},
  {f: 279, x: 5700, y: 520, k: 1.07},
];
const camara = (f: number) => {
  let i = 0;
  while (i < CLAVES.length - 2 && f >= CLAVES[i + 1].f) i++;
  const a = CLAVES[i];
  const b = CLAVES[i + 1];
  const u0 = c01((f - a.f) / (b.f - a.f));
  const u = b.viaje ? inout(u0) : 1 - Math.pow(1 - u0, 1.6);
  const mix = (p: number, q: number) => p + (q - p) * u;
  // el desenfoque tiene su pico en mitad del viaje: ahi se esconde el corte
  const borr = b.viaje ? Math.sin(Math.PI * u0) * 22 : 0;
  return {x: mix(a.x, b.x), y: mix(a.y, b.y), k: mix(a.k, b.k), borr};
};

export const PruebaVox: React.FC = () => {
  const ok = useFuentes();
  const f = useCurrentFrame();
  if (!ok) return <AbsoluteFill style={{background: '#E9E0CC'}} />;
  const c = camara(f);
  const g = a12(f);
  // Sin temblor: una deriva lenta y continua, de un par de pixeles. El temblor
  // a doses (+-5 px y giro al azar) se leia como un fallo, no como camara en mano.
  const tx = Math.sin(f / 37) * 2.2;
  const ty = Math.cos(f / 29) * 1.6;
  const rot = 0;
  const mundo = (factor: number): React.CSSProperties => ({
    position: 'absolute', left: 0, top: 0, width: W, height: H, transformOrigin: '0 0',
    transform: `translate(${W / 2 + tx}px, ${H / 2 + ty}px) rotate(${rot}deg) scale(${1 + (c.k - 1) * factor}) translate(${-c.x * factor}px, ${-c.y * factor}px)`,
  });
  // la textura de la mesa cambia unas tres veces por segundo
  const semilla = 3 + (Math.floor(f / 8) % 5);
  return (
    <AbsoluteFill style={{background: '#E4DAC4', overflow: 'hidden'}}>
      <svg width={0} height={0} style={{position: 'absolute'}}>
        <defs>
          <filter id="rugoso" x="-3%" y="-3%" width="106%" height="106%">
            <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves={3} seed={7} result="r" />
            <feDisplacementMap in="SourceGraphic" in2="r" scale={5} />
          </filter>
          <filter id="fibra">
            <feTurbulence type="fractalNoise" baseFrequency="0.75 0.9" numOctaves={3} seed={11} />
            <feColorMatrix type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.3  0 0 0 0 0.2  0 0 0 -1.1 0.62" />
          </filter>
          <filter id="mesa">
            <feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves={4} seed={semilla} />
            <feColorMatrix type="matrix" values="0 0 0 0 0.42  0 0 0 0 0.34  0 0 0 0 0.2  0 0 0 -0.9 0.34" />
          </filter>
          <filter id="grano">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={(f % 7) + 1} />
            <feColorMatrix type="saturate" values="0" />
          </filter>
        </defs>
      </svg>

      {/* 1-2 · la mesa y su textura viva: se mueve menos que los papeles (parallax) */}
      <div style={{...mundo(0.35), filter: c.borr > 0.5 ? `blur(${c.borr * 0.4}px)` : undefined}}>
        <svg width={9000} height={2600} style={{position: 'absolute', left: -1500, top: -700}}>
          <rect width="100%" height="100%" fill="#E4DAC4" />
          <rect width="100%" height="100%" filter="url(#mesa)" />
        </svg>
      </div>

      {/* 3-6 · los papeles, las marcas y los rotulos */}
      <div style={{...mundo(1), filter: c.borr > 0.5 ? `blur(${c.borr}px)` : undefined}}>
        <Apoyo x={-420} y={-180} w={560} h={640} giro={-9} />
        <Apoyo x={1690} y={560} w={600} h={520} giro={7} />
        <Apoyo x={2280} y={-260} w={520} h={560} giro={-6} />
        <Apoyo x={4160} y={480} w={620} h={560} giro={5} />
        <Apoyo x={4380} y={-300} w={560} h={480} giro={-8} />
        <Apoyo x={6560} y={180} w={540} h={620} giro={6} />
        <Periodico f={f} />
        <Ticket f={f} />
        <Grafico f={f} />
      </div>

      {/* 7 · lente: vineta y grano por encima de todo */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(40,28,8,0) 52%, rgba(40,28,8,0.34) 100%)'}} />
      <svg width={W} height={H} style={{position: 'absolute', mixBlendMode: 'multiply', opacity: 0.16}}>
        <rect width="100%" height="100%" filter="url(#grano)" />
      </svg>
    </AbsoluteFill>
  );
};
