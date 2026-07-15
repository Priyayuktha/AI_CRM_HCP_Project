import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.langgraph.nodes import reset_conversation_memory
from app.langgraph.workflow import graph

router = APIRouter(prefix="/chat", tags=["AI Chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(request: ChatRequest):
    try:
        state = graph.invoke(
            {
                "user_input": request.message
            }
        )

        return state["response"]
    except Exception as exc:
        logger.exception("Chat processing failed")
        return {
            "success": False,
            "tool": "crm",
            "tool_used": "crm",
            "intent": "crm",
            "extracted_data": {},
            "missing_fields": [],
            "result": {
                "status": "not_found",
                "message": "Something went wrong. Please try again.",
            },
            "database_result": {
                "status": "not_found",
                "message": "Something went wrong. Please try again.",
            },
            "message": "Something went wrong. Please try again.",
        }


@router.post("/reset")
def reset_chat():
    reset_conversation_memory()
    return {"success": True}
