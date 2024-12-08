import torch
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
import yaml

# Load the configuration file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
checkpoint = config["text_embed"]["HF_transformers_embeddings"]


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained(checkpoint, trust_remote_code=True)
model.eval()

device = (
    "mps"
    if torch.backends.mps.is_available()
    else ("cuda" if torch.cuda.is_available() else "cpu")
)
model = model.to(device)


def get_text_embeddings(text, norm=False):
    """
    Gets the text embeddings for the given text.

    Args:
        text (str): The text to get embeddings for.

    Returns:
        list: The text embeddings as a list.
    """
    encoded_input = tokenizer(
        [text], padding=True, truncation=True, return_tensors="pt"
    ).to(device)
    with torch.no_grad():
        model_output = model(**encoded_input)

    embeddings = mean_pooling(model_output, encoded_input["attention_mask"])
    if norm:
        embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings.cpu().squeeze(0).numpy().tolist()
