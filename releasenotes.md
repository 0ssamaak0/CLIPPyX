This release .....

# New Features 🌟
- Image search can work with any image locally or form URL
- Support for Apple Silicon GPU
- Parallel Image indexing and inference for CLIP and OCR
- Separation of indexing and searching scripts for memory optimization
- Voidtool Everything is no longer required, it's optional now
- text embeddings now support hugging face transformers, Llama.cpp, Ollama and any OpenAI Compatible API
- top k and threshold selection for all functionalities
- Settings UI
- Powertoys run Plugin for Windows
- Raycast Extension for Mac

# Bug Fixes 🐞
- If new image is saved with the same name as previous image e.g., `untitlied` will be reindexed if `deep_scan` is activated from config
- Fixing an issue when ollama isn't running


# pip install git+https://github.com/apple/ml-mobileclip.git@main#egg=mobileclip --no-deps
