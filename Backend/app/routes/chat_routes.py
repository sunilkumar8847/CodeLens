from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from services.answer_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/ask", response_model=ChatResponse)
async def ask_question(req: ChatRequest)-> ChatResponse:
    return answer_question(req.question, req.history)

