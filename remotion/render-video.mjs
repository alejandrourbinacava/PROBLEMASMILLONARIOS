#!/usr/bin/env node
/**
 * Renderiza un video entero de la piel moderna a partir de su spec.json.
 *   node render-video.mjs <spec.json> <salida.mp4>            video entero (sin audio)
 *   node render-video.mjs <spec.json> --stills <carpeta>      un fotograma por escena, al 88 % de su duracion
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
const t0 = Date.now();
const serveUrl = await bundle({entryPoint: path.join(AQUI, 'src', 'vox', 'index.ts'), publicDir: publica});
const inputProps = {spec};
const composition = await selectComposition({serveUrl, id: 'Video', inputProps, logLevel: 'error'});
console.log(`bundle en ${((Date.now() - t0) / 1000).toFixed(1)} s · ${composition.durationInFrames} fotogramas`);

if (args.includes('--stills')) {
  const dir = opt('--stills');
  fs.mkdirSync(dir, {recursive: true});
  const nav = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
  const solo = opt('--solo') ? opt('--solo').split(',').map(Number) : null;
  for (const [i, e] of spec.escenas.entries()) {
    if (solo && !solo.includes(i)) continue;
    const fr = Math.min(e.f1 - 2, Math.round(e.f0 + (e.f1 - e.f0) * 0.88));
    await renderStill({composition, serveUrl, output: path.join(dir, `${String(i).padStart(2, '0')}_${e.tipo}.jpeg`), frame: fr, inputProps, puppeteerInstance: nav, imageFormat: 'jpeg', jpegQuality: 80, logLevel: 'error'});
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
