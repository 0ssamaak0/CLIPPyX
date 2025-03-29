import requests
import json
import yaml

# Load the configuration file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(stream=f)
model = config["text_embed"]["ollama_embeddings"]
url = config["text_embed"]["ollama_url"] #url = "http://localhost:11434/api/embeddings"

def get_text_embeddings(text):
    """
    Sends a POST request to a local API to get embeddings for the given text.

    Parameters:
    text (str): The text for which to get embeddings.

    Returns:
    list: The embeddings for the given text as a list of floats.
    """
    try:
        data = {"model": model, "prompt": text}
        response = requests.post(url, data=json.dumps(data))
    except:
        raise Exception(
            "Failed to connect to Ollama. Please make sure Ollama is running."
        )
    return response.json()["embedding"]
