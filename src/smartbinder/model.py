from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Card(Base):
    __tablename__: str = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))



"""Aether bindings of the third age"""
"""Figment of Erudition // Suraya, Archangel of Erudition"""
"""Convulsions from the Bellows of Hell // Convulsions from the Bellows of Hell"""