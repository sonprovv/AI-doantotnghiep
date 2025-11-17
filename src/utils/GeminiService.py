import os
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiService:

    def __init__(
        self,
        model_name: str = "models/text-embedding-004"
    ):
        # Lấy API key từ .env
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY không tìm thấy trong file .env")
        
        # Cấu hình Gemini
        genai.configure(api_key=api_key)
        
        # Model embedding (text-embedding-004 là model mới nhất)
        self.modelName = model_name

        # Cache đơn giản trong RAM: {text_norm: embedding}
        self._cache = {}

    # --------------------------------------------------------------

    def get_embedding(self, text_to_embed: str) -> Optional[List[float]]:
        if not text_to_embed or not text_to_embed.strip():
            return None

        # Chuẩn hoá text để cache hợp lý (lower + strip)
        text_norm = text_to_embed.strip().lower()

        # 1. Kiểm tra cache trước
        if text_norm in self._cache:
            return self._cache[text_norm]

        try:
            # Gọi Gemini API để lấy embedding
            result = genai.embed_content(
                model=self.modelName,
                content=text_norm,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']

            # Lưu cache nếu hợp lệ
            if embedding and isinstance(embedding, list):
                self._cache[text_norm] = embedding

            return embedding

        except Exception as e:
            print(f"[GeminiService] Lỗi khi gọi API Gemini: {e}")
            return None

    # --------------------------------------------------------------

    def gemini_get_embedding(self, query: str):
        from src.utils.Timer import Timer
        timer = Timer()

        vector = self.get_embedding(query)

        if vector:
            print(f"[GeminiService] Chuỗi: '{query}'")
            print(f"[GeminiService] Kích thước vector: {len(vector)}")
            print(f"[GeminiService] ⏱ Thời gian embed: {timer.elapsed_ms():.2f} ms")
        else:
            print("[GeminiService] Không thể trích xuất embedding.")
        
        return vector

    # --------------------------------------------------------------
