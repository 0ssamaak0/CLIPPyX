from flask import Flask, abort, request, jsonify, send_from_directory
from flask_cors import CORS
from Index.create_db import (
    create_vectordb,
    get_clip_image,
    get_clip_text,
    get_text_embeddings,
)

import os
import requests
from io import BytesIO

image_collection, text_collection = create_vectordb("db")


def parse_image(image_path, top_k=5, threshold=0):
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


def search_clip_text(text, image_collection, top_k=5, threshold=0):
    """
    Search for images that are semantically similar to the input text.

    Args:
        text (str): The input text to search for.
        image_collection: The collection of images to search in.

    Returns:
        tuple: A tuple containing the paths of the top 5 images and their distances from the input text.
    """
    text_embedding = get_clip_text(text)
    results = image_collection.query(text_embedding, n_results=top_k)
    similarities = [1 - d for d in results["distances"][0]]
    paths, similarities = [
        p for p, d in zip(results["ids"][0], similarities) if d > threshold
    ], [d for d in similarities if d > threshold]
    return paths, similarities


def search_clip_image(
    image_path, image_collection, top_k=5, threshold=0, get_self=False
):
    """
    Search for images that are visually similar to the input image within a given image collection.

    Args:
        image_path (str): The path to the input image to search for. This path is stripped of any leading or trailing quotes and adjusted for posix systems.
        image_collection (FaissCollection): The collection of images to search in. This is an object that supports querying for nearest neighbors.
        get_self (bool, optional): If set to True, the function will return the input image as one of the results.
    Returns:
        tuple: A tuple containing two lists. The first list contains the paths of the top 5 images (or top 6 if get_self is True). The second list contains the corresponding distances of these images from the input image.
    """
    image_embedding = get_clip_image([image_path])
    results = image_collection.query(image_embedding, n_results=top_k)
    similarities = [1 - d for d in results["distances"][0]]
    paths, similarities = [
        p for p, d in zip(results["ids"][0], similarities) if d > threshold
    ], [d for d in similarities if d > threshold]
    if not get_self:
        for i in range(len(paths)):
            if paths[i] == image_path:
                paths.pop(i)
                similarities.pop(i)
                break
    return paths, similarities


def search_embed_text(text, text_collection, top_k=5, threshold=0):
    """
    Search for texts that are semantically similar to the input text.

    Args:
        text (str): The input text to search for.
        text_collection: The collection of texts to search in.

    Returns:
        tuple: A tuple containing the paths of the top 5 texts and their distances from the input text.
    """
    text_embedding = get_text_embeddings(text)
    results = text_collection.query(text_embedding, n_results=top_k)
    similarities = [1 - d for d in results["distances"][0]]
    paths, similarities = [
        p for p, d in zip(results["ids"][0], similarities) if d > threshold
    ], [d for d in similarities if d > threshold]
    return paths, similarities


# Flask App
app = Flask(__name__, static_folder="UI/CLIPPyX WebUI")
CORS(app)


@app.route("/clip_text", methods=["POST"])
def clip_text_route():
    """
    Handle a POST request to search images via text queries (using CLIP).

    Retrieves the following JSON fields from the request:
        - query (str): The text query to search for.
        - threshold (float): The minimum similarity threshold. Defaults to 0.
        - top_k (int): The number of top results to return. Defaults to 5.

    Calls `search_clip_text` with these parameters to retrieve a list of image
    paths (and their associated distances). Returns the list of image paths as JSON.

    Returns:
        flask.Response: A JSON response containing a list of image paths.
    """
    query = request.json.get("query", "")
    threshold = float(request.json.get("threshold", 0))
    top_k = int(request.json.get("top_k", 5))
    print(f"threshold: {threshold} top_k: {top_k}")
    paths, distances = search_clip_text(query, image_collection, top_k, threshold)
    print(len(paths))
    return jsonify(paths)


@app.route("/clip_image", methods=["POST"])
def clip_image_route():
    """
    Handle a POST request to search images via an image query (using CLIP).

    Retrieves the following JSON fields from the request:
        - query (str): Base64-encoded or URL reference to the image.
        - threshold (float): The minimum similarity threshold. Defaults to 0.
        - top_k (int): The number of top results to return. Defaults to 5.

    Calls `parse_image` to transform the input into a usable format, then uses
    `search_clip_image` to find matching images in the collection. Returns the
    list of matching image paths as JSON.

    Returns:
        flask.Response: A JSON response containing a list of image paths.
    """
    query = request.json.get("query", "")
    threshold = float(request.json.get("threshold", 0))
    top_k = int(request.json.get("top_k", 5))
    query = parse_image(query)
    paths, distances = search_clip_image(query, image_collection, top_k, threshold)
    return jsonify(paths)


@app.route("/ebmed_text", methods=["POST"])
def ebmed_text_route():
    """
    Handle a POST request to search text embeddings.

    Retrieves the following JSON fields from the request:
        - query (str): The text to be embedded and searched.
        - threshold (float): The minimum similarity threshold. Defaults to 0.
        - top_k (int): The number of top results to return. Defaults to 5.

    Calls `search_embed_text` to find matching text entries in the collection.
    Returns the list of matching document paths (or identifiers) as JSON.

    Returns:
        flask.Response: A JSON response containing a list of text document paths.
    """
    query = request.json.get("query", "")
    threshold = float(request.json.get("threshold", 0))
    top_k = int(request.json.get("top_k", 5))
    paths, distances = search_embed_text(query, text_collection, top_k, threshold)
    return jsonify(paths)


@app.route("/")
def serve_index():
    """
    Serve the main index page (index.html) from the static folder.

    Returns:
        flask.Response: The index.html file from the `app.static_folder`.
    """
    return send_from_directory(app.static_folder, "index.html")


@app.route("/images/<path:filename>")
def serve_image(filename):
    """
    Serve an image file from within the images directory.

    Args:
        filename (str): The path to the image file within the images directory.

    Returns:
        flask.Response: The requested image file from its directory.
    """
    filename = os.path.join("/", filename)
    return send_from_directory(os.path.dirname(filename), os.path.basename(filename))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 23107))
    app.run(host="0.0.0.0", port=port)
