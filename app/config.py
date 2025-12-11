from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordBearer
import os


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"

    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    CORS_ORIGINS: list[str] = Field(..., env="CORS_ORIGINS")


settings = Settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
origins = settings.CORS_ORIGINS
