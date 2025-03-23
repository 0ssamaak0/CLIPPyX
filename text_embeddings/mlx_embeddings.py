import mlx.core as mx
from mlx_embeddings.utils import load

# Load the model and tokenizer
model, tokenizer = load("sentence-transformers/all-MiniLM-L6-v2")


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element contains all token embeddings
    input_mask_expanded = mx.expand_dims(attention_mask, axis=-1)
    input_mask_expanded = mx.broadcast_to(input_mask_expanded, token_embeddings.shape)
    input_mask_expanded = input_mask_expanded.astype(mx.float32)
    sum_embeddings = mx.sum(token_embeddings * input_mask_expanded, axis=1)
    sum_mask = mx.sum(input_mask_expanded, axis=1)
    return sum_embeddings / mx.maximum(sum_mask, 1e-9)


def normalize_embeddings(embeddings):
    second_norm = mx.sqrt(mx.sum(mx.square(embeddings), axis=1, keepdims=True))
    return embeddings / mx.maximum(second_norm, 1e-9)


def get_text_embeddings(texts):
    inputs = tokenizer.batch_encode_plus(
        [texts], return_tensors="mlx", padding=True, truncation=True, max_length=512
    )
    outputs = model(inputs["input_ids"], attention_mask=inputs["attention_mask"])
    outputs = mean_pooling(outputs, inputs["attention_mask"])
    outputs = normalize_embeddings(outputs)
    return outputs.tolist()[0]
