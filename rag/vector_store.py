import chromadb
from chromadb.config import Settings


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path = "db/chroma_db"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="rag_documents"
        )

    def add_embeddings(self, embedded_chunks):

        documents = []
        embeddings = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(embedded_chunks):

            documents.append(chunk["content"])
            embeddings.append(chunk["embedding"])
            metadatas.append(chunk["metadata"])
            ids.append(f"chunk_{i}")

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print("Stored", len(documents), "chunks in ChromaDB")