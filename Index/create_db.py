import chromadb
from tqdm import tqdm
import os
import base64
import cohere
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
co = cohere.ClientV2(api_key=config["cohere_api_key"])


# Functions For Cohere Embed 3 (Instead of default pipeline)
def get_clip_image(image_path):
    processed_image = image_to_base64_data_url(image_path=image_path)
    embeddings = co.embed(
        model="embed-english-v3.0",
        images=[processed_image],
        input_type="image",
        embedding_types=["float"],
    ).embeddings.float_[0]
    return embeddings


def get_clip_text(text):
    embeddings = co.embed(
        model="embed-english-v3.0",
        texts=[text],
        input_type="search_query",
        embedding_types=["float"],
    ).embeddings.float_[0]
    return embeddings


import os
import base64
from PIL import Image
import io


def image_to_base64_data_url(image_path, max_size_bytes=5242880):
    # Check file extension for MIME type
    _, file_extension = os.path.splitext(image_path)
    file_type = file_extension[1:]

    # Open the image using PIL
    with Image.open(image_path) as img:
        # Reduce the image size if it exceeds the max size
        buffer = io.BytesIO()
        img.save(buffer, format=img.format)

        # Check if resizing is needed
        if buffer.tell() > max_size_bytes:
            # Resize the image until it's under the max size
            quality = 85  # Starting quality level
            while buffer.tell() > max_size_bytes and quality > 10:
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=quality)
                buffer.seek(0)
                quality -= 10  # Lower quality in increments

        # Encode the resized image to base64
        enc_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/{file_type};base64,{enc_img}"


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
    return image_collection, None


def index_images(image_collection):
    """
    Index images in the database.

    This function iterates over all image paths in the OS-specific format (os_paths), and for each path,
    it checks if the image is already in the image collection using the original path. If not, it gets
    the embeddings using Embed 3 Multimodal model

    Args:
        os_paths (list): The list of image paths in OS-specific format. These paths are used to read
                         the images.
        original_paths (list): The list of original image paths. These paths are used as IDs in the
                               image collection.
        image_collection (Collection): The image collection in the database.
    """
    paths, averages = read_from_csv("paths.csv")
    with tqdm(total=len(paths), desc="Indexing images using Cohere Embed 3") as pbar:
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
                image_embeddings = []
                for image_path in to_process:
                    image_embeddings.append(get_clip_image(image_path))
                    pbar.update(1)

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


def clean_index(image_collection, verbose=False):
    """
    Clean up the database.

    This function iterates over all IDs in the image collection, and for each ID, it checks if the ID is in
    the list of original image paths. If not, it deletes the ID from the image collection and the text collection.

    Args:
        paths (list): The list of original image paths. These paths are used as IDs in the
                               image and text collections.
        image_collection (Collection): The image collection in the database.
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
