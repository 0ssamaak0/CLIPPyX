import tkinter as tk
import ttkbootstrap as ttk
import platform
from settings.tooltip import CreateToolTip


class OCRManager:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        # Create frame for OCR settings
        ocr_frame = ttk.LabelFrame(self.parent, text="OCR Settings")
        ocr_frame.pack(fill=tk.X, padx=10, pady=10)

        # OCR Provider selection
        ocr_provider_frame = ttk.Frame(ocr_frame)
        ocr_provider_frame.pack(fill=tk.X, pady=5)

        ocr_provider_label = ttk.Label(ocr_provider_frame, text="OCR Provider:")
        ocr_provider_label.pack(side=tk.LEFT, padx=5)
        CreateToolTip(
            ocr_provider_label,
            text="Select the OCR provider to use for text recognition in images",
        )

        # Get the saved OCR provider or default to "doctr"
        self.ocr_provider_var = tk.StringVar(
            value=self.config.get("ocr_provider", "doctr")
        )

        # Radio buttons frame
        ocr_radio_frame = ttk.Frame(ocr_provider_frame)
        ocr_radio_frame.pack(side=tk.LEFT, padx=5)

        # Doctr option
        ttk.Radiobutton(
            ocr_radio_frame, text="Doctr", variable=self.ocr_provider_var, value="doctr"
        ).pack(side=tk.LEFT, padx=10)

        # Live Text option (Mac only)
        live_text_radio = ttk.Radiobutton(
            ocr_radio_frame,
            text="Live Text (Mac only)",
            variable=self.ocr_provider_var,
            value="livetext",
            state=tk.NORMAL if platform.system() == "Darwin" else tk.DISABLED,
        )
        live_text_radio.pack(side=tk.LEFT, padx=10)

    def get_config(self):
        return {
            "ocr_provider": self.ocr_provider_var.get(),
        }
