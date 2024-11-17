<div align = "center" >
<img src="assets/logo_text.png" height="150">


CLIPPyX is an AI Assisted search tool that allows search in image content and text on your desk or external drives.

----------------------------------------

</div>

![CLIPPyX Demo](assets/fastgif.gif)

🎬 [Video at 1x speed](https://x.com/0ssamaak0/status/1797373251049713827)

# Main Features
- 🟡 **Search by Image Caption**: Search by any text or phrase that matches the image description.

- 🔵 **Search by Textual Content in Images**: Search by the semantic meaning of the text in your images.

- 🟡 **Search by Image Similarity**: Provide an existing image as a reference as a path or a URL, CLIPPyX will find visually similar images using CLIP.

# Tool Overview

![CLIPPyX Overview](assets/CLIPPyX_diag.png)

- **CLIP**:
[OpenAI's CLIP](https://openai.com/index/clip/) is the main component of CLIPPyX. It's to store all image embeddings in a vector database to query later.

- **OCR & Text Embedding**:
OCR is applied to all images to extract text from them, then these texts are embedded using a text embedding model and stored in a vector database to perform text-based search.

- **CLIPPyX Server**:
CLIPPyX server receives the search query from the [UI](#User-Interface), and then it queries the collections of image embeddings and text embeddings to return the relevant images.

# Getting Started
## Installation
- Install [Pytorch](https://pytorch.org/)
- Clone the repository
- in the root directory, run the command

```
pip install -e .
```
## Settings
- CLIPPyX provides a UI to select the settings (can be configured from `config.yaml` too) to access the settings UI run:
```
CLIPPyX --settings
```
The settings you can set are:
- Deep Scan: Deepscan ensures if a file content has changed but the file name is the same, it will still be reindexed (It may affect performance for large directories)
- Batch Size: 
- Scan Method:
    - Default: You manually select paths to include/exclude in your search
    - Voidtools Everything (Windows Only): If you have [Everything](https://www.voidtools.com) installed, you can use its index
- CLIP Provider: 
    - Apple's [MobileClip](https://machinelearning.apple.com/research/mobileclip) 
    - any CLIP model from Huggingface 🤗 Transformers
- Text Embedding Provider: 
    - Any text embedding model from Huggingface 🤗 Transformers
    - Ollama
    - llama.cpp
    - Any OpenAI Compatible API (e.g., Fireworks.ai)

## Running CLIPPyX
- To start CLIPPyX server, run 
```
CLIPPyX
```

Some models may download automatically the first time you run CLIPPyX, then you should see the indexing process starting. When the indexing process you can search through any UI

```
 * Serving Flask app 'server'
 * Debug mode: off
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:23107
 * Running on http://172.25.97.13:23107
 ```

You can check the server is running by sending a simple request to the server using CURL or Postman.

```
curl -X POST -H "Content-Type: application/json" -d "{\"text\": \"Enter your query here\"}" http://localhost:23107/clip_text
```

# User Interface
Having CLIPPyX server running, you can use any UI capable of sending HTTP requests to the server, you can customize any UI to do this, or use one of the provided UIs.

Currently CLIPPyX Supports:
- Simple WebUI
- Raycast (MacOS)
- Flow Launcher (Windows)
- PowerToys Run (Windows)

Check [UI page](https://github.com/0ssamaak0/CLIPPyX/tree/main/UI) for more information

# Common Issues
Check the [Common Issues](https://github.com/0ssamaak0/CLIPPyX/blob/main/docs/Common%20Issues.md) page for common issues and their solutions.



# Future Work
Check [Issues](https://github.com/0ssamaak0/CLIPPyX/issues) for future work and contributions. Don't hesitate to open a new issue for any feature request or bug report.