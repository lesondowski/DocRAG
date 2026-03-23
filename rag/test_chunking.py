import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.document_loader import load_pdf
from rag.chunk_builder import build_chunks

documents = load_pdf("data/raw/document/pdf/PDF2.pdf")
chunks = build_chunks(documents, "PDF2.pdf", chunking_strategy='auto')  # Auto-detect strategy
print("Total chunks:", len(chunks))
print("Strategy used:", chunks[0]['metadata']['chunking_strategy'] if chunks else 'none')
print("First chunk:", chunks[0]['content'][:200] + "..." if chunks else 'no chunks')