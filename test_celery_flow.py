#!/usr/bin/env python3
"""
Script de teste para validar o fluxo completo do celery_app com automatic_events
"""

import json
import os
from datetime import datetime
import pytz
from copy import deepcopy
from src.pipe.traqueamento import is_automatic_events, is_status_failed, is_non_messages_event

# Payload completo de automatic_events
payload_automatic_events = {
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "field": "automatic_events",
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "16505551111",
                            "phone_number_id": "123456123"
                        },
                        "automatic_events": [
                            {
                                "id": "ABGGFlA5Fpa",
                                "event_name": "purchase",
                                "timestamp": 1504902988
                            }
                        ]
                    }
                }
            ]
        }
    ]
}


def test_classification():
    """Testa a classificação do payload"""
    
    print("=" * 60)
    print("🧪 TESTE: Classificação de Payloads")
    print("=" * 60)
    
    # Adiciona timestamps como o celery_app faz
    TZ_SP = pytz.timezone("America/Sao_Paulo")
    data_criacao = datetime.now(TZ_SP).astimezone(pytz.utc)
    payload = deepcopy(payload_automatic_events)
    payload.setdefault("createdAt", data_criacao)
    payload["dataAtual"] = data_criacao
    
    print("\n📦 Testando payload de automatic_events:")
    print("-" * 60)
    print(f"is_status_failed: {is_status_failed(payload)}")
    print(f"is_automatic_events: {is_automatic_events(payload)}")
    print(f"is_non_messages_event: {is_non_messages_event(payload)}")
    
    # Verifica qual rota seria tomada
    if is_status_failed(payload):
        print("\n📍 Rota: is_status_failed → collection.insert_one")
    elif is_automatic_events(payload):
        print("\n📍 Rota: is_automatic_events → webhook N8N_AUTOMATICS_EVENTS")
        url_webhook = os.getenv("N8N_AUTOMATICS_EVENTS")
        print(f"   URL Webhook: {url_webhook or 'Não configurado'}")
    elif is_non_messages_event(payload):
        print("\n📍 Rota: is_non_messages_event → collectionEvents.insert_one")
    else:
        print("\n📍 Rota: default → collectionVariadic.insert_one")
    
    print("\n✅ Classificação concluída!")


def simulate_celery_flow():
    """Simula o fluxo do celery_app.save_webhook_event"""
    
    print("\n" + "=" * 60)
    print("🔄 SIMULAÇÃO: Fluxo do celery_app.save_webhook_event")
    print("=" * 60)
    
    # Simula o body que vem do RabbitMQ
    body = json.dumps(payload_automatic_events)
    
    # Parse como o celery_app faz
    if isinstance(body, (bytes, bytearray)):
        body = body.decode()
    if isinstance(body, str):
        body = json.loads(body)
    
    # Deepcopy e adiciona timestamps
    data = deepcopy(body)
    TZ_SP = pytz.timezone("America/Sao_Paulo")
    data_criacao = datetime.now(TZ_SP).astimezone(pytz.utc)
    data.setdefault("createdAt", data_criacao)
    data["dataAtual"] = data_criacao
    
    print("\n📋 Payload processado:")
    print(f"   Tipo: {type(data)}")
    print(f"   Keys: {list(data.keys())}")
    print(f"   createdAt: {data.get('createdAt')}")
    
    # Simula a lógica de roteamento
    print("\n🔀 Roteamento:")
    print("-" * 60)
    
    try:
        if is_status_failed(data):
            print("✅ [failed] → collection.insert_one + webhook")
        elif is_automatic_events(data):
            print("✅ [automatic events] → webhook N8N_AUTOMATICS_EVENTS")
            url_webhook = os.getenv("N8N_AUTOMATICS_EVENTS")
            if url_webhook:
                print(f"   📤 Enviaria para: {url_webhook}")
            else:
                print("   ⚠️  N8N_AUTOMATICS_EVENTS não configurado!")
        elif is_non_messages_event(data):
            print("✅ [non-messages] → collectionEvents.insert_one")
        else:
            print("ℹ️  [variadic] → collectionVariadic.insert_one")
            
    except Exception as exc:
        print(f"❌ Erro: {exc!r}")
        raise
    
    print("\n✅ Simulação concluída!")


if __name__ == "__main__":
    print("\n🚀 Iniciando testes de fluxo...\n")
    
    # Testa classificação
    test_classification()
    
    # Simula fluxo completo
    simulate_celery_flow()
    
    print("\n✨ Testes concluídos!\n")

