import chromadb
from tqdm import tqdm
import os
import sys

from CLIP.mobile_clip import get_clip_image, get_clip_text
from text_embeddings.llamacpp_embeddings import get_text_embeddings
from OCR import apply_OCR


import warnings

warnings.filterwarnings("ignore")


def create_vectordb(path):
    """
    Create and return image and text collections in a VectorDB database.

    This function initializes a PersistentClient with the given path, and then
    gets or creates two collections: 'images' and 'texts'. Both collections
    use cosine similarity for nearest neighbor search.

    Args:
        path (str): The path to the VectorDB database.

    Returns:
        tuple: A tuple containing two Collection objects. The first element
        is the 'images' collection, and the second element is the 'texts'
        collection.
    """
    client = chromadb.PersistentClient(
        path,
    )
    image_collection = client.get_or_create_collection(
        "images", metadata={"hnsw:space": "cosine"}
    )
    text_collection = client.get_or_create_collection(
        "texts", metadata={"hnsw:space": "cosine"}
    )
    return image_collection, text_collection


def get_images_paths(file_path):
    """
    Extract image paths from a file and return them in original and OS-specific formats.

    This function reads a file line by line, with each line expected to contain a path to an image.
    It returns two lists of paths: one with the original paths as they are in the file, and one with
    the paths formatted for the current operating system.

    If the script is running on a POSIX system (like Linux or WSL), it will replace backslashes with
    forward slashes and 'C:' with '/mnt/c' in the paths.

    Args:
        file_path (str): The path to the file containing the image paths.

    Returns:
        tuple: A tuple containing two lists of strings. The first list contains the original paths,
        and the second list contains the OS-specific paths.
    """
    original_paths = []
    with open(file_path, "r") as f:
        for line in f:
            original_paths.append(line.strip())

    if os.name == "posix":  # If running on WSL
        os_paths = [
            path.replace("\\", "/").replace("C:", "/mnt/c") for path in original_paths
        ]
    else:
        os_paths = original_paths
    return original_paths, os_paths


def index_images(os_paths, original_paths, image_collection, text_collection):
    """
    Index images in the database.

    This function iterates over all image paths in the OS-specific format (os_paths), and for each path,
    it checks if the image is already in the image collection using the original path. If not, it gets
    the image embeddings and upserts them into the image collection. It also applies OCR to the image
    and upserts the text embeddings into the text collection.

    Args:
        os_paths (list): The list of image paths in OS-specific format. These paths are used to read
                         the images and apply OCR.
        original_paths (list): The list of original image paths. These paths are used as IDs in the
                               image and text collections.
        image_collection (Collection): The image collection in the database.
        text_collection (Collection): The text collection in the database.
    """
    for i, image in tqdm(
        enumerate(os_paths), total=len(os_paths), desc="Creating VectorDB"
    ):
        if len(image_collection.get(ids=original_paths[i])["ids"]) > 0:
            continue
        image_embeddings = get_clip_image(os_paths[i])
        image_collection.upsert(ids=[original_paths[i]], embeddings=image_embeddings)
        ocr_text = apply_OCR(os_paths[i])
        if ocr_text is not None:
            text_embeddings = get_text_embeddings(ocr_text)
            text_collection.upsert(ids=[original_paths[i]], embeddings=text_embeddings)


def clean_index(original_paths, image_collection, text_collection):
    """
    Clean up the database.

    This function iterates over all IDs in the image collection, and for each ID, it checks if the ID is in
    the list of original image paths. If not, it deletes the ID from the image collection and the text collection.

    Args:
        original_paths (list): The list of original image paths. These paths are used as IDs in the
                               image and text collections.
        image_collection (Collection): The image collection in the database.
        text_collection (Collection): The text collection in the database.
    """
    for i, id in tqdm(
        enumerate(image_collection.get()["ids"]),
        total=len(image_collection.get()["ids"]),
        desc="Cleaning up database",
    ):
        if id not in original_paths:
            print(f"deleting: {id} from image_collection")
            image_collection.delete(ids=[id])
            try:
                print(f"deleting: {id} from text_collection")
                text_collection.delete(ids=[id])
            except:
                pass
