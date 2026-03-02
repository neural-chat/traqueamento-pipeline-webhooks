from math import e
from src.n8n.webhooks import send_webhook


def is_status_failed(payload: dict) -> bool:
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for status in value.get("statuses", []):
                if status.get("status") == "failed" and status.get("errors"):
                    return True
    return False




def is_non_messages_event(payload: dict) -> bool:
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            # pega o valor de 'field' (pode vir vazio ou None)
            field = change.get("field")
            if field and field != "messages":
                return True
    return False


def is_automatic_events(payload: dict) -> bool:
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            # pega o valor de 'field' (pode vir vazio ou None)
            field = change.get("field")
            value = change.get("value", {})
            # verifica se field é "automatic_events" E se existe a key "automatic_events" em value
            if field and field == "automatic_events" and "automatic_events" in value:
                return True
    return False




def extract_whatsapp_error_info(payload: dict) -> dict | None:
    try:
        change = payload["entry"][0]["changes"][0]
        value = change["value"]
        status = value["statuses"][0]
        error = status["errors"][0]

        payload = {
            "title": error["title"],
            "message": error["message"],
            "code": error["code"],
            "details": error["error_data"]["details"],
            "phone_number_id": value["metadata"]["phone_number_id"],
            "lead": status["recipient_id"],
            "status": status["status"],
            "token_cliente": payload["_meta"]["token_cliente"],
        }
        
        sender = send_webhook(payload)
        if sender:
            print(f"✅ Webhook enviado com sucesso: {sender.status_code}")
        else:
            print("❌ Falha ao enviar webhook.")
        

    except (KeyError, IndexError, TypeError) as e:
        print(f"⚠️ Não encontrei as chaves esperadas: {e}")
        return None
    