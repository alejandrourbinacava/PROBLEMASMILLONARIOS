import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

// ---------------------------------------------------------------------------
// El formato de escenas.json, tal cual
// ---------------------------------------------------------------------------

export type Grade = {
  saturacion?: number;
  brillo?: number;
  contraste?: number;
  tinte?: string;
  tinteFuerza?: number;
  desenfoque?: number;
};

export type Contador = {
  de: number;
  a: number;
  decimales?: number;
  frames?: number;
};

export type Capa = {
  id: string;
  /** null en las capas de texto: no todas las capas son una imagen. */
  src?: string | null;
  tipo?: string;
  contenido?: string;
  contador?: Contador;
  anclaje?: string;
  sombra?: {desenfoque?: number; opacidad?: number};
  /** Altura del sujeto sobre el alto del encuadre. En MagnatesMedia el sujeto
   *  domina: 0,6-0,7, no el 0,45 que salia al dejarlo en `contain`. */
  escala_alto?: number;
  /** Posicion horizontal, en fraccion de ancho. Descentrado -0,3 a 0,4- para
   *  que el fondo respire por el otro lado. */
  posicion_x?: number;
  /** Donde va un rotulo: "inferior" lo baja para que no cruce al sujeto. */
  posicion?: string;
  /** Ancho maximo del rotulo, en fraccion del ancho de composicion. El texto
   *  se encoge hasta caber: mas vale una letra mas pequena que una palabra
   *  cortada por el borde. */
  ancho_max?: number;
  z: number;
  principal?: boolean;
  zoom?: number[];
  x?: number[];
  y?: number[];
  opacidad?: number[];
  texto?: string;
  grade?: Grade;
};

export type EscenaSpec = {
  id: string;
  duracion: number;
  preset?: string;
  horizonte?: number;
  luz?: string;
  camara?: {zoom?: number[]; x?: number[]; y?: number[]};
  capas: Capa[];
};

export type Tipografia = {
  familia: string;
  transform?: string;
  tracking?: number;
  color?: string;
  sombra?: {desenfoque: number; opacidad: number};
  entrada?: {frames: number; escala: number[]; opacidad: number[]};
};

export type GuionSpec = {
  proyecto: string;
  fps: number;
  ancho: number;
  alto: number;
  duracion_total: number;
  tipografia: Tipografia;
  escenas: EscenaSpec[];
};

export type GuionProps = {
  spec: GuionSpec;
  /** Carpeta dentro de public/ donde estan los PNG de las capas. */
  carpeta: string;
  audio?: string;
};

/**
 * Distancia del ojo al plano cero.
 *
 * El JSON reparte las z entre -800 y 0. Con una perspectiva de 1200, una capa
 * a -800 se veria al 60% de su tamano, asi que hay que compensar; la formula
 * esta en `compensar`. Lo que sobrevive a esa compensacion, y es todo el
 * efecto, es la diferencia de VELOCIDAD entre capas al mover la camara.
 */
const PERSPECTIVA = 1200;
const compensar = (z: number) => (PERSPECTIVA - z) / PERSPECTIVA;

const CURVA = Easing.bezier(0.33, 0, 0.2, 1);

const entre = (par: number[] | undefined, avance: number, porDefecto = 0) =>
  par && par.length >= 2 ? par[0] + (par[1] - par[0]) * avance : porDefecto;

/** Traduce el bloque `grade` del JSON a un filtro CSS. */
const aFiltro = (g?: Grade): string | undefined => {
  if (!g) return undefined;
  const partes: string[] = [];
  if (g.brillo !== undefined) partes.push(`brightness(${g.brillo})`);
  if (g.contraste !== undefined) partes.push(`contrast(${g.contraste})`);
  if (g.saturacion !== undefined) partes.push(`saturate(${g.saturacion})`);
  if (g.desenfoque) partes.push(`blur(${g.desenfoque}px)`);
  return partes.length ? partes.join(' ') : undefined;
};

