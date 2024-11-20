import asyncio
import cv2
from loguru import logger
import heapq

from carder.cli.settings import settings
from carder.services.image_hashing import ImageHashingService
from carder.services.local_storage import LocalStorageService
from carder.services.scanner import (
    get_webcam_feed,
    preprocess_image,
    detect_card,
    warp_card,
)


def scan():
    asyncio.run(scan_async())


async def scan_async() -> None:
    hashing = ImageHashingService()
    local_storage = LocalStorageService(settings.sqlite_db, settings.images_dir)
    cards_iterable = await local_storage.fetch_images_and_hashes()
    image_feed = get_webcam_feed(0)

    cv2.namedWindow("preview")
    cv2.namedWindow("preprocess")
    cv2.namedWindow("detection")
    cv2.namedWindow("warp")

    async for frame in image_feed:
        cv2.imshow("preview", frame)
        frame_pp = preprocess_image(frame)
        cv2.imshow("preprocess", frame_pp)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        contour = detect_card(frame_pp)
        image_with_contour = cv2.cvtColor(frame_pp, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(image_with_contour, [contour], -1, (0, 255, 0), 2)
        if contour is None:
            continue
        cv2.imshow("detection", image_with_contour)

        frame_warped = warp_card(frame_pp, contour)
        if frame_warped is not None:
            cv2.imshow("warp", frame_warped)
        else:
            logger.error("unable to warp")
            continue

        input_hash = hashing.hash_image(cv2.imencode(".jpg", frame_warped)[1].tobytes())

        # best_match, confidence_scores = match_card(frame_warped, card_scans)with in_card.open("rb") as in_f:
        top_results = []
        for card in cards_iterable:
            score = hashing.compare_hashes(card.get("phash"), input_hash)
            entry = (100 - score, card.get("image"))
            if len(top_results) < 5:
                heapq.heappush(top_results, entry)
            else:
                heapq.heappushpop(top_results, entry)

        logger.debug("Best match: {}", sorted(top_results)[-1])

    cv2.destroyAllWindows()
