from litellm import completion
from tenacity import retry, stop_after_attempt, wait_exponential

from config import MODEL
from models.schemas import Result, Citation, ChatResponse
from services.retrieval_service import fetch_context

SYSTEM_PROMPT = """
You are CodeLens, an expert code analysis assistant.
You are helping a developer understand a codebase by answering questions about it.
Your answer will be evaluated for accuracy, relevance, and completeness.

IMPORTANT RULES:
1. Answer ONLY based on the provided code context. Do not make up information.
2. Always cite the specific file(s) where you found the information.
3. Include relevant code snippets in your answer using markdown code blocks.
4. If the answer spans multiple files, mention each file.
5. If you don't know the answer from the provided context, say so.

For context, here are specific extracts from the codebase that are relevant to the user's question:

{context}

With this context, please answer the user's question accurately with file citations.
Format file references as: `filename` (e.g., `src/auth.py`)
"""

def make_rag_messages(question: str, history: list[dict], chunks: list[Result]) -> list[dict]:
    context = "\n\n".join(
        f"File: {chunk.metadata.get('source', '')}"
        f"{chunk.metadata.get("language", "unknown")} ---\n {chunk.page_content}"
        for chunk in chunks
        )

    system_prompt = SYSTEM_PROMPT.format(context=context)

    return (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": question}]
    )


def _extract_citations(chunks: list[Result]) -> list[Citation]:
    seen = set()
    citations = []

    for chunk in chunks:
        file_path = chunk.metadata.get('source', '')
        if file_path and file_path not in seen:
            seen.add(file_path)

            snippet = chunk.page_content[:500]
            if len(chunk.page_content) > 500:
                snippet += "\n..."

            citations.append(Citation(
                file_path=file_path,
                file_name=chunk.metadata.get("file_name", file_path.split("/")[-1]),
                language=chunk.metadata.get("language", "unknown"),
                snippet=snippet
            ))
    return citations


def _generate_answer(messages: list[dict]) -> str:
    try:
        response = completion(model=MODEL, messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        print(f"[answer] LLM call failed: {type(e).__name__}: {str(e)[:300]}")
        raise


def answer_question(question: str, history: list[dict]) -> ChatResponse:
    chunks = fetch_context(question)
    print(f"[answer] Got {len(chunks)} chunks from retrieval")

    if not chunks:
        return ChatResponse(
            answer="I don't have any indexed code to search. "
                   "Please ingest a repository first using the Ingest tab.",
            citations=[],
        )

    messages = make_rag_messages(question, history, chunks)

    try:
        answer_text = _generate_answer(messages)
    except Exception as e:
        print(f"[answer] LLM answer generation failed: {e}")
        answer_text = (
            "I found relevant code but couldn't generate an answer due to an API error. "
            "Here are the matched files — check the citations panel for code snippets.\n\n"
            f"**Error:** {str(e)[:200]}"
        )

    citations = _extract_citations(chunks)
    print(f"[answer] Extracted {len(citations)} citations")

    return ChatResponse(answer=answer_text, citations=citations)
