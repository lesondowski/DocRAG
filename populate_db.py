import sys
from pathlib import Path
from tqdm import tqdm
from rag.document_loader import load_pdf
from rag.chunk_builder import build_chunks
from rag.embedding import GeminiEmbedder
from rag.vector_store import VectorStore

#Config
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data" / "raw" / "document" / "pdf"
DB_DIR = ROOT_DIR / "db" / "chroma_db"

def main():
    """
    Main function to orchestrate the RAG database population pipeline.
    """

    # --- 1. Initialize Components ---
    print("Initializing components...")
    vector_store = VectorStore(path=str(DB_DIR))
    embedder = GeminiEmbedder()
    
    # --- 2. Reset Database ---
    print("Resetting ChromaDB collection...")
    vector_store.reset()

    # --- 3. Find Documents ---
    pdf_files = list(DATA_DIR.glob("**/*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {DATA_DIR}. Exiting.")
        return

    print(f"Found {len(pdf_files)} PDF document(s) to process.")

    # --- 4. Process Each Document ---
    total_chunks_processed = 0
    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
        try:
            print(f"\nProcessing file: {pdf_path.name}")

            # Load document pages
            pages = load_pdf(str(pdf_path))
            if not pages:
                print(f"Could not extract text from {pdf_path.name}. Skipping.")
                continue

            # Build chunks with metadata
            chunks = build_chunks(pages, pdf_path.name, chunking_strategy='auto')  # Auto-detect strategy
            if not chunks:
                print(f"No chunks created for {pdf_path.name}. Skipping.")
                continue
            
            print(f"Created {len(chunks)} chunks.")

            # Create embeddings for chunks
            print("Generating embeddings with Gemini...")
            embedded_chunks = embedder.embed_chunks(chunks)

            # Store in Vector DB
            print("Adding chunks to ChromaDB...")
            vector_store.add_embeddings(embedded_chunks)
            
            total_chunks_processed += len(embedded_chunks)

        except Exception as e:
            print(f"An error occurred while processing {pdf_path.name}: {e}")
            # Optionally, decide if you want to stop or continue
            # continue
    
    print("\n--- RAG Database Population Complete ---")
    print(f"Total chunks processed and stored: {total_chunks_processed}")


if __name__ == "__main__":
    main()
