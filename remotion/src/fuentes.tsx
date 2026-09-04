import React from 'react';
import {staticFile} from 'remotion';

/**
 * Las tipografias del canal, declaradas en un sitio.
 *
 * Estaban solo dentro de EscenaA, asi que cualquier otra composicion
 * renderizaba con la fuente de reserva del navegador y no habia aviso: el
 * contador de G2 salio en una sans fina en vez de en Archivo Black.
 *
 * `font-display: block` obliga al navegador a esperar en vez de pintar con la
 * de reserva, que es lo que hay que hacer en un render.
 */
export const CARAS = `
@font-face {
  font-family: 'Archivo Black';
  src: url('${staticFile('fonts/ArchivoBlack-Regular.ttf')}') format('truetype');
  font-weight: 400;
  font-display: block;
}`;

export const Fuentes: React.FC = () => <style>{CARAS}</style>;
