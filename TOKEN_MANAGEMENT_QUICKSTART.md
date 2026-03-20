# Token Management - Quick Start Guide

## 🚀 Khởi Động Nhanh

### 1. Chạy Ứng Dụng Với Token Tracking

```bash
python main.py
```

**Output sẽ tự động show:**
- Model được chọn cho mỗi câu hỏi
- Số token sử dụng (prompt + output)
- Chi phí cho mỗi query
- Tổng chi phí session

### 2. Xem Test Demo

```bash
python rag/test_token_manager.py
```

**Kết quả:**
- Complexity estimation (1-10)
- Model selection logic
- Cost calculation
- Session summary

---

## 📊 Hiểu Kết Quả

### Token Info Mỗi Query

```
[Model Selection] Complexity 5: Flash 2.0 (balanced)
--------------------------------------------------
[Token Usage] Model: gemini-2.0-flash
  Prompt: 2,500 | Output: 400 | Total: 2,900
  Cost: $0.000400
  Session Cost: $0.005234
--------------------------------------------------
```

**Giải thích:**
- **Complexity 5**: Độ phức tạp câu hỏi (1=đơn giản, 10=phức tạp)
- **Flash 2.0**: Model được chọn tự động (cân bằng chi phí & chất lượng)
- **Prompt tokens**: Token của prompt (system + context + question)
- **Output tokens**: Token của câu trả lời từ AI
- **Cost**: Chi phí cho query này
- **Session Cost**: Tổng chi phí từ đầu phiên

### Session Summary

```
============================================================
TOKEN MANAGEMENT SUMMARY
============================================================
Total Queries: 10
Total Tokens Used: 28,500
Total Cost: $0.087654
Avg Cost/Query: $0.008765

Model Usage Breakdown:
  gemini-2.5-flash-lite:
    - Queries: 4
    - Tokens: 5,000
    - Cost: $0.000675
  gemini-2.0-flash:
    - Queries: 5
    - Tokens: 15,000
    - Cost: $0.024000
  gemini-1.5-pro:
    - Queries: 1
    - Tokens: 8,500
    - Cost: $0.062979
```

---

## 💡 Hiểu Cơ Chế Chọn Model

### Complexity Scoring (Tự động tính từ câu hỏi)

```
Complexity 1-3  →  Flash Lite (Cheapest) 
   - Câu đơn: "Là gì audit?"
   - Truy vấn cơ bản
   - Chi phí: ~$0.0001/query

Complexity 4-7  →  Flash 2.0 (Balanced)  
   - Câu trung bình: "Giải thích quy trình audit"
   - Cần so sánh, tóm tắt
   - Chi phí: ~$0.0004/query

Complexity 8-10 →  Pro (Best Quality)
   - Câu phức tạp: "Phân tích chi tiết, tại sao, làm sao cải thiện"
   - Cần suy luận sâu
   - Chi phí: ~$0.025/query (nhưng chất lượng tốt nhất)
```

### Các Từ Khóa Phát Hiện Lớp Cao (Complexity += 2 mỗi từ)

```
Phân tích, So sánh, Giải thích, Tại sao, 
Làm sao, Chi tiết, Toàn bộ, Tổng hợp, 
Cách, Quy trình
```

---

## 📈 Ví Dụ Thực Tế

### Scenario 1: RAG Session 10 queries

| Câu hỏi | Độ phức tạp | Model | Tokens | Cost | 
|--------|-----------|-------|--------|------|
| "Là gì?" | 1 | Flash Lite | 500 | $0.00007 |
| "Quy trình?" | 3 | Flash Lite | 1500 | $0.00020 |
| "Giải thích chi tiết" | 5 | Flash 2.0 | 2500 | $0.00040 |
| "Tại sao? Ưu điểm?" | 7 | Flash 2.0 | 3000 | $0.00048 |
| ... (6 queries nữa) | - | - | - | - |
| **TỔNG** | - | - | **28,500** | **$0.0876** |

**Nếu dùng Pro cho tất cả**: ~$0.60 (6.8x đắt hơn!)
**Với Smart Selection**: $0.0876 (tiết kiệm 85%)

### Scenario 2: 1000 Queries/Month

```
Bình thường (dùng Pro): 1000 * 0.025 = $25/tháng
Smart Selection:        1000 * 0.0088 = $8.8/tháng
Tiết kiệm:             $16.2/tháng (65% tiết kiệm)
```

---

## 🔍 Xem Log Files

### Tìm log files

```bash
ls logs/
# Kết quả: session_20240321_103045.json, ...
```

### Đọc và phân tích

