import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

/**
 * Los graficos del canal. Todos comparten tres reglas:
 *
 *   - Fondo negro casi puro. La cifra tiene que ser lo unico que hay.
 *   - Nada aparece de golpe: cada elemento entra con su retardo.
 *   - La animacion siempre va con interpolate sobre el frame. Ninguna
 *     transicion de CSS, que en un render por fotogramas no existe.
 */

export type Tipografia = {
  familia: string;
  color?: string;
  tracking?: number;
  sombra?: {desenfoque?: number; opacidad?: number};
};

export type ContenidoGrafico = {
  cifra?: number;
  prefijo?: string;
  decimales?: number;
  pie?: string;
  titulo?: string;
  linea?: string;
  barras?: {etiqueta: string; min?: number; max?: number; valor?: number}[];
  columnas?: {titulo: string; lineas: string[]}[];
  conceptos?: {etiqueta: string; valor: string}[];
  total?: string;
};

export type GraficoProps = {
  variante: string;
  contenido: ContenidoGrafico;
  duracion: number;
  tipografia: Tipografia;
};

const AMBAR = '#E9A13B';
const CURVA = Easing.out(Easing.cubic);

/** Separador de miles con punto, como se escribe en espanol. */
const miles = (valor: number, decimales = 0) => {
  const fijo = valor.toFixed(decimales);
  const [entera, decimal] = fijo.split('.');
  const conPuntos = entera.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return decimal ? `${conPuntos},${decimal}` : conPuntos;
};

