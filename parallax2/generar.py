#!/usr/bin/env python3
"""
Genera los PNG del guion. Todo OPACO; las capas que no son fondo se
generan sobre croma verde y se recortan luego con recortar.py.

    python3 generar.py proyecto/guion.json --estimar        # no gasta nada
    python3 generar.py proyecto/guion.json
    python3 generar.py proyecto/guion.json --proveedor nano_banana

El proveedor sale de proveedores.json. NO se elige en el codigo ni lo
decide el modelo: es configuracion. La mayoria de agregadores exponen un
endpoint compatible con OpenAI, asi que basta con poner su base_url.
"""
import os, json, base64, argparse, urllib.request

CROMA = ("IMPORTANTE: el fondo detras del sujeto es un plano de color verde "
         "croma liso y uniforme (RGB 0,177,64), de un solo tono, sin "
         "degradado. NO hay cielo, NO hay calle, NO hay habitacion, NO hay "
         "horizonte: solo verde plano. Sin sombra proyectada sobre el fondo "
         "y sin suelo")

ENCUADRE = {
    "fondo":       "plano general de fondo, sin primer plano",
    "medio_lejos": "sujeto completo y centrado, pequeno en el encuadre",
    "medio":       "sujeto centrado, frontal y simetrico, completo dentro del encuadre",
    "horizonte":   "franja que ocupa TODO el ancho del encuadre de lado a "
                   "lado, del borde izquierdo al borde derecho sin dejar "
                   "huecos, situada en la mitad inferior, vista frontal a la "
                   "altura de los ojos y sin perspectiva de fuga, nada por "
                   "encima de ella",
    "figura":      "persona entera de pie y de cuerpo completo, de la cabeza a "
                   "los pies, vista de frente y a la altura de los ojos, con "
                   "los pies visibles apoyados en el suelo",
    "suelo":       "objeto completo apoyado sobre una superficie, con la base "
                   "visible y su sombra de contacto, vista frontal a la altura "
                   "de la mesa",
    "frente":      "elemento de primer plano ocupando todo el ancho, "
                   "cortado por el borde inferior del encuadre",
    "frente_bajo": "elemento de primer plano muy cercano, cortado por el borde inferior",
}


def prompt_de(capa, estilo):
    """El croma va el ULTIMO, despues del estilo.

    El estilo dice "noche cerrada", y puesto detras del croma le gana: el
    modelo devolvia la fachada recortada contra un cielo nocturno en vez de
    contra verde. Entonces `es_croma` la mandaba a rembg, y rembg le abria
    las ventanas iluminadas -cuarenta agujeros en la fachada- porque no las
    entiende como parte del edificio. Lo ultimo que lee el modelo es lo que
    mas pesa, asi que la instruccion de fondo va al final.
    """
    p = f'{capa["prompt"]}. {ENCUADRE[capa["rol"]]}. Estilo: {estilo}.'
    if capa["rol"] != "fondo":
        p += f" {CROMA}."
    return p


# --- backends --------------------------------------------------------------

def gen_openai_compatible(prompt, destino, cfg):
    from openai import OpenAI
    cli = OpenAI(api_key=os.environ[cfg["api_key_env"]],
                 base_url=cfg.get("base_url") or None)
    kw = dict(model=cfg["modelo"], prompt=prompt, size=cfg.get("tam", "1536x1024"))
    if cfg.get("calidad"):
        kw["quality"] = cfg["calidad"]
    r = cli.images.generate(**kw)
    d = r.data[0]
    if getattr(d, "b64_json", None):
        open(destino, "wb").write(base64.b64decode(d.b64_json))
    else:
        urllib.request.urlretrieve(d.url, destino)


def gen_fal(prompt, destino, cfg):
    import fal_client
    r = fal_client.subscribe(cfg["modelo"], arguments={
        "prompt": prompt, "image_size": "landscape_16_9",
        "num_images": 1, "output_format": "png"})
    urllib.request.urlretrieve(r["images"][0]["url"], destino)


def gen_replicate(prompt, destino, cfg):
    import replicate
    s = replicate.run(cfg["modelo"], input={
        "prompt": prompt, "aspect_ratio": "3:2", "output_format": "png"})
    item = s[0] if isinstance(s, list) else s
    datos = item.read() if hasattr(item, "read") else urllib.request.urlopen(str(item)).read()
    open(destino, "wb").write(datos)


