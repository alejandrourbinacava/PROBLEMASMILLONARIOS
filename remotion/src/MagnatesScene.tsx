import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export type MagnatesSceneProps = {
  /** El fondo dramático, sin el sujeto. */
  capaFondo: string;
  /** El sujeto principal, PNG con alfa limpio. */
  capaSujeto?: string;
  /** Partículas o elementos flotantes, PNG con alfa. */
  capaElementos?: string;
  texto?: string;
  duracion: number;
  /** Sentido del paneo de cámara. */
  paneo?: 'izquierda' | 'derecha';
  /** Z del fondo. El rango util va de -200 a -400. */
  zFondo?: number;
  /** Z de los elementos frontales. De 100 a 300. */
  zElementos?: number;
};

/** Distancia del ojo al plano cero. Todo el calculo de escala depende de esto. */
const PERSPECTIVA = 1200;

/**
 * Cuanto hay que ampliar una capa para que, puesta a esa Z, se vea del mismo
 * tamano aparente que si estuviera en el plano cero.
 *
 *     escala = (perspectiva + |z|) / perspectiva     para z negativa
 *     escala = (perspectiva - z) / perspectiva       para z positiva
 *
 * Sin esto, el fondo a -300 se ve al 80% y aparece un marco negro alrededor;
 * y el texto a +200 se ve un 20% mas grande de lo previsto. Lo que se conserva
 * al compensar no es el tamano -eso es lo que se iguala- sino la diferencia de
 * VELOCIDAD cuando la camara se mueve, que es el parallax.
 */
const compensar = (z: number) => (PERSPECTIVA - z) / PERSPECTIVA;

export const MagnatesScene: React.FC<MagnatesSceneProps> = ({
  capaFondo,
  capaSujeto,
  capaElementos,
  texto,
  duracion,
  paneo = 'derecha',
  zFondo = -300,
  zElementos = 200,
}) => {
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();

  // ---- camara ----
  // Empuje continuo en Z mas un paneo lateral. El paneo es lo que hace visible
  // el parallax: con un empuje puro, todas las capas crecen casi lo mismo y el
  // ojo lo lee como un zoom sobre una foto plana.
  const camaraZ = interpolate(frame, [0, duracion], [0, 90], {
    extrapolateRight: 'clamp',
  });
  const sentido = paneo === 'derecha' ? 1 : -1;
  const camaraX = interpolate(frame, [0, duracion], [-34 * sentido, 34 * sentido], {
    extrapolateRight: 'clamp',
  });
  const camaraY = interpolate(frame, [0, duracion], [10, -10], {
    extrapolateRight: 'clamp',
  });

  // ---- entrada del sujeto ----
  // spring da el rebote al asentarse. La rotacion en Y es minima a proposito:
  // un giro grande delata que es una imagen plana girando en el espacio.
  const asiento = spring({frame, fps, config: {damping: 14, mass: 0.6, stiffness: 90}});
  const escalaSujeto = interpolate(asiento, [0, 1], [0.92, 1]);
  const giroSujeto = interpolate(asiento, [0, 1], [-4, 0]);

  const entradaTexto = spring({
    frame: frame - 4,
    fps,
    config: {damping: 16, mass: 0.5, stiffness: 110},
  });

  // El fondo se amplia un poco de mas: el paneo lo desplaza y sin ese margen
  // asomaria el borde de la imagen por un lado.
  const escalaFondo = compensar(zFondo) * 1.14;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#08080c',
        perspective: `${PERSPECTIVA}px`,
        perspectiveOrigin: '50% 50%',
        overflow: 'hidden',
      }}
    >
      {/* La camara: un nodo vacio que mueve todo lo que cuelga de el. Al
          animar el padre, cada Z produce su propio recorrido y el parallax
          sale solo, con las proporciones correctas. */}
      <AbsoluteFill
        style={{
          transformStyle: 'preserve-3d',
          transform: `translate3d(${camaraX}px, ${camaraY}px, ${camaraZ}px)`,
        }}
      >
        {/* CAPA 1 - FONDO, al fondo en Z */}
        <AbsoluteFill
          style={{
            transform: `translate3d(0, 0, ${zFondo}px) scale(${escalaFondo})`,
            transformStyle: 'preserve-3d',
          }}
        >
          <Img
            src={staticFile(capaFondo)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              // Oscuro y contrastado, que es la base del estilo. Va sobre la
              // capa de fondo, nunca sobre el sujeto: aplicarlo al conjunto
              // aplastaria tambien la silueta y perderia la separacion.
              filter: 'brightness(0.52) contrast(1.28) saturate(1.06)',
            }}
          />
        </AbsoluteFill>

        {/* Viñeta, en su propio plano justo delante del fondo. Cierra los
            bordes y deja el centro limpio para el sujeto. */}
        <AbsoluteFill
          style={{
            transform: `translate3d(0, 0, ${zFondo + 60}px) scale(${compensar(zFondo + 60) * 1.14})`,
            background:
              'radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 34%, rgba(0,0,0,0.52) 78%, rgba(0,0,0,0.82) 100%)',
          }}
        />

        {/* CAPA 2 - SUJETO, en el plano cero */}
        {capaSujeto ? (
          <AbsoluteFill
            style={{
              transform: 'translate3d(0, 0, 0px)',
              transformStyle: 'preserve-3d',
              justifyContent: 'flex-end',
              alignItems: 'center',
            }}
          >
            <Img
              src={staticFile(capaSujeto)}
              style={{
                height: '82%',
                width: 'auto',
                objectFit: 'contain',
                transform: `scale(${escalaSujeto}) rotateY(${giroSujeto}deg)`,
                transformOrigin: 'bottom center',
              }}
            />
          </AbsoluteFill>
        ) : null}

        {/* CAPA 3 - ELEMENTOS Y TEXTO, delante en Z */}
        {capaElementos ? (
          <AbsoluteFill
            style={{
              transform: `translate3d(0, 0, ${zElementos}px) scale(${compensar(zElementos)})`,
              transformStyle: 'preserve-3d',
            }}
          >
            <Img
              src={staticFile(capaElementos)}
              style={{width: '100%', height: '100%', objectFit: 'cover'}}
            />
          </AbsoluteFill>
        ) : null}

        {texto ? (
          <AbsoluteFill
            style={{
              transform: `translate3d(0, 0, ${zElementos - 60}px) scale(${compensar(zElementos - 60)})`,
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <div
              style={{
                maxWidth: '78%',
                textAlign: 'center',
                fontFamily: 'Poppins, sans-serif',
                fontWeight: 900,
                fontSize: Math.round(width * 0.055),
                lineHeight: 1.04,
                letterSpacing: '-0.015em',
                color: '#fff',
                textShadow: '0 12px 44px rgba(0,0,0,0.8), 0 2px 10px rgba(0,0,0,0.7)',
                opacity: interpolate(entradaTexto, [0, 1], [0, 1]),
                transform: `translateY(${interpolate(entradaTexto, [0, 1], [26, 0])}px)`,
              }}
            >
              {texto}
            </div>
          </AbsoluteFill>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
