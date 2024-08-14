import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import darkdetect

from settings.config_manager import load_config, save_config
from settings.directory_manager import DirectoryManager
from settings.clip_manager import CLIPManager
from settings.text_embed_manager import TextEmbedManager


class CLIPPyXSettings:
    def __init__(self):
        self.config = load_config("config.yaml")
        self.setup_ui()

    def setup_ui(self):
        theme = darkdetect.theme()
        theme_dict = {"Light": "lumen", "Dark": "darkly"}
        self.root = ttk.Window(themename=theme_dict[theme])
        self.root.title("CLIPPyX Settings")
        self.root.minsize(840, 860)
        self.root.iconphoto(False, tk.PhotoImage(file="assets/icon.png"))

        self.create_main_frame()
        self.create_directory_options()
        self.create_clip_options()
        self.create_text_embed_options()
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

    def create_clip_options(self):
        self.clip_manager = CLIPManager(self.frame, self.config)

    def create_text_embed_options(self):
        self.text_embed_manager = TextEmbedManager(self.frame, self.config)

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
        self.config.update(self.clip_manager.get_config())
        self.config.update(self.text_embed_manager.get_config())

        save_config(self.config, "config.yaml")
        messagebox.showinfo("Success", "Configuration saved successfully!")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CLIPPyXSettings()
    app.run()
