from fastapi import UploadFile, File, BackgroundTasks
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from langchain_community.document_loaders import PDFMinerLoader
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_postgres.vectorstores import PGVector

from typing import cast

from dotenv import load_dotenv

import asyncio
import json
import os
import shutil

load_dotenv()
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")


def get_embedding() -> HuggingFaceEndpointEmbeddings:
    if not EMBEDDING_MODEL_NAME:
        raise ValueError("EMBEDDING_MODEL_NAME is required for vector ingestion")
    return HuggingFaceEndpointEmbeddings(
        huggingfacehub_api_token=HF_TOKEN,
        model=EMBEDDING_MODEL_NAME,
    )


def _save_upload_file(src_file, dst_path: str) -> None:
    with open(dst_path, "wb+") as file_object:
        shutil.copyfileobj(src_file, file_object)

class ItemService:
    def __init__(self) :
        pass
    async def handle_save_upload_file(self ,bg_tasks : BackgroundTasks ,directory : str , uploaded_file : UploadFile = File(...)):
        #save file to target folder
        os.makedirs(directory, exist_ok=True)
        if uploaded_file.filename is None:
            raise ValueError("Uploaded file must have a filename")
        file_location = f"{directory}/{uploaded_file.filename}"
        await asyncio.to_thread(_save_upload_file, uploaded_file.file, file_location)
        # convert to vector
        temp = cast(str,uploaded_file.filename)
        named = os.path.splitext(temp)[0]
        print(named)
        bg_tasks.add_task(self.handle_convert_to_vector,file_location, named)
        return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}' !\n The File is is being processed."}

    async def _load_json_documents(self, file_path: str) -> list[Document]:
        def _read_and_parse() -> object:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        payload = await asyncio.to_thread(_read_and_parse)
        records = payload if isinstance(payload, list) else [payload]
        documents: list[Document] = []

        for record in records:
            if not isinstance(record, dict):
                continue
            content = record.get("content")
            if not isinstance(content, str) or not content.strip():
                continue
            metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
            documents.append(Document(page_content=content.strip(), metadata=metadata))

        if not documents:
            raise ValueError("JSON file does not contain valid 'content' fields")

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        return await asyncio.to_thread(splitter.split_documents, documents)

    async def handle_convert_to_vector(self, file_path : str, file_name : str):
        try:
            # load file
            if file_path.endswith('.pdf'):
                loader = PDFMinerLoader(file_path)
                documents = await asyncio.to_thread(loader.load)
                splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                document_chunks = await asyncio.to_thread(splitter.split_documents, documents)
            elif file_path.endswith('.json'):
                document_chunks = await self._load_json_documents(file_path)
            else:
                raise ValueError("Unsupported file format")

            if not document_chunks:
                raise ValueError("No chunks generated from uploaded file")

            async_connection = os.getenv("A_DATABASE_URL")
            if async_connection is None:
                raise ValueError("A_DATABASE_URL is required for async PGVector operations")

            vector_store = PGVector(
                get_embedding(),
                connection=async_connection,
                collection_name=file_name,
                use_jsonb=True,
                async_mode=True,
                create_extension=False,
            )
            # save to database
            await vector_store.aadd_documents(document_chunks)
            print(f"[INGEST] Imported {len(document_chunks)} chunks into collection '{file_name}'")
        except Exception as exc:
            print(f"[INGEST][ERROR] Failed to process '{file_path}': {exc}")