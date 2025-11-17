# ✅ Migration hoàn tất: Gemini 2.0 Flash

## Tóm tắt

Đã chuyển đổi thành công từ Ollama local sang **Google Gemini 2.0 Flash**.

## Models đang sử dụng

- **Embedding:** `models/text-embedding-004` (768 dimensions)
- **LLM:** `gemini-2.0-flash-exp` (model mới nhất, nhanh nhất)

## Đã hoàn thành

✅ Cài đặt dependencies (langchain-google-genai, google-generativeai)  
✅ Tạo GeminiService thay thế OllamaService  
✅ Cập nhật tất cả Controllers và Services  
✅ Fix imports (langchain.prompts → langchain_core.prompts)  
✅ Xóa ChromaDB cũ (dimension mismatch)  
✅ Ingest thành công với Gemini embeddings  
✅ Test thành công tất cả services  

## Chạy ứng dụng

```bash
python app.py
```

Server sẽ chạy tại: http://localhost:8000

## API Endpoints

- `POST /api/job/search` - Tìm công việc
- `POST /api/info/answer` - Trả lời về dịch vụ
- `POST /api/chatbot` - Chatbot với ARAG

## Lưu ý quan trọng

### API Key
- Đảm bảo `GOOGLE_API_KEY` trong `.env` là hợp lệ
- API key phải không bị giới hạn cho Android
- Tạo tại: https://aistudio.google.com/app/apikey

### Quota (Free tier)
- **Embeddings:** 1,500 requests/day
- **Gemini 2.0 Flash:** 1,500 requests/day
- Kiểm tra tại: https://ai.google.dev/pricing

### Nếu hết quota
1. Đợi 24h để quota reset
2. Tạo project mới với API key mới
3. Hoặc upgrade lên paid plan

## Files đã thay đổi

**Core Services:**
- `src/utils/GeminiService.py` (mới)
- `src/info/InfoService.py`
- `src/policy/PolicyService.py`
- `src/arag/AragController.py`
- `src/job/JobController.py`
- `src/create/CreateController.py`

**Ingest Scripts:**
- `src/info/ingest.py`
- `src/info/ingest_jobs.py`
- `src/policy/ingest_policy.py`

**Config:**
- `requirements.txt`
- `.env` (thêm GOOGLE_API_KEY)

## Rollback về Ollama

Nếu cần quay lại Ollama:

1. Restore `requirements.txt` cũ
2. Đổi imports từ GeminiService về OllamaService
3. Xóa ChromaDB và re-ingest với Ollama
4. Cài Ollama: https://ollama.ai

## Troubleshooting

### Lỗi: "API key not valid"
→ Tạo API key mới không bị giới hạn

### Lỗi: "Quota exceeded"
→ Đợi 24h hoặc tạo project mới

### Lỗi: "Dimension mismatch"
→ Xóa `chroma_db` và `chroma_db_policy`, chạy lại ingest

### Lỗi: "Module not found"
→ `pip install -r requirements.txt`

## Performance

**So với Ollama:**
- ⚡ Nhanh hơn (không phụ thuộc hardware local)
- ☁️ Ổn định hơn (Google infrastructure)
- 🎯 Chất lượng tốt hơn (Gemini 2.0 > Llama 3)
- 💰 Free tier: 1,500 requests/day

**Lưu ý:**
- Cần internet connection
- Có rate limits
- Data được gửi lên Google servers

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. API key hợp lệ trong `.env`
2. ChromaDB đã được ingest với Gemini embeddings
3. Dependencies đã cài đầy đủ
4. Quota chưa hết

---

**Chúc mừng! Ứng dụng đã sẵn sàng với Gemini 2.0 Flash! 🎉**
