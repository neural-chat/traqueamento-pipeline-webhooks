from dotenv import load_dotenv
import os, logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost/")
QUEUE_NAME = os.getenv("QUEUE_NAME", "my_events")
TOPIC_KEY= os.getenv("TOPIC_KEY", "events.#")

MONGO_URL  = os.getenv("MONGO_URL",  "mongodb://localhost:27017")
DB_NAME    = os.getenv("DB_NAME",    "nextflow")
COLLECTION = os.getenv("COLLECTION", "events")






