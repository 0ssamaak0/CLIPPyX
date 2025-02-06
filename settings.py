import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import darkdetect

from settings.config_manager import load_config, save_config
from settings.directory_manager import DirectoryManager
from settings.clip_manager import CLIPManager
from settings.text_embed_manager import TextEmbedManager


class CLIPPyXSettings:
    """
    Manages the CLIPPyX Settings interface.

    This class initializes and displays a graphical user interface (GUI) for configuring
    various settings related to the CLIPPyX application. It loads an existing configuration
    from a YAML file, constructs the interface elements, and provides functionality to update
    and save new settings.

    Attributes:
        config (dict): Holds the loaded configuration data from 'config.yaml'.
        root (ttk.Window): The root window for the settings interface.
        main_frame (ttk.Frame): The main frame holding the scrollable canvas.
        canvas (tk.Canvas): A canvas to enable scrolling for the settings form.
        scrollbar (ttk.Scrollbar): A scrollbar for the settings canvas.
        frame (ttk.Frame): A frame nested within the canvas to hold UI components.
        directory_manager (DirectoryManager): Manages directory settings.
        clip_manager (CLIPManager): Manages CLIP-related settings.
        text_embed_manager (TextEmbedManager): Manages text embedding settings.
    """

    def __init__(self):
        """
        Initialize CLIPPyXSettings.

        Loads the configuration from 'config.yaml' and calls `setup_ui()` to set up the GUI.
        """
        self.config = load_config("config.yaml")
        self.setup_ui()

    def setup_ui(self):
        """
        Set up the main window and UI components.

        Determines whether to use a light or dark theme (via `darkdetect`), then creates
        and configures the main application window, including an icon, minimum size,
        and title. Finally, calls other methods to create the main frame, directory,
        CLIP, and text embedding options, and a button panel.
        """
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
        """
        Create and configure the main scrollable frame.

        Sets up a canvas and scrollbar to allow the interface to be scrollable if
        it exceeds the window size. Places the actual UI components inside a nested
        frame added to the canvas.
        """
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.scrollbar = ttk.Scrollbar(
            self.main_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
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
        """
        Create and initialize directory management settings.

        Instantiates a DirectoryManager object, providing it the main content frame
        (`self.frame`) and the current `config`.
        """
        self.directory_manager = DirectoryManager(self.frame, self.config)

    def create_clip_options(self):
        """
        Create and initialize CLIP-related settings.

        Instantiates a CLIPManager object, which controls settings related to CLIP models
        and configurations. It is given the main content frame and the current `config`.
        """
        self.clip_manager = CLIPManager(self.frame, self.config)

    def create_text_embed_options(self):
        """
        Create and initialize text embedding settings.

        Instantiates a TextEmbedManager object, providing it the main content frame and
        the current `config`. This allows the user to configure text embedding parameters.
        """
        self.text_embed_manager = TextEmbedManager(self.frame, self.config)

    def create_buttons(self):
        """
        Create and configure buttons for saving and quitting.

        Adds "Save" and "Quit" buttons to the bottom of the settings UI. The "Save" button
        triggers `save_changes()` and the "Quit" button closes the application.
        """
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(pady=10)

        ttk.Button(buttons_frame, text="Save", command=self.save_changes).pack(
            side=tk.LEFT, padx=10
        )
        ttk.Button(buttons_frame, text="Quit", command=self.root.quit).pack(
            side=tk.LEFT, padx=10
        )

    def save_changes(self):
        """
        Save configuration changes.

        Gathers updated settings from the DirectoryManager, CLIPManager, and
        TextEmbedManager, merges them into `self.config`, and saves them to 'config.yaml'.
        Displays a success message upon completion.
        """
        # Update config with values from all managers
        self.config.update(self.directory_manager.get_config())
        self.config.update(self.clip_manager.get_config())
        self.config.update(self.text_embed_manager.get_config())

        save_config(self.config, "config.yaml")
        messagebox.showinfo("Success", "Configuration saved successfully!")

    def run(self):
        """
        Start the main event loop.

        Blocks execution until the GUI is closed.
        """
        self.root.mainloop()



if __name__ == "__main__":
    app = CLIPPyXSettings()
    app.run()
