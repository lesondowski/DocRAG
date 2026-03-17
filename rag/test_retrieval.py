from embedding import GeminiEmbedder
from retriever import Retriever


query = "Hướng dẫn chụp hình audit?"

embedder = GeminiEmbedder()
query_embedding = embedder.embed_text(query)


retriever = Retriever()

results = retriever.retrieve(query_embedding)

print(results["documents"])