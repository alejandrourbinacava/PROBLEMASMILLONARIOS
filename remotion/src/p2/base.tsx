import React, {useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

/**
 * Tipos del manifiesto que escribe `parallax2/exportar_platos.py`, la paleta
 * del tema de papel y las tres tipografias del canal.
 */

export type Plato = {
  archivo: string;
  frames: number;
  id: string;
  duracion: number;
  fondo_titulo: string;
  acento: number[];
  fase: number;
  // La ficha del grafico tal como sale de motion_banco / motion_manual, mas
  // los colores ya resueltos a RGB (`_ac`, `_destacar`, `_colores`...).
  grafico: any | null;
  texto_pantalla: any | null;
  lat_ent: number | null;
  lat_sal: number | null;
};

export type Manifiesto = {
  fps: number;
  w: number;
  h: number;
  paleta: Record<string, any>;
  total: number;
  platos: Plato[];
};

/** El tema `papel`. Es el unico que usa el canal ahora mismo. */
export const P = {
  acento: [206, 32, 38] as number[],
  aviso: [206, 32, 38] as number[],
  serie: [58, 64, 74] as number[],
  ok: [26, 122, 72] as number[],
  tinta: [24, 24, 28] as number[], // en el motor se llama "hueso"
  tenue: [124, 128, 136] as number[],
  carta: [255, 255, 255] as number[],
  papel: [246, 244, 238] as number[],
};

export const NEGRA = 'P2 Black';
export const FUERTE = 'P2 SemiBold';
export const MEDIA = 'P2 Medium';

const CARAS: [string, string][] = [
  [NEGRA, 'p2/fonts/Poppins-Black.ttf'],
  [FUERTE, 'p2/fonts/Poppins-SemiBold.ttf'],
  [MEDIA, 'p2/fonts/Poppins-Medium.ttf'],
];

let cargadas: Promise<void> | null = null;

/** Carga las tres tipografias UNA vez y bloquea el render hasta tenerlas. */
const cargaFuentes = () => {
  if (!cargadas) {
    cargadas = Promise.all(
      CARAS.map(async ([nombre, ruta]) => {
        const cara = new FontFace(nombre, `url(${staticFile(ruta)})`);
        await cara.load();
        (document as any).fonts.add(cara);
      }),
    ).then(() => undefined);
  }
  return cargadas;
};

/**
 * Sin esto el video sale en la tipografia de reserva del navegador y NO falla:
 * se ve al revisarlo. Es el mismo fallo que ya hubo con las dos rutas de
 * fuente absolutas del motor de Pillow.
 */
export const useFuentes = () => {
  const [listo, setListo] = useState(false);
  const [handle] = useState(() => delayRender('fuentes del canal'));
  useEffect(() => {
    cargaFuentes()
      .then(() => {
        setListo(true);
        continueRender(handle);
      })
      .catch((e) => {
        console.error('no cargaron las fuentes', e);
        continueRender(handle);
      });
  }, [handle]);
  return listo;
};

let lienzo: CanvasRenderingContext2D | null = null;

/** Ancho de un texto en pixeles, con tracking opcional (como `_ancho_esp`). */
export const medir = (txt: string, px: number, familia: string, esp = 0) => {
  if (!lienzo) lienzo = document.createElement('canvas').getContext('2d');
  if (!lienzo) return txt.length * px * 0.55;
  lienzo.font = `${px}px "${familia}"`;
  return lienzo.measureText(txt).width + esp * Math.max(0, txt.length - 1);
};

/** Texto SVG con su linea de base exacta: lo que `anchor="ls"` hacia en PIL. */
export const T: React.FC<{
  x: number;
  y: number;
  px: number;
  familia: string;
  fill: string;
  anchor?: 'start' | 'middle' | 'end';
  esp?: number;
  op?: number;
  children: React.ReactNode;
}> = ({x, y, px, familia, fill, anchor = 'start', esp = 0, op = 1, children}) => (
  <text
    x={x}
    y={y}
    fontFamily={`"${familia}"`}
    fontSize={px}
    fill={fill}
    fillOpacity={op}
    textAnchor={anchor}
    style={{letterSpacing: esp ? `${esp}px` : undefined}}
  >
    {children}
  </text>
);
