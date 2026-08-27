import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {Grafico, ContenidoGrafico, Tipografia} from './Graficos';

// ---------------------------------------------------------------------------
// El formato de escenas_casino.json, tal cual
// ---------------------------------------------------------------------------

export type Grade = {
  saturacion?: number;
  brillo?: number;
  contraste?: number;
  tinte?: string;
  tinteFuerza?: number;
  desenfoque?: number;
};

export type Sombra = {
  angulo?: number;
  largo?: number;
  opacidad?: number;
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
  escala_alto?: number;
  posicion_x?: number;
  anclaje?: string;
  sombra?: Sombra;
  grade?: Grade;
};

export type TextoEscena = {
  linea: string;
  posicion?: string;
  ancho_max?: number;
  /** Ids de capas por DELANTE de las cuales va el texto. Lo que no esta en la
   *  lista queda por encima, que es como el sujeto tapa parte del rotulo. */
  delante_de?: string[];
  entrada_frame?: number;
};

export type EscenaSpec = {
  id: string;
  bloque?: string;
  tipo: string;
  patron?: string;
  variante?: string;
  duracion: number;
  horizonte?: number;
  camara?: {zoom?: number[]; x?: number[]; y?: number[]};
  capas?: Capa[];
  texto?: TextoEscena;
  contenido?: ContenidoGrafico;
  /** Clips: nombres de fichero ya descargados, en orden. */
  clips?: string[];
  grade?: Grade;
};

export type Patron = {
  tipo?: string;
  duracion?: number;
  variante?: string;
  grade?: Grade;
  texto?: {posicion?: string};
  sujeto?: {escala_alto?: number; posicion_x?: number; anclaje?: string};
};

export type EpisodioSpec = {
  proyecto: string;
  fps: number;
  ancho: number;
  alto: number;
  tipografia: Tipografia & {
    transform?: string;
    sombra?: {desenfoque?: number; opacidad?: number};
    entrada?: {frames: number; escala: number[]; opacidad: number[]};
  };
  patrones: Record<string, Patron>;
  escenas: EscenaSpec[];
};

export type EpisodioProps = {
  spec: EpisodioSpec;
  carpeta: string;
  audio?: string;
};

const PERSPECTIVA = 1200;
const compensar = (z: number) => (PERSPECTIVA - z) / PERSPECTIVA;
const CURVA = Easing.bezier(0.33, 0, 0.2, 1);

const entre = (par: number[] | undefined, t: number, porDefecto = 0) =>
  par && par.length >= 2 ? par[0] + (par[1] - par[0]) * t : porDefecto;

const aFiltro = (g?: Grade): string | undefined => {
  if (!g) return undefined;
  const partes: string[] = [];
  if (g.brillo !== undefined) partes.push(`brightness(${g.brillo})`);
  if (g.contraste !== undefined) partes.push(`contrast(${g.contraste})`);
  if (g.saturacion !== undefined) partes.push(`saturate(${g.saturacion})`);
  if (g.desenfoque) partes.push(`blur(${g.desenfoque}px)`);
  return partes.length ? partes.join(' ') : undefined;
};

/**
 * Sombra proyectada a partir del angulo y el largo que declara el guion.
 *
 * Se hace con drop-shadow y no con box-shadow porque el sujeto es un PNG
 * recortado: box-shadow dibujaria la sombra de la CAJA rectangular, no la de
 * la figura.
 */
const aSombra = (s: Sombra | undefined, alto: number): string | undefined => {
  if (!s) return undefined;
  const angulo = ((s.angulo ?? 200) * Math.PI) / 180;
  const largo = (s.largo ?? 1) * alto * 0.05;
  const dx = Math.round(Math.sin(angulo) * largo);
  const dy = Math.round(Math.abs(Math.cos(angulo)) * largo * 0.45);
  const desenfoque = Math.round(s.desenfoque ?? largo * 0.9);
  return `drop-shadow(${dx}px ${dy}px ${desenfoque}px rgba(0,0,0,${s.opacidad ?? 0.55}))`;
};

// ---------------------------------------------------------------------------

