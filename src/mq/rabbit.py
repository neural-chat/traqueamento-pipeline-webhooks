import aio_pika
import asyncio, json, logging, time       # ← adiciona time
from src.config import RABBIT_URL, QUEUE_NAME
from src.db.mongo import collection,init_ttl_index
import pytz
from datetime import datetime
from src.config import RABBIT_URL, QUEUE_NAME, TOPIC_KEY
from src.utils.utils_logs import log_payload_table
TZ_SP = pytz.timezone("America/Sao_Paulo")

logger = logging.getLogger("worker")
_last_msg_ts = time.time()

async def handle_message(message: aio_pika.IncomingMessage):
    global _last_msg_ts

    async with message.process(requeue=False):
        try:
            data = json.loads(message.body)
            data["createdAt"] = datetime.now(TZ_SP)

            log_payload_table(data, title="📦  Novo webhook recebido")

            print(f"{data}")
            result = await collection.insert_one(data)
            _last_msg_ts = time.time()

            logger.info(
                f"✅ Doc {result.inserted_id} salvo "
                f"(expires ~36 h): {data['createdAt']:%d/%m %H:%M}"
            )

        except Exception:
            logger.exception("Falha no processamento")
            raise

# ✔️ tarefa heartbeat
async def _heartbeat():
    while True:
        await asyncio.sleep(60)                   # 60 s = 1 min
        if time.time() - _last_msg_ts >= 60:
            logger.info("⏰ 1 min sem mensagens… ainda na escuta!")

async def consume() -> None:

    # ── 1) Conexão RabbitMQ ───────────────────────────────────────
    logger.info("🔗 Conectando ao RabbitMQ…")
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel    = await connection.channel()
    await channel.set_qos(prefetch_count=16)
    logger.info("✅ Conectado ao RabbitMQ!")

    # ── 2) Exchange + Queue  ──────────────────────────────────────
    # Se você usa o default exchange, pule o bloco 'exchange'
    exchange = await channel.declare_exchange(
        name="amq.topic", 
        type=aio_pika.ExchangeType.TOPIC,
        durable=True
    )

    queue = await channel.declare_queue(
        name=QUEUE_NAME,
        durable=True
    )

    # Bind obrigatório se usa exchange/topic
    await queue.bind(exchange, routing_key=TOPIC_KEY)   # exemplo: "events.#"

    logger.info(f"🚀 Aguardando mensagens em {QUEUE_NAME} (rk={TOPIC_KEY})")

    # ── 3) Consumidor + heartbeat ─────────────────────────────────
    await queue.consume(handle_message)
    asyncio.create_task(_heartbeat())     # log a cada 5 min se ocioso

    # trava para sempre
    await asyncio.Future()