# FILE: server/src/api/conf.py (NEW FILE)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        # This path tells the app (running from `src/`) to look
        # one directory up for the .env file.
        env_file = "../.env"

settings = Settings()