from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
import yaml

# Load the configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
checkpoint = config['clip']['transformers_clip_checkpoint']

# load model and tokenizer
model = CLIPModel.from_pretrained(checkpoint)
processor = CLIPProcessor.from_pretrained(checkpoint)
# move model to cuda if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def get_clip_image(image_path: str):
    """
    Gets the image embeddings for the given image path.

    Args:
        image_path (str): The path to the image file.

    Returns:
        list: The image embeddings as a list.
    """
    image = Image.open(image_path.encode("utf-16").decode("utf-16"))
    with torch.no_grad():
        processed_image = processor(images=image, return_tensors="pt").to(device)
        image_features = model.get_image_features(**processed_image)
    return image_features.cpu().squeeze(0).numpy().tolist()

def get_clip_text(text):
    """
    Gets the text embeddings for the given text.

    Args:
        text (str): The text to get embeddings for.

    Returns:
        list: The text embeddings as a list.
    """
    with torch.no_grad():
        processed_text = processor(text=text, return_tensors="pt").to(device)
        text_features = model.get_text_features(**processed_text)
    return text_features.cpu().squeeze(0).numpy().tolist()