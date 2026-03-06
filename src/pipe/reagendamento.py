import requests
import os
from src.plugins.TermColor import colored

N8N_REAGENDAMENTO_URL = os.getenv("N8N_REAGENDAMENTO_URL")

def enviar_reagendamento(payload: dict):
    """Envia o payload de reagendamento para o N8N."""
    if not N8N_REAGENDAMENTO_URL:
        colored.error("❌ N8N_REAGENDAMENTO_URL não configurada.")
        return None
    
    try:
        response = requests.post(N8N_REAGENDAMENTO_URL, json=payload, timeout=10)
        response.raise_for_status()
        colored.success(f"✅ Reagendamento enviado com sucesso: {response.status_code}")
        return response.json()
    except Exception as e:
        colored.error(f"❌ Erro ao enviar reagendamento: {str(e)}")
        return None

def processar_reagendamento(templates: list, lead_trace: dict, registro_redis: dict):
    """Processa a busca do próximo template e dispara o envio."""
    next_template = next((t for t in templates if t.get("status") == "em_espera"), None)
    if not next_template:
        return False

    t_id = next_template.get("template_identificador")
    payload = {
        "cliente_id": lead_trace.get("cliente_id"),
        "fluxo": registro_redis.get("hash_disparo", "reagendamento_automatico"),
        "templates": [t_id],
        "leads": [
            {
                "telefone": lead_trace.get("telefone"),
                "nome": lead_trace.get("lead_nome"),
                "template_params": { t_id: next_template.get("params", {}) },
                "midia_link": { t_id: next_template.get("midia_url") } if next_template.get("midia_url") else {}
            }
        ],
        "next_fail_template": False,
        "from_service": {
            "name": "traqueamento-pipeline",
            "user_send": "sistema"
        },
        "enterprise_id": registro_redis.get("enterprise"),
        "not_send_if_interaction_days": True,
        "days_limit": 5,
        "reagendamento": True,
        "lead_id": lead_trace.get("lead_id"),
    }
    
    return enviar_reagendamento(payload)



def processar_reagendamento(templates: list, lead_trace: dict, registro_redis: dict):
    """Processa a busca do próximo template e dispara o envio."""
    next_template = next((t for t in templates if t.get("status") == "em_espera"), None)
    if not next_template:
        return False

    t_id = next_template.get("template_identificador")
    payload = {
        "cliente_id": lead_trace.get("cliente_id"),
        "fluxo": registro_redis.get("hash_disparo", "reagendamento_automatico"),
        "templates": [t_id],
        "leads": [
            {
                "telefone": lead_trace.get("telefone"),
                "nome": lead_trace.get("lead_nome"),
                "template_params": { t_id: next_template.get("params", {}) },
                "midia_link": { t_id: next_template.get("midia_url") } if next_template.get("midia_url") else {}
            }
        ],
        "next_fail_template": False,
        "from_service": {
            "name": "traqueamento-pipeline",
            "user_send": "sistema"
        },
        "enterprise_id": registro_redis.get("enterprise"),
        "not_send_if_interaction_days": True,
        "days_limit": 5,
        "reagendamento": True,
        "lead_id": lead_trace.get("lead_id"),
    }
    
    return enviar_reagendamento(payload)