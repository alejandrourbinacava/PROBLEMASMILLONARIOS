#!/usr/bin/env python3
"""
Renderiza un guion.json a MP4 (parallax 2.5D estilo MagnatesMedia).

    python3 render.py guion.json salida.mp4

El JSON NO contiene coordenadas. Solo dice que rol cumple cada PNG
("fondo", "medio", "frente"...) y que movimiento lleva la escena.
La geometria sale de PRESETS_ROL, que esta calibrado y no se toca.
"""
import sys, os, json, math, subprocess
import numpy as np
from PIL import Image, ImageFilter

SIGNOS = ".,¿¡\"'"

import efectos as FX

# ---------------------------------------------------------------------------
# PRESETS DE ROL  --  esto es lo que el modelo NO decide.
#   ancho    : ancho de la capa como fraccion del lienzo (>1 = sangra fuera)
#   ancla    : ("top"|"center"|"bottom", fraccion de la altura del lienzo)
#   dz       : cuanto crece la capa a lo largo de la escena (el parallax)
#   zy       : altura del punto de fuga sobre el que zoomea
# ---------------------------------------------------------------------------
# El salto de dz entre roles es lo que hace visible la profundidad. Si los
# valores estan juntos, el ojo no separa las capas y parece una foto con
# zoom. Aqui el frente se mueve casi 5 veces mas que el fondo.
PRESETS_ROL = {
    "fondo":       dict(ancho=1.22, ancla=("center", 0.44), dz=0.035, zy=0.50, blur=11.0, oscurecer=0.3, prof=0.0),
    "medio_lejos": dict(ancho=0.62, ancla=("top",    0.22), dz=0.055, zy=0.58, blur=4.0, oscurecer=0.12, prof=0.3),
    "medio":       dict(ancho=0.85, ancla=("top",    0.11), dz=0.075, zy=0.59, blur=0.0, oscurecer=0.0, prof=0.5),
    # Un objeto suelto -una mesa, una ruleta, una maqueta- no cuelga del aire:
    # se apoya. `medio` ancla por arriba y escala al 85% del ancho, que va bien
    # para una fachada que llena el cuadro pero deja flotando cualquier cosa
    # que deberia estar sobre una superficie. Este rol ancla por ABAJO, un poco
    # por encima del borde inferior, y escala menos.
    "suelo":       dict(ancho=0.58, ancla=("bottom", 0.92), dz=0.090, zy=0.95, blur=0.0, oscurecer=0.0, prof=0.6),
    # El PLANO SOBRE EL QUE SE APOYA el sujeto. Un edificio recortado sobre un
    # cielo cuelga del aire, y una ruleta sobre un fondo abstracto flota: no
    # es que esten mal colocados, es que falta el suelo. Para un edificio ese
    # suelo son los edificios vecinos; para un objeto, la mesa. Va detras del
    # sujeto y delante del fondo, ancho y anclado al borde de abajo, y se
    # mueve poco mas que el fondo porque esta casi igual de lejos.
    "horizonte":   dict(ancho=1.35, ancla=("bottom", 1.00), dz=0.055, zy=0.86, blur=7.0, oscurecer=0.22, prof=0.25),
    # UNA PERSONA DE PIE dentro de la escena: el crupier detras de la mesa,
    # un jugador al lado. No cabe en ningun rol de los otros. "medio" y
    # "medio_lejos" escalan al 85% y al 62% del ancho, y como el ancho se
    # aplica a la capa YA recortada, una figura estrecha y alta reventaba el
    # cuadro. Esta ancla por abajo, sobre el mismo suelo que el sujeto, y
    # ocupa lo que ocupa una persona.
    "figura":      dict(ancho=0.30, ancla=("bottom", 0.88), dz=0.072, zy=0.92, blur=1.2, oscurecer=0.08, prof=0.45),
    "frente":      dict(ancho=1.24, ancla=("top",    0.64), dz=0.170, zy=1.00, blur=2.6, oscurecer=0.22, prof=1.0),
    "frente_bajo": dict(ancho=1.40, ancla=("top",    0.82), dz=0.210, zy=1.00, blur=6.0, oscurecer=0.34, prof=1.0),
}