```python
import json

with open("logs/session_20240321_103045.json") as f:
    data = json.load(f)

print(f"Total queries: {data['total_queries']}")
print(f"Total cost: ${data['total_cost']:.4f}")
print(f"Models used: {list(data['model_usage'].keys())}")

# Xem từng query
for query in data['queries'][:3]:
    print(f"- {query['query']}: Cost ${query['cost_usd']:.6f}")
```

---

## ⚙️ Tùy Chỉnh Cấu Hình

### Thay Đổi Pricing (nếu API giá thay đổi)

File: `rag/token_manager.py`

```python
PRICING = {
    "gemini-1.5-flash": {"input": 0.075, "output": 0.3},  # Update ở đây
    "gemini-2.0-flash": {"input": 0.1, "output": 0.4},
    "gemini-1.5-pro": {"input": 2.5, "output": 7.5},
}
```

### Thay Đổi Ngưỡng Complexity (nếu muốn khác)

File: `rag/token_manager.py` - hàm `select_model()`

```python
if complexity <= 3:  # Thay 3 thành số khác
    return "gemini-2.5-flash-lite", ...
elif complexity <= 7:  # Thay 7 thành số khác
    return "gemini-2.0-flash", ...
else:
    return "gemini-1.5-pro", ...
```

### Thay Đổi Keywords Phát Hiện Lớp Cao

File: `rag/token_manager.py` - hàm `estimate_complexity()`

```python
complex_keywords = [
    "phân tích", "so sánh", "giải thích",  # Thêm/xóa keyword
    # ... thêm keyword của bạn
]
```

---

## 📝 Logs & Analytics

### Cấu Trúc Log

```json
{
  "timestamp": "2024-03-21T10:30:45.123456",
  "total_queries": 5,
  "total_tokens": 10030,
  "total_cost": 0.013214,
  "model_usage": {
    "gemini-1.5-flash": {
      "count": 1,
      "tokens": 480,
      "cost": 0.000054
    },
    "gemini-2.0-flash": {
      "count": 3,
      "tokens": 6250,
      "cost": 0.00091
    },
    "gemini-1.5-pro": {
      "count": 1,
      "tokens": 3300,
      "cost": 0.01225
    }
  },
  "queries": [
    {
      "timestamp": "2024-03-21T10:30:45",
      "query": "Là gì audit?",
      "complexity": 1,
      "model": "gemini-1.5-flash",
      "prompt_tokens": 400,
      "output_tokens": 80,
      "total_tokens": 480,
      "cost_usd": 0.000054,
      "answer_preview": "Audit là quá trình..."
    },
    // ... more queries
  ]
}
```

---

## ⚠️ Lưu Ý & Troubleshooting

### Token Count không chính xác

**Tình huống**: API không trả về usage_metadata
**Giải pháp**: Dùng rough estimate (`len(text) // 4`)
**Cải thiện**: Sử dụng Google's tokenizer API

### Chi phí cao bất ngờ

**Khả năng**: 
1. Context quá lớn (> 3000 tokens)
2. Complexity scoring không chính xác
3. API pricing đã thay đổi

**Giải pháp**:
1. Giảm `k` trong `retriever.retrieve(k=5)` - lấy ít context hơn
2. Điều chỉnh keyword phát hiện complexity
3. Cập nhật PRICING trong token_manager.py

### Model selection không như mong muốn

**Tình huống**: Muốn dùng Pro nhưng hệ thống chọn Flash
**Giải pháp**: Thay đổi complexity ngưỡng hoặc force model trong code

```python
# Trong main.py, bỏ comment dòng sau:
# selected_model = "gemini-1.5-pro"  # Force Pro
```

---

## 🎯 Best Practices

✅ **Đơn giản, rõ ràng** → Dùng Flash Lite  
✅ **Trung bình phức tạp** → Để hệ thống chọn Flash 2.0  
✅ **Phức tạp, quan trọng** → Để hệ thống chọn Pro (hoặc force)  
✅ **Kiểm tra log hàng tuần** → Tối ưu từ khóa & ngưỡng  
✅ **Set budget hàng tháng** → Không vượt quá $X  

---

## 📚 Tài Liệu Liên Quan

- [TOKEN_MANAGEMENT_REPORT.md](TOKEN_MANAGEMENT_REPORT.md) - Chi tiết kỹ thuật
- [main.py](main.py) - Integration code
- [rag/token_manager.py](rag/token_manager.py) - Core logic
- [rag/test_token_manager.py](rag/test_token_manager.py) - Tests & examples

---

**Phiên bản**: 1.0  
**Cập nhật**: 2024-03-21  
**API**: Google Gemini v2.5
