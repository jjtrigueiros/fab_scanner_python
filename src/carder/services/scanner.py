import os
from pathlib import Path

import cv2
import cv2.typing as cv2t
import numpy as np
import numpy.typing as npt
import requests

from loguru import logger


def preprocess_image(image: cv2t.MatLike) -> cv2t.MatLike:
    """Convert to grayscale and apply Gaussian blur."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred


def load_card_scans(scan_folder: Path) -> dict[str, cv2t.MatLike]:
    """Load all .webp card scans into a dictionary."""
    card_scans: dict[str, cv2t.MatLike] = {}
    for file in os.listdir(scan_folder):
        if file.endswith(".webp"):
            filepath = os.path.join(scan_folder, file)
            card_name = os.path.splitext(file)[0]
            image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
            card_scans[card_name] = image
    return card_scans


def detect_card(image) -> cv2t.MatLike | None:
    edged = cv2.Canny(image, 30, 150)
    # show

    contours, _ = cv2.findContours(
        edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        logger.error("No contours detected.")
        return None

    # Find the largest contour by area
    largest_contour = max(contours, key=cv2.contourArea)

    # Approximate the contour to a polygon
    peri = cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)

    if len(approx) != 4:
        logger.debug("Card contour not found (not a quadrilateral).")
        return None
    return approx


def warp_card(image: cv2t.MatLike, contours: cv2t.MatLike) -> cv2t.MatLike:
    """perform a perspective warp."""

    # Reorder points for perspective transform
    pts = contours.reshape(4, 2)
    rect = reorder_points(pts)

    # Perform perspective warp
    max_width = 300
    max_height = 400
    dst = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype="float32",
    )
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    # show

    return warped


def reorder_points(pts):
    """Reorder points for perspective transform."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Top-left
    rect[2] = pts[np.argmax(s)]  # Bottom-right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Top-right
    rect[3] = pts[np.argmax(diff)]  # Bottom-left
    return rect


def classify_card(input_photo_path, scan_folder):
    """Main function to classify a card in an input photo."""
    input_photo = cv2.imread(input_photo_path)

    if input_photo is None:
        raise ValueError("Could not load the input photo.")

    preprocessed_photo = preprocess_image(input_photo)
    contour = detect_card(preprocessed_photo)
    warped_card = warp_card(preprocessed_photo, contour)

    if warped_card is None:
        return "No card detected or unable to warp."

    card_scans = load_card_scans(scan_folder)
    best_match, confidence_scores = match_card(warped_card, card_scans)

    return best_match, confidence_scores


def match_card(input_card, card_scans):
    """Compare the input card with scans and return the best match."""
    orb = cv2.ORB_create()

    # Compute keypoints and descriptors for input card
    kp1, des1 = orb.detectAndCompute(input_card, None)
    # input_card_with_keypoints = cv2.drawKeypoints(input_card, kp1, None, color=(0, 255, 0))
    # cv2.imshow("Input Card Keypoints", input_card_with_keypoints)

    match_scores = {}

    for card_name, card_image in card_scans.items():
        # Compute keypoints and descriptors for scanned card
        kp2, des2 = orb.detectAndCompute(card_image, None)

        # Match descriptors using BFMatcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # Sort matches by distance (lower is better)
        matches = sorted(matches, key=lambda x: x.distance)
        score = sum([match.distance for match in matches]) / (len(matches) or 1)
        match_scores[card_name] = score

        # Visualize matches (optional)
        # match_visualization = cv2.drawMatches(input_card, kp1, card_image, kp2, matches[:10], None, flags=2)
        # cv2.imshow(f"Matches with {card_name}", match_visualization)

    if not match_scores:
        return None, []

    # Normalize scores to get confidence values
    min_score = min(match_scores.values())
    max_score = max(match_scores.values())
    normalized_scores = (
        {
            name: (1 - (score - min_score) / (max_score - min_score))
            for name, score in match_scores.items()
        }
        if max_score
        else {}
    )

    # Sort by confidence
    sorted_scores = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
    best_match = sorted_scores[0] if sorted_scores else None
    return best_match, sorted_scores


def read_video_feed(uri):
    while True:
        # Use urllib to get the image and convert into a cv2 usable format
        video_feed_response = requests.get(uri, stream=True)
        if video_feed_response.status_code == 200:
            stream_contents = bytes()
            for chunk in video_feed_response.iter_content():
                stream_contents += chunk
                a = stream_contents.find(b"\xff\xd8")
                b = stream_contents.find(b"\xff\xd9")
                if a != -1 and b != -1:
                    img = stream_contents[a : b + 2]
                    stream_contents = stream_contents[b + 2 :]
                    i = cv2.imdecode(
                        np.fromstring(img, dtype=np.uint8), cv2.IMREAD_COLOR
                    )
                    cv2.imshow("i", i)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        # put the image on screen
        cv2.imshow("IPWebcam", img)

        # To give the processor some less stress
        # time.sleep(0.1)


async def get_url_image_feed() -> npt.NDArray[np.uint8] | None:
    PHOTO_FEED_URI = "http://192.168.1.129:8080/shot.jpg"
    while True:
        feed_response = requests.get(url=PHOTO_FEED_URI)
        if feed_response.ok:
            yield cv2.imdecode(
                np.fromstring(feed_response.content, dtype=np.uint8), cv2.IMREAD_COLOR
            )


async def get_webcam_feed(device_id: int = 0):
    vc = cv2.VideoCapture(device_id)
    if not vc.isOpened():
        logger.error("Could not open webcam")
        return

    try:
        while True:
            rval, frame = vc.read()
            if not rval:
                logger.error("Could not read camera frame")
                break
            yield frame
    finally:
        vc.release()
