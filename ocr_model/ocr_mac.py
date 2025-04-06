from ocrmac import ocrmac
from concurrent.futures import ThreadPoolExecutor

texts = []  # Clear previous texts to avoid duplicates


def process_image(image):
    annotations = ocrmac.OCR(image, recognition_level="fast").recognize()
    return " ".join([a[0] for a in annotations])


def apply_OCR(images):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_image, images))

    texts.extend(results)
    return texts