# COMPOSICION: donde cae el peso del encuadre. Es lo que evita que las 85
# escenas sean el mismo plano con distinta foto. Cada entrada desplaza y
# reescala por rol -> (dx en fracciones de W, dy en fracciones de H, escala).
#
# "suelo" lleva su propia fila en cada composicion. Sin ella, una escena
# construida sobre un objeto apoyado -una ruleta, una torre de fichas- se
# quedaba sin encuadre: pedias "cerca" o "derecha" y el objeto salia igual de
# pequeno y centrado en todas, porque el diccionario solo tenia filas para
# medio, frente y fondo. Los valores siguen a los de "medio", que es el rol
# del que sale, pero con menos desplazamiento vertical: lo que se apoya no se
# puede subir sin despegarlo de la superficie.
PRESETS_COMP = {
    "centrado":  {},
    "izquierda": {"medio": (-0.17, 0.02, 0.80), "frente": ( 0.09, 0.00, 1.06),
                  "fondo": ( 0.04, 0.00, 1.00), "suelo": (-0.19, 0.00, 0.86), "horizonte": ( 0.03, 0.00, 1.00), "figura": (-0.20, 0.00, 0.94)},
    "derecha":   {"medio": ( 0.17, 0.02, 0.80), "frente": (-0.09, 0.00, 1.06),
                  "fondo": (-0.04, 0.00, 1.00), "suelo": ( 0.19, 0.00, 0.86), "horizonte": (-0.03, 0.00, 1.00), "figura": ( 0.20, 0.00, 0.94)},
    "alto":      {"medio": ( 0.00,-0.08, 0.70), "frente": ( 0.00, 0.11, 1.12),
                  "fondo": ( 0.00,-0.03, 1.00), "suelo": ( 0.00,-0.04, 0.78), "horizonte": ( 0.00,-0.02, 0.96), "figura": ( 0.00,-0.03, 0.86)},
    "bajo":      {"medio": ( 0.00, 0.14, 0.98), "frente": ( 0.00, 0.17, 1.16),
                  "fondo": ( 0.00, 0.04, 1.00), "suelo": ( 0.00, 0.03, 1.10), "horizonte": ( 0.00, 0.03, 1.04), "figura": ( 0.00, 0.02, 1.08)},
    "cerca":     {"medio": ( 0.00, 0.04, 1.38), "frente": ( 0.00, 0.13, 1.28),
                  "fondo": ( 0.00, 0.00, 1.06), "suelo": ( 0.00, 0.02, 1.46), "horizonte": ( 0.00, 0.02, 1.14), "figura": ( 0.00, 0.02, 1.30)},
    "lejos":     {"medio": ( 0.00,-0.05, 0.54), "frente": ( 0.00, 0.07, 1.04),
                  "fondo": ( 0.00, 0.00, 1.00), "suelo": ( 0.00,-0.02, 0.62), "horizonte": ( 0.00,-0.01, 0.92), "figura": ( 0.00,-0.02, 0.70)},
    "diagonal":  {"medio": (-0.11,-0.05, 0.86), "frente": ( 0.13, 0.09, 1.18),
                  "fondo": ( 0.05, 0.00, 1.00), "suelo": (-0.13,-0.02, 0.92), "horizonte": ( 0.04, 0.00, 1.02), "figura": (-0.15,-0.02, 0.98)},
}

# MOVIMIENTO. "contra_*" mueve fondo y frente en sentidos OPUESTOS: es el
# que mas separa las capas y el que hay que usar cuando una escena se ve
# plana.
PRESETS_MOV = {
    "push_in":    dict(k= 1.0,  dx= 0.0, dy= 1.0, contra=False),
    "pull_out":   dict(k=-1.0,  dx= 0.0, dy=-1.0, contra=False),
    "estatico":   dict(k= 0.30, dx= 0.0, dy= 0.3, contra=False),
    "drift_izq":  dict(k= 0.5,  dx=-1.0, dy= 0.4, contra=False),
    "drift_der":  dict(k= 0.5,  dx= 1.0, dy= 0.4, contra=False),
    "contra_izq": dict(k= 0.6,  dx=-1.0, dy= 0.3, contra=True),
    "contra_der": dict(k= 0.6,  dx= 1.0, dy= 0.3, contra=True),
    "subir":      dict(k= 0.7,  dx= 0.0, dy=-1.5, contra=False),
    "bajar":      dict(k= 0.7,  dx= 0.0, dy= 1.5, contra=False),
}

