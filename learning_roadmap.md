# How to Understand & Rebuild CodeLens — A Learning Roadmap

You already understand RAG in a notebook. Now you need to understand it as a **real application**. Here's the mental shift and the exact path to follow.

---

## The Core Mental Model

In a notebook, RAG looks like this:

```
Cell 1: Load documents
Cell 2: Split into chunks  
Cell 3: Create embeddings → store in vector DB
Cell 4: User asks question → search vector DB → get relevant chunks
Cell 5: Stuff chunks into prompt → call LLM → get answer
```

In a production app, **each cell becomes a service**, and **a web server connects them to a user**:

```
Cell 1  →  parser_service.py + git_utils.py + file_utils.py
Cell 2  →  chunk_service.py
Cell 3  →  embedding_service.py + vector_store.py
Cell 4  →  retrieval_service.py
Cell 5  →  answer_service.py

The notebook itself  →  repo_service.py (runs cells 1-3 in order)
The "Run" button     →  FastAPI routes (main.py + routes/)
The UI               →  Gradio frontend (app.py)
```

That's it. There's nothing magical here. It's the same 5 steps, just organized into separate files.

---

## Phase 0: Understand Before You Build

Before writing any code, **read** the original CodeLens in this exact order. Don't read alphabetically — follow the data flow.

### Reading Order

| Order | File | What to focus on | Notebook equivalent |
|-------|------|-----------------|---------------------|
| 1 | `config.py` | What models, what chunk size, what paths | The first cell where you set variables |
| 2 | `models/schemas.py` | What does a "chunk" look like? What does the API accept/return? | Your data structures |
| 3 | `main.py` | How does the server start? How are routes plugged in? | *New concept* — no notebook equivalent |
| 4 | `routes/repo_routes.py` | What URL triggers ingestion? | *New concept* — the "Run" button |
| 5 | `routes/chat_routes.py` | What URL triggers a question? | *New concept* — the "Run" button |
| 6 | `services/repo_service.py` | **READ THIS CAREFULLY** — it's your entire notebook's ingestion flow in one function | Your notebook cells 1-3 in order |
| 7 | `utils/git_utils.py` | How do we download code? | Cell 1 (load data) |
| 8 | `utils/file_utils.py` | How do we filter files? | Cell 1 (load data) |
| 9 | `services/parser_service.py` | How do we read file contents? | Cell 1 (load data) |
| 10 | `services/chunk_service.py` | How do we split code? | Cell 2 (chunking) |
| 11 | `services/embedding_service.py` | How do we embed + store? | Cell 3 (embeddings) |
| 12 | `storage/vector_store.py` | How does ChromaDB work? | Cell 3 (vector DB) |
| 13 | `services/retrieval_service.py` | How do we search? | Cell 4 (retrieval) |
| 14 | `services/answer_service.py` | How do we generate the answer? | Cell 5 (generation) |
| 15 | `Frontend/app.py` | How does the UI talk to the backend? | *New concept* — no notebook equivalent |

### While reading each file, ask yourself:
1. **What is the INPUT to this file?** (What data comes in?)
2. **What is the OUTPUT?** (What does it return?)
3. **What is the ONE job this file does?** (It should be one sentence)
4. **Which other files does it call?** (Follow the imports)

---

## Phase 1: The Skeleton (You're here! ✅)

**Goal:** A server that responds to HTTP requests with fake data.

**What you're building:**
```
Backend/
├── app/
│   ├── main.py          ← FastAPI server + CORS + health checks
│   └── chat_routes.py   ← Fake /chat/ask endpoint
```

**What you should have working:**
- Visit `http://localhost:8000/` → see `{"status": "running"}`
- Visit `http://localhost:8000/docs` → see the interactive docs
- POST to `/chat/ask` → get `{"message": "Hello from chat!"}`

**What you're learning:**
- How FastAPI works (decorators, routers, CORS)
- How to split routes into separate files
- How `uvicorn` serves your app

> [!TIP]
> You've already done this! Your `main.py` and `chat_routes.py` are working. Move to Phase 2.

### Phase 1 checklist before moving on:
- [ ] Server starts without errors
- [ ] `http://localhost:8000/docs` shows your endpoints
- [ ] You can POST to `/chat/ask` from the docs page

