from fastapi import UploadFile, File, BackgroundTasks
from langchain_ollama import OllamaEmbeddings

from langchain_community.document_loaders import PDFMinerLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_postgres.vectorstores import PGVector

from typing import cast

from dotenv import load_dotenv

import asyncio
import os
import shutil

load_dotenv()


def _save_upload_file(src_file, dst_path: str) -> None:
    with open(dst_path, "wb+") as file_object:
        shutil.copyfileobj(src_file, file_object)

class ItemService:
    def __init__(self) :
        pass
    async def handle_save_upload_file(self ,bg_tasks : BackgroundTasks ,directory : str , uploaded_file : UploadFile = File(...)):
        #save file to target folder
        os.makedirs(directory, exist_ok=True)
        file_location = f"{directory}/{uploaded_file.filename}"
        await asyncio.to_thread(_save_upload_file, uploaded_file.file, file_location)
        # convert to vector
        temp = cast(str,uploaded_file.filename)
        length = len(temp)
        named = cast(str, temp[0:length - 4])
        print(named)
        bg_tasks.add_task(self.handle_convert_to_vector,file_location, named)
        return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}' !\n The File is is being processed."}
    async def handle_convert_to_vector(self, file_path : str, file_name : str):
        # load file
        loader = PDFMinerLoader(file_path)
        documents = await asyncio.to_thread(loader.load)
        # create chunk
        splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
        document_chunks = await asyncio.to_thread(splitter.split_documents, documents)
        embedding = OllamaEmbeddings(model="llama3.2")
        async_connection = os.getenv("A_DATABASE_URL")
        if async_connection is None:
            raise ValueError("A_DATABASE_URL is required for async PGVector operations")

        vector_store = PGVector(
            embedding,
            connection=async_connection,
            collection_name=file_name,
            use_jsonb=True,
            async_mode=True,
            create_extension=False,
        )
        # save to database
        await vector_store.aadd_documents(document_chunks)