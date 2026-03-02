#!/usr/bin/env python3
"""
Script de teste para validar o payload de automatic_events
"""

import json
from src.pipe.traqueamento import is_automatic_events

# Payload de exemplo baseado na estrutura fornecida
payload_automatic_events = {
    "entry": [
        {
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

# Payload que NÃO deve ser detectado como automatic_events (sem a key automatic_events em value)
payload_not_automatic = {
    "entry": [
        {
            "changes": [
                {
                    "field": "automatic_events",
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "16505551111",
                            "phone_number_id": "123456123"
                        }
                        # Sem a key "automatic_events" aqui
                    }
                }
            ]
        }
    ]
}

# Payload com field diferente
payload_different_field = {
    "entry": [
        {
            "changes": [
                {
                    "field": "messages",
                    "value": {
                        "messaging_product": "whatsapp",
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


def test_is_automatic_events():
    """Testa a função is_automatic_events com diferentes payloads"""
    
    print("=" * 60)
    print("🧪 TESTE: is_automatic_events")
    print("=" * 60)
    
    # Teste 1: Payload correto com automatic_events
    print("\n📦 Teste 1: Payload com field='automatic_events' e key 'automatic_events' em value")
    print("-" * 60)
    result1 = is_automatic_events(payload_automatic_events)
    print(f"Resultado: {result1}")
    print(f"✅ Esperado: True | Obtido: {result1}")
    assert result1 == True, "❌ Falhou! Deveria retornar True"
    print("✅ PASSOU!")
    
    # Teste 2: Payload sem a key automatic_events em value
    print("\n📦 Teste 2: Payload com field='automatic_events' mas SEM key 'automatic_events' em value")
    print("-" * 60)
    result2 = is_automatic_events(payload_not_automatic)
    print(f"Resultado: {result2}")
    print(f"✅ Esperado: False | Obtido: {result2}")
    assert result2 == False, "❌ Falhou! Deveria retornar False"
    print("✅ PASSOU!")
    
    # Teste 3: Payload com field diferente
    print("\n📦 Teste 3: Payload com field diferente de 'automatic_events'")
    print("-" * 60)
    result3 = is_automatic_events(payload_different_field)
    print(f"Resultado: {result3}")
    print(f"✅ Esperado: False | Obtido: {result3}")
    assert result3 == False, "❌ Falhou! Deveria retornar False"
    print("✅ PASSOU!")
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)


def test_payload_structure():
    """Mostra a estrutura do payload formatada"""
    print("\n" + "=" * 60)
    print("📋 ESTRUTURA DO PAYLOAD DE TESTE")
    print("=" * 60)
    print(json.dumps(payload_automatic_events, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("\n🚀 Iniciando testes...\n")
    
    # Mostra a estrutura do payload
    test_payload_structure()
    
    # Executa os testes
    test_is_automatic_events()
    
    print("\n✨ Testes concluídos!\n")



