import ctypes

# Constants
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002

# DLL imports
everything_dll = ctypes.WinDLL("C:\\Everything-SDK\\DLL\\Everything64.dll")
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

    for format in formats:
        # Create buffers
        filename = ctypes.create_unicode_buffer(260)

        # Setup search
        everything_dll.Everything_SetSearchW(format)
        everything_dll.Everything_SetRequestFlags(
            EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH
        )

        # Execute the query
        everything_dll.Everything_QueryW(1)

        # Get the number of results
        num_results = everything_dll.Everything_GetNumResults()

        # Show results
        for i in range(num_results):
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
    with open(file_path, "w") as f:
        for file_name in file_names:
            f.write(file_name + "\n")

    print(f"Paths saved to {file_path}")


if __name__ == "__main__":
    # Search for files
    file_names = search_files()
    # Save file names to text file
    save_file_names(file_names, "images_paths.txt")
