from PIL import Image
import imagehash
import io


class ImageHashingService:
    def __init__(self):
        pass

    def hash_image(self, img_bytes: bytes) -> str:
        return str(imagehash.phash(Image.open(io.BytesIO(img_bytes))))

    def compare_hashes(self, hash_1: str, hash_2: str) -> int:
        return imagehash.hex_to_hash(hash_1) - imagehash.hex_to_hash(hash_2)
