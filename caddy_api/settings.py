import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

CONFIG_FILE_PATH = os.getenv("CADDY_CONFIG_FILE_PATH", BASE_DIR / "data/caddy/caddy.json")

CADDY_API_URL = os.getenv("CADDY_API_URL", "http://localhost:2019")

JWT_SECRET = os.getenv("JWT_SECRET")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

JWT_AUDIENCE = os.getenv("JWT_AUDIENCE")

HASURA_CRON_SECRET = os.getenv("HASURA_CRON_SECRET")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")