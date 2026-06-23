from fastapi import FastAPI
from routes.chat_routes import router as chat_router
from routes.repo_routes import router as repo_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CodeLens API",
    description="Code Intelligence Backend — Ingest repos, ask questions, get cited answers.",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(repo_router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "CodeLens API",
        "status": "running",
        "version": "0.1.0",
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "endpoints": [
            "POST /repo/ingest",
            "GET /repo/status",
            "POST /chat/ask",
        ],
    }
