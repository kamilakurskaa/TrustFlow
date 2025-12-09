import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://trustflow_user:trustflow_pass@localhost:5432/trustflow")

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "super-mega-ultra-password")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа

    # Блокчейн


    # ML модель

    # Файлы
settings = Settings()