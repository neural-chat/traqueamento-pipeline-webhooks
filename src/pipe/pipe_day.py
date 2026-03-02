import os, logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from src.db import mongo

raw = mongo.collection
daily = mongo.db["raw_daily"]

TZ_SP = pytz.timezone("America/Sao_Paulo")
logger = logging.getLogger("metrics")



hoje      = datetime.now(TZ_SP).date()
inicio_dia = datetime.combine(hoje - timedelta(days=1), datetime.min.time(), TZ_SP)
fim_dia    = datetime.combine(hoje,              datetime.min.time(), TZ_SP)




async def aggregate_daily(reference: datetime | None = None) -> None:
    """
    Agrega as mensagens das últimas 24 h por display_phone_number
    e grava/atualiza em <RAW_COLLECTION>_daily.
    """
    now   = reference or datetime.now(TZ_SP)
    today = now.date()

    start = datetime.combine(today - timedelta(days=1), datetime.min.time(), TZ_SP)
    end   = datetime.combine(today,              datetime.min.time(), TZ_SP)

    logger.info(f"📊 Agregando métricas de {start:%d/%m/%Y}")

    pipeline = [
        {"$match": {"createdAt": {"$gte": start, "$lt": end}}},
        {"$unwind": "$entry"},
        {"$unwind": "$entry.changes"},
        {"$project": {
            "display_phone_number": "$entry.changes.value.metadata.display_phone_number",
            "msg_type": {
                "$arrayElemAt": ["$entry.changes.value.messages.type", 0]
            },
        }},
        {"$group": {
            "_id": "$display_phone_number",
            "total": {"$sum": 1},
            "types": {"$push": "$msg_type"},
        }},
    ]

    metrics = await raw.aggregate(pipeline).to_list(None)

    doc = {
        "day": start.date().isoformat(),   # ex.: "2025-06-26"
        "generatedAt": now,
        "metrics": metrics,
    }

    # upsert idempotente: se já existe, substitui
    await daily.update_one(
        {"day": doc["day"]},
        {"$set": doc},
        upsert=True,
    )

    logger.info(f"✅ {len(metrics)} números resumidos em (dia {doc['day']})")