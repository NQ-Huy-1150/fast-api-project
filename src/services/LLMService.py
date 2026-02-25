from langchain_ollama import ChatOllama
from langchain_classic.chains import history_aware_retriever
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from repositories.LLMRepository import LLMRepository
from domain.schema.Ai import ChatRequest
from fastapi import Depends
llm = ChatOllama(model="llama3.2")
chat_history = []
prompt_template = ChatPromptTemplate.from_messages(
    [
    (
        "system",
        "You are an AI named Llama, a helpful assistant, Answer the user question simple and wisely.",
    ),
    MessagesPlaceholder(variable_name = "chat_history"),
    ("human", "{input}"),
    ]
)
chain = prompt_template | llm
class AIService:
    def __init__(self, repo : LLMRepository = Depends()):
        self.repo = repo
    async def ask(self, request: ChatRequest):
        response = await chain.ainvoke({"input": request.prompt, "chat_history": chat_history})
        chat_history.append(HumanMessage(content=request.prompt))
        chat_history.append(response)
        print(f"AI: {response.content}")
        return response.content

