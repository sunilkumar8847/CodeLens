from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL_NAME
from models.schemas import Result
from storage.vector_store import clear_and_get_collection
# from storage.vector_store import clear_and_get_collection, query_search

model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def embed_query(text: str) -> list[float]:
    return model.embed_query(text)

def create_embedding(chunks: list[Result]) -> int:
    if not chunks:
        return 0

    collection = clear_and_get_collection()

    texts = [chunk.page_content for chunk in chunks]
    metas = [chunk.metadata for chunk in chunks]
    ids = [str(i) for i in range(len(chunks))]

    vectors = model.embed_documents(texts)

    collection.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metas)

    print(f"[embeddings] Stored {collection.count()} chunks")

    return collection.count()

# query = "authentication"
# embedded_query = embed_query(query)
# query_search(embedded_query)