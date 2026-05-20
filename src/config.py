from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    API_KEY: str

    @property
    def DB_URL_async(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

settings = Settings()
