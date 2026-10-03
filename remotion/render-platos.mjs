#!/usr/bin/env node
/**
 * Renderiza con Remotion los planos de PLATO de un episodio y los deja donde
 * `render_par.py` los espera: `_escenas/NNN_id.mp4`.
 *
 *   node render-platos.mjs <platos.json> <carpeta _escenas> [opciones]
 *
 *   --solo <id>        solo ese plano (por su id: cap6_03b)
 *   --ids a,b,c        solo esos planos, en ese orden
 *   --max <n>          solo los n primeros (para probar)
 *   --still <frame>    NO hace video: guarda ese fotograma en --out (con --solo)
 *   --out <fichero>    destino del fotograma suelto
 *   --concurrencia <n> pestanas del navegador a la vez
 *   --estilo <e>       paridad (como Pillow, por defecto) o pro (movimiento nuevo)
 *
 * Por que PNG a ffmpeg y no el codec de Remotion: `render_par.py` codifica
 * fotogramas RGB con libx264 y deja que ffmpeg haga el paso a YUV. Si estos
 * planos se codificaran por otro camino, el papel saldria con otro tono que los
 * planos de metraje que tiene al lado y el corte se veria. Mismo camino, mismo
 * color.
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
const opt = (nombre, defecto = null) => {
  const i = args.indexOf(nombre);
  return i >= 0 ? args[i + 1] : defecto;
};
const [manifiestoRuta, destino] = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
if (!manifiestoRuta) {
  console.error('uso: node render-platos.mjs <platos.json> <_escenas> [--solo id] [--max n] [--still f --out x.png]');
  process.exit(2);
}

const manifiesto = JSON.parse(fs.readFileSync(manifiestoRuta, 'utf-8'));
const {fps, w: W, h: H} = manifiesto;
const estilo = opt('--estilo', 'paridad');
let platos = manifiesto.platos;
if (opt('--solo')) platos = platos.filter((p) => p.id === opt('--solo'));
if (opt('--ids')) {
  const ids = opt('--ids').split(',');
  platos = ids.map((id) => platos.find((p) => p.id === id)).filter(Boolean);
}
if (opt('--max')) platos = platos.slice(0, Number(opt('--max')));
if (!platos.length) {
  console.error('ningun plano coincide');
  process.exit(2);
}

// --- carpeta publica minima: solo las tres tipografias --------------------
// El `public/` de remotion pesa gigas de episodios anteriores y el bundler lo
// copia entero; aqui solo hacen falta las fuentes.
const publica = path.join(AQUI, '.publica_p2');
const fuentes = path.join(publica, 'p2', 'fonts');
fs.mkdirSync(fuentes, {recursive: true});
for (const f of ['Poppins-Black.ttf', 'Poppins-SemiBold.ttf', 'Poppins-Medium.ttf']) {
  fs.copyFileSync(path.join(AQUI, '..', 'assets', 'fonts', f), path.join(fuentes, f));
}

const t0 = Date.now();
const serveUrl = await bundle({
  entryPoint: path.join(AQUI, 'src', 'p2', 'index.ts'),
  publicDir: publica,
});
console.log(`bundle listo en ${((Date.now() - t0) / 1000).toFixed(1)} s`);

const navegador = await openBrowser('chrome', {
  chromiumOptions: {gl: 'angle'},
  logLevel: 'error',
});

const composicion = async (plato) =>
  selectComposition({
    serveUrl,
    id: 'Plato',
    inputProps: {plato, W, H, fps, estilo},
    puppeteerInstance: navegador,
    logLevel: 'error',
  });

// --- modo varios fotogramas sueltos: --stills id:frame,id:frame --outdir x --
if (opt('--stills')) {
  const dir = opt('--outdir', 'stills');
  fs.mkdirSync(dir, {recursive: true});
  for (const par of opt('--stills').split(',')) {
    const [id, frame] = par.split(':');
    const plato = manifiesto.platos.find((p) => p.id === id);
    if (!plato) {
      console.error('no existe el plano', id);
      continue;
    }
    const comp = await composicion(plato);
    const salida = path.join(dir, `${id}_f${frame}.png`);
    await renderStill({
      composition: comp,
      serveUrl,
      output: salida,
      frame: Number(frame),
      inputProps: {plato, W, H, fps, estilo},
      puppeteerInstance: navegador,
      imageFormat: 'png',
      logLevel: 'error',
    });
    console.log(`${id} f${frame}/${comp.durationInFrames} -> ${salida}`);
  }
  await navegador.close({silent: true});
  process.exit(0);
}

// --- modo fotograma suelto ------------------------------------------------
if (opt('--still') !== null) {
  const plato = platos[0];
  const comp = await composicion(plato);
  const salida = opt('--out', 'still.png');
  await renderStill({
    composition: comp,
    serveUrl,
    output: salida,
    frame: Number(opt('--still')),
    inputProps: {plato, W, H, fps, estilo},
    puppeteerInstance: navegador,
    imageFormat: 'png',
    logLevel: 'error',
  });
  console.log(`fotograma ${opt('--still')} de ${plato.id} (${comp.durationInFrames} f) -> ${salida}`);
  await navegador.close({silent: true});
  process.exit(0);
}

// --- video ----------------------------------------------------------------
fs.mkdirSync(destino, {recursive: true});
const concurrencia = Number(opt('--concurrencia', Math.max(1, Math.min(4, os.cpus().length))));
let hechos = 0;
let saltados = 0;
for (const plato of platos) {
  const fin = path.join(destino, plato.archivo);
  if (fs.existsSync(fin)) {
    saltados++;
    continue;
  }
  const comp = await composicion(plato);
  if (comp.durationInFrames !== plato.frames) {
    throw new Error(`${plato.id}: la composicion dura ${comp.durationInFrames} f y el manifiesto pide ${plato.frames}`);
  }
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'plato-'));
  const t1 = Date.now();
  await renderFrames({
    composition: comp,
    serveUrl,
    inputProps: {plato, W, H, fps, estilo},
    outputDir: tmp,
    imageFormat: 'png',
    puppeteerInstance: navegador,
    concurrency: concurrencia,
    onStart: () => undefined,
    onFrameUpdate: () => undefined,
    logLevel: 'error',
  });
  // Remotion rellena con ceros segun el TOTAL de fotogramas (element-000.png
  // para 115, element-0000.png para 1150): se lee del propio nombre.
  const primero = fs.readdirSync(tmp).filter((x) => /^element-\d+\.png$/.test(x)).sort()[0];
  if (!primero) throw new Error(`${plato.id}: Remotion no dejo ningun fotograma`);
  const digitos = primero.match(/element-(\d+)\.png/)[1].length;
  const parcial = fin + '.parcial.mp4';
  const ff = spawnSync(
    'ffmpeg',
    [
      '-y', '-v', 'error',
      '-framerate', String(fps),
      '-i', path.join(tmp, `element-%0${digitos}d.png`),
      '-an',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
      '-pix_fmt', 'yuv420p',
      parcial,
    ],
    {stdio: 'inherit'},
  );
  fs.rmSync(tmp, {recursive: true, force: true});
  if (ff.status !== 0) throw new Error(`ffmpeg fallo en ${plato.id}`);
  fs.renameSync(parcial, fin);
  hechos++;
  console.log(
    `[${hechos + saltados}/${platos.length}] ${plato.archivo} ${plato.frames} f en ${((Date.now() - t1) / 1000).toFixed(1)} s`,
  );
}
await navegador.close({silent: true});
console.log(`${hechos} planos renderizados, ${saltados} ya estaban · ${((Date.now() - t0) / 60000).toFixed(1)} min`);
