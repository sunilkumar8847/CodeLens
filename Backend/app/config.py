from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

MODEL = "groq/openai/gpt-oss-120b"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

BASE_DIR = Path(__file__).parent.parent
# print(f"Path: {BASE_DIR}")
DB_NAME = str(BASE_DIR/"vector_db")
COLLECTION_NAME = "code_chunks"

REPOS_DIR = BASE_DIR/"repo"
REPOS_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 1000
OVERLAP_SIZE = 200

RETRIEVAL_K = 10
FINAL_K = 5

IGNORED_DIRS = {
    ".git", "node_modules", "dist", "build", "__pycache__",
    ".venv", "venv", "env", ".env", ".tox", ".mypy_cache",
    ".pytest_cache", ".idea", ".vscode", ".vs", "coverage",
    "htmlcov", ".eggs", "*.egg-info", "vendor", "bower_components",
    ".next", ".nuxt", ".output", "out", ".svelte-kit",
    "target", "bin", "obj",
}

IGNORED_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "uv.lock",
    "Pipfile.lock", "poetry.lock", "composer.lock", "Gemfile.lock",
    "Cargo.lock", "go.sum",
    ".DS_Store", "Thumbs.db", ".gitignore", ".gitattributes",
    ".editorconfig", ".prettierrc", ".eslintrc",
}

SUPPORTED_EXTENSTIONS = {
    # Python
    ".py", ".pyi", ".pyw",
    # JavaScript / TypeScript
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    # Web
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    # Java / Kotlin / Scala
    ".java", ".kt", ".kts", ".scala",
    # C / C++ / C#
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh", ".cs",
    # Go / Rust
    ".go", ".rs",
    # Ruby / PHP / Swift
    ".rb", ".php", ".swift",
    # Shell
    ".sh", ".bash", ".zsh", ".fish", ".ps1",
    # Config / Data
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".xml", ".csv",
    # Docs
    ".md", ".txt", ".rst", ".adoc",
    # SQL
    ".sql",
    # Docker / CI
    ".dockerfile",
    # R / Julia / Lua
    ".r", ".jl", ".lua",
}

EXTENSTION_TO_LANGUAGE = {
    ".py": "Python", ".pyi": "Python", ".pyw": "Python",
    ".js": "JavaScript", ".jsx": "JavaScript (JSX)",
    ".ts": "TypeScript", ".tsx": "TypeScript (TSX)",
    ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".html": "HTML", ".htm": "HTML",
    ".css": "CSS", ".scss": "SCSS", ".sass": "Sass", ".less": "Less",
    ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin",
    ".scala": "Scala",
    ".c": "C", ".h": "C/C++ Header",
    ".cpp": "C++", ".hpp": "C++ Header", ".cc": "C++", ".hh": "C++ Header",
    ".cs": "C#",
    ".go": "Go", ".rs": "Rust",
    ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
    ".sh": "Shell", ".bash": "Bash", ".zsh": "Zsh",
    ".fish": "Fish", ".ps1": "PowerShell",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".ini": "INI", ".cfg": "Config", ".conf": "Config",
    ".xml": "XML", ".csv": "CSV",
    ".md": "Markdown", ".txt": "Text", ".rst": "reStructuredText",
    ".adoc": "AsciiDoc",
    ".sql": "SQL",
    ".dockerfile": "Dockerfile",
    ".r": "R", ".jl": "Julia", ".lua": "Lua",
}

MAX_FILE_SIZE_BYTES = 100_000