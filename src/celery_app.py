
from celery import Celery
from celery.signals import worker_ready
from src.config import RABBIT_URL              
import json, time       # ← adiciona time
from src.db.mongo import collection,collectionEvents,collectionVariadic 
import pytz
from datetime import datetime
from src.config import RABBIT_URL
from src.n8n import webhooks
from src.utils.thread_logs import log_webhook_start, log_webhook_action, log_webhook_error, log_webhook_skip
from src.policy.error_policy import format_error_alert, get_meta_error_details, is_critical, get_lead_info_for_blacklist, format_redis_failure_alert
from src.plugins.Evolution.evolution_api import send_group_message
from src.supabase.client import (
    get_meta_erro, 
    insert_black_lead, 
    get_strategy_by_canal_uuid, 
    rastrear_lead_por_message_id, 
    update_message_error,
    insert_log_reagendamento
)
from src.plugins.TermColor import colored
from src.pipe.traqueamento import is_status_failed,is_non_messages_event,is_automatic_events
from pyfiglet import Figlet
from copy import deepcopy

from src.plugins.Redis.connection.redis_connection import RedisConnectionHandle
from src.plugins.Redis.redis_repository import RedisRepository

import os
from dotenv import load_dotenv
load_dotenv()


redis_conn = RedisConnectionHandle().connect()
redis_repository = RedisRepository(redis_conn)


def cronner_say(message:str):
    fig = Figlet(font='slant',width=1000)
    print(fig.renderText(message))
    

TZ_SP = pytz.timezone("America/Sao_Paulo")                      

celery_app = Celery(
    "traqueamento_payloads",
    broker=RABBIT_URL,
    include=["src.celery_app"]  # Importa o módulo atual
)


celery_app.conf.update(
    task_acks_late=True,          
    task_default_queue="traqueamento_payloads",
    task_default_exchange="amq.topic",
    task_default_exchange_type="topic",
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)



# ── 🔔 hook de inicialização ───────────────────────────────────
@worker_ready.connect
def ensure_ttl_index(**kwargs):
    from src.db.mongo import init_ttl_index        
    try:
        init_ttl_index()
    except Exception as exc:
        import logging
        logging.getLogger("worker").exception(
            "Falha ao criar índice TTL no startup – continuando sem TTL", exc_info=exc
        )

