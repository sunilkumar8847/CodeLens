from utils.git_utils import clone_repo, extract_reponame
from services.parser_service import parse_repo
from services.chunk_service import create_chunks
from services.embedding_service import create_embedding
from storage.vector_store import client, COLLECTION_NAME

_current_repo = {"name": "", "ingested": False}

def get_current_repo_status() -> dict:
    collection = client.get_or_create_collection(COLLECTION_NAME)
    return {
        "ingested": _current_repo["ingested"],
        "repo_name": _current_repo["name"],
        "chunks_count": collection.count(),
    }

def ingest_repo(repo_url: str) -> dict:
    global _current_repo

    repo_name = extract_reponame(repo_url)
    print(f"\n[ingest] Starting ingestion for: {repo_name}\n")

    try:
        file_path = clone_repo(repo_url)
        documents = parse_repo(file_path)

        if len(documents) == 0:
            return {
                "status": "err",
                "repo_name": repo_name,
                "files_count": 0,
                "chunks_count": 0,
            }

        chunks = create_chunks(documents)
        chunks_count = create_embedding(chunks)

        _current_repo = {"name": repo_name, "ingested": True}

        print(f"[ingest] ✅ Done! Files: {len(documents)}, Chunks: {chunks_count}")

        return {
            "status": "success",
            "repo_name": repo_name,
            "files_count": len(documents),
            "chunks_count": chunks_count,
        }

    except Exception as e:
        print(f"[ingest] ❌ Error: {e}")
        return {
                "status": "err",
                "repo_name": repo_name,
                "files_count": 0,
                "chunks_count": 0,
            }
