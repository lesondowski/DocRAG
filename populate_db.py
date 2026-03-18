import sys
import os
sys.path.append(os.path.dirname(__file__))

from rag.chunk_builder import build_chunks
from rag.document_loader import load_pdf
from rag.chunking import Chunker
from rag.metadata_builder import MetadataBuilder
from rag.embedding import GeminiEmbedder
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.generator import Generator
from rag.context_builder import ContextBuilder


# Sample PDF path
pdf_path = "data/raw/document/pdf/PDF2.pdf"
query = "Hướng dẫn chụp hình audit?"

# Load document
pages = load_pdf(pdf_path)

# Initialize pipeline components
chunker = Chunker()
metadata_builder = MetadataBuilder()
embedder = GeminiEmbedder()
vector_store = VectorStore()

# Build chunks with metadata

chunks = build_chunks(pages)

# Create embeddings
embedded_chunks = embedder.embed_chunks(chunks)

# Store embeddings in vector DB
vector_store.add_embeddings(embedded_chunks)

# ----- Query pipeline -----

# Embed query
query_embedding = embedder.embed_text(query)

# Retrieve relevant chunks
retriever = Retriever()
results = retriever.retrieve(query_embedding)

# Build context for LLM
context_builder = ContextBuilder()
context = context_builder.build(results)

# Generate answer
generator = Generator()
answer = generator.generate(query, context)

print(answer)