---

## Phase 2: Accept Real Input

**Goal:** Make your endpoints accept structured data (not just return hardcoded responses).

**New files to create:**
```
app/
├── models/
│   └── schemas.py       ← Pydantic models for request/response
├── routes/
│   ├── chat_routes.py   ← Now accepts a question
│   └── repo_routes.py   ← Accepts a GitHub URL (still fake)
```

**What to build in `schemas.py`:**
```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    history: list[dict] = []

class ChatResponse(BaseModel):
    answer: str
    citations: list = []

class RepoIngestRequest(BaseModel):
    repo_url: str
```

**Update `chat_routes.py`:**
```python
@router.post("/ask")
async def ask_question(request: ChatRequest):
    # Still fake, but now it echoes the real question
    return ChatResponse(
        answer=f"You asked: {request.question}. I don't have a brain yet!",
        citations=[]
    )
```

**What you're learning:**
- Pydantic validation (if someone sends bad data, FastAPI auto-rejects it)
- Request/Response contracts
- Why separating "data shape" from "logic" matters

### Phase 2 checklist:
- [ ] POST to `/chat/ask` with `{"question": "hello"}` → get an echo response
- [ ] POST to `/chat/ask` with `{}` (no question) → get a validation error automatically
- [ ] POST to `/repo/ingest` with `{"repo_url": "https://github.com/..."}` → get a fake success

---

## Phase 3: Clone & Read a Real Repo

**Goal:** When the user submits a GitHub URL, actually download and read the files.

**New files:**
```
app/
├── utils/
│   ├── git_utils.py     ← Clone a repo with subprocess
│   └── file_utils.py    ← Walk the directory, filter files
├── services/
│   └── parser_service.py ← Read file contents into dicts
```

**Build order:**
1. `git_utils.py` first — write `clone_repo()`, test it by cloning a small repo and printing the path
2. `file_utils.py` next — write `list_repo_files()`, test it by printing all filenames
3. `parser_service.py` — combine them, return a list of `{source, text, language}` dicts

**Test it:** Add a temporary print in your `/repo/ingest` route:
```python
documents = parse_repo(clone_repo(request.repo_url))
print(f"Found {len(documents)} files")
for doc in documents[:3]:
    print(f"  {doc['source']} ({doc['language']}) — {len(doc['text'])} chars")
```

**What you're learning:**
- How to go from "paste text in notebook" to "download code from the internet"
- File filtering (why you skip `node_modules`, lock files, images)
- This is your notebook's **Cell 1** — but for real code, not sample PDFs

### Phase 3 checklist:
- [ ] Ingesting a small repo prints the correct number of files
- [ ] `.git` folder is NOT included
- [ ] `node_modules` / `__pycache__` are NOT included
- [ ] Binary files (images, etc.) are NOT included

---

## Phase 4: Chunk the Code

**Goal:** Split those files into small, searchable pieces.

**New file:**
```
app/
├── services/
│   └── chunk_service.py  ← LangChain text splitters
```

**What to build:**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

def create_chunks(documents):
    chunks = []
    for doc in documents:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,  # pick based on doc["language"]
            chunk_size=1000,
            chunk_overlap=200,
        )
        raw_chunks = splitter.split_text(doc["text"])
        for chunk_text in raw_chunks:
            chunks.append({"text": chunk_text, "source": doc["source"], ...})
    return chunks
```

**Test it:** Print the first 3 chunks. Check: does a Python function stay in one chunk? Are chunks roughly 1000 chars?

**What you're learning:**
- This is your notebook's **Cell 2** — but using code-aware splitters instead of `CharacterTextSplitter`
- Why `from_language(Language.PYTHON)` is better — it splits on `def` and `class` boundaries
- Why overlap matters (a function call at the end of chunk 1 also appears at the start of chunk 2)

### Phase 4 checklist:
- [ ] A 50-line Python function stays in one chunk (not split in the middle)
- [ ] Each chunk is roughly 800-1200 characters
- [ ] Chunk metadata includes the original file path

---

## Phase 5: Embed & Store (The Vector DB)

**Goal:** Convert chunks to vectors and store them in ChromaDB.

**New files:**
```
app/
├── services/
│   └── embedding_service.py  ← HuggingFace embeddings
├── storage/
│   └── vector_store.py       ← ChromaDB wrapper
```

**Build order:**
1. `vector_store.py` first — initialize ChromaDB, write `add_to_collection()` and `query_collection()`
2. `embedding_service.py` next — load the HuggingFace model, embed chunks, call vector_store to save

**Test it:** After ingesting, query ChromaDB directly with a test question:
```python
results = query_collection(embed_query("authentication"), n_results=3)
for r in results:
    print(r.metadata["source"], r.page_content[:100])
