# Hướng dẫn tối ưu thời gian chạy LLM

## 1. Tối ưu đã implement ✅

### OllamaService
- ✅ **Session reuse**: Giữ HTTP connection để tránh tạo connection mới
- ✅ **Keep-alive**: Giữ connection mở giữa các request
- ✅ **Cache embedding**: Cache kết quả embedding trong RAM
- ✅ **Preload model**: Load model vào memory khi khởi động
- ✅ **Keep model alive**: Giữ model trong memory 5 phút sau mỗi request

### AragController
- ✅ **Keyword routing**: Dùng keyword thay vì agent cho hầu hết queries
- ✅ **Agent cache**: Cache kết quả agent (nếu cần dùng)
- ✅ **Direct routing**: Bypass agent hoàn toàn cho queries rõ ràng

## 2. Tối ưu thêm (optional)

### A. Dùng model nhỏ hơn (nhanh nhất)
```python
# Trong AragController.__init__
self.llmModel = "llama3.2:1b"  # Thay vì "llama3"
# hoặc
self.llmModel = "phi3:mini"
```

**Ưu điểm**: Nhanh gấp 3-5 lần
**Nhược điểm**: Độ chính xác giảm một chút

### B. Giảm context length
```python
self.llm = ChatOllama(
    model=self.llmModel, 
    temperature=0,
    num_ctx=2048  # Giảm từ 4096 xuống 2048
)
```

### C. Tăng performance Ollama
Chỉnh file Ollama config hoặc chạy với options:
```bash
# Tăng số GPU layers
ollama run llama3 --num-gpu 99

# Tăng số threads
ollama run llama3 --num-thread 8
```

### D. Batch processing
Nếu có nhiều queries cùng lúc, gom lại xử lý batch:
```python
def batch_search(self, queries, references):
    results = []
    for query, ref in zip(queries, references):
        results.append(self.agent_search(query, ref))
    return results
```

## 3. Monitoring performance

### Thêm timer vào AragController
```python
from src.utils.Timer import Timer

def agent_search(self, query, reference):
    timer = Timer()
    
    # ... code xử lý ...
    
    print(f"[AragController] Total time: {timer.elapsed_ms():.2f} ms")
    return result
```

### Chạy test với debug mode
```bash
python test.py
```

## 4. Kết quả mong đợi

| Tối ưu | Thời gian trước | Thời gian sau | Cải thiện |
|--------|----------------|---------------|-----------|
| Cache embedding | 500-1000ms | 50-100ms | 10x |
| Keyword routing | 2000-3000ms | 100-200ms | 15x |
| Model nhỏ hơn | 2000ms | 500ms | 4x |
| Keep-alive | 1000ms | 200ms | 5x |

## 5. Trade-offs

- **Cache**: Tốn RAM nhưng nhanh hơn nhiều
- **Keyword routing**: Mất tính linh hoạt của agent nhưng nhanh và chính xác hơn
- **Model nhỏ**: Nhanh hơn nhưng có thể kém chính xác
- **Keep-alive**: Tốn memory server nhưng response nhanh hơn

## 6. Khuyến nghị

1. **Ưu tiên cao**: Dùng keyword routing (đã implement)
2. **Ưu tiên trung bình**: Cache embedding (đã implement)
3. **Nếu vẫn chậm**: Thử model nhỏ hơn
4. **Nếu có nhiều RAM**: Tăng cache size
5. **Nếu có GPU tốt**: Tăng num_gpu trong Ollama
