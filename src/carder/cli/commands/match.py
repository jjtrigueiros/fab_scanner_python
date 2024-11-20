import asyncio
import heapq
from pathlib import Path

from loguru import logger

from carder.cli.settings import settings
from carder.services.local_storage import LocalStorageService
from carder.services.image_hashing import ImageHashingService


def match_card(in_card: Path):
    storage = LocalStorageService(settings.sqlite_db, settings.images_dir)
    hashing = ImageHashingService()

    logger.info("loading image hashes...")
    cards_iterable = asyncio.run(storage.fetch_images_and_hashes())
    logger.info("loaded {} hashes", len(cards_iterable))
    logger.info("hashing input...")
    with in_card.open("rb") as in_f:
        input_hash = hashing.hash_image(in_f.read())

    logger.info("comparing...")
    top_results = []
    for card in cards_iterable:
        score = hashing.compare_hashes(card.get("phash"), input_hash)
        entry = (100 - score, card.get("image"))
        if len(top_results) < 5:
            heapq.heappush(top_results, entry)
        else:
            heapq.heappushpop(top_results, entry)

    logger.info("done!")
    print("Top results:")
    for result in sorted(top_results):
        print(f"{result[0]}%: {result[1]}")

    logger.info("Goodbye")
