from src.utils.GeminiService import GeminiService
from src.utils.PineconeService import PineconeService
from src.utils.RecommendService import RecommendService
from src.utils.Timer import Timer

class JobController:

    def __init__(self, debug=False):
        self.geminiService = GeminiService()
        self.pineconeService = PineconeService()
        self.recommendService = RecommendService()
        self.debug = debug  # <-- thêm flag

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

        # 4. Tổng
        if self.debug:
            print(f"[DEBUG] ⏱ Tổng thời gian xử lý: {total_timer.elapsed_ms():.2f} ms\n")

        return {
            "success": True,
            "message": "Thành công",
            "type": "Job",
            "data": top_jobs  # Trả về danh sách top 3 jobs
        }
