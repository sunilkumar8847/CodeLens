from pathlib import Path
from utils.file_utils import list_repo_files

def parse_repo(repo_path: Path) -> list[dict]:
    raw_files = list_repo_files(repo_path)

    documents = []
    for f in raw_files:
        documents.append({
            "source": f["path"],
            "type": f["language"],
            "file_name": f["name"],
            "language": f["language"],
            "text": f["content"]
        })

    print(f"[parser] Loaded {len(documents)}, source file from {repo_path.name}")
    return documents