from fastapi import APIRouter, UploadFile, File, Depends
from services.ItemService import ItemService
router = APIRouter()
@router.post("/pdf")
async def get_pdf(file : UploadFile = File(...), service : ItemService = Depends()):
    return service.handle_save_upload_file("./resources",file)