```

Do the results make sense? If you search for "authentication", do you get auth-related files?

**What you're learning:**
- This is your notebook's **Cell 3** — same ChromaDB, same embeddings, just in separate files
- Lazy loading pattern (load the model once, reuse it)
- The abstraction pattern — `vector_store.py` hides ChromaDB details so you could swap to FAISS later

### Phase 5 checklist:
- [ ] After ingestion, ChromaDB has the correct number of chunks
- [ ] Querying with a relevant term returns relevant code chunks
- [ ] Re-ingesting the same repo clears old data first (not duplicated)

---

## Phase 6: Retrieval & Answer (The RAG Core)

**Goal:** When the user asks a question, find relevant code and generate an answer.

**New files:**
```
app/
├── services/
│   ├── retrieval_service.py  ← Search the vector DB
│   └── answer_service.py     ← Build prompt + call LLM
```

**Build order:**
1. `retrieval_service.py` — start simple: just embed the question and search ChromaDB. Don't add query rewriting yet.
2. `answer_service.py` — build the RAG prompt, call the LLM, return the answer.

**Start with the simplest possible retrieval:**
```python
def fetch_context(question):
    query_vector = embed_query(question)
    return query_collection(query_vector, n_results=5)
```

**Start with the simplest possible answer:**
```python
def answer_question(question):
    chunks = fetch_context(question)
    context = "\n\n".join(c.page_content for c in chunks)
    prompt = f"Answer based on this code:\n{context}\n\nQuestion: {question}"
    response = completion(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content
```

**Test it:** Ask "What does this project do?" — does the answer reference real files?

**What you're learning:**
- This is your notebook's **Cell 4 + Cell 5** — retrieval + generation
- The SYSTEM_PROMPT matters enormously — it controls whether the LLM hallucinates or cites files
- Why you return citations (the chunk metadata already has the file paths!)

### Phase 6 checklist:
- [ ] Ask a question → get a real answer mentioning real files
- [ ] The answer doesn't make up files that don't exist
- [ ] The citations panel shows the correct source files

---

## Phase 7: Advanced Upgrades (Only After Phase 6 Works!)

Once the basic RAG works end-to-end, **then** add these one at a time:

| Upgrade | What it does | Why it helps |
|---------|-------------|-------------|
| Query rewriting | LLM rewrites "how does auth work?" → "JWT middleware login function" | Better vector search matches |
| Conversation history | Pass previous Q&A to the LLM | The LLM can handle follow-up questions |
| File citations panel | Extract `metadata["source"]` from chunks, show snippets | User can verify the answer |
| Retry with backoff | Wrap LLM calls in `@retry` | Handles API rate limits gracefully |
| Progress indicator | Show "Processing..." in the UI during ingestion | Better user experience |

> [!IMPORTANT]
> **Add ONE upgrade at a time.** Test it. Make sure it works. Then add the next one. If you add them all at once and something breaks, you won't know what caused it.

---

## The Golden Rule

**Every RAG app in the world follows the same 5 steps:**

```
1. LOAD    → Get the data (files, PDFs, web pages, databases)
2. CHUNK   → Split it into pieces
3. EMBED   → Convert pieces to vectors
4. SEARCH  → Find the relevant pieces for a question
5. ANSWER  → Give the pieces to an LLM to generate an answer
```

The only things that change between apps are:
- **What** you're loading (code vs PDFs vs web pages)
- **How** you chunk (by function vs by paragraph vs by page)
- **Which** embedding model and vector DB you use
- **How clever** your retrieval is (simple search vs rewrite vs rerank)
- **What** your system prompt says

Master these 5 steps in CodeLens, and you can build RAG over **anything**.
