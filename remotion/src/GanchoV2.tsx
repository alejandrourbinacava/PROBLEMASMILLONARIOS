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
import {Contador} from './Contador';

/**
 * El gancho entero, montado con la biblioteca de assets.
 *
 * Las reglas de movimiento y de color son las del documento de escenas, iguales
 * para todo el episodio:
 *
 *   cielo / fondo      20 px por cada 100 frames   desenfoque 4   brillo 0,65
 *   arquitectura       55 px                       desenfoque 2   brillo 0,90
 *   primer plano      190 px                       desenfoque 0   brillo 0,75
 *
 * La diferencia entre 20 y 190 ES el efecto. Con 8 y 100 -lo que tenia antes-
 * la multitud casi no se movia y el plano se leia como una foto.
 *
 * Los cortes caen donde los pone la locucion, no donde los pone el documento:
 * el guion estima duraciones y el SRT las mide.
 */

const CURVA = Easing.bezier(0.33, 0, 0.15, 1);
const FPS = 25;

// Recorrido en pixeles por cada 100 frames, por papel de capa.
const RECORRIDO = {fondo: 20, medio: 55, frente: 190};
const GRADE = {
  fondo: 'brightness(0.65) saturate(0.6) blur(4px)',
  medio: 'brightness(0.9) saturate(0.85) blur(2px)',
  frente: 'brightness(0.75) saturate(0.9) contrast(1.45)',
};

const rampa = (frame: number, dur: number, par: number[], curva = true) =>
  interpolate(frame, [0, Math.max(1, dur - 1)], par, {
    easing: curva ? CURVA : undefined,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

/** La lente. Va siempre: es lo que une capas de origenes distintos. */
const Lente: React.FC<{color?: string; x?: string}> = ({
  color = '#8A5A2B',
  x = '78%',
}) => (
  <AbsoluteFill style={{mixBlendMode: 'screen', pointerEvents: 'none'}}>
    <div
      style={{
        position: 'absolute',
        left: x,
        top: '38%',
        width: '135%',
        height: '150%',
        borderRadius: '50%',
        backgroundColor: color,
        opacity: 0.18,
        filter: 'blur(300px)',
        transform: 'translate(-50%, -50%)',
      }}
    />
  </AbsoluteFill>
);

const Vineta: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        'radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.5) 100%)',
      pointerEvents: 'none',
    }}
  />
);

/** Un rotulo que entra por la derecha, como pide el documento. */
const Rotulo: React.FC<{
  texto: string;
  pie?: string;
  desde: number;
  x?: number;
  y?: number;
  cuerpo?: number;
}> = ({texto, pie, desde, x = 0.5, y = 0.2, cuerpo = 0.075}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const t = interpolate(frame, [desde, desde + 12], [0, 1], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        position: 'absolute',
        left: `${x * 100}%`,
        top: `${y * 100}%`,
        transform: `translate(-50%, -50%) translateX(${(1 - t) * 180}px)`,
        opacity: t,
        textAlign: 'center',
        whiteSpace: 'nowrap',
      }}
    >
      <div
        style={{
          fontFamily: "'Archivo Black', Poppins, sans-serif",
          fontSize: Math.round(width * cuerpo),
          lineHeight: 1,
          color: '#F2E9D8',
          letterSpacing: '-0.015em',
          textShadow: '0 12px 40px rgba(0,0,0,0.75)',
        }}
      >
        {texto}
      </div>
      {pie ? (
        <div
          style={{
            marginTop: 12,
            fontFamily: 'Poppins, sans-serif',
            fontWeight: 700,
            fontSize: Math.round(width * 0.016),
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
            color: '#C9A227',
            textShadow: '0 6px 20px rgba(0,0,0,0.85)',
          }}
        >
          {pie}
        </div>
      ) : null}
    </div>
  );
};

/* ---------------- G1 · la torre y la multitud ---------------- */