LOOK = dict(bloom=0.38, bloom_th=168, bloom_r=26,
            vineta=0.30, grano=3.0, flicker=0.012, aberracion=1.2)

# Entradas por defecto segun el rol. El fondo no entra nunca (ya esta ahi
# cuando arranca la escena); lo que entra es lo que el ojo mira.
ENTRADA_ROL = {"fondo": "escala", "horizonte": "escala",
               "medio_lejos": "golpe", "medio": "golpe", "suelo": "golpe",
               "figura": "rebote",
               "frente": "desplome", "frente_bajo": "rebote"}
DUR_ENTRADA = 0.34          # corta: una entrada larga se lee como estatica
DUR_SALIDA = 0.22
ESCALON = 0.09              # retardo entre capa y capa, de atras a delante

ALPHA_UMBRAL = 40      # por debajo de esto, el pixel no cuenta como contenido


def ease(t):
    return t * t * (3 - 2 * t)


def retardo_rotulo(esc, ppm=140):
    """Segundo, dentro de la escena, en que debe entrar el rotulo.

    El rotulo se cronometra contra la PALABRA que lo dispara: se busca la
    primera palabra de la locucion que contenga la primera del rotulo y se
    convierte su posicion a segundos con el ritmo del guion.

    Esta fuera de render_escena porque sonido.py necesita el mismo numero: el
    efecto que suena cuando aparece un rotulo tiene que caer donde cae el
    rotulo, y calcularlo dos veces por separado es como se desincroniza.
    """
    txt = esc.get("texto_pantalla")
    if not txt:
        return None
    if txt.get("retardo") is not None:
        return float(txt["retardo"])
    loc = esc.get("texto", "").lower().split()
    # se limpian tambien los signos de apertura: con "¿CUANTO" el rotulo
    # nunca encontraba su palabra en la locucion y caia al retardo por defecto
    clave = txt["texto"].replace("*", "").split()[0].strip(SIGNOS).lower()
    idx = next((i for i, w in enumerate(loc) if clave in w.strip(".,")), None)
    return round(idx * 60.0 / ppm, 2) if idx is not None else 0.6


DUR_LATIGO = 0.22        # segundos de barrido a cada lado del corte