export const Guion: React.FC<GuionProps> = ({spec, carpeta, audio}) => {
  let cursor = 0;
  const tramos = spec.escenas.map((escena) => {
    const desde = cursor;
    cursor += escena.duracion;
    return {escena, desde};
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {audio ? <Audio src={staticFile(audio)} /> : null}
      {tramos.map(({escena, desde}) => (
        <Sequence
          key={escena.id}
          from={desde}
          durationInFrames={escena.duracion}
          layout="none"
        >
          <Escena escena={escena} carpeta={carpeta} tipografia={spec.tipografia} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const Escena: React.FC<{
  escena: EscenaSpec;
  carpeta: string;
  tipografia: Tipografia;
}> = ({escena, carpeta, tipografia}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();

  const avance = interpolate(frame, [0, Math.max(1, escena.duracion - 1)], [0, 1], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const cam = escena.camara ?? {};
  const camZoom = entre(cam.zoom, avance, 1);
  const camX = entre(cam.x, avance);
  const camY = entre(cam.y, avance);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#08080b',
        perspective: `${PERSPECTIVA}px`,
        perspectiveOrigin: '50% 50%',
        overflow: 'hidden',
      }}
    >
      {/* La camara mueve el contenedor. Al animar el padre, cada z produce su
          propio recorrido y el parallax sale con las proporciones correctas. */}
      <AbsoluteFill
        style={{
          transformStyle: 'preserve-3d',
          transform: `translate3d(${camX}px, ${camY}px, 0) scale(${camZoom})`,
        }}
      >
        {escena.capas.map((capa) =>
          // Una capa es texto cuando no trae imagen. Mirar solo `texto` dejaba
          // fuera las de tipo texto_grande, que traen `contenido` y src null, y
          // el render moria pidiendo un fichero llamado "null".
          !capa.src ? (
            <Rotulo
              key={capa.id}
              capa={capa}
              avance={avance}
              frame={frame}
              ancho={width}
              tipografia={tipografia}
            />
          ) : (
            <CapaImagen key={capa.id} capa={capa} carpeta={carpeta} avance={avance} />
          )
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const CapaImagen: React.FC<{capa: Capa; carpeta: string; avance: number}> = ({
  capa,
  carpeta,
  avance,
}) => {
  const zoom = entre(capa.zoom, avance, 1);
  const x = entre(capa.x, avance);
  const y = entre(capa.y, avance);
  const opacidad = capa.opacidad ? entre(capa.opacidad, avance, 1) : 1;

  // Margen extra sobre la compensacion: la capa se desplaza con su propio x/y
  // y con el de la camara, y sin holgura asomaria el borde del PNG.
  const escala = compensar(capa.z) * zoom * 1.12;

  // Un sujeto con escala_alto se coloca por altura y posicion, no estirado
  // sobre el encuadre: asi domina el plano y queda descentrado, que es como lo
  // hacen ellos. Sin estos campos, `contain` lo deja centrado y pequeno.
  const colocado = capa.escala_alto !== undefined || capa.posicion_x !== undefined;

  return (
    <AbsoluteFill
      style={{
        transform: `translate3d(${x}px, ${y}px, ${capa.z}px) scale(${escala})`,
        transformStyle: 'preserve-3d',
        opacity: opacidad,
      }}
    >
      <Img
        src={staticFile(`${carpeta}/${capa.src}`)}
        style={
          colocado
            ? {
                position: 'absolute',
                bottom: 0,
                left: `${(capa.posicion_x ?? 0.5) * 100}%`,
                height: `${(capa.escala_alto ?? 0.65) * 100}%`,
                width: 'auto',
                objectFit: 'contain',
                transform: 'translateX(-50%)',
                filter: aFiltro(capa.grade),
              }
            : {
                width: '100%',
                height: '100%',
                // contain para las capas con alfa y cover para los fondos,
                // que tienen que cubrir el encuadre.
                objectFit: capa.principal ? 'contain' : 'cover',
                filter: aFiltro(capa.grade),
              }
        }
      />
      {/* El tinte va en su propia capa multiplicada encima, no en el filtro:
          CSS no tiene un filtro de tinte y hacerlo con hue-rotate desplaza
          tambien los colores que ya estaban bien. */}
      {capa.grade?.tinte && capa.grade.tinteFuerza ? (
        <AbsoluteFill
          style={{
            backgroundColor: capa.grade.tinte,
            opacity: capa.grade.tinteFuerza,
            mixBlendMode: 'color',
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};

/** Formatea el valor de un contador con la coma decimal espanola. */
const cifra = (valor: number, decimales: number, plantilla?: string) => {
  const numero = valor.toFixed(decimales).replace(".", ",");
  // Si el contenido trae un sufijo -"2,7%"- se conserva: lo que cuenta es el
  // numero, no el simbolo que lo acompana.
  const sufijo = plantilla ? plantilla.replace(/[\d.,]/g, "") : "";
  return numero + sufijo;
};

const Rotulo: React.FC<{
  capa: Capa;
  avance: number;
  frame: number;
  ancho: number;
  tipografia: Tipografia;
}> = ({capa, avance, frame, ancho, tipografia}) => {
  const ent = tipografia.entrada ?? {frames: 6, escala: [1.04, 1], opacidad: [0, 1]};
  const [escIni, escFin] = [ent.escala[0] ?? 1.04, ent.escala[1] ?? 1];
  const [opaIni, opaFin] = [ent.opacidad[0] ?? 0, ent.opacidad[1] ?? 1];
  const t = interpolate(frame, [0, ent.frames], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const escalaTexto = escIni + (escFin - escIni) * t;
  const opacidad = opaIni + (opaFin - opaIni) * t;

  const x = entre(capa.x, avance);
  const y = entre(capa.y, avance);
  const sombra = {
    desenfoque: capa.sombra?.desenfoque ?? tipografia.sombra?.desenfoque ?? 24,
    opacidad: capa.sombra?.opacidad ?? tipografia.sombra?.opacidad ?? 0.5,
  };

  // Un texto grande ocupa el doble y ademas se acerca durante el plano: es la
  // cifra la que lleva el peso del argumento, no un rotulo de apoyo.
  const grande = capa.tipo === "texto_grande";
  const zoomTexto = entre(capa.zoom, avance, 1);

  // El cuerpo de letra se reduce hasta que el texto cabe en ancho_max. La
  // estimacion usa 0,52 em por caracter, que es lo que mide una tipografia
  // negra en mayusculas; no es exacta, pero se queda del lado seguro y el
  // maxWidth de abajo remata lo que se escape.
  const anchoMax = capa.ancho_max ?? 0.8;
  const cuerpoBase = ancho * (grande ? 0.13 : 0.055);
  const contenidoTexto = capa.texto ?? capa.contenido ?? "";
  const lineaMasLarga = contenidoTexto
    .split("\n")
    .reduce((a, b) => (a.length > b.length ? a : b), "");
  const anchoEstimado = lineaMasLarga.length * cuerpoBase * 0.52;
  const limite = ancho * anchoMax;
  const cuerpo = anchoEstimado > limite
    ? Math.max(cuerpoBase * 0.55, cuerpoBase * (limite / anchoEstimado))
    : cuerpoBase;

  let contenido = capa.texto ?? capa.contenido ?? "";
  if (capa.contador) {
    const t = interpolate(frame, [0, capa.contador.frames ?? 40], [0, 1], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    const valor = capa.contador.de + (capa.contador.a - capa.contador.de) * t;
    contenido = cifra(valor, capa.contador.decimales ?? 0, capa.contenido);
  }

  return (
    <AbsoluteFill
      style={{
        transform: `translate3d(${x}px, ${y}px, ${capa.z}px) scale(${compensar(capa.z)})`,
        // "inferior" baja el rotulo para que no cruce el pecho del sujeto: si
        // el texto es lo mas brillante y ademas pasa por encima de la figura,
        // el ojo va al texto y el sujeto deja de existir.
        justifyContent: capa.posicion === 'inferior' ? 'flex-end' : 'center',
        alignItems: 'center',
        paddingBottom: capa.posicion === 'inferior' ? '7%' : 0,
      }}
    >
      <div
        style={{
          maxWidth: `${anchoMax * 100}%`,
          textAlign: 'center',
          fontFamily: `'${tipografia.familia}', Poppins, sans-serif`,
          fontWeight: 900,
          fontSize: Math.round(cuerpo),
          lineHeight: 1.04,
          letterSpacing: `${tipografia.tracking ?? 0}em`,
          textTransform: (tipografia.transform as 'uppercase') ?? 'none',
          color: tipografia.color ?? '#fff',
          textShadow: `0 10px ${sombra.desenfoque}px rgba(0,0,0,${sombra.opacidad})`,
          opacity: opacidad,
          transform: `scale(${escalaTexto * zoomTexto})`,
        }}
      >
        {contenido}
      </div>
    </AbsoluteFill>
  );
};
