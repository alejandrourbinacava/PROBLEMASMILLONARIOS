#!/usr/bin/env node
/** node render-doodle-hoja.mjs <salida.png> [papel] [desde] [hasta] */
import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const [salida, papel = 'crema', desde = '0', hasta = '99'] = process.argv.slice(2);
const publica = path.join(AQUI, '.publica_doodle');
const fuentes = path.join(publica, 'doodle', 'fonts');
fs.mkdirSync(fuentes, {recursive: true});
for (const f of ['Fredoka-SemiBold.ttf', 'Baloo2-ExtraBold.ttf']) fs.copyFileSync(path.join(AQUI, '..', 'assets', 'fonts', f), path.join(fuentes, f));
const serveUrl = await bundle({entryPoint: path.join(AQUI, 'src', 'doodle', 'index.ts'), publicDir: publica});
const nav = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}, logLevel: 'error'});
const inputProps = {papel, desde: Number(desde), hasta: Number(hasta)};
const composition = await selectComposition({serveUrl, id: 'Hoja', inputProps, puppeteerInstance: nav, logLevel: 'error'});
await renderStill({composition, serveUrl, output: salida, frame: 0, inputProps, puppeteerInstance: nav, imageFormat: 'png', logLevel: 'error'});
await nav.close({silent: true});
console.log('ok', salida);
