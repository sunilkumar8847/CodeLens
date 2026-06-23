from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from tqdm import tqdm

from models.schemas import Result
from config import CHUNK_SIZE, OVERLAP_SIZE

_LANGUAGE_MAP: dict[str, Language] = {
    "Python": Language.PYTHON,
    "JavaScript": Language.JS,
    "JavaScript (JSX)": Language.JS,
    "TypeScript": Language.TS,
    "TypeScript (TSX)": Language.TS,
    "Java": Language.JAVA,
    "Go": Language.GO,
    "Rust": Language.RUST,
    "Ruby": Language.RUBY,
    "PHP": Language.PHP,
    "Swift": Language.SWIFT,
    "Scala": Language.SCALA,
    "C": Language.C,
    "C++": Language.CPP,
    "C/C++ Header": Language.CPP,
    "C++ Header": Language.CPP,
    "C#": Language.CSHARP,
    "Markdown": Language.MARKDOWN,
    "HTML": Language.HTML,
    "Kotlin": Language.KOTLIN,
    "Lua": Language.LUA,
    "Shell": Language.PYTHON,      # no shell enum; Python separators work OK
    "Bash": Language.PYTHON,
    "PowerShell": Language.PYTHON,
}

def _get_splitter(language: str) -> RecursiveCharacterTextSplitter:
    lang_enum = _LANGUAGE_MAP.get(language)

    if lang_enum:
        return RecursiveCharacterTextSplitter.from_language(
            language=lang_enum,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=OVERLAP_SIZE
        )

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=OVERLAP_SIZE,
        separators=["\n\n", "\n", " ", ""],
    )

def process_documents(document: dict) -> list[Result]:
    language = document.get("language", "Unknown")
    splitter = _get_splitter(language)

    text = document["text"]
    if not text.strip():
        return []

    raw_chunks = splitter.split_text(text)

    results = []

    for i, chunk_text in enumerate(raw_chunks):
        header = f"File: {document["source"]} ({language})\n\n"
        page_content = header + chunk_text

        metadata = {
            "source": document["source"],
            "type": language,
            "file_name": document.get("file_name", ""),
            "language": language,
            "chunk_index": i,
            "total_chunks": len(raw_chunks)
        }
        
        results.append(Result(page_content=page_content, metadata=metadata))

    return results


def create_chunks(documents: list[dict]) -> list[Result]:
    chunks = []
    print(f"[chunking] Processing {len(documents)} documents with LangChain splitters...")

    for doc in tqdm(documents, desc="chunking files"):
        try:
            results = process_documents(doc)
            chunks.extend(results)
        except Exception as e:
            print(f"[chunking] Failed to chunk {doc['source']}: {e}")
            # Fallback
            fallback = Result(
                page_content = f"File: {doc["source"]} \n\n {doc["text"][:2000]}",
                metadata={
                    "source": doc["source"],
                    "type": doc.get("language", "Unknown"),
                    "file_name": doc.get("file_name", ""),
                    "language": doc.get("language", "Unknown"),
                    "chunk_index": 0,
                    "total_chunks": 1,
                }
            )

            chunks.append(fallback)

    print(f"[chunking] Created {len(chunks)} total chunks (local, no API calls)")
    return chunks
