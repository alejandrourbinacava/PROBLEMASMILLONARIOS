/*
 * El circuito del dinero de Wachovia, en After Effects.
 *
 *   "C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\AfterFX.exe" -r ae\circuito.jsx
 *
 * Se ejecuta sin tocar la interfaz: construye la composicion, la guarda y
 * sale. El render lo hace aerender por consola.
 *
 * Por que este plano y no otro: es lo que el pipeline de codigo NO puede
 * hacer. Un SVG puede dibujar la flecha, pero no puede TRAZARLA -que se vaya
 * dibujando- ni ponerle desenfoque de movimiento de verdad. Aqui las flechas
 * se trazan con trim paths y todo lleva motion blur real, que es lo que mas
 * separa una animacion cara de una barata.
 *
 * ExtendScript es ES3: ni let, ni arrow functions, ni plantillas de cadena.
 */

// ------------------------------------------------------------- constantes
var W = 1920, H = 1080, FPS = 30, DUR = 9.0;

var NEGRO = [0, 0, 0];
var AMBAR = [1.0, 0.690, 0.235];        // #FFB03C
var ROJO = [0.910, 0.337, 0.251];       // #E85640
var PAPEL = [0.929, 0.906, 0.855];      // #EDE7DA
var GRIS = [0.353, 0.408, 0.494];

var NODOS = [
  {t: "EFECTIVO",        p: "el dinero de la droga",    x: 300},
  {t: "CASA DE CAMBIO",  p: "México",                   x: 760},
  {t: "MIAMI",           p: "disfrazado de remesas",    x: 1220},
  {t: "ACTIVOS",         p: "aviones, inmuebles",       x: 1680}
];

var Y = 520;                 // linea del circuito
var ENTRA = 0.55;            // cada nodo entra con este retardo

// ------------------------------------------------------------- utilidades
function seg(s) { return s; }

function texto(comp, cadena, x, y, tam, color, negrita) {
  var capa = comp.layers.addText(cadena);
  var doc = capa.property("Source Text").value;
  doc.resetCharStyle();
  doc.fontSize = tam;
  doc.fillColor = color;
  doc.applyFill = true;
  doc.applyStroke = false;
  doc.font = negrita ? "Arial-BoldMT" : "ArialMT";
  doc.justification = ParagraphJustification.CENTER_JUSTIFY;
  capa.property("Source Text").setValue(doc);
  capa.property("Transform").property("Position").setValue([x, y]);
  capa.motionBlur = true;
  return capa;
}

/* Un rectangulo de contorno. Se construye a mano porque addShape() da una
   capa vacia: hay que colgarle el grupo, el trazado y el trazo. */
function caja(comp, x, y, w, h, color, grosor) {
  var capa = comp.layers.addShape();
  capa.name = "caja";
  var raiz = capa.property("ADBE Root Vectors Group");
  var grupo = raiz.addProperty("ADBE Vector Group");
  var conts = grupo.property("ADBE Vectors Group");

  var rect = conts.addProperty("ADBE Vector Shape - Rect");
  rect.property("ADBE Vector Rect Size").setValue([w, h]);
  rect.property("ADBE Vector Rect Roundness").setValue(4);

  var trazo = conts.addProperty("ADBE Vector Graphic - Stroke");
  trazo.property("ADBE Vector Stroke Color").setValue(color);
  trazo.property("ADBE Vector Stroke Width").setValue(grosor);

  capa.property("Transform").property("Position").setValue([x, y]);
  capa.motionBlur = true;
  return capa;
}

/* La flecha entre dos nodos, con trim paths para que se DIBUJE. Esto es lo
   que no se puede hacer con un SVG estatico. */
function flecha(comp, x0, x1, y, color, t0) {
  var capa = comp.layers.addShape();
  capa.name = "flecha";
  var raiz = capa.property("ADBE Root Vectors Group");
  var grupo = raiz.addProperty("ADBE Vector Group");
  var conts = grupo.property("ADBE Vectors Group");

  var camino = conts.addProperty("ADBE Vector Shape - Group");
  var forma = new Shape();
  forma.vertices = [[x0, y], [x1, y]];
  forma.closed = false;
  camino.property("ADBE Vector Shape").setValue(forma);

  var trazo = conts.addProperty("ADBE Vector Graphic - Stroke");
  trazo.property("ADBE Vector Stroke Color").setValue(color);
  trazo.property("ADBE Vector Stroke Width").setValue(4);
  trazo.property("ADBE Vector Stroke Line Cap").setValue(2);

  // TRIM PATHS: el trazo se dibuja de 0 a 100 en medio segundo
  var trim = conts.addProperty("ADBE Vector Filter - Trim");
  var fin = trim.property("ADBE Vector Trim End");
  fin.setValueAtTime(t0, 0);
  fin.setValueAtTime(t0 + 0.45, 100);
  suavizar(fin);

  capa.property("Transform").property("Position").setValue([0, 0]);
  capa.motionBlur = true;
  return capa;
}

