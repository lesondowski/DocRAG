from document_loader import load_pdf
from chunk_builder import build_chunks

documents = load_pdf("data/raw/document/pdf/PDF2.pdf")
chunks = build_chunks(documents)
print("Total chunks:", len(chunks))
print(chunks[0])