from typing import Dict, Any, Optional

def get_service_type(message_data: Dict[str, Any]) -> str:
    """
    Determina o tipo de serviço baseado nos metadados da mensagem.
    Tipos: 'disparo', 'followup' ou 'conversation'.
    """
    # {ASSUNÇÃO: o campo 'type' na tabela messages já contém essa informação}
    service_type = message_data.get("type", "conversation")
    if service_type in ["disparo", "followup", "conversation"]:
        return service_type
    return "conversation"

def is_critical(error_data: Optional[Dict[str, Any]]) -> bool:
    """
    Determina se o erro é crítico baseado nos detalhes da tabela meta_erros.
    Erros críticos exigem bloqueio (blacklist) e notificação.
    """
    if not error_data:
        return False
    
    # {ASSUNÇÃO: o campo critical_template ou o código de erro define a criticidade}
    return error_data.get("critical_template", False)

def format_error_alert(
    error_data: Optional[Dict[str, Any]], 
    service: str, 
    lead_id: Any, 
    error_msg: str,
    manual_code: Any = None,
    manual_solucoes: str = None
) -> str:
    """
    Formata o alerta de erro para o WhatsApp seguindo o template do usuário.
    """
    error_code = manual_code or (error_data.get("erro", "N/A") if error_data else "N/A")
    recomendacao = manual_solucoes or (error_data.get("solucoes", "Verificar logs técnicos") if error_data else "Verificar logs técnicos")
    
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        "🚨 *ALERTA DE ERRO DA META*\n"
        f"Serviço: {service}\n"
        "Evento: Falha no processamento de lead\n"
        f"Lead ID: {lead_id}\n"
        f"Codigo Erro: {error_code}\n"
        "Erro:\n"
        f"{error_msg}\n\n"
        f"Timestamp: {now}\n\n"
        "Ação recomendada:\n"
        f"{recomendacao}"
    )

def format_redis_failure_alert(
    wamid: str,
    servico: str,
    telefone: str,
    lead_nome: str,
    lead_id: Any
) -> str:
    """
    Formata o alerta para quando o registro de envio não é encontrado no Redis.
    """
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        "⚠️ *AVISO: FALHA DE REAGENDAMENTO*\n"
        f"A mensagem `{wamid}` foi feita pelo serviço: *{servico}* não pôde ser reagendada.\n\n"
        "*Detalhes:* \n"
        f"Lead: {lead_nome} (ID: {lead_id})\n"
        f"Telefone: +{telefone}\n"
        "Motivo: Não foi configurada uma Retentativa .\n\n"
        f"Timestamp: {now}\n"
        "_Nada foi enviado para o lead._"
    )

def get_meta_error_details(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extrai código, mensagem e detalhes de erro do payload da Meta.
    Procura em entry.changes.value.statuses.errors ou entry.changes.value.errors.
    """
    try:
        entries = payload.get("entry", [])
        if not entries: return None
        
        changes = entries[0].get("changes", [])
        if not changes: return None
        
        value = changes[0].get("value", {})
        
        # Caso 1: Erro em statuses (falha de entrega)
        statuses = value.get("statuses", [])
        if statuses and statuses[0].get("errors"):
            err = statuses[0]["errors"][0]
            return {
                "code": err.get("code"),
                "message": err.get("message") or err.get("title"),
                "details": err.get("error_data", {}).get("details", "")
            }
            
        # Caso 2: Erro direto no value (ex: erros de inbound)
        errors = value.get("errors", [])
        if errors:
            err = errors[0]
            return {
                "code": err.get("code"),
                "message": err.get("message"),
                "details": err.get("error_data", {}).get("details", "")
            }
            
    except Exception:
        pass
    return None

def get_lead_info_for_blacklist(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extrai informações necessárias para a tabela black_leads do payload da Meta.
    Principalmente phone_number (recipient_id) e conversation_id.
    """
    try:
        entries = payload.get("entry", [])
        if not entries: return None
        
        changes = entries[0].get("changes", [])
        if not changes: return None
        
        value = changes[0].get("value", {})
        
        # O telefone do lead está em recipient_id nos statuses
        statuses = value.get("statuses", [])
        if statuses:
            status = statuses[0]
            return {
                "phone_number": status.get("recipient_id"),
                "conversation_id": payload.get("conversation_id"), # {ASSUNÇÃO: pode vir no payload principal}
            }
            
    except Exception:
        pass
    return None
