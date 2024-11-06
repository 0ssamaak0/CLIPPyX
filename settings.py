import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import darkdetect
import warnings

warnings.filterwarnings("ignore")

from settings.config_manager import load_config, save_config
from settings.directory_manager import DirectoryManager


class CLIPPyXSettings:
    def __init__(self):
        self.config = load_config("config.yaml")
        self.setup_ui()

    def setup_ui(self):
        theme = darkdetect.theme()
        theme_dict = {"Light": "lumen", "Dark": "darkly"}
        self.root = ttk.Window(themename=theme_dict[theme])
        self.root.title("CLIPPyX Settings")
        self.root.minsize(840, 610)
        self.root.iconphoto(False, tk.PhotoImage(file="assets/icon.png"))

        self.create_main_frame()
        self.create_directory_options()
        self.create_buttons()

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.scrollbar = ttk.Scrollbar(
            self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

    def create_directory_options(self):
        self.directory_manager = DirectoryManager(self.frame, self.config)

        # Add entry for cohere_api_key
        api_key_label = ttk.Label(self.frame, text="Cohere API Key:")
        api_key_label.pack(pady=5, anchor="w")

        self.api_key_entry = ttk.Entry(self.frame)
        self.api_key_entry.pack(fill=tk.X, padx=10)

        # Populate with existing config value if available
        self.api_key_entry.insert(0, self.config.get("cohere_api_key", ""))

    def create_buttons(self):
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        ttk.Button(buttons_frame, text="Save", command=self.save_changes).pack(
            side=tk.LEFT, padx=10
        )
        ttk.Button(buttons_frame, text="Quit", command=self.root.quit).pack(
            side=tk.LEFT, padx=10
        )

    def save_changes(self):
        # Update config with values from all managers
        self.config.update(self.directory_manager.get_config())

        # Save cohere_api_key from entry field
        self.config["cohere_api_key"] = self.api_key_entry.get()

        save_config(self.config, "config.yaml")
        messagebox.showinfo("Success", "Configuration saved successfully!")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CLIPPyXSettings()
    app.run()
