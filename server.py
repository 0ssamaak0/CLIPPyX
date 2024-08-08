from flask import Flask, abort, request, jsonify, send_from_directory
from flask_cors import CORS
from Index.index_utils import *
from Index.scan_all import read_from_sqlite
import warnings
import os

warnings.filterwarnings("ignore")

image_collection, text_collection = create_vectordb("db")
# original_paths, os_paths = get_images_paths("images_paths.txt")
original_paths = read_from_sqlite("images.db")
os_paths = original_paths
print("number of paths: ", len(original_paths))
index_images(os_paths, original_paths, image_collection, text_collection)
clean_index(original_paths, image_collection, text_collection)


def search_clip_text(text, image_collection):
    """
    Search for images that are semantically similar to the input text.

    Args:
        text (str): The input text to search for.
        image_collection: The collection of images to search in.

    Returns:
        tuple: A tuple containing the paths of the top 5 images and their distances from the input text.
    """
    text_embedding = get_clip_text(text)
    results = image_collection.query(text_embedding, n_results=5)
    distances = results["distances"][0]
    paths = results["ids"][0]
    return paths, distances


def search_clip_image(image_path, image_collection, get_self=False):
    """
    Search for images that are visually similar to the input image within a given image collection.

    Args:
        image_path (str): The path to the input image to search for. This path is stripped of any leading or trailing quotes and adjusted for posix systems.
        image_collection (FaissCollection): The collection of images to search in. This is an object that supports querying for nearest neighbors.
        get_self (bool, optional): If set to True, the function will return the input image as one of the results.
    Returns:
        tuple: A tuple containing two lists. The first list contains the paths of the top 5 images (or top 6 if get_self is True). The second list contains the corresponding distances of these images from the input image.
    """
    image_path = image_path.strip('"').strip("'")
    # TODO handle wsl later
    # if os.name == "posix":
    #     image_path = image_path.replace("\\", "/").replace("C:", "/mnt/c")
    image_embedding = get_clip_image(image_path)
    if not get_self:
        results = image_collection.query(image_embedding, n_results=6)
        distances = results["distances"][0][1:]
        paths = results["ids"][0][1:]
    else:
        results = image_collection.query(image_embedding, n_results=5)
        distances = results["distances"][0]
        paths = results["ids"][0]
    return paths, distances


def search_embed_text(text, text_collection):
    """
    Search for texts that are semantically similar to the input text.

    Args:
        text (str): The input text to search for.
        text_collection: The collection of texts to search in.

    Returns:
        tuple: A tuple containing the paths of the top 5 texts and their distances from the input text.
    """
    text_embedding = get_text_embeddings(text)
    results = text_collection.query(text_embedding, n_results=5)
    distances = results["distances"][0]
    paths = results["ids"][0]
    return paths, distances


# Flask App
app = Flask(__name__, static_folder="UI/CLIPPyX WebUI")
CORS(app)


@app.route("/clip_text", methods=["POST"])
def clip_text_route():
    query = request.json.get("query", "")
    paths, distances = search_clip_text(query, image_collection)
    # for path, distance in zip(paths, distances):
    #     print(f"Path: {path}, Distance: {distance}")
    return jsonify(paths)


@app.route("/clip_image", methods=["POST"])
def clip_image_route():
    query = request.json.get("query", "")
    paths, distances = search_clip_image(query, image_collection)
    # for path, distance in zip(paths, distances):
    #     print(f"Path: {path}, Distance: {distance}")
    return jsonify(paths)


@app.route("/ebmed_text", methods=["POST"])
def ebmed_text_route():
    query = request.json.get("query", "")
    paths, distances = search_embed_text(query, text_collection)
    # for path, distance in zip(paths, distances):
    #     print(f"Path: {path}, Distance: {distance}")
    return jsonify(paths)


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/images/<path:filename>")
def serve_image(filename):
    filename = os.path.join("/", filename)
    # TODO handle WSL later
    # if os.name == "posix":
    #     filename = filename.replace("\\", "/").replace("C:", "/mnt/c")
    # # Not needed for now
    # LOCAL_IMAGE_DIR = os.getenv("LOCAL_IMAGE_DIR")
    # assert filename.startswith(LOCAL_IMAGE_DIR)
    return send_from_directory(os.path.dirname(filename), os.path.basename(filename))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 23107))
    app.run(host="0.0.0.0", port=port)
