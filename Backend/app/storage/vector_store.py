import chromadb
from config import DB_NAME, COLLECTION_NAME
from models.schemas import Result

client = chromadb.PersistentClient(path=DB_NAME)

def clear_and_get_collection():
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)

    return client.get_or_create_collection(COLLECTION_NAME)

def query_search(embedded_query: list[float], n_results: int=5) -> list[Result]:
    collection = client.get_or_create_collection(COLLECTION_NAME)

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[embedded_query], n_results=min(n_results, collection.count())
    )

    chunks = []

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append(Result(page_content=doc, metadata=meta))

    print("Chunks:", chunks)

    return chunks

