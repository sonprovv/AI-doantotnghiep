# Hướng dẫn Migration từ Ollama sang Google Gemini

## Các thay đổi đã thực hiện

### 1. Dependencies (requirements.txt)
- ❌ Xóa: `langchain-ollama>=0.1.0`
- ✅ Thêm: 
  - `langchain-google-genai>=1.0.0`
  - `google-generativeai>=0.3.0`

### 2. Environment Variables (.env)
- ✅ Thêm: `GOOGLE_API_KEY=YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE`

**Lấy API key tại:** https://aistudio.google.com/app/apikey

### 3. Service Layer
- ✅ Tạo mới: `src/utils/GeminiService.py` (thay thế OllamaService)
- Model embedding: `models/embedding-001` (Gemini)
- Cache mechanism: Giữ nguyên để tối ưu performance

### 4. Controllers
- `src/job/JobController.py`: OllamaService → GeminiService
- `src/create/CreateController.py`: OllamaService → GeminiService

### 5. LangChain Services
**InfoService, PolicyService, AragController:**
- Embeddings: `OllamaEmbeddings` → `GoogleGenerativeAIEmbeddings`
- LLM: `ChatOllama` → `ChatGoogleGenerativeAI`
- Model: `llama3` → `gemini-1.5-flash`

### 6. Ingest Scripts
**ingest.py, ingest_jobs.py, ingest_policy.py:**
- Embeddings: `OllamaEmbeddings` → `GoogleGenerativeAIEmbeddings`
- Model: `mxbai-embed-large:latest` → `models/embedding-001`

## Cài đặt và Chạy

### Bước 1: Cài đặt dependencies mới
```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình API Key
Mở file `.env` và thay thế:
```
GOOGLE_API_KEY=YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE
```

### Bước 3: Re-ingest dữ liệu (QUAN TRỌNG!)
Vì embedding model đã thay đổi, bạn cần tạo lại vector database:

```bash
# Ingest info data
python src/info/ingest.py

# Ingest jobs data
python src/info/ingest_jobs.py

# Ingest policy data
python src/policy/ingest_policy.py
```

### Bước 4: Chạy ứng dụng
```bash
python app.py
```

## So sánh Ollama vs Gemini

| Tính năng | Ollama (Local) | Gemini (Cloud) |
|-----------|----------------|----------------|
| **Tốc độ** | Phụ thuộc hardware | Nhanh, ổn định |
| **Chi phí** | Miễn phí | Free tier: 60 requests/phút |
| **Setup** | Cần cài Ollama + models | Chỉ cần API key |
| **Offline** | ✅ Có | ❌ Không |
| **Chất lượng** | Tốt (llama3) | Rất tốt (Gemini 1.5) |

## Lưu ý quan trọng

1. **Vector Database:** Phải re-ingest vì embedding dimension khác nhau
   - Ollama mxbai-embed-large: 1024 dimensions
   - Gemini embedding-001: 768 dimensions

2. **Rate Limits:** Gemini free tier có giới hạn:
   - 60 requests/phút
   - 1500 requests/ngày
   
3. **API Key Security:** Không commit API key lên Git!

4. **Fallback:** Giữ lại OllamaService.py nếu muốn quay lại Ollama

## Troubleshooting

### Lỗi: "GOOGLE_API_KEY không tìm thấy"
- Kiểm tra file `.env` có chứa `GOOGLE_API_KEY`
- Đảm bảo đã load dotenv: `load_dotenv()`

### Lỗi: "Rate limit exceeded"
- Đợi 1 phút rồi thử lại
- Hoặc nâng cấp lên paid plan

### Lỗi: "Embedding dimension mismatch"
- Xóa folder `chroma_db` và `chroma_db_policy`
- Chạy lại các script ingest

## Rollback về Ollama

Nếu muốn quay lại Ollama:
1. Restore `requirements.txt` cũ
2. Đổi import từ `GeminiService` về `OllamaService`
3. Restore các file Service/Controller
4. Re-ingest với Ollama embeddings
