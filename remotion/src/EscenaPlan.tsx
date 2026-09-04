import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';

/**
 * Renderiza un PLAN de escena: capas por papel, con su profundidad y su
 * recorrido.
 *
 * La diferencia con lo anterior no es cosmetica. Antes habia una imagen y se
 * le hacia zoom, y el espectador ve enseguida que es una foto moviendose.
 * Aqui hay cinco assets distintos a cinco profundidades, y lo que se anima es
 * UNA CAMARA: cada capa se desplaza segun lo lejos que este.
 *
 * El primer plano recorre 260 px y el fondo lejano 13. Esa diferencia de 20 a
 * 1 es lo que el ojo lee como profundidad; sin ella, por mucho translateZ que
 * se ponga, el plano se ve plano.
 */

const CURVA = Easing.bezier(0.33, 0, 0.15, 1);

export type CapaPlan = {
  papel: string;
  z: number;
  parallax: number;
  recortar: boolean | null;
  recorrido_px: number;
  encargo: string;
  origen: string;
};

export type Plan = {
  locucion: string;
  duracion_frames: number;
  tipo: string;
  revela: string;
  camara: {push: number[]; lateral: number[]; frames: number};
  capas: CapaPlan[];
};

/**
 * Como se coloca cada papel en el encuadre.
 *
 * Un techo no se coloca igual que unas fichas. El fondo y el fondo lejano
 * llenan el cuadro; lo recortado se coloca por su altura y su sitio, y cuanto
 * mas cerca de la camara, mas grande y mas abajo: es lo que hace que las
 * fichas parezcan estar en el borde de la mesa y no flotando.
 */
const COLOCACION: Record<string, {alto: number; x: number; abajo: number}> = {
  midground: {alto: 0.42, x: 0.72, abajo: 0.18},
  subject: {alto: 0.62, x: 0.36, abajo: 0.06},
  foreground: {alto: 0.38, x: 0.14, abajo: -0.08},
};

export const EscenaPlan: React.FC<{plan: Plan; carpeta: string}> = ({
  plan,
  carpeta,
}) => {
  const frame = useCurrentFrame();
  const cam = plan.camara;

  // El avance de la camara, de 0 a 1. Todo lo demas se deriva de aqui.
  const t = interpolate(frame, [0, Math.max(1, cam.frames - 1)], [0, 1], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const push = cam.push[0] + (cam.push[1] - cam.push[0]) * t;
  const lateral = cam.lateral[0] + (cam.lateral[1] - cam.lateral[0]) * t;

  const ordenadas = [...plan.capas].sort((a, b) => b.z - a.z);

  return (
    <AbsoluteFill style={{backgroundColor: '#07070a', overflow: 'hidden'}}>
      {ordenadas.map((capa) => {
        // Lo que recorre esta capa depende de lo lejos que este. Es la regla
        // entera del parallax, y esta en una sola linea.
        const x = lateral * capa.parallax + capa.recorrido_px * t * capa.parallax;

        // La camara al acercarse agranda mas lo cercano que lo lejano.
        const escala = 1 + (push - 1) * (0.25 + capa.parallax * 0.75);

        const sitio = COLOCACION[capa.papel];
        const recortada = capa.recortar === true && sitio;

        return (
          <AbsoluteFill
            key={capa.papel}
            style={{transform: `translateX(${x}px) scale(${escala})`}}
          >
            <Img
              src={staticFile(`${carpeta}/${capa.papel}.png`)}
              style={
                recortada
                  ? {
                      position: 'absolute',
                      left: `${sitio.x * 100}%`,
                      bottom: `${sitio.abajo * 100}%`,
                      height: `${sitio.alto * 100}%`,
                      width: 'auto',
                      transform: 'translateX(-50%)',
                      // La bruma atmosferica: lo lejano pierde contraste y se
                      // aclara. Es lo que integra capas de origen distinto sin
                      // recurrir a desenfocar el fondo entero.
                      filter: `brightness(${1 - capa.z / 2600}) saturate(${1 - capa.z / 3400})`,
                    }
                  : {
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      filter: `brightness(${1 - capa.z / 2600}) saturate(${1 - capa.z / 3400})`,
                    }
              }
            />
          </AbsoluteFill>
        );
      })}

      {/* La lente, que unifica los cinco origenes distintos */}
      <AbsoluteFill style={{mixBlendMode: 'screen', pointerEvents: 'none'}}>
        <div
          style={{
            position: 'absolute',
            left: '78%',
            top: '35%',
            width: '135%',
            height: '155%',
            borderRadius: '50%',
            backgroundColor: '#8A5A2B',
            opacity: 0.16,
            filter: 'blur(300px)',
            transform: 'translate(-50%, -50%)',
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.35) 100%)',
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};
