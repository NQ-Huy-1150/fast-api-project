import os
import re
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, messages_from_dict, messages_to_dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
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
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")
if EMBEDDING_MODEL_NAME is None :
    raise ValueError("No embedding model found !")

prompt_template = ChatPromptTemplate.from_messages(
    [
    (
        "system", # ràng buộc chặt chẽ hơn
        "Bạn là một hướng dẫn viên du lịch ảo tại Hà Nội. BẠN BỊ CẤM SỬ DỤNG KIẾN THỨC BÊN NGOÀI.\n"
        "Chỉ được phép trả lời dựa trên nội dung trong phần <ngu_canh> dưới đây.\n\n"
        "<ngu_canh>\n{context}\n</ngu_canh>\n\n"
        "QUY TẮC BẮT BUỘC: Nếu thông tin không có trong <ngu_canh>, TUYỆT ĐỐI KHÔNG TỰ BỊA ĐẶT mà hãy trả lời nguyên văn: "
        "'Tôi không biết, tôi không có thông tin về nó và không trả lời thêm thông tin nào khác'.",
    ),
    MessagesPlaceholder(variable_name = "chat_history"),
    ("human", "{input}"),
    ]
)
embedding = HuggingFaceEndpointEmbeddings(huggingfacehub_api_token=HF_TOKEN, model=EMBEDDING_MODEL_NAME)
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
            search_kwargs={"k": 3}
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
    
    #crag section
    def normalize_query(self, input: str) -> str:
        question = input.strip()
        synonyms = {
            r"(?i)\bho guom | hồ hoàn kiếm | ho hoan kiem\b": "Hồ Hoàn Kiếm",
            r"(?i)\blăng bác | lang bac | lăng hồ chủ tịch | lang ho chu tich | lăng chủ tịch | lang chu tich\b": "Lăng Chủ tịch Hồ Chí Minh",
            r"(?i)\bvăn miếu | van mieu | quốc tử giám | quoc tu giam | van mieu quoc tu giam\b": "Văn Miếu Quốc Tử Giám",
            r"(?i)\bhoả lò | hoa lo | nhà tù hoả lò | nha tu hoa lo | di tích hoả lò | di tich hoa lo\b": "Di tích lịch sử Nhà tù Hỏa Lò",
            r"(?i)\bcột cờ | cot co\b": "Cột cờ Hà Nội",
            r"(?i)\bhoàng thành | hoang thanh | thành thăng long | thanh thang long | thăng long | thang long\b": "Hoàng thành Thăng Long",
            r"(?i)\b36 pho phuong | 36 phuong | 36 phường | pho phuong | phố phường\b": "36 phố phường",
            r"(?i)\bphố cổ | pho co | khu phố cổ | khu pho co | phố cổ hà nội | pho co ha noi\b": "Khu phố cổ Hà Nội"
        }
        # Duyệt qua từ điển và thay thế
        for pattern, replacement in synonyms.items():
            question = re.sub(pattern, replacement, input)
        # Cập nhật lại câu hỏi đã được "dịch" ra tên chuẩn
        print(f"\n[TIỀN XỬ LÝ] Câu hỏi sau chuẩn hoá: '{question}'")
        return question

    

    async def get_create_chat(self, user_id : int):
        return await self.repo.create_chat_history(user_id)
    async def get_chat_histories_by_user_id (self,user_id : int):
        return await self.repo.find_by_user_id(user_id)
    async def get_update_chat_history(self, history: ChatHistoryUpdate):
        return await self.repo.update_chat_history(history)
    async def is_chat_history_with_user_id_exist(self, user_id : int, chat_id : int):
        return await self.repo.exist_by_chat_history_and_user_id(chat_id, user_id)
    async def get_chat_history_by_id(self, id: int):
        return await self.repo.find_by_id(id)
    async def get_delete (self, id : int) :
        return await self.repo.delete_by_id(id)

