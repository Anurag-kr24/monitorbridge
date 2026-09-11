import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///monitorbridge.db"
    )
    ALERT_THRESHOLD = float(
        os.getenv("ALERT_THRESHOLD", "0.75")
    )
