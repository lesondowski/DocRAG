import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from rag.embedding import GeminiEmbedder
from rag.retriever import Retriever


query = "Hướng dẫn chụp hình audit?"

embedder = GeminiEmbedder()
query_embedding = embedder.embed_text(query)


retriever = Retriever()

results = retriever.retrieve(query_embedding)

print(results["documents"])