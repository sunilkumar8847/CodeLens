from fastapi import APIRouter
from models.schemas import RepoIngestRequest, RepoIngestResponse, RepoStatusResponse
# from utils.git_utils import clone_repo
# from services.parser_service import parse_repo
# from services.chunk_service import create_chunks
# from services.embedding_service import create_embedding
from services.repo_service import get_current_repo_status, ingest_repo

router = APIRouter(prefix="/repo", tags=["Repository"])

@router.post("/ingest", response_model=RepoIngestResponse)
# @router.post("/ingest")
async def ingest_repository(req: RepoIngestRequest):
    result = ingest_repo(req.repo_url)
    return RepoIngestResponse(**result)

@router.get("/status", response_model=RepoStatusResponse)
async def repo_status():
    result = get_current_repo_status()
    return RepoStatusResponse(**result)
