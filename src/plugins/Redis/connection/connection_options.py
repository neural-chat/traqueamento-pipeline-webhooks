import os
from dotenv import load_dotenv


load_dotenv()

connection_options = {
    "HOST": os.getenv("REDIS_HOST"),
    "PORT": int(os.getenv("REDIS_PORT", 6379)),
    "PASSWORD": os.getenv("REDIS_PASSWORD"),
    "DB": int(os.getenv("REDIS_DB", 0)),
    "USER": os.getenv("REDIS_USER", "default"),
}
