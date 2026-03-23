class ContextBuilder:

    def build(self, retrieved_docs):

        documents = retrieved_docs["documents"][0]
        metadatas = retrieved_docs["metadatas"][0]

        context = []
        # chỉ định tài liệu nào được sử dụng để trả lời câu hỏi
        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            source = meta.get("source", "unknown")
            page = meta.get("page", "N/A")

            context.append(
                f"""[{source}/{page}]
                content:
                {doc}"""
            )

        return "\n\n".join(context)