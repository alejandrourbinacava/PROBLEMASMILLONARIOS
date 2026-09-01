import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

/**
 * Efectos en bucle con canal alfa: lo que Meta AI no puede dar porque solo
 * hace imagenes fijas.
 *
 * Se renderizan como secuencia de PNG con transparencia y el motor de VOX
 * los superpone en bucle. No hace falta ni Google Flow ni creditos de video:
 * el fuego y el agua son turbulencia y senos, y eso se calcula.
 *
 * El bucle tiene que CERRAR: el ultimo fotograma enlaza con el primero o se
 * ve un salto cada vez que da la vuelta. Por eso todo va en funcion de
 * `frame / durationInFrames` y con periodos enteros.
 */

export const Fuego: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const u = frame / durationInFrames;
  // la semilla no puede ir subiendo sin mas: al cerrar el bucle daria un
  // salto. Va y vuelve, asi el ultimo fotograma se parece al primero.
  const semilla = Math.round(8 + 8 * Math.sin(2 * Math.PI * u));
  const alto = 1 + 0.10 * Math.sin(2 * Math.PI * u * 2);

  return (
    <AbsoluteFill>
      <svg width="100%" height="100%" viewBox="0 0 400 520">
        <defs>
          <filter id="llama" x="-40%" y="-40%" width="180%" height="180%">
            <feTurbulence type="fractalNoise" baseFrequency="0.016 0.045"
              numOctaves={3} seed={semilla} result="ruido"/>
            <feDisplacementMap in="SourceGraphic" in2="ruido" scale={34}
              xChannelSelector="R" yChannelSelector="G"/>
            <feGaussianBlur stdDeviation={3}/>
          </filter>
          <radialGradient id="calor" cx="50%" cy="78%" r="62%">
            <stop offset="0%" stopColor="#fff3b0"/>
            <stop offset="32%" stopColor="#ffb703"/>
            <stop offset="68%" stopColor="#e8590c"/>
            <stop offset="100%" stopColor="#c92a2a" stopOpacity="0"/>
          </radialGradient>
        </defs>
        <g filter="url(#llama)" transform={`translate(200 470) scale(1 ${alto}) translate(-200 -470)`}>
          <path d="M200 470 C 120 430, 118 330, 172 250 C 168 316, 200 330, 206 286
                   C 232 322, 246 260, 236 214 C 300 300, 292 424, 200 470 Z"
                fill="url(#calor)"/>
          <path d="M200 468 C 158 442, 156 372, 190 320 C 188 366, 210 372, 214 344
                   C 240 386, 236 440, 200 468 Z"
                fill="#fff3b0" opacity={0.85}/>
        </g>
      </svg>
    </AbsoluteFill>
  );
};

export const Agua: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames, width} = useVideoConfig();
  const u = frame / durationInFrames;

  // tres crestas a velocidades distintas: una sola onda se lee como una
  // cinta ondulando, tres se leen como agua
  const onda = (amp: number, largo: number, vel: number, y0: number) => {
    const pts: string[] = [];
    for (let x = 0; x <= width + 20; x += 12) {
      const y = y0 + amp * Math.sin((x / largo + u * vel) * 2 * Math.PI);
      pts.push(`${x},${y.toFixed(1)}`);
    }
    return `M-20,400 L${pts.join(' L')} L${width + 20},400 Z`;
  };

  return (
    <AbsoluteFill>
      <svg width="100%" height="100%" viewBox={`0 0 ${width} 400`}>
        <path d={onda(16, 460, 1, 150)} fill="#3b5b70" opacity={0.55}/>
        <path d={onda(22, 320, 2, 196)} fill="#2b4356" opacity={0.75}/>
        <path d={onda(13, 210, 3, 238)} fill="#1d2f3d"/>
      </svg>
    </AbsoluteFill>
  );
};
