This release .....

# New Features 🌟
- Image search can work with any image locally or form URL
- Image paths are stored to SQLite database instead of text file for faster access
- parallel clip model and parsing
- parrlel ocr and reading
- separate file for memory efficiency
- text embeddings now support hugging face transformers, Llama.cpp, Ollama and any OpenAI Compatible API
- top k and threshold
- Settings UI

# Bug Fixes 🐞
- If new image is saved with the same name as previous image e.g., `untitlied` will be reindexed if `deep_scan` is activated from config
- Fixing an issue when ollama isn't running


# pip install git+https://github.com/apple/ml-mobileclip.git@main#egg=mobileclip --no-deps