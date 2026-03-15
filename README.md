# DocRAG


## chunking
Dưới đây là triển khai chi tiết phần Chunking Strategy trong pipeline RAG. Phần này bám theo best-practice trong Gemini API Cookbook và các ví dụ trong Google Gemini Cookbook GitHub Repository, nơi nhấn mạnh:

- chia tài liệu thành semantic chunks

- giữ metadata

- dùng overlap để bảo toàn ngữ cảnh

- chunk theo token thay vì ký tự

Phần này thường chiếm một mục riêng trong report vì nó ảnh hưởng trực tiếp tới độ chính xác của RAG retrieval.