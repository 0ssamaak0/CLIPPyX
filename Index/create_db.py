import chromadb
from tqdm import tqdm
import os
import sys
import yaml
from Index.scan import read_from_csv

# Load the configuration file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

deep_scan = config["deep_scan"]

if config["clip"]["provider"] == "transformers":
    from CLIP.hftransformers_clip import get_clip_image, get_clip_text
elif config["clip"]["provider"] == "mobileclip":
    from CLIP.mobile_clip import get_clip_image, get_clip_text

if config["text_embed"]["provider"] == "transformers":
    from text_embeddings.hftransformers_embeddings import get_text_embeddings
elif config["text_embed"]["provider"] == "ollama":
    from text_embeddings.ollama_embeddings import get_text_embeddings
if config["text_embed"]["provider"] == "llama_cpp":
    from text_embeddings.llamacpp_embeddings import get_text_embeddings
from OCR import apply_OCR


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


def index_images(image_collection, text_collection):
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
    paths, averages = read_from_csv("paths.csv")
    for i, image in tqdm(enumerate(paths), total=len(paths), desc="Creating VectorDB"):
        if len(image_collection.get(ids=paths[i])["ids"]) > 0:
            if deep_scan:
                # Check if the average pixel value has changed
                average = image_collection.get(ids=paths[i])["metadatas"][0]["average"]
                if average == averages[i]:
                    continue
            continue
        image_embeddings = get_clip_image(paths[i])
        image_collection.upsert(
            ids=[paths[i]],
            embeddings=image_embeddings,
            metadatas={"average": averages[i]},
        )
        ocr_text = apply_OCR(paths[i])
        if ocr_text is not None:
            text_embeddings = get_text_embeddings(ocr_text)
            text_collection.upsert(ids=[paths[i]], embeddings=text_embeddings)


def clean_index(image_collection, text_collection):
    """
    Clean up the database.

    This function iterates over all IDs in the image collection, and for each ID, it checks if the ID is in
    the list of original image paths. If not, it deletes the ID from the image collection and the text collection.

    Args:
        paths (list): The list of original image paths. These paths are used as IDs in the
                               image and text collections.
        image_collection (Collection): The image collection in the database.
        text_collection (Collection): The text collection in the database.
    """
    paths, averages = read_from_csv("paths.csv")
    for i, id in tqdm(
        enumerate(image_collection.get()["ids"]),
        total=len(image_collection.get()["ids"]),
        desc="Cleaning up database",
    ):
        if id not in paths:
            print(f"deleting: {id} from image_collection")
            image_collection.delete(ids=[id])
            try:
                print(f"deleting: {id} from text_collection")
                text_collection.delete(ids=[id])
            except:
                pass
