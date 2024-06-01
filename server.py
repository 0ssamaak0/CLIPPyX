from flask import Flask, request, jsonify
from Index.index_utils import *

image_collection, text_collection = create_vectordb("db")
original_paths, os_paths = get_images_paths("images_paths.txt")
index_images(os_paths, original_paths, image_collection, text_collection)
clean_index(original_paths, image_collection, text_collection)


def search_image(text, image_collection):
    """
    Search for images that are semantically similar to the input text.

    Args:
        text (str): The input text to search for.
        image_collection (FaissCollection): The collection of images to search in.

    Returns:
        tuple: A tuple containing the paths of the top 5 images and their distances from the input text.
    """
    text_embedding = get_clip_text(text)
    results = image_collection.query(text_embedding, n_results=5)
    distances = results["distances"][0]
    paths = results["ids"][0]
    return paths, distances


def search_text(text, text_collection):
    """
    Search for texts that are semantically similar to the input text.

    Args:
        text (str): The input text to search for.
        text_collection (FaissCollection): The collection of texts to search in.

    Returns:
        tuple: A tuple containing the paths of the top 5 texts and their distances from the input text.
    """
    text_embedding = get_text_embeddings(text)
    results = text_collection.query(text_embedding, n_results=5)
    distances = results["distances"][0]
    paths = results["ids"][0]
    return paths, distances


# Flask App
app = Flask(__name__)


@app.route("/search_image", methods=["POST"])
def image_route():
    text = request.json.get("text", "")
    paths, distances = search_image(text, image_collection)
    for path, distance in zip(paths, distances):
        print(f"Path: {path}, Distance: {distance}")
    return jsonify(paths)


@app.route("/search_text", methods=["POST"])
def text_route():
    text = request.json.get("text", "")
    paths, distances = search_text(text, text_collection)
    for path, distance in zip(paths, distances):
        print(f"Path: {path}, Distance: {distance}")
    return jsonify(paths)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
