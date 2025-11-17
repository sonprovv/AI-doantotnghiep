# Deploy GoodJob API lên Vercel

## Bước 1: Chuẩn bị

### 1.1. Cài Vercel CLI (optional)
```bash
npm install -g vercel
```

### 1.2. Tạo tài khoản Vercel
- Truy cập: https://vercel.com/signup
- Đăng ký bằng GitHub

## Bước 2: Cấu hình Environment Variables

Trên Vercel Dashboard, thêm các biến môi trường:

```
GOOGLE_API_KEY=AIzaSy...
PINECONE_API_KEY=pcsk_...
PINECONE_HOST=https://...
```

**Lưu ý:** Không commit file `.env` lên Git!

## Bước 3: Deploy

### Cách 1: Deploy qua Vercel Dashboard (Khuyến nghị)

1. Push code lên GitHub
2. Truy cập: https://vercel.com/new
3. Import repository
4. Vercel tự động detect Python project
5. Thêm Environment Variables
6. Click "Deploy"

### Cách 2: Deploy qua CLI

```bash
# Login
vercel login

# Deploy
vercel

# Deploy production
vercel --prod
```

## Bước 4: Test API

Sau khi deploy, bạn sẽ có URL như: `https://your-project.vercel.app`

Test endpoints:

```bash
# Health check
curl https://your-project.vercel.app/

# Search jobs
curl -X POST https://your-project.vercel.app/api/job/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm công việc dọn dẹp",
    "reference": {
      "location": {"name": "Quận 1, TP.HCM"},
      "experiences": {"CLEANING": 2}
    }
  }'

# Chatbot
curl -X POST https://your-project.vercel.app/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Có những loại công việc nào",
    "reference": {}
  }'
```

## Lưu ý quan trọng

### 1. ChromaDB không hoạt động trên Vercel
Vercel là serverless, không có persistent storage. ChromaDB cần:
- Upload lên cloud storage (S3, GCS)
- Hoặc dùng Chroma Cloud: https://www.trychroma.com/
- Hoặc chuyển sang vector DB khác (Pinecone, Weaviate)

### 2. Cold Start
Lần đầu tiên gọi API sẽ chậm (5-10s) do cold start. Các request sau sẽ nhanh hơn.

### 3. Timeout
Vercel free tier có timeout 10s. Nếu request chậm hơn, cần:
- Upgrade lên Pro plan (60s timeout)
- Tối ưu code

### 4. Rate Limits
- Gemini free tier: 10 requests/minute
- Vercel free tier: 100GB bandwidth/month

## Giải pháp cho ChromaDB

### Option 1: Chroma Cloud (Khuyến nghị)
```python
# src/info/InfoService.py
import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host="your-chroma-cloud-host",
    settings=Settings(
        chroma_client_auth_provider="token",
        chroma_client_auth_credentials="your-token"
    )
)
```

### Option 2: Pinecone cho tất cả
Chuyển ChromaDB sang Pinecone hoàn toàn (đã có sẵn cho jobs).

### Option 3: Supabase Vector
Dùng Supabase pgvector (free tier tốt).

## Troubleshooting

### Lỗi: "Module not found"
- Kiểm tra `requirements.txt` đầy đủ
- Vercel tự động cài dependencies

### Lỗi: "Function timeout"
- Tối ưu code
- Upgrade Vercel plan
- Cache kết quả

### Lỗi: "ChromaDB not working"
- ChromaDB cần persistent storage
- Chuyển sang cloud solution

## Monitoring

- Logs: https://vercel.com/dashboard/logs
- Analytics: https://vercel.com/dashboard/analytics
- Usage: https://vercel.com/dashboard/usage

## Cost

**Vercel Free Tier:**
- 100GB bandwidth/month
- 100 hours serverless function execution
- 10s timeout

**Vercel Pro ($20/month):**
- 1TB bandwidth
- 1000 hours execution
- 60s timeout

**Gemini Free Tier:**
- 1,500 requests/day
- 1 million tokens/day

## Next Steps

1. ✅ Deploy lên Vercel
2. ⚠️ Migrate ChromaDB sang cloud solution
3. 🔧 Setup monitoring và alerts
4. 📊 Optimize performance
5. 🔒 Add authentication nếu cần

---

**Chúc bạn deploy thành công! 🚀**
