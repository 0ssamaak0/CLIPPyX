import requests
import json


def get_text_embeddings(text):
    """
    Sends a POST request to a local API to get embeddings for the given text.

    Parameters:
    text (str): The text for which to get embeddings.

    Returns:
    list: The embeddings for the given text as a list of floats.
    """
    try:
        url = "http://localhost:11434/api/embeddings"
        data = {"model": "0ssamaak0/nomic-embed-text", "prompt": text}
        response = requests.post(url, data=json.dumps(data))
    except:
        raise Exception(
            "Failed to connect to Ollama. Please make sure Ollama is running."
        )
    return response.json()["embedding"]
