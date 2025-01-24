import os
import time
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def scan_directory(directory, exclude_directories):
    """
    Recursively scans a directory for image files, excluding any directories specified.

    Args:
        directory (str): The directory to scan for image files.
        exclude_directories (list): A list of directories to exclude from the scan.

    Returns:
        list: A list of paths to image files found within the directory, excluding those in excluded directories.
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    images = []
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if (
                    entry.is_file()
                    and not entry.name.startswith("._")
                    and entry.name.lower().endswith(tuple(image_extensions))
                ):
                    images.append(entry.path)
                elif entry.is_dir():
                    # Check if this directory is in the exclude list
                    if not any(
                        os.path.commonpath([entry.path, excl]) == excl
                        for excl in exclude_directories
                    ):
                        images.extend(scan_directory(entry.path, exclude_directories))
    except PermissionError:
        print(f"Permission denied: {directory}")
    except Exception as e:
        print(f"Error scanning {directory}: {e}")
    return images


def fast_scan_for_images(directories, exclude_directories=None):
    """
    Scans multiple directories for image files in parallel, excluding specified directories.

    Args:
        directories (list): A list of directories to scan for image files.
        exclude_directories (list, optional): Directories to exclude from the scan. Defaults to None.

    Returns:
        tuple: A tuple containing a list of image paths found and the total time taken to scan.
    """
    if exclude_directories is None:
        exclude_directories = []

    start_time = time.time()
    all_images = []

    with tqdm(total=len(directories), desc="Scanning directories") as pbar:
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            future_to_dir = {
                executor.submit(scan_directory, dir, exclude_directories): dir
                for dir in directories
            }
            for future in as_completed(future_to_dir):
                dir = future_to_dir[future]
                try:
                    images = future.result()
                    all_images.extend(images)
                    pbar.update()
                except Exception as e:
                    print(f"Error processing {dir}: {e}")

    end_time = time.time()
    return all_images, end_time - start_time
