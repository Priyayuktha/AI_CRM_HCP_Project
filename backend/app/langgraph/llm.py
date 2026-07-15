from langchain_groq import ChatGroq

from app.config import get_settings

settings = get_settings()

llm = ChatGroq(
    model=settings.groq_model,
    api_key=settings.groq_api_key,
    temperature=0,
)