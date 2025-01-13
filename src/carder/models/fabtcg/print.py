import typing as t
from pydantic import BaseModel

CardImageSize = t.Literal["small", "normal", "large"]


class FabTcgPrint(BaseModel):
    print_id: str
    card_id: str
    pitch: str
    name: str
    display_name: str
    object_type: str
    image: dict[CardImageSize, str]
    layout: dict[str, str]
    finish_types: list[dict[str, str]]