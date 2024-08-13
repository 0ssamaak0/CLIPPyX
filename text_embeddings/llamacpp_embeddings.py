import requests
from tqdm import tqdm
from llama_cpp import Llama
import os
import yaml

# Load the configuration file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
embedding_gguf = config["text_embed"]["embedding_gguf"]
llm = Llama(
    model_path=f"{embedding_gguf}",
    n_gpu_layers=-1,  # Uncomment to use GPU acceleration
    embedding=True,
    verbose=False,
)


def get_text_embeddings(text):
    """
    Gets the text embeddings for the given text.

    Args:
        text (str): The text to get embeddings for.

    Returns:
        list: The text embeddings as a list.
    """
    return llm.create_embedding(text)["data"][0]["embedding"]
