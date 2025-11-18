from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY').strip())

# Tạo index mới
index_name = "demo-pinecone"

print(f"Đang tạo index '{index_name}'...")

pc.create_index(
    name=index_name,
    dimension=768,  # Gemini embedding dimension
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

print(f"✅ Đã tạo index '{index_name}' thành công!")
print(f"Danh sách indexes: {[idx.name for idx in pc.list_indexes()]}")
