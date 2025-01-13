
from pydantic import BaseModel
import typing as t

CardImageSize = t.Literal["small", "normal", "large"]

class FabTcgCard(BaseModel):
    card_id: str
    card_type: str
    display_name: str
    name: str
    pitch: str
    cost: str
    defense: str
    life: str
    intellect: str
    power: str
    object_type: str
    text: str
    text_html: str
    typebox: str
    url: str
    image: dict[CardImageSize, str]
