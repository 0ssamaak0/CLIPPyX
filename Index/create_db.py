import chromadb
from tqdm import tqdm
import os
import base64
import cohere
import time
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
co = cohere.ClientV2(api_key=config["text_embed"]["openai_api_key"])


def get_clip_image(image_paths):
    embeddings = []
    for image in image_paths:
        try:
            processed_image = image_to_base64_data_url(image)
            embeddings.append(
                co.embed(
                    model="embed-english-v3.0",
                    images=[processed_image],
                    input_type="image",
                    embedding_types=["float"],
                ).embeddings.float_[0]
            )
        except:
            print(image)
    return embeddings


def get_clip_text(text):
    embeddings = co.embed(
        model="embed-english-v3.0",
        texts=[text],
        input_type="search_query",
        embedding_types=["float"],
    ).embeddings.float_[0]
    return embeddings


# if config["clip"]["provider"] == "HF_transformers":
#     from CLIP.hftransformers_clip import get_clip_image, get_clip_text
# elif config["clip"]["provider"] == "mobileclip":
#     from CLIP.mobile_clip import get_clip_image, get_clip_text

# if config["text_embed"]["provider"] == "HF_transformers":
#     from text_embeddings.hftransformers_embeddings import get_text_embeddings
# elif config["text_embed"]["provider"] == "ollama":
#     from text_embeddings.ollama_embeddings import get_text_embeddings
# elif config["text_embed"]["provider"] == "llama_cpp":
#     from text_embeddings.llamacpp_embeddings import get_text_embeddings
# elif config["text_embed"]["provider"] == "openai_api":
#     from text_embeddings.openai_api import get_text_embeddings
# from ocr_model.OCR import apply_OCR


def image_to_base64_data_url(image_path):
    _, file_extension = os.path.splitext(image_path)
    file_type = file_extension[1:]

    with open(image_path, "rb") as f:
        enc_img = base64.b64encode(f.read()).decode("utf-8")
        enc_img = f"data:image/{file_type};base64,{enc_img}"
    return enc_img


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
