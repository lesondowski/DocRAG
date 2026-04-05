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
        self.fallback_answer = (
            "Tôi là trợ lý AI thông minh của ứng dụng Audit App "
            "chỉ có thể trả lời các câu hỏi trong ứng dụng Audit này"
        )

    def _build_prompt(self, query: str, context: str) -> str:
        context_section = f"\n\n[CONTEXT]\n{context}" if context and context.strip() else ""
        return f"""Bạn là trợ lý AI thông minh của ứng dụng Audit App.

Quy tắc trả lời:
1. Nếu câu hỏi là lời chào hỏi, hỏi về bản thân bạn, hoặc câu giao tiếp thông thường → trả lời tự nhiên, thân thiện.
2. Nếu câu hỏi liên quan đến Audit App và có context → trả lời dựa trên context, sử dụng citation [1], [2]... khi cần.
3. Nếu câu hỏi không liên quan đến Audit App và không phải chào hỏi → bắt buộc trả lời đúng câu: "{self.fallback_answer}"

Giữ câu trả lời rõ ràng, ngắn gọn, chính xác.

[CÂU HỎI]
{query}{context_section}

Yêu cầu output JSON hợp lệ:
{{
  "answer": "câu trả lời ở đây"
}}""".strip()

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
            parsed = {"answer": self.fallback_answer}

        answer_text = str(parsed.get("answer", "") or "").strip().lower()
        blocked_patterns = [
            "không đủ thông tin",
            "khong du thong tin",
            "ngoài phạm vi",
            "ngoai pham vi",
        ]
        if any(pattern in answer_text for pattern in blocked_patterns):
            parsed["answer"] = self.fallback_answer

        usage = getattr(response, "usage_metadata", None)

        token_info = {
            "model": model,
            "prompt_tokens": getattr(usage, "prompt_token_count", 0) if usage else 0,
            "response_tokens": getattr(usage, "candidates_token_count", 0) if usage else 0,
            "total_tokens": getattr(usage, "total_token_count", 0) if usage else 0,
        }

        return parsed, token_info