def gen_kie(prompt, destino, cfg):
    """kie.ai. No expone /v1/images/generations: va por tareas.

    Se comprobo: tanto /v1/images/generations como /api/v1/images/generations
    devuelven 404. El agregador usa su propio flujo de crear tarea y luego
    consultarla, asi que no vale el backend compatible con OpenAI.
    """
    import json as _json
    import time as _time

    import requests

    cab = {"Authorization": "Bearer " + os.environ[cfg["api_key_env"]],
           "Content-Type": "application/json"}
    base = cfg.get("base_url") or "https://api.kie.ai/api/v1"
    entrada = {"prompt": prompt,
               "aspect_ratio": cfg.get("proporcion", "3:2"),
               "resolution": cfg.get("resolucion", "1K")}
    r = requests.post(f"{base}/jobs/createTask", headers=cab, timeout=60,
                      json={"model": cfg["modelo"], "input": entrada}).json()
    if r.get("code") != 200:
        raise RuntimeError(f'kie.ai: {r.get("msg")}')
    tarea = r["data"]["taskId"]

    for _ in range(80):
        _time.sleep(6)
        d = requests.get(f"{base}/jobs/recordInfo", headers=cab, timeout=40,
                         params={"taskId": tarea}).json().get("data") or {}
        if d.get("state") == "fail":
            raise RuntimeError(f'kie.ai fallo: {d.get("failMsg")}')
        if d.get("state") == "success":
            url = _json.loads(d.get("resultJson") or "{}")["resultUrls"][0]
            open(destino, "wb").write(requests.get(url, timeout=120).content)
            return
    raise RuntimeError("kie.ai no termino la tarea")


BACKENDS = {"openai_compatible": gen_openai_compatible,
            "fal": gen_fal, "replicate": gen_replicate, "kie": gen_kie}


def capas_unicas(guion):
    """En ORDEN DE GUION, no alfabetico.

    Importa cuando los creditos no llegan para el episodio entero: generando
    por orden alfabetico se completan trozos sueltos repartidos por los trece
    minutos y no se puede montar nada. Por orden de guion, lo que se genera
    son los primeros capitulos enteros, que si se pueden ver.
    """
    d = {}
    for esc in guion["escenas"]:
        for c in esc["capas"]:
            d.setdefault(c["archivo"], c)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("--config", default=None)
    ap.add_argument("--proveedor", default=None)
    ap.add_argument("--salida", default="crudas")
    ap.add_argument("--solo", nargs="*")
    ap.add_argument("--estimar", action="store_true",
                    help="cuenta imagenes y coste sin llamar a nada")
    a = ap.parse_args()

    base = os.path.dirname(os.path.abspath(a.guion))
    cfg_path = a.config or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "proveedores.json")
    conf = json.load(open(cfg_path, encoding="utf-8"))
    guion = json.load(open(a.guion, encoding="utf-8"))
    capas = capas_unicas(guion)
    crudas = os.path.join(base, a.salida)

    if a.estimar:
        faltan = [k for k in capas if not os.path.exists(os.path.join(crudas, k))]
        print(f'{len(guion["escenas"])} escenas · '
              f'{sum(len(e["capas"]) for e in guion["escenas"])} usos de capa · '
              f'{len(capas)} PNG unicos · {len(faltan)} por generar\n')
        print(f'{"proveedor":14s} {"modelo":22s} {"$/img":>8s} {"total":>9s}')
        for nom, p in conf["proveedores"].items():
            pr = p.get("precio_img", 0)
            print(f'{nom:14s} {p["modelo"]:22s} {pr:8.4f} {pr*len(faltan):9.2f}')
        print("\nprecios orientativos, comprueba los de tu proveedor")
        return

    nombre = a.proveedor or conf["por_defecto"]
    p = conf["proveedores"][nombre]
    if p["api_key_env"] not in os.environ:
        raise SystemExit(f'falta la variable de entorno {p["api_key_env"]}')
    fn = BACKENDS[p["tipo"]]
    os.makedirs(crudas, exist_ok=True)

    hechas = fallos = 0
    print(f'{len(capas)} imagenes · {nombre} · {p["modelo"]}')
    for arch, capa in capas.items():
        if a.solo and arch not in a.solo:
            continue
        destino = os.path.join(crudas, arch)
        if os.path.exists(destino) and not a.solo:
            continue
        hechas += 1
        print(f'  [{hechas}] {arch} ({capa["rol"]})', flush=True)
        try:
            fn(prompt_de(capa, guion.get("estilo", "")), destino, p)
        except Exception as e:
            print(f"    FALLO: {type(e).__name__}: {str(e)[:200]}")
            fallos += 1
            if "insufficient" in str(e).lower() or "credit" in str(e).lower():
                print("  SIN CREDITOS. Lo generado hasta aqui vale, y al "
                      "recargar se sigue por donde iba.")
                break


if __name__ == "__main__":
    main()
