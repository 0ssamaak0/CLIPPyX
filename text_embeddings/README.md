# Using llama.cpp

There's an option to run CLIPPyX using `GGUF` quantized models from [Llama cpp python](https://github.com/abetlen/llama-cpp-python) which is faster and consumes less memory

- Follow the intallation process in the repo, you may install `llama.cpp` itself first then install thep python binding
- make sure GPU is enabled if you have one
- in `config.yaml`, `text_embed:` set `provider` to `llama_cpp`
- change the quantization method if u want (default is `Q4_0`)