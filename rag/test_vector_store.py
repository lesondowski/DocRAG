from document_loader import load_pdf
from chunk_builder import build_chunks
from embedding import GeminiEmbedder
from vector_store import VectorStore


documents = load_pdf("data/raw/document/pdf/PDF2.pdf")

chunks = build_chunks(documents)

print("Total chunks:", len(chunks))


embedder = GeminiEmbedder()
embedded_chunks = embedder.embed_chunks(chunks)


vector_store = VectorStore()

vector_store.add_embeddings(embedded_chunks)