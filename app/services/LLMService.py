import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, messages_from_dict, messages_to_dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import cast
from repositories.LLMRepository import LLMRepository
from domain.schema.Ai import ChatRequest
from fastapi import Depends
from domain.schema.ChatHistory import ChatHistoryUpdate
from dotenv import load_dotenv
load_dotenv()
#LLM
model_name = os.getenv("OLLAMA_MODEL")
if model_name is None:
    raise ValueError ("No model name found !")
llm = ChatOllama(model=model_name, temperature=0.01)
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
    async def ask(self, user_id: int, chat_id: int ,request: ChatRequest):
        orm_obj = await self.get_chat_history_by_id(chat_id)
        if not orm_obj or cast(int, orm_obj.user_id) != user_id:
            return "Chat history not exist!"

        # Bước 1: Chuyển từ JSON (List[dict]) sang LangChain Objects
        chat_history = messages_from_dict(cast(list, orm_obj.messages))

        # Bước 2: Gọi AI
        response = await chain.ainvoke({"input": request.prompt, "chat_history": chat_history})

        # Bước 3: Cập nhật lịch sử (Thêm tin nhắn mới)
        chat_history.append(HumanMessage(content=request.prompt))
        chat_history.append(response)

        # Bước 4: Chuyển ngược từ LangChain Objects sang JSON để lưu vào DB
        updated_messages = messages_to_dict(chat_history)
        # Bước 5: Lưu thông qua Repo với đúng type ChatHistoryUpdate
        history_update = ChatHistoryUpdate(id=cast(int, orm_obj.id), messages=updated_messages)
        await self.repo.update_chat_history(history_update)
        # Bước 6: In câu trả lời ra console để debug
        print(response.content)
        return response.content
    async def get_create_chat(self, user_id : int):
        return await self.repo.create_chat_history(user_id)
    async def get_all_chat_history_by_user_id (self,user_id : int):
        return await self.repo.find_by_user_id(user_id)
    async def get_update_chat_history(self, history: ChatHistoryUpdate):
        return await self.repo.update_chat_history(history)
    async def is_chat_history_with_user_id_exist(self, user_id : int, chat_id : int):
        return await self.repo.exist_by_chat_history_and_user_id(chat_id, user_id)
    async def get_chat_history_by_id(self, id: int):
        return await self.repo.find_by_id(id)

