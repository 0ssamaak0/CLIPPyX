from PIL import Image
from CLIP.MLX import clip
import mlx.core as mx
from mlx.core import linalg as LA


# Getting text embeddings
# 1. Load the model, tokenizer, and image processor
model, tokenizer, img_processor = clip.load("CLIP/MLX/mlx_model")


def get_clip_image(image_paths):
    """
    Computes the image embeddings for a batch of images using MLX CLIP.

    This function opens each image from the specified paths, preprocesses them for the MLX CLIP model,
    and computes their embeddings using L2 normalization.

    Args:
        image_paths (list): List of image paths with length equal to batch_size

    Returns:
        list: A list containing the image embeddings for each image in the batch.
    """
    images = [Image.open(path) for path in image_paths]
    images = [img.convert("RGB") for img in images]
    pixel_values = img_processor(images)
    image_embeds_raw = model.get_image_features(pixel_values)
    image_embeds = image_embeds_raw / LA.norm(image_embeds_raw, axis=-1, keepdims=True)
    return image_embeds.tolist()


def get_clip_text(text):
    """
    Gets the text embeddings for the given text using MLX CLIP.

    Args:
        text (str): The text to get embeddings for.

    Returns:
        list: The text embeddings as a list.
    """
    text_inputs = tokenizer([text])
    text_embeds_raw = model.get_text_features(text_inputs)
    text_embeds = text_embeds_raw / LA.norm(text_embeds_raw, axis=-1, keepdims=True)
    return text_embeds.squeeze(0).tolist()
