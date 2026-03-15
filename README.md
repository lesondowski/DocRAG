# DocRAG


## chunking
Dưới đây là triển khai chi tiết phần Chunking Strategy trong pipeline RAG. Phần này bám theo best-practice trong Gemini API Cookbook và các ví dụ trong Google Gemini Cookbook GitHub Repository, nơi nhấn mạnh:

- chia tài liệu thành semantic chunks

- giữ metadata

- dùng overlap để bảo toàn ngữ cảnh

- chunk theo token thay vì ký tự

Phần này thường chiếm một mục riêng trong report vì nó ảnh hưởng trực tiếp tới độ chính xác của RAG retrieval.


### Embedding

- Mô hình mới nhất, `gemini-embedding-2-preview`, là mô hình nhúng đa phương thức đầu tiên trong Gemini API. Mô hình này ánh xạ văn bản, hình ảnh, video, âm thanh và tài liệu vào một không gian nhúng thống nhất, cho phép tìm kiếm, phân loại và phân cụm đa phương thức trên hơn 100 ngôn ngữ

- `gemini-embedding-001` dùng cho các trường hợp sử dụng chỉ có văn bản