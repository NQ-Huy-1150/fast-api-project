from pydantic import BaseModel
#Create history
class ChatHistory(BaseModel):
    messages : list[dict] = []
#Return history
class ChatHistoryResponse(BaseModel):
    id : int
    user_id : int
    messages : list[dict] = []
    class Config:
        from_attributes = True
# Update History
class ChatHistoryUpdate(BaseModel):
    id : int
    messages : list[dict] = []
    class Config:
        from_attributes = True