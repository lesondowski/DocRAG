from __future__ import annotations

import os
import json
from typing import Any, Dict, Tuple

from dotenv import load_dotenv
import google.genai as genai

load_dotenv()


class Generator:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables.")

        self.client = genai.Client(api_key=api_key)
        self.default_model = os.getenv("GEMINI_GENERATE_MODEL", "gemini-2.5-flash")

    def _build_prompt(self, query: str, context: str) -> str:
        return f"""
Bạn là trợ lý RAG.
Chỉ trả lời dựa trên context được cung cấp.
Nếu context không đủ, hãy nói rõ là không đủ thông tin.
Giữ câu trả lời rõ ràng, ngắn gọn, chính xác.
Khi dùng thông tin từ tài liệu, giữ nguyên placeholder citation dạng [1], [2]... nếu có trong output mẫu nội bộ.

[CÂU HỎI]
{query}

[CONTEXT]
{context}

Yêu cầu output JSON hợp lệ:
{{
  "answer": "câu trả lời ở đây"
}}
""".strip()

    def generate(self, query: str, context: str, model_name: str | None = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        model = model_name or self.default_model
        prompt = self._build_prompt(query, context)

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
        )

        text = getattr(response, "text", "") or ""
        text = text.strip()

        parsed: Dict[str, Any]
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                parsed = {"answer": text}
        except Exception:
            parsed = {"answer": text or "Xin lỗi, tôi không thể tạo câu trả lời."}

        usage = getattr(response, "usage_metadata", None)

        token_info = {
            "model": model,
            "prompt_tokens": getattr(usage, "prompt_token_count", 0) if usage else 0,
            "response_tokens": getattr(usage, "candidates_token_count", 0) if usage else 0,
            "total_tokens": getattr(usage, "total_token_count", 0) if usage else 0,
        }

        return parsed, token_info