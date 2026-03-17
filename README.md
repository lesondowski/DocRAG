# DocRAG

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