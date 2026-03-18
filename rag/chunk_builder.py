from rag.text_cleaner import clean_text
from rag.chunking import Chunker


def build_chunks(documents):
    chunker = Chunker()
    dataset = []

    for doc_id, doc in enumerate(documents):
        page = doc.get("page", doc_id + 1)
        text = doc.get("text", "")
        if not text:
            continue
        cleaned_text = clean_text(text)
        chunks = chunker.chunk_text(cleaned_text)
        for i, chunk in enumerate(chunks):
            dataset.append(
                {
                    "content": chunk,
                    "metadata": {
                        "page": page,
                        "chunk_index": i,
                        "document_id": doc_id
                    }
                }
            )

    return dataset