from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(verbose=True)

class Settings(BaseSettings):
    
    # run
    HOST: str
    PORT: int
    WORKERS: int
    
    # security
    SECRET_KEY: str
    ALGORITHM: str
    ALLOWED_HOSTS: str
    DEBUG: bool = True
    ACCESS_TOKEN_EXPIRE_SECONDS: int
    REFRESH_TOKEN_EXPIRE_SECONDS: int

    # databases
    MONGODB_NAME: str
    MONGODB_URI: str
    REDIS_URI: str

    # email
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    #cdn
    CDN_USERNAME: str
    CDN_PASSWORD: str
    CDN_REPOSITORY: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()

settings = Settings() # type: ignore


AVATARS_DIRECTORY = Path("static/avatars")
AVATARS_DIRECTORY.mkdir(parents=True, exist_ok=True)
MEDIA_DIRECTORY = Path("static/media")
MEDIA_DIRECTORY.mkdir(parents=True, exist_ok=True)
DATAS_DIRECTORY = Path("static/datas")
DATAS_DIRECTORY.mkdir(parents=True, exist_ok=True)