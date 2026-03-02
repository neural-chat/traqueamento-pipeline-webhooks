#!/usr/bin/env python3
"""
Script de teste REAL que envia payload para o Celery worker de verdade
"""

import json
import sys
from src.celery_app import celery_app

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

# Payload de status failed (para testar outra rota)
payload_status_failed = {
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "field": "messages",
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "16505551111",
                            "phone_number_id": "123456123"
                        },
                        "statuses": [
                            {
                                "id": "wamid.XXX",
                                "status": "failed",
                                "timestamp": "1504902988",
                                "recipient_id": "5511999999999",
                                "errors": [
                                    {
                                        "code": 131047,
                                        "title": "Message undeliverable",
                                        "message": "The message was not delivered",
                                        "error_data": {
                                            "details": "Message expired"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
    ]
}

# Payload de non-messages event
payload_non_messages = {
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "field": "message_status",
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "16505551111",
                            "phone_number_id": "123456123"
                        }
                    }
                }
            ]
        }
    ]
}


def send_to_celery(payload: dict, payload_name: str = "payload"):
    """
    Envia um payload para o Celery worker usando a task save_webhook_event
    """
    print(f"\n{'='*60}")
    print(f"📤 Enviando {payload_name} para o Celery...")
    print(f"{'='*60}")
    
    try:
        # Envia a task para o Celery
        # O Celery aceita dict, str ou bytes - vamos enviar como dict
        result = celery_app.send_task(
            'save_webhook_event',
            args=[payload],
            queue='traqueamento_payloads'
        )
        
        print(f"✅ Task enviada com sucesso!")
        print(f"   Task ID: {result.id}")
        
        # Tenta obter o status apenas se o backend estiver configurado
        try:
            status = result.state
            print(f"   Status: {status}")
        except (AttributeError, NotImplementedError):
            print(f"   Status: Enviado (backend de resultados não configurado)")
        
        print(f"\n💡 Verifique os logs do worker do Celery para ver o processamento")
        print(f"   O worker deve processar e classificar o payload automaticamente")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao enviar task: {e}")
        import traceback
        traceback.print_exc()
        return None


def send_as_json_string(payload: dict, payload_name: str = "payload"):
    """
    Envia como JSON string (simula como vem do RabbitMQ)
    """
    print(f"\n{'='*60}")
    print(f"📤 Enviando {payload_name} como JSON string...")
    print(f"{'='*60}")
    
    try:
        # Converte para JSON string (como vem do RabbitMQ)
        payload_json = json.dumps(payload)
        
        result = celery_app.send_task(
            'save_webhook_event',
            args=[payload_json],
            queue='traqueamento_payloads'
        )
        
        print(f"✅ Task enviada com sucesso!")
        print(f"   Task ID: {result.id}")
        
        # Tenta obter o status apenas se o backend estiver configurado
        try:
            status = result.state
            print(f"   Status: {status}")
        except (AttributeError, NotImplementedError):
            print(f"   Status: Enviado (backend de resultados não configurado)")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao enviar task: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Função principal"""
    print("\n" + "🚀" * 30)
    print("TESTE REAL - Enviando payloads para o Celery Worker")
    print("🚀" * 30)
    
    print("\n⚠️  CERTIFIQUE-SE de que o Celery worker está rodando:")
    print("   celery -A src.celery_app worker --loglevel=info -Q traqueamento_payloads")
    
    # Menu de opções
    if len(sys.argv) > 1:
        payload_type = sys.argv[1].lower()
    else:
        print("\n📋 Escolha o tipo de payload:")
        print("   1. automatic_events (padrão)")
        print("   2. status_failed")
        print("   3. non_messages")
        print("   4. todos")
        payload_type = input("\nDigite o número ou nome: ").strip()
    
    # Mapeia escolhas
    if payload_type in ['1', 'automatic_events', '']:
        send_to_celery(payload_automatic_events, "automatic_events")
        
    elif payload_type in ['2', 'status_failed', 'failed']:
        send_to_celery(payload_status_failed, "status_failed")
        
    elif payload_type in ['3', 'non_messages', 'non-messages']:
        send_to_celery(payload_non_messages, "non_messages")
        
    elif payload_type in ['4', 'todos', 'all']:
        print("\n🔄 Enviando todos os tipos de payload...")
        send_to_celery(payload_automatic_events, "automatic_events")
        send_to_celery(payload_status_failed, "status_failed")
        send_to_celery(payload_non_messages, "non_messages")
        
    else:
        print(f"❌ Opção inválida: {payload_type}")
        print("   Use: automatic_events, status_failed, non_messages ou todos")
        return
    
    print("\n" + "="*60)
    print("✅ Teste concluído!")
    print("="*60)
    print("\n💡 Dica: Use 'celery -A src.celery_app inspect active' para ver tasks ativas")
    print("   Ou monitore os logs do worker para ver o processamento em tempo real\n")


if __name__ == "__main__":
    main()

