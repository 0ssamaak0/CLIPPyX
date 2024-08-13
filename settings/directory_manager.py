import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
import platform
from settings.tooltip import CreateToolTip


class DirectoryManager:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        self.create_scan_method_options()
        self.create_directory_lists()

    def create_scan_method_options(self):
        # Deep Scan and Batch Size in the same row
        self.deep_scan_var = tk.BooleanVar(value=self.config["deep_scan"])
        self.batch_size_var = tk.IntVar(value=int(self.config["batch_size"]))

        deep_scan_frame = ttk.Frame(self.parent)
        deep_scan_frame.pack(fill=tk.X, pady=10)

        deep_scan_label = ttk.Label(deep_scan_frame, text="Deep Scan:")
        deep_scan_label.pack(side=tk.LEFT, padx=5, pady=5)
        CreateToolTip(
            deep_scan_label,
            text="Deepscan ensures if a file content has changed but the file name is the same, it will still be reindexed.\n(It may affect performance for large directories)",
        )
        tk.Checkbutton(deep_scan_frame, variable=self.deep_scan_var).pack(
            side=tk.LEFT, padx=5, pady=5
        )

        batch_size_label = ttk.Label(deep_scan_frame, text="Batch Size:")
        batch_size_label.pack(side=tk.LEFT, padx=5, pady=5)
        CreateToolTip(
            batch_size_label,
            text="Batch size for both file IO, CLIP inference and OCR inference.",
        )
        tk.Entry(deep_scan_frame, textvariable=self.batch_size_var).pack(
            side=tk.LEFT, padx=5, pady=5
        )

        # Scan Method as Horizontal Radio Buttons
        scan_method_label = ttk.Label(self.parent, text="Scan Method:")
        scan_method_label.pack(anchor="w")
        CreateToolTip(
            scan_method_label,
            text="Default method scans the selected directories\nEverything method uses voidtools Everything (Windows only)\nYou should have Everything installed and running\nConfigure directories to include/exclude from Everything itself",
        )
        self.scan_method_var = tk.StringVar(value=self.config["scan_method"])
        radiobutton_frame = ttk.Frame(self.parent)
        radiobutton_frame.pack(anchor="w")
        radiobuttons = [
            ("Default", "default"),
            ("voidtools Everything (Windows only)", "Everything"),
        ]
        for text, mode in radiobuttons:
            state = (
                tk.NORMAL
                if mode == "default" or platform.system() == "Windows"
                else tk.DISABLED
            )
            tk.Radiobutton(
                radiobutton_frame,
                text=text,
                variable=self.scan_method_var,
                value=mode,
                state=state,
                command=self.update_directory_options,
            ).pack(side="left", padx=5, pady=5)

    def create_directory_lists(self):
        directories_frame = ttk.Frame(self.parent)
        directories_frame.pack(fill=tk.X, pady=10)

        # Include Directories
        include_frame = ttk.Frame(directories_frame)
        include_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=0)

        ttk.Label(include_frame, text="Include Directories:").pack(anchor="w")
        self.include_listbox = tk.Listbox(include_frame, width=43)
        self.include_listbox.pack(fill=tk.BOTH, expand=1)

        for directory in self.config["include_directories"]:
            self.include_listbox.insert(tk.END, directory)

        self.include_buttons = []
        self.include_buttons.append(
            ttk.Button(
                include_frame,
                text="Add",
                command=lambda: self.add_directory(
                    self.include_listbox, "include_directories"
                ),
            )
        )
        self.include_buttons[-1].pack(side=tk.LEFT, padx=5, pady=5)
        self.include_buttons.append(
            ttk.Button(
                include_frame,
                text="Remove",
                command=lambda: self.remove_directory(
                    self.include_listbox, "include_directories"
                ),
            )
        )
        self.include_buttons[-1].pack(side=tk.LEFT, padx=5, pady=5)

        # Exclude Directories
        exclude_frame = ttk.Frame(directories_frame)
        exclude_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=0)

        ttk.Label(exclude_frame, text="Exclude Directories:").pack(anchor="w")
        self.exclude_listbox = tk.Listbox(exclude_frame, width=43)
        self.exclude_listbox.pack(fill=tk.BOTH, expand=1)

        for directory in self.config["exclude_directories"]:
            self.exclude_listbox.insert(tk.END, directory)

        self.exclude_buttons = []
        self.exclude_buttons.append(
            ttk.Button(
                exclude_frame,
                text="Add",
                command=lambda: self.add_directory(
                    self.exclude_listbox, "exclude_directories"
                ),
            )
        )
        self.exclude_buttons[-1].pack(side=tk.LEFT, padx=5, pady=5)
        self.exclude_buttons.append(
            ttk.Button(
                exclude_frame,
                text="Remove",
                command=lambda: self.remove_directory(
                    self.exclude_listbox, "exclude_directories"
                ),
            )
        )
        self.exclude_buttons[-1].pack(side=tk.LEFT, padx=5, pady=5)

    def add_directory(self, listbox, config_key):
        new_dir = filedialog.askdirectory()
        if new_dir:
            self.config[config_key].append(new_dir)
            listbox.insert(tk.END, new_dir)

    def remove_directory(self, listbox, config_key):
        selected = listbox.curselection()
        if selected:
            self.config[config_key].pop(selected[0])
            listbox.delete(selected)

    def update_directory_options(self):
        state = tk.NORMAL if self.scan_method_var.get() == "default" else tk.DISABLED
        self.include_listbox.config(state=state)
        self.exclude_listbox.config(state=state)
        for button in self.include_buttons + self.exclude_buttons:
            button.config(state=state)

    def get_config(self):
        return {
            "scan_method": self.scan_method_var.get(),
            "deep_scan": self.deep_scan_var.get(),
            "batch_size": int(self.batch_size_var.get()),
            "include_directories": list(self.include_listbox.get(0, tk.END)),
            "exclude_directories": list(self.exclude_listbox.get(0, tk.END)),
        }