def preparar(guion):
    """Anota las escenas con lo que solo se sabe mirando a las vecinas.

    Dos cosas que una escena no puede calcular sola:

    HILO. Varias escenas seguidas que cuentan la misma idea comparten el
    campo "hilo". En vez de que cada una arranque su movimiento de camara
    desde cero -que es lo que delata el corte-, el grupo entero es UN solo
    movimiento y a cada escena le toca su tramo, repartido por duracion. La
    camara cruza el corte sin enterarse: es la transicion invisible.
    Dentro de un hilo las capas no vuelven a entrar de golpe (seria un
    parpadeo a mitad de una panoramica) y el corte va seco, sin deslizar.

    LATIGO. Una escena puede declarar "latigo": "izq" o "der". Entonces sale
    barriendo a toda velocidad y la SIGUIENTE entra con el mismo barrido en
    el mismo sentido, que es como se hace un whip pan: el desenfoque tapa el
    corte y el ojo lee una panoramica, no un salto. El corte tiene que ir
    seco tambien, o el fundido se comeria el efecto.

    Ninguna de las dos cosas la escribe el guion en numeros: el guion dice
    "estas tres van hiladas", y el reparto sale de aqui.
    """
    esc = guion["escenas"]
    for e in esc:
        e["_tramo"] = (0.0, 1.0)

    i = 0
    while i < len(esc):
        hilo = esc[i].get("hilo")
        if not hilo:
            i += 1
            continue
        j = i
        while j < len(esc) and esc[j].get("hilo") == hilo:
            j += 1
        grupo = esc[i:j]
        total = sum(g.get("duracion", 4) for g in grupo) or 1.0
        acum = 0.0
        for k, g in enumerate(grupo):
            d = g.get("duracion", 4)
            g["_tramo"] = (acum / total, (acum + d) / total)
            acum += d
            if k:                       # solo la primera entra de golpe
                for c in g["capas"]:
                    c["entrada"] = "ninguna"
            if k < len(grupo) - 1:
                g.setdefault("transicion", "corte")
        i = j

    # VARIAS PERSONAS EN LA MISMA ESCENA. Un rol solo sabe donde va UNA
    # figura, asi que tres crupieres saldrian los tres en el centro, uno
    # tapando a otro. Aqui se reparten a lo ancho y, sobre todo, a distinta
    # PROFUNDIDAD: el que esta mas al borde va un poco mas lejos y mas
    # pequeno. Eso es lo que convierte una fila de recortes en una mesa con
    # gente alrededor.
    for e in esc:
        figuras = [c for c in e.get("capas", []) if c["rol"] == "figura"]
        if len(figuras) < 2:
            continue
        n = len(figuras)
        for k, c in enumerate(figuras):
            # -1 .. +1, sin que nadie caiga exactamente en el centro
            t = (k + 0.5) / n * 2.0 - 1.0
            ajuste = dict(c.get("ajuste") or {})
            ajuste["dx"] = round(0.30 * t, 3)
            # los de los lados, mas lejos: mas pequenos y mas apagados
            lejania = abs(t)
            ajuste["ancho"] = round(0.30 * (1.0 - 0.22 * lejania), 3)
            ajuste["prof"] = round(0.45 - 0.16 * lejania, 3)
            ajuste["ancla"] = ("bottom", round(0.88 - 0.035 * lejania, 3))
            c["ajuste"] = ajuste
            # y no entran todos a la vez
            c["retardo"] = round(c.get("retardo", 0.0) + 0.06 * k, 2)

    for k, e in enumerate(esc):
        lat = e.get("latigo")
        if not lat:
            continue
        d = -1.0 if lat.startswith("izq") else 1.0
        e["_lat_sal"] = d
        e["transicion"] = "corte"
        if k + 1 < len(esc):
            esc[k + 1]["_lat_ent"] = d
    return guion


# PROFUNDIDAD DE CAMPO
#
# Solo el sujeto va nitido. El fondo desenfocado y bajado de luz es lo que
# hace que el sujeto destaque, y separa las capas MAS que cualquier
# movimiento de camara: el ojo calcula la distancia por foco antes que por
# paralaje.
#
# Antes esto se derivaba de la profundidad del rol con una curva unica. Ahora
# cada rol declara su desenfoque y su atenuacion en PRESETS_ROL: es mas
# explicito y permite afinar un rol sin mover los demas. Se puede pisar por
# capa con "desenfoque" y "oscurecer" dentro de `ajuste`, pero rara vez hace
# falta.
def profundidad_de_campo(im, preset, ajuste):
    blur = float(ajuste.get("desenfoque", preset.get("blur", 0.0)))
    osc = float(ajuste.get("oscurecer", preset.get("oscurecer", 0.0)))
    if blur <= 0.2 and osc <= 0.001:
        return im
    r, g, b, a = im.split()
    rgb = Image.merge("RGB", (r, g, b))
    if blur > 0.2:
        rgb = rgb.filter(ImageFilter.GaussianBlur(blur))
    if osc > 0.001:
        rgb = rgb.point(lambda v, k=1.0 - osc: int(v * k))
    rgb.putalpha(a)
    return rgb


