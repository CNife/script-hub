from pathlib import Path

from pydantic_settings import BaseSettings

_CWD: Path = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    DEBUG_MODE: bool = False
    REDIS_URL: str = "redis://localhost:6379"
    WORKER_LOG_PATH: Path = _CWD / ".debug_data" / "worker.log"
    WORKER_NAME_PATH: Path = _CWD / ".debug_data" / "worker.pid"


settings = Settings()
