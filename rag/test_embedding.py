from document_loader import load_pdf
from chunk_builder import build_chunks
from embedding import GeminiEmbedder


documents = load_pdf("data/raw/document/pdf/PDF1.pdf")

chunks = build_chunks(documents)

print("Total chunks:", len(chunks))

embedder = GeminiEmbedder()

embedded_chunks = embedder.embed_chunks(chunks)

print("Vector length:", len(embedded_chunks[0]["embedding"]))