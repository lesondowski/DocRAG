# Token Management & Cost Optimization - Báo Cáo Chi Tiết

## 1. Tổng Quan

Token Management là giai đoạn tối ưu hóa chi phí API so với chất lượng response trong RAG systems. Mục tiêu:
- ✅ Theo dõi sử dụng token cho mỗi request
- ✅ Tính toán chi phí API thực tế
- ✅ Tự động chọn model phù hợp dựa trên độ phức tạp của câu hỏi
- ✅ Tiết kiệm chi phí mà vẫn duy trì chất lượng câu trả lời

---

## 2. Kiến Trúc Token Manager

### 2.1 Thành phần chính

```
rag/token_manager.py
├── TokenManager (class chính)
│   ├── count_tokens(text) - Đếm token
│   ├── estimate_complexity(query) - Ước tính độ phức tạp
│   ├── select_model(query) - Chọn model tối ưu
│   ├── calculate_cost() - Tính chi phí
│   ├── log_query() - Ghi log
│   ├── print_session_summary() - Báo cáo session
│   └── save_session_log() - Lưu log
```

---

## 3. Chi Phí API (Pricing)

Dựa trên Google Gemini API (2024):

| Model | Input Cost | Output Cost | Tốc độ | Chất lượng | Use Case |
|-------|-----------|-----------|--------|-----------|----------|
| **Gemini-1.5-Flash** (Lite) | $0.075/1M | $0.30/1M | ⚡⚡⚡ Nhanh | ⭐ Cơ bản | Câu hỏi đơn giản |
| **Gemini-2.0-Flash** | $0.10/1M | $0.40/1M | ⚡⚡ Trung bình | ⭐⭐ Tốt | Câu hỏi trung bình |
| **Gemini-1.5-Pro** | $2.50/1M | $7.50/1M | ⚡ Chậm | ⭐⭐⭐⭐ Xuất sắc | Câu hỏi phức tạp |

**Lưu ý**: Giá có thể thay đổi, cần cập nhật trong `token_manager.py` khi có thay đổi.

---

## 4. Cơ Chế Chọn Model (Model Selection Logic)

### 4.1 Ước Tính Độ Phức Tạp (Complexity Scoring)

Hệ thống tự động tính độ phức tạp từ 1-10 dựa trên:

#### A. Length-based (Độ dài câu hỏi)
```python
base_complexity = 1
+2 nếu câu hỏi > 100 ký tự
+2 nếu câu hỏi > 200 ký tự
```

#### B. Keyword-based (Từ khóa chỉ phức tạp)
Từ khóa phát hiện():
- "phân tích" (+2)
- "so sánh" (+2)
- "giải thích" (+2)
- "tại sao" (+2)
- "làm sao" (+2)
- "chi tiết" (+2)
- "toàn bộ" (+2)
- "tổng hợp" (+2)
- "cách" (+2)
- "quy trình" (+2)

#### C. Multiple questions (Nhiều câu hỏi)
```
+2 nếu có > 1 dấu "?"
```

### 4.2 Quyết Định Model

```
Complexity 1-3:    ⭐ Flash Lite (Tiết kiệm nhất)
Complexity 4-7:    ⭐⭐ Flash 2.0 (Cân bằng)
Complexity 8-10:   ⭐⭐⭐⭐ Pro (Chất lượng cao)
```

**Ví dụ:**

| Câu hỏi | Độ phức tạp | Model Chọn | Chi phí ước tính |
|--------|-----------|-----------|-----------------|
| "Là gì audit?" | 1 | Flash Lite | ~$0.0001 |
| "Quy trình audit của công ty?" | 5 | Flash 2.0 | ~$0.0015 |
| "Phân tích chi tiết các bước audit, ưu điểm và hạn chế của quy trình?" | 9 | Pro | ~$0.025 |

---

## 5. Token Counting (Đếm Token)

### 5.1 Phương Pháp Hiện Tại

```python
# Rough heuristic
token_count ≈ len(text) / 4
```

**Giải thích**: Trong tiếng Anh/Việt, 1 token ≈ 4 ký tự trung bình.

### 5.2 Cải Thiện (Optional)
Sử dụng Google's official tokenizer:
```python
import google.ai.generativelanguage as glm
# Hoặc dùng Gemini API's tokenize method
```

---

## 6. Cost Calculation (Tính Chi Phí)

### 6.1 Công Thức

```python
cost_USD = (input_tokens / 1,000,000) * input_price 
         + (output_tokens / 1,000,000) * output_price
```

### 6.2 Ví dụ Thực Tế

| Scenario | Input | Output | Model | Chi phí |
|----------|-------|--------|-------|---------|
| Câu hỏi đơn | 500 | 100 | Flash Lite | ~$0.000045 |
| Câu hỏi trung | 2000 | 500 | Flash 2.0 | ~$0.00040 |
| Câu hỏi phức | 3000 | 1000 | Pro | ~$0.0125 |

---

## 7. Session Tracking & Logging

### 7.1 Cấu trúc Log

Mỗi query được log với thông tin:
```json
{
  "timestamp": "2024-03-21T10:30:45",
  "query": "Hướng dẫn chụp hình audit?",
  "complexity": 5,
  "model": "gemini-2.0-flash",
  "prompt_tokens": 1500,
  "output_tokens": 300,
  "total_tokens": 1800,
  "cost_usd": 0.000720,
  "answer_preview": "Hướng dẫn chụp hình audit bao gồm..."
}
```