def cargar(path, W, H, rol, ajuste, comp="centrado"):
    p = dict(PRESETS_ROL[rol])
    cdx, cdy, cesc = PRESETS_COMP.get(comp, {}).get(rol, (0.0, 0.0, 1.0))
    p["ancho"] *= cesc
    p.update(ajuste or {})
    im = Image.open(path)
    im = im.convert("RGBA") if im.mode != "RGBA" else im

    a = np.array(im.getchannel("A"))
    if a.min() < 255:
        a[a > 240] = 255                       # sujeto a opaco de verdad
        im.putalpha(Image.fromarray(a))
        bbox = Image.fromarray(((a > ALPHA_UMBRAL) * 255).astype(np.uint8)).getbbox()
        if bbox:
            im = im.crop(bbox)                 # recorte al contenido REAL

    ow, oh = im.size
    bw = int(round(p["ancho"] * W))
    bh = int(round(oh * bw / ow))
    if bw > ow * 1.6:
        print(f"  aviso: {os.path.basename(path)} se amplia x{bw/ow:.1f}, "
              f"generalo mas grande", file=sys.stderr)
    im = im.resize((bw, bh), Image.LANCZOS)
    # PROFUNDIDAD DE CAMPO. Se aplica UNA vez al cargar, no en cada fotograma:
    # son casi veinte mil fotogramas por episodio.
    im = profundidad_de_campo(im, p, ajuste or {})

    modo, frac = p["ancla"]
    x = (W - bw) / 2.0 + (cdx + p.get("dx", 0.0)) * W
    y = (frac + cdy) * H
    if modo == "center":
        y -= bh / 2.0
    elif modo == "bottom":
        y -= bh
    return dict(img=im, x=x, y=y, w=bw, h=bh, dz=p["dz"],
                zy=p["zy"] * H, prof=p.get("prof", 0.5))


def colocar(im, x, y, w, h, W, H):
    ow, oh = im.size
    sx, sy = w / ow, h / oh
    return im.transform((W, H), Image.AFFINE,
                        (1/sx, 0, -x/sx, 0, 1/sy, -y/sy), Image.BICUBIC)


def vineta(W, H, fuerza):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W/2)/(W/2), (yy - H/2)/(H/2))
    return (1.0 - fuerza * np.clip((d - .55)/.85, 0, 1)**1.6)[..., None].astype(np.float32)


