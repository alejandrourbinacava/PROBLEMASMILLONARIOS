/*
 * Parallax de verdad: capas en 3D con camara, no capas en 2D a distinta
 * velocidad.
 *
 *   "...\AfterFX.exe" -r ae\parallax3d.jsx
 *
 * Esta es la prueba donde After Effects deberia ganar, y por una razon
 * concreta: el pipeline de codigo NO mueve una camara, mueve cada capa a una
 * velocidad distinta. Se parece, pero no es lo mismo.
 *
 *   - Con capas 2D, el desplazamiento es lineal: todo se mueve en linea
 *     recta. Con una camara 3D hay PERSPECTIVA: los bordes del cuadro se
 *     abren, las capas cercanas cruzan mas rapido en los laterales que en el
 *     centro, y al acercarse la escena se "abre".
 *   - La profundidad de campo es real: el desenfoque sale de la distancia al
 *     plano de foco, no de un blur fijo por rol.
 *   - Y el desenfoque de movimiento tambien.
 *
 * Las tres capas son las del gancho del casino: cielo, fachada y multitud de
 * espaldas. Las mismas que usa el pipeline, para poder comparar.
 */

var W = 1920, H = 1080, FPS = 30, DUR = 8.0;
var ZOOM = 1778;          // la distancia de camara por defecto de una comp 1920

// archivo, Z, escala base (ancho del png), y, nombre
var CAPAS = [
  {f: "f01_cielo_estrellado.png", z: 2600, ancho: 2048, y: 470, n: "cielo"},
  {f: "01_casino.png",            z:  620, ancho: 2096, y: 560, n: "fachada"},
  {f: "01_multitud.png",          z: -360, ancho: 2048, y: 1010, n: "multitud"}
];

function proyecto() {
  var aqui = new File($.fileName).parent;
  return new Folder(aqui.parent.fsName + "/parallax2/proyecto");
}

function importar(nombre) {
  var f = new File(proyecto().fsName + "/" + nombre);
  if (!f.exists) throw new Error("no encuentro " + f.fsName);
  var io = new ImportOptions(f);
  return app.project.importFile(io);
}

function suavizar(prop) {
  var n = prop.numKeys;
  for (var i = 1; i <= n; i++) {
    prop.setInterpolationTypeAtKey(i, KeyframeInterpolationType.BEZIER,
                                   KeyframeInterpolationType.BEZIER);
  }
  if (n >= 2) {
    var e = new KeyframeEase(0, 60);
    prop.setTemporalEaseAtKey(1, [e], [e]);
    prop.setTemporalEaseAtKey(n, [e], [e]);
  }
}

function construir() {
  app.beginUndoGroup("parallax3d");
  app.newProject();
  app.project.bitsPerChannel = 16;

  var comp = app.project.items.addComp("Parallax3D", W, H, 1, DUR, FPS);
  comp.bgColor = [0, 0, 0];
  comp.motionBlur = true;
  comp.shutterAngle = 180;

  for (var i = 0; i < CAPAS.length; i++) {
    var c = CAPAS[i];
    var capa = comp.layers.add(importar(c.f));
    capa.name = c.n;
    capa.threeDLayer = true;               // ESTO es lo que cambia todo
    capa.motionBlur = true;

    // Una capa a Z se ve mas pequena en proporcion ZOOM/(ZOOM+Z). Se
    // compensa en la escala para que todas entren encuadradas igual que en
    // el pipeline 2D, y asi lo unico que cambia entre las dos versiones sea
    // la camara.
    var llenar = (W / c.ancho) * 100;
    var comp_z = (ZOOM + c.z) / ZOOM;
    var s = llenar * comp_z * 1.06;        // 6% de sangrado para el movimiento
    capa.property("Transform").property("Scale").setValue([s, s, 100]);
    capa.property("Transform").property("Position")
        .setValue([W / 2, c.y * comp_z - (comp_z - 1) * H / 2, c.z]);

    // el fondo, mas apagado: es lo que hace que el sujeto destaque
    if (i === 0) capa.property("Transform").property("Opacity").setValue(72);
  }

  // ---- la camara. Un solo nodo: se mueve y mira adelante.
  var cam = comp.layers.addCamera("camara", [W / 2, H / 2]);
  cam.property("Transform").property("Point of Interest")
     .setValue([W / 2, H / 2, 620]);

  var pos = cam.property("Transform").property("Position");
  // dolly hacia dentro y deriva lateral: la deriva es la que revela la
  // perspectiva, el dolly solo la que da profundidad
  pos.setValueAtTime(0.0, [W / 2 - 130, H / 2 + 40, -ZOOM]);
  pos.setValueAtTime(DUR, [W / 2 + 130, H / 2 - 30, -ZOOM + 620]);
  suavizar(pos);

  // ---- profundidad de campo REAL: el desenfoque sale de la distancia
  var op = cam.property("ADBE Camera Options Group");
  op.property("ADBE Camera Depth of Field").setValue(1);
  op.property("ADBE Camera Focus Distance").setValue(ZOOM + 620);  // la fachada
  op.property("ADBE Camera Aperture").setValue(190);

  app.endUndoGroup();
  return comp;
}

// Un fallo dentro del script deja a AE con un dialogo abierto y a mi sin
// saber que ha pasado: sin ventana, el mensaje no llega a ninguna parte. Se
// escribe a fichero antes de rendirse.
function apuntar(msg) {
  var log = new File(new File($.fileName).parent.fsName + "/_jsx.log");
  log.open("w"); log.write(msg); log.close();
}

var comp;
try {
  comp = construir();
} catch (err) {
  apuntar("ERROR linea " + err.line + ": " + err.message);
  app.quit();
}
var aqui = new File($.fileName).parent;
var aep = new File(aqui.fsName + "/parallax3d.aep");
app.project.save(aep);

try {
  var item = app.project.renderQueue.items.add(comp);
  var mod = item.outputModule(1);
  mod.file = new File(aqui.fsName + "/salida/parallax3d.mov");
  app.project.save(aep);
  apuntar("ok");
} catch (err2) {
  apuntar("ERROR en la cola: " + err2.message);
}
app.quit();