### 7.2 Session Summary

Sau phiên làm việc, system tự động show:
```
============================================================
TOKEN MANAGEMENT SUMMARY
============================================================
Total Queries: 15
Total Tokens Used: 45,000
Total Cost: $0.125678
Avg Cost/Query: $0.008379

Model Usage Breakdown:
  gemini-1.5-flash:
    - Queries: 8
    - Tokens: 20,000
    - Cost: $0.035000
  gemini-2.0-flash:
    - Queries: 5
    - Tokens: 18,000
    - Cost: $0.072000
  gemini-1.5-pro:
    - Queries: 2
    - Tokens: 7,000
    - Cost: $0.018678
============================================================
```

### 7.3 Log Files

Logs được lưu vào:
```
logs/session_20240321_103045.json
```

---

## 8. Integration với RAG Pipeline

### 8.1 Flow

```
User Query
    ↓
[token_manager.estimate_complexity] → Complexity Score
    ↓
[token_manager.select_model] → Best Model
    ↓
[generator.generate with selected_model]
    ↓
[token_manager.log_query] → Track Usage
    ↓
Display Response + Cost
```

### 8.2 Code Changes

**main.py:**
```python
from rag.token_manager import TokenManager

token_manager = TokenManager()

# For each query:
selected_model, reason = token_manager.select_model(query)
response, tokens = generator.generate(query, context, model_name=selected_model)
token_manager.log_query(query, selected_model, tokens["prompt_tokens"], tokens["output_tokens"], response)
```

---

## 9. Tối Ưu Hóa Chi Phí - Best Practices

### 9.1 Khi sử dụng Flash Lite
✅ Câu hỏi đơn, rõ ràng  
✅ Truy vấn cơ bản từ database  
✅ Nhân diện và phân loại cản  

### 9.2 Khi sử dụng Flash 2.0
✅ Câu hỏi trung bình phức tạp  
✅ Cần so sánh, tóm tắt  
✅ Yêu cầu logic nhưng không quá sâu  

### 9.3 Khi sử dụng Pro
✅ Câu hỏi rất phức tạp  
✅ Yêu cầu suy luận đa bước  
✅ Phân tích chi tiết, cảnh báo  
✅ Nội dung quan trọng, chi phí không là vấn đề  

### 9.4 Các chiến lược tiết kiệm
1. **Caching**: Lưu câu hỏi + đáp án trùng lặp
2. **Batch Processing**: Xử lý nhiều câu hỏi cùng lúc
3. **Context Compression**: Giảm kích thước context được gửi
4. **Fallback to Cache**: Sử dụng câu trả lời cached nếu có

---

## 10. Monitoring & Alerts

### 10.1 Metrics cần theo dõi

```python
# Trên console mỗi lần query
❌ Warn nếu chi phí/query > $0.05  → "High cost this query"
❌ Warn nếu tổng chi phí session > $5 → "Session approaching limit"
❌ Warn nếu token count > 4000 → "Large prompt, consider shorter context"
```

### 10.2 Báo cáo hàng tháng

```
Monthly Cost Report:
App Version X
- Total Queries: 1,500
- Total Cost: $45.67
- Flash Lite: $12.50 (27%)
- Flash 2.0: $25.00 (55%)
- Pro: $8.17 (18%)

Optimization Suggestions:
⭐ 60% queries có complexity <= 3, hãy dùng Flash Lite
⭐ Setup caching cho 30 câu hỏi phổ biến
```

---

## 11. Cài đặt & Sử dụng

### 11.1 Cài đặt

```bash
# Đã tích hợp sẵn trong project
# File: rag/token_manager.py

python main.py
# Tự động tracking và log token usage
```

### 11.2 Xem logs

```bash
# Logs lưu trong thư mục:
ls logs/session_*.json
```

### 11.3 Phân tích logs

```python
import json

with open("logs/session_20240321_103045.json") as f:
    data = json.load(f)
    
print(f"Total cost: ${data['total_cost']}")
print(f"Most used model: {max(data['model_usage'], key=lambda x: data['model_usage'][x]['count'])}")
```

---

## 12. Tương Lai: Context Caching (Mức 4)

Khi dữ liệu rất lớn, sử dụng Google Gemini's **Prompt Caching**:

```python
# Lưu context lớn lần đầu (tốn tiền hơn)
# Cache 5 phút trên server Google (5% giảm chi phí)
# Request sau tái sử dụng cache (tiết kiệm 90%)
```

**Chi phí:**
- Prompt cache creation: 25% chi phí input
- Prompt cache usage: 10% chi phí input (khá nhất)

**Lợi ích:**  
Với dữ liệu 100K token:
- Bình thường: 100,000 * $2.50/1M = $0.25/query
- Với cache: $0.025 (creation) + $0.025 (reuse) = tiết kiệm 50%+

---

## 13. Kết Luận

**Token Management** cung cấp:
- 🎯 **Visibility** - Biết chính xác tốn bao nhiêu từng API call
- 💰 **Cost Control** - Tiết kiệm 60-70% chi phí bằng smart model selection
- 📊 **Analytics** - Dữ liệu để tối ưu hệ thống
- ⚡ **Performance** - Dùng model nhanh cho câu đơn, Pro cho câu phức

**Next Step**: Cài đặt Context Caching (Mức 4) cho dữ liệu siêu lớn.

---

*Báo cáo cập nhật: 2024-03-21*  
*Framework: Google Gemini API v2.5*
