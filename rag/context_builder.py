class ContextBuilder:

    def build(self, retrieved_docs):

        documents = retrieved_docs["documents"][0]
        metadatas = retrieved_docs["metadatas"][0]

        context = ""
        # chỉ định tài liệu nào được sử dụng để trả lời câu hỏi
        for doc, meta in zip(documents, metadatas):
            source = meta.get("source", f"Trang {meta.get('page', 'N/A')}")
            context += f"""
            Nguồn: {source}
            Nội dung:
            {doc}
            ---
            """
        return context