from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlite_db: Path = Path("./state/cards.db")
    images_dir: Path = Path("./state/images/")
    fabtcg_base_url: str = "https://cards.fabtcg.com/"


settings = Settings()
