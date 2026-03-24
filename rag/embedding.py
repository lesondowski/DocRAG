from __future__ import annotations

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
import google.genai as genai

load_dotenv()


class GeminiEmbedder:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-2-preview")

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return []

        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
        )
        return response.embeddings[0].values

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        embedded_chunks: List[Dict[str, Any]] = []

        for chunk in chunks:
            content = (chunk.get("content") or "").strip()
            if not content:
                continue

            embedding = self.embed_text(content)
            if not embedding:
                continue

            embedded_chunks.append(
                {
                    "id": chunk["id"],
                    "content": content,
                    "embedding": embedding,
                    "metadata": chunk["metadata"],
                }
            )

        return embedded_chunks