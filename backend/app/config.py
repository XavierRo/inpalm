from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "NBalance"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql+asyncpg://nbalance:nbalance_dev@localhost:5432/nbalance"
    # URL synchrone pour Alembic
    DATABASE_URL_SYNC: str = "postgresql://nbalance:nbalance_dev@localhost:5432/nbalance"

    class Config:
        env_file = ".env"
        extra = "ignore"  # pour pydantic ?


settings = Settings()
