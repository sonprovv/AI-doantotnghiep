# Hướng dẫn Workflow StateGraph

## Cấu trúc Workflow

```
START → classify_topic
         ├─ "policy" → policy_search → END
         ├─ "info" → info_search → END
         └─ "job" → job_search → END
```

## 3 Nodes chính

### 1. Policy Search (application.md)
- **Mục đích**: Trả lời câu hỏi về thông tin ứng dụng, chính sách
- **Data source**: `src/info/data/application.md`
- **Vector DB**: `chroma_db_policy/`
- **Ví dụ câu hỏi**:
  - "Ứng dụng do ai làm ra?"
  - "Có những loại công việc nào?"
  - "Thông tin liên hệ?"
  - "Tập đoàn nào phát triển?"

### 2. Info Search (cleaning.md, healthcare.md)
- **Mục đích**: Trả lời câu hỏi về dịch vụ cụ thể
- **Data source**: `src/info/data/cleaning.md`, `src/info/data/healthcare.md`
- **Vector DB**: `chroma_db/`
- **Ví dụ câu hỏi**:
  - "Dịch vụ dọn phòng khách giá bao nhiêu?"
  - "Dịch vụ chăm sóc sức khỏe có những gì?"
  - "Thời lượng dịch vụ vệ sinh?"

### 3. Job Search (Pinecone)
- **Mục đích**: Tìm kiếm công việc phù hợp
- **Data source**: Pinecone vector DB
- **Ví dụ câu hỏi**:
  - "Tìm công việc gần tôi"
  - "Công việc dọn dẹp ở Hà Nội"
  - "Việc làm phù hợp với chuyên môn"

## Cách chạy

### 1. Ingest data vào Vector DB

```bash
# Ingest policy data (application.md)
python src/policy/ingest_policy.py

# Ingest info data (cleaning.md, healthcare.md)
python src/info/ingest_jobs.py
```

### 2. Sử dụng

```python
from src.arag.AragController import AragController

controller = AragController(None, None)

# Câu hỏi về policy
result = controller.agent_search("Ứng dụng do ai làm ra?", {})

# Câu hỏi về dịch vụ
result = controller.agent_search("Giá dịch vụ dọn phòng khách?", {})

# Tìm công việc
result = controller.agent_search("Tìm việc gần tôi", {"location": "Hà Nội"})
```

## Phân loại tự động

Hệ thống tự động phân loại câu hỏi dựa trên prompts:

- **Policy prompts**: ứng dụng, app, tính năng, ai làm ra, danh mục, tập đoàn, liên hệ
- **Info prompts**: dịch vụ dọn dẹp, dịch vụ chăm sóc, phòng khách, giá dịch vụ
- **Job prompts**: tuyển dụng, tìm việc, công việc gần tôi, gần nhất

## Mở rộng

Để thêm node mới:
1. Tạo Controller và Service mới
2. Thêm node vào `_build_workflow()`
3. Cập nhật `_classify_topic()` với prompts mới
4. Cập nhật `_route_by_topic()` với routing mới
