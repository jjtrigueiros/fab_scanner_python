import asyncio
from carder.cli.settings import settings
from carder.services import db
from carder.services.fabtcg import FabTcgService
from carder.services.card_image_downloader import CardImageDownloader
from carder.services.image_hashers import PHasher
from carder.services.local_storage import LocalCardStorage

def download():
    asyncio.run(_async_download())

async def _async_download():
    hasher = PHasher()
    storage = LocalCardStorage(db.Session(), settings.images_dir)
    fabtcg = FabTcgService(base_url=settings.fabtcg_base_url)
    db.init_db()

    await CardImageDownloader(fabtcg, storage, hasher).download_images()
