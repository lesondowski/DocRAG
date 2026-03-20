import chromadb
from chromadb.config import Settings


class VectorStore:

    def __init__(self, path="db/chroma_db"):

        self.client = chromadb.PersistentClient(
            path=path
        )
        
        self.collection = self.client.get_or_create_collection(
            name="rag_documents"
        )

    def reset(self):
        """
        Deletes and recreates the collection.
        """
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name="rag_documents"
        )
        print("ChromaDB collection reset.")

    def add_embeddings(self, embedded_chunks):

        if not embedded_chunks:
            print("No embeddings to add.")
            return

        documents = []
        embeddings = []
        metadatas = []
        ids = []

        for chunk in embedded_chunks:
            documents.append(chunk["content"])
            embeddings.append(chunk["embedding"])
            metadatas.append(chunk["metadata"])
            ids.append(chunk["id"])

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print("Stored", len(documents), "chunks in ChromaDB")