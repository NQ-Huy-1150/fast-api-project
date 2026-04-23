from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from services.ItemService import ItemService
router = APIRouter()
@router.post("/upload_file")
async def get_pdf_or_json(bg_task : BackgroundTasks ,file : UploadFile = File(...), service : ItemService = Depends()):
    return await service.handle_save_upload_file(bg_task,"./resources",file)