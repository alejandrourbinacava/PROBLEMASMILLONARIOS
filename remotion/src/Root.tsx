import React from 'react';
import {Composition} from 'remotion';
import {Fuego, Agua} from './Efectos';
import {ParallaxScene, Manifest} from './ParallaxScene';
import {PhotoDrop} from './PhotoDrop';
import {Demo} from './Demo';
import {Secuencia, Paso} from './Secuencia';
import {PruebaMagnates, PasoMagnates} from './PruebaMagnates';
import {Guion, GuionSpec} from './Guion';
import {Episodio, EpisodioSpec} from './Episodio';
import {EscenaA, EscenaASpec} from './EscenaA';
import {EscenaPlan, Plan} from './EscenaPlan';
import {Entrada} from './Entrada';
import {Gancho} from './Gancho';
import {Contador} from './Contador';
import {GanchoV2} from './GanchoV2';
import guionCasa from '../public/guion/escenas.json';
import episodioCasino from '../public/episodio/escenas.json';
import escenaA from '../../config/escena_A.json';
import planEscena from '../public/plan/plan.json';

// Tres capas por escena, ni una mas: fondo, sujeto y elementos/texto.
// Las Z se reparten en los rangos utiles: fondo entre -200 y -400, sujeto en 0,
// elementos entre 100 y 300. Alternar la profundidad del fondo escena a escena
// cambia cuanto parallax hay en cada una, y eso da variedad sin tocar nada mas.
const MAGNATES: PasoMagnates[] = [
  {hasta: 2.18, capaFondo: 'prueba/calle.jpg', capaSujeto: 'prueba/hombre_sil.png',
   capaElementos: 'prueba/polvo.png', texto: 'NO APUESTA CONTRA TI',
   paneo: 'derecha', zFondo: -320, zElementos: 210},

  {hasta: 3.58, capaFondo: 'prueba/noche.jpg', capaSujeto: 'prueba/silueta_sil.png',
   capaElementos: 'prueba/brasas.png', texto: 'TE VENDE TIEMPO',
   paneo: 'izquierda', zFondo: -260, zElementos: 170},

  {hasta: 6.36, capaFondo: 'prueba/avenida.jpg', capaElementos: 'prueba/brasas.png',
   texto: '37 CASILLAS', paneo: 'derecha', zFondo: -380, zElementos: 240},

  {hasta: 9.82, capaFondo: 'prueba/frontal.jpg', capaSujeto: 'prueba/ejecutivo_sil.png',
   capaElementos: 'prueba/polvo.png', texto: 'TE PAGA 36',
   paneo: 'izquierda', zFondo: -300, zElementos: 190},

  {hasta: 12.40, capaFondo: 'prueba/calle.jpg', capaSujeto: 'prueba/mujer_sil.png',
   capaElementos: 'prueba/brasas_densas.png', texto: 'ESA CASILLA ES EL NEGOCIO',
   paneo: 'derecha', zFondo: -340, zElementos: 220},

  {hasta: 15.94, capaFondo: 'prueba/noche.jpg', capaElementos: 'prueba/brasas.png',
   texto: 'EL 2,7% DE CADA EURO', paneo: 'izquierda', zFondo: -220, zElementos: 260},

  {hasta: 17.32, capaFondo: 'prueba/avenida.jpg', capaSujeto: 'prueba/hombre_sil.png',
   capaElementos: 'prueba/polvo.png', texto: 'PARECE POCO',
   paneo: 'derecha', zFondo: -300, zElementos: 180},

  {hasta: 22.28, capaFondo: 'prueba/frontal.jpg', capaSujeto: 'prueba/silueta_sil.png',
   capaElementos: 'prueba/brasas.png', texto: '18 HORAS AL DÍA · 365 DÍAS AL AÑO',
   paneo: 'izquierda', zFondo: -360, zElementos: 200},

  {hasta: 26.90, capaFondo: 'prueba/calle.jpg', capaSujeto: 'prueba/ejecutivo_sil.png',
   capaElementos: 'prueba/brasas_densas.png', texto: '48 MILLONES AL AÑO',
   paneo: 'derecha', zFondo: -280, zElementos: 230},

  {hasta: 30.00, capaFondo: 'prueba/noche.jpg', capaElementos: 'prueba/brasas.png',
   texto: 'PROBLEMAS MILLONARIOS', paneo: 'derecha', zFondo: -400, zElementos: 280},
];

