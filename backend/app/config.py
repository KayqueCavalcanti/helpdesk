import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

SECRET_KEY: str = os.getenv("SECRET_KEY", "TROQUE_EM_PRODUCAO_USE_openssl_rand_hex_32")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./helpdesk.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
