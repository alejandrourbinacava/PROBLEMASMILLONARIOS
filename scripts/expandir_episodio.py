"""Completa el episodio: convierte el guion en escenas aplicando los patrones.

El JSON de entrada especifica al detalle el gancho y el capitulo 1 -catorce
escenas, 57 segundos- y deja el resto para generar. Este script lo completa
usando las marcas del SRT de cada capitulo, asi que cada escena dura lo que dura
lo que se dice en ella y no un valor inventado.

Como se reparten los tipos:

  El JSON trae dos criterios que se contradicen. `mezcla_objetivo` pide un 25%
  de escenas por capas -serian 37 escenas y unos 127.000 creditos de imagenes- y
  la regla de al lado dice que se reservan al gancho, la apertura de cada
  capitulo y las revelaciones de los capitulos 4 y 6, que son unas diez y
  34.500 creditos.

  Se sigue la REGLA, que es la instruccion mas concreta y ademas explica su
  motivo. Queda anotado aqui porque la nota de uso pide avisar en vez de
  elegir en silencio.

  El resto se reparte entre grafico y clip por lo que dice cada frase: si lleva
  una cifra o una comparacion, es grafico; si no, es metraje.

    python scripts/expandir_episodio.py config/escenas_casino.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

FPS = 25
# Ningun plano pasa de esto: es la regla de montaje del guion.
MAX_FRAMES = 4 * FPS
MIN_FRAMES = int(1.8 * FPS)

# La locucion escribe los numeros EN LETRA -"seiscientos noventa y seis
# millones"-, asi que buscar digitos no encuentra casi nada: con la primera
# version salia un 80% de clips y un 15% de graficos, cuando el guion esta
# lleno de cifras. Se busca el numero Y su UNIDAD, que es lo que convierte una
# frase en un dato que merece grafico.
# El % va FUERA del grupo con \b: "del 2,7 %" lleva un espacio delante del
# signo, y \b antes de % exige un caracter de palabra, asi que no casaba nunca
# y el capitulo 5 entero -que va de margenes- se clasificaba como metraje.
UNIDAD = re.compile(
    r"\b(millones?|mil(?:es)?|d[oó]lar(?:es)?|por ciento|puntos?|"
    r"pie cuadrado|habitaciones|anuales?|mensuales?|iniciales|centavos)\b|%",
    re.IGNORECASE,
)
NUMERO = re.compile(
    r"\b(\d[\d.,]*|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|"
    r"once|doce|trece|catorce|quince|veinte|veinticinco|treinta|cuarenta|"
    r"cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|doscientos|"
    r"trescientos|cuatrocientos|quinientos|seiscientos|setecientos|"
    r"ochocientos|novecientos)\b",
    re.IGNORECASE,
)


def CIFRA_search(texto: str):
    """Una frase es un dato cuando lleva un numero Y su unidad."""
    return NUMERO.search(texto) and UNIDAD.search(texto)
COMPARA = re.compile(r"\b(entre|frente a|mientras que|en cambio|el otro extremo|"
                     r"dos modelos|comparad)\b", re.IGNORECASE)
# Una frase que enumera conceptos pide un desglose, no un contador.
ENUMERA = re.compile(r"\b(cada uno|uno por uno|la lista|los conceptos|ademas de|"
                     r"por un lado|y luego|sumas|se suman|entre todos)\b", re.IGNORECASE)
# Papel oficial: solicitudes, leyes, informes. Se ensena el documento.
DOCUMENTO = re.compile(r"\b(oficial(es)?|la ley|regulaci[oó]n|comisi[oó]n|informe|"
                       r"solicitud|formulario|estatuto|c[oó]digo|expediente|"
                       r"registro p[uú]blico|p[uú]blicos?|auditor[ií]a|contrato)\b",
                       re.IGNORECASE)
# Nevada de los cincuenta: metraje de archivo virado.
ARCHIVO = re.compile(r"\b(a[nñ]os cincuenta|los cincuenta|mil novecientos|"
                     r"en aquella [eé]poca|entonces Las Vegas|hace setenta a[nñ]os|"
                     r"al principio de todo)\b", re.IGNORECASE)


def clasificar(texto: str, primera: bool) -> tuple[str, str, str | None]:
    """Decide que se ve en un plano a partir de lo que se dice en el."""
    if primera:
        return "capas", "apertura_capitulo", None
    if ARCHIVO.search(texto):
        return "clip", "archivo_historico", None
    if CIFRA_search(texto) and ENUMERA.search(texto):
        return "grafico", "desglose", "lista_apilada"
    if CIFRA_search(texto) and COMPARA.search(texto):
        return "grafico", "comparativa", "barras_enfrentadas"
    if CIFRA_search(texto):
        return "grafico", "cifra_impacto", "contador"
    if DOCUMENTO.search(texto):
        return "documento", "documento", None
    return "clip", "textura_real", None


def leer_srt(ruta: Path) -> list[dict]:
    """Devuelve las frases con su inicio y fin en segundos."""
    if not ruta.exists():
        return []
    bloques = re.split(r"\n\s*\n", ruta.read_text(encoding="utf-8").strip())
    frases = []
    for bloque in bloques:
        lineas = [l for l in bloque.splitlines() if l.strip()]
        if len(lineas) < 2:
            continue
        tiempos = next((l for l in lineas if "-->" in l), None)
        if not tiempos:
            continue
        def a_segundos(marca: str) -> float:
            h, m, resto = marca.strip().split(":")
            s, ms = resto.replace(".", ",").split(",")
            return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        desde, hasta = [a_segundos(p) for p in tiempos.split("-->")]
        texto = " ".join(l for l in lineas if "-->" not in l and not l.strip().isdigit())
        frases.append({"desde": desde, "hasta": hasta, "texto": texto.strip()})
    return frases


def frasear(fragmentos: list[dict]) -> list[dict]:
    """Reconstruye frases completas a partir de los fragmentos del SRT.

    El SRT viene en trozos de subtitulo -"tiene una tasa que,"- de dos o tres
    segundos, no en frases. Si se agrupa directamente sobre ellos, cada plano
    acaba siendo medio predicado sin sentido y sin la cifra, que suele caer en
    el fragmento siguiente. Se juntan hasta el punto final.
    """
    frases: list[dict] = []
    actual: dict | None = None
    for f in fragmentos:
        if actual is None:
            actual = dict(f)
        else:
            actual["hasta"] = f["hasta"]
            actual["texto"] += " " + f["texto"]
        if actual["texto"].rstrip().endswith((".", "?", "!", "…", ":")):
            frases.append(actual)
            actual = None
    if actual:
        frases.append(actual)
    return frases


def agrupar(frases: list[dict]) -> list[dict]:
    """Junta frases seguidas hasta llegar al maximo por plano.

    El corte cae donde acaba una frase, nunca a mitad: partir una frase entre
    dos planos deja la segunda mitad huerfana, sin imagen que la sostenga. Una
    frase mas larga que el maximo se queda sola y ocupa lo que dure.
    """
    grupos: list[dict] = []
    actual: dict | None = None
    for frase in frases:
        if actual is None:
            actual = dict(frase)
            continue
        largo = (frase["hasta"] - actual["desde"]) * FPS
        if largo > MAX_FRAMES:
            grupos.append(actual)
            actual = dict(frase)
        else:
            actual["hasta"] = frase["hasta"]
            actual["texto"] += " " + frase["texto"]
    if actual:
        grupos.append(actual)
    return grupos


def rotulo(texto: str) -> str | None:
    """Saca un rotulo corto de la frase, o None si no hay nada que destacar."""
    limpio = re.sub(r"[.,;:]", "", texto)
    palabras = limpio.split()
    if len(palabras) <= 6:
        return limpio.upper()
    # Una cifra con su unidad es el mejor rotulo posible
    m = re.search(r"(\d[\d.,]*\s*(?:millones|mil|por ciento|%|dolares))", texto, re.I)
    if m:
        return m.group(1).upper()
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--voz", type=Path, default=Path("build/_casino/voz"))
    parser.add_argument("--out", type=Path, default=Path("config/escenas_casino_completo.json"))
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    patrones = spec.get("patrones", {})
    resumen = json.loads((args.voz / "resumen.json").read_text(encoding="utf-8"))

    # Las escenas ya especificadas cubren el gancho y el capitulo 1.
    ya = {e["id"]: e for e in spec["escenas"]}
    bloques_hechos = {e.get("bloque") for e in spec["escenas"]}
    print(f"ya especificados: {sorted(b for b in bloques_hechos if b)}")

    # El gancho y el capitulo 1 vienen escritos a mano, pero solo cubren 57 de
    # los 141 segundos que dura su locucion: si se dan por cerrados, hay 84
    # segundos de voz sin imagen. Se respeta lo escrito y se completa el resto
    # desde donde acaba, en vez de descartarlo o de pisarlo.
    cubierto: dict[str, float] = {}
    for e in spec["escenas"]:
        b = e.get("bloque")
        if b:
            cubierto[b] = cubierto.get(b, 0) + e["duracion"] / FPS

    nuevas: list[dict] = []
    for indice, bloque in enumerate(resumen):
        titulo = bloque["titulo"]
        nombre = "gancho" if indice == 0 else f"capitulo_{indice}"
        desde_seg = cubierto.get(nombre, 0.0)
        frases = leer_srt(args.voz / f"{bloque['base']}.srt")
        if not frases:
            print(f"  {titulo}: SIN SRT, se salta")
            continue
        grupos = agrupar(frasear(frases))
        # Se tiran los planos que caen dentro de lo ya escrito a mano.
        if desde_seg > 0:
            grupos = [g for g in grupos if g["hasta"] > desde_seg + 0.4]
            if grupos:
                grupos[0] = dict(grupos[0], desde=max(grupos[0]["desde"], desde_seg))
        if not grupos:
            print(f"  {titulo[:40]:42} ya cubierto a mano")
            continue
        # Los capitulos que continuan lo escrito a mano llevan otra etiqueta:
        # el capitulo 1 ya tiene un C1_02, y generar otro deja dos escenas
        # distintas con el mismo id.
        etiqueta = "G" if indice == 0 else f"C{indice}"
        if desde_seg > 0:
            etiqueta += "x"
        # El primer plano arranca donde arranca el capitulo, no donde entra la
        # primera palabra: el SRT empieza en 0,24s y ese cuarto de segundo se
        # quedaria sin imagen.
        grupos[0] = dict(grupos[0], desde=desde_seg)
        primera_nueva = len(nuevas)
        print(f"  {titulo[:40]:42} {len(frases):3} frag -> "
              f"{len(frasear(frases)):3} frases -> {len(grupos):3} planos")

        for n, grupo in enumerate(grupos):
            # La escena dura hasta que empieza la siguiente, no hasta que
            # termina su propia frase: si no, los silencios entre frases se
            # quedan sin plano y el video acaba mas corto que la locucion.
            siguiente = (grupos[n + 1]["desde"] if n + 1 < len(grupos)
                         else bloque["duracion"])
            frames = max(MIN_FRAMES, round((siguiente - grupo["desde"]) * FPS))
            texto = grupo["texto"]
            tipo, patron, variante = clasificar(texto, n == 0 and desde_seg == 0)

            # Una frase larga no cabe en un plano. La regla de los cuatro
            # segundos esta escrita sobre `textura_real`, o sea sobre el
            # METRAJE: un grafico dura lo que dice su patron -75, 130, 150
            # frames- porque una cifra necesita leerse. Asi que el recurso que
            # pide la frase se lleva su duracion entera y lo que sobra se cubre
            # con metraje, que es como se monta de verdad: se ensena el dato y
            # luego se cubre.
            #
            # El resto NO se parte a ciegas: repartir "duracion del patron y lo
            # que sobre" deja colas de un frame -C2_09b duraba 1/25 de segundo-
            # que no son un plano, son un parpadeo. Se reparte a partes iguales
            # entre los trozos que hagan falta, y si el sobrante no da ni para
            # un plano corto se lo queda el recurso principal.
            if tipo == "clip":
                # Metraje: se reparte a partes iguales, todos por debajo de los
                # cuatro segundos que manda `textura_real`.
                trozos = max(1, -(-frames // MAX_FRAMES))
                corte = [round(frames * k / trozos) for k in range(trozos + 1)]
            else:
                propia = min(frames, patrones.get(patron, {}).get("duracion", MAX_FRAMES))
                resto = frames - propia
                sobrantes = -(-resto // MAX_FRAMES) if resto >= MIN_FRAMES else 0
                if sobrantes == 0:
                    propia = frames
                corte = [0, propia]
                for k in range(sobrantes):
                    corte.append(propia + round((frames - propia) * (k + 1) / sobrantes))
                trozos = 1 + sobrantes
            for k in range(trozos):
                sub_tipo, sub_patron, sub_var = (
                    (tipo, patron, variante) if k == 0
                    else ("clip", "textura_real", None))
                sufijo = "" if trozos == 1 else chr(ord("a") + k)
                escena = {
                    "id": f"{etiqueta}_{n + 1:02d}{sufijo}",
                    "bloque": nombre,
                    "tipo": sub_tipo,
                    "patron": sub_patron,
                    "duracion": corte[k + 1] - corte[k],
                    "locucion": texto if k == 0 else "",
                }
                if k > 0:
                    # El sub-plano no lleva locucion propia -no se dice nada
                    # nuevo en el- pero si necesita saber de que va la frase
                    # para poder buscarle un plano que la represente.
                    escena["contexto"] = texto
                if sub_var:
                    escena["variante"] = sub_var
                r = rotulo(texto) if k == 0 else None
                if r and sub_tipo not in ("clip",):
                    escena["contenido"] = {"linea": r}
                    if sub_var == "contador":
                        escena["variante"] = "frase_destacada"
                nuevas.append(escena)

        # El ultimo plano absorbe el redondeo para que las escenas del capitulo
        # sumen EXACTAMENTE su locucion. Si no, cada capitulo queda unas
        # centesimas corto o largo, hay que recortar el audio al montarlo -y un
        # recorte se come la ultima palabra- y ademas el desfase se acumula a
        # lo largo de los ocho bloques.
        objetivo = round((bloque["duracion"] - desde_seg) * FPS)
        puestos = sum(e["duracion"] for e in nuevas[primera_nueva:])
        nuevas[-1]["duracion"] += objetivo - puestos

    spec["escenas"] = spec["escenas"] + nuevas
    total = sum(e["duracion"] for e in spec["escenas"])
    spec["duracion_total"] = total

    tipos: dict[str, int] = {}
    for e in spec["escenas"]:
        tipos[e["tipo"]] = tipos.get(e["tipo"], 0) + e["duracion"]

    args.out.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(spec['escenas'])} escenas, {total} frames = {total / FPS / 60:.1f} min")
    for tipo, frames in sorted(tipos.items(), key=lambda kv: -kv[1]):
        print(f"  {tipo:9} {frames / FPS:6.0f}s  {frames / total * 100:4.0f}%")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
