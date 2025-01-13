from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
from .base import Base


class CardImage(Base):
    __tablename__ = "card_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    raw_data: Mapped[dict] = mapped_column(JSON)
    name: Mapped[str] = mapped_column()
    pitch: Mapped[int | None] = mapped_column()
    print_id: Mapped[str] = mapped_column()
    image: Mapped[str] = mapped_column(unique=True)
    hash: Mapped[str] = mapped_column()
