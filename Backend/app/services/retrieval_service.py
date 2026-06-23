from litellm import completion

from config import MODEL, RETRIEVAL_K, FINAL_K
from models.schemas import Result
from services.embedding_service import embed_query
from storage.vector_store import query_search


def fetch_context_unranked(question: str) -> list[Result]:
    embeded_query = embed_query(question)
    return query_search(embeded_query, n_results=RETRIEVAL_K)


def rewrite_query(question: str, history: list[dict]=[]) -> str:
    message = f"""
    You are helping a developer search a code repository.
    Rewrite this question into a short, precise search query focused on
    filenames, function names, class names, or technical terms.

    Question: {question}

    Respond ONLY with the search query, nothing else.
    """

    response = completion(model=MODEL, messages=[{"role": "system", "content": message}])
    return response.choices[0].message.content



def merge_chunks(chunk1: list[Result], chunk2: list[Result]) -> list[Result]:
    merged = chunk1[:]
    existing = {chunk.page_content for chunk in chunk1}

    for chunk in chunk2:
        if chunk.page_content not in existing:
            merged.append(chunk)
            existing.add(chunk.page_content)

    return merged

def fetch_context(question: str, history: list[dict]=[]) -> list[Result]:
    chunks1 = fetch_context_unranked(question)

    try:
        rewritten_query = rewrite_query(question)
        print(f"[retrieval] Rewritten query: {rewritten_query}")
        chunks2 = fetch_context_unranked(rewritten_query)
        print(f"[retrieval] Secondary search: {len(chunks2)} chunks")
    except Exception as e:
        print(f"[retrieval] Query rewrite failed (using primary only): {e}")
        chunks2 = []

    merged = merge_chunks(chunks1, chunks2)
    print(f"[retrieval] Merged: {len(merged)} unique chunks")

    final_chunk = merged[:FINAL_K]
    print(f"[retrieval] Returning {len(final_chunk)} chunks to answer service")
    return final_chunk