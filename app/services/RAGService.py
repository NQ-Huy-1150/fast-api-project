import os
from langchain_ollama import ChatOllama ,OllamaEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, messages_from_dict, messages_to_dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import cast
from repositories.RAGRepository import RAGRepository
from domain.schema.Ai import ChatRequest
from fastapi import Depends, HTTPException
from domain.schema.RagChatHistory import ChatHistoryUpdate
from langchain_postgres.vectorstores import PGVector
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
load_dotenv()
# RAG define
llm = ChatOllama(model="llama3.2")
prompt_template = ChatPromptTemplate.from_messages(
    [
    (
        "system", # ràng buộc chặt chẽ hơn
        "You MUST only answer using the provided context below. "
        "If the answer is not found in the context, respond ONLY with: "
        "'I don't have information about this in the provided documents.' "
        "Do NOT use any external knowledge.\n\nContext: {context}",
    ),
    MessagesPlaceholder(variable_name = "chat_history"),
    ("human", "{input}"),
    ]
)
embedding = OllamaEmbeddings(model="llama3.2")
question_answer_chain = create_stuff_documents_chain(llm, prompt_template)

class RagService:
    _retriever_cache = {}
    def __init__(self, repo : RAGRepository = Depends()):
        self.repo = repo
    async def get_retriever (self, collection_name : str) :
        if collection_name in self._retriever_cache:
            return self._retriever_cache[collection_name]
        async_connection = os.getenv("A_DATABASE_URL")
        if async_connection is None:
            raise ValueError("A_DATABASE_URL is required for async PGVector operations")

        vector = PGVector(
            embedding,
            connection=async_connection,
            collection_name=collection_name,
            async_mode=True,
            create_extension=False,
        )
        retriever = vector.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        self._retriever_cache[collection_name] = retriever
        return retriever
    
    async def ask(self, user_id: int, chat_id: int, collection_name: str, request: ChatRequest):
        if not await self.repo.exist_by_collecton_name(collection_name):
            raise HTTPException(status_code=404, detail="Collection or document name not found !")

        orm_obj = await self.get_chat_history_by_id(chat_id)
        if not orm_obj or cast(int, orm_obj.user_id) != user_id:
            raise HTTPException(status_code=404, detail="Chat history not found !")

        retriever = await self.get_retriever(collection_name)
        chain = create_retrieval_chain(retriever, question_answer_chain)
        chat_history = messages_from_dict(cast(list, orm_obj.messages))
        response = await chain.ainvoke({
            "input": request.prompt,
            "chat_history": chat_history
        })

        chat_history.append(HumanMessage(content=request.prompt))
        chat_history.append(AIMessage(content=response["answer"]))
        updated_messages = messages_to_dict(chat_history)
        history_update = ChatHistoryUpdate(id=cast(int, orm_obj.id), messages=updated_messages)
        await self.repo.update_chat_history(history_update)
        print(str(response["answer"]))
        return str(response["answer"])

    async def get_create_chat(self, user_id : int):
        return await self.repo.create_chat_history(user_id)
    async def get_chat_history_by_user_id (self,user_id : int):
        return await self.repo.find_by_user_id(user_id)
    async def get_update_chat_history(self, history: ChatHistoryUpdate):
        return await self.repo.update_chat_history(history)
    async def is_chat_history_with_user_id_exist(self, user_id : int, chat_id : int):
        return await self.repo.exist_by_chat_history_and_user_id(chat_id, user_id)
    async def get_chat_history_by_id(self, id: int):
        return await self.repo.find_by_id(id)

