import asyncio
from pathlib import Path

from loguru import logger
from yarl import URL

from .fabtcg import FabTcgCard, FabTcgService
from .image_hashing import ImageHashingService
from .local_storage import LocalStorageService

# TODO - adapt to CLI structure

SQLITE_DB = Path("./state/cards.db")
IMG_DL_DIR = Path("./state/cards/")
Path("./state/").mkdir(exist_ok=True)


async def process_card(
    fabtcg: FabTcgService,
    image_hasher: ImageHashingService,
    local_storage: LocalStorageService,
    card: FabTcgCard,
    counter: dict[str, int],
    counter_lock: asyncio.Lock,
):
    img_bytes = await fabtcg.get_image(card)
    img_hash = image_hasher.hash_image(img_bytes)
    img_name = URL(card.image.get("large", "")).name
    await local_storage.save_card(
        card_id=card.card_id,
        card_metadata=card,
        card_img_name=img_name,
        card_img_bytes=img_bytes,
        card_hash=img_hash,
    )
    async with counter_lock:
        counter["n_cards_saved"] += 1
        logger.info("Saved: {} ({} total)", img_name, counter["n_cards_saved"])


async def download():
    fabtcg = FabTcgService()
    image_hasher = ImageHashingService()
    local_storage = LocalStorageService(sqlite_db=SQLITE_DB, img_dir=IMG_DL_DIR)

    await local_storage.initialize_db()
    await local_storage.initialize_cards_dir()

    cards = fabtcg.get_cards_all()
    counter = {"n_cards_saved": 0}
    counter_lock = asyncio.Lock()
    tasks = []
    async for card in cards:
        tasks.append(
            asyncio.create_task(
                process_card(
                    fabtcg, image_hasher, local_storage, card, counter, counter_lock
                )
            )
        )
    _ = await asyncio.gather(*tasks)
