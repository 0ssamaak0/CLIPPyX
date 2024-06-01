import requests
from tqdm import tqdm
import torch
from PIL import Image
import mobileclip
import os

def download_mobile_clip(checkpoint):
    """
    Downloads the MobileCLIP checkpoint file.

    Args:
        checkpoint (str): The name of the checkpoint file.
    """
    url = f"https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/{checkpoint}.pt"
    response = requests.get(url, stream=True)

    file_size = int(response.headers.get("Content-Length", 0))
    chunk_size = 1024  # 1 KB
    filename = url.split("/")[-1]

    progress = tqdm(response.iter_content(chunk_size), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(f"checkpoints/{filename}", "wb") as f:
        for data in progress.iterable:
            f.write(data)
            progress.update(len(data))

# define checkpoint TODO from config later
checkpoint = "mobileclip_s0"
if not os.path.exists(f"checkpoints/{checkpoint}.pt"):
    download_mobile_clip(checkpoint)

# load model and tokenizer
model, _, preprocess = mobileclip.create_model_and_transforms(checkpoint, pretrained=f"checkpoints/{checkpoint}.pt")
tokenizer = mobileclip.get_tokenizer(checkpoint)
# move model to cuda if available
device = ("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def get_clip_image(image_path):
    """
    Gets the image embeddings for the given image path.

    Args:
        image_path (str): The path to the image file.

    Returns:
        list: The image embeddings as a list.
    """
    image = Image.open(image_path)
    image =  preprocess(image.convert('RGB')).unsqueeze(0).to(device)
    with torch.no_grad(), torch.cuda.amp.autocast():
        image_features = model.encode_image(image)
    return image_features.cpu().squeeze(0).numpy().tolist()

def get_clip_text(text):
    """
    Gets the text embeddings for the given text.

    Args:
        text (str): The text to get embeddings for.

    Returns:
        list: The text embeddings as a list.
    """
    text = tokenizer([text]).to(device)
    with torch.no_grad(), torch.cuda.amp.autocast():
        text_features = model.encode_text(text)
    return text_features.cpu().squeeze(0).numpy().tolist()