from rag.text_cleaner import clean_text
from rag.chunking import Chunker


def build_chunks(documents, file_name, chunking_strategy='auto'):
    """
    Build chunks from documents using specified chunking strategy.
    
    Args:
        documents: List of document dicts with 'text' and 'page'
        file_name: Source file name
        chunking_strategy: 'auto', 'text', 'structure', 'semantic', 'function'
    """
    chunker = Chunker()
    dataset = []

    for doc_id, doc in enumerate(documents):
        page = doc.get("page", doc_id + 1)
        text = doc.get("text", "")
        if not text:
            continue
        cleaned_text = clean_text(text)
        
        # Auto-detect strategy if requested
        if chunking_strategy == 'auto':
            detected_strategy = chunker.auto_detect_strategy(cleaned_text)
        else:
            detected_strategy = chunking_strategy
        
        # Choose chunking method based on strategy
        if detected_strategy == 'structure':
            chunks = chunker.chunk_structure_aware(cleaned_text)
        elif detected_strategy == 'semantic':
            chunks = chunker.chunk_semantic(cleaned_text)
        elif detected_strategy == 'function':
            chunks = chunker.chunk_function_api(cleaned_text)
        else:  # 'text'
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
                        "chunking_strategy": detected_strategy
                    }
                }
            )

    return dataset