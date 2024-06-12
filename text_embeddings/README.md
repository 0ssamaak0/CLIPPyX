# Using Ollama
- Download [Ollama](https://ollama.com/download)
- Download nomic-embed-text `Q4_0` quantized model
```bash
ollama pull 0ssamaak0/nomic-embed-text
```
- in `config.yaml`, `text_embed:` set `provider` to `ollama`



## Notes: 
- If you have Ollama already installed, make sure you're on `v0.1.43` or later.
- [nomic-embed-text](https://ollama.com/library/nomic-embed-text) is already available on Ollama, but this model is `F16` quantized.

# Using llama.cpp

There's an option to run `CLIPPyX` using `GGUF` quantized models from [Llama cpp python](https://github.com/abetlen/llama-cpp-python) which is faster and consumes less memory

- Follow the intallation process in the repo, you may install `llama.cpp` itself first then install thep python binding
- make sure GPU is enabled if you have one
- in `config.yaml`, `text_embed:` set `provider` to `llama_cpp`
- change the quantization method if u want (default is `Q4_0`)