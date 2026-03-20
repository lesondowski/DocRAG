import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.document_loader import load_pdf
from rag.chunk_builder import build_chunks

documents = load_pdf("data/raw/document/pdf/PDF2.pdf")
chunks = build_chunks(documents)
print("Total chunks:", len(chunks))
print(chunks[0])