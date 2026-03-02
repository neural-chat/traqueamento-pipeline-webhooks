#import requests
from typing import Dict, Any
import requests

import os
from dotenv import load_dotenv

load_dotenv()

url_webhook = os.getenv("WEBHOOK_URL")

def send_webhook(
    payload: dict,
    headers: dict | None = None,
    url: str | None = None,
    end_webhook: str | None = None,
    timeout: float = 5.0
) -> requests.Response | None:
    """
    Envia um payload JSON para um webhook via POST.
    Retorna o objeto Response em caso de sucesso,
    ou None se der erro na requisição.
    """
    global url_webhook
    url_final = end_webhook or url or url_webhook
    hdrs = headers or {"Content-Type": "application/json"}
    print(f"🚀 Enviando payload pro webhook [bold]{url_final}[/]...")

    try:
        del payload['createdAt']
        del payload['dataAtual']
        resp = requests.post(url_final, json=payload, headers=hdrs, timeout=timeout)
        resp.raise_for_status()
        print(f"✅ Sucesso! Status {resp.status_code}")
        return resp

    except requests.HTTPError as http_err:
        print(f"❌ Erro HTTP ao chamar webhook: {http_err}")
    except requests.RequestException as req_err:
        print(f"❌ Falha na requisição: {req_err}")

    return None