@celery_app.task(name="save_webhook_event")
def save_webhook_event(body):

    cronner_say("TRAQUEAMENTO")

    # ---------- 1) Parse seguro ----------
    if isinstance(body, (bytes, bytearray)):
        body = body.decode()             # bytes → str
    if isinstance(body, str):
        body = json.loads(body)          # str → dict
    if not isinstance(body, dict):
        raise TypeError(f"Tipo de payload inesperado: {type(body)}")

    # NÃO mutar o objeto de entrada (Celery cuida dele nos retries)
    data = deepcopy(body)

    # Garante timestamp de criação
    data_criacao = datetime.now(TZ_SP).astimezone(pytz.utc)
    data.setdefault("createdAt", data_criacao)
    data["dataAtual"] = data_criacao


    try:
        wamid = None
        recipient_id = None
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                field = change.get("field", "messages")
                if field != "messages":
                    log_webhook_action("webhook", "EVENTO", f"Campo: {field}")
                    colored.debug_vars(dados=data, title_table=f"🔔  Evento: {field}")
                else:
                    colored.debug_vars(dados=data, title_table="📦  Novo webhook recebido")

                val = change.get("value", {})
                for s in val.get("statuses", []):
                    wamid = s.get("id")

        # Log bonito na sua tabela fancy
        log_webhook_start("traqueamento", wamid)
        # ---------- 2) Rotas de persistência ----------
        # CASE A: Eventos de falha (Meta Status Error)
        if is_status_failed(data):
            # 1. Persistência bruta no MongoDB (Log de Erros)
            collection.insert_one(deepcopy(data))
            
            # 2. Extração e Busca do Erro (Meta + Supabase)
            meta_err_info = get_meta_error_details(data)
            if meta_err_info:
                code = meta_err_info.get("code")
                supabase_err = get_meta_erro(code) if code else None

                # 3. Rastreamento do Lead (RPC Supabase)
                # Passamos o contexto explicitamente conforme nova regra
                lead_trace = rastrear_lead_por_message_id(wamid, ['context', 'tool']) if wamid else None
                if lead_trace:
                    colored.debug_vars(dados=lead_trace, title_table="📦  Lead trace")
                else:
                    colored.success_bg(f"📦 Lead trace: N/A (não encontrado) ({lead_trace}) 🆗 ")
                # 4. Formatação de Dados para Alerta/Log
                lead_suffix = (
                    f" | lead={lead_trace['lead_id']} ({lead_trace['lead_nome']}) "
                    f"tel={lead_trace['telefone']} etapa={lead_trace['etapa']} "
                    f"cliente={lead_trace['cliente_nome']}"
                ) if lead_trace else f" | tel={recipient_id}" if recipient_id else ""

                lead_id_display = (f"{lead_trace['lead_id']} – {lead_trace['lead_nome']} ({lead_trace['cliente_nome']})") if lead_trace else (data.get("lead_id") or recipient_id or "N/A")

                error_msg_display = (
                    f"{meta_err_info['message']} - {meta_err_info['details']}"
                    + (f"\n📱 Tel: {lead_trace['telefone']} | Etapa: {lead_trace['etapa']}" if lead_trace else f"\n📱 Tel: {recipient_id}" if recipient_id else "")
                )

                alert_msg = format_error_alert(
                    error_data=supabase_err,
                    service=lead_trace.get('message_type') if lead_trace else "traqueamento",
                    lead_id=lead_id_display,
                    error_msg=error_msg_display,
                    manual_code=code
                )

                # 5. Lógica de Lote de Notificações (Redis Rate Limiting)
                # Envia notificação a cada 10 ocorrências por cliente/serviço
                should_notify = True
                if lead_trace:
                    cliente_id = lead_trace.get("cliente_id")
                    servico = lead_trace.get("message_type", "traqueamento")
                    redis_key = f"notificacoes:erro:{cliente_id}:{servico}"
                    
                    count = redis_repository.get(redis_key)
                    count = int(count) + 1 if count else 1
                    
                    if count >= 10:
                        redis_repository.delete_key(redis_key)
                        should_notify = True
                    else:
                        redis_repository.insert_ex(redis_key, str(count), ex=86400) # TTL 24h
                        should_notify = False

                # 6. Disparo do Alerta (se o lote fechou)
                if should_notify:
                    send_group_message(alert_msg)
                    log_webhook_action("failed", "ALERTA ENVIADO", f"code={code}{lead_suffix}")
                else:
                    log_webhook_action("failed", "LOTE AGUARDANDO", f"code={code} count={count}{lead_suffix}")

                # 7. Atualização de Mensagem (Supabase)
                # Extrai status específico (delivered, read, failed, etc)
                status_wpp = next(
                    (s.get("status", "failed") for entry in data.get("entry", [])
                     for change in entry.get("changes", [])
                     for s in change.get("value", {}).get("statuses", [])),
                    "failed"
                )
                update_message_error(wamid, status_wpp, code, meta_err_info['details'])

                # 8. Lógica de Blacklist (Bloqueio de Lead)
                if is_critical(supabase_err):
                    lead_info = get_lead_info_for_blacklist(data)
                    if lead_info:
                        if wamid:
                            strat = get_strategy_by_canal_uuid(wamid)
                            if strat:
                                lead_info.update({
                                    "strategy": strat.get("last_strategy"),
                                    "conversation_id": wamid,
                                    "service_send": strat.get("service_send")
                                })
                        lead_info["erro_code"] = code
                        insert_black_lead(lead_info)
                        log_webhook_action("failed", "BLACKLIST", f"phone={lead_info.get('phone_number')}{lead_suffix}")
                else:
                    log_webhook_action("failed", "NÃO CRÍTICO", f"code={code}{lead_suffix}")
                    # Reagendamento para erros não críticos
                    if wamid:
                        redis_key = f"registro_envio_lead:{wamid}"
                        registro_redis = redis_repository.get_json(redis_key)
                        
                        # Registro de Log de Reagendamento
                        if registro_redis:
                            last_sent_template = None
                            all_templates_sent = False
                            
                            if registro_redis and registro_redis.get("templates"):
                                templates = registro_redis.get("templates")
                                sent_templates = [t for t in templates if t.get("status") == "enviado"]
                                
                                if sent_templates:
                                    last_sent_template = sent_templates[-1]
                                
                                # Se o número de enviados for igual ao total, todos foram tentados
                                if len(sent_templates) == len(templates):
                                    all_templates_sent = True

                            log_data = {
                                "cliente_id": lead_trace.get("cliente_id"),
                                "nome_lead": lead_trace.get("lead_nome"),
                                "identificador": lead_trace.get("telefone"),
                                "strategy": registro_redis.get("strategy") if registro_redis else None,
                                "servico": lead_trace.get("message_type"),
                                "conversation_id": wamid,
                                "template": json.dumps(last_sent_template) if last_sent_template else None,
                                "enterprise_id": registro_redis.get("enterprise") if registro_redis else None
                            }
                            insert_log_reagendamento(log_data)

                            # --- Reagendamento efetivo (Próximo Template) ---
                            from src.pipe.reagendamento import processar_reagendamento
                            if processar_reagendamento(templates, lead_trace, registro_redis):
                                log_webhook_action("failed", "REAGENDAMENTO ENVIADO", f"wamid={wamid}")

                            # Alerta de exaustão de alternativas
                            if all_templates_sent:
                                telefone = lead_trace.get('telefone', 'N/A')
                                lead_nome = lead_trace.get('lead_nome', 'N/A')
                                alert_exhausted = (
                                    f"⚠️ *TODAS ALTERNATIVAS TENTADAS*\n"
                                    f"Tentamos todas as alternativas de template para o lead {lead_nome} (+{telefone}) "
                                    f"no disparo `{lead_trace.get('message_type')}` e não obtivemos sucesso.\n\n"
                                    f"O último registro que tivemos foi com o ID: `{wamid}` e o serviço utilizado foi: *{lead_trace.get('message_type')}*"
                                )
                                send_group_message(alert_exhausted)
                                log_webhook_action("failed", "EXAUSTAO TEMPLATES", f"wamid={wamid}")



                            log_webhook_action("failed", "REAGENDAMENTO", f"wamid={wamid}")
                            
                        else:
                            if lead_trace:
                                alert_msg = format_redis_failure_alert(
                                    wamid=wamid,
                                    servico=lead_trace.get('message_type', 'N/A'),
                                    telefone=lead_trace.get('telefone', 'N/A'),
                                    lead_nome=lead_trace.get('lead_nome', 'N/A'),
                                    lead_id=lead_trace.get('lead_id', 'N/A')
                                )
                                send_group_message(alert_msg)
                                log_webhook_action("failed", "ALERTA SEM REAGENDAMENTO", f"wamid={wamid}")

                    

            _update_last_ts()



        elif is_automatic_events(data):
            url_webhook = os.getenv("N8N_AUTOMATICS_EVENTS")
            # webhooks.send_webhook(deepcopy(data),end_webhook=url_webhook)
            log_webhook_action("automatic", "ENVIADO", f"Evento: {field}")
            _update_last_ts()

        elif is_non_messages_event(data):
            collectionEvents.insert_one(deepcopy(data))
            log_webhook_action("events", "SALVO", f"Evento: {field}")
            _update_last_ts()
            
        # ---------- 3) Caso não seja nenhuma das duas categorias ----------
        else:
            collectionVariadic.insert_one(deepcopy(data))
            log_webhook_action("variadic", "SALVO", f"Evento: {field}")
            _update_last_ts()
            
        

    except Exception as exc:
        # Retenta sem deixar o ObjectId poluir o payload original
        log_webhook_error("processamento", f"{exc!r} — entrando em retry")

        # Envio de Alerta para o Grupo de Logs (WhatsApp)
        try:
            lead_id = data.get("lead_id") or data.get("leadId") or "N/A"
            alert_msg = format_error_alert(
                error_data=None, 
                service="traqueamento erros",
                lead_id=lead_id,
                error_msg=str(exc)
            )
            send_group_message(alert_msg)
        except Exception as alert_exc:
            print(f"❌ Falha ao enviar alerta de WhatsApp: {alert_exc}")

        raise exc
        


def _update_last_ts():
    global _last_msg_ts
    _last_msg_ts = time.time()

    