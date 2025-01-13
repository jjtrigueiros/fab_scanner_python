from pathlib import Path
from sqlalchemy.orm import Session

from carder.models.fabtcg.print import FabTcgPrint
from carder.models.db import CardImage
import sqlalchemy as sa


class LocalCardStorage:
    def __init__(self, db_session: Session, img_dir: Path):
        self.db_session: Session = db_session
        self.img_dir: Path = img_dir

        self.img_dir.mkdir(exist_ok=True)

    def save(
        self,
        card_metadata: FabTcgPrint,
        card_img_name: str,
        card_img_bytes: bytes,
        card_hash: bytes,
    ):
        card_image = CardImage(
            raw_data=card_metadata.model_dump_json(),
            name=card_metadata.name,
            pitch=card_metadata.pitch,
            print_id=card_metadata.print_id,
            image=card_img_name,
            hash=card_hash,
        )
        self.db_session.add(card_image)

        save_location = self.img_dir / card_img_name
        with save_location.open("wb") as f:
            f.write(card_img_bytes)

        self.db_session.commit()


    def fetch_images_and_hashes(self):
        q = sa.select(CardImage.id, CardImage.image, CardImage.hash)
        return self.db_session.execute(q).all()

    def card_exists(self, card_metadata: FabTcgPrint):
        q = (
            sa.select(CardImage.id)
            .where(CardImage.print_id == card_metadata.print_id)
            .limit(1)
        )
        return self.db_session.scalar(q) is not None

    def image_exists(self, image_name: str):
        q = sa.select(CardImage.id).where(CardImage.image == image_name).limit(1)
        return self.db_session.scalar(q) is not None