const G1: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const p = (px: number) => rampa(frame, dur, [0, -px * (dur / 100)]);
  return (
    <AbsoluteFill style={{backgroundColor: '#05060c', overflow: 'hidden'}}>
      <Fuentes />
      <AbsoluteFill style={{transform: `translateX(${p(RECORRIDO.fondo)}px) scale(1.1)`}}>
        <Img src={staticFile('entrada/cielo.png')}
          style={{width: '100%', height: '100%', objectFit: 'cover', filter: GRADE.fondo}} />
      </AbsoluteFill>

      {/* La torre ademas sube 12 px, como dice el documento */}
      <AbsoluteFill
        style={{
          transform: `translate(${p(RECORRIDO.medio)}px, ${rampa(frame, dur, [0, -12])}px)`,
        }}
      >
        <Img src={staticFile('biblioteca/casino_torre.png')}
          style={{
            position: 'absolute', left: '58%', bottom: '6%',
            height: '82%', width: 'auto', transform: 'translateX(-50%)',
            filter: GRADE.medio,
          }} />
      </AbsoluteFill>

      <AbsoluteFill style={{transform: `translateX(${p(RECORRIDO.frente)}px)`}}>
        <Img src={staticFile('entrada/gente.png')}
          style={{
            position: 'absolute', left: '46%', bottom: '-3%',
            width: `${width * 1.3}px`, height: 'auto',
            transform: 'translateX(-50%)', filter: GRADE.frente,
          }} />
      </AbsoluteFill>

      <Rotulo texto="FEBRERO DE 2026" desde={40} x={0.28} y={0.16} cuerpo={0.055} />
      <Lente />
      <Vineta />
    </AbsoluteFill>
  );
};

/* ---------------- G3 · la torre pasa por delante del casino pequeño ---------------- */

const G3: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const p = (px: number) => rampa(frame, dur, [px * 0.6 * (dur / 100), -px * (dur / 100)]);
  return (
    <AbsoluteFill style={{backgroundColor: '#05060c', overflow: 'hidden'}}>
      <Fuentes />
      <AbsoluteFill style={{transform: `translateX(${p(RECORRIDO.fondo)}px) scale(1.1)`}}>
        <Img src={staticFile('entrada/cielo.png')}
          style={{width: '100%', height: '100%', objectFit: 'cover', filter: GRADE.fondo}} />
      </AbsoluteFill>

      {/* El casino pequeño va DETRAS y mas lento: la torre lo adelanta */}
      <AbsoluteFill style={{transform: `translateX(${p(RECORRIDO.medio * 0.55)}px)`}}>
        <Img src={staticFile('biblioteca/casino_pequeno.png')}
          style={{
            position: 'absolute', left: '74%', bottom: '16%',
            height: '30%', width: 'auto', transform: 'translateX(-50%)',
            filter: 'brightness(0.78) saturate(0.75) blur(2px)',
          }} />
      </AbsoluteFill>

      <AbsoluteFill style={{transform: `translateX(${p(RECORRIDO.frente)}px)`}}>
        <Img src={staticFile('biblioteca/casino_torre.png')}
          style={{
            position: 'absolute', left: '34%', bottom: '4%',
            height: '88%', width: 'auto', transform: 'translateX(-50%)',
            filter: GRADE.medio,
          }} />
      </AbsoluteFill>

      <Rotulo texto="$696.285.791" pie="solo el Strip · 28 días"
        desde={30} x={0.72} y={0.22} cuerpo={0.058} />
      <Lente />
      <Vineta />
    </AbsoluteFill>
  );
};

/* ---------------- G4 · la ruleta y el 2,7 % ---------------- */

