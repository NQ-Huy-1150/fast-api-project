from fastapi import UploadFile, File
import os
class ItemService:
    def __init__(self) :
        pass
    def handle_save_upload_file(self ,directory : str , uploaded_file : UploadFile = File(...)):
        os.makedirs(directory, exist_ok=True)
        file_location = f"{directory}/{uploaded_file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(uploaded_file.file.read())
        return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}'"}