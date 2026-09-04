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
 * Escena A, construida literalmente desde config/escena_A.json.
 *
 * Todos los valores vienen del archivo: escalas, centros en pixeles,
 * desenfoques, grades, recorridos, la lente, el texto y el acabado. Aqui no se
 * elige nada ni se completa nada.
 *
 * Los centros van en pixeles sobre un lienzo de 1920x1080, asi que se colocan
 * con left/top absolutos y `translate(-50%, -50%)`, que es lo que convierte una
 * esquina en un centro.
 */

// La curva unica que manda el archivo. Ni spring ni linear.
const CURVA = Easing.bezier(0.33, 0, 0.15, 1);

// La fuente se declara aqui y no se deja al sistema: el archivo pide Archivo
// Black, y si el navegador del render no la encuentra cae en otra sin avisar.
// La fuente se declara con @font-face dentro del componente.
//
// Antes se cargaba con FontFace y delayRender a nivel de modulo, y eso
// bloqueaba el render de CUALQUIER composicion, porque Root importa este
// fichero aunque se este renderizando otra cosa. Una etiqueta <style> no
// tiene ese problema.
const CARA_ARCHIVO = `@font-face {
  font-family: 'Archivo Black';
  src: url('${staticFile('fonts/ArchivoBlack-Regular.ttf')}') format('truetype');
  font-weight: 400;
  font-display: block;
}`;

export type GradeA = {
  brillo: number;
  saturacion: number;
  contraste: number;
  opacidad: number;
};

export type MovimientoA = {
  x_inicio: number;
  x_fin: number;
  frame_inicio: number;
  frame_fin: number;
};

export type CapaA = {
  orden: number;
  archivo: string;
  escala?: number;
  alto_px?: number;
  centro_x: number;
  centro_y: number;
  desenfoque_px: number;
  grade: GradeA;
  sombra_suelo?: {
    ancho_px: number;
    alto_px: number;
    opacidad: number;
    desenfoque_px: number;
  };
  movimiento: MovimientoA;
};

export type EscenaASpec = {
  fps: number;
  ancho: number;
  alto: number;
  duracion_frames: number;
  CAPAS: CapaA[];
  LENTE: {
    color: string;
    ancho_px: number;
    alto_px: number;
    centro_x: number;
    centro_y: number;
    desenfoque_px: number;
    blend: string;
    opacidad: number;
  };
  TEXTO: {
    linea: string;
    fuente: string;
    tamano_px: number;
    color: string;
    centro_x: number;
    centro_y: number;
    ancho_max_px: number;
    sombra: {desenfoque_px: number; opacidad: number};
    entrada: {
      frame_inicio: number;
      frame_fin: number;
      x_desde: number;
      x_hasta: number;
      opacidad_desde: number;
      opacidad_hasta: number;
    };
  };
  ACABADO: {vineta: number; grano: number; negros: number};
  SALIDA: {
    frame_inicio: number;
    frame_fin: number;
    conjunto_x_desde: number;
    conjunto_x_hasta: number;
  };
};

