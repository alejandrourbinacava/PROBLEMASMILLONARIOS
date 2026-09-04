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
import {Fuentes} from './fuentes';

/**
 * El gancho, montado por capas.
 *
 * Un solo decorado -cielo, fachada, gente- rodado desde sitios distintos, y
 * las cifras metidas DENTRO de la escena en su propia capa de profundidad, no
 * como cartel encima de todo. Por eso la multitud le pasa por delante al
 * numero: el rotulo esta a z 150 y la gente a z 50.
 *
 * Cada capa lleva su recorrido y su color. El cielo casi no se mueve y va frio;
 * la gente recorre todo y va a contraluz.
 */

const CURVA = Easing.bezier(0.33, 0, 0.15, 1);
const FPS = 25;

// Cuanto recorre cada capa del movimiento de camara.
const PARALLAX = {cielo: 0.08, casino: 0.35, cifra: 0.62, gente: 1.0};

type Camara = {
  zoom: number[];
  deriva: number[];
  /** Punto de la escena al que mira la camara, en fraccion del ancho. */
  centro?: number;
};

const rampa = (frame: number, dur: number, par: number[]) =>
  interpolate(frame, [0, Math.max(1, dur - 1)], par, {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

/**
 * Una toma del decorado.
 *
 * `cifra` y `pie` son opcionales: cuando estan, entran como una capa mas, a su
 * profundidad, con su propio recorrido.
 */
const Toma: React.FC<{
  duracion: number;
  camara: Camara;
  cifra?: string;
  pie?: string;
  entradaCifra?: number;
  /** Donde va la cifra, en fraccion del cuadro. */
  sitio?: {x: number; y: number};
}> = ({duracion, camara, cifra, pie, entradaCifra = 8, sitio}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();

  const zoom = rampa(frame, duracion, camara.zoom);
  const deriva = rampa(frame, duracion, camara.deriva);

  // Las nubes van por su cuenta, al margen de la camara: un cielo quieto
  // delata que es una foto.
  const nubes = interpolate(frame, [0, duracion], [0, -46], {
    extrapolateRight: 'clamp',
  });

  const capa = (p: number) => ({
    escala: 1 + (zoom - 1) * (0.3 + p * 0.7),
    x: deriva * p,
  });
  const c = capa(PARALLAX.cielo);
  const f = capa(PARALLAX.casino);
  const g = capa(PARALLAX.gente);
  const n = capa(PARALLAX.cifra);

  // La cifra se materializa: entra desde poca opacidad y bajando de escala.
  const tCifra = interpolate(frame, [entradaCifra, entradaCifra + 14], [0, 1], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#05060c', overflow: 'hidden'}}>
      {/* CIELO */}
      <AbsoluteFill
        style={{transform: `translateX(${c.x + nubes}px) scale(${c.escala * 1.08})`}}
      >
        <Img
          src={staticFile('entrada/cielo.png')}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'brightness(0.92) saturate(0.85)',
          }}
        />
      </AbsoluteFill>

      {/* Bruma: separa el cielo de la fachada sin desenfocar nada */}
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(to bottom, rgba(20,28,48,0) 38%, rgba(24,30,52,0.5) 100%)',
        }}
      />

      {/* FACHADA */}
      <AbsoluteFill style={{transform: `translateX(${f.x}px) scale(${f.escala})`}}>
        <Img
          src={staticFile('entrada/casino.png')}
          style={{
            position: 'absolute',
            left: '50%',
            bottom: '4%',
            height: '86%',
            width: 'auto',
            transform: 'translateX(-50%)',
            filter: 'brightness(0.95) saturate(1.06)',
          }}
        />
      </AbsoluteFill>

      {/* LA CIFRA: una capa mas, a su profundidad. La gente le pasa por
          delante porque va detras de ella en la pila. */}
      {cifra ? (
        <AbsoluteFill
          style={{
            transform: `translateX(${n.x}px) scale(${n.escala})`,
            opacity: tCifra,
          }}
        >
          <div
            style={{
              // La cifra NO va en el centro: ahi esta el rotulo del casino,
              // que es lo mas brillante del cuadro, y los dos se pelean. Va
              // donde hay sitio, y en una de las tomas lo bastante baja como
              // para que la multitud la tape a medias.
              position: 'absolute',
              left: `${(sitio?.x ?? 0.5) * 100}%`,
              top: `${(sitio?.y ?? 0.5) * 100}%`,
              transform: `translate(-50%, -50%) scale(${1.12 - 0.12 * tCifra})`,
              textAlign: 'center',
              // Sin esto la cifra se parte en dos lineas al acercarse al borde
              // y se sale del cuadro: paso con "696 M$".
              whiteSpace: 'nowrap',
            }}
          >
            <div
              style={{
                fontFamily: "'Archivo Black', Poppins, sans-serif",
                fontSize: Math.round(width * 0.105),
                lineHeight: 1,
                color: '#F2E9D8',
                letterSpacing: '-0.02em',
                textShadow: '0 12px 40px rgba(0,0,0,0.7)',
              }}
            >
              {cifra}
            </div>
            {pie ? (
              <div
                style={{
                  marginTop: 14,
                  fontFamily: 'Poppins, sans-serif',
                  fontWeight: 600,
                  fontSize: Math.round(width * 0.019),
                  letterSpacing: '0.16em',
                  textTransform: 'uppercase',
                  color: '#C9A227',
                  textShadow: '0 6px 22px rgba(0,0,0,0.8)',
                }}
              >
                {pie}
              </div>
            ) : null}
          </div>
        </AbsoluteFill>
      ) : null}

      {/* GENTE: delante de todo, incluido el numero */}
      <AbsoluteFill style={{transform: `translateX(${g.x}px) scale(${g.escala})`}}>
        <Img
          src={staticFile('entrada/gente.png')}
          style={{
            position: 'absolute',
            left: '50%',
            bottom: '-2%',
            width: `${width * 1.12}px`,
            height: 'auto',
            transform: 'translateX(-50%)',
            filter: 'brightness(0.7) contrast(1.14) saturate(0.88)',
          }}
        />
      </AbsoluteFill>

      {/* Resplandor de la marquesina, por delante de todo */}
      <AbsoluteFill style={{mixBlendMode: 'screen'}}>
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '46%',
            width: '58%',
            height: '46%',
            borderRadius: '50%',
            backgroundColor: '#C98B34',
            opacity: 0.2,
            filter: 'blur(140px)',
            transform: 'translate(-50%, -50%)',
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.5) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};

