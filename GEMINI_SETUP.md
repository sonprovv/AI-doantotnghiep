# Hướng dẫn Setup Gemini 2.0 Flash

## ⚠️ Lỗi API Key bị chặn

Nếu bạn gặp lỗi:
- `API_KEY_ANDROID_APP_BLOCKED`
- `Quota exceeded`
- `API key not valid`

**Nguyên nhân:** API key bị giới hạn hoặc cấu hình sai

## ✅ Giải pháp: Tạo API Key mới

### Bước 1: Tạo API Key không bị giới hạn

1. Truy cập: **https://aistudio.google.com/app/apikey**
2. Click **"Create API key"**
3. Chọn project hoặc tạo mới
4. **QUAN TRỌNG:** 
   - Không chọn "Android app restrictions"
   - Chọn "None" hoặc "IP addresses" (nếu cần)
5. Copy API key (bắt đầu bằng `AIza...`)

### Bước 2: Cập nhật file .env

Mở file `.env` và thay thế:

```properties
GOOGLE_API_KEY=AIzaSy...your_new_api_key_here
```

**Lưu ý:** 
- API key phải bắt đầu bằng `AIza`
- Không có khoảng trắng hoặc ký tự thừa
- Không có chữ "Y" ở đầu

### Bước 3: Kiểm tra Quota

Truy cập: **https://ai.google.dev/pricing**

**Free tier limits:**
- **Embeddings (text-embedding-004):** 1,500 requests/day
- **Gemini 2.0 Flash:** 1,500 requests/day, 1 million tokens/day

Nếu hết quota, đợi 24h hoặc upgrade lên paid plan.

### Bước 4: Test API Key

Chạy script test đơn giản:

```python
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key: {api_key[:10]}...")

genai.configure(api_key=api_key)

# Test embedding
result = genai.embed_content(
    model="models/text-embedding-004",
    content="Hello world"
)
print(f"✅ Embedding thành công! Dimension: {len(result['embedding'])}")
```

### Bước 5: Chạy Ingest

```bash
# Ingest info data
python src/info/ingest.py

# Ingest jobs data  
python src/info/ingest_jobs.py

# Ingest policy data
python src/policy/ingest_policy.py
```

## Models đang sử dụng

- **Embedding:** `models/text-embedding-004` (768 dimensions, model mới nhất)
- **LLM:** `gemini-2.0-flash-exp` (nhanh, miễn phí)

## Troubleshooting

### Lỗi: "API key not valid"
- Kiểm tra API key có đúng format không
- Tạo API key mới từ Google AI Studio

### Lỗi: "Quota exceeded"
- Đợi 24h để quota reset
- Hoặc upgrade lên paid plan
- Hoặc tạo project mới với API key mới

### Lỗi: "Android app blocked"
- API key bị giới hạn cho Android
- Tạo API key mới với "No restrictions"

### Lỗi: "Permission denied"
- Enable Generative Language API tại: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

## Alternative: Quay lại Ollama

Nếu không muốn dùng Gemini, có thể quay lại Ollama local (miễn phí, không giới hạn):

```bash
# Cài Ollama
# Download từ: https://ollama.ai

# Pull model
ollama pull mxbai-embed-large
ollama pull llama3

# Revert code về Ollama
# (liên hệ để được hỗ trợ)
```
