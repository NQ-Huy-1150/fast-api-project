import re
import os
import asyncio
from domain.schema.GraphState import GraphState
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Model
model_name = os.getenv("OLLAMA_MODEL")
if model_name is None :
    raise ValueError ("No model found !")
llm = ChatOllama(model=model_name, temperature=0.01)

FALLBACK_TEXT = "Tôi không biết, tôi không có thông tin về nó và không trả lời thêm thông tin nào khác."

def normalize_query(question: str) -> str:
    fillers = [
        r"(?i)\bbạn ơi[,\s]*", r"(?i)\bcho mình hỏi[,\s]*",
        r"(?i)\bcho tôi hỏi[,\s]*", r"(?i)\bnhỉ\b", r"(?i)\bạ\b",
        r"(?i)\bcái\b", r"(?i)\bthế\b", r"(?i)\bvậy\b"
    ]
    for f in fillers:
        question = re.sub(f, " ", question).strip()

    synonyms = {
        r"(?i)văn miếu quốc tử giám": "Văn Miếu Quốc Tử Giám",
        r"(?i)\bvăn miếu\b": "Văn Miếu Quốc Tử Giám",
        r"(?i)\bquốc tử giám\b": "Văn Miếu Quốc Tử Giám",
        r"(?i)\bhồ hoàn kiếm\b": "Hồ Hoàn Kiếm",
        r"(?i)\bhồ gươm\b": "Hồ Hoàn Kiếm",
        r"(?i)\blăng bác\b": "Lăng Chủ tịch Hồ Chí Minh",
        r"(?i)\blăng hồ chủ tịch\b": "Lăng Chủ tịch Hồ Chí Minh"
    }
    for pattern, replacement in synonyms.items():
        question = re.sub(pattern, replacement, question)

    return re.sub(r"\s+", " ", question).strip()

# 2. HẬU XỬ LÝ: Ép văn phong và xử lý từ chối
def may_chem_van_phong(text: str) -> str:
    text = text.replace("<|im_end|>", "").replace("<|im_start|>", "").strip()
    
    tu_choi_keywords = [
        "không có thông tin", "không đề cập", "tôi không biết", 
        "không tìm thấy", "chưa có thông tin", "không trả lời được"
    ]
    if any(kw in text.lower() for kw in tu_choi_keywords):
        return FALLBACK_TEXT

    # Xóa các mào đầu rườm rà
    mao_dau = r"^(Dạ|Vâng|Đúng rồi|Theo tài liệu|Dựa vào ngữ cảnh|Câu trả lời là).*?[:.,\s]+"
    text = re.sub(mao_dau, "", text, flags=re.IGNORECASE).strip()
    
    if len(text) > 0:
        text = text[0].upper() + text[1:]
    return text or FALLBACK_TEXT


