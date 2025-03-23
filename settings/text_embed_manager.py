import tkinter as tk
import ttkbootstrap as ttk
from settings.tooltip import CreateToolTip


class TextEmbedManager:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        text_embed_frame = ttk.Frame(self.parent)
        text_embed_frame.pack(fill=tk.X, pady=10)

        self.text_embed_provider_var = tk.StringVar(
            value=self.config["text_embed"]["provider"]
        )
        self.embedding_gguf_var = tk.StringVar(
            value=self.config["text_embed"]["embedding_gguf"]
        )
        self.ollama_embeddings_var = tk.StringVar(
            value=self.config["text_embed"]["ollama_embeddings"]
        )
        self.transformers_embeddings_var = tk.StringVar(
            value=self.config["text_embed"]["HF_transformers_embeddings"]
        )
        self.openai_api_base_url_var = tk.StringVar(
            value=self.config["text_embed"]["openai_endpoint"]
        )
        self.openai_api_key_var = tk.StringVar(
            value=self.config["text_embed"]["openai_api_key"]
        )
        self.openai_model_var = tk.StringVar(
            value=self.config["text_embed"]["openai_model"]
        )

        self.create_provider_selection(text_embed_frame)
        self.ollama_frame = self.create_ollama_options(text_embed_frame)
        self.gguf_frame = self.create_gguf_options(text_embed_frame)
        self.hf_frame = self.create_hf_options(text_embed_frame)
        self.openai_frame = self.create_openai_options(text_embed_frame)

        self.text_embed_provider_var.trace_add("write", self.update_text_embed_options)
        self.update_text_embed_options()

    def create_provider_selection(self, parent):
        provider_frame = ttk.Frame(parent)
        provider_frame.pack(fill=tk.X, pady=5)

        ttk.Label(provider_frame, text="Text Embedding Provider:").pack(
            side=tk.LEFT, padx=5, pady=5
        )
        self.text_embed_provider_entry = ttk.Combobox(
            provider_frame,
            textvariable=self.text_embed_provider_var,
            values=["HF_transformers", "ollama", "llama_cpp", "openai_api", "MLX"],
            width=15,
        )
        self.text_embed_provider_entry.pack(side=tk.LEFT, padx=5, pady=5)

    def create_ollama_options(self, parent):
        ollama_frame = ttk.Frame(parent)
        ollama_embeddings_label = ttk.Label(
            ollama_frame, text="Ollama Embedding Model:"
        )
        ollama_embeddings_label.pack(side=tk.LEFT, padx=5, pady=5)
        CreateToolTip(
            ollama_embeddings_label,
            text="You should have the model already downloaded\nExample: ollama pull <model_name>\nEnter <model_name> here",
        )
        self.ollama_embeddings_entry = tk.Entry(
            ollama_frame, textvariable=self.ollama_embeddings_var, width=30
        )
        self.ollama_embeddings_entry.pack(side=tk.LEFT, padx=5, pady=5)
        return ollama_frame

    def create_gguf_options(self, parent):
        gguf_frame = ttk.Frame(parent)
        gguf_embedding_label = ttk.Label(gguf_frame, text="GGUF Embedding Model Path:")
        gguf_embedding_label.pack(side=tk.LEFT, padx=5, pady=5)
        CreateToolTip(
            gguf_embedding_label,
            text="Path to GGUF file of the embedding model to use Llama.cpp",
        )
        self.gguf_embedding_entry = tk.Entry(
            gguf_frame, textvariable=self.embedding_gguf_var, width=50
        )
        self.gguf_embedding_entry.pack(side=tk.LEFT, padx=5, pady=5)
        return gguf_frame

    def create_hf_options(self, parent):
        hf_frame = ttk.Frame(parent)
        transformers_embeddings_label = ttk.Label(
            hf_frame, text="Hugging Face 🤗 Transformers Embedding:"
        )
        transformers_embeddings_label.pack(side=tk.LEFT, padx=5, pady=5)
        CreateToolTip(
            transformers_embeddings_label,
            text="Modify `hftransformers_embeddings.py` if needed to work with your model",
        )
        self.transformers_embeddings_entry = tk.Entry(
            hf_frame, textvariable=self.transformers_embeddings_var, width=40
        )
        self.transformers_embeddings_entry.pack(side=tk.LEFT, padx=5, pady=5)
        return hf_frame

    def create_openai_options(self, parent):
        openai_frame = ttk.Frame(parent)

        # First row for API Base URL
        openai_api_base_url_frame = ttk.Frame(openai_frame)
        openai_api_base_url_frame.pack(fill=tk.X)

        openai_api_base_url_label = ttk.Label(
            openai_api_base_url_frame, text="OpenAI API Base URL:"
        )
        openai_api_base_url_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.openai_api_base_url_entry = tk.Entry(
            openai_api_base_url_frame,
            textvariable=self.openai_api_base_url_var,
            width=40,
        )
        self.openai_api_base_url_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Second row for API Key
        openai_api_key_frame = ttk.Frame(openai_frame)
        openai_api_key_frame.pack(fill=tk.X)

        openai_api_key_label = ttk.Label(openai_api_key_frame, text="OpenAI API Key:")
        openai_api_key_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.openai_api_key_entry = tk.Entry(
            openai_api_key_frame,
            textvariable=self.openai_api_key_var,
            width=40,
            show="*",
        )
        self.openai_api_key_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Third row for Model
        openai_model_frame = ttk.Frame(openai_frame)
        openai_model_frame.pack(fill=tk.X)
        openai_model_label = ttk.Label(openai_model_frame, text="OpenAI Model:")
        openai_model_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.openai_model_entry = tk.Entry(
            openai_model_frame, textvariable=self.openai_model_var, width=40
        )
        self.openai_model_entry.pack(side=tk.LEFT, padx=5, pady=5)

        return openai_frame

    def update_text_embed_options(self, *args):
        selected_provider = self.text_embed_provider_var.get()

        self.ollama_frame.pack_forget()
        self.gguf_frame.pack_forget()
        self.hf_frame.pack_forget()
        self.openai_frame.pack_forget()

        if selected_provider == "ollama":
            self.ollama_frame.pack(fill=tk.X, pady=5)
        elif selected_provider == "llama_cpp":
            self.gguf_frame.pack(fill=tk.X, pady=5)
        elif selected_provider == "HF_transformers":
            self.hf_frame.pack(fill=tk.X, pady=5)
        elif selected_provider == "openai_api":
            self.openai_frame.pack(fill=tk.X, pady=5)

    def get_config(self):
        return {
            "text_embed": {
                "provider": self.text_embed_provider_var.get(),
                "embedding_gguf": self.embedding_gguf_var.get(),
                "ollama_embeddings": self.ollama_embeddings_var.get(),
                "HF_transformers_embeddings": self.transformers_embeddings_var.get(),
                "openai_endpoint": self.openai_api_base_url_var.get(),
                "openai_api_key": self.openai_api_key_var.get(),
                "openai_model": self.openai_model_var.get(),
            }
        }
