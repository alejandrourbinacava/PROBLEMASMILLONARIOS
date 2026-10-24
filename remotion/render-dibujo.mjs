#!/usr/bin/env node
/** Pruebas de estilo de ilustracion: un fotograma por estilo y escena.
 *   node render-dibujo.mjs <carpeta de salida> [estilos,separados] [escenas,separadas]
 */
import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const [salida = 'dibujos', estilos = 'doodle,plano,recorte,cuaderno,tiza', escenas = 'bar,monedas,fachada'] = process.argv.slice(2);

const publica = path.join(AQUI, '.publica_dibujo');
const fuentes = path.join(publica, 'dibujo', 'fonts');
fs.mkdirSync(fuentes, {recursive: true});
for (const f of ['Fredoka-SemiBold.ttf', 'Anton-Regular.ttf', 'Baloo2-ExtraBold.ttf']) {
  fs.copyFileSync(path.join(AQUI, '..', 'assets', 'fonts', f), path.join(fuentes, f));
}
fs.mkdirSync(salida, {recursive: true});

const serveUrl = await bundle({entryPoint: path.join(AQUI, 'src', 'dibujo', 'index.ts'), publicDir: publica});
const navegador = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
for (const estilo of estilos.split(',')) {
  for (const escena of escenas.split(',')) {
    const inputProps = {estilo, escena};
    const composition = await selectComposition({serveUrl, id: 'Dibujo', inputProps, puppeteerInstance: navegador, logLevel: 'error'});
    const out = path.join(salida, `${estilo}_${escena}.png`);
    await renderStill({composition, serveUrl, output: out, frame: 10, inputProps, puppeteerInstance: navegador, imageFormat: 'png', logLevel: 'error'});
    console.log('ok', out);
  }
}
await navegador.close({silent: true});
