import aiofiles
import aiosqlite
from pathlib import Path

from .fabtcg import FabTcgCard


CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metadata JSON NOT NULL,
    image TEXT UNIQUE NOT NULL,
    phash TEXT NOT NULL
);
"""

INSERT_CARD_QUERY = """
INSERT INTO cards (metadata, image, phash)
VALUES (?, ?, ?);
"""

FETCH_CARD_QUERY = """
SELECT metadata, image, phash
FROM cards
WHERE id = ?;
"""

FETCH_CARDS_NO_META_QUERY = """
SELECT id, metadata, phash
FROM cards
"""


class LocalStorageService:
    def __init__(self, sqlite_db: Path, img_dir: Path):
        self.db_path: Path = sqlite_db
        self.img_dir: Path = img_dir

    # Initialize the database
    async def initialize_db(self):
        self.db_path.touch()
        async with aiosqlite.connect(self.db_path) as db:
            _ = await db.execute(CREATE_TABLE_QUERY)
            await db.commit()

    async def initialize_cards_dir(self):
        self.img_dir.mkdir(exist_ok=True)

    async def save_card(
        self,
        card_metadata: FabTcgCard,
        card_img_name: str,
        card_img_bytes: bytes,
        card_hash: bytes,
    ):
        async with aiosqlite.connect(self.db_path) as db:
            _ = await db.execute(
                INSERT_CARD_QUERY,
                (card_metadata.model_dump_json(), card_img_name, card_hash),
            )
            await db.commit()
        save_location = self.img_dir / card_img_name
        async with aiofiles.open(save_location, mode="wb") as file:
            _ = await file.write(card_img_bytes)

    async def fetch_image(self, file_name: str):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(FETCH_CARD_QUERY, (file_name,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    metadata, image, phash = result
                    return {
                        "metadata": metadata,
                        "image": image,
                        "perceptual_hash": phash,
                    }
                return None

    async def fetch_images_and_hashes(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(FETCH_CARDS_NO_META_QUERY) as cursor:
                results = await cursor.fetchall()
                return [
                    {"card_id": card_id, "image": image, "phash": phash}
                    for (card_id, image, phash) in results
                ]