/** Las tomas, cortadas donde lo pide la locucion. */
const TOMAS: {
  hasta: number;
  camara: Camara;
  cifra?: string;
  pie?: string;
  entradaCifra?: number;
  sitio?: {x: number; y: number};
}[] = [
  // "En febrero de 2026, los casinos de Nevada ganaron 1.236 millones."
  {hasta: 6.95, camara: {zoom: [1.0, 1.16], deriva: [-70, 40]},
   cifra: '1.236 M$', pie: 'Nevada · febrero de 2026', entradaCifra: 62,
   sitio: {x: 0.26, y: 0.2}},
  // "Eso no es lo que apostaron. Eso es lo que perdieron."
  {hasta: 12.24, camara: {zoom: [1.26, 1.1], deriva: [90, -50]},
   cifra: 'LO QUE PERDIERON', entradaCifra: 10,
   sitio: {x: 0.46, y: 0.66}},
  // "Solo el Strip se quedo 696 millones."
  {hasta: 16.5, camara: {zoom: [1.04, 1.2], deriva: [-40, 60]},
   cifra: '696 M$', pie: 'solo el Strip · 28 días', entradaCifra: 8,
   sitio: {x: 0.68, y: 0.2}},
  // "En 28 dias. Y a diferencia de cualquier otro negocio..."
  {hasta: 27.1, camara: {zoom: [1.3, 1.02], deriva: [110, -110]}},
  // "Depende de una formula matematica que no falla nunca."
  {hasta: 30.4, camara: {zoom: [1.0, 1.24], deriva: [-30, 30]},
   cifra: 'UNA FÓRMULA', entradaCifra: 6, sitio: {x: 0.3, y: 0.24}},
];

export const Gancho: React.FC = () => {
  let desde = 0;
  return (
    <AbsoluteFill>
      <Fuentes />
      <Audio src={staticFile('entrada/voz_gancho.mp3')} />
      {TOMAS.map((toma, i) => {
        const inicio = desde;
        const dur = Math.round(toma.hasta * FPS) - Math.round(inicio * FPS);
        desde = toma.hasta;
        return (
          <Sequence
            key={i}
            from={Math.round(inicio * FPS)}
            durationInFrames={dur}
          >
            <Toma
              duracion={dur}
              camara={toma.camara}
              cifra={toma.cifra}
              pie={toma.pie}
              entradaCifra={toma.entradaCifra}
              sitio={toma.sitio}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
