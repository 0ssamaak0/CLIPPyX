from Index.create_db import *
from Index.scan import scan_and_save

import time

scanned = scan_and_save()
if not scanned:
    raise Exception("Error scanning images")
image_collection, text_collection = create_vectordb("db")
start = time.time()
index_images(image_collection, text_collection)
clean_index(image_collection, text_collection)
end = time.time()
print(f"Indexing took {end - start} seconds")