function suavizar(prop) {
  var n = prop.numKeys;
  for (var i = 1; i <= n; i++) {
    prop.setInterpolationTypeAtKey(i, KeyframeInterpolationType.BEZIER,
                                   KeyframeInterpolationType.BEZIER);
  }
  if (n >= 2) {
    var e = new KeyframeEase(0, 75);
    prop.setTemporalEaseAtKey(1, [e], [e]);
    prop.setTemporalEaseAtKey(n, [e], [e]);
  }
}

/* Entrada: sube y aparece. El rebasamiento es lo que se lee como vivo. */
function entrar(capa, t0, dy) {
  var pos = capa.property("Transform").property("Position");
  var p = pos.value;
  pos.setValueAtTime(t0, [p[0], p[1] + dy]);
  pos.setValueAtTime(t0 + 0.38, [p[0], p[1] - 6]);
  pos.setValueAtTime(t0 + 0.52, p);
  suavizar(pos);

  var op = capa.property("Transform").property("Opacity");
  op.setValueAtTime(t0, 0);
  op.setValueAtTime(t0 + 0.22, 100);
  suavizar(op);
}

// ---------------------------------------------------------------- montaje
function construir() {
  app.beginUndoGroup("circuito");
  app.newProject();
  var proy = app.project;
  proy.bitsPerChannel = 16;

  var comp = proy.items.addComp("Circuito", W, H, 1, DUR, FPS);
  comp.bgColor = NEGRO;
  comp.motionBlur = true;                 // el interruptor de la comp
  comp.shutterAngle = 220;                // mas de 180: se nota, y aqui queremos que se note

  // fondo negro solido, para que el render no salga con alfa
  var fondo = comp.layers.addSolid(NEGRO, "fondo", W, H, 1);
  fondo.moveToEnd();

  // rotulo de arriba
  var titulo = texto(comp, "EL CIRCUITO", W / 2, 150, 34, AMBAR, true);
  titulo.property("Source Text").value.tracking = 400;
  entrar(titulo, 0.15, 26);

  // las flechas van DEBAJO de los nodos: se dibujan antes de que caiga la caja
  for (var i = 0; i < NODOS.length - 1; i++) {
    flecha(comp, NODOS[i].x + 130, NODOS[i + 1].x - 130, Y, GRIS,
           0.5 + i * ENTRA + 0.30);
  }

  // los cuatro nodos
  for (var j = 0; j < NODOS.length; j++) {
    var n = NODOS[j];
    var t0 = 0.5 + j * ENTRA;
    var c = caja(comp, n.x, Y, 250, 118, (j === 3) ? ROJO : AMBAR, 3);
    entrar(c, t0, 40);
    var tt = texto(comp, n.t, n.x, Y + 4, 30, PAPEL, true);
    entrar(tt, t0 + 0.06, 40);
    var tp = texto(comp, n.p, n.x, Y + 108, 22, GRIS, false);
    entrar(tp, t0 + 0.12, 30);
  }

  // la cifra. Cuenta sola con una expresion: no hay que poner keyframes.
  var cifra = texto(comp, "0", W / 2, 830, 96, PAPEL, true);
  cifra.property("Source Text").expression =
    "t = linear(time, 3.0, 5.4, 0, 378400);\r" +
    "n = Math.round(t);\r" +
    "s = n.toString();\r" +
    "out = '';\r" +
    "for (i = 0; i < s.length; i++) {\r" +
    "  if (i > 0 && (s.length - i) % 3 == 0) out += '.';\r" +
    "  out += s.charAt(i);\r" +
    "}\r" +
    "out + '  millones de dolares';";
  entrar(cifra, 2.9, 34);

  var pie = texto(comp, "Wachovia, 2010 · acuerdo con el Departamento de Justicia",
                  W / 2, 900, 24, GRIS, false);
  entrar(pie, 5.4, 22);

  var multa = texto(comp, "MULTA: 160 MILLONES · CERO DETENIDOS",
                    W / 2, 975, 30, ROJO, true);
  entrar(multa, 6.3, 26);

  app.endUndoGroup();
  return comp;
}

// ------------------------------------------------------------------ salida
var comp = construir();
var aqui = new File($.fileName).parent;
var aep = new File(aqui.fsName + "/circuito.aep");
app.project.save(aep);

// se deja la cola preparada para aerender, que es quien renderiza
var item = app.project.renderQueue.items.add(comp);
var mod = item.outputModule(1);
try { mod.applyTemplate("Lossless with Alpha"); } catch (e) {}
mod.file = new File(aqui.fsName + "/salida/circuito.mov");
app.project.save(aep);

$.writeln("aep escrito en " + aep.fsName);
app.quit();
