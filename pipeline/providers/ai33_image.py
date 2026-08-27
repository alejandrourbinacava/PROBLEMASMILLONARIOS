"""Generación de imágenes con ai33.pro (API v1i).

    POST https://api.ai33.pro/v1i/task/generate-image
    cabecera: xi-api-key
    cuerpo:   multipart con prompt, model_id, generations_count,
              model_parameters (JSON en una cadena) y assets opcionales
    respuesta: {"success": true, "task_id": ..., "estimated_credits": ...}

Se espera con el mismo GET /v3/task/{id} que la voz, y el resultado llega en
metadata.result_images.

Lo que hace especial a este módulo no es la llamada, que es trivial, sino
`prompt_por_capas`: para que una imagen sirva de material 2.5D no basta con que
sea bonita, tiene que estar CONSTRUIDA por planos. Una foto de un interior con
barandillas, cristales y veinte personas a veinte distancias no son cuatro
profundidades, son cuarenta, y el separador la parte por sitios absurdos. Al
generarla se puede pedir exactamente lo contrario.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests

from ..config import Config, env
from ..util import log

BASE_IMAGEN = "https://api.ai33.pro/v1i"
BASE_TAREA = "https://api.ai33.pro/v3"
_TIMEOUT = 90
_POLL = 4.0
_POLL_TIMEOUT = 900.0

_DONE = {"done", "completed", "complete", "success", "succeeded", "finished"}
_FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}

# NINGUNO de los modelos de 4K acepta prompt negativo: supports_negative_prompt
# viene a false en los seis. Asi que una lista de "no esto, no lo otro" no se
# interpreta como prohibicion, se le da al modelo como DESCRIPCION. Al escribir
# "no text anywhere" lo que recibe es un prompt que contiene la palabra "text",
# y sale un cartel escrito. Paso exactamente eso.
#
# Con estos modelos hay que decir lo que SI se quiere. Cada linea de aqui
# sustituye a una prohibicion que no funcionaba:
#
#   no railings, no fences, no wires  ->  volumenes macizos, superficies enteras
#   no glass, no reflections          ->  todo opaco y mate
#   no text anywhere                  ->  paneles lisos encendidos
#   no aircraft, no birds             ->  en el cielo solo hay nubes
#   no scattered crowds               ->  la calle esta vacia
QUERIDO = (
    "Every structure is a solid massive volume with unbroken surfaces and a "
    "clean silhouette against what is behind it. All materials are opaque, "
    "matte stone and painted metal. Sign faces are plain glowing panels of "
    "flat colour. The street is empty and quiet. Above the horizon the sky "
    "holds only clouds and haze. The light is even, with detail held in both "
    "the bright facades and the shadows"
)


class Ai33ImageError(RuntimeError):
    pass


def prompt_por_capas(
    primer_plano: str, plano_medio: str, fondo: str, *,
    ambiente: str = "dusk, strong backlight, low sun raking across the scene",
) -> str:
    """Construye un prompt que produce una imagen con ESPACIO, no con capas.

    La primera version pedia planos separables y salia un poster: fachada
    frontal, figura de frente, composicion simetrica, todo paralelo al plano de
    camara. Tenia capas y no tenia profundidad, que no es lo mismo.

    El parallax funciona porque al mover la camara SE DESCUBRE lo que estaba
    tapado. Si nada tapa a nada, no hay nada que descubrir y el dolly se ve como
    un zoom. La prueba: si te movieras dos pasos a la izquierda, ¿verias algo que
    antes no veias? En un plano frontal, no.

    De ahi las tres exigencias que se anaden a las siluetas limpias:

      - PERSPECTIVA: vista de tres cuartos y algo que se aleje -una calle, una
        acera, una hilera-. El retroceso es lo que hace que avanzar se sienta
        como avanzar.
      - SEPARACION REAL: el sujeto a media distancia del fondo, no pegado a la
        pared, con suelo visible entre los dos.
      - OCLUSION: los planos tienen que solaparse y taparse entre si. Eso es
        justo lo que el movimiento revela.

    Y dos que vienen de mirar lo que fallaba: el cielo necesita materia -un
    degradado limpio desplazandose no se ve moverse- y la fachada no puede
    quedar quemada, porque el modelo de profundidad se apoya en el gradiente y
    en la textura, y ante una superficie sin informacion da profundidad ruidosa
    justo en la superficie mas grande del encuadre.
    """
    return (
        f"Cinematic wide shot, {ambiente}. "
        f"Strong perspective with real depth: low angle, three-quarter view, "
        f"a road and pavement receding diagonally into the distance, "
        f"clear vanishing point. Nothing is parallel to the camera. "
        f"FOREGROUND, close to camera: {primer_plano}. "
        f"MIDDLE DISTANCE, clearly further back with visible ground between them: "
        f"{plano_medio}. "
        f"FAR BACKGROUND: {fondo}. "
        f"The planes overlap and partly hide each other, so moving sideways "
        f"would reveal what is behind them. "
        f"{QUERIDO}."
    )


class Ai33Image:
    def __init__(self, cfg: Config | None = None) -> None:
        self.cfg = cfg
        self.credits = 0
        self._session = requests.Session()
        self._session.headers.update({"xi-api-key": env("AI33_API_KEY", required=True)})

    def modelos(self) -> list[dict]:
        r = self._session.get(f"{BASE_IMAGEN}/models", timeout=_TIMEOUT)
        r.raise_for_status()
        return (r.json() or {}).get("models") or []

    def generar(
        self, prompt: str, destino: Path, *, model_id: str = "bytedance-seedream-4.5",
        aspect_ratio: str = "16:9", resolution: str = "4K",
        generaciones: int = 1, extra: dict[str, Any] | None = None,
    ) -> list[Path]:
        parametros = {"aspect_ratio": aspect_ratio, "resolution": resolution}
        parametros.update(extra or {})
        campos = {
            "prompt": (None, prompt),
            "model_id": (None, model_id),
            "generations_count": (None, str(generaciones)),
            "model_parameters": (None, json.dumps(parametros)),
        }
        r = self._session.post(
            f"{BASE_IMAGEN}/task/generate-image", files=campos, timeout=_TIMEOUT)
        if r.status_code >= 400:
            raise Ai33ImageError(f"{r.status_code}: {r.text[:400]}")
        payload = r.json()
        tarea = payload.get("task_id")
        if not tarea:
            raise Ai33ImageError(f"Sin task_id: {str(payload)[:300]}")
        estimado = payload.get("estimated_credits")
        log.info(f"Imagen encargada ({model_id}, {resolution}): tarea {tarea}, "
                 f"~{estimado} créditos")

        datos = self._esperar(tarea)
        self.credits += int(datos.get("credit_cost") or 0)
        imagenes = (datos.get("metadata") or {}).get("result_images") or []
        if not imagenes:
            raise Ai33ImageError(f"La tarea {tarea} terminó sin imágenes")

        destino.mkdir(parents=True, exist_ok=True)
        salida = []
        for indice, imagen in enumerate(imagenes):
            url = imagen.get("imageUrl") or imagen.get("previewUrl")
            if not url:
                continue
            ruta = destino / f"{tarea[:8]}_{indice}.png"
            self._descargar(url, ruta)
            log.info(f"  {ruta.name}  {imagen.get('width')}x{imagen.get('height')}")
            salida.append(ruta)
        return salida

    def _esperar(self, tarea: str) -> dict:
        limite = time.time() + _POLL_TIMEOUT
        while time.time() < limite:
            r = self._session.get(f"{BASE_TAREA}/task/{tarea}", timeout=_TIMEOUT)
            datos = (r.json() or {}).get("data") or {}
            estado = str(datos.get("status") or "").lower()
            if estado in _FAILED:
                raise Ai33ImageError(
                    f"Tarea {tarea} falló: {datos.get('message') or estado}")
            if estado in _DONE:
                return datos
            time.sleep(_POLL)
        raise Ai33ImageError(f"Tarea {tarea} no terminó en {int(_POLL_TIMEOUT)}s")

    def _descargar(self, url: str, destino: Path) -> None:
        with self._session.get(url, stream=True, timeout=_TIMEOUT) as r:
            r.raise_for_status()
            with open(destino, "wb") as fh:
                for trozo in r.iter_content(65536):
                    fh.write(trozo)
        if destino.stat().st_size < 2048:
            raise Ai33ImageError(f"Imagen vacía desde {url}")

    def report(self) -> None:
        if self.credits:
            log.info(f"ai33.pro imagen: {self.credits:,} créditos")
