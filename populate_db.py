import sys
import os
sys.path.append(os.path.dirname(__file__))

from rag.document_loader import load_pdf
from rag.text_cleaner import clean_text
from rag.chunking import Chunker
from rag.metadata_builder import MetadataBuilder
from rag.embedding import GeminiEmbedder
from rag.vector_store import VectorStore

# Sample PDF path (thay bằng file thực tế)
pdf_path = "data/raw/document/pdf/PDF1.pdf"  # Giả sử có file sample

pages = load_pdf(pdf_path)

chunker = Chunker()
metadata_builder = MetadataBuilder()
embedder = GeminiEmbedder()
vector_store = VectorStore()

all_chunks = []
for page in pages:
    cleaned_text = clean_text(page["text"])
    chunks = chunker.chunk_text(cleaned_text)
    for i, chunk in enumerate(chunks):
        metadata = metadata_builder.build_metadata(pdf_path.split("/")[-1], page["page_number"], i)
        all_chunks.append({"content": chunk, "metadata": metadata})

embedded_chunks = embedder.embed_chunks(all_chunks)
vector_store.add_embeddings(embedded_chunks)

print("Data populated successfully.")