const G4: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const zoom = rampa(frame, dur, [1.0, 1.15]);
  // La linea converge al 2,7 %: sube deprisa y se aplana.
  const pct = interpolate(frame, [dur * 0.35, dur * 0.8], [0, 2.7], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const tPct = interpolate(frame, [dur * 0.35, dur * 0.45], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{backgroundColor: '#040407', overflow: 'hidden'}}>
      <Fuentes />
      <Img src={staticFile('biblioteca/fondo_negro_textura.png')}
        style={{width: '100%', height: '100%', objectFit: 'cover'}} />

      <AbsoluteFill style={{transform: `scale(${zoom})`}}>
        <Img src={staticFile('biblioteca/ruleta_perfil.png')}
          style={{
            position: 'absolute', left: '50%', top: '54%',
            height: '45%', width: 'auto',
            transform: 'translate(-50%, -50%)',
            filter: 'brightness(0.92) saturate(0.95) contrast(1.15)',
          }} />
      </AbsoluteFill>

      <div
        style={{
          position: 'absolute', left: '50%', top: '17%',
          transform: 'translateX(-50%)', textAlign: 'center',
          opacity: tPct, whiteSpace: 'nowrap',
        }}
      >
        <div
          style={{
            fontFamily: "'Archivo Black', Poppins, sans-serif",
            fontSize: Math.round(width * 0.085),
            color: '#F2E9D8',
            fontVariantNumeric: 'tabular-nums',
            textShadow: '0 12px 40px rgba(0,0,0,0.8)',
          }}
        >
          {pct.toFixed(1).replace('.', ',')} %
        </div>
        <div
          style={{
            marginTop: 10,
            fontFamily: 'Poppins, sans-serif',
            fontWeight: 700,
            fontSize: Math.round(width * 0.015),
            letterSpacing: '0.2em',
            color: '#C9A227',
          }}
        >
          VENTAJA DE LA CASA
        </div>
      </div>
      <Lente x="30%" />
      <Vineta />
    </AbsoluteFill>
  );
};

/* ---------------- G5 · el amanecer y el hombre en silueta ---------------- */

const G5: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  // Retroceso: todo se aleja.
  const zoom = rampa(frame, dur, [1.14, 1.0]);
  return (
    <AbsoluteFill style={{backgroundColor: '#0b0d12', overflow: 'hidden'}}>
      <Fuentes />
      {/* Regla de contraste del documento: cielo a 1,25 y hombre a 0,12 */}
      <AbsoluteFill style={{transform: `scale(${zoom * 1.04})`}}>
        <Img src={staticFile('biblioteca/cielo_amanecer.png')}
          style={{
            width: '100%', height: '100%', objectFit: 'cover',
            filter: 'brightness(1.25) saturate(0.9)',
          }} />
      </AbsoluteFill>

      <AbsoluteFill style={{transform: `scale(${zoom})`}}>
        <Img src={staticFile('biblioteca/casino_pequeno.png')}
          style={{
            position: 'absolute', left: '66%', bottom: '18%',
            height: '34%', width: 'auto', transform: 'translateX(-50%)',
            filter: 'brightness(0.42) saturate(0.5) contrast(1.3)',
          }} />
      </AbsoluteFill>

      <AbsoluteFill style={{transform: `scale(${zoom * 1.06})`}}>
        <Img src={staticFile('biblioteca/hombre_traje_espaldas.png')}
          style={{
            position: 'absolute', left: '34%', bottom: '10%',
            height: '65%', width: 'auto', transform: 'translateX(-50%)',
            filter: 'brightness(0.12) contrast(1.6) saturate(0.3)',
          }} />
      </AbsoluteFill>

      <Rotulo texto="¿CUÁNTO CUESTA?" desde={14} x={0.5} y={0.86} cuerpo={0.056} />
      <Vineta />
    </AbsoluteFill>
  );
};

/* ---------------- G6 · pantalla partida ---------------- */

