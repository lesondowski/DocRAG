from rag.text_cleaner import clean_text
from rag.chunking import Chunker


def build_chunks(documents, file_name):
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
            chunk_id = f"{file_name}-p{page}-c{i}"
            dataset.append(
                {
                    "id": chunk_id,
                    "content": chunk,
                    "metadata": {
                        "source": file_name,
                        "page": page,
                    }
                }
            )

    return dataset