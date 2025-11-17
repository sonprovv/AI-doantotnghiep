from pinecone import Pinecone
import os
import time
from src.job.JobController import JobController
from src.info.InfoController import InfoController
from src.arag.AragController import AragController  # chỉnh lại path đúng với project của bạn

# Test Pinecone connection
api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)
index_info = pc.describe_index("demo-pinecone")
print(index_info)

print("\n" + "="*50)
print("Testing AragController (Chatbot Router)")
print("="*50 + "\n")

info_controller = InfoController()
job_controller = JobController(debug=True)
arag = AragController(info_controller, job_controller)

reference = {
    "location": {
        "name": "Quận 1, TP.HCM",
        "lat": 10.7769,
        "lon": 106.7009
    },
    "experiences": {
        "CLEANING": 2,
        "HEALTHCARE": 0,
        "MAINTENANCE": 1
    }
}

test_queries = [
    "Tìm công việc dọn dẹp",
    "Có những loại công việc nào",
    "Ứng dụng này do ai làm ra",
    "Công việc gần tôi nhất là gì",
    "Những công việc phù hợp với chuyên môn của tôi và gần nhất",
    "Trông trẻ thì cần làm gì",
    "Chăm sóc người già thì cần làm gì",
    "Chăm sóc người khuyết tật thì cần làm gì",
    "Khi tôi bất cẩn làm sai thì có bị phạt gì không"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*60}")
    print(f"TEST {i}/{len(test_queries)}")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Reference: {reference}\n")
    
    result = arag.agent_search(query, reference)
    print("\nResult:")
    print(result)
    print(f"{'='*60}\n")
    
    # Nghỉ 10 giây giữa các query để tránh rate limit
    if i < len(test_queries):
        print(f"⏳ Đợi 10 giây trước query tiếp theo...\n")
        time.sleep(10)
