from fastapi import UploadFile, File, BackgroundTasks
from langchain_ollama import OllamaEmbeddings

from langchain_community.document_loaders import PDFMinerLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_postgres.vectorstores import PGVector

from typing import cast

from dotenv import load_dotenv

import os
import shutil

load_dotenv()

class ItemService:
    def __init__(self) :
        pass
    def handle_save_upload_file(self ,bg_tasks : BackgroundTasks ,directory : str , uploaded_file : UploadFile = File(...)):
        #save file to target folder
        os.makedirs(directory, exist_ok=True)
        file_location = f"{directory}/{uploaded_file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(uploaded_file.file, file_object)
        # convert to vector
        # remove dot "." from collection_name to fix api critical bug
        temp = cast(str,uploaded_file.filename)
        length = len(temp)
        named = cast(str, temp[0:length - 4])
        print(named)
        bg_tasks.add_task(self.handle_convert_to_vector,file_location, named)
        return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}' !\n The File is is being processed."}
    def handle_convert_to_vector(self, file_path : str, file_name : str):
        # load file
        loader = PDFMinerLoader(file_path)
        documents = loader.load()
        # create chunk
        splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
        document_chunks = splitter.split_documents(documents)
        embedding = OllamaEmbeddings(model="llama3.2")
        # save to database
        PGVector.from_documents(
            document_chunks, embedding, connection=os.getenv("DATABASE_URL"), collection_name= file_name, use_jsonb= True)