const G6: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const izq = interpolate(frame, [4, 16], [0, 1], {
    easing: CURVA, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const der = interpolate(frame, [19, 31], [0, 1], {
    easing: CURVA, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // La interrogacion parpadea una vez.
  const parpadeo = interpolate(frame, [40, 44, 48, 52], [1, 0.15, 1, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  const col = (titulo: string, linea: string, t: number, lado: number, alfa = 1) => (
    <div
      style={{
        position: 'absolute',
        left: `${lado * 100}%`,
        top: '50%',
        transform: `translate(-50%, -50%) translateY(${(1 - t) * 30}px)`,
        opacity: t,
        textAlign: 'center',
        whiteSpace: 'nowrap',
      }}
    >
      <div style={{
        fontFamily: 'Poppins, sans-serif', fontWeight: 700,
        fontSize: Math.round(width * 0.016), letterSpacing: '0.2em',
        color: '#C9A227', marginBottom: 18,
      }}>{titulo}</div>
      <div style={{
        fontFamily: "'Archivo Black', Poppins, sans-serif",
        fontSize: Math.round(width * 0.062), color: '#F2E9D8',
        opacity: alfa, textShadow: '0 12px 40px rgba(0,0,0,0.8)',
      }}>{linea}</div>
    </div>
  );

  return (
    <AbsoluteFill style={{backgroundColor: '#040407', overflow: 'hidden'}}>
      <Fuentes />
      <Img src={staticFile('biblioteca/fondo_negro_textura.png')}
        style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      <div style={{
        position: 'absolute', left: '50%', top: '22%', width: 2, height: '56%',
        backgroundColor: 'rgba(201,162,39,0.35)', opacity: der,
      }} />
      {col("McDONALD'S", 'EL DINERO', izq, 0.27)}
      {col('CASINO', '¿?', der, 0.73, parpadeo)}
      <Vineta />
    </AbsoluteFill>
  );
};

/* ---------------- G7 · la oficina y la licencia ---------------- */

const G7: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const zoom = rampa(frame, dur, [1.0, 1.28]);
  // Al final el documento se desvanece y queda el fondo vacio.
  const seVa = interpolate(frame, [dur - 22, dur - 14], [1, 0], {
    easing: CURVA, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#0a0d12', overflow: 'hidden'}}>
      <Fuentes />
      <AbsoluteFill style={{transform: `scale(${zoom * 1.04})`}}>
        <Img src={staticFile('biblioteca/fondo_oficina.png')}
          style={{
            width: '100%', height: '100%', objectFit: 'cover',
            filter: 'brightness(0.6) saturate(0.45) blur(3px)',
          }} />
      </AbsoluteFill>
      <AbsoluteFill style={{transform: `scale(${zoom})`, opacity: seVa}}>
        <Img src={staticFile('biblioteca/licencia_documento.png')}
          style={{
            position: 'absolute', left: '50%', top: '52%',
            height: '52%', width: 'auto', transform: 'translate(-50%, -50%)',
            filter: 'brightness(0.95) saturate(0.7) contrast(1.1)',
          }} />
      </AbsoluteFill>
      {/* Lente fria: los capitulos institucionales van sin ambar */}
      <Lente color="#3E5166" x="34%" />
      <Vineta />
    </AbsoluteFill>
  );
};

/* ---------------- G8 · título ---------------- */

const G8: React.FC<{dur: number}> = ({dur}) => {
  const frame = useCurrentFrame();
  const {width} = useVideoConfig();
  const t = interpolate(frame, [2, 8], [0, 1], {
    easing: CURVA, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#040407', overflow: 'hidden'}}>
      <Fuentes />
      <Img src={staticFile('biblioteca/fondo_negro_textura.png')}
        style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div
          style={{
            maxWidth: '76%',
            textAlign: 'center',
            fontFamily: "'Archivo Black', Poppins, sans-serif",
            fontSize: Math.round(width * 0.058),
            lineHeight: 1.08,
            color: '#F2E9D8',
            opacity: t,
            transform: `scale(${1.04 - 0.04 * t})`,
            textShadow: '0 14px 46px rgba(0,0,0,0.85)',
          }}
        >
          LO QUE CUESTA DE VERDAD TENER UN CASINO
        </div>
      </AbsoluteFill>
      <Vineta />
    </AbsoluteFill>
  );
};

/* ---------------- el montaje ---------------- */

// Los cortes van donde los pone la locucion, medidos del SRT.
const CORTES: {hasta: number; escena: React.FC<{dur: number}>}[] = [
  {hasta: 6.98, escena: G1},
  {hasta: 12.24, escena: (p) => <Contador duracion={p.dur} frameFinal={44} />},
  {hasta: 16.52, escena: G3},
  {hasta: 30.32, escena: G4},
  {hasta: 34.16, escena: G5},
  {hasta: 40.32, escena: G6},
  {hasta: 50.6, escena: G7},
  {hasta: 53.64, escena: G8},
];

export const GanchoV2: React.FC = () => {
  let desde = 0;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <Audio src={staticFile('entrada/voz_gancho_full.mp3')} />
      {CORTES.map((corte, i) => {
        const inicio = Math.round(desde * FPS);
        const dur = Math.round(corte.hasta * FPS) - inicio;
        desde = corte.hasta;
        const Escena = corte.escena;
        return (
          <Sequence key={i} from={inicio} durationInFrames={dur}>
            <Escena dur={dur} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
