#!/usr/bin/env python3
"""
Pega los clips de escena con transiciones DESLIZANTES.

    python3 montar.py proyecto/guion.json ep02.mp4 --tmp _escenas

La escena entera sale por un lado y la siguiente entra por el otro, que es
el corte que usa MagnatesMedia. No es un fundido: es un empujon lateral.

El sentido alterna solo (izquierda, derecha, izquierda...) para que no se
vuelva monotono, y se puede fijar por escena con "transicion" en el JSON:
  "slideleft" | "slideright" | "slideup" | "slidedown" | "fade" | "corte"

Nota: la duracion final es la suma de las escenas menos un solape por cada
corte. render.py ya anade ese solape a cada clip, asi que cuadra.
"""
import os, sys, json, argparse, subprocess

SOLAPE = 0.45          # segundos de deslizamiento

# Alternar solo entre slideleft y slideright cansa: son el mismo gesto en
# espejo, y a los veinte cortes el ojo ya lo predice. La rueda mezcla cuatro
# familias -deslizamiento, barrido, apertura y disolvencia- para que el ritmo
# no sea adivinable. Es una lista prima (7) para que no caiga en fase con los
# patrones de escena, que van de 2, 3 y 4.
RUEDA = ["slideleft", "smoothright", "wipeleft", "dissolve",
         "slideright", "circleopen", "smoothleft"]

# El corte de capitulo pide otra cosa: un negro corto que separe bloques.
# Se marca en el JSON con "cierra_bloque": true en la ultima escena del
# capitulo, y montar.py lo traduce a un fundido a negro.
CIERRE_BLOQUE = "fadeblack"

# Un corte seco no se monta con `concat`: encadenar concat con xfade en el
# mismo filter_complex rompe las marcas de tiempo y ffmpeg aborta con EINVAL.
# Se monta como un fundido de UN fotograma, que a 25 imagenes por segundo el
# ojo no distingue de un corte, y deja el grafo entero homogeneo.
DUR_CORTE = 0.04


def linea_de_tiempo(guion, solape=SOLAPE):
    """Instante en que empieza cada escena en el video ya montado.

    No es la suma de duraciones menos un solape fijo: un corte seco -los de
    dentro de un hilo, los de un latigazo, los que pida el JSON- no solapa
    nada. Contarlos como si solaparan desplaza todo lo que viene detras, y
    ese error se acumula: en un episodio de 225 escenas con treinta cortes
    secos son mas de trece segundos de desfase entre la voz y la imagen.

    Devuelve (inicios, transiciones, duracion_total). Lo usan montar.py para
    colocar los xfade y sonido.py para colocar la voz y los golpes: es la
    misma cuenta, y tiene que salir de un solo sitio.
    """
    esc = guion["escenas"]
    trans = []
    for i, e in enumerate(esc):
        if e.get("transicion"):
            trans.append(e["transicion"])
        elif e.get("cierra_bloque"):
            trans.append(CIERRE_BLOQUE)
        else:
            trans.append(RUEDA[i % len(RUEDA)])

    inicios = [0.0]
    reloj = esc[0].get("duracion", 4)
    for i in range(1, len(esc)):
        salto = DUR_CORTE if trans[i - 1] == "corte" else solape
        arranque = reloj - salto
        inicios.append(arranque)
        reloj = arranque + esc[i].get("duracion", 4)
    return inicios, trans, reloj


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion"); ap.add_argument("salida", nargs="?", default="salida.mp4")
    ap.add_argument("--tmp", default="_escenas")
    ap.add_argument("--solape", type=float, default=SOLAPE)
    a = ap.parse_args()

    # preparar() es quien pone "corte" dentro de los hilos y en los
    # latigazos. Sin llamarlo, montar.py deslizaria por encima de una
    # panoramica continua y se cargaria el efecto.
    import render as R
    guion = R.preparar(json.load(open(a.guion, encoding="utf-8")))
    _, trans, _ = linea_de_tiempo(guion, a.solape)
    clips = []
    for i, esc in enumerate(guion["escenas"]):
        ruta = os.path.join(a.tmp, f'{i:03d}_{esc["id"]}.mp4')
        if not os.path.exists(ruta):
            sys.exit(f"falta el clip {ruta}: lanza render_par.py primero")
        clips.append(ruta)

    if len(clips) == 1:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", clips[0],
                        "-c", "copy", a.salida], check=True)
        return

    entradas, filtro, prev, reloj = [], [], "[0:v]", dur(clips[0])
    for i in range(1, len(clips)):
        t = trans[i - 1]
        seco = t == "corte"
        salto = DUR_CORTE if seco else a.solape
        offset = reloj - salto
        etiqueta = f"[v{i}]"
        filtro.append(f"{prev}[{i}:v]xfade="
                      f"transition={'fade' if seco else t}:"
                      f"duration={salto}:offset={offset:.3f}{etiqueta}")
        reloj = offset + dur(clips[i])
        prev = etiqueta

    for c in clips:
        entradas += ["-i", c]

    cmd = (["ffmpeg", "-y", "-v", "error"] + entradas +
           ["-filter_complex", ";".join(filtro), "-map", prev,
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.salida])
    import collections as _c
    reparto = _c.Counter(trans[:len(clips)-1])
    print(f"{len(clips)} clips · {len(clips)-1} transiciones · "
          f"{int(reloj//60)}:{reloj%60:04.1f}")
    print("  " + " · ".join(f"{k} x{v}" for k, v in reparto.most_common()))
    subprocess.run(cmd, check=True)
    print("OK ->", a.salida)


if __name__ == "__main__":
    main()
