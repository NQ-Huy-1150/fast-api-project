from typing import List, TypedDict, Any
class GraphState(TypedDict):
    question:    str
    documents:   List[Any]
    scores:      List[float]
    chat_history: List[Any]
    generation:  str
    fallback:    bool
    retry_count: int