const rampa = (
  frame: number,
  desde: number,
  hasta: number,
  a: number,
  b: number,
) =>
  interpolate(frame, [desde, hasta], [a, b], {
    easing: CURVA,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

const filtro = (g: GradeA, desenfoque: number) => {
  const partes = [
    `brightness(${g.brillo})`,
    `saturate(${g.saturacion})`,
    `contrast(${g.contraste})`,
  ];
  if (desenfoque > 0) partes.push(`blur(${desenfoque}px)`);
  return partes.join(' ');
};

export const EscenaA: React.FC<{spec: EscenaASpec; carpeta: string}> = ({
  spec,
  carpeta,
}) => {
  const frame = useCurrentFrame();

  // A partir del frame de salida, TODO el conjunto se desliza fuera de cuadro.
  const salida = rampa(
    frame,
    spec.SALIDA.frame_inicio,
    spec.SALIDA.frame_fin,
    spec.SALIDA.conjunto_x_desde,
    spec.SALIDA.conjunto_x_hasta,
  );

  const t = spec.TEXTO;
  const textoX = rampa(
    frame,
    t.entrada.frame_inicio,
    t.entrada.frame_fin,
    t.entrada.x_desde,
    t.entrada.x_hasta,
  );
  const textoOpacidad = rampa(
    frame,
    t.entrada.frame_inicio,
    t.entrada.frame_fin,
    t.entrada.opacidad_desde,
    t.entrada.opacidad_hasta,
  );

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <style>{CARA_ARCHIVO}</style>
      <AbsoluteFill style={{transform: `translateX(${salida}px)`}}>
        {/* Las tres capas, en el orden del archivo */}
        {[...spec.CAPAS]
          .sort((a, b) => a.orden - b.orden)
          .map((capa) => {
            const x = rampa(
              frame,
              capa.movimiento.frame_inicio,
              capa.movimiento.frame_fin,
              capa.movimiento.x_inicio,
              capa.movimiento.x_fin,
            );
            return (
              <React.Fragment key={capa.archivo}>
                {/* La sombra va DEBAJO de su capa, apoyada en la base del
                    sujeto: centro_y mas la mitad de su alto. */}
                {capa.sombra_suelo ? (
                  <div
                    style={{
                      position: 'absolute',
                      left: capa.centro_x + x,
                      top: capa.centro_y + (capa.alto_px ?? 0) / 2,
                      width: capa.sombra_suelo.ancho_px,
                      height: capa.sombra_suelo.alto_px,
                      transform: 'translate(-50%, -50%)',
                      borderRadius: '50%',
                      backgroundColor: '#000',
                      opacity: capa.sombra_suelo.opacidad,
                      filter: `blur(${capa.sombra_suelo.desenfoque_px}px)`,
                    }}
                  />
                ) : null}
                <Img
                  src={staticFile(`${carpeta}/${capa.archivo}`)}
                  style={{
                    position: 'absolute',
                    left: capa.centro_x + x,
                    top: capa.centro_y,
                    // `escala` multiplica el tamano natural; `alto_px` fija la
                    // altura en pixeles. El archivo usa una u otra por capa.
                    height: capa.alto_px ? capa.alto_px : undefined,
                    width: capa.alto_px ? 'auto' : spec.ancho,
                    transform: `translate(-50%, -50%) scale(${capa.escala ?? 1})`,
                    opacity: capa.grade.opacidad,
                    filter: filtro(capa.grade, capa.desenfoque_px),
                  }}
                />
              </React.Fragment>
            );
          })}

        {/* La lente: ovalo de color muy desenfocado, en modo pantalla */}
        <AbsoluteFill style={{mixBlendMode: spec.LENTE.blend as 'screen'}}>
          <div
            style={{
              position: 'absolute',
              left: spec.LENTE.centro_x,
              top: spec.LENTE.centro_y,
              width: spec.LENTE.ancho_px,
              height: spec.LENTE.alto_px,
              transform: 'translate(-50%, -50%)',
              borderRadius: '50%',
              backgroundColor: spec.LENTE.color,
              opacity: spec.LENTE.opacidad,
              filter: `blur(${spec.LENTE.desenfoque_px}px)`,
            }}
          />
        </AbsoluteFill>

        {/* El texto entra por la derecha mientras las capas se van a la izquierda */}
        <div
          style={{
            position: 'absolute',
            left: textoX,
            top: t.centro_y,
            transform: 'translate(-50%, -50%)',
            width: t.ancho_max_px,
            textAlign: 'center',
            fontFamily: `'${t.fuente}', 'Archivo Black', sans-serif`,
            fontWeight: 400,
            fontSize: t.tamano_px,
            lineHeight: 1.06,
            color: t.color,
            opacity: textoOpacidad,
            textShadow: `0 10px ${t.sombra.desenfoque_px}px rgba(0,0,0,${t.sombra.opacidad})`,
          }}
        >
          {t.linea}
        </div>
      </AbsoluteFill>

      {/* Acabado: negros levantados, vineta y grano, en ese orden */}
      <AbsoluteFill
        style={{
          backgroundColor: '#fff',
          opacity: spec.ACABADO.negros,
          mixBlendMode: 'lighten',
          pointerEvents: 'none',
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,${spec.ACABADO.vineta}) 100%)`,
          pointerEvents: 'none',
        }}
      />
      <Grano intensidad={spec.ACABADO.grano} />
    </AbsoluteFill>
  );
};

/**
 * Grano.
 *
 * Se dibuja con un patron SVG de ruido, que es determinista: el mismo
 * fotograma da siempre el mismo grano y el render se puede repetir.
 */
const Grano: React.FC<{intensidad: number}> = ({intensidad}) => (
  <AbsoluteFill style={{opacity: intensidad / 100, pointerEvents: 'none'}}>
    <svg width="100%" height="100%">
      <filter id="ruido">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" />
      </filter>
      <rect width="100%" height="100%" filter="url(#ruido)" />
    </svg>
  </AbsoluteFill>
);
