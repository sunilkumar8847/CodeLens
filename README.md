# CodeLens

CodeLens is a code intelligence assistant that ingests GitHub repositories and allows you to ask questions about the codebase with accurate file citations and code snippets.

It consists of a **FastAPI Backend** (for repo ingestion, vector storage, and RAG answer generation) and a **Gradio Frontend** (for a simple web UI).

## Prerequisites
- Python 3.10+
- Git installed on your system (for cloning repositories)

## 1. Setup Environment and API Keys

The project requires a `.env` file with your API keys. Ensure you have the `.env` file located either at the root of `llm_engineering` or `week5/CodeLens/`.

Required keys:
```
GROQ_API_KEY=your_groq_api_key
```
(By default, the project uses `groq/openai/gpt-oss-120b` via the Groq API).

## 2. Install Dependencies

Navigate to the `week5/CodeLens/Backend` directory and install the required Python packages:

```bash
cd "week5/CodeLens/Backend"
pip install -r requirements.txt
```
*(It is highly recommended to use a virtual environment).*

## 3. Run the Backend (FastAPI)

The backend handles the RAG pipeline, LLM interactions, and ChromaDB vector storage. It must be running for the frontend to work.

From the `week5/CodeLens/Backend` directory, start the FastAPI server:

```bash
cd "week5/CodeLens/Backend"
uvicorn app.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`. You can view the API documentation at `http://localhost:8000/docs`.

## 4. Run the Frontend (Gradio)

The frontend is a simple Gradio web interface. Open a **new terminal window/tab**, navigate to the `Frontend` directory, and start the app:

```bash
cd "week5/CodeLens/Frontend"
python app.py
```

The Gradio UI will launch automatically in your browser (typically at `http://127.0.0.1:7860`).

## Usage Instructions
1. **Ingest a Repository:** Open the Gradio UI, go to the **📦 Ingest Repository** tab, paste a public GitHub URL (e.g., `https://github.com/pallets/flask`), and click **Ingest**. Wait for the process to complete.
2. **Ask Questions:** Switch to the **💬 Ask Questions** tab, type a question about the code, and get answers with citations and code snippets.
