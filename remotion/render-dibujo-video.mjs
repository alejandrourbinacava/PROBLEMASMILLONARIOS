#!/usr/bin/env node
/** Prueba de movimiento: node render-dibujo-video.mjs <estilo> <escena> <salida.mp4> [frames] */
import {bundle} from '@remotion/bundler';
import {openBrowser, renderFrames, selectComposition} from '@remotion/renderer';
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const [estilo, escena, salida, frames = '100'] = process.argv.slice(2);
const publica = path.join(AQUI, '.publica_dibujo');
const serveUrl = await bundle({entryPoint: path.join(AQUI, 'src', 'dibujo', 'index.ts'), publicDir: publica});
const nav = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
const inputProps = {estilo, escena};
const composition = await selectComposition({serveUrl, id: 'Dibujo', inputProps, puppeteerInstance: nav, logLevel: 'error'});
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'dib-'));
await renderFrames({composition: {...composition, durationInFrames: Number(frames)}, serveUrl, inputProps, outputDir: tmp, imageFormat: 'jpeg', jpegQuality: 92,
  puppeteerInstance: nav, concurrency: 2, onStart: () => undefined, onFrameUpdate: () => undefined, logLevel: 'error'});
const primero = fs.readdirSync(tmp).filter((x) => /^element-\d+\.jpe?g$/.test(x)).sort()[0];
const dig = primero.match(/element-(\d+)\./)[1].length;
spawnSync('ffmpeg', ['-y', '-v', 'error', '-framerate', '25', '-i', path.join(tmp, `element-%0${dig}d.jpeg`), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', salida], {stdio: 'inherit'});
fs.rmSync(tmp, {recursive: true, force: true});
await nav.close({silent: true});
console.log('ok', salida);
