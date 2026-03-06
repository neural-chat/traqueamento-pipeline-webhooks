import os, json, time
from supabase import create_client, Client
from src.plugins.TermColor import colored


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_message_by_canal_uuid(canal_uuid: str):
    """Busca mensagem pelo ID da Meta (canal_uuid)."""
    response = supabase_client.table("messages").select("*").eq("canal_uuid", canal_uuid).execute()
    return response.data[0] if response.data else None


def get_meta_erro(erro_code: int):
    """Busca detalhes e soluções de um erro da Meta pelo código."""
    response = supabase_client.table("meta_erros").select("*").eq("erro", erro_code).execute()
    return response.data[0] if response.data else None


def insert_black_lead(data: dict):
    """Insere um lead na lista negra (blacklist)."""
    response = supabase_client.table("black_leads").insert(data).execute()
    return response.data


def insert_log_reagendamento(data: dict):
    """Insere um log de tentativa de reagendamento."""
    response = supabase_client.table("logs_reagendamentos").insert(data).execute()
    return response.data


def rastrear_lead_por_message_id(message_id: str, context: list = None) -> dict | None:
    """Chama a RPC rastrear_lead_por_message_id com até 3 tentativas (retry)."""
    params = {"p_message_id": message_id}
    if context:
        params["p_invalid_types"] = context

    for attempt in range(3):
        colored.alert(f"🔍 Tentativa {attempt + 1}/3 de pesquisa: {message_id}")
        response = supabase_client.rpc("rastrear_lead_por_message_id", params).execute()
        if response.data:
            colored.success(f"✅ Lead encontrado na tentativa {attempt + 1}")
            return response.data[0]
        
        if attempt < 2:  # Não espera na última tentativa
            colored.error(f"⚠️ Tentativa {attempt + 1} sem sucesso, retentando em 2s...")
            time.sleep(2)

    colored.error(f"❌ Todas as 3 tentativas falharam para: {message_id}")
    return None



def update_message_error(wamid: str, status: str, code: int, details: str):
    """Atualiza o status e metadados de erro de uma mensagem."""
    msg = get_message_by_canal_uuid(wamid)
    if not msg:
        return None

    metdado = msg.get("metdado", {})
    if isinstance(metdado, str):
        try:
            metdado = json.loads(metdado)
        except:
            metdado = {}

    metdado["code_error"] = code
    metdado["wpp_error_message"] = details

    update_data = {
        "status": status,
        "read": False,
        "metdado": json.dumps(metdado) if isinstance(msg.get("metdado"), str) else metdado
    }

    response = supabase_client.table("messages").update(update_data).eq("canal_uuid", wamid).execute()
    return response.data


def get_strategy_by_canal_uuid(canal_uuid: str):
    """
    Busca o lead_id pela canal_uuid (messages) e retorna lead_id + last_strategy.
    """
    msg = supabase_client.table("messages").select("lead_id, type").eq("canal_uuid", canal_uuid).limit(1).execute()
    if not msg.data:
        return None

    lead_id = msg.data[0]["lead_id"]
    service_send = msg.data[0].get("type")

    lead = supabase_client.table("leads_whatsapp").select("last_strategy").eq("id", lead_id).limit(1).execute()
    if not lead.data:
        return None

    return {
        "lead_id": lead_id,
        "last_strategy": lead.data[0]["last_strategy"],
        "service_send": service_send
    }