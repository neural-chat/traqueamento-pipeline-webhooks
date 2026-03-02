from pymongo import MongoClient
from src.config import MONGO_URL, DB_NAME, COLLECTION

# Cliente síncrono
_client = MongoClient(MONGO_URL)
db = _client[DB_NAME]
collection = db[COLLECTION]
collectionEvents = db["events"]
collectionVariadic = db["variadic_events"]

def init_ttl_index():
    # Lista de coleções para aplicar TTL
    targets = [
        (COLLECTION, collection),
        ("events", collectionEvents),
    ]

    for name, coll in targets:
        try:
            index_name = coll.create_index(
                [("createdAt", 1)],
                expireAfterSeconds=168 * 60 * 60  # 7 dias
            )
            print(f"🗑️ Índice TTL 7 dias garantido na coleção '{name}' (index: '{index_name}')")
        except Exception as exc:
            print(f"❌ Falha ao criar índice TTL na coleção '{name}':", exc)
            # aqui você pode escolher se quer continuar ou re-levantar
