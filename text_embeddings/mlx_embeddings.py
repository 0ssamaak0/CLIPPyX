import mlx.core as mx
from mlx_embeddings.utils import load

# Load the model and tokenizer
model, tokenizer = load("sentence-transformers/all-MiniLM-L6-v2")


def get_text_embeddings(text):
    inputs = tokenizer.batch_encode_plus(
        [text], return_tensors="mlx", padding=True, truncation=True, max_length=512
    )
    outputs = model(inputs["input_ids"], attention_mask=inputs["attention_mask"])
    return outputs.text_embeds.tolist()[0]
