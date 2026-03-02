from xml.etree.ElementInclude import include
from celery import Celery
from celery.signals import worker_ready
import asyncio
from src.config import RABBIT_URL              
import json, time       # ← adiciona time
from src.db.mongo import collection,collectionEvents,collectionVariadic 
import pytz
from datetime import datetime
from src.config import RABBIT_URL
from src.n8n import webhooks
from src.utils.utils_logs import log_payload_table
from src.plugins.TermColor.colored import debug_vars
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
    

BROKER_URL = RABBIT_URL
TZ_SP = pytz.timezone("America/Sao_Paulo")                      

celery_app = Celery(
    "traqueamento_payloads",
    broker=BROKER_URL,
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

@celery_app.task(name="save_webhook_event", autoretry_for=(Exception,), retry_backoff=True)
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

    # Log bonito na sua tabela fancy
    debug_vars(dados=data, title_table="📦  Novo webhook recebido")

    try:
        # ---------- 2) Rotas de persistência ----------
        if is_status_failed(data):
            # Deepcopy DE NOVO pra não ganhar _id no dicionário usado adiante
            webhooks.send_webhook(deepcopy(data))  # avisa seu sistema
            collection.insert_one(deepcopy(data))
            print(
                f"✅ [failed] salvo (expira ~7 dias): "
                f"{data['createdAt']:%d/%m %H:%M}"
            )
            webhooks.send_webhook(data)  # avisa seu sistema
            _update_last_ts()


        elif is_automatic_events(data):
            url_webhook = os.getenv("N8N_AUTOMATICS_EVENTS")
            webhooks.send_webhook(deepcopy(data),end_webhook=url_webhook)
            print(
                f"✅ [automatic events] enviado para webhook: "
                f"{data['createdAt']:%d/%m %H:%M}"
            )
            _update_last_ts()

        elif is_non_messages_event(data):
            collectionEvents.insert_one(deepcopy(data))
            print(
                f"✅ [non-messages] salvo (expira ~36 h): "
                f"{data['createdAt']:%d/%m %H:%M}"
            )
            _update_last_ts()
        # ---------- 3) Caso não seja nenhuma das duas categorias ----------
        else:
            collectionVariadic.insert_one(deepcopy(data))
            print(
                f"ℹ️  Evento diferente das tratativas salvas na coleção variadic (expira ~36 h): "
                f"{data['createdAt']:%d/%m %H:%M}"
            )
            _update_last_ts()
            
        

    except Exception as exc:
        # Retenta sem deixar o ObjectId poluir o payload original
        print(f"⚠️  Erro: {exc!r} — entrando em retry")
        raise exc
        


def _update_last_ts():
    global _last_msg_ts
    _last_msg_ts = time.time()

    