from src.utils.GeminiService import GeminiService
from src.utils.PineconeService import PineconeService
from src.utils.RecommendService import RecommendService
from src.utils.Timer import Timer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class JobController:

    def __init__(self, debug=False):
        self.geminiService = GeminiService()
        self.pineconeService = PineconeService()
        self.recommendService = RecommendService()
        self.debug = debug
        
        # Khởi tạo LLM
        self.llmModel = "models/gemini-2.5-flash"
        self.llm = ChatGoogleGenerativeAI(
            model=self.llmModel, 
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Template cho câu trả lời
        self.promptTemplate = """
            Bạn là trợ lý AI của ứng dụng GoodJob - giúp người dùng tìm công việc phù hợp.
            
            QUY TẮC:
            - Trả lời bằng TIẾNG VIỆT tự nhiên, thân thiện
            - Chọn TỐI ĐA 3 công việc PHÙ HỢP NHẤT từ danh sách
            - Có thể chọn 1, 2 hoặc 3 công việc tuỳ độ phù hợp
            - Nêu rõ: loại dịch vụ, giá, thời gian, địa điểm
            - Sắp xếp theo độ phù hợp (công việc đầu tiên là phù hợp nhất)
            - BẮT BUỘC: Khi giới thiệu mỗi công việc, PHẢI ghi rõ [JobID: XXX] ở đầu mỗi công việc
            - Nếu không có công việc phù hợp, trả lời lịch sự
            
            Câu hỏi của người dùng: {query}
            
            Danh sách công việc tìm được (tối đa 3):
            {jobs_context}
            
            Hãy chọn và giới thiệu các công việc PHÙ HỢP NHẤT (1-3 công việc) một cách tự nhiên.
            QUAN TRỌNG: Mỗi công việc PHẢI bắt đầu bằng [JobID: XXX]:
        """
        
        self.customPrompt = PromptTemplate(
            input_variables=["query", "jobs_context"],
            template=self.promptTemplate
        )

    # --------------------------------------------------------------

    def _format_jobs_context(self, jobs):
        """Format danh sách jobs thành context cho LLM"""
        if not jobs:
            return "Không tìm thấy công việc nào."
        
        context_parts = []
        for idx, job in enumerate(jobs, 1):
            service_type_map = {
                "CLEANING": "Dọn dẹp vệ sinh",
                "HEALTHCARE": "Chăm sóc sức khỏe",
                "MAINTENANCE": "Bảo trì thiết bị"
            }
            
            service_name = service_type_map.get(job.get("serviceType", ""), job.get("serviceType", ""))
            price = job.get("price", "Chưa có")
            location = job.get("location", "Chưa rõ")
            start_time = job.get("startTime", "Chưa rõ")
            list_days = job.get("listDays", [])
            days_text = ", ".join(list_days) if list_days else "Chưa rõ"
            job_id = job.get("jobID", "")
            
            job_text = f"""
Công việc {idx} [JobID: {job_id}]:
- Loại dịch vụ: {service_name}
- Giá: {price} VNĐ
- Địa điểm: {location}
- Thời gian bắt đầu: {start_time}
- Các ngày làm việc: {days_text}
"""
            context_parts.append(job_text.strip())
        
        return "\n\n".join(context_parts)

    # --------------------------------------------------------------

    def _extract_job_ids_from_answer(self, answer):
        """Trích xuất các JobID mà LLM đã đề cập trong câu trả lời"""
        import re
        # Tìm tất cả pattern [JobID: XXX] hoặc JobID: XXX
        pattern = r'\[?JobID:\s*([^\]]+)\]?'
        matches = re.findall(pattern, answer, re.IGNORECASE)
        # Clean và return unique job IDs
        job_ids = [match.strip() for match in matches]
        return list(set(job_ids))  # Remove duplicates

    # --------------------------------------------------------------

    def _send_to_llm(self, query, jobs):
        """Gửi context và query tới LLM để tạo câu trả lời tự nhiên"""
        jobs_context = self._format_jobs_context(jobs)
        prompt = self.customPrompt.format(query=query, jobs_context=jobs_context)
        response = self.llm.invoke(prompt)
        return response.content

    # --------------------------------------------------------------

    def search(self, query: str, reference: dict):
        total_timer = Timer()

        # 1. Tạo vector
        step1_timer = Timer()
        # Chuẩn hoá location từ reference: có thể là dict, string, hoặc thiếu
        raw_location = reference.get("location") if isinstance(reference, dict) else None
        if isinstance(raw_location, dict):
            location_text = raw_location.get("name") or raw_location.get("address") or raw_location.get("formattedAddress") or ""
        elif isinstance(raw_location, str):
            location_text = raw_location
        else:
            location_text = ""

        query_vector_text = f"{query}. Tôi ở địa chỉ {location_text}" if location_text else query
        embed = self.geminiService.gemini_get_embedding(query_vector_text)

        if embed is None:
            return {"success": False, "error": "Embedding lỗi"}

        if self.debug:
            print(f"[DEBUG] 🧠 Thời gian tạo embedding: {step1_timer.elapsed_ms():.2f} ms\n")

        # 2. Query Pinecone
        step2_timer = Timer()
        pinecone_result = self.pineconeService.pinecone_search_data(embed, query)

        if not pinecone_result.get("success"):
            return pinecone_result

        jobs = pinecone_result["data"]

        if self.debug:
            print(f"[DEBUG] 🧲 Thời gian Pinecone query: {step2_timer.elapsed_ms():.2f} ms\n")

        # 3. Recommend - lấy top 3 jobs
        step3_timer = Timer()
        top_jobs = self.recommendService.recommendJob(reference, jobs, top_k=3)

        if self.debug:
            print(f"[DEBUG] 🎯 Thời gian Recommend: {step3_timer.elapsed_ms():.2f} ms\n")

        # 4. Tạo câu trả lời tự nhiên bằng LLM
        step4_timer = Timer()
        answer = self._send_to_llm(query, top_jobs)
        
        if self.debug:
            print(f"[DEBUG] 🤖 Thời gian LLM tạo câu trả lời: {step4_timer.elapsed_ms():.2f} ms\n")

        # 5. Lọc jobs theo những job mà LLM đã đề cập
        mentioned_job_ids = self._extract_job_ids_from_answer(answer)
        filtered_jobs = [job for job in top_jobs if job.get("jobID") in mentioned_job_ids]
        
        # Nếu không parse được JobID, fallback về top_jobs
        if not filtered_jobs:
            filtered_jobs = top_jobs
        
        if self.debug:
            print(f"[DEBUG] 📋 Jobs được LLM chọn: {mentioned_job_ids}")
            print(f"[DEBUG] 📊 Số lượng jobs trả về: {len(filtered_jobs)}\n")

        # 6. Tổng
        if self.debug:
            print(f"[DEBUG] ⏱ Tổng thời gian xử lý: {total_timer.elapsed_ms():.2f} ms\n")

        print(f"[Job] Trả lời: {answer}")
        print(f"[Job] Số lượng jobs: {len(filtered_jobs)}")
        print("=================================================================\n")

        return {
            "success": True,
            "message": "Thành công",
            "type": "Job",
            "data": {
                "answer": answer,        # Câu trả lời tự nhiên từ LLM
                "jobs": filtered_jobs    # Chỉ trả về jobs mà LLM đã giới thiệu
            }
        }
