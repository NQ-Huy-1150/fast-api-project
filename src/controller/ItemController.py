from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from services.ItemService import ItemService
router = APIRouter()
@router.post("/pdf")
async def get_pdf(bg_task : BackgroundTasks ,file : UploadFile = File(...), service : ItemService = Depends()):
    return service.handle_save_upload_file(bg_task,"./resources",file)