export const Episodio: React.FC<EpisodioProps> = ({spec, carpeta, audio}) => {
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
        <Sequence key={escena.id} from={desde} durationInFrames={escena.duracion} layout="none">
          <Escena escena={escena} spec={spec} carpeta={carpeta} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const Escena: React.FC<{escena: EscenaSpec; spec: EpisodioSpec; carpeta: string}> = ({
  escena,
  spec,
  carpeta,
}) => {
  // El patron aporta lo que la escena no diga. La escena siempre manda.
  const patron = escena.patron ? spec.patrones[escena.patron] : undefined;
  const variante = escena.variante ?? patron?.variante;

  if (escena.tipo === 'grafico') {
    return (
      <Grafico
        variante={variante ?? 'frase_destacada'}
        contenido={escena.contenido ?? {}}
        duracion={escena.duracion}
        tipografia={spec.tipografia}
      />
    );
  }
  if (escena.tipo === 'clip') {
    return <Clips escena={escena} carpeta={carpeta} patron={patron} />;
  }
  return <PorCapas escena={escena} spec={spec} carpeta={carpeta} patron={patron} />;
};

// ---------------------------------------------------------------------------

/**
 * Metraje real. Si el guion pide varios subplanos, se reparten la duracion en
 * fotogramas ENTEROS y acumulativos: redondeando cada uno por su cuenta, a los
 * cuatro subplanos ya hay deriva contra la locucion.
 */
const Clips: React.FC<{escena: EscenaSpec; carpeta: string; patron?: Patron}> = ({
  escena,
  carpeta,
  patron,
}) => {
  const clips = escena.clips ?? [];
  if (!clips.length) {
    return <AbsoluteFill style={{backgroundColor: '#050506'}} />;
  }

  let previo = 0;
  const tramos = clips.map((clip, indice) => {
    const fin = Math.round((escena.duracion * (indice + 1)) / clips.length);
    const tramo = {clip, desde: previo, duracion: Math.max(1, fin - previo)};
    previo = fin;
    return tramo;
  });

  const grade = escena.grade ?? patron?.grade;

  return (
    <AbsoluteFill style={{backgroundColor: '#050506'}}>
      {tramos.map(({clip, desde, duracion}) => (
        <Sequence key={clip} from={desde} durationInFrames={duracion} layout="none">
          <SubClip clip={`${carpeta}/${clip}`} grade={grade} duracion={duracion} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const SubClip: React.FC<{clip: string; grade?: Grade; duracion: number}> = ({
  clip,
  grade,
  duracion,
}) => {
  const frame = useCurrentFrame();
  // Un empuje minimo: sin el, un plano de archivo quieto se nota estatico al
  // lado de las escenas por capas, que siempre tienen camara.
  const zoom = interpolate(frame, [0, duracion], [1.03, 1.09], {
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <OffthreadVideo
        src={staticFile(clip)}
        muted
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${zoom})`,
          filter: aFiltro(grade),
        }}
      />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------

const PorCapas: React.FC<{
  escena: EscenaSpec;
  spec: EpisodioSpec;
  carpeta: string;
  patron?: Patron;
}> = ({escena, spec, carpeta, patron}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const t = interpolate(frame, [0, Math.max(1, escena.duracion - 1)], [0, 1], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const cam = escena.camara ?? {};
  const capas = escena.capas ?? [];
  const texto = escena.texto;

  // `delante_de` dice detras de que capas va el rotulo. Todo lo que NO esta en
  // esa lista queda por encima del texto, y asi el sujeto le tapa un trozo: es
  // el efecto de estar dentro de la escena y no delante de un cartel.
  const detras = new Set(texto?.delante_de ?? []);
  const corte = texto
    ? capas.findIndex((c) => !detras.has(c.id))
    : capas.length;
  const indiceCorte = corte === -1 ? capas.length : corte;

  const pinta = (capa: Capa) => (
    <CapaImagen key={capa.id} capa={capa} carpeta={carpeta} t={t} patron={patron} alto={height} />
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#08080b',
        perspective: `${PERSPECTIVA}px`,
        perspectiveOrigin: '50% 50%',
        overflow: 'hidden',
      }}
    >
      <AbsoluteFill
        style={{
          transformStyle: 'preserve-3d',
          transform: `translate3d(${entre(cam.x, t)}px, ${entre(cam.y, t)}px, 0) scale(${entre(cam.zoom, t, 1)})`,
        }}
      >
        {capas.slice(0, indiceCorte).map(pinta)}

        {texto ? (
          <Rotulo
            texto={texto}
            tipografia={spec.tipografia}
            posicionPatron={patron?.texto?.posicion}
            ancho={width}
          />
        ) : null}

        {capas.slice(indiceCorte).map(pinta)}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const CapaImagen: React.FC<{
  capa: Capa;
  carpeta: string;
  t: number;
  patron?: Patron;
  alto: number;
}> = ({capa, carpeta, t, patron, alto}) => {
  const zoom = entre(capa.zoom, t, 1);
  const x = entre(capa.x, t);
  const y = entre(capa.y, t);
  const opacidad = capa.opacidad ? entre(capa.opacidad, t, 1) : 1;

  // El patron da los valores del sujeto que la escena no declare.
  const escalaAlto = capa.escala_alto ?? (capa.principal ? patron?.sujeto?.escala_alto : undefined);
  const posicionX = capa.posicion_x ?? (capa.principal ? patron?.sujeto?.posicion_x : undefined);
  const anclaje = capa.anclaje ?? (capa.principal ? patron?.sujeto?.anclaje : undefined);
  const colocado = escalaAlto !== undefined || posicionX !== undefined;

  // Margen sobre la compensacion: la capa lleva su propio x/y ademas del de la
  // camara, y sin holgura asomaria el borde del PNG.
  const escala = compensar(capa.z) * zoom * 1.12;

  const filtros = [aFiltro(capa.grade), aSombra(capa.sombra, alto)]
    .filter(Boolean)
    .join(' ');

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
                // "pies" apoya al sujeto en el borde inferior; "centro" lo
                // centra, que es lo que quiere un objeto suelto como una
                // carpeta sobre una mesa.
                bottom: anclaje === 'centro' ? undefined : 0,
                top: anclaje === 'centro' ? '50%' : undefined,
                left: `${(posicionX ?? 0.5) * 100}%`,
                height: `${(escalaAlto ?? 0.65) * 100}%`,
                width: 'auto',
                objectFit: 'contain',
                transform:
                  anclaje === 'centro' ? 'translate(-50%, -50%)' : 'translateX(-50%)',
                filter: filtros || undefined,
              }
            : {
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                filter: filtros || undefined,
              }
        }
      />
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
  texto: TextoEscena;
  tipografia: EpisodioSpec['tipografia'];
  posicionPatron?: string;
  ancho: number;
}> = ({texto, tipografia, posicionPatron, ancho}) => {
  const frame = useCurrentFrame();
  const entrada = tipografia.entrada ?? {frames: 6, escala: [1.04, 1], opacidad: [0, 1]};
  const desde = texto.entrada_frame ?? 0;

  const t = interpolate(frame, [desde, desde + entrada.frames], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const anchoMax = texto.ancho_max ?? 0.8;
  const cuerpoBase = ancho * 0.05;
  // El cuerpo se reduce hasta caber: una letra mas pequena es mejor que una
  // palabra cortada por el borde.
  const estimado = texto.linea.length * cuerpoBase * 0.52;
  const limite = ancho * anchoMax;
  const cuerpo = estimado > limite ? Math.max(cuerpoBase * 0.55, cuerpoBase * (limite / estimado)) : cuerpoBase;

  const posicion = texto.posicion ?? posicionPatron;
  const sombra = tipografia.sombra ?? {desenfoque: 24, opacidad: 0.5};

  return (
    <AbsoluteFill
      style={{
        transform: 'translate3d(0, 0, 60px) scale(0.95)',
        justifyContent: posicion === 'inferior' ? 'flex-end' : 'center',
        alignItems: 'center',
        paddingBottom: posicion === 'inferior' ? '8%' : 0,
      }}
    >
      <div
        style={{
          maxWidth: `${anchoMax * 100}%`,
          textAlign: 'center',
          fontFamily: `'${tipografia.familia}', Poppins, sans-serif`,
          fontWeight: 900,
          fontSize: Math.round(cuerpo),
          lineHeight: 1.06,
          letterSpacing: `${tipografia.tracking ?? -0.01}em`,
          textTransform: (tipografia.transform as 'uppercase') ?? 'none',
          color: tipografia.color ?? '#E8E2D8',
          textShadow: `0 10px ${sombra.desenfoque ?? 24}px rgba(0,0,0,${sombra.opacidad ?? 0.5})`,
          opacity: (entrada.opacidad[0] ?? 0) + ((entrada.opacidad[1] ?? 1) - (entrada.opacidad[0] ?? 0)) * t,
          transform: `scale(${(entrada.escala[0] ?? 1.04) + ((entrada.escala[1] ?? 1) - (entrada.escala[0] ?? 1.04)) * t})`,
        }}
      >
        {texto.linea}
      </div>
    </AbsoluteFill>
  );
};
