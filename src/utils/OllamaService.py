import requests
import json
from typing import List, Optional


class OllamaService: 

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "mxbai-embed-large:latest",
        timeout: int = 30  # Tăng timeout để tránh timeout khi model load lần đầu
    ):
        # URL base & endpoint
        self.base_url = base_url.rstrip("/")
        self.embeddings_url = f"{self.base_url}/api/embeddings"

        # Model embedding
        self.modelName = model_name

        # Timeout cho mỗi request (giây)
        self.timeout = timeout

        # Session để reuse connection (nhanh hơn tạo request mới mỗi lần)
        self.session = requests.Session()
        # Keep-alive để giữ connection
        self.session.headers.update({'Connection': 'keep-alive'})

        # Cache đơn giản trong RAM: {text_norm: embedding}
        self._cache = {}
        
        # Preload model vào memory (optional)
        self._preload_model()

    # --------------------------------------------------------------

    def _preload_model(self):
        """Preload model vào memory để request đầu tiên nhanh hơn"""
        try:
            # Gọi một embedding đơn giản để load model
            payload = {
                "model": self.modelName,
                "prompt": "preload",
                "keep_alive": "5m"  # Giữ model trong memory 5 phút
            }
            self.session.post(
                self.embeddings_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=self.timeout
            )
        except Exception:
            pass  # Không quan trọng nếu preload fail

    # --------------------------------------------------------------

    def get_embedding(self, text_to_embed: str) -> Optional[List[float]]:
        if not text_to_embed or not text_to_embed.strip():
            return None

        # Chuẩn hoá text để cache hợp lý (lower + strip)
        text_norm = text_to_embed.strip().lower()

        # 1. Kiểm tra cache trước
        if text_norm in self._cache:
            return self._cache[text_norm]

        payload = {
            "model": self.modelName,
            "prompt": text_norm,
            "keep_alive": "5m"  # Giữ model trong memory 5 phút
        }

        try:
            response = self.session.post(
                self.embeddings_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            embedding = result.get("embedding")

            # Lưu cache nếu hợp lệ
            if embedding and isinstance(embedding, list):
                self._cache[text_norm] = embedding

            return embedding

        except requests.exceptions.RequestException as e:
            print(f"[OllamaService] Lỗi khi gọi API Ollama: {e}")
            return None

    # --------------------------------------------------------------

    def ollama_get_embedding(self, query: str):
        from src.utils.Timer import Timer
        timer = Timer()

        vector = self.get_embedding(query)

        if vector:
            print(f"[OllamaService] Chuỗi: '{query}'")
            print(f"[OllamaService] Kích thước vector: {len(vector)}")
            print(f"[OllamaService] ⏱ Thời gian embed: {timer.elapsed_ms():.2f} ms")
        else:
            print("[OllamaService] Không thể trích xuất embedding.")
        
        return vector


    # --------------------------------------------------------------
