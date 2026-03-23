# DocRAG

DocRAG là một hệ thống RAG (Retrieval-Augmented Generation) với giao diện web ChatGPT-like để hỏi đáp về tài liệu.

## Tính năng

- **Chatbot AI**: Hỏi đáp thông minh về nội dung tài liệu
- **Upload PDF**: Thêm tài liệu mới vào knowledge base
- **Citations**: Trích dẫn nguồn với trang cụ thể
- **Giao diện tối giản**: Thiết kế giống ChatGPT với dark mode
- **Responsive**: Hoạt động trên desktop và mobile

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Chuẩn bị dữ liệu

Chạy populate_db.py để tạo knowledge base từ PDF:

```bash
python populate_db.py
```

### 3. Chạy Backend API

```bash
python main_web.py
```

Backend sẽ chạy trên http://127.0.0.1:5000

### 4. Chạy Frontend (tùy chọn)

Nếu muốn giao diện web:

```bash
cd frontend
npm install
npm start
```

Frontend sẽ chạy trên http://localhost:3000

## Sử dụng

### Terminal (mặc định)

```bash
python main.py
```

### Web Interface

1. Mở http://localhost:3000
2. Upload file PDF nếu cần thêm tài liệu
3. Chat với AI về nội dung tài liệu

## Chunking
Dưới đây là triển khai chi tiết phần Chunking Strategy trong pipeline RAG. Phần này bám theo best-practice trong Gemini API Cookbook và các ví dụ trong Google Gemini Cookbook GitHub Repository, nơi nhấn mạnh:

- Chia tài liệu thành semantic chunks theo token (không phải ký tự) để tối ưu cho LLM.
- Giữ metadata (filename, page) để trích dẫn nguồn.
- Dùng overlap (50 tokens) để bảo toàn ngữ cảnh giữa chunks.
- Chunk size 500 tokens để cân bằng giữa context và retrieval accuracy.

## Embedding
- Mô hình mới nhất, `gemini-embedding-2-preview`, là mô hình nhúng đa phương thức đầu tiên trong Gemini API. Mô hình này ánh xạ văn bản, hình ảnh, video, âm thanh và tài liệu vào một không gian nhúng thống nhất, cho phép tìm kiếm, phân loại và phân cụm đa phương thức trên hơn 100 ngôn ngữ.
- `gemini-embedding-001` dùng cho các trường hợp sử dụng chỉ có văn bản.

## Structured Output và Citations
- Generator sử dụng JSON mode của Gemini để trả về structured output, tránh hallucination.
- System prompt định danh AI chỉ trả lời dựa trên context, yêu cầu trích dẫn nguồn rõ ràng.
- Context injection ghép metadata vào prompt để AI dễ dàng cite nguồn (ví dụ: "Theo trang 12, tài liệu X").

Token Management & Cost Optimization