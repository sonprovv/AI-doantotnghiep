# GoodJob API - AI Job Matching System

Hệ thống tìm kiếm và gợi ý công việc thông minh sử dụng Gemini 2.5 Flash và ARAG (Agentic RAG).

## Features

- 🤖 **ARAG Chatbot**: Tự động phân loại và route câu hỏi
- 🔍 **Job Search**: Tìm kiếm công việc với vector similarity
- 💬 **Info Q&A**: Trả lời câu hỏi về dịch vụ
- 📋 **Policy Q&A**: Thông tin về ứng dụng

## Tech Stack

- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: Gemini text-embedding-004 (768 dimensions)
- **Vector DB**: Pinecone + ChromaDB
- **Framework**: Flask + LangChain
- **Platform**: HuggingFace Spaces

## API Endpoints

### Health Check
```bash
GET /
```

### Job Search
```bash
POST /api/job/search
{
  "query": "Tìm công việc dọn dẹp",
  "reference": {
    "location": {"name": "Quận 1, TP.HCM"},
    "experiences": {"CLEANING": 2}
  }
}
```

### Chatbot (ARAG)
```bash
POST /api/chatbot
{
  "query": "Có những loại công việc nào",
  "reference": {}
}
```

### Info Q&A
```bash
POST /api/info/answer
{
  "query": "Trông trẻ thì cần làm gì",
  "reference": {}
}
```

## Environment Variables

```
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_HOST=your_pinecone_host
```

## Local Development

```bash
pip install -r requirements.txt
python app_hf.py
```

## Deploy to HuggingFace Spaces

See `README_HUGGINGFACE.md` for detailed instructions.

## License

MIT
