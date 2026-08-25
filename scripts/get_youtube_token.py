"""Obtiene el refresh token de YouTube. Se ejecuta UNA VEZ, en tu ordenador.

Antes de correrlo:

  1. Entra en https://console.cloud.google.com/ y crea un proyecto.
  2. APIs y servicios -> Biblioteca -> activa "YouTube Data API v3".
  3. Pantalla de consentimiento OAuth -> tipo "Externo" -> rellena lo minimo ->
     en "Usuarios de prueba" anade tu propio correo de Google.
  4. Credenciales -> Crear credenciales -> ID de cliente de OAuth ->
     tipo "Aplicacion de escritorio". Descarga el JSON.
  5. Guarda ese JSON en la raiz del repo como client_secret.json
     (ya esta en .gitignore, no se sube).

Luego:

    python scripts/get_youtube_token.py

Se abre el navegador, das permiso con la cuenta del canal y el script imprime
los tres valores que hay que meter en los secrets de GitHub.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: E402

from pipeline.config import ROOT  # noqa: E402
from pipeline.providers.youtube import SCOPES  # noqa: E402


def main() -> int:
    secret = ROOT / "client_secret.json"
    if not secret.exists():
        candidates = sorted(ROOT.glob("client_secret*.json"))
        if not candidates:
            print(
                f"No encuentro {secret.name} en {ROOT}.\n"
                "Descarga el JSON de credenciales OAuth (tipo 'Aplicacion de escritorio') "
                "desde Google Cloud Console y guardalo ahi.",
                file=sys.stderr,
            )
            return 1
        secret = candidates[0]

    print(f"Usando {secret.name}")
    print("Se va a abrir el navegador. Entra con la cuenta del canal de YouTube.\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES)
    # prompt=consent fuerza que Google devuelva refresh_token tambien si ya
    # habias autorizado antes; sin esto el segundo intento llega sin token.
    credentials = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    if not credentials.refresh_token:
        print(
            "\nGoogle no devolvio refresh_token. Revoca el acceso en "
            "https://myaccount.google.com/permissions y vuelve a ejecutar.",
            file=sys.stderr,
        )
        return 1

    print("\n" + "=" * 72)
    print("LISTO. Crea estos tres secrets en tu repositorio de GitHub:")
    print("Settings -> Secrets and variables -> Actions -> New repository secret")
    print("=" * 72)
    print(f"\nYT_CLIENT_ID\n{credentials.client_id}")
    print(f"\nYT_CLIENT_SECRET\n{credentials.client_secret}")
    print(f"\nYT_REFRESH_TOKEN\n{credentials.refresh_token}")
    print("\n" + "=" * 72)
    print("No los pegues en ningun archivo del repo. Solo en Secrets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
