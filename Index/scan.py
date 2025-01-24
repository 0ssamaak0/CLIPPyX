# from Index.create_db import create_vectordb
import chromadb
from Index.scan_default import fast_scan_for_images
from concurrent.futures import ThreadPoolExecutor
import yaml
from tqdm import tqdm
from PIL import Image


def process_image(path):
    try:
        with Image.open(path) as img:
            try:
                first_channel = img.split()[0]
                pixel_data = list(first_channel.getdata())
            except AttributeError:
                pixel_data = list(img.getdata())
            total = sum(pixel_data)
            num_pixels = len(pixel_data)
            average = int(total / num_pixels)
        return (path, average)
    except Exception as e:
        print(f"Error processing {path}: {e}")
        return (path, 0)


def getDb(path="db"):
    client = chromadb.PersistentClient(
        path
    )
    paths = client.get_or_create_collection(
        "paths"
    )
    return paths


def save_to_db(image_paths, save_average=False, db="db"):
    paths_collection = getDb(db)
    ### Delete existing paths before inserting new ones.
    ids=paths_collection.get()["ids"]
    if len(ids)>0:
        paths_collection.delete(ids)

    image_paths = [path.replace("\\", "/") for path in image_paths]
    image_paths = list(set(image_paths))

    if save_average:
        with ThreadPoolExecutor() as executor:
            results = list(
                tqdm(
                    executor.map(process_image, image_paths), total=len(image_paths)
                )
            )
        upsert_metadatas = [
            {"average": result[1]} for result in results
        ]
    else:
        upsert_metadatas = [
            {"average": 0} for i in image_paths
        ]
        # Perform batch upsert for image collection
    upsert_embeddings = [[0] for i in image_paths]
    paths_collection.upsert(
        ids=image_paths,
        embeddings=upsert_embeddings,
        metadatas=upsert_metadatas,
    )


def read_from_db(db="db"):
    """
    Reads image paths and, optionally, their average pixel values from the db.

    Returns:
        tuple: Depending on read_average, returns a tuple containing one or two lists: one of the image paths and, if read_average is True, one of their average pixel values.
    """
    paths_collection = getDb(db)
    paths = paths_collection.get()["ids"]
    averages = [paths_collection.get(
        ids=[path])["metadatas"][0]["average"] for path in paths]

    return (paths, averages)


def scan_and_save():
    """
    Scans for images based on the configuration specified in 'config.yaml' and saves the paths.

    The function supports two scanning methods: 'default' and 'Everything'. The 'default' method uses specified
    include and exclude directories to find images, while the 'Everything' method utilizes the Everything SDK for scanning.

    Returns:
        bool: True if the scan and save operation was successful, False otherwise.
    """
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        if config["scan_method"] == "default":
            include_dirs = config["include_directories"]
            exclude_dirs = config["exclude_directories"]
            if len(include_dirs) == 0:
                include_dirs = None
                print("No directories to include")
                return False
            paths, _ = fast_scan_for_images(include_dirs, exclude_dirs)
        elif config["scan_method"] == "Everything":
            from Index.scan_EverythingSDK import search_EverythingSDK

            paths = search_EverythingSDK()
        else:
            print("Error in config.yaml: scan_method must be 'default' or 'Everything'")
            return False

        save_to_db(paths, config["deep_scan"])
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
