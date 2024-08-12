from flask import Flask, abort, request, jsonify, send_from_directory
from flask_cors import CORS
from Index.create_db import create_vectordb, get_clip_image, get_clip_text

import os
import requests
from io import BytesIO

image_collection, text_collection = create_vectordb("db")


def parse_image(image_path):
    """
    Parses an image from a given path or URL.

    If the image_path is a URL (starts with 'http://' or 'https://'), the function fetches the image
    from the web and returns a BytesIO object containing the image data. If the image_path is a local
    file path, it simply returns the path as is.

    Parameters:
    - image_path (str): The path or URL to the image.

    Returns:
    - BytesIO or str: A BytesIO object containing the image data if the image_path is a URL,
                      or the image_path itself if it's a local file path.
    """
    if image_path.startswith("http://") or image_path.startswith("https://"):
        response = requests.get(image_path)
        return BytesIO(response.content)
    else:
        image_path = image_path.strip('"').strip("'")
        return image_path


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
    # TODO handle wsl later
    # if os.name == "posix":
    #     image_path = image_path.replace("\\", "/").replace("C:", "/mnt/c")
    image_embedding = get_clip_image([image_path])
    results = image_collection.query(image_embedding, n_results=5)
    distances = results["distances"][0]
    paths = results["ids"][0]
    for i in range(len(paths)):
        if paths[i] == image_path:
            paths.pop(i)
            distances.pop(i)
            break
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
    query = parse_image(query)
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
