import requests
from tqdm import tqdm
from llama_cpp import Llama
import os


def download_nomic_embed(checkpoint):
    """
    Downloads the MobileCLIP checkpoint file.

    Args:
        checkpoint (str): The name of the checkpoint file.
    """
    # you can modify this to any GGUF model
    url = f"https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/{checkpoint}.gguf"
    response = requests.get(url, stream=True)

    file_size = int(response.headers.get("Content-Length", 0))
    chunk_size = 1024  # 1 KB
    filename = url.split("/")[-1]

    progress = tqdm(
        response.iter_content(chunk_size),
        f"Downloading {filename}",
        total=file_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    )
    with open(f"checkpoints/{filename}", "wb") as f:
        for data in progress.iterable:
            f.write(data)
            progress.update(len(data))


# Select quantization method
quantization_method = "Q4_0"
checkpoint = f"nomic-embed-text-v1.5.{quantization_method}"
if not os.path.exists(f"checkpoints/{checkpoint}.gguf"):
    download_nomic_embed(checkpoint)

# load model
llm = Llama(
    model_path=f"checkpoints/{checkpoint}.gguf",
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
