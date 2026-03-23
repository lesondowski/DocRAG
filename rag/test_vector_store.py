import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.document_loader import load_pdf
from rag.chunk_builder import build_chunks
from rag.embedding import GeminiEmbedder
from rag.vector_store import VectorStore


documents = load_pdf("data/raw/document/pdf/PDF2.pdf")

chunks = build_chunks(documents, "PDF2.pdf", chunking_strategy='auto')  # Auto-detect

print("Total chunks:", len(chunks))


embedder = GeminiEmbedder()
embedded_chunks = embedder.embed_chunks(chunks)


vector_store = VectorStore()

vector_store.add_embeddings(embedded_chunks)