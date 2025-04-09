import chromadb
from tqdm import tqdm
import os
import sys
import yaml
from Index.scan import read_from_csv
import warnings

warnings.filterwarnings("ignore")

# Load the configuration file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

deep_scan = config["deep_scan"]
batch_size = config["batch_size"]

if config["clip"]["provider"] == "HF_transformers":
    from CLIP.hftransformers_clip import get_clip_image, get_clip_text
elif config["clip"]["provider"] == "mobileclip":
    from CLIP.mobile_clip import get_clip_image, get_clip_text
elif config["clip"]["provider"] == "MLX":
    from CLIP.mlx_clip import get_clip_image, get_clip_text

if config["text_embed"]["provider"] == "HF_transformers":
    from text_embeddings.hftransformers_embeddings import get_text_embeddings
elif config["text_embed"]["provider"] == "ollama":
    from text_embeddings.ollama_embeddings import get_text_embeddings
elif config["text_embed"]["provider"] == "llama_cpp":
    from text_embeddings.llamacpp_embeddings import get_text_embeddings
elif config["text_embed"]["provider"] == "openai_api":
    from text_embeddings.openai_api import get_text_embeddings
elif config["text_embed"]["provider"] == "MLX":
    from text_embeddings.mlx_embeddings import get_text_embeddings

from ocr_model.OCR import apply_OCR


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
    with tqdm(total=len(paths), desc="Indexing images") as pbar:
        for i in range(0, len(paths), batch_size):
            batch_paths = paths[i : i + batch_size]
            to_process = []

            for path in batch_paths:
                if len(image_collection.get(ids=[path])["ids"]) > 0:
                    if deep_scan:
                        # Check if the average pixel value has changed
                        average = image_collection.get(ids=[path])["metadatas"][0][
                            "average"
                        ]
                        if average != averages[paths.index(path)]:
                            to_process.append(path)
                else:
                    to_process.append(path)

            if to_process:
                # Process CLIP embeddings in batch
                image_embeddings = get_clip_image(to_process)

                # Prepare data for batch upsert
                upsert_ids = to_process
                upsert_embeddings = image_embeddings
                upsert_metadatas = [
                    {"average": averages[paths.index(path)]} for path in to_process
                ]

                # Perform batch upsert for image collection
                image_collection.upsert(
                    ids=upsert_ids,
                    embeddings=upsert_embeddings,
                    metadatas=upsert_metadatas,
                )
                ocr_texts = apply_OCR(to_process)

                # Process OCR and text embeddings individually
                for i in range(len(to_process)):
                    if ocr_texts[i] is not None:
                        text_embeddings = get_text_embeddings(ocr_texts[i])
                        text_collection.upsert(
                            ids=[to_process[i]], embeddings=[text_embeddings]
                        )

            pbar.update(min(batch_size, len(paths) - i))


def clean_index(image_collection, text_collection, verbose=False):
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
            if verbose:
                print(f"deleting: {id} from image_collection")
            image_collection.delete(ids=[id])
            try:
                if verbose:
                    print(f"deleting: {id} from text_collection")
                text_collection.delete(ids=[id])
            except:
                pass
