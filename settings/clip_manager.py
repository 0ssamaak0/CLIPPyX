import tkinter as tk
import ttkbootstrap as ttk
import platform
from settings.tooltip import CreateToolTip


class CLIPManager:
    """
    A GUI manager for configuring CLIP model settings using Tkinter.
    
    This class provides an interface for selecting a CLIP model provider and setting
    the corresponding checkpoint options. It supports both Hugging Face Transformers
    CLIP models and MobileCLIP variants.

    Attributes:
        parent (tk.Widget): The parent widget to attach the UI elements to.
        config (dict): A dictionary containing initial configuration values.
        clip_provider_var (tk.StringVar): Tracks the selected CLIP provider.
        mobileclip_checkpoint_var (tk.StringVar): Tracks the selected MobileCLIP checkpoint.
        transformers_clip_var (tk.StringVar): Tracks the Hugging Face CLIP model checkpoint.
        mobileclip_frame (ttk.Frame): The frame containing MobileCLIP options.
        hf_clip_frame (ttk.Frame): The frame containing Hugging Face CLIP options.
    """
    def __init__(self, parent, config):
        """
        Initializes the CLIPManager with the given parent widget and configuration.
        
        Args:
            parent (tk.Widget): The parent widget.
            config (dict): A dictionary containing default CLIP settings.
        """
        self.parent = parent
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the graphical user interface for selecting CLIP settings.
        """
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
        """
        Creates a dropdown menu for selecting the CLIP provider.
        
        Args:
            parent (tk.Widget): The parent widget to attach the selection UI.
        """
        provider_frame = ttk.Frame(parent)
        provider_frame.pack(fill=tk.X, pady=5)

        ttk.Label(provider_frame, text="CLIP Provider:").pack(
            side=tk.LEFT, padx=5, pady=5
        )
        
        # Create a list of providers, with MLX only available on macOS
        providers = ["HF_transformers", "mobileclip"]
        if platform.system() == "Darwin":
            providers.append("MLX")
            
        self.clip_provider_entry = ttk.Combobox(
            provider_frame,
            textvariable=self.clip_provider_var,
            values=providers,
            width=15,
        )
        self.clip_provider_entry.pack(side=tk.LEFT, padx=5, pady=5)

    def create_mobileclip_options(self, parent):
        """
        Creates UI elements for selecting a MobileCLIP variant.
        
        Args:
            parent (tk.Widget): The parent widget to attach the MobileCLIP options.
        
        Returns:
            ttk.Frame: The frame containing MobileCLIP options.
        """
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
        """
        Creates UI elements for specifying a Hugging Face Transformers CLIP model.
        
        Args:
            parent (tk.Widget): The parent widget to attach the Hugging Face CLIP options.
        
        Returns:
            ttk.Frame: The frame containing Hugging Face CLIP options.
        """
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
        """
        Updates the UI to show the appropriate options based on the selected CLIP provider.
        """
        selected_provider = self.clip_provider_var.get()

        self.mobileclip_frame.pack_forget()
        self.hf_clip_frame.pack_forget()

        if selected_provider == "mobileclip":
            self.mobileclip_frame.pack(fill=tk.X, pady=5)
        elif selected_provider == "HF_transformers":
            self.hf_clip_frame.pack(fill=tk.X, pady=5)

    def get_config(self):
        """
        Retrieves the current CLIP configuration from the UI.
        
        Returns:
            dict: A dictionary containing the selected CLIP settings.
        """
        return {
            "clip": {
                "provider": self.clip_provider_var.get(),
                "mobileclip_checkpoint": self.mobileclip_checkpoint_var.get(),
                "HF_transformers_clip": self.transformers_clip_var.get(),
            }
        }
