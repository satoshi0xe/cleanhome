from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "CleanHome"
    APP_ENV: str = "development"

    DATABASE_URL: str = "sqlite:///./cleanhome.db"

    JWT_SECRET: str = "cleanhome"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24


settings = Settings()