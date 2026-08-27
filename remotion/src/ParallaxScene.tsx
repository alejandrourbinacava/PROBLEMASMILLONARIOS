import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export type Layer = {
  file: string;
  depth_mean: number;
  z: number;
};

export type Manifest = {
  width: number;
  height: number;
  padding: number;
  layers: Layer[];
};

export type ParallaxSceneProps = {
  manifest: Manifest;
  assetDir: string;
  title?: string;
  startZ: number;
  endZ: number;
  panX: number;
  panY: number;
};

/** Distancia del ojo al plano z=0. Todo el cálculo de escala depende de esto. */
const PERSPECTIVE = 1000;

/**
 * CSS acerca visualmente lo que tiene translateZ positivo y aleja lo negativo.
 * Sin compensar, una capa a z=-800 se ve al 55% de su tamaño y el fondo sale
 * diminuto en mitad del encuadre. Este factor la devuelve a su tamaño aparente
 * original; lo que se conserva es la diferencia de VELOCIDAD al mover la
 * cámara, que es justo lo que se busca.
 */
const compensacion = (z: number) => (PERSPECTIVE - z) / PERSPECTIVE;

export const ParallaxScene: React.FC<ParallaxSceneProps> = ({
  manifest,
  assetDir,
  title,
  startZ,
  endZ,
  panX,
  panY,
}) => {
  const frame = useCurrentFrame();
  const {durationInFrames, height} = useVideoConfig();

  // Una sola curva para todo el movimiento. Nada de spring: el rebote del
  // muelle delata que es una animación, y aquí lo que tiene que parecer es
  // una cámara sobre un raíl.
  const avance = interpolate(frame, [0, durationInFrames - 1], [0, 1], {
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const camaraZ = startZ + (endZ - startZ) * avance;
  const camaraX = panX * avance;
  const camaraY = panY * height * avance;

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* La cámara mueve el CONTENEDOR. Las capas no se animan una a una: al
          desplazar el padre, cada z produce su propio recorrido y el parallax
          sale solo, con las proporciones correctas. */}
      <AbsoluteFill
        style={{
          perspective: `${PERSPECTIVE}px`,
          transformStyle: 'preserve-3d',
        }}
      >
        <AbsoluteFill
          style={{
            transformStyle: 'preserve-3d',
            transform: `translate3d(${camaraX}px, ${camaraY}px, ${camaraZ}px)`,
          }}
        >
          {manifest.layers.map((layer) => (
            <AbsoluteFill
              key={layer.file}
              style={{
                transform: `translateZ(${layer.z}px) scale(${compensacion(layer.z)})`,
                transformStyle: 'preserve-3d',
              }}
            >
              <Img
                src={staticFile(`${assetDir}/${layer.file}`)}
                style={{
                  width: `${100 * (1 + manifest.padding)}%`,
                  height: `${100 * (1 + manifest.padding)}%`,
                  objectFit: 'cover',
                  // El margen del PNG se centra sobre el encuadre, para que
                  // sobre por los cuatro lados cuando la cámara se desplace.
                  marginLeft: `${(-100 * manifest.padding) / 2}%`,
                  marginTop: `${(-100 * manifest.padding) / 2}%`,
                }}
              />
            </AbsoluteFill>
          ))}
        </AbsoluteFill>
      </AbsoluteFill>

      {title ? <Title text={title} /> : null}
    </AbsoluteFill>
  );
};

/**
 * El rótulo vive fuera del contenedor de la cámara, en su propio plano. Si
 * viajara con las capas se movería con ellas y dejaría de leerse: el texto
 * pertenece al espectador, no a la escena.
 */
const Title: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();

  const entrada = interpolate(frame, [0, 6], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          maxWidth: '90%',
          // overflow visible a propósito: si el texto se sale, tiene que verse
          // en la revisión en vez de quedar recortado sin avisar.
          overflow: 'visible',
          textAlign: 'center',
          fontFamily: 'Poppins, sans-serif',
          fontWeight: 900,
          fontSize: Math.round(width * 0.062),
          lineHeight: 1.05,
          letterSpacing: '-0.01em',
          color: '#fff',
          // Sombra suave, no contorno: separa del fondo sin ensuciar la letra.
          textShadow: '0 8px 34px rgba(0,0,0,0.62), 0 2px 8px rgba(0,0,0,0.5)',
          opacity: entrada,
          transform: `scale(${1.04 - 0.04 * entrada})`,
          whiteSpace: 'pre-wrap',
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