// El manifest vive en public/ junto a las capas, asi que se carga en el
// arranque y el Studio lo recoge sin recompilar.
import manifest from '../public/scene/manifest.json';

const FPS = 25;
const DURACION_S = 6;

// 90 fotogramas de transicion y 4 segundos de escena en medio.
const TRANSICION = 90;
const ESCENA = FPS * 4;

const FOTO = {
  imagenEscena: 'scene/escena.jpg',
  imagenMadera: 'scene/madera.jpg',
};

// Las escenas se cortan por las marcas del SRT de la narracion, no cada N
// segundos: asi el rotulo aparece cuando se dice lo que dice.
//
// Cada escena lleva fondo, UN sujeto y texto. Ni una capa mas. Lo que da
// riqueza no es la cantidad de elementos, es que los pocos que hay se muevan a
// velocidades distintas y que las escenas entren deslizando.
const PASOS: Paso[] = [
  {hasta: 2.18, fondo: 'prueba/calle.jpg', sujeto: 'prueba/hombre.png',
   texto: 'NO APUESTA CONTRA TI', zoom: 'in', ladoSujeto: 0.76, altoSujeto: 0.62},

  {hasta: 3.58, fondo: 'prueba/noche.jpg', sujeto: 'prueba/silueta.png',
   texto: 'TE VENDE TIEMPO', zoom: 'out', ladoSujeto: 0.24, altoSujeto: 0.70,
   entra: 'derecha'},

  {hasta: 6.36, fondo: 'prueba/avenida.jpg', texto: '37 CASILLAS',
   zoom: 'in', entra: 'derecha'},

  {hasta: 9.82, fondo: 'prueba/frontal.jpg', sujeto: 'prueba/ejecutivo.png',
   texto: 'TE PAGA 36', zoom: 'out', ladoSujeto: 0.72, altoSujeto: 0.78,
   entra: 'izquierda'},

  {hasta: 12.40, fondo: 'prueba/calle.jpg', sujeto: 'prueba/mujer.png',
   texto: 'ESA CASILLA ES EL NEGOCIO', zoom: 'in', ladoSujeto: 0.28,
   altoSujeto: 0.74, entra: 'derecha'},

  {hasta: 15.94, fondo: 'prueba/noche.jpg', texto: 'EL 2,7% DE CADA EURO',
   zoom: 'out', entra: 'derecha'},

  {hasta: 17.32, fondo: 'prueba/avenida.jpg', sujeto: 'prueba/hombre.png',
   texto: 'PARECE POCO', zoom: 'in', ladoSujeto: 0.74, altoSujeto: 0.58,
   entra: 'izquierda'},

  {hasta: 22.28, fondo: 'prueba/frontal.jpg', sujeto: 'prueba/silueta.png',
   texto: '18 HORAS AL DÍA · 365 DÍAS AL AÑO', zoom: 'out', ladoSujeto: 0.26,
   altoSujeto: 0.66, entra: 'derecha'},

  {hasta: 26.90, fondo: 'prueba/calle.jpg', sujeto: 'prueba/ejecutivo.png',
   texto: '48 MILLONES AL AÑO', zoom: 'in', ladoSujeto: 0.75, altoSujeto: 0.80,
   entra: 'derecha'},

  {hasta: 30.00, fondo: 'prueba/noche.jpg', texto: 'PROBLEMAS MILLONARIOS',
   zoom: 'in', entra: 'derecha'},
];

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ParallaxScene"
        component={ParallaxScene}
        durationInFrames={FPS * DURACION_S}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          manifest: manifest as Manifest,
          assetDir: 'scene',
          title: undefined,
          // El movimiento lateral es lo que hace VISIBLE la separacion en capas.
          // Un dolly puro no vale: con las z de una escena normal, la capa mas
          // cercana crece un 13,6% y la mas lejana un 7,1%, o sea 6,5 puntos de
          // diferencia, que el ojo no distingue de un zoom sobre una foto plana.
          // Desplazando 260 px, la capa de delante recorre 260 y la del fondo
          // 144: 116 px de diferencia, y ahi si se lee la profundidad.
          startZ: 0,
          endZ: 90,
          panX: 260,
          panY: 0.02,
        }}
      />

      <Composition
        id="PhotoDrop"
        component={PhotoDrop}
        durationInFrames={TRANSICION}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          ...FOTO,
          duracion: TRANSICION,
          direccion: 'drop' as const,
        }}
      />

      <Composition
        id="Demo"
        component={Demo}
        durationInFrames={TRANSICION * 2 + ESCENA}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          ...FOTO,
          duracionTransicion: TRANSICION,
          duracionEscena: ESCENA,
        }}
      />
      <Composition
        id="Prueba"
        component={Secuencia}
        durationInFrames={FPS * 30}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          pasos: PASOS,
          audio: 'prueba/voz.mp3',
          transicion: 10,
        }}
      />

      <Composition
        id="PruebaMagnates"
        component={PruebaMagnates}
        durationInFrames={FPS * 30}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          pasos: MAGNATES,
          audio: 'prueba/voz.mp3',
        }}
      />
      <Composition
        id="GanchoV2"
        component={GanchoV2}
        durationInFrames={1341}
        fps={25}
        width={1920}
        height={1080}
      />

      <Composition
        id="G2Contador"
        component={Contador}
        durationInFrames={100}
        fps={25}
        width={1920}
        height={1080}
        defaultProps={{duracion: 100}}
      />

      <Composition
        id="Gancho"
        component={Gancho}
        durationInFrames={760}
        fps={25}
        width={1920}
        height={1080}
      />

      <Composition
        id="Entrada"
        component={Entrada}
        durationInFrames={250}
        fps={25}
        width={1920}
        height={1080}
      />

      <Composition
        id="EscenaPlan"
        component={EscenaPlan}
        durationInFrames={(planEscena as unknown as Plan).duracion_frames}
        fps={25}
        width={1920}
        height={1080}
        defaultProps={{
          plan: planEscena as unknown as Plan,
          carpeta: 'plan',
        }}
      />

      <Composition
        id="EscenaA"
        component={EscenaA}
        durationInFrames={(escenaA as unknown as EscenaASpec).duracion_frames}
        fps={(escenaA as unknown as EscenaASpec).fps}
        width={(escenaA as unknown as EscenaASpec).ancho}
        height={(escenaA as unknown as EscenaASpec).alto}
        defaultProps={{
          spec: escenaA as unknown as EscenaASpec,
          carpeta: 'escenaA',
        }}
      />

      <Composition
        id="Episodio"
        component={Episodio}
        durationInFrames={(episodioCasino as unknown as EpisodioSpec).escenas.reduce(
          (total, escena) => total + escena.duracion,
          0,
        )}
        fps={(episodioCasino as unknown as EpisodioSpec).fps}
        width={(episodioCasino as unknown as EpisodioSpec).ancho}
        height={(episodioCasino as unknown as EpisodioSpec).alto}
        defaultProps={{
          spec: episodioCasino as unknown as EpisodioSpec,
          carpeta: 'episodio',
          audio: 'episodio/voz.mp3',
        }}
      />

      <Composition
        id="Guion"
        component={Guion}
        durationInFrames={(guionCasa as GuionSpec).duracion_total}
        fps={(guionCasa as GuionSpec).fps}
        width={(guionCasa as GuionSpec).ancho}
        height={(guionCasa as GuionSpec).alto}
        defaultProps={{
          spec: guionCasa as GuionSpec,
          carpeta: 'guion',
          audio: undefined,
        }}
      />
      <Composition
        id="Fuego"
        component={Fuego}
        durationInFrames={48}
        fps={24}
        width={400}
        height={520}
      />
      <Composition
        id="Agua"
        component={Agua}
        durationInFrames={60}
        fps={24}
        width={1920}
        height={400}
      />
    </>
  );
};
