import typing as t

import aiohttp
from loguru import logger
from pydantic import BaseModel

T = t.TypeVar("T")


CardSize = t.Literal["small", "normal", "large"]


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
    image: dict[CardSize, str]


class FabTcgListResponseModel[T](BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[T]
    errors: dict[str, str]


class FabTcgService:
    def __init__(self, base_url: str = "https://cards.fabtcg.com/") -> None:
        self._fabtcg_session: aiohttp.ClientSession = aiohttp.ClientSession(
            base_url=base_url
        )
        self._downloader_session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def get_cards_paginated(
        self, offset: int = 0, limit: int = 100
    ) -> FabTcgListResponseModel[FabTcgCard]:
        logger.debug("Fetching api page")
        response = await self._fabtcg_session.get(
            "/api/search/v1/cards", params={"offset": offset, "limit": limit}
        )
        return FabTcgListResponseModel[FabTcgCard].model_validate(await response.json())

    async def get_cards_all(self, limit: int = 500):
        offset = 0
        while True:
            page = await self.get_cards_paginated(offset=offset, limit=limit)
            for result in page.results:
                yield result
            offset += limit

    async def get_image(self, card: FabTcgCard, size: CardSize = "large") -> bytes:
        response = await self._downloader_session.get(card.image.get(size))
        return await response.content.read()
