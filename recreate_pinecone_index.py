"""
Script để xóa và tạo lại Pinecone index với dimension 768 (Gemini)
"""
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "demo-pinecone"

pc = Pinecone(api_key=PINECONE_API_KEY)

# Xóa index cũ nếu tồn tại
try:
    print(f"🗑️  Đang xóa index '{INDEX_NAME}'...")
    pc.delete_index(INDEX_NAME)
    print(f"✅ Đã xóa index '{INDEX_NAME}'")
except Exception as e:
    print(f"⚠️  Index không tồn tại hoặc lỗi: {e}")

# Tạo index mới với dimension 768
print(f"\n🔨 Đang tạo index mới '{INDEX_NAME}' với dimension 768...")
pc.create_index(
    name=INDEX_NAME,
    dimension=768,  # Gemini embedding dimension
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

print(f"✅ Đã tạo index '{INDEX_NAME}' thành công!")
print(f"\n📝 Bước tiếp theo:")
print(f"   1. Đợi vài giây để index khởi tạo")
print(f"   2. Chạy: python -c \"from src.create.CreateController import CreateController; c = CreateController(); c.create_sample_data()\"")
print(f"   3. Hoặc upload dữ liệu job của bạn qua API /api/job-embedding")
