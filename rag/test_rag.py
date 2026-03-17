from embedding import GeminiEmbedder
from retriever import Retriever
from context_builder import ContextBuilder
from generator import Generator


question = "Hướng dẫn chụp hình Audit?"

embedder = GeminiEmbedder()
query_embedding = embedder.embed_text(question)

retriever = Retriever()
results = retriever.retrieve(query_embedding)

context_builder = ContextBuilder()
context = context_builder.build(results)

generator = Generator()
answer = generator.generate(question, context)


print("QUESTION:")
print(question)
print("\n------------------------\nCONTEXT:")
print(context)
print("\n------------------------\nANSWER:")
if isinstance(answer, dict):
    print("Câu trả lời:", answer.get("answer", "N/A"))
    print("Trích dẫn:", answer.get("citations", []))
else:
    print(answer)