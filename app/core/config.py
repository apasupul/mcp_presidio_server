import os
from pathlib import Path

class Settings:
    API_HOST: str = os.environ.get("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.environ.get("API_PORT", 8000))
    DATA_DIR: Path = Path(os.environ.get("DATA_DIR", "./data")).resolve()
    VAULT_DB_PATH: Path = Path(os.environ.get("VAULT_DB_PATH", str(DATA_DIR / "vault.db"))).resolve()
    PLACEHOLDER_SECRET: str = os.environ.get("PLACEHOLDER_SECRET", "")

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
