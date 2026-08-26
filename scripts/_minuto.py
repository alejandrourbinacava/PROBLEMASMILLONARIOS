"""Prueba de un minuto con los dos lenguajes repartidos.

La regla de reparto, que es lo que da coherencia al montaje:

    hay cifras   ->  gráfico de papel (VOX y el arco financiero)
    no hay cifras ->  composición por capas con parallax

Así los dos lenguajes no compiten: cada uno entra donde le toca. Y las escenas
por capas abundan sin convertirse en el recurso por defecto.

Los cortes y los tiempos internos salen del SRT de la propia narración.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, ".")

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from pipeline.util import annotate, ffmpeg, graphics
from pipeline.util import layers as L

W, H, FPS = 1920, 1080, 25
OUT = Path("build/_minuto").resolve()
CLIPS = Path(".cache/clips").resolve()
SUJETOS = Path("build/_sujetos").resolve()
FONT = Path("assets/fonts/Poppins-Black.ttf").resolve()
SFX = Path("assets/sfx").resolve()
MUSICA = Path("assets/music/circuit_synthwave.mp3").resolve()

TEMA = graphics.Theme(width=W, height=H, font_file=FONT)

# La sombra es común a todo el vídeo: es lo que hace que las escenas pertenezcan
# al mismo sitio. Lo que cambia es la luz, una por escena.
#
# Dentro de una escena todas las piezas pasan por la MISMA rampa, y por eso deja
# de notarse la luz con la que se rodó cada una. Pero si todo el vídeo comparte
# también la luz, seis escenas seguidas son seis veces la misma imagen. Cada una
# lleva su color dominante, como hacen ellos.
SOMBRA = (14, 18, 38)
LUZ = (255, 176, 96)

AMBAR = (255, 176, 96)
FRIO = (120, 180, 255)
DINERO = (150, 235, 185)
MAGENTA = (255, 145, 195)
NOCHE = (135, 155, 255)

ENCODE = [
    "-r", str(FPS), "-fps_mode", "cfr",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
    "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
    "-x264-params", f"keyint={FPS * 2}:min-keyint={FPS * 2}:scenecut=0",
    "-threads", "1", "-f", "mpegts",
]


def encode(frames: int, name: str) -> list[str]:
    return ["-frames:v", str(frames)] + ENCODE + [name]


# ---------------------------------------------------------------------------
# Piezas
# ---------------------------------------------------------------------------

def grafico(kind: str, frames: int, nombre: str, **campos) -> Path:
    out = OUT / nombre
    graphics.render(
        graphics.GraphicSpec(kind=kind, **campos), out,
        frames=frames, fps=FPS, theme=TEMA, encode_args=encode(frames, out.name),
    )
    return out


def anotado(frames: int, nombre: str, clip: str, ann: annotate.Annotation,
            desde: float = 1.2) -> Path:
    patron = annotate.render_frames(ann, OUT / f"ann_{nombre}", frames=frames)
    out = OUT / nombre
    ffmpeg.run([
        "-ss", str(desde), "-i", str(CLIPS / clip),
        "-framerate", str(FPS), "-i", str(patron),
        "-filter_complex",
        f"[0:v]fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},setsar=1,eq=saturation=0.92:contrast=1.06[base];"
        f"[base][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]",
    ] + encode(frames, out.name), cwd=OUT)
    return out


def fondo(clip: str, at: float, nombre: str) -> Image.Image:
    dst = OUT / f"bg_{nombre}.png"
    if not dst.exists():
        ffmpeg.run([
            "-ss", f"{at}", "-i", str(CLIPS / clip), "-frames:v", "1",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
            str(dst),
        ])
    return Image.open(dst).convert("RGBA")


def sujeto(nombre: str) -> Image.Image:
    """Carga un recorte ya validado por scripts/_buscar_sujeto.py."""
    image = Image.open(SUJETOS / f"{nombre}.png").convert("RGBA")
    if not (L.is_cutout(image) and L.is_complete(image)):
        raise SystemExit(f"{nombre} no pasa las comprobaciones de recorte")
    return image


def texto_capa(cadena: str, size: int, y: float, hueco: tuple[float, float],
               colour=(255, 255, 255)) -> Image.Image:
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # El texto cabe DENTRO del hueco, sin margen de cortesia. Dejarle un 18% de
    # holgura "para que asome por detras de la figura" se comia justo la ultima
    # palabra: NO APUESTA CONTRA T, TODO EL NEGOCI, SIN REL...ES. El efecto de
    # pasar por detras ya lo da el empuje de camara, que separa las capas a
    # distinta velocidad. La legibilidad manda.
    ancho = (hueco[1] - hueco[0]) * W - 40
    while size > 46:
        font = ImageFont.truetype(str(FONT), size)
        if draw.textlength(cadena, font=font) <= ancho:
            break
        size -= 6
    font = ImageFont.truetype(str(FONT), size)
    span = draw.textlength(cadena, font=font)
    # Centrado en el hueco, no en el lienzo
    izquierda = (hueco[0] + hueco[1]) / 2 * W - span / 2
    izquierda = min(max(48, izquierda), W - span - 48)
    draw.text((izquierda, H * y), cadena, font=font, fill=(*colour, 255))
    print(f"    rotulo a {size}px, hueco {hueco[0]:.2f}-{hueco[1]:.2f}")
    return image


def suelo() -> Image.Image:
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    inicio = int(H * 0.72)
    for y in range(inicio, H):
        t = (y - inicio) / max(1, H - inicio)
        draw.line([(0, y), (W, y)], fill=(*SOMBRA, int(220 * (t ** 0.55))))
    return image


def velo(image: Image.Image, opacidad: float) -> Image.Image:
    out = image.convert("RGBA").copy()
    out.putalpha(out.getchannel("A").point(lambda v: int(v * opacidad)))
    return out


def escena(
    frames: int, nombre: str, *, clip_fondo: str, at: float, recorte: str,
    rotulo: str, escala: float, lado: float, entrada_sujeto: str,
    entrada_texto: str, size: int = 118,
    luz: tuple[int, int, int] = LUZ,
    tinte_fondo: tuple[int, int, int] = (210, 150, 120),
) -> Path:
    """Composición por capas: fondo, sujeto, texto entre medias, suelo.

    El texto va DETRÁS del sujeto —ese es el efecto— pero en el hueco medido,
    para que la figura no se coma una palabra.
    """
    bruto = sujeto(recorte)
    tope = L.max_scale(bruto, H)
    figura = L.fit_canvas(bruto, W, H, min(escala, tope), (lado, 1.0))
    hueco = L.free_span([figura], W, H)

    comp = L.Composition(width=W, height=H, push=0.09, layers=[
        L.Layer(L.backdrop_glow(W, H, luz, centre=(0.5, 0.6), radius=0.85),
                entrance="fade", delay=0.00, duration=0.18, parallax=0.0),
        L.Layer(velo(L.duotone(fondo(clip_fondo, at, nombre), SOMBRA, tinte_fondo,
                               contrast=1.22), 0.74),
                entrance="scale", delay=0.02, duration=0.24, parallax=0.15),
        L.Layer(texto_capa(rotulo, size, 0.36, hueco),
                entrance=entrada_texto, delay=0.26, duration=0.24, parallax=0.38),
        L.Layer(L.contact_shadow(figura),
                entrance="fade", delay=0.16, duration=0.26, parallax=1.35),
        L.Layer(L.duotone(figura, SOMBRA, luz, contrast=1.6),
                entrance=entrada_sujeto, delay=0.16, duration=0.30, parallax=1.35),
        L.Layer(suelo(), entrance="wipe_up", delay=0.08, duration=0.22, parallax=0.45),
    ])
    out = OUT / nombre
    L.render(comp, out, frames=frames, fps=FPS, encode_args=encode(frames, out.name))
    return out


def corte(frames: int, nombre: str, clip: str, desde: float = 1.2) -> Path:
    out = OUT / nombre
    ffmpeg.run([
        "-ss", str(desde), "-i", str(CLIPS / clip),
        "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,"
               f"crop={W}:{H},setsar=1,eq=saturation=1.1:contrast=1.08,format=yuv420p",
        "-an",
    ] + encode(frames, out.name), cwd=OUT)
    return out


# ---------------------------------------------------------------------------
# El plan. Cada entrada dice hasta que segundo va, sacado del SRT.
#   capas   -> no hay cifra: composicion por capas con parallax
#   papel   -> hay cifra: grafico VOX / arco financiero
# ---------------------------------------------------------------------------

HOOK = 4.6   # arranque a cortes rapidos, solo con whoosh

PLAN = [
    # --- narracion ---
    (2.18, "capas", dict(
        clip_fondo="pixabay_176993_16ce96aae2.mp4", at=2.0,
        recorte="pixabay_45254_97e5d3c506_8", rotulo="NO APUESTA CONTRA TI", tinte_fondo=(230, 170, 120), luz=AMBAR,
        escala=0.74, lado=0.84, entrada_sujeto="slide_left",
        entrada_texto="rise", size=112)),
    (3.58, "capas", dict(
        clip_fondo="pexels_9807879_49e3623999.mp4", at=1.5,
        recorte="pixabay_26793_8c8b33bf21_20", rotulo="TE VENDE TIEMPO", tinte_fondo=(120, 165, 225), luz=FRIO,
        escala=0.80, lado=0.18, entrada_sujeto="slide_right",
        entrada_texto="scale", size=124)),
    (6.36, "ruleta", dict(etiqueta="37 CASILLAS")),
    (9.82, "papel", dict(kind="compare", context="La ruleta europea",
        label="esta casilla es el negocio",
        items=[("casillas", "37"), ("te paga", "36")])),
    (12.40, "capas", dict(
        clip_fondo="pexels_7607942_e0c26d60bb.mp4", at=1.4,
        recorte="pexels_3044129_2dc5c3c295_20", rotulo="TODO EL NEGOCIO", tinte_fondo=(140, 215, 175), luz=DINERO,
        escala=0.78, lado=0.80, entrada_sujeto="rise",
        entrada_texto="slide_left", size=126)),
    (15.94, "papel", dict(kind="bar", label="DE CADA EURO", display="2,7%",
        value=2.7, unit="percent", context="En la mesa, en cada giro")),
    (17.32, "capas", dict(
        clip_fondo="pexels_36147796_c8b4e20f0c.mp4", at=1.0,
        recorte="pixabay_118956_02d6681416_35", rotulo="PARECE POCO", tinte_fondo=(225, 150, 195), luz=MAGENTA,
        escala=0.72, lado=0.20, entrada_sujeto="fall",
        entrada_texto="rise", size=136)),
    (22.28, "papel", dict(kind="stack", context="Multiplicado",
        items=[("Horas al dia", "18"), ("Dias al ano", "365"),
               ("Horas de mesa", "6.570")])),
    # El arco financiero: un solo plano de 18 s, con cada gasto en su marca
    (40.60, "arco", dict()),
    (43.10, "capas", dict(
        clip_fondo="pixabay_176993_16ce96aae2.mp4", at=3.5,
        recorte="pexels_9362273_3de3eb47ca_20", rotulo="COMPRA EL SILENCIO", tinte_fondo=(235, 165, 110), luz=AMBAR,
        escala=0.76, lado=0.82, entrada_sujeto="slide_left",
        entrada_texto="fall", size=120)),
    (47.40, "capas", dict(
        clip_fondo="pexels_7608145_26072465ae.mp4", at=2.0,
        recorte="pixabay_46637_c1a0d5b84a_20", rotulo="SIN RELOJES", tinte_fondo=(130, 145, 225), luz=NOCHE,
        escala=0.70, lado=0.24, entrada_sujeto="rise",
        entrada_texto="scale", size=140)),
]

# Los gastos, con el segundo en que se nombran segun el SRT
ARCO_DESDE, ARCO_HASTA = 22.28, 40.60
GASTOS = [
    ("Personal", "14200000", 26.90),
    ("Licencia y tasas", "9600000", 29.80),
    ("Edificio", "7100000", 32.30),
    ("Suministros", "3400000", 34.60),
    ("Marketing", "2900000", 36.40),
]

HOOK_CLIPS = [
    "pexels_36600728_38ae073548.mp4", "pexels_7608129_8c59b41adf.mp4",
    "pexels_35728857_19020f1c2a.mp4", "pexels_7607444_852c68bc1e.mp4",
    "pexels_31869126_ba8a2aa5c0.mp4", "pexels_34805837_bebca13e8a.mp4",
    "pexels_9807879_49e3623999.mp4", "pexels_35728852_cb23b26767.mp4",
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    piezas: list[Path] = []
    cortes: list[float] = []

    # ---- hook: cortes rapidos, solo whoosh ----
    frames_hook = int(round(HOOK * FPS))
    por_corte = frames_hook // len(HOOK_CLIPS)
    acumulado = 0
    for indice, clip in enumerate(HOOK_CLIPS):
        frames = por_corte if indice < len(HOOK_CLIPS) - 1 else frames_hook - acumulado
        piezas.append(corte(frames, f"h{indice}.ts", clip, desde=1.4 + indice * 0.3))
        acumulado += frames
        cortes.append(round(acumulado / FPS, 3))

    # ---- narracion ----
    frame_previo = frames_hook
    for indice, (fin, recurso, campos) in enumerate(PLAN):
        frame_fin = int(round((HOOK + fin) * FPS))
        frames = max(1, frame_fin - frame_previo)
        nombre = f"{indice:02d}_{recurso}.ts"
        print(f"  {indice:02d} {recurso:7} {frames / FPS:5.2f}s -> {HOOK + fin:6.2f}s")

        if recurso == "capas":
            piezas.append(escena(frames, nombre, **campos))
        elif recurso == "ruleta":
            piezas.append(anotado(frames, nombre, "pexels_35728855_0962957f02.mp4",
                annotate.Annotation(
                    width=W, height=H, font_file=FONT,
                    circles=[annotate.Circle(centre=(0.52, 0.47), radius=0.15, delay=0.14)],
                    arrows=[annotate.Arrow(start=(0.16, 0.78), end=(0.40, 0.56),
                                           bend=0.24, delay=0.42)],
                    labels=[annotate.Label(campos["etiqueta"], at=(0.07, 0.78),
                                           size=64, delay=0.34)])))
        elif recurso == "arco":
            duracion = ARCO_HASTA - ARCO_DESDE
            piezas.append(grafico(
                "ledger", frames, nombre,
                context="Facturacion anual", label="lo que se queda la casa",
                value=48_000_000,
                items=[(n, c) for n, c, _ in GASTOS],
                beats=[(t - ARCO_DESDE) / duracion for _, _, t in GASTOS],
            ))
        else:
            piezas.append(grafico(campos.pop("kind"), frames, nombre, **campos))

        cortes.append(round(frame_fin / FPS, 3))
        frame_previo = frame_fin

    mudo = OUT / "mudo.mp4"
    ffmpeg.concat_copy(piezas, mudo, OUT)
    total = ffmpeg.duration(mudo)
    print(f">> imagen {total:.2f}s / voz {ffmpeg.duration(OUT / 'voz.mp3'):.2f}s + hook {HOOK}s")
    mezclar(mudo, total, cortes[:-1])


def mezclar(mudo: Path, total: float, cortes: list[float]) -> None:
    whoosh = SFX / "whoosh" / "01_woosh.wav"
    entradas = ["-i", str(mudo), "-i", str(OUT / "voz.mp3"), "-i", str(MUSICA)]
    partes = [
        # La voz entra despues del hook: los primeros segundos van solo a efectos
        f"[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
        f"loudnorm=I=-15:TP=-1.5:LRA=11,adelay={int(HOOK * 1000)}|{int(HOOK * 1000)},"
        f"asplit=2[voz][vozsc]",
        f"[2:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
        f"atrim=0:{total:.3f},asetpts=N/SR/TB,volume=-3dB[mus]",
        "[mus][vozsc]sidechaincompress=threshold=0.06:ratio=9:attack=6:release=340[musd]",
    ]
    etiquetas = []
    indice = 3
    for marca in cortes:
        entradas += ["-i", str(whoosh)]
        etiqueta = f"w{indice}"
        arranque = max(0.0, marca - 0.22)
        # En el hook suenan todos; despues solo uno de cada dos, para que el
        # efecto no compita con la voz.
        volumen = -6 if marca < HOOK else -13
        partes.append(
            f"[{indice}:a]atrim=0:1.0,asetpts=N/SR/TB,volume={volumen}dB,"
            f"adelay={int(arranque * 1000)}|{int(arranque * 1000)}[{etiqueta}]")
        etiquetas.append(etiqueta)
        indice += 1

    mezcla = "[voz][musd]" + "".join(f"[{e}]" for e in etiquetas)
    partes.append(
        f"{mezcla}amix=inputs={2 + len(etiquetas)}:duration=longest:normalize=0,"
        f"alimiter=limit=0.89,aresample=48000,apad,atrim=0:{total:.3f}[a]")

    final = OUT / "minuto.mp4"
    ffmpeg.run(entradas + [
        "-filter_complex", ";".join(partes),
        "-map", "0:v", "-map", "[a]", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", str(final),
    ])
    print(f">> {final}  {ffmpeg.duration(final):.2f}s")


if __name__ == "__main__":
    main()
