from pydantic import BaseModel, Field

class Chunk(BaseModel):
    """A single chunk produced by LLM-based document splitting."""
    headline: str = Field(
        description="A brief heading for this chunk, typically a few words, "
                    "that is most likely to be surfaced in a query"
    )
    summary: str = Field(
        description="A few sentences summarizing the content of this chunk "
                    "to answer common questions"
    )
    original_text: str = Field(
        description="The original text of this chunk from the provided document, "
                    "exactly as is, not changed in any way"
    )

    def as_result(self, document: dict) -> "Result":
        """Convert this chunk into a Result with metadata from the source document."""
        metadata = {
            "source": document["source"],
            "type": document["type"],
            "file_name": document.get("file_name", ""),
            "language": document.get("language", "Unknown"),
        }
        return Result(
            page_content=self.headline + "\n\n" + self.summary + "\n\n" + self.original_text,
            metadata=metadata,
        )

class Chunks(BaseModel):
    chunks: list[Chunk]

class Result(BaseModel):
    page_content: str
    metadata: dict

class RankOrder(BaseModel):
    """LLM reranking response: ordered list of chunk IDs by relevance."""
    order: list[int] = Field(
        description="The order of relevance of chunks, from most relevant "
                    "to least relevant, by chunk id number"
    )

# -----------------------------------------------------------------------------#

class ChatRequest(BaseModel):
    question: str
    history: list[dict] = []

class ChatResponse(BaseModel):
    answer: str
    citations: list = []

# class IngestRepo(BaseModel):
#     repo_url: str = Field(default="https://github.com/pallets/flask")

class RepoIngestRequest(BaseModel):
    repo_url: str = Field(
        default="https://github.com/pallets/flask",
        description = "GitHub repository URL to ingest",
        examples = ["https://github.com/pallets/flask"]
    )

class RepoIngestResponse(BaseModel):
    status: str = Field(description="Ingestion status: 'success' or 'error'")
    repo_name: str = Field(description="Name of the ingested repository")
    files_count: int = Field(description="Number of source files processed")
    chunks_count: int = Field(description="Number of chunks created and indexed")

class RepoStatusResponse(BaseModel):
    ingested: bool = Field(description="Whether a repo has been ingested")
    repo_name: str = Field(default="", description="Name of the current repo")
    chunks_count: int = Field(default=0, description="Number of indexed chunks")

class Citation(BaseModel):
    """A single file citation in an answer."""
    file_path: str = Field(description="Relative path of the source file")
    file_name: str = Field(description="Filename")
    language: str = Field(description="Programming language")
    snippet: str = Field(description="Relevant code/text snippet from the file")