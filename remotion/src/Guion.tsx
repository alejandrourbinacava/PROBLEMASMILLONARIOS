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

export type Capa = {
  id: string;
  src: string;
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
          capa.texto ? (
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
        style={{
          width: '100%',
          height: '100%',
          // contain para las capas con alfa -un sujeto recortado no se puede
          // recortar mas- y cover para los fondos, que tienen que cubrir.
          objectFit: capa.principal ? 'contain' : 'cover',
          filter: aFiltro(capa.grade),
        }}
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
  const sombra = tipografia.sombra ?? {desenfoque: 24, opacidad: 0.5};

  return (
    <AbsoluteFill
      style={{
        transform: `translate3d(${x}px, ${y}px, ${capa.z}px) scale(${compensar(capa.z)})`,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          maxWidth: '80%',
          textAlign: 'center',
          fontFamily: `'${tipografia.familia}', Poppins, sans-serif`,
          fontWeight: 900,
          fontSize: Math.round(ancho * 0.055),
          lineHeight: 1.04,
          letterSpacing: `${tipografia.tracking ?? 0}em`,
          textTransform: (tipografia.transform as 'uppercase') ?? 'none',
          color: tipografia.color ?? '#fff',
          textShadow: `0 10px ${sombra.desenfoque}px rgba(0,0,0,${sombra.opacidad})`,
          opacity: opacidad,
          transform: `scale(${escalaTexto})`,
        }}
      >
        {capa.texto}
      </div>
    </AbsoluteFill>
  );
};
