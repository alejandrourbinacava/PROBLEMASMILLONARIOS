import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {Escena, EscenaProps} from './Escena';

export type Paso = Omit<EscenaProps, 'duracion'> & {
  /** Hasta que segundo dura, sacado de las marcas del SRT de la narracion. */
  hasta: number;
  /** Por donde entra esta escena. La primera no lleva. */
  entra?: 'izquierda' | 'derecha';
};

export type SecuenciaProps = {
  pasos: Paso[];
  audio?: string;
  /** Cuanto dura el deslizamiento entre escenas, en fotogramas. */
  transicion: number;
};

/**
 * Encadena las escenas deslizando de lado.
 *
 * La transicion no es un fundido: la escena nueva ENTRA empujando, y la vieja
 * sale hacia el lado contrario a algo menos de velocidad. Esa diferencia de
 * velocidad entre la que entra y la que sale es lo que hace que se lea como un
 * desplazamiento por un espacio y no como dos imagenes que se cruzan.
 */
export const Secuencia: React.FC<SecuenciaProps> = ({pasos, audio, transicion}) => {
  const {fps} = useVideoConfig();

  let anterior = 0;
  const tramos = pasos.map((paso) => {
    const desde = anterior;
    const hasta = Math.round(paso.hasta * fps);
    anterior = hasta;
    return {paso, desde, duracion: Math.max(1, hasta - desde)};
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {audio ? <Audio src={staticFile(audio)} /> : null}

      {tramos.map(({paso, desde, duracion}, indice) => (
        <Sequence
          key={indice}
          from={desde}
          // Se alarga lo que dura la transicion para que la escena siga viva
          // mientras la siguiente entra por encima.
          durationInFrames={duracion + transicion}
          layout="none"
        >
          <Deslizante
            entra={indice === 0 ? undefined : paso.entra ?? 'derecha'}
            transicion={transicion}
            duracion={duracion}
            esUltima={indice === tramos.length - 1}
          >
            <Escena {...paso} duracion={duracion} />
          </Deslizante>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const Deslizante: React.FC<{
  entra?: 'izquierda' | 'derecha';
  transicion: number;
  duracion: number;
  esUltima: boolean;
  children: React.ReactNode;
}> = ({entra, transicion, duracion, esUltima, children}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();

  const curva = Easing.bezier(0.4, 0, 0.1, 1);

  // Entrada: llega desde fuera del encuadre hasta su sitio.
  const dentro = entra
    ? interpolate(frame, [0, transicion], [entra === 'derecha' ? width : -width, 0], {
        easing: curva,
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 0;

  // Salida: se va al lado contrario, pero solo un 45% del ancho. Sacarla
  // entera deja el fondo negro asomando por el borde durante la transicion.
  const fuera =
    esUltima
      ? 0
      : interpolate(frame, [duracion, duracion + transicion], [0, -width * 0.45], {
          easing: curva,
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

  return (
    <AbsoluteFill style={{transform: `translateX(${dentro + fuera}px)`}}>
      {children}
    </AbsoluteFill>
  );
};
