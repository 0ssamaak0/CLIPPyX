import os
import time
import csv
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def scan_directory(directory):
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    images = []
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(tuple(image_extensions)):
                    images.append(entry.path)
                elif entry.is_dir():
                    images.extend(scan_directory(entry.path))
    except PermissionError:
        print(f"Permission denied: {directory}")
    except Exception as e:
        print(f"Error scanning {directory}: {e}")
    return images

def fast_scan_for_images(directories):
    start_time = time.time()
    all_images = []

    with tqdm(total=len(directories), desc="Scanning directories") as pbar:
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            future_to_dir = {executor.submit(scan_directory, dir): dir for dir in directories}
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

def save_to_csv(image_paths, filename='image_paths.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['path'])  # Header
        for path in image_paths:
            writer.writerow([path])
    print(f"Image paths saved to {filename}")

def save_to_sqlite(image_paths, filename='image_database.db'):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id INTEGER PRIMARY KEY, path TEXT UNIQUE)''')
    c.executemany("INSERT OR IGNORE INTO images (path) VALUES (?)", 
                  [(path,) for path in image_paths])
    conn.commit()
    conn.close()
    print(f"Image paths saved to SQLite database: {filename}")

def read_from_csv(filename='image_paths.csv'):
    image_paths = []
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            image_paths.append(row[0])
    return image_paths

def read_from_sqlite(filename='image_database.db'):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT path FROM images")
    image_paths = [row[0] for row in c.fetchall()]
    conn.close()
    return image_paths

def process_image(path):
    # Placeholder for image processing function
    # Replace this with your actual image processing logic
    print(f"Processing image: {path}")

directories = ["C:\\Users\\ossam\\OneDrive\\Pictures"]

if not directories:
    print("No valid directories entered. Exiting.")
    exit()

print(f"\nStarting scan of {len(directories)} directories...")
image_paths, scan_time = fast_scan_for_images(directories)

print(f"\nScan completed in {scan_time:.2f} seconds")
print(f"Total images found: {len(image_paths)}")

# # Save to CSV
# save_to_csv(image_paths)

# Save to SQLite
save_to_sqlite(image_paths)

# # Example of reading back the data
# print("\nReading from CSV:")
# csv_paths = read_from_csv()
# print(f"Read {len(csv_paths)} paths from CSV")

# print("\nReading from SQLite:")
# sqlite_paths = read_from_sqlite()
# print(f"Read {len(sqlite_paths)} paths from SQLite")

# Print sample paths
print("\nSample of image paths:")
for path in image_paths[:10]:
    print(path)
if len(image_paths) > 10:
    print(f"... and {len(image_paths) - 10} more")

# Example of processing images
print("\nProcessing images (demo):")
for path in image_paths[:5]:  # Process first 5 images as a demo
    process_image(path)