class CRAG:
    def __init__(self):
        self.location_map = {
            "hồ hoàn kiếm": "Hồ Hoàn Kiếm", "văn miếu quốc tử giám": "Văn Miếu – Quốc Tử Giám",
            "lăng chủ tịch hồ chí minh": "Lăng Chủ tịch Hồ Chí Minh", "chả cá lã vọng": "Chả cá Lã Vọng",
            "hàng buồm": "Phố Hàng Buồm", "hàng mã": "Phố Hàng Mã", "hàng đào": "Phố Hàng Đào",
            "hàng gai": "Phố Hàng Gai", "hàng bạc": "Phố Hàng Bạc", "hàng hòm": "Phố Hàng Hòm",
            "hàng trống": "Phố Hàng Trống", "hàng ngang": "Phố Hàng Ngang", "hàng đường": "Phố Hàng Đường",
            "hàng mắm": "Phố Hàng Mắm", "hàng nón": "Phố Hàng Nón", "hàng gà": "Phố Hàng Gà"
        }

    def get_chain(self, vector_store):
        
        async def retrieve_node(state: GraphState):
            question = state["question"]
            print(f"\n[RETRIEVE] Tìm kiếm: {question}")
            
            target_location = None
            for key in self.location_map:
                if key in question.lower():
                    target_location = self.location_map[key]
                    break
            
            if target_location:
                print(f"   -> [HYBRID] Lọc theo địa danh: {target_location}")
                docs = await vector_store.asimilarity_search(question, k=5, filter={"dia_diem": target_location})
            else:
                docs = await vector_store.asimilarity_search(question, k=5)
            
            return {
                "documents": docs,
                "question": question,
                "retry_count": state.get("retry_count", 0),
            }

        async def grade_node(state: GraphState):
            print("[GRADE] Đang kiểm tra từng tài liệu bằng LLM...")
            question = state["question"]
            documents = state["documents"]
            
            prompt = PromptTemplate(
                template="""Bạn là một trợ lý kiểm tra dữ liệu. Hãy xem tài liệu có chứa thông tin để trả lời câu hỏi hay không.
Chỉ trả lời "yes" hoặc "no". Không giải thích gì thêm.

Ví dụ 1:
TÀI LIỆU: Hồ Gươm nằm ở trung tâm thủ đô Hà Nội.
CÂU HỎI: Hồ Gươm ở đâu?
TRẢ LỜI: yes

Ví dụ 2:
TÀI LIỆU: Phở là món ăn truyền thống của Việt Nam.
CÂU HỎI: Ai là người xây dựng Văn Miếu?
TRẢ LỜI: no

Bây giờ đến lượt bạn:
TÀI LIỆU: {document}
CÂU HỎI: {question}
TRẢ LỜI:""",
                input_variables=["question", "document"],
            )
            grader_chain = prompt | llm | StrOutputParser()
            
            valid_docs = []
            for doc in documents:
                # Gọi LLM đánh giá từng cái, không tin vào điểm vector
                verdict = await grader_chain.ainvoke({"question": question, "document": doc.page_content})
                if "yes" in verdict.lower():
                    valid_docs.append(doc)
            
            print(f"   -> Giữ lại {len(valid_docs)}/{len(documents)} tài liệu chính xác.")
            return {"documents": valid_docs, "fallback": len(valid_docs) == 0}

        async def rewrite_node(state: GraphState):
            print("[REWRITE] Trích xuất từ khóa cứu hộ...")
            question = state["question"]
            prompt = PromptTemplate(
                template="Trích xuất các danh từ riêng và từ khóa chính để tìm kiếm. Chỉ in từ khóa.\nCâu hỏi: {question}\nTừ khóa:",
                input_variables=["question"]
            )
            keywords = await (prompt | llm | StrOutputParser()).ainvoke({"question": question})
            return {"question": keywords.strip(), "retry_count": state["retry_count"] + 1}

        async def refuse_node(state: GraphState):
            print("[REFUSE] Kích hoạt luật Zero-Hallucination.")
            return {"generation": FALLBACK_TEXT}

        async def generate_node(state: GraphState):
            print("[GENERATE] Đang tổng hợp đáp án...")
            context = "\n\n".join([d.page_content for d in state["documents"]])
            prompt = PromptTemplate(
                template="""Bạn là một NPC hướng dẫn viên du lịch ảo nhiệt tình, am hiểu sâu sắc về văn hóa, lịch sử và địa danh Hà Nội.
Nhiệm vụ của bạn là giải đáp thắc mắc cho du khách một cách tự nhiên dựa trên <ngu_canh> dưới đây.

<ngu_canh>
{context}
</ngu_canh>

<câu_hỏi_của_du_khách>
{question}
</câu_hỏi_của_du_khách>

Hướng dẫn trả lời:
- Hãy trả lời ngắn gọn, lịch sự và chính xác những gì có trong <ngu_canh>.
- TUYỆT ĐỐI KHÔNG tự ý suy diễn hay bịa đặt thông tin không có trong <ngu_canh>.
- Nếu <ngu_canh> không có thông tin, bạn BẮT BUỘC trả lời đúng nguyên văn: "{fallback}"
Trả lời:""",
                input_variables=["context", "question", "fallback"]
            )
            response = await (prompt | llm | StrOutputParser()).ainvoke({
                "context": context, 
                "question": state["original_question"],
                "fallback": FALLBACK_TEXT
            })
            return {"generation": may_chem_van_phong(response)}

        # Xây dựng Workflow
        workflow = StateGraph(GraphState)
        workflow.add_node("retrieve", retrieve_node)
        workflow.add_node("grade", grade_node)
        workflow.add_node("rewrite", rewrite_node)
        workflow.add_node("generate", generate_node)
        workflow.add_node("refuse", refuse_node)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade")
        workflow.add_conditional_edges("grade", 
            lambda x: "rewrite" if x["fallback"] and x["retry_count"] < 1 else ("generate" if not x["fallback"] else "refuse"),
            {"rewrite": "rewrite", "generate": "generate", "refuse": "refuse"}
        )
        # Sau khi rewrite phải retrieve lại tài liệu mới trước khi grade.
        workflow.add_edge("rewrite", "retrieve")
        workflow.add_edge("generate", END)
        workflow.add_edge("refuse", END)
        
        app = workflow.compile()

        async def run(user_input: str):
            clean_q = normalize_query(user_input)
            initial_state: GraphState = {
                "question": clean_q,
                "original_question": clean_q,
                "documents": [],
                "generation": "",
                "fallback": False,
                "retry_count": 0,
            }
            final = await app.ainvoke(initial_state)
            return final.get("generation", FALLBACK_TEXT)

        return RunnableLambda(run)