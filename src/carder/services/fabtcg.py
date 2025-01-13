import typing as t

import aiohttp
from loguru import logger
from pydantic import BaseModel

from carder.models.fabtcg.print import FabTcgPrint, CardImageSize

T = t.TypeVar("T")


class FabTcgListResponseModel[T](BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[T]


class FabTcgService:
    def __init__(self, base_url: str = "https://cards.fabtcg.com/") -> None:
        self.fabtcg_session = aiohttp.ClientSession(base_url)
        self.generic_session = aiohttp.ClientSession()

    async def get_cards_paginated(
        self, offset: int = 0, limit: int = 100
    ) -> FabTcgListResponseModel[FabTcgPrint]:
        logger.debug(f"Fetching api page (#{int(offset/limit) + 1})")
        response = await self.fabtcg_session.get(
                "/api/fab/v1/prints", params={"offset": offset, "limit": limit}
        )
        json = await response.json()
        return FabTcgListResponseModel[FabTcgPrint].model_validate(json)

    async def get_cards_all(self, limit: int = 500) -> t.AsyncGenerator[FabTcgPrint, None]:
        offset = 0
        while True:
            page = await self.get_cards_paginated(offset=offset, limit=limit)
            for result in page.results:
                yield result
            if not page.next:
                break
            offset += limit

    async def get_image(self, card: FabTcgPrint, size: CardImageSize = "large") -> bytes:
        response = await self.generic_session.get(card.image.get(size))
        return await response.content.read()