import chromadb
from tqdm import tqdm

chroma_client = chromadb.PersistentClient(path="windows_db")
collection = chroma_client.get_or_create_collection(name="my_collection")

for i in tqdm(range(200)):
    collection.upsert(ids = str(i), embeddings = [i, i, i])