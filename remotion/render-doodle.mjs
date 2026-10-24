#!/usr/bin/env node
/**
 * Renderiza con Remotion los planos "doodle" de un episodio y los deja donde
 * `render_par.py` los espera: `_escenas/NNN_id.mp4`.
 *
 *   node render-doodle.mjs <doodle.json> <carpeta _escenas> [opciones]
 *   --solo <id> | --ids a,b | --max <n>
 *   --stills id:frame,id:frame --outdir <dir>   fotogramas sueltos
 *   --concurrencia <n>
 */
import {bundle} from '@remotion/bundler';
import {openBrowser, renderFrames, renderStill, selectComposition} from '@remotion/renderer';
import {spawnSync} from 'node:child_process';
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
const [manRuta, destino] = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
if (!manRuta) {
  console.error('uso: node render-doodle.mjs <doodle.json> <_escenas> [--solo id] [--stills id:f,..] [--outdir d]');
  process.exit(2);
}
const man = JSON.parse(fs.readFileSync(manRuta, 'utf-8'));
const {fps} = man;
let planos = man.planos;
if (opt('--solo')) planos = planos.filter((p) => p.id === opt('--solo'));
if (opt('--ids')) planos = opt('--ids').split(',').map((id) => planos.find((p) => p.id === id)).filter(Boolean);
if (opt('--max')) planos = planos.slice(0, Number(opt('--max')));

const publica = path.join(AQUI, '.publica_doodle');
const fuentes = path.join(publica, 'doodle', 'fonts');
fs.mkdirSync(fuentes, {recursive: true});
for (const f of ['Fredoka-SemiBold.ttf', 'Baloo2-ExtraBold.ttf']) fs.copyFileSync(path.join(AQUI, '..', 'assets', 'fonts', f), path.join(fuentes, f));

const t0 = Date.now();
const serveUrl = await bundle({entryPoint: path.join(AQUI, 'src', 'doodle', 'index.ts'), publicDir: publica});
console.log(`bundle listo en ${((Date.now() - t0) / 1000).toFixed(1)} s`);
const nav = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
const comp = (plano) => selectComposition({serveUrl, id: 'Plano', inputProps: {plano, fps}, puppeteerInstance: nav, logLevel: 'error'});

if (opt('--stills')) {
  const dir = opt('--outdir', 'stills');
  fs.mkdirSync(dir, {recursive: true});
  for (const par of opt('--stills').split(',')) {
    const [id, frame] = par.split(':');
    const plano = man.planos.find((p) => p.id === id);
    if (!plano) {
      console.error('no existe', id);
      continue;
    }
    const c = await comp(plano);
    const out = path.join(dir, `${id}_f${frame}.png`);
    await renderStill({composition: c, serveUrl, output: out, frame: Number(frame), inputProps: {plano, fps}, puppeteerInstance: nav, imageFormat: 'png', logLevel: 'error'});
    console.log(`${id} f${frame}/${c.durationInFrames} -> ${out}`);
  }
  await nav.close({silent: true});
  process.exit(0);
}

fs.mkdirSync(destino, {recursive: true});
const conc = Number(opt('--concurrencia', Math.max(1, Math.min(4, os.cpus().length))));
let hechos = 0;
let saltados = 0;
for (const plano of planos) {
  const fin = path.join(destino, plano.archivo);
  if (fs.existsSync(fin)) {
    saltados++;
    continue;
  }
  const c = await comp(plano);
  if (c.durationInFrames !== plano.frames) throw new Error(`${plano.id}: dura ${c.durationInFrames} f y el manifiesto pide ${plano.frames}`);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'doodle-'));
  const t1 = Date.now();
  await renderFrames({composition: c, serveUrl, inputProps: {plano, fps}, outputDir: tmp, imageFormat: 'png', puppeteerInstance: nav, concurrency: conc, onStart: () => undefined, onFrameUpdate: () => undefined, logLevel: 'error'});
  const primero = fs.readdirSync(tmp).filter((x) => /^element-\d+\.png$/.test(x)).sort()[0];
  if (!primero) throw new Error(`${plano.id}: sin fotogramas`);
  const dig = primero.match(/element-(\d+)\.png/)[1].length;
  const parcial = fin + '.parcial.mp4';
  const ff = spawnSync('ffmpeg', ['-y', '-v', 'error', '-framerate', String(fps), '-i', path.join(tmp, `element-%0${dig}d.png`), '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', parcial], {stdio: 'inherit'});
  fs.rmSync(tmp, {recursive: true, force: true});
  if (ff.status !== 0) throw new Error(`ffmpeg fallo en ${plano.id}`);
  fs.renameSync(parcial, fin);
  hechos++;
  console.log(`[${hechos + saltados}/${planos.length}] ${plano.archivo} ${plano.frames} f en ${((Date.now() - t1) / 1000).toFixed(1)} s`);
}
await nav.close({silent: true});
console.log(`${hechos} planos renderizados, ${saltados} ya estaban · ${((Date.now() - t0) / 60000).toFixed(1)} min`);
