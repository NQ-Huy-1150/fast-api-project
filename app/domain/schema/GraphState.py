from typing import List, TypedDict, Any
class GraphState(TypedDict):
    question: str
    original_question: str
    documents: List[Any]
    generation: str
    fallback: bool
    retry_count: int
