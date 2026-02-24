from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str
    model_name: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt" : "Hi ollama",
                    "model_name" : "Ollama3.2"
                }
            ]
        }
    }

class ChatResponse(BaseModel):
    answer: str
    class Config:
        from_attributes = True