import ctypes
import requests
from tqdm import tqdm
import os
from zipfile import ZipFile 
import yaml

# Load the configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

include_folders = config['include_folders']
exclude_folders = config['exclude_folders']

print(include_folders)
print(exclude_folders)

# Constants
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002

# DLL imports
try:
    everything_dll = ctypes.WinDLL("Index\\Everything-SDK\\DLL\\Everything64.dll")
except:
    url = f"https://www.voidtools.com/Everything-SDK.zip"
    response = requests.get(url, stream=True)

    file_size = int(response.headers.get("Content-Length", 0))
    chunk_size = 1024  # 1 KB
    filename = url.split("/")[-1]

    progress = tqdm(
        response.iter_content(chunk_size),
        f"Downloading {filename}",
        total=file_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    )
    with open(f"Index/{filename}", "wb") as f:
        for data in progress.iterable:
            f.write(data)
            progress.update(len(data))

    # unzip the downloaded file
    with ZipFile(f"Index/{filename}", "r") as zip_ref:
        zip_ref.extractall("Index/Everything-SDK")
    # delete the downloaded zip file
    os.remove(f"Index/{filename}")
    # load the DLL
    everything_dll = ctypes.WinDLL("Index\\Everything-SDK\\DLL\\Everything64.dll")

everything_dll.Everything_GetResultDateModified.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_ulonglong),
]
everything_dll.Everything_GetResultSize.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_ulonglong),
]
everything_dll.Everything_GetResultFileNameW.argtypes = [ctypes.c_int]
everything_dll.Everything_GetResultFileNameW.restype = ctypes.c_wchar_p


def search_files(formats=["*.png", "*.jpg", "*.jpeg"]):
    """
    Search for files with the given formats and return their full path names.

    Args:
        formats (list): List of file formats to search for.

    Returns:
        list: List of full path names of the found files.
    """
    file_names = []

    for file_format in formats:
        # Create search query with include and exclude paths
        query = file_format
        if 'all' not in include_folders:
            query += " " + " | ".join(f'"{path}"' for path in include_folders)
        elif exclude_folders:
            query += " " + " ".join(f'!"{path}"' for path in exclude_folders)
        
        # Setup search
        everything_dll.Everything_SetSearchW(query)
        everything_dll.Everything_SetRequestFlags(
            EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH
        )

        # Execute the query
        everything_dll.Everything_QueryW(1)

        # Get the number of results
        num_results = everything_dll.Everything_GetNumResults()

        # Show results
        for i in range(num_results):
            filename = ctypes.create_unicode_buffer(260)
            everything_dll.Everything_GetResultFullPathNameW(i, filename, 260)
            file_names.append(ctypes.wstring_at(filename))

    return file_names


def save_file_names(file_names, file_path):
    """
    Save the file names to a text file.

    Args:
        file_names (list): List of file names to save.
        file_path (str): Path to the text file to save the file names in.
    """
    with open(file_path, "w", encoding='utf-16') as f:
        for file_name in file_names:
            f.write(file_name + "\n")

    print(f"Paths of all images saved in {file_path}")


if __name__ == "__main__":
    # Search for files
    file_names = search_files()
    # Save file names to text file
    save_file_names(file_names, "images_paths.txt")
