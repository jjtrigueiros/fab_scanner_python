from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlite_db: Path = Path("./state/cards.db")
    images_dir: Path = Path("./state/cards/")


settings = Settings()
