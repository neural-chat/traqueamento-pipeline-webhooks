import os
import requests
from typing import Optional

def send_group_message(message: str, group_id: Optional[str] = None) -> bool:
    """
    Envia uma mensagem de texto para um grupo via Evolution API.
    Se group_id não for passado, usa a variável de ambiente EVOLUTION_GROUP_ID.
    """
    base_url = os.getenv("EVOLUTION_URL")
    api_key = os.getenv("EVOLUTION_API_KEY")
    instance = os.getenv("EVOLUTION_INSTANCE")
    target_group = group_id or os.getenv("EVOLUTION_GROUP_ID")
    
    if not (base_url and api_key and instance and target_group):
        print("❌ [Evolution] Credenciais ou Group ID ausentes no .env")
        return False
        
    url = f"{base_url}/message/sendText/{instance}"
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    
    payload = {
        "number": target_group,
        "text": message,
        "delay": 1200,
        "linkPreview": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ [Evolution] Erro ao enviar mensagem: {e}")
        return False
