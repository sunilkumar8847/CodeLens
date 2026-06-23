from pathlib import Path
from config import (
    IGNORED_DIRS,
    IGNORED_FILES,
    SUPPORTED_EXTENSTIONS,
    EXTENSTION_TO_LANGUAGE,
    MAX_FILE_SIZE_BYTES,
)

def detect_language(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    name = Path(file_path).name.lower()

    special_files = {
        "dockerfile": "Dockerfile",
        "makefile": "Makefile",
        "cmakelists.txt": "CMake",
        "rakefile": "Ruby",
        "gemfile": "Ruby",
        "procfile": "Procfile",
        "vagrantfile": "Ruby",
        ".bashrc": "Bash",
        ".zshrc": "Zsh",
    }

    if name in special_files:
        return special_files[name]

    return EXTENSTION_TO_LANGUAGE.get(ext, "Unknown")


def should_ignore(file_path: Path, repo_root: Path) -> bool:
    try:
        rel = file_path.relative_to(repo_root)
    except ValueError:
        return True

    for part in rel.parts:
        if part in IGNORED_DIRS:
            return True

    special_files = {"dockerfile", "makefile", "rakefile", "gemfile", "procfile", "vagrantfile",}

    if file_path.is_file():
        if file_path.name in IGNORED_FILES:
            return True

        if file_path.suffix.lower() not in SUPPORTED_EXTENSTIONS:
            if file_path.suffix == "" and file_path.name not in special_files:
                return True

        try:
            if file_path.stat().st_size > MAX_FILE_SIZE_BYTES or file_path.stat().st_size == 0:
                return True
        except OSError:
            return True

    return False


def list_repo_files(repo_path: Path) -> list[dict]:
    files = []

    for file_path in sorted(repo_path.rglob("*")):
        if not file_path.is_file():
            continue
        if should_ignore(file_path, repo_path):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue

        if not content.strip():
            continue

        rel_path = file_path.relative_to(repo_path).as_posix()
        language = detect_language(rel_path)

        files.append({
            "path": rel_path,
            "name": file_path.name,
            "language": language,
            "content": content
        })

    return files