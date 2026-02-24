from langchain_ollama import ChatOllama
from repositories.LLMRepository import LLMRepository
from domain.schema.Ai import ChatRequest
from fastapi import Depends
class AIService:
    def __init__(self, repo : LLMRepository = Depends()):
        self.repo = repo
        self.llm = ChatOllama(model="llama3.2", temperature=0.5)
    async def ask(self, request: ChatRequest):
        messages = [
        (
            "system",
            "You are a helpful assistant, Answer the user question wisely",
        ),
        ("human", request.prompt),
        ]
        generated = await self.llm.ainvoke(messages)
        aiAnswer = generated.content
        return aiAnswer
