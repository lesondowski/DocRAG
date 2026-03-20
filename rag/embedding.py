import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()
class GeminiEmbedder:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def embed_text(self, text: str):

        # text to embedding vector
        response = self.client.models.embed_content(
            model="gemini-embedding-2-preview",
            contents=text
        )
        return response.embeddings[0].values

    def embed_chunks(self, chunks):
        embedded_chunks = []
        # Use a more efficient batch embedding if the API and library support it in the future
        for chunk in chunks:
            embedding = self.embed_text(chunk["content"])
            embedded_chunks.append(
                {
                    "id": chunk["id"],
                    "content": chunk["content"],
                    "embedding": embedding,
                    "metadata": chunk["metadata"]
                }
            )
        return embedded_chunks
















