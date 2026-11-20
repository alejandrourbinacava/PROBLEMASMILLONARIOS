#!/usr/bin/env node
/**
 * Prueba del estilo VOX por capas.
 *   node render-vox.mjs <salida.mp4>                 video entero
 *   node render-vox.mjs --stills 10,60,95 <carpeta>   fotogramas sueltos
 *   --comp PruebaModerna                              otra composicion (por defecto PruebaVox)
 */
import {bundle} from '@remotion/bundler';
import {openBrowser, renderFrames, renderStill, selectComposition} from '@remotion/renderer';
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const todos = process.argv.slice(2);
const ic = todos.indexOf('--comp');
const COMP = ic >= 0 ? todos[ic + 1] : 'PruebaVox';
const args = ic >= 0 ? todos.filter((_, i) => i !== ic && i !== ic + 1) : todos;
const publica = path.join(AQUI, '.publica_vox');
const fuentes = path.join(publica, 'vox', 'fonts');
fs.mkdirSync(fuentes, {recursive: true});
for (const f of ['PlayfairDisplay-VF.ttf', 'OldStandard-Regular.ttf', 'OldStandard-Italic.ttf', 'LibreFranklin-VF.ttf', 'Caveat-VF.ttf', 'CourierPrime-Regular.ttf', 'CourierPrime-Bold.ttf', 'ArchivoBlack-Regular.ttf', 'Poppins-Black.ttf', 'Poppins-SemiBold.ttf', 'Poppins-Medium.ttf']) {
  fs.copyFileSync(path.join(AQUI, '..', 'assets', 'fonts', f), path.join(fuentes, f));
}
const serveUrl = await bundle({entryPoint: path.join(AQUI, 'src', 'vox', 'index.ts'), publicDir: publica});
const nav = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
const composition = await selectComposition({serveUrl, id: COMP, inputProps: {}, puppeteerInstance: nav, logLevel: 'error'});

if (args[0] === '--stills') {
  const dir = args[2] ?? 'stills';
  fs.mkdirSync(dir, {recursive: true});
  for (const fr of args[1].split(',')) {
    const out = path.join(dir, `vox_${String(fr).padStart(3, '0')}.png`);
    await renderStill({composition, serveUrl, output: out, frame: Number(fr), inputProps: {}, puppeteerInstance: nav, imageFormat: 'png', logLevel: 'error'});
    console.log('ok', out);
  }
} else {
  const salida = args[0] ?? 'prueba_vox.mp4';
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'vox-'));
  await renderFrames({composition, serveUrl, inputProps: {}, outputDir: tmp, imageFormat: 'jpeg', jpegQuality: 94, puppeteerInstance: nav, concurrency: 2, onStart: () => undefined, onFrameUpdate: () => undefined, logLevel: 'error'});
  const primero = fs.readdirSync(tmp).filter((x) => /^element-\d+\.jpe?g$/.test(x)).sort()[0];
  const dig = primero.match(/element-(\d+)\./)[1].length;
  spawnSync('ffmpeg', ['-y', '-v', 'error', '-framerate', '25', '-i', path.join(tmp, `element-%0${dig}d.jpeg`), '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', salida], {stdio: 'inherit'});
  fs.rmSync(tmp, {recursive: true, force: true});
  console.log('ok', salida);
}
await nav.close({silent: true});
