import asyncio
import queue
from loguru import logger
from yarl import URL

from .fabtcg import FabTcgService
from .image_hashers import ImageHasher
from .local_storage import LocalCardStorage
from carder.models.fabtcg.print import FabTcgPrint


class CardImageDownloader:
    def __init__(self, fabtcg: FabTcgService, storage: LocalCardStorage, hasher: ImageHasher, max_concurrent_downloads: int = 50):
        self.fabtcg = fabtcg
        self.storage = storage
        self.hasher = hasher
        self.queue = queue.Queue(maxsize=100)
        self.max_concurrent_downloads = max_concurrent_downloads

    async def process_card(
        self,
        card: FabTcgPrint,
    ):
        img_name = URL(card.image.get("large", "")).name
        if self.storage.card_exists(card):
            logger.info("Card already exists: {}", card.card_id)
            return
        if self.storage.image_exists(img_name):
            logger.info("Image already exists: {}", img_name)
            return
        img_bytes = await self.fabtcg.get_image(card)
        img_hash = self.hasher.hash_image(img_bytes)
        self.storage.save(
            card_metadata=card,
            card_img_name=img_name,
            card_img_bytes=img_bytes,
            card_hash=img_hash,
        )
        logger.info("Saved card: {}", card.card_id)


    async def download_images(self):
        semaphore = asyncio.Semaphore(self.max_concurrent_downloads)
        tasks: set[asyncio.Task] = set()
        successes = 0
        failures = 0

        async def process_card_with_semaphore(card: FabTcgPrint):
            async with semaphore:
                return await self.process_card(card)

        async for card in self.fabtcg.get_cards_all():
            tasks_done = {task for task in tasks if task.done()}
            for task_done in tasks_done:
                try:
                    if await task_done:
                        successes += 1
                    else:
                        failures += 1
                except Exception as e:
                    logger.error("Task failed with error: {}", e)
                    failures += 1
                tasks.remove(task_done)

            new_task = asyncio.create_task(process_card_with_semaphore(card))
            tasks.add(new_task)

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successes += sum(1 for r in results if r is True)
            failures += sum(1 for r in results if r is not True)

        logger.info(f"Downloaded {successes} images with {failures} failures")
