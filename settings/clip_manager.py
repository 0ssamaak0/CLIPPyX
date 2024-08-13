import tkinter as tk
import ttkbootstrap as ttk
from settings.tooltip import CreateToolTip


class CLIPManager:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        clip_frame = ttk.Frame(self.parent)
        clip_frame.pack(fill=tk.X, pady=10)

        self.clip_provider_var = tk.StringVar(value=self.config["clip"]["provider"])
        self.mobileclip_checkpoint_var = tk.StringVar(
            value=self.config["clip"]["mobileclip_checkpoint"]
        )
        self.transformers_clip_var = tk.StringVar(
            value=self.config["clip"]["HF_transformers_clip"]
        )

        self.create_provider_selection(clip_frame)
        self.mobileclip_frame = self.create_mobileclip_options(clip_frame)
        self.hf_clip_frame = self.create_hf_clip_options(clip_frame)

        self.clip_provider_var.trace_add("write", self.update_clip_options)
        self.update_clip_options()

    def create_provider_selection(self, parent):
        provider_frame = ttk.Frame(parent)
        provider_frame.pack(fill=tk.X, pady=5)

        ttk.Label(provider_frame, text="CLIP Provider:").pack(
            side=tk.LEFT, padx=5, pady=5
        )
        self.clip_provider_entry = ttk.Combobox(
            provider_frame,
            textvariable=self.clip_provider_var,
            values=["HF_transformers", "mobileclip"],
            width=15,
        )
        self.clip_provider_entry.pack(side=tk.LEFT, padx=5, pady=5)

    def create_mobileclip_options(self, parent):
        mobileclip_frame = ttk.Frame(parent)
        ttk.Label(mobileclip_frame, text="MobileCLIP Variant:").pack(
            side=tk.LEFT, padx=5, pady=5
        )
        self.mobileclip_checkpoint_entry = ttk.Combobox(
            mobileclip_frame,
            textvariable=self.mobileclip_checkpoint_var,
            values=[
                "mobileclip_s0",
                "mobileclip_s1",
                "mobileclip_s2",
                "mobileclip_b",
                "mobileclip_blt",
            ],
            width=15,
        )
        self.mobileclip_checkpoint_entry.pack(side=tk.LEFT, padx=5, pady=5)
        return mobileclip_frame

    def create_hf_clip_options(self, parent):
        hf_clip_frame = ttk.Frame(parent)
        HF_checkpoint_label = ttk.Label(
            hf_clip_frame, text="Hugging Face 🤗 Transformers CLIP:"
        )
        HF_checkpoint_label.pack(side=tk.LEFT, padx=5, pady=5)
        CreateToolTip(
            HF_checkpoint_label,
            text="Any model compatible with Huggingface `CLIPModel`",
        )
        self.transformers_clip_checkpoint_entry = tk.Entry(
            hf_clip_frame, textvariable=self.transformers_clip_var, width=40
        )
        self.transformers_clip_checkpoint_entry.pack(side=tk.LEFT, padx=5, pady=5)
        return hf_clip_frame

    def update_clip_options(self, *args):
        selected_provider = self.clip_provider_var.get()

        self.mobileclip_frame.pack_forget()
        self.hf_clip_frame.pack_forget()

        if selected_provider == "mobileclip":
            self.mobileclip_frame.pack(fill=tk.X, pady=5)
        elif selected_provider == "HF_transformers":
            self.hf_clip_frame.pack(fill=tk.X, pady=5)

    def get_config(self):
        return {
            "clip": {
                "provider": self.clip_provider_var.get(),
                "mobileclip_checkpoint": self.mobileclip_checkpoint_var.get(),
                "HF_transformers_clip": self.transformers_clip_var.get(),
            }
        }
