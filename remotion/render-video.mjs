#!/usr/bin/env node
/**
 * Renderiza un video entero de la piel moderna a partir de su spec.json.
 *   node render-video.mjs <spec.json> <salida.mp4>            video entero (sin audio)
 *   node render-video.mjs <spec.json> --stills <carpeta>      un fotograma por escena, al 88 % de su duracion
 *   --fracs 0.3,0.6,0.9        (con --stills) varios fotogramas por escena
 *   --solo 3,7,12              (con --stills) solo esas escenas
 *   --fotogramas 10,50,120     (con --stills) fotogramas absolutos sueltos
 *   --desde <f> --hasta <f>    solo ese tramo de fotogramas
 *   --concurrencia <n>
 */
import {bundle} from '@remotion/bundler';
import {openBrowser, renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (n, d = null) => {
  const i = args.indexOf(n);
  return i >= 0 ? args[i + 1] : d;
};
const spec = JSON.parse(fs.readFileSync(args[0], 'utf-8'));
const publica = path.join(AQUI, '.publica_vox');
const fuentes = path.join(publica, 'vox', 'fonts');
fs.mkdirSync(fuentes, {recursive: true});
for (const f of ['PlayfairDisplay-VF.ttf', 'OldStandard-Regular.ttf', 'OldStandard-Italic.ttf', 'LibreFranklin-VF.ttf', 'Caveat-VF.ttf', 'CourierPrime-Regular.ttf', 'CourierPrime-Bold.ttf', 'ArchivoBlack-Regular.ttf', 'Poppins-Black.ttf', 'Poppins-SemiBold.ttf', 'Poppins-Medium.ttf']) {
  fs.copyFileSync(path.join(AQUI, '..', 'assets', 'fonts', f), path.join(fuentes, f));
}
// metraje y fotos que cita el spec: {nombre: ruta dentro del repo}
const media = path.join(publica, 'vox', 'media');
fs.mkdirSync(media, {recursive: true});
const quiere = new Set(Object.keys(spec.medios ?? {}));
for (const viejo of fs.readdirSync(media)) if (!quiere.has(viejo)) fs.rmSync(path.join(media, viejo));
for (const [nombre, rel] of Object.entries(spec.medios ?? {})) {
  const src = path.join(AQUI, '..', rel);
  if (!fs.existsSync(src)) {
    console.error('FALTA EL MEDIO ' + rel);
    process.exit(1);
  }
  const dst = path.join(media, nombre);
  if (!fs.existsSync(dst) || fs.statSync(dst).size !== fs.statSync(src).size) fs.copyFileSync(src, dst);
}
const t0 = Date.now();
const serveUrl = await bundle({entryPoint: path.join(AQUI, 'src', 'vox', 'index.ts'), publicDir: publica, outDir: path.join(AQUI, '.bundle_vox')});
const inputProps = {spec};
const composition = await selectComposition({serveUrl, id: 'Video', inputProps, logLevel: 'error'});
console.log(`bundle en ${((Date.now() - t0) / 1000).toFixed(1)} s · ${composition.durationInFrames} fotogramas`);

if (args.includes('--fotogramas')) {
  // fotogramas sueltos (absolutos): --fotogramas 10,50,120 --stills <carpeta>
  const dir = opt('--stills');
  fs.mkdirSync(dir, {recursive: true});
  const nav = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
  for (const fr of opt('--fotogramas').split(',').map(Number)) {
    await renderStill({composition, serveUrl, output: path.join(dir, `f${String(fr).padStart(5, '0')}.jpeg`), frame: Math.min(composition.durationInFrames - 1, fr), inputProps, puppeteerInstance: nav, imageFormat: 'jpeg', jpegQuality: 82, logLevel: 'error'});
  }
  await nav.close({silent: true});
  console.log('fotogramas en', dir);
} else if (args.includes('--stills')) {
  const dir = opt('--stills');
  fs.mkdirSync(dir, {recursive: true});
  const nav = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
  const solo = opt('--solo') ? opt('--solo').split(',').map(Number) : null;
  for (const [i, e] of spec.escenas.entries()) {
    if (solo && !solo.includes(i)) continue;
    // --fracs 0.3,0.6,0.9 saca varios fotogramas por escena, para ver las capas entrar y salir
    const fracs = (opt('--fracs') ?? '0.88').split(',').map(Number);
    for (const [k, fr0] of fracs.entries()) {
      const fr = Math.min(e.f1 - 2, Math.round(e.f0 + (e.f1 - e.f0) * fr0));
      await renderStill({composition, serveUrl, output: path.join(dir, `${String(i).padStart(2, '0')}${fracs.length > 1 ? 'abcdef'[k] : ''}_${e.tipo}.jpeg`), frame: fr, inputProps, puppeteerInstance: nav, imageFormat: 'jpeg', jpegQuality: 80, logLevel: 'error'});
    }
  }
  await nav.close({silent: true});
  console.log('fotogramas en', dir);
} else {
  const salida = args[1];
  const desde = Number(opt('--desde', 0));
  const hasta = Number(opt('--hasta', composition.durationInFrames - 1));
  let ult = 0;
  await renderMedia({
    composition, serveUrl, codec: 'h264', outputLocation: salida, inputProps, frameRange: [desde, hasta], crf: 18, pixelFormat: 'yuv420p',
    concurrency: Number(opt('--concurrencia', Math.max(1, Math.min(4, os.cpus().length)))), chromiumOptions: {gl: 'angle'}, logLevel: 'error',
    onProgress: ({renderedFrames}) => {
      if (renderedFrames - ult >= 500) {
        ult = renderedFrames;
        console.log(`${renderedFrames}/${hasta - desde + 1} fotogramas · ${((Date.now() - t0) / 60000).toFixed(1)} min`);
      }
    },
  });
  console.log(`ok ${salida} · ${((Date.now() - t0) / 60000).toFixed(1)} min`);
}
