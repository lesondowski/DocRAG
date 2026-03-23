import chromadb

# Semantic Retrieval + Grounding + Tool-Augmented Retrieval
class Retriever:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="db/chroma_db"
        )

        self.collection = self.client.get_collection(
            name="rag_documents"
        )

    def retrieve(self, query_embedding, k=4):

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        return results