# Deploy lên HuggingFace Spaces

## Bước 1: Tạo Space

1. Truy cập: https://huggingface.co/new-space
2. Điền thông tin:
   - **Space name**: `goodjob-api` (hoặc tên bạn muốn)
   - **License**: MIT
   - **Select the Space SDK**: **Docker**
   - **Space hardware**: CPU basic (free) hoặc upgrade nếu cần
3. Click "Create Space"

## Bước 2: Clone Space về local

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/goodjob-api
cd goodjob-api
```

## Bước 3: Copy files từ project hiện tại

Copy tất cả files (trừ `.git`, `__pycache__`, `chroma_db`) vào folder space:

```bash
# Windows
xcopy /E /I /Y "C:\Users\Dell\Desktop\ARAG-thien\ARAG - Copy\*" "goodjob-api\"

# Hoặc copy thủ công các folder:
# - src/
# - app_hf.py
# - requirements.txt
# - Dockerfile
# - .env (đổi tên thành .env.example)
```

## Bước 4: Add Environment Variables

Trên HuggingFace Space Settings:

1. Click tab "Settings"
2. Scroll xuống "Repository secrets"
3. Add secrets:
   - `GOOGLE_API_KEY` = `AIzaSy...`
   - `PINECONE_API_KEY` = `pcsk_...`
   - `PINECONE_HOST` = `https://...`

## Bước 5: Push lên HuggingFace

```bash
cd goodjob-api
git add .
git commit -m "Initial commit"
git push
```

## Bước 6: Đợi build

- HuggingFace sẽ tự động build Docker image
- Thời gian build: 5-10 phút
- Xem logs tại tab "Logs"

## Bước 7: Test API

Space URL: `https://YOUR_USERNAME-goodjob-api.hf.space`

```bash
# Health check
curl https://YOUR_USERNAME-goodjob-api.hf.space/

# Test chatbot
curl -X POST https://YOUR_USERNAME-goodjob-api.hf.space/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Có những loại công việc nào",
    "reference": {}
  }'
```

## Lưu ý

### 1. ChromaDB trên HuggingFace
- ChromaDB sẽ hoạt động bình thường (có persistent storage)
- Data sẽ được lưu trong container
- Nếu restart space, data có thể mất → nên backup

### 2. Hardware
- **CPU basic (free)**: 2 vCPU, 16GB RAM
- **CPU upgrade ($0.03/hour)**: 8 vCPU, 32GB RAM
- **GPU**: Nếu cần xử lý nặng

### 3. Timeout
- Không có timeout limit như Vercel
- Request có thể chạy lâu

### 4. Cold Start
- Space sẽ sleep sau 48h không dùng
- Lần đầu gọi API sẽ chậm (1-2 phút)
- Upgrade lên persistent để tránh sleep

## Troubleshooting

### Build failed
- Kiểm tra `Dockerfile` syntax
- Kiểm tra `requirements.txt`
- Xem logs chi tiết

### API không hoạt động
- Kiểm tra Environment Variables
- Xem logs: Tab "Logs"
- Test local trước: `python app_hf.py`

### ChromaDB error
- Kiểm tra folder `chroma_db` tồn tại
- Chạy ingest scripts trước khi deploy

## Cost

**Free tier:**
- CPU basic: Free
- 50GB storage
- Public space

**Paid:**
- CPU upgrade: $0.03/hour
- Persistent: $5/month (không sleep)
- Private space: $9/month

## Monitoring

- Logs: Tab "Logs" trên Space
- Metrics: Tab "Analytics"
- Usage: Settings → Billing

---

**Chúc bạn deploy thành công! 🚀**