def leer_clip(ruta, W, H, fps, n, recorte=0.0):
    """
    Decodifica un clip de stock a fotogramas crudos del tamano del lienzo.
    Rellena a lo ancho y recorta (nunca deforma). Si el clip es mas corto
    que la escena, se congela el ultimo fotograma en vez de cortar.
    """
    vf = (f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H}")
    cmd = ["ffmpeg", "-v", "error"]
    if recorte:
        cmd += ["-ss", str(recorte)]
    cmd += ["-i", ruta, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    # El cierre va en un `finally`. Antes estaba al final del cuerpo, y a un
    # generador que se abandona a medias -que es lo que hace el render: pide
    # sus n fotogramas y lo deja ahi- ese final no se ejecuta NUNCA. Con
    # doscientas ocho escenas eso son doscientos ocho ffmpeg vivos
    # descomprimiendo 1080p a la vez: la maquina se queda sin memoria y matan
    # el proceso. En local con diez escenas no se notaba.
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    tam = W * H * 3
    ult = None
    try:
        for _ in range(n):
            b = p.stdout.read(tam)
            if len(b) < tam:
                if ult is None:
                    raise SystemExit(f"clip ilegible: {ruta}")
                yield ult
                continue
            ult = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
            yield ult
    finally:
        try:
            p.stdout.close()
        except Exception:
            pass
        if p.poll() is None:
            p.kill()
        p.wait()


def render_escena(esc, cfg, base, ff):
    W, H, FPS = cfg["w"], cfg["h"], cfg["fps"]
    n = int(FPS * esc.get("duracion", 8))
    mov = PRESETS_MOV[esc.get("movimiento", "push_in")]
    comp = esc.get("composicion", "centrado")

    # --- escena de clip de stock: mismo acabado, sin capas ---
    clip = esc.get("clip")
    fuente = None
    if clip:
        ruta = clip if os.path.isabs(clip) else os.path.join(base, clip)
        fuente = leer_clip(ruta, W, H, FPS, n, esc.get("clip_desde", 0.0))

    capas = []
    for c in ([] if clip else esc["capas"]):
        ruta = c["archivo"] if os.path.isabs(c["archivo"]) else os.path.join(base, c["archivo"])
        L = cargar(ruta, W, H, c["rol"], c.get("ajuste"), comp)
        L["entrada"] = c.get("entrada", ENTRADA_ROL.get(c["rol"], "golpe"))
        L["salida"] = c.get("salida", "ninguna")
        L["retardo"] = c.get("retardo", len(capas) * ESCALON)
        capas.append(L)

    # efectos de pantalla y texto de la escena
    sistemas = [FX.Particulas(nom, W, H, semilla=esc["id"])
                for nom in esc.get("efectos", []) if nom in FX.PARTICULAS]
    con_fuga = "fuga_luz" in esc.get("efectos", [])
    grade = esc.get("grade", "neutro")
    graf = esc.get("grafico")
    txt = esc.get("texto_pantalla")
    if txt and txt.get("retardo") is None:
        txt["retardo"] = retardo_rotulo(esc, cfg.get("ppm", 140))
    capa_txt = FX.render_texto(
        txt["texto"], W, H,
        px=txt.get("px", 132),
        color=tuple(txt.get("color", (255, 255, 255))),
        acento=tuple(txt["acento"]) if txt.get("acento") else None,
        pos=(txt.get("x", "center"), txt.get("y", 0.5))) if txt else None

    vg = vineta(W, H, LOOK["vineta"]) if LOOK["vineta"] else None

    t0, t1 = esc.get("_tramo", (0.0, 1.0))
    nlat = max(1, int(FPS * DUR_LATIGO))

    for f in range(n):
        # El easing se aplica al recorrido COMPLETO del hilo, no al trozo:
        # suavizar cada tramo por separado daria un frenazo y un aceleron en
        # cada corte, que es justo lo que el hilo quiere evitar.
        t = ease(t0 + (t1 - t0) * (f / max(1, n - 1)))
        lienzo = Image.new("RGB", (W, H), (4, 6, 14))
        if fuente is not None:
            # KEN BURNS DE VERDAD sobre el metraje. Antes era un zoom
            # centrado del 5% y punto: en un video hecho solo de clips eso se
            # lee como metraje quieto con un temblor, no como camara. Ahora
            # el mismo `movimiento` que declara la escena manda tambien aqui
            # -zoom Y desplazamiento- asi que un clip y un plano compuesto se
            # mueven igual y el corte entre los dos no canta.
            #
            # Se parte SIEMPRE de un margen: para poder desplazar hace falta
            # tener imagen fuera de cuadro. Por eso la base es 1.14 y el
            # movimiento se mueve dentro de ese margen.
            cru = next(fuente)
            MARGEN = 1.14
            RECORRIDO = 0.085          # fraccion del cuadro que recorre
            zk = MARGEN * (1.0 + 0.09 * mov["k"] * t)
            nw, nh = int(W * zk), int(H * zk)
            # centro del recorte, moviendose a lo largo de la escena
            cx = (nw - W) / 2.0 + mov["dx"] * RECORRIDO * W * (t - 0.5) * 2.0
            cy = (nh - H) / 2.0 + mov["dy"] * RECORRIDO * H * (t - 0.5)
            cx = float(np.clip(cx, 0, max(0, nw - W)))
            cy = float(np.clip(cy, 0, max(0, nh - H)))
            im = Image.fromarray(cru.astype(np.uint8)).resize((nw, nh), Image.BICUBIC)
            im = im.crop((int(cx), int(cy), int(cx) + W, int(cy) + H))
            lienzo = im

        for L in capas:
            ue, us = FX.factor_anim(f, n, FPS, DUR_ENTRADA, DUR_SALIDA,
                                    L["retardo"])
            z = 1.0 + L["dz"] * mov["k"] * t
            # en contra_* el fondo va hacia un lado y el frente hacia el otro
            signo = (1.0 - 2.0 * L["prof"]) if mov["contra"] else 1.0
            dx = mov["dx"] * signo * L["dz"] * 340 * t
            dy = mov["dy"] * L["dz"] * 200 * t

            # entrada y salida propias de la capa
            adx, ady, aesc, aop, ablur = FX.anim_capa(L["entrada"], ue, W, H)
            sdx, sdy, sesc, sop, sblur = FX.anim_capa(L["salida"], us, W, H, True)
            dx += adx + sdx; dy += ady + sdy
            z *= aesc * sesc
            op = aop * sop
            if op <= 0.01:
                continue

            x = W/2 + (L["x"] - W/2) * z + dx
            y = L["zy"] + (L["y"] - L["zy"]) * z + dy
            w = colocar(L["img"], x, y, L["w"]*z, L["h"]*z, W, H)
            if ablur + sblur > 0.3:
                w = w.filter(ImageFilter.GaussianBlur(ablur + sblur))
            if op < 0.999:
                al = w.getchannel("A").point(lambda v: int(v * op))
                w.putalpha(al)
            lienzo.paste(w, (0, 0), w)

        arr = np.asarray(lienzo).astype(np.float32)
        arr = FX.gradar(arr, grade)
        if LOOK["flicker"]:
            arr *= 1 + LOOK["flicker"] * math.sin(f*.9) * math.sin(f*.31 + 1.2)
        if LOOK["bloom"]:
            sa = np.asarray(lienzo.resize((W//4, H//4), Image.BILINEAR)).astype(np.float32)
            sa = np.clip(sa - LOOK["bloom_th"], 0, None) * (255/(255 - LOOK["bloom_th"]))
            g = Image.fromarray(sa.astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(LOOK["bloom_r"]/4)).resize((W, H), Image.BILINEAR)
            arr = 255 - (255-arr) * (255 - np.asarray(g).astype(np.float32)*LOOK["bloom"])/255
        seg = f / FPS
        for S in sistemas:
            arr = arr + S.dibujar(seg)
        if con_fuga:
            arr = arr + FX.fuga_luz(W, H, seg)
        if vg is not None:
            arr *= vg
        if capa_txt is not None:
            ret = txt.get("retardo", 0.35)
            f0 = int(ret * FPS)
            te, ts = FX.factor_anim(max(0, f - f0), n - f0, FPS,
                                    txt.get("dur_entrada", 0.5),
                                    txt.get("dur_salida", 0.4))
            if f >= f0:
                arr = FX.compon_texto(arr, capa_txt, te, ts,
                                      txt.get("estilo", "sube"), W, H)
        if graf is not None:
            f0 = int(graf.get("retardo", 0.25) * FPS)
            dur_g = graf.get("duracion", min(1.6, n / FPS * 0.55))
            if f >= f0:
                ug = min(1.0, (f - f0) / max(1, int(dur_g * FPS)))
                ge, gs = FX.factor_anim(f - f0, n - f0, FPS, 0.32, 0.25)
                cg = FX.grafico(graf, W, H, ug)
                arr = FX.compon_grafico(arr, cg, graf.get("entrada", "golpe"),
                                        ge, gs, W, H)
        if LOOK["aberracion"]:
            arr = FX.aberracion(np.clip(arr, 0, 255).astype(np.uint8),
                                LOOK["aberracion"])
        if LOOK["grano"]:
            arr += np.random.normal(0, LOOK["grano"], arr.shape).astype(np.float32)
        # El latigazo va el ULTIMO: barre y desenfoca la imagen ya acabada,
        # grano y rotulos incluidos. Si fuera antes, el texto quedaria nitido
        # sobre un fondo barrido y se veria pegado.
        if esc.get("_lat_ent") is not None and f < nlat:
            arr = FX.latigo(arr, esc["_lat_ent"], 1.0 - f / nlat)
        if esc.get("_lat_sal") is not None and f >= n - nlat:
            arr = FX.latigo(arr, esc["_lat_sal"], (f - (n - nlat)) / nlat)
        ff.stdin.write(np.clip(arr, 0, 255).astype(np.uint8).tobytes())

    if fuente is not None:
        fuente.close()          # dispara el finally de leer_clip


def main(guion_path, salida):
    guion = preparar(json.load(open(guion_path, encoding="utf-8")))
    base = os.path.dirname(os.path.abspath(guion_path))
    cfg = {**dict(w=1920, h=1080, fps=25), **guion.get("lienzo", {})}

    ff = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f'{cfg["w"]}x{cfg["h"]}', "-r", str(cfg["fps"]), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "slow", "-crf", "17",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", salida
    ], stdin=subprocess.PIPE)

    for esc in guion["escenas"]:
        print(f"  escena {esc['id']} ({esc.get('movimiento','push_in')}, "
              f"{esc.get('duracion',8)}s)", file=sys.stderr)
        render_escena(esc, cfg, base, ff)

    ff.stdin.close(); ff.wait()
    print(f"OK -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "salida.mp4")


# --- paralelizacion -------------------------------------------------------
# Un episodio de 13 min son ~19.500 fotogramas. En serie eso son horas.
# Cada escena es independiente, asi que se rinden en paralelo y se pegan.
#
#   python3 render_par.py guion.json salida.mp4 --procesos 8