const avance = (frame: number, desde: number, dura: number) =>
  interpolate(frame, [desde, desde + dura], [0, 1], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

export const Grafico: React.FC<GraficoProps> = (props) => {
  const {variante} = props;
  if (variante === 'contador') return <Contador {...props} />;
  if (variante === 'titulo' || variante === 'frase_destacada') return <Frase {...props} />;
  if (variante === 'barras_enfrentadas') return <Barras {...props} />;
  if (variante === 'comparativa_modelos') return <Columnas {...props} />;
  if (variante === 'lista_apilada') return <Lista {...props} />;
  // Si llega una variante que no existe, se ve NEGRO y se avisa en consola.
  // Es mejor que dibujar algo parecido: un plano en negro se detecta al
  // revisar, y un grafico inventado se cuela.
  console.warn(`Grafico: variante desconocida "${variante}"`);
  return <AbsoluteFill style={{backgroundColor: '#050506'}} />;
};

const base = (tipografia: Tipografia): React.CSSProperties => ({
  fontFamily: `'${tipografia.familia}', Poppins, sans-serif`,
  fontWeight: 900,
  color: tipografia.color ?? '#E8E2D8',
  letterSpacing: `${tipografia.tracking ?? -0.01}em`,
  textTransform: 'uppercase',
});

// ---------------------------------------------------------------------------

/**
 * La cifra sube digito a digito hasta el valor completo.
 *
 * Ver llenarse los nueve digitos ES el efecto, asi que el ancho se reserva
 * desde el primer fotograma: si la caja creciera con el numero, el texto
 * bailaria de sitio y se perderia justamente eso.
 */
const Contador: React.FC<GraficoProps> = ({contenido, duracion, tipografia}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();

  const cuenta = avance(frame, 0, 40);
  const valor = (contenido.cifra ?? 0) * cuenta;
  const texto = `${contenido.prefijo ?? ''}${miles(valor, contenido.decimales ?? 0)}`;
  const completo = `${contenido.prefijo ?? ''}${miles(contenido.cifra ?? 0, contenido.decimales ?? 0)}`;

  const cuerpo = (width * 0.4) / Math.max(1, completo.length * 0.56);
  const entradaPie = avance(frame, 42, 12);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#050506',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
      }}
    >
      <div style={{position: 'relative'}}>
        {/* Fantasma del numero completo: reserva el ancho para que la cifra
            no se desplace mientras cuenta. */}
        <div style={{...base(tipografia), fontSize: cuerpo, opacity: 0, whiteSpace: 'nowrap'}}>
          {completo}
        </div>
        <div
          style={{
            ...base(tipografia),
            fontSize: cuerpo,
            position: 'absolute',
            inset: 0,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            whiteSpace: 'nowrap',
            textShadow: '0 8px 40px rgba(0,0,0,0.8)',
          }}
        >
          {texto}
        </div>
      </div>

      {contenido.pie ? (
        <div
          style={{
            ...base(tipografia),
            fontSize: width * 0.017,
            marginTop: width * 0.018,
            letterSpacing: '0.06em',
            color: AMBAR,
            opacity: entradaPie,
            transform: `translateY(${(1 - entradaPie) * 14}px)`,
          }}
        >
          {contenido.pie}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------

/** Una frase sola sobre negro. Para los titulos y los golpes de guion. */
const Frase: React.FC<GraficoProps> = ({contenido, tipografia}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const t = avance(frame, 0, 8);
  const texto = contenido.titulo ?? contenido.linea ?? '';
  const cuerpo = Math.min(width * 0.062, (width * 0.86) / Math.max(1, texto.length * 0.5));

  return (
    <AbsoluteFill
      style={{backgroundColor: '#050506', justifyContent: 'center', alignItems: 'center'}}
    >
      <div
        style={{
          ...base(tipografia),
          fontSize: cuerpo,
          maxWidth: '86%',
          textAlign: 'center',
          lineHeight: 1.06,
          opacity: t,
          transform: `scale(${1.04 - 0.04 * t})`,
          textShadow: '0 10px 44px rgba(0,0,0,0.8)',
        }}
      >
        {texto}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------

/**
 * Barras horizontales que crecen desde la izquierda, una detras de otra.
 *
 * La escala la fija SIEMPRE el valor mayor de la tanda, no cada barra por su
 * cuenta: si cada una se normalizara a si misma, todas llegarian al mismo
 * sitio y la comparacion -que es el argumento- desapareceria.
 */
const Barras: React.FC<GraficoProps> = ({contenido, tipografia}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const barras = contenido.barras ?? [];
  const tope = Math.max(...barras.map((b) => b.max ?? b.valor ?? 0), 1);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#050506',
        justifyContent: 'center',
        padding: `0 ${width * 0.07}px`,
      }}
    >
      {barras.map((barra, indice) => {
        const t = avance(frame, indice * 20, 22);
        const desde = (barra.min ?? 0) / tope;
        const hasta = (barra.max ?? barra.valor ?? 0) / tope;
        const etiqueta = avance(frame, indice * 20, 10);
        const rango = barra.min !== undefined && barra.max !== undefined;

        return (
          <div key={barra.etiqueta} style={{marginBottom: width * 0.026}}>
            <div
              style={{
                ...base(tipografia),
                fontSize: width * 0.019,
                letterSpacing: '0.05em',
                opacity: etiqueta,
                marginBottom: width * 0.008,
              }}
            >
              {barra.etiqueta}
            </div>
            <div style={{position: 'relative', height: width * 0.032}}>
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  top: 0,
                  bottom: 0,
                  width: `${hasta * t * 100}%`,
                  background: `linear-gradient(90deg, ${AMBAR} 0%, #F2C57C 100%)`,
                }}
              />
              {/* En un rango, el minimo se marca con una linea: sin ella, la
                  barra sugiere que el coste es el maximo y no un intervalo. */}
              {rango && t > 0.6 ? (
                <div
                  style={{
                    position: 'absolute',
                    left: `${desde * 100}%`,
                    top: -4,
                    bottom: -4,
                    width: 3,
                    backgroundColor: '#050506',
                  }}
                />
              ) : null}
            </div>
            <div
              style={{
                ...base(tipografia),
                fontSize: width * 0.021,
                marginTop: width * 0.006,
                color: AMBAR,
                opacity: avance(frame, indice * 20 + 12, 10),
              }}
            >
              {rango
                ? `${contenido.prefijo ?? ''}${miles((barra.min ?? 0) / 1e6)} – ${contenido.prefijo ?? ''}${miles((barra.max ?? 0) / 1e6)} M`
                : `${contenido.prefijo ?? ''}${miles(barra.valor ?? 0)}`}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------

/** Dos columnas que se construyen a la vez, linea a linea. */
const Columnas: React.FC<GraficoProps> = ({contenido, tipografia}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const columnas = contenido.columnas ?? [];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#050506',
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        gap: width * 0.09,
      }}
    >
      {columnas.map((columna) => (
        <div key={columna.titulo} style={{minWidth: width * 0.27}}>
          <div
            style={{
              ...base(tipografia),
              fontSize: width * 0.028,
              color: AMBAR,
              opacity: avance(frame, 0, 10),
              marginBottom: width * 0.022,
            }}
          >
            {columna.titulo}
          </div>
          {columna.lineas.map((linea, indice) => {
            const t = avance(frame, 14 + indice * 14, 10);
            return (
              <div
                key={`${linea}-${indice}`}
                style={{
                  ...base(tipografia),
                  fontSize: width * 0.022,
                  lineHeight: 1.9,
                  opacity: t,
                  transform: `translateX(${(1 - t) * 18}px)`,
                }}
              >
                {linea}
              </div>
            );
          })}
        </div>
      ))}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------

/**
 * La lista de gastos que se apila. Las partidas ya puestas se atenuan y la
 * nueva entra encendida: es la que cuenta la historia del canal, como el
 * dinero se va yendo linea a linea.
 */
const Lista: React.FC<GraficoProps> = ({contenido, duracion, tipografia}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const conceptos = (contenido.conceptos ?? []).slice(0, 5);
  const cierre = avance(frame, duracion - 40, 16);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#050506',
        justifyContent: 'center',
        padding: `0 ${width * 0.09}px`,
      }}
    >
      {conceptos.map((concepto, indice) => {
        const t = avance(frame, indice * 22, 12);
        const ultima = indice === conceptos.length - 1;
        return (
          <div
            key={concepto.etiqueta}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              opacity: t * (ultima ? 1 : 1 - 0.45 * cierre),
              transform: `translateY(${(1 - t) * 16}px)`,
              marginBottom: width * 0.017,
            }}
          >
            <span style={{...base(tipografia), fontSize: width * 0.024}}>
              {concepto.etiqueta}
            </span>
            <span style={{...base(tipografia), fontSize: width * 0.027, color: AMBAR}}>
              {concepto.valor}
            </span>
          </div>
        );
      })}

      {contenido.total ? (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline',
            marginTop: width * 0.03,
            paddingTop: width * 0.02,
            borderTop: `2px solid rgba(233,161,59,${cierre * 0.8})`,
            opacity: cierre,
            // Un parpadeo unico al aparecer el total: llama la atencion sin
            // convertirse en un efecto que se repite.
            filter: `brightness(${1 + Math.max(0, 1 - Math.abs(cierre - 0.6) * 8) * 0.8})`,
          }}
        >
          <span style={{...base(tipografia), fontSize: width * 0.028}}>Total</span>
          <span style={{...base(tipografia), fontSize: width * 0.042, color: AMBAR}}>
            {contenido.total}
          </span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
