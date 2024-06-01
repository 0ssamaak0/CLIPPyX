# CLIP for Image and search query embedding
# ---------------------------------------------
CLIP_PROVIDER = "mobileclip"  # OR "transformers"

# if using "mobileclip"
# Check https://github.com/apple/ml-mobileclip/tree/main?tab=readme-ov-file#evaluation
MOBILECLIP_CHECKPOINT = "mobileclip_s0"

# if using "transformers"
# Check https://huggingface.co/models?other=clip,endpoints_compatible&sort=trending or any compatible model
TRANSFORMERS_CLIP_CHECKPOINT = "openai/clip-vit-base-patch16"

# Text embedding model for OCR and search query embedding
# ---------------------------------------------
TEXTEMB_PROVIDER = "llama_cpp"  # OR "transformers"

# if using "llama_cpp"
# Check https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/tree/main
QUANTIZATION_METHOD